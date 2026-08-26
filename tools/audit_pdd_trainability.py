# -*- coding: utf-8 -*-
"""工具脚本：对 B0, B1, B1-U, PDD-U 四种配置执行参数可训练性与实际 Step 更新审计

依据任务卡 PRT-002-A1 要求：
对 conv1/bn1, layer1, maxpool/PDD 记录：
- 参数总数与 trainable 参数数
- requires_grad 状态与 optimizer membership
- 实际执行 1 次 optimizer step 前后的参数更新范数 (max / L2 update norm)
- 梯度范数与 NaN / Inf 校验
输出: outputs/PRT-002-A1/audit/parameter_update_audit.json
"""

import os
import os.path as osp
import json
import torch
import torch.nn as nn
from mmengine.config import Config
from mmdet.registry import MODELS
from mmdet.utils import register_all_modules
register_all_modules()
import prtiny.models  # 注册 ResNetWithPDD


def audit_single_config(config_path: str, name: str) -> dict:
    cfg = Config.fromfile(config_path)
    model = MODELS.build(cfg.model)
    model.train()
    
    # 模拟构建优化器
    lr = 0.005
    optimizer = torch.optim.SGD(
        [p for p in model.parameters() if p.requires_grad],
        lr=lr, momentum=0.9, weight_decay=0.0001
    )
    
    # 统计模块参数状态
    modules_to_inspect = ["conv1", "bn1", "maxpool", "layer1", "layer2", "neck", "bbox_head"]
    module_stats = {}
    
    # 记录 step 前参数
    params_before = {}
    for p_name, param in model.named_parameters():
        params_before[p_name] = param.detach().clone()
        
    # 构造虚拟输入执行前向与反向
    # FCOS forward_train 需要 data_samples
    dummy_x = torch.randn(1, 3, 256, 256, requires_grad=False)
    
    # 骨干网络前向
    features = model.backbone(dummy_x)
    loss = sum(f.sum() for f in features)
    loss.backward()
    
    grad_stats = {}
    for p_name, param in model.named_parameters():
        if param.grad is not None:
            g_norm = float(param.grad.norm().item())
            has_nan = bool(torch.isnan(param.grad).any().item())
            has_inf = bool(torch.isinf(param.grad).any().item())
            grad_stats[p_name] = {"grad_norm": round(g_norm, 6), "has_nan": has_nan, "has_inf": has_inf}
        else:
            grad_stats[p_name] = {"grad_norm": 0.0, "has_nan": False, "has_inf": False}
            
    optimizer.step()
    
    # 记录 step 后参数并计算更新量
    update_stats = {}
    for p_name, param in model.named_parameters():
        diff = (param.detach() - params_before[p_name]).norm().item()
        update_stats[p_name] = round(float(diff), 6)
        
    # 汇总各层级模块信息
    for mod_name in modules_to_inspect:
        mod_params = []
        trainable_count = 0
        total_count = 0
        max_update = 0.0
        max_grad_norm = 0.0
        
        for p_name, param in model.named_parameters():
            if mod_name in p_name:
                total_count += param.numel()
                if param.requires_grad:
                    trainable_count += param.numel()
                diff = update_stats.get(p_name, 0.0)
                g_norm = grad_stats.get(p_name, {}).get("grad_norm", 0.0)
                if diff > max_update:
                    max_update = diff
                if g_norm > max_grad_norm:
                    max_grad_norm = g_norm
                    
        module_stats[mod_name] = {
            "total_params": total_count,
            "trainable_params": trainable_count,
            "is_trainable": trainable_count > 0,
            "max_gradient_norm": round(max_grad_norm, 6),
            "max_param_update_norm": round(max_update, 6),
            "actually_updated": max_update > 0.0
        }
        
    total_model_params = sum(p.numel() for p in model.parameters())
    trainable_model_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        "config_name": name,
        "config_path": config_path,
        "frozen_stages": cfg.model.backbone.get("frozen_stages", None),
        "total_params": total_model_params,
        "trainable_params": trainable_model_params,
        "frozen_params": total_model_params - trainable_model_params,
        "trainable_ratio": round(trainable_model_params / total_model_params, 4),
        "module_breakdown": module_stats
    }


def main():
    configs = [
        ("B0", "configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py"),
        ("B1", "configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py"),
        ("B1-U", "configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py"),
        ("PDD-U", "configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py")
    ]
    
    out_dir = "outputs/PRT-002-A1/audit"
    os.makedirs(out_dir, exist_ok=True)
    
    results = {}
    print("=" * 60)
    print("正在执行四配置参数训练状态与 Step 更新审计...")
    print("=" * 60)
    
    for name, cfg_path in configs:
        print(f"--> 审计配置 {name} ({cfg_path})...")
        res = audit_single_config(cfg_path, name)
        results[name] = res
        print(f"    Total params: {res['total_params']}, Trainable: {res['trainable_params']} ({res['trainable_ratio']*100:.1f}%)")
        print(f"    conv1 updated: {res['module_breakdown']['conv1']['actually_updated']}, maxpool/PDD updated: {res['module_breakdown']['maxpool']['actually_updated']}, layer1 updated: {res['module_breakdown']['layer1']['actually_updated']}")
        
    out_json = osp.join(out_dir, "parameter_update_audit.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("=" * 60)
    print(f"参数训练状态审计完成，输出至: {out_json}")
    print("=" * 60)


if __name__ == '__main__':
    main()

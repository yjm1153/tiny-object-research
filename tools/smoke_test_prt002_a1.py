# -*- coding: utf-8 -*-
"""PRT-002-A1 Smoke Test: 验证 B1-U 与 PDD-U 前向、反向与轻量训练流程稳定性"""

import os
import os.path as osp
import json
import torch
from mmengine.config import Config
from mmengine.runner import Runner
from mmdet.registry import MODELS
from mmdet.utils import register_all_modules
register_all_modules()
import prtiny.models


def run_smoke(config_path: str, work_dir: str, name: str) -> dict:
    os.makedirs(work_dir, exist_ok=True)
    cfg = Config.fromfile(config_path)
    cfg.work_dir = work_dir
    
    # 缩减为 10 iters smoke
    cfg.train_dataloader.dataset.ann_file = "annotations/aitod_val_v1.json"
    cfg.train_dataloader.dataset.data_prefix = dict(img='val/images/')
    cfg.train_cfg = dict(type='IterBasedTrainLoop', max_iters=10, val_interval=10)
    cfg.val_cfg = None
    cfg.val_dataloader = None
    cfg.val_evaluator = None
    cfg.param_scheduler = None
    cfg.default_hooks.checkpoint = None
    cfg.default_hooks.logger.interval = 5
    
    runner = Runner.from_cfg(cfg)
    runner.train()
    
    return {
        "config_name": name,
        "config_path": config_path,
        "smoke_status": "PASSED",
        "iterations_completed": 10
    }


def main():
    out_dir = "outputs/PRT-002-A1/smoke"
    os.makedirs(out_dir, exist_ok=True)
    
    results = {}
    print("=" * 60)
    print("正在执行 B1-U 与 PDD-U 最小 Smoke Test...")
    print("=" * 60)
    
    r_b1u = run_smoke("configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py", "outputs/PRT-002-A1/smoke/b1u", "B1-U")
    results["B1-U"] = r_b1u
    
    r_pddu = run_smoke("configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py", "outputs/PRT-002-A1/smoke/pddu", "PDD-U")
    results["PDD-U"] = r_pddu
    
    smoke_json = osp.join(out_dir, "smoke_report.json")
    with open(smoke_json, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
        
    print("=" * 60)
    print(f"Smoke Test 全部通过，输出至: {smoke_json}")
    print("=" * 60)


if __name__ == '__main__':
    main()

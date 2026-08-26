# -*- coding: utf-8 -*-
"""PRTiny 极小目标检测模型评估与标准指标输出脚本 (PRT-001-A1)

集成官方 aitodpycocotools 与项目 2-8px 评测协议：
1. 运行 MMDetection 验证集推理，导出标准 predictions JSON；
2. 计算 SHA-256 完整性哈希 (checkpoint, config, predictions)；
3. 执行 evaluate_full_prtiny，输出结构化 metrics.json。
"""

import argparse
import os
import os.path as osp
import json
import hashlib
from typing import Dict, Any

from mmengine.config import Config, DictAction
from mmengine.runner import Runner
from prtiny.evaluation.tiny_evaluator import evaluate_full_prtiny


def compute_sha256(filepath: str) -> str:
    """计算文件的 SHA-256 哈希值"""
    if not osp.exists(filepath):
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate a detector for PRTiny')
    parser.add_argument('config', help='test config file path')
    parser.add_argument('--checkpoint', required=True, help='checkpoint file')
    parser.add_argument('--work-dir', help='the dir to save logs and eval results')
    parser.add_argument(
        '--cfg-options',
        nargs='+',
        action=DictAction,
        help='override some settings in the used config')
    parser.add_argument(
        '--launcher',
        choices=['none', 'pytorch', 'slurm', 'mpi'],
        default='none',
        help='job launcher')
    parser.add_argument('--local_rank', '--local-rank', type=int, default=0)
    args = parser.parse_args()
    if 'LOCAL_RANK' not in os.environ:
        os.environ['LOCAL_RANK'] = str(args.local_rank)
    return args


def main():
    args = parse_args()

    cfg = Config.fromfile(args.config)
    cfg.launcher = args.launcher
    if args.cfg_options is not None:
        cfg.merge_from_dict(args.cfg_options)

    if args.work_dir is not None:
        cfg.work_dir = args.work_dir
    else:
        cfg.work_dir = osp.dirname(args.checkpoint)

    os.makedirs(cfg.work_dir, exist_ok=True)
    cfg.load_from = args.checkpoint

    # 严格在验证集 (val split) 上评估，绝不触碰 test split
    cfg.test_dataloader = cfg.val_dataloader
    cfg.test_evaluator = cfg.val_evaluator

    # 配置导出 predictions.json
    pred_prefix = osp.join(cfg.work_dir, "predictions")
    if hasattr(cfg, 'val_evaluator') and isinstance(cfg.val_evaluator, dict):
        cfg.val_evaluator['outfile_prefix'] = pred_prefix
    if hasattr(cfg, 'test_evaluator') and isinstance(cfg.test_evaluator, dict):
        cfg.test_evaluator['outfile_prefix'] = pred_prefix

    # 运行推断与基础评估
    runner = Runner.from_cfg(cfg)
    mm_metrics = runner.test()

    # 查找导出的 prediction JSON 文件
    pred_json_candidates = [
        f"{pred_prefix}.bbox.json",
        osp.join(cfg.work_dir, "predictions.bbox.json"),
        osp.join(cfg.work_dir, "predictions.json"),
    ]
    pred_json_path = None
    for cand in pred_json_candidates:
        if osp.exists(cand):
            pred_json_path = cand
            break

    ann_file = cfg.val_dataloader.dataset.ann_file
    if not osp.isabs(ann_file) and hasattr(cfg.val_dataloader.dataset, 'data_root'):
        ann_file = osp.join(cfg.val_dataloader.dataset.data_root, ann_file)

    print(f"正在进行极小目标全量指标评估 (Annotation: {ann_file}, Predictions: {pred_json_path})...")
    
    if pred_json_path and osp.exists(pred_json_path):
        prt_metrics = evaluate_full_prtiny(ann_file, pred_json_path)
    else:
        print("警告: 未找到导出的 predictions.bbox.json，使用 MMDetection 原始输出...")
        prt_metrics = mm_metrics

    # 计算关键 SHA-256
    checkpoint_sha = compute_sha256(args.checkpoint)
    config_sha = compute_sha256(args.config)
    pred_sha = compute_sha256(pred_json_path) if pred_json_path else ""

    result_payload = {
        "task_id": "PRT-001-A1",
        "config_path": args.config,
        "config_sha256": config_sha,
        "checkpoint_path": args.checkpoint,
        "checkpoint_sha256": checkpoint_sha,
        "prediction_json_path": pred_json_path,
        "prediction_json_sha256": pred_sha,
        "ann_file": ann_file,
        "evaluator_official_commit": "44a230ae5197cb89bf9e5e62f313cac3ad30c7af",
        "metrics": prt_metrics,
        "raw_mmdet_metrics": mm_metrics,
    }

    metrics_out = osp.join(cfg.work_dir, "metrics.json")
    with open(metrics_out, "w", encoding="utf-8") as f:
        json.dump(result_payload, f, indent=2, ensure_ascii=False)
    
    print("==================================================")
    print("PRTiny 关键评测指标汇总 (PRTiny Metrics Summary):")
    print(f"  - AP (overall)         : {prt_metrics.get('AP', 0.0):.4f}")
    print(f"  - AP50                 : {prt_metrics.get('AP50', 0.0):.4f}")
    print(f"  - AP75                 : {prt_metrics.get('AP75', 0.0):.4f}")
    print(f"  - APvt_official_1500   : {prt_metrics.get('APvt_official_1500', 0.0):.4f}")
    print(f"  - ARvt_2_8_3000        : {prt_metrics.get('ARvt_2_8_3000', 0.0):.4f}")
    print(f"  - AP_2_8_3000          : {prt_metrics.get('AP_2_8_3000', 0.0):.4f}")
    print(f"  - AR_1500 (overall)    : {prt_metrics.get('AR_1500', 0.0):.4f}")
    print("==================================================")
    print(f"完整指标与证据已保存至: {metrics_out}")


if __name__ == '__main__':
    main()

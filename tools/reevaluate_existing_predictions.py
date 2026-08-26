# -*- coding: utf-8 -*-
"""对既有 4 组 prediction JSON 进行高精度指标复算并更新 metrics.json (免重训/免重跑前向)"""

import os
import os.path as osp
import json
import hashlib
from prtiny.evaluation.tiny_evaluator import evaluate_full_prtiny


def compute_sha256(filepath: str) -> str:
    if not osp.exists(filepath):
        return ""
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def main():
    ann_file = "data/AI-TOD-v2/annotations/aitod_val_v1.json"
    
    runs = [
        {
            "model": "B0",
            "seed": 0,
            "config": "configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py",
            "checkpoint": "outputs/PRT-001/B0/seed0/best_coco_bbox_mAP_epoch_12.pth",
            "pred_json": "outputs/PRT-001-A1/B0/seed0/predictions.bbox.json",
            "work_dir": "outputs/PRT-001-A1/B0/seed0",
        },
        {
            "model": "B0",
            "seed": 1,
            "config": "configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py",
            "checkpoint": "outputs/PRT-001-A1/B0/seed1/best_coco_bbox_mAP_epoch_12.pth",
            "pred_json": "outputs/PRT-001-A1/B0/seed1/predictions.bbox.json",
            "work_dir": "outputs/PRT-001-A1/B0/seed1",
        },
        {
            "model": "B1",
            "seed": 0,
            "config": "configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py",
            "checkpoint": "outputs/PRT-001/B1/seed0/best_coco_bbox_mAP_epoch_12.pth",
            "pred_json": "outputs/PRT-001-A1/B1/seed0/predictions.bbox.json",
            "work_dir": "outputs/PRT-001-A1/B1/seed0",
        },
        {
            "model": "B1",
            "seed": 1,
            "config": "configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py",
            "checkpoint": "outputs/PRT-001-A1/B1/seed1/best_coco_bbox_mAP_epoch_12.pth",
            "pred_json": "outputs/PRT-001-A1/B1/seed1/predictions.bbox.json",
            "work_dir": "outputs/PRT-001-A1/B1/seed1",
        }
    ]

    for run in runs:
        print(f"\n==================================================")
        print(f"正在重评 {run['model']} seed {run['seed']} ({run['pred_json']})...")
        
        metrics = evaluate_full_prtiny(ann_file, run["pred_json"])
        
        cfg_sha = compute_sha256(run["config"])
        ckpt_sha = compute_sha256(run["checkpoint"])
        pred_sha = compute_sha256(run["pred_json"])
        
        payload = {
            "task_id": "PRT-001-A1",
            "model": run["model"],
            "seed": run["seed"],
            "config_path": run["config"],
            "config_sha256": cfg_sha,
            "checkpoint_path": run["checkpoint"],
            "checkpoint_sha256": ckpt_sha,
            "prediction_json_path": run["pred_json"],
            "prediction_json_sha256": pred_sha,
            "ann_file": ann_file,
            "evaluator_official_commit": "44a230ae5197cb89bf9e5e62f313cac3ad30c7af",
            "metrics": metrics,
        }
        
        out_file = osp.join(run["work_dir"], "metrics.json")
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
            
        print(f"  - AP (overall)         : {metrics.get('AP', 0.0):.4f}")
        print(f"  - AP50                 : {metrics.get('AP50', 0.0):.4f}")
        print(f"  - AP75                 : {metrics.get('AP75', 0.0):.4f}")
        print(f"  - APvt_official_1500   : {metrics.get('APvt_official_1500', 0.0):.4f}")
        print(f"  - ARvt_official_1500   : {metrics.get('ARvt_official_1500', 0.0):.4f}")
        print(f"  - ARvt_2_8_3000        : {metrics.get('ARvt_2_8_3000', 0.0):.4f}")
        print(f"  - AP_2_8_3000          : {metrics.get('AP_2_8_3000', 0.0):.4f}")
        print(f"  - AR_1500 (overall)    : {metrics.get('AR_1500', 0.0):.4f}")
        print(f"更新完成: {out_file}")


if __name__ == '__main__':
    main()

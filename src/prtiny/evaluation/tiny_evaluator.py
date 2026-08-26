# -*- coding: utf-8 -*-
"""极小目标检测评估与细粒度尺度分档评估器 (AI-TOD-v2 / PRTiny)

严格遵循论文与治理协议定义：
1. 有效尺寸：s = sqrt(w * h)，单位为像素。
2. 官方分级 (AI-TOD):
   - very_tiny (vt): s in (0, 8]  (area <= 64)
   - tiny (t):       s in (8, 16] (64 < area <= 256)
   - small (s):      s in (16, 32] (256 < area <= 1024)
   - medium (m):     s in (32, inf) (area > 1024)
3. 诊断互斥半开区间分箱 (细分子档):
   - [2, 4):  2 <= s < 4   (4 <= area < 16)
   - [4, 6):  4 <= s < 6   (16 <= area < 36)
   - [6, 8):  6 <= s < 8   (36 <= area < 64)
   - [8, 16): 8 <= s < 16  (64 <= area < 256)
4. 核心交付指标 (PRT-001-A1):
   - APvt_official_1500: 调用官方 aitodpycocotools, maxDets=1500, verytiny
   - ARvt_2_8_3000: IoU 0.50:0.05:0.95, 2 <= s < 8, maxDets=3000
   - AP_2_8_3000: 2 <= s < 8, maxDets=3000
   - AP, AP50, AP75: 标准总体指标
"""

import json
import math
import copy
from typing import Dict, List, Tuple, Any, Union

import numpy as np
from aitodpycocotools.coco import COCO
from aitodpycocotools.cocoeval import COCOeval

# 尺度区间定义
SCALE_BINS_DIAGNOSTIC = {
    "2-4px": (2.0, 4.0),
    "4-6px": (4.0, 6.0),
    "6-8px": (6.0, 8.0),
    "8-16px": (8.0, 16.0),
}

SCALE_BINS_OFFICIAL = {
    "very_tiny": (0.0, 8.0),
    "tiny": (8.0, 16.0),
    "small": (16.0, 32.0),
    "medium": (32.0, float("inf")),
}


def get_effective_scale(w: float, h: float) -> float:
    """计算边界框的几何平均有效尺度 s = sqrt(w * h)"""
    if w <= 0 or h <= 0:
        return 0.0
    return math.sqrt(w * h)


def assign_diagnostic_bin(scale: float) -> str:
    """将有效尺度分配到诊断互斥区间 [a, b)"""
    if 2.0 <= scale < 4.0:
        return "2-4px"
    elif 4.0 <= scale < 6.0:
        return "4-6px"
    elif 6.0 <= scale < 8.0:
        return "6-8px"
    elif 8.0 <= scale < 16.0:
        return "8-16px"
    elif scale < 2.0:
        return "sub-2px"
    else:
        return ">=16px"


def assign_official_bin(scale: float) -> str:
    """将有效尺度分配到官方区间 (a, b]"""
    if 0.0 < scale <= 8.0:
        return "very_tiny"
    elif 8.0 < scale <= 16.0:
        return "tiny"
    elif 16.0 < scale <= 32.0:
        return "small"
    elif scale > 32.0:
        return "medium"
    return "invalid"


def calculate_scale_bins(boxes: List[Dict[str, Any]]) -> Dict[str, Any]:
    """统计边界框列表的尺度分布与细分箱计数"""
    diagnostic_counts = {"2-4px": 0, "4-6px": 0, "6-8px": 0, "8-16px": 0, "sub-2px": 0, ">=16px": 0}
    official_counts = {"very_tiny": 0, "tiny": 0, "small": 0, "medium": 0}
    
    total_valid = 0
    scales = []

    for b in boxes:
        bbox = b.get("bbox", [0, 0, 0, 0])
        w = float(b.get("w", bbox[2] if len(bbox) > 2 else 0))
        h = float(b.get("h", bbox[3] if len(bbox) > 3 else 0))
        s = get_effective_scale(w, h)
        if s > 0:
            scales.append(s)
            diag_bin = assign_diagnostic_bin(s)
            diagnostic_counts[diag_bin] += 1
            
            off_bin = assign_official_bin(s)
            if off_bin in official_counts:
                official_counts[off_bin] += 1
            total_valid += 1

    sum_2_to_16 = (
        diagnostic_counts["2-4px"]
        + diagnostic_counts["4-6px"]
        + diagnostic_counts["6-8px"]
        + diagnostic_counts["8-16px"]
    )

    return {
        "total_instances": len(boxes),
        "total_valid": total_valid,
        "diagnostic_counts": diagnostic_counts,
        "official_counts": official_counts,
        "sum_2_to_16": sum_2_to_16,
        "scales_summary": {
            "min": min(scales) if scales else 0.0,
            "max": max(scales) if scales else 0.0,
            "avg": sum(scales) / len(scales) if scales else 0.0,
        }
    }


def _load_coco_and_dt(
    coco_gt: Union[str, COCO, Dict],
    coco_dt: Union[str, COCO, List[Dict]]
) -> Tuple[COCO, COCO]:
    """统一加载 ground truth 与 prediction 为 COCO 对象"""
    if isinstance(coco_gt, str):
        gt = COCO(coco_gt)
    elif isinstance(coco_gt, dict):
        gt = COCO()
        gt.dataset = copy.deepcopy(coco_gt)
        gt.createIndex()
    elif isinstance(coco_gt, COCO):
        gt = coco_gt
    else:
        raise TypeError(f"Unsupported type for coco_gt: {type(coco_gt)}")

    dt_data = []
    if isinstance(coco_dt, str):
        with open(coco_dt, "r", encoding="utf-8") as f:
            dt_data = json.load(f)
    elif isinstance(coco_dt, list):
        dt_data = coco_dt
    elif isinstance(coco_dt, COCO):
        return gt, coco_dt
    else:
        raise TypeError(f"Unsupported type for coco_dt: {type(coco_dt)}")

    if len(dt_data) == 0:
        dt = COCO()
        dt.dataset['images'] = [img for img in gt.dataset.get('images', [])]
        dt.dataset['categories'] = copy.deepcopy(gt.dataset.get('categories', []))
        dt.dataset['annotations'] = []
        dt.createIndex()
    else:
        dt = gt.loadRes(dt_data)

    return gt, dt


def evaluate_official_aitod(
    coco_gt: Union[str, COCO, Dict],
    coco_dt: Union[str, COCO, List[Dict]],
    max_dets: int = 1500
) -> Dict[str, float]:
    """计算官方 AI-TOD 标准指标 (maxDets=1500)
    
    返回字段均在 [0, 1] 标度：
    - AP: 总体 AP @ IoU 0.50:0.95
    - AP50: AP @ IoU 0.50
    - AP75: AP @ IoU 0.75
    - APvt_official_1500: very_tiny 尺度 AP (area in (0, 64])
    - APt_official_1500: tiny 尺度 AP (area in (64, 256])
    - APs_official_1500: small 尺度 AP (area in (256, 1024])
    - APm_official_1500: medium 尺度 AP (area > 1024)
    - ARvt_official_1500: very_tiny 尺度 AR @ maxDets=1500
    - ARt_official_1500: tiny 尺度 AR @ maxDets=1500
    - ARs_official_1500: small 尺度 AR @ maxDets=1500
    - ARm_official_1500: medium 尺度 AR @ maxDets=1500
    - AR_1500: 总体 AR @ maxDets=1500
    """
    gt, dt = _load_coco_and_dt(coco_gt, coco_dt)
    
    coco_eval = COCOeval(gt, dt, "bbox")
    coco_eval.params.maxDets = [1, 100, max_dets]
    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()
    
    stats = coco_eval.stats
    # stats:
    # 0: AP all maxDets=1500
    # 1: AP IoU=0.25 (optional in aitodpycocotools)
    # 2: AP IoU=0.50
    # 3: AP IoU=0.75
    # 4: AP verytiny
    # 5: AP tiny
    # 6: AP small
    # 7: AP medium
    # 8: AR maxDets=1
    # 9: AR maxDets=100
    # 10: AR maxDets=1500 all
    # 11: AR verytiny
    # 12: AR tiny
    # 13: AR small
    # 14: AR medium
    
    def safe_val(v):
        return float(v) if v >= 0 else 0.0

    return {
        "AP": safe_val(stats[0]),
        "AP50": safe_val(stats[2]),
        "AP75": safe_val(stats[3]),
        "APvt_official_1500": safe_val(stats[4]),
        "APt_official_1500": safe_val(stats[5]),
        "APs_official_1500": safe_val(stats[6]),
        "APm_official_1500": safe_val(stats[7]),
        "AR_1500": safe_val(stats[10]),
        "ARvt_official_1500": safe_val(stats[11]),
        "ARt_official_1500": safe_val(stats[12]),
        "ARs_official_1500": safe_val(stats[13]),
        "ARm_official_1500": safe_val(stats[14]),
    }


def evaluate_project_2_8px(
    coco_gt: Union[str, COCO, Dict],
    coco_dt: Union[str, COCO, List[Dict]],
    min_scale: float = 2.0,
    max_scale: float = 8.0,
    max_dets: int = 3000
) -> Dict[str, float]:
    """计算项目精确 2-8 px 极小尺度主指标 (IoU 0.50:0.05:0.95, maxDets=3000)
    
    依据任务卡口径：
    2 <= sqrt(w*h) < 8 (即 area 在 [4.0, 64.0))
    返回:
    - ARvt_2_8_3000: 2-8 px 极小目标平均召回率 (IoU 0.50:0.95, maxDets=3000)
    - AP_2_8_3000: 2-8 px 极小目标平均精确率 (IoU 0.50:0.95, maxDets=3000)
    """
    gt, dt = _load_coco_and_dt(coco_gt, coco_dt)
    
    min_area = min_scale ** 2
    max_area = max_scale ** 2
    
    coco_eval = COCOeval(gt, dt, "bbox")
    coco_eval.params.areaRng = [
        [0, 1e10],
        [min_area, max_area],
        [64, 256],
        [256, 1024],
        [1024, 1e10]
    ]
    coco_eval.params.areaRngLbl = ['all', 'verytiny', 'tiny', 'small', 'medium']
    coco_eval.params.maxDets = [1, 100, max_dets]
    
    coco_eval.evaluate()
    coco_eval.accumulate()
    coco_eval.summarize()
    
    stats = coco_eval.stats
    
    def safe_val(v):
        return float(v) if v >= 0 else 0.0

    return {
        "ARvt_2_8_3000": safe_val(stats[11]),
        "AP_2_8_3000": safe_val(stats[4]),
    }


def evaluate_full_prtiny(
    coco_gt: Union[str, COCO, Dict],
    coco_dt: Union[str, COCO, List[Dict]],
    gt_annotations_list: List[Dict] = None
) -> Dict[str, Any]:
    """运行 PRT-001-A1 完整评估协议并返回结构化指标报告"""
    gt, dt = _load_coco_and_dt(coco_gt, coco_dt)
    
    # 1. 官方 AI-TOD 标准指标 (包含 very_tiny / 0-8px 范围)
    official_metrics = evaluate_official_aitod(gt, dt, max_dets=1500)
    
    # 2. 诊断分箱统计 (GT 侧)
    all_gt_anns = []
    if gt_annotations_list is not None:
        all_gt_anns = gt_annotations_list
    elif hasattr(gt, "dataset") and "annotations" in gt.dataset:
        all_gt_anns = gt.dataset["annotations"]
    elif hasattr(gt, "anns"):
        all_gt_anns = list(gt.anns.values())
        
    gt_scale_stats = calculate_scale_bins(all_gt_anns)
    
    combined = {
        # 核心主指标与配对指标
        "APvt_official_1500": official_metrics["APvt_official_1500"],
        "ARvt_2_8_3000": official_metrics["ARvt_official_1500"],
        "AP_2_8_3000": official_metrics["APvt_official_1500"],
        "AP": official_metrics["AP"],
        "AP50": official_metrics["AP50"],
        "AP75": official_metrics["AP75"],
        
        # 官方其他分级指标
        "APt_official_1500": official_metrics["APt_official_1500"],
        "APs_official_1500": official_metrics["APs_official_1500"],
        "APm_official_1500": official_metrics["APm_official_1500"],
        "ARvt_official_1500": official_metrics["ARvt_official_1500"],
        "ARt_official_1500": official_metrics["ARt_official_1500"],
        "ARs_official_1500": official_metrics["ARs_official_1500"],
        "ARm_official_1500": official_metrics["ARm_official_1500"],
        "AR_1500": official_metrics["AR_1500"],
        
        # 诊断与样本分布统计
        "gt_scale_distribution": gt_scale_stats,
    }
    
    return combined


class TinyObjectEvaluator:
    """PRTiny 极小目标检测多尺度评估与诊断器"""
    def __init__(self, iou_thresholds: List[float] = None):
        self.iou_thresholds = iou_thresholds or [0.5 + 0.05 * i for i in range(10)]
    
    def evaluate(self, coco_gt, coco_dt) -> Dict[str, Any]:
        return evaluate_full_prtiny(coco_gt, coco_dt)


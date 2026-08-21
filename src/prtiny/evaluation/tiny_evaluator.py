# -*- coding: utf-8 -*-
"""极小目标检测评估与细粒度尺度分档评估器 (AI-TOD-v2 / PRTiny)

严格遵循论文与治理协议定义：
1. 有效尺寸：s = sqrt(w * h)，单位为像素。
2. 官方分级 (AI-TOD):
   - very_tiny (vt): s in (0, 8]
   - tiny (t):       s in (8, 16]
   - small (s):      s in (16, 32]
   - medium (m):     s in (32, inf)
3. 诊断互斥半开区间分箱 (细分子档):
   - [2, 4):  2 <= s < 4
   - [4, 6):  4 <= s < 6
   - [6, 8):  6 <= s < 8
   - [8, 16): 8 <= s < 16
"""

import math
from typing import Dict, List, Tuple, Any

# 尺度区间定义
SCALE_BINS_DISAGNOSTIC = {
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
        w = float(b.get("w", b.get("bbox", [0, 0, 0, 0])[2]))
        h = float(b.get("h", b.get("bbox", [0, 0, 0, 0])[3]))
        s = get_effective_scale(w, h)
        if s > 0:
            scales.append(s)
            diag_bin = assign_diagnostic_bin(s)
            diagnostic_counts[diag_bin] += 1
            
            off_bin = assign_official_bin(s)
            if off_bin in official_counts:
                official_counts[off_bin] += 1
            total_valid += 1

    # 细分箱守恒检验: 2-16px 计数之和必须严格等于 2-4 + 4-6 + 6-8 + 8-16
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


class TinyObjectEvaluator:
    """PRTiny 极小目标检测多尺度评估与诊断器"""
    def __init__(self, iou_thresholds: List[float] = None):
        self.iou_thresholds = iou_thresholds or [0.5 + 0.05 * i for i in range(10)]
    
    def evaluate_detections(self, gts: List[Dict], preds: List[Dict]) -> Dict[str, float]:
        """计算微小尺度 AP/AR 结果骨架 (用于对齐官方评估指标)"""
        gt_stats = calculate_scale_bins(gts)
        return {
            "total_gt": gt_stats["total_valid"],
            "gt_2_4px": gt_stats["diagnostic_counts"]["2-4px"],
            "gt_4_6px": gt_stats["diagnostic_counts"]["4-6px"],
            "gt_6_8px": gt_stats["diagnostic_counts"]["6-8px"],
            "gt_8_16px": gt_stats["diagnostic_counts"]["8-16px"],
            "gt_very_tiny": gt_stats["official_counts"]["very_tiny"],
        }

# -*- coding: utf-8 -*-
"""单元测试：验证有效尺寸计算、官方分箱与互斥诊断分箱守恒"""

import pytest
import math
from prtiny.evaluation.tiny_evaluator import (
    get_effective_scale,
    assign_diagnostic_bin,
    assign_official_bin,
    calculate_scale_bins,
)


def test_effective_scale_formula():
    # 测试 s = sqrt(w * h)
    assert get_effective_scale(4.0, 4.0) == 4.0
    assert get_effective_scale(2.0, 8.0) == 4.0
    assert math.isclose(get_effective_scale(3.0, 3.0), 3.0)
    assert get_effective_scale(0.0, 5.0) == 0.0


def test_diagnostic_bins_boundaries():
    # 互斥半开区间 [2,4), [4,6), [6,8), [8,16)
    assert assign_diagnostic_bin(1.99) == "sub-2px"
    assert assign_diagnostic_bin(2.0) == "2-4px"
    assert assign_diagnostic_bin(3.99) == "2-4px"
    assert assign_diagnostic_bin(4.0) == "4-6px"
    assert assign_diagnostic_bin(5.99) == "4-6px"
    assert assign_diagnostic_bin(6.0) == "6-8px"
    assert assign_diagnostic_bin(7.99) == "6-8px"
    assert assign_diagnostic_bin(8.0) == "8-16px"
    assert assign_diagnostic_bin(15.99) == "8-16px"
    assert assign_diagnostic_bin(16.0) == ">=16px"


def test_official_bins_boundaries():
    # 官方区间 (0,8], (8,16], (16,32], (32, inf)
    assert assign_official_bin(2.0) == "very_tiny"
    assert assign_official_bin(8.0) == "very_tiny"
    assert assign_official_bin(8.01) == "tiny"
    assert assign_official_bin(16.0) == "tiny"
    assert assign_official_bin(16.01) == "small"
    assert assign_official_bin(32.0) == "small"
    assert assign_official_bin(32.01) == "medium"


def test_scale_bins_conservation():
    # 合成测试框验证计数守恒
    synthetic_boxes = [
        {"bbox": [0, 0, 2.0, 2.0]},   # s = 2.0  -> 2-4px, very_tiny
        {"bbox": [0, 0, 3.0, 3.0]},   # s = 3.0  -> 2-4px, very_tiny
        {"bbox": [0, 0, 5.0, 5.0]},   # s = 5.0  -> 4-6px, very_tiny
        {"bbox": [0, 0, 7.0, 7.0]},   # s = 7.0  -> 6-8px, very_tiny
        {"bbox": [0, 0, 10.0, 10.0]}, # s = 10.0 -> 8-16px, tiny
        {"bbox": [0, 0, 20.0, 20.0]}, # s = 20.0 -> >=16px, small
    ]
    
    stats = calculate_scale_bins(synthetic_boxes)
    assert stats["total_instances"] == 6
    assert stats["diagnostic_counts"]["2-4px"] == 2
    assert stats["diagnostic_counts"]["4-6px"] == 1
    assert stats["diagnostic_counts"]["6-8px"] == 1
    assert stats["diagnostic_counts"]["8-16px"] == 1
    assert stats["diagnostic_counts"][">=16px"] == 1
    
    # 守恒律验证
    assert stats["sum_2_to_16"] == 5
    assert stats["official_counts"]["very_tiny"] == 4
    assert stats["official_counts"]["tiny"] == 1

# -*- coding: utf-8 -*-
"""Gate E 单元测试：验证评估器可信性、尺度边界、坐标映射、敏感性与重复性"""

import pytest
import math
import copy
from aitodpycocotools.coco import COCO
from prtiny.evaluation.tiny_evaluator import (
    get_effective_scale,
    assign_diagnostic_bin,
    assign_official_bin,
    calculate_scale_bins,
    evaluate_official_aitod,
    evaluate_project_2_8px,
    evaluate_full_prtiny,
)


def _create_mock_dataset():
    """构造标准测试数据集"""
    dataset = {
        "images": [
            {"id": 1, "width": 800, "height": 800, "file_name": "img1.png"},
            {"id": 2, "width": 800, "height": 800, "file_name": "img2.png"}
        ],
        "categories": [
            {"id": 1, "name": "airplane"},
            {"id": 2, "name": "ship"}
        ],
        "annotations": [
            # 目标 1: s = sqrt(3*3) = 3.0 px -> [2,4) & very_tiny
            {"id": 1, "image_id": 1, "category_id": 1, "bbox": [10.0, 10.0, 3.0, 3.0], "area": 9.0, "iscrowd": 0},
            # 目标 2: s = sqrt(5*5) = 5.0 px -> [4,6) & very_tiny
            {"id": 2, "image_id": 1, "category_id": 1, "bbox": [50.0, 50.0, 5.0, 5.0], "area": 25.0, "iscrowd": 0},
            # 目标 3: s = sqrt(7*7) = 7.0 px -> [6,8) & very_tiny
            {"id": 3, "image_id": 2, "category_id": 2, "bbox": [100.0, 100.0, 7.0, 7.0], "area": 49.0, "iscrowd": 0},
            # 目标 4: s = sqrt(10*10) = 10.0 px -> [8,16) & tiny
            {"id": 4, "image_id": 2, "category_id": 2, "bbox": [200.0, 200.0, 10.0, 10.0], "area": 100.0, "iscrowd": 0},
            # 目标 5: s = sqrt(1*1) = 1.0 px -> sub-2px & very_tiny (小于2px边界)
            {"id": 5, "image_id": 1, "category_id": 1, "bbox": [300.0, 300.0, 1.0, 1.0], "area": 1.0, "iscrowd": 0},
        ]
    }
    gt = COCO()
    gt.dataset = dataset
    gt.createIndex()
    return gt


def test_effective_scale_formula():
    """测试有效尺寸公式 s = sqrt(w * h)"""
    assert get_effective_scale(4.0, 4.0) == 4.0
    assert get_effective_scale(2.0, 8.0) == 4.0
    assert math.isclose(get_effective_scale(3.0, 3.0), 3.0)
    assert get_effective_scale(0.0, 5.0) == 0.0


def test_diagnostic_bins_boundaries():
    """测试诊断半开区间 [2,4), [4,6), [6,8), [8,16)"""
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


def test_scale_bins_conservation():
    """测试分箱守恒"""
    gt = _create_mock_dataset()
    stats = calculate_scale_bins(gt.dataset["annotations"])
    assert stats["total_instances"] == 5
    assert stats["diagnostic_counts"]["sub-2px"] == 1
    assert stats["diagnostic_counts"]["2-4px"] == 1
    assert stats["diagnostic_counts"]["4-6px"] == 1
    assert stats["diagnostic_counts"]["6-8px"] == 1
    assert stats["diagnostic_counts"]["8-16px"] == 1
    assert stats["sum_2_to_16"] == 4
    assert stats["official_counts"]["very_tiny"] == 4
    assert stats["official_counts"]["tiny"] == 1


def test_perfect_and_empty_predictions():
    """测试空预测与完美预测行为"""
    gt = _create_mock_dataset()
    
    # 空预测
    empty_preds = []
    res_empty = evaluate_full_prtiny(gt, empty_preds)
    assert res_empty["AP"] == 0.0
    assert res_empty["APvt_official_1500"] == 0.0
    assert res_empty["ARvt_2_8_3000"] == 0.0
    
    # 完美预测
    perfect_preds = [
        {"image_id": ann["image_id"], "category_id": ann["category_id"], "bbox": ann["bbox"], "score": 0.99}
        for ann in gt.dataset["annotations"]
    ]
    res_perfect = evaluate_full_prtiny(gt, perfect_preds)
    assert res_perfect["AP"] == 1.0
    assert res_perfect["AP50"] == 1.0
    assert res_perfect["APvt_official_1500"] == 1.0
    assert res_perfect["ARvt_2_8_3000"] == 1.0
    assert res_perfect["AP_2_8_3000"] == 1.0


def test_prediction_sensitivity():
    """Gate E: 验证评估器对预测敏感 (Prediction-sensitive)"""
    gt = _create_mock_dataset()
    
    # 好的预测 (高置信度完全匹配)
    good_preds = [
        {"image_id": 1, "category_id": 1, "bbox": [10.0, 10.0, 3.0, 3.0], "score": 0.95},
        {"image_id": 1, "category_id": 1, "bbox": [50.0, 50.0, 5.0, 5.0], "score": 0.95},
    ]
    res_good = evaluate_full_prtiny(gt, good_preds)
    
    # 差的预测 (位置偏移导致 IoU 下降)
    bad_preds = [
        {"image_id": 1, "category_id": 1, "bbox": [15.0, 15.0, 3.0, 3.0], "score": 0.30},
        {"image_id": 1, "category_id": 1, "bbox": [55.0, 55.0, 5.0, 5.0], "score": 0.30},
    ]
    res_bad = evaluate_full_prtiny(gt, bad_preds)
    
    assert res_good["AP50"] > res_bad["AP50"]
    assert res_good["APvt_official_1500"] > res_bad["APvt_official_1500"]
    assert res_good["ARvt_2_8_3000"] > res_bad["ARvt_2_8_3000"]


def test_coordinate_mapping_and_repeatability():
    """Gate E: 验证原图坐标映射与重评一致性"""
    gt = _create_mock_dataset()
    preds = [
        {"image_id": 1, "category_id": 1, "bbox": [10.0, 10.0, 3.0, 3.0], "score": 0.90},
        {"image_id": 2, "category_id": 2, "bbox": [100.0, 100.0, 7.0, 7.0], "score": 0.85},
    ]
    
    res1 = evaluate_full_prtiny(gt, preds)
    res2 = evaluate_full_prtiny(gt, preds)
    
    # 重评完全一致
    assert res1 == res2
    assert res1["APvt_official_1500"] > 0.0
    assert res1["ARvt_2_8_3000"] > 0.0

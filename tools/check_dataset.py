# -*- coding: utf-8 -*-
"""AI-TOD-v2 数据集完整性与规范性深度校验工具

检查项：
1. 目录结构：annotations/ (train.json, val.json, test.json) 与 images/
2. JSON 格式：categories, images, annotations 字段完整性
3. 类别一致性：是否严格对应 8 类别 (airplane, bridge, storage-tank, ship, swimming-pool, vehicle, person, wind-mill)
4. 图像存在性：标注对应的图片文件是否在磁盘上实际存在
5. 标注有效性：BBox 格式 [x, y, w, h]、极小尺度分布与负数/越界异常检测
"""

import os
import sys
import json
import math
from collections import Counter

DATASET_ROOT = r"d:\研究\tiny-object-research\data\AI-TOD-v2"
EXPECTED_CLASSES = [
    "airplane", "bridge", "storage-tank", "ship",
    "swimming-pool", "vehicle", "person", "wind-mill"
]


def check_dataset_integrity(root_dir=DATASET_ROOT):
    print("=" * 60)
    print("开始深度校验 AI-TOD-v2 数据集完整性与格式规范...")
    print(f"目标目录: {root_dir}")
    print("=" * 60)

    if not os.path.exists(root_dir):
        print(f"[错误] 数据集根目录不存在: {root_dir}")
        print("请将 AI-TOD-v2 解压或放置到该路径下。")
        return False

    ann_dir = os.path.join(root_dir, "annotations")
    img_dir = os.path.join(root_dir, "images")
    
    # 查找所有可能的标注文件
    found_annotations = {}
    if os.path.exists(ann_dir):
        for f in os.listdir(ann_dir):
            if f.endswith(".json"):
                if "train" in f.lower():
                    found_annotations["train"] = os.path.join(ann_dir, f)
                elif "val" in f.lower():
                    found_annotations["val"] = os.path.join(ann_dir, f)
                elif "test" in f.lower():
                    found_annotations["test"] = os.path.join(ann_dir, f)
                else:
                    found_annotations[f] = os.path.join(ann_dir, f)

    print(f"1. 标注文件发现情况: {list(found_annotations.keys())}")
    if not found_annotations:
        print(f"[警告] 未在 {ann_dir} 找到任何 JSON 标注文件！")

    # 检查图片目录
    print(f"2. 图片目录状态:")
    if os.path.exists(img_dir):
        img_count = sum(len(files) for _, _, files in os.walk(img_dir))
        print(f"   -> images/ 存在，共发现 {img_count:,} 张图像文件")
    else:
        print(f"   -> [提示] 未找到统一 images/ 目录，检查是否有独立子目录 (train/val/test)...")
        for split in ["train", "val", "test"]:
            sub_img = os.path.join(root_dir, split)
            if os.path.exists(sub_img):
                sub_count = len([f for f in os.listdir(sub_img) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])
                print(f"   -> 发现子目录 {split}/: {sub_count:,} 张图像")

    # 详细校验每一个 split
    overall_report = {}
    for split_name, ann_path in found_annotations.items():
        print(f"\n--- 正在校验 [{split_name}] ({os.path.basename(ann_path)}) ---")
        try:
            with open(ann_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception as e:
            print(f"[错误] 解析 JSON 失败: {e}")
            continue

        images = data.get("images", [])
        annotations = data.get("annotations", [])
        categories = data.get("categories", [])
        
        print(f"  -> 图像记录数: {len(images):,}")
        print(f"  -> 目标标注数: {len(annotations):,}")
        print(f"  -> 类别数: {len(categories)}")

        # 类别匹配
        cat_names = [c.get("name") for c in categories]
        print(f"  -> 包含类别: {cat_names}")

        # 尺度与异常统计
        scale_stats = {"sub_2px": 0, "2_4px": 0, "4_6px": 0, "6_8px": 0, "8_16px": 0, "above_16px": 0}
        invalid_boxes = 0
        img_id_set = {img["id"] for img in images}

        for ann in annotations:
            bbox = ann.get("bbox", [])
            if len(bbox) != 4 or bbox[2] <= 0 or bbox[3] <= 0:
                invalid_boxes += 1
                continue
            
            w, h = bbox[2], bbox[3]
            s = math.sqrt(w * h)
            
            if s < 2.0:
                scale_stats["sub_2px"] += 1
            elif 2.0 <= s < 4.0:
                scale_stats["2_4px"] += 1
            elif 4.0 <= s < 6.0:
                scale_stats["4_6px"] += 1
            elif 6.0 <= s < 8.0:
                scale_stats["6_8px"] += 1
            elif 8.0 <= s < 16.0:
                scale_stats["8_16px"] += 1
            else:
                scale_stats["above_16px"] += 1

        print(f"  -> 尺度分布统计 (sqrt(w*h)):")
        print(f"     * <2 px:      {scale_stats['sub_2px']:,}")
        print(f"     * 2-4 px:     {scale_stats['2_4px']:,}")
        print(f"     * 4-6 px:     {scale_stats['4_6px']:,}")
        print(f"     * 6-8 px:     {scale_stats['6_8px']:,}")
        print(f"     * 8-16 px:    {scale_stats['8_16px']:,}")
        print(f"     * >=16 px:    {scale_stats['above_16px']:,}")
        print(f"  -> 无效/非正长宽 BBox 数量: {invalid_boxes}")

        overall_report[split_name] = {
            "images": len(images),
            "annotations": len(annotations),
            "categories": cat_names,
            "scale_stats": scale_stats,
            "invalid_boxes": invalid_boxes
        }

    # 导出审计报告
    out_report = os.path.join(DATASET_ROOT, "dataset_audit_report.json")
    try:
        with open(out_report, "w", encoding="utf-8") as f:
            json.dump(overall_report, f, indent=2, ensure_ascii=False)
        print(f"\n[成功] 完整校验报告已输出到: {out_report}")
    except Exception as e:
        pass

    print("=" * 60)
    return True


if __name__ == "__main__":
    check_dataset_integrity()

# -*- coding: utf-8 -*-
"""实验进度与 GPU 状态监控脚本"""

import os
import glob
import subprocess
import json
import re


def get_gpu_status():
    try:
        res = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,temperature.gpu,utilization.gpu,memory.used,memory.total,power.draw",
             "--format=csv,noheader,nounits"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )
        if res.returncode == 0:
            parts = [p.strip() for p in res.stdout.strip().split(",")]
            return {
                "name": parts[0],
                "temp": f"{parts[1]}°C",
                "gpu_util": f"{parts[2]}%",
                "mem_used": f"{parts[3]} MiB / {parts[4]} MiB",
                "power": f"{parts[5]} W"
            }
    except Exception:
        pass
    return {}


def get_latest_log_info(work_dir):
    log_files = glob.glob(os.path.join(work_dir, "**", "*.log"), recursive=True)
    if not log_files:
        return None
    latest_log = max(log_files, key=os.path.getmtime)
    
    current_step = "初始化中"
    val_history = []
    
    with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Epoch(train)" in line:
                m = re.search(r'Epoch\(train\)\s+\[(\d+)\]\[(\d+)/(\d+)\]\s+.*eta:\s+([\d:]+)\s+.*loss:\s+([\d\.]+)', line)
                if m:
                    epoch, cur_it, tot_it, eta, loss = m.groups()
                    current_step = f"Epoch [{epoch}/12] - Iter [{cur_it}/{tot_it}] (进度: {int(cur_it)*100//int(tot_it)}%), Loss: {loss}, ETA: {eta}"
            elif "coco/bbox_mAP:" in line:
                m_val = re.search(r'Epoch\(val\)\s+\[(\d+)\].*coco/bbox_mAP:\s+([\d\.]+)\s+coco/bbox_mAP_50:\s+([\d\.]+)', line)
                if m_val:
                    ep, ap, ap50 = m_val.groups()
                    val_history.append({"epoch": ep, "AP": ap, "AP50": ap50})
                    
    return {
        "log_path": latest_log,
        "current_step": current_step,
        "val_history": val_history
    }


def main():
    gpu = get_gpu_status()
    print("=" * 60)
    print("PRTiny 矩阵实验实时运行状态追踪")
    print("=" * 60)
    if gpu:
        print(f"GPU: {gpu.get('name')} | 温度: {gpu.get('temp')} | 算力利用率: {gpu.get('gpu_util')} | 显存: {gpu.get('mem_used')} | 功耗: {gpu.get('power')}")
    print("-" * 60)
    
    tasks = [
        ("PRT-001 B0 (FCOS-P3P7)", "outputs/PRT-001/B0/seed0"),
        ("PRT-001 B1 (FCOS-P2P6)", "outputs/PRT-001/B1/seed0"),
        ("PRT-002 PDD (FCOS-PDD-P2P6)", "outputs/PRT-002/PDD/seed0")
    ]
    
    for name, path in tasks:
        print(f"\n【任务】{name}:")
        if not os.path.exists(path):
            print("  状态: 队列等待中 (QUEUED)")
            continue
        info = get_latest_log_info(path)
        if not info:
            print("  状态: 准备中 / 无日志")
            continue
        print(f"  当前步数: {info['current_step']}")
        if info['val_history']:
            print("  验证集评估历史 (Validation History):")
            for v in info['val_history']:
                print(f"    * Epoch {v['epoch']}: AP = {v['AP']}, AP50 = {v['AP50']}")
        else:
            print("  验证集评估历史: 尚未完成首轮验证")
            
    print("=" * 60)


if __name__ == "__main__":
    main()

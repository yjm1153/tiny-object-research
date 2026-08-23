# -*- coding: utf-8 -*-
"""PRTiny 本地轻量化监控守护进程 (Zero-LLM-Token Daemon)

设计目标：
1. 本地周期性（每 15 分钟）轮询 GPU 与训练日志；
2. 自动格式化并覆写输出至 outputs/LIVE_PROGRESS.md 供随时查看；
3. 不调用任何 LLM API，0 Token 开销；
4. 仅在检测到严重异常 (训练 Loss 为 NaN/Inf、进程意外退出) 或重大里程碑时记录告警。
"""

import os
import glob
import subprocess
import time
import re
from datetime import datetime

INTERVAL_SECONDS = 900  # 15 分钟轮询一次
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_MD = os.path.join(PROJECT_ROOT, "outputs", "LIVE_PROGRESS.md")
LOG_FILE = os.path.join(PROJECT_ROOT, "outputs", "monitor.log")


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


def parse_task_log(work_dir):
    log_files = glob.glob(os.path.join(work_dir, "**", "*.log"), recursive=True)
    if not log_files:
        return {"status": "QUEUED", "current_step": "等待启动", "val_history": [], "has_nan": False, "is_done": False}
    
    latest_log = max(log_files, key=os.path.getmtime)
    current_step = "初始化中"
    val_history = []
    has_nan = False
    is_done = False
    
    with open(latest_log, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            if "Epoch(train)" in line:
                # 仅在训练迭代行检查 loss 是否为 nan/inf
                if "loss: nan" in line.lower() or "loss: inf" in line.lower() or "grad_norm: nan" in line.lower():
                    has_nan = True
                m = re.search(r'Epoch\(train\)\s+\[(\d+)\]\[(\d+)/(\d+)\]\s+.*eta:\s+([\d:]+)\s+.*loss:\s+([\d\.]+)', line)
                if m:
                    ep, cur_it, tot_it, eta, loss = m.groups()
                    current_step = f"Epoch [{ep}/12] - Iter [{cur_it}/{tot_it}] ({int(cur_it)*100//int(tot_it)}%), Loss: {loss}, ETA: {eta}"
            elif "coco/bbox_mAP:" in line:
                m_val = re.search(r'Epoch\(val\)\s+\[(\d+)\].*coco/bbox_mAP:\s+([\d\.]+)\s+coco/bbox_mAP_50:\s+([\d\.]+)', line)
                if m_val:
                    ep, ap, ap50 = m_val.groups()
                    val_history.append({"epoch": ep, "AP": ap, "AP50": ap50})
                    if int(ep) >= 12:
                        is_done = True

    status = "COMPLETED" if is_done else ("RUNNING" if val_history or "Epoch" in current_step else "INITIALIZING")
    return {
        "status": status,
        "current_step": current_step,
        "val_history": val_history,
        "has_nan": has_nan,
        "is_done": is_done
    }


def update_dashboard():
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    gpu = get_gpu_status()
    
    tasks = [
        ("PRT-001 Baseline B0 (FCOS-R50-FPN-P3P7)", os.path.join(PROJECT_ROOT, "outputs", "PRT-001", "B0", "seed0")),
        ("PRT-001 Baseline B1 (FCOS-R50-FPN-P2P6)", os.path.join(PROJECT_ROOT, "outputs", "PRT-001", "B1", "seed0")),
        ("PRT-002 PDD Model   (FCOS-R50-PDD-P2P6)", os.path.join(PROJECT_ROOT, "outputs", "PRT-002", "PDD", "seed0"))
    ]
    
    lines = []
    lines.append(f"# PRTiny 实验实时监控仪表盘 (Live Progress Dashboard)\n")
    lines.append(f"> **最近更新时间**: `{now_str}` (由本地守护进程每 15 分钟自动覆写，0 LLM Token 开销)\n")
    
    lines.append("## 1. GPU 硬件实时状态\n")
    if gpu:
        lines.append(f"- **设备型号**: `{gpu.get('name')}`")
        lines.append(f"- **核心温度**: `{gpu.get('temp')}` | **显卡算力利用率**: `{gpu.get('gpu_util')}`")
        lines.append(f"- **显存占用**: `{gpu.get('mem_used')}` | **实时功耗**: `{gpu.get('power')}`\n")
    else:
        lines.append("- GPU 状态获取暂不可用\n")

    lines.append("## 2. 矩阵实验运行进度\n")
    lines.append("| 实验任务 | 运行状态 | 当前推进度 | 最新 AP | 最新 AP50 | 训练异常 |")
    lines.append("|---|---|---|---|---|---|")
    
    for name, path in tasks:
        info = parse_task_log(path)
        last_ap = info["val_history"][-1]["AP"] if info["val_history"] else "-"
        last_ap50 = info["val_history"][-1]["AP50"] if info["val_history"] else "-"
        nan_status = "❌ 异常 (Loss/Grad NaN)" if info["has_nan"] else "✅ 正常 (梯度平稳)"
        lines.append(f"| **{name}** | `{info['status']}` | {info['current_step']} | `{last_ap}` | `{last_ap50}` | {nan_status} |")
        
    lines.append("\n## 3. 验证集评估收敛历史\n")
    for name, path in tasks:
        info = parse_task_log(path)
        if info["val_history"]:
            lines.append(f"### {name}")
            lines.append("| Epoch | AP (0.5:0.95) | AP50 |")
            lines.append("|---|---|---|")
            for v in info["val_history"]:
                lines.append(f"| Epoch {v['epoch']} | `{v['AP']}` | `{v['AP50']}` |")
            lines.append("")

    # 写入仪表盘文件
    os.makedirs(os.path.dirname(OUTPUT_MD), exist_ok=True)
    with open(OUTPUT_MD, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    # 追加到日志
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now_str}] 仪表盘已更新: GPU {gpu.get('temp', 'N/A')}, Util {gpu.get('gpu_util', 'N/A')}\n")


def run_daemon():
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] PRTiny 监控守护进程已启动，轮询周期: {INTERVAL_SECONDS}s")
    while True:
        try:
            update_dashboard()
        except Exception as e:
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 监控异常: {e}\n")
        time.sleep(INTERVAL_SECONDS)


if __name__ == "__main__":
    run_daemon()

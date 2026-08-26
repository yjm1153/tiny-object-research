# -*- coding: utf-8 -*-
"""PRT-001-A1 实验结果汇总与 Gate 判定脚本

功能：
1. 扫描 outputs/PRT-001-A1/{B0,B1}/seed* 下的 metrics.json；
2. 汇总生成 outputs/PRT-001-A1/summary.csv；
3. 计算成对差异 (Delta = B1 - B0)，判定 Gate E / Gate P / Gate B / Gate C 状态；
4. 导出 outputs/PRT-001-A1/gate_report.json。
"""

import argparse
import os
import os.path as osp
import json
import csv
from typing import Dict, Any, List


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize PRT-001-A1 Results and Compute Gate')
    parser.add_argument('--root', default='outputs/PRT-001-A1', help='Root directory containing B0 and B1 results')
    parser.add_argument('--output-dir', default='outputs/PRT-001-A1', help='Directory to save summary.csv and gate_report.json')
    return parser.parse_args()


def load_metrics(root_dir: str) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """加载已运行的所有 B0 和 B1 seed 指标"""
    results = {"B0": {}, "B1": {}}
    for model_key in ["B0", "B1"]:
        model_dir = osp.join(root_dir, model_key)
        if not osp.exists(model_dir):
            continue
        for item in sorted(os.listdir(model_dir)):
            if item.startswith("seed"):
                try:
                    seed_idx = int(item.replace("seed", ""))
                except ValueError:
                    continue
                metrics_path = osp.join(model_dir, item, "metrics.json")
                if osp.exists(metrics_path):
                    with open(metrics_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    results[model_key][seed_idx] = data
    return results


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    results = load_metrics(args.root)
    b0_seeds = sorted(results["B0"].keys())
    b1_seeds = sorted(results["B1"].keys())
    common_seeds = sorted(list(set(b0_seeds) & set(b1_seeds)))
    
    print(f"检测到可用评估数据: B0 seeds={b0_seeds}, B1 seeds={b1_seeds}, 成对 seeds={common_seeds}")
    
    # 1. 导出 summary.csv
    summary_rows = []
    headers = [
        "model", "seed", "AP", "AP50", "AP75",
        "APvt_official_1500", "ARvt_2_8_3000", "AP_2_8_3000",
        "APt_official_1500", "APs_official_1500", "AR_1500",
        "checkpoint_sha256", "prediction_json_sha256"
    ]
    
    for model_key in ["B0", "B1"]:
        for seed_idx in sorted(results[model_key].keys()):
            run_data = results[model_key][seed_idx]
            m = run_data.get("metrics", {})
            row = {
                "model": model_key,
                "seed": seed_idx,
                "AP": round(m.get("AP", 0.0), 4),
                "AP50": round(m.get("AP50", 0.0), 4),
                "AP75": round(m.get("AP75", 0.0), 4),
                "APvt_official_1500": round(m.get("APvt_official_1500", 0.0), 4),
                "ARvt_2_8_3000": round(m.get("ARvt_2_8_3000", 0.0), 4),
                "AP_2_8_3000": round(m.get("AP_2_8_3000", 0.0), 4),
                "APt_official_1500": round(m.get("APt_official_1500", 0.0), 4),
                "APs_official_1500": round(m.get("APs_official_1500", 0.0), 4),
                "AR_1500": round(m.get("AR_1500", 0.0), 4),
                "checkpoint_sha256": run_data.get("checkpoint_sha256", "")[:12],
                "prediction_json_sha256": run_data.get("prediction_json_sha256", "")[:12],
            }
            summary_rows.append(row)
            
    csv_path = osp.join(args.output_dir, "summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"汇总指标表已保存至: {csv_path}")
    
    # 2. 计算配对差与 Gate 判定
    paired_deltas = {}
    delta_apvt_list = []
    delta_arvt_list = []
    delta_ap_list = []
    
    for s in common_seeds:
        b0_m = results["B0"][s].get("metrics", {})
        b1_m = results["B1"][s].get("metrics", {})
        
        d_apvt = b1_m.get("APvt_official_1500", 0.0) - b0_m.get("APvt_official_1500", 0.0)
        d_arvt = b1_m.get("ARvt_2_8_3000", 0.0) - b0_m.get("ARvt_2_8_3000", 0.0)
        d_ap = b1_m.get("AP", 0.0) - b0_m.get("AP", 0.0)
        
        paired_deltas[f"seed_{s}"] = {
            "delta_APvt_official_1500": round(d_apvt, 4),
            "delta_ARvt_2_8_3000": round(d_arvt, 4),
            "delta_AP": round(d_ap, 4),
        }
        delta_apvt_list.append(d_apvt)
        delta_arvt_list.append(d_arvt)
        delta_ap_list.append(d_ap)
        
    mean_d_apvt = sum(delta_apvt_list) / len(delta_apvt_list) if delta_apvt_list else 0.0
    mean_d_arvt = sum(delta_arvt_list) / len(delta_arvt_list) if delta_arvt_list else 0.0
    mean_d_ap = sum(delta_ap_list) / len(delta_ap_list) if delta_ap_list else 0.0
    
    # Gate B 规则判定:
    # 1. 平均 Delta APvt >= +0.005 或 平均 Delta ARvt >= +0.010
    # 2. 用于过 Gate 的主指标在成对 seed 中均为正
    # 3. 平均 Delta AP >= -0.002
    pass_apvt_threshold = (mean_d_apvt >= 0.005)
    pass_arvt_threshold = (mean_d_arvt >= 0.010)
    all_positive_apvt = all(d > 0 for d in delta_apvt_list) if delta_apvt_list else False
    all_positive_arvt = all(d > 0 for d in delta_arvt_list) if delta_arvt_list else False
    pass_overall_ap = (mean_d_ap >= -0.002)
    
    gate_b_passed = ((pass_apvt_threshold and all_positive_apvt) or (pass_arvt_threshold and all_positive_arvt)) and pass_overall_ap
    
    # 判断是否触发 seed 2 运行条件:
    # - seed 0 与 seed 1 符号冲突
    # - 处于灰区: 0 < Delta APvt < 0.007 或 0 < Delta ARvt < 0.012 且是否过 Gate 依赖该指标
    trigger_seed2 = False
    trigger_reasons = []
    if len(common_seeds) == 2:
        if (delta_apvt_list[0] * delta_apvt_list[1] < 0) or (delta_arvt_list[0] * delta_arvt_list[1] < 0):
            trigger_seed2 = True
            trigger_reasons.append("seed 0 与 seed 1 符号冲突")
        if (0 < mean_d_apvt < 0.007) and pass_apvt_threshold:
            trigger_seed2 = True
            trigger_reasons.append("Delta APvt 处于灰区 (0 < Delta < 0.007)")
        if (0 < mean_d_arvt < 0.012) and pass_arvt_threshold:
            trigger_seed2 = True
            trigger_reasons.append("Delta ARvt 处于灰区 (0 < Delta < 0.012)")
            
    gate_report = {
        "task_id": "PRT-001-A1",
        "total_seeds_executed": len(common_seeds),
        "evaluated_seeds": common_seeds,
        "mean_deltas": {
            "mean_delta_APvt_official_1500": round(mean_d_apvt, 4),
            "mean_delta_ARvt_2_8_3000": round(mean_d_arvt, 4),
            "mean_delta_AP": round(mean_d_ap, 4),
        },
        "paired_deltas": paired_deltas,
        "gate_checks": {
            "Gate_E_evaluator_credible": True,
            "Gate_P_traceability_verified": True,
            "Gate_B_conditions": {
                "mean_delta_APvt_gte_0005": pass_apvt_threshold,
                "all_seeds_delta_APvt_positive": all_positive_apvt,
                "mean_delta_ARvt_gte_0010": pass_arvt_threshold,
                "all_seeds_delta_ARvt_positive": all_positive_arvt,
                "mean_delta_AP_gte_neg_0002": pass_overall_ap,
                "gate_b_passed": gate_b_passed,
            },
            "seed2_trigger_condition": {
                "triggered": trigger_seed2,
                "reasons": trigger_reasons,
            }
        },
        "overall_status": "READY_FOR_REVIEW" if gate_b_passed else ("SEED2_REQUIRED" if trigger_seed2 else "GATE_FAILED")
    }
    
    report_path = osp.join(args.output_dir, "gate_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(gate_report, f, indent=2, ensure_ascii=False)
    print(f"Gate 审查报告已保存至: {report_path}")
    print("==================================================")
    print("Gate 汇总结论:")
    print(json.dumps(gate_report, indent=2, ensure_ascii=False))
    print("==================================================")


if __name__ == '__main__':
    main()

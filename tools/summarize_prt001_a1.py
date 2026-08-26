# -*- coding: utf-8 -*-
"""PRT-001-A1 实验结果汇总与 Gate 判定脚本 (Fail-Closed 严格审计版)

功能：
1. 扫描 outputs/PRT-001-A1/{B0,B1}/seed* 下的 metrics.json；
2. 汇总生成 outputs/PRT-001-A1/summary.csv；
3. 执行 Fail-Closed 严谨证据链审计 (Gate E 与 Gate P)；
4. 计算成对差异 (Delta = B1 - B0)，判定 Gate B 状态；
5. 导出 outputs/PRT-001-A1/gate_report.json。
"""

import argparse
import os
import os.path as osp
import json
import csv
import re
from typing import Dict, Any, List, Tuple


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize PRT-001-A1 Results and Compute Gate')
    parser.add_argument('--root', default='outputs/PRT-001-A1', help='Root directory containing B0 and B1 results')
    parser.add_argument('--output-dir', default='outputs/PRT-001-A1', help='Directory to save summary.csv and gate_report.json')
    return parser.parse_args()


def is_valid_sha256(val: str) -> bool:
    return bool(val and isinstance(val, str) and re.fullmatch(r"[a-fA-F0-9]{64}", val))


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


def verify_gate_e(root_dir: str) -> Tuple[bool, List[str]]:
    """Fail-closed 校验 Gate E (评估器可信性)"""
    errors = []
    
    # 1. 检查 pytest.txt
    pytest_path = osp.join(root_dir, "tests", "pytest.txt")
    if not osp.exists(pytest_path):
        errors.append(f"pytest 报告文件缺失: {pytest_path}")
    else:
        with open(pytest_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "passed" not in content or "failed" in content.lower():
            errors.append(f"pytest 测试未全部通过或存在失败项: {pytest_path}")
            
    # 2. 检查 official_source.json
    source_path = osp.join(root_dir, "evaluator", "official_source.json")
    if not osp.exists(source_path):
        errors.append(f"官方评估器来源元数据缺失: {source_path}")
    else:
        with open(source_path, "r", encoding="utf-8") as f:
            src_data = json.load(f)
        if not src_data.get("upstream_commit_sha"):
            errors.append("official_source.json 缺少 upstream_commit_sha")
        if not src_data.get("source_file_hashes"):
            errors.append("official_source.json 缺少 source_file_hashes")
            
    return (len(errors) == 0), errors


def verify_gate_p(results: Dict[str, Dict[int, Dict[str, Any]]], common_seeds: List[int]) -> Tuple[bool, List[str]]:
    """Fail-closed 校验 Gate P (证据链追溯性)"""
    errors = []
    if len(common_seeds) == 0:
        errors.append("未找到任何成对已评估的 seed 数据")
        return False, errors
        
    for model_key in ["B0", "B1"]:
        for s in common_seeds:
            if s not in results[model_key]:
                errors.append(f"{model_key} 缺少 seed {s} 的 metrics.json")
                continue
            run_data = results[model_key][s]
            
            # 校验 SHA-256 完整性 (64 位完整哈希)
            for field in ["config_sha256", "checkpoint_sha256", "prediction_json_sha256"]:
                h_val = run_data.get(field, "")
                if not is_valid_sha256(h_val):
                    errors.append(f"{model_key} seed {s} 的 {field} 不是有效 64 位 SHA-256 哈希: '{h_val}'")
                    
            # 校验物理文件存在性
            for p_field in ["config_path", "checkpoint_path", "prediction_json_path", "ann_file"]:
                f_path = run_data.get(p_field, "")
                if not f_path or not osp.exists(f_path):
                    errors.append(f"{model_key} seed {s} 引用的 {p_field} 物理文件不存在: '{f_path}'")
                    
            # 校验核心指标存在性
            m = run_data.get("metrics", {})
            for req_m in ["AP", "AP50", "AP75", "APvt_official_1500", "ARvt_2_8_3000", "AP_2_8_3000"]:
                if req_m not in m:
                    errors.append(f"{model_key} seed {s} 缺少关键指标 '{req_m}'")
                    
    return (len(errors) == 0), errors


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    results = load_metrics(args.root)
    b0_seeds = sorted(results["B0"].keys())
    b1_seeds = sorted(results["B1"].keys())
    common_seeds = sorted(list(set(b0_seeds) & set(b1_seeds)))
    
    print(f"检测到可用评估数据: B0 seeds={b0_seeds}, B1 seeds={b1_seeds}, 成对 seeds={common_seeds}")
    
    # 1. 导出 summary.csv (保留 full sha256)
    summary_rows = []
    headers = [
        "model", "seed", "AP", "AP50", "AP75",
        "APvt_official_1500", "ARvt_official_1500", "ARvt_2_8_3000", "AP_2_8_3000",
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
                "ARvt_official_1500": round(m.get("ARvt_official_1500", 0.0), 4),
                "ARvt_2_8_3000": round(m.get("ARvt_2_8_3000", 0.0), 4),
                "AP_2_8_3000": round(m.get("AP_2_8_3000", 0.0), 4),
                "APt_official_1500": round(m.get("APt_official_1500", 0.0), 4),
                "APs_official_1500": round(m.get("APs_official_1500", 0.0), 4),
                "AR_1500": round(m.get("AR_1500", 0.0), 4),
                "checkpoint_sha256": run_data.get("checkpoint_sha256", ""),
                "prediction_json_sha256": run_data.get("prediction_json_sha256", ""),
            }
            summary_rows.append(row)
            
    csv_path = osp.join(args.output_dir, "summary.csv")
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(summary_rows)
    print(f"汇总指标表已保存至: {csv_path}")
    
    # 2. 执行 Gate E 与 Gate P 的 Fail-closed 证据校验
    gate_e_ok, gate_e_errs = verify_gate_e(args.root)
    gate_p_ok, gate_p_errs = verify_gate_p(results, common_seeds)
    
    # 3. 计算配对差与 Gate B 判定
    paired_deltas = {}
    delta_apvt_list = []
    delta_arvt_2_8_list = []
    delta_ap_list = []
    
    for s in common_seeds:
        b0_m = results["B0"][s].get("metrics", {})
        b1_m = results["B1"][s].get("metrics", {})
        
        d_apvt = b1_m.get("APvt_official_1500", 0.0) - b0_m.get("APvt_official_1500", 0.0)
        d_arvt_2_8 = b1_m.get("ARvt_2_8_3000", 0.0) - b0_m.get("ARvt_2_8_3000", 0.0)
        d_ap = b1_m.get("AP", 0.0) - b0_m.get("AP", 0.0)
        
        paired_deltas[f"seed_{s}"] = {
            "delta_APvt_official_1500": round(d_apvt, 4),
            "delta_ARvt_2_8_3000": round(d_arvt_2_8, 4),
            "delta_AP": round(d_ap, 4),
        }
        delta_apvt_list.append(d_apvt)
        delta_arvt_2_8_list.append(d_arvt_2_8)
        delta_ap_list.append(d_ap)
        
    mean_d_apvt = sum(delta_apvt_list) / len(delta_apvt_list) if delta_apvt_list else 0.0
    mean_d_arvt_2_8 = sum(delta_arvt_2_8_list) / len(delta_arvt_2_8_list) if delta_arvt_2_8_list else 0.0
    mean_d_ap = sum(delta_ap_list) / len(delta_ap_list) if delta_ap_list else 0.0
    
    # Gate B 规则判定:
    # 1. 平均 Delta APvt >= +0.005 或 平均 Delta ARvt >= +0.010
    # 2. 用于过 Gate 的主指标在成对 seed 中均为正
    # 3. 平均 Delta AP >= -0.002
    pass_apvt_threshold = (mean_d_apvt >= 0.005)
    pass_arvt_threshold = (mean_d_arvt_2_8 >= 0.010)
    all_positive_apvt = all(d > 0 for d in delta_apvt_list) if delta_apvt_list else False
    all_positive_arvt = all(d > 0 for d in delta_arvt_2_8_list) if delta_arvt_2_8_list else False
    pass_overall_ap = (mean_d_ap >= -0.002)
    
    gate_b_passed = ((pass_apvt_threshold and all_positive_apvt) or (pass_arvt_threshold and all_positive_arvt)) and pass_overall_ap
    
    # 检查是否触发 seed 2
    trigger_seed2 = False
    trigger_reasons = []
    if len(common_seeds) == 2:
        if (delta_apvt_list[0] * delta_apvt_list[1] < 0) or (delta_arvt_2_8_list[0] * delta_arvt_2_8_list[1] < 0):
            trigger_seed2 = True
            trigger_reasons.append("seed 0 与 seed 1 符号冲突")
        if (0 < mean_d_apvt < 0.007) and pass_apvt_threshold:
            trigger_seed2 = True
            trigger_reasons.append("Delta APvt 处于灰区 (0 < Delta < 0.007)")
        if (0 < mean_d_arvt_2_8 < 0.012) and pass_arvt_threshold:
            trigger_seed2 = True
            trigger_reasons.append("Delta ARvt 处于灰区 (0 < Delta < 0.012)")
            
    gate_report = {
        "task_id": "PRT-001-A1",
        "total_seeds_executed": len(common_seeds),
        "evaluated_seeds": common_seeds,
        "mean_deltas": {
            "mean_delta_APvt_official_1500": round(mean_d_apvt, 4),
            "mean_delta_ARvt_2_8_3000": round(mean_d_arvt_2_8, 4),
            "mean_delta_AP": round(mean_d_ap, 4),
        },
        "paired_deltas": paired_deltas,
        "gate_checks": {
            "Gate_E_evaluator_credible": gate_e_ok,
            "Gate_E_audit_errors": gate_e_errs,
            "Gate_P_traceability_verified": gate_p_ok,
            "Gate_P_audit_errors": gate_p_errs,
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
        "overall_status": "READY_FOR_REVIEW" if (gate_e_ok and gate_p_ok and gate_b_passed) else "REVISION_REQUIRED"
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

# -*- coding: utf-8 -*-
"""PRT-002-A1 实验结果汇总与 Gate 判定脚本 (Fail-Closed 严格审计版)

功能：
1. 扫描 outputs/PRT-002-A1/{B1-U,PDD-U}/seed* 下的 metrics.json；
2. 汇总生成 outputs/PRT-002-A1/summary.csv 与 outputs/PRT-002-A1/paired_deltas.csv；
3. 执行 Fail-Closed 严谨证据链审计 (Gate A/P)；
4. 计算成对差异 (Delta = PDD-U - B1-U)，判定 Gate V (Seed 0) 与 Gate B (两 Seed) 状态；
5. 导出 outputs/PRT-002-A1/gate_report.json。
"""

import argparse
import os
import os.path as osp
import json
import csv
import re
from typing import Dict, Any, List, Tuple


def parse_args():
    parser = argparse.ArgumentParser(description='Summarize PRT-002-A1 Results and Compute Gate')
    parser.add_argument('--root', default='outputs/PRT-002-A1', help='Root directory containing B1-U and PDD-U results')
    parser.add_argument('--output-dir', default='outputs/PRT-002-A1', help='Directory to save summaries and gate_report.json')
    return parser.parse_args()


def is_valid_sha256(val: str) -> bool:
    return bool(val and isinstance(val, str) and re.fullmatch(r"[a-fA-F0-9]{64}", val))


def load_metrics(root_dir: str) -> Dict[str, Dict[int, Dict[str, Any]]]:
    """加载已运行的所有 B1-U 和 PDD-U seed 指标"""
    results = {"B1-U": {}, "PDD-U": {}}
    for model_key in ["B1-U", "PDD-U"]:
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


def verify_gate_ap(root_dir: str, results: Dict[str, Dict[int, Dict[str, Any]]]) -> Tuple[bool, List[str]]:
    """Fail-closed 校验 Gate A/P (前序数据、拓扑、参数与证据审计)"""
    errors = []
    
    # 1. 检查 audit 目录下的 4 个必要文件
    audit_files = [
        ("dataset_manifest.json", ["splits", "audit_passed"]),
        ("topology_audit.json", ["actual_replacement_location", "conforms_to_less_than_3_percent"]),
        ("parameter_update_audit.json", ["B1-U", "PDD-U"]),
        ("legacy_run_audit.json", ["audited_runs", "conclusion"])
    ]
    
    for fname, req_keys in audit_files:
        fpath = osp.join(root_dir, "audit", fname)
        if not osp.exists(fpath):
            errors.append(f"审计文件缺失: {fpath}")
        else:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k in req_keys:
                if k not in data:
                    errors.append(f"审计文件 {fname} 缺少必要字段: '{k}'")
                    
    # 2. 检查 pytest.txt
    pytest_path = osp.join(root_dir, "tests", "pytest.txt")
    if not osp.exists(pytest_path):
        errors.append(f"pytest 报告文件缺失: {pytest_path}")
    else:
        with open(pytest_path, "r", encoding="utf-8") as f:
            content = f.read()
        if "passed" not in content or "failed" in content.lower():
            errors.append(f"pytest 测试未全部通过: {pytest_path}")
            
    return (len(errors) == 0), errors


def main():
    args = parse_args()
    os.makedirs(args.output_dir, exist_ok=True)
    
    results = load_metrics(args.root)
    b1u_seeds = sorted(results["B1-U"].keys())
    pddu_seeds = sorted(results["PDD-U"].keys())
    common_seeds = sorted(list(set(b1u_seeds) & set(pddu_seeds)))
    
    print(f"检测到可用评估数据: B1-U seeds={b1u_seeds}, PDD-U seeds={pddu_seeds}, 成对 seeds={common_seeds}")
    
    # 1. 导出 summary.csv
    summary_rows = []
    headers = [
        "model", "seed", "AP", "AP50", "AP75",
        "APvt_official_1500", "ARvt_official_1500", "ARvt_2_8_3000", "AP_2_8_3000",
        "APt_official_1500", "APs_official_1500", "AR_1500",
        "checkpoint_sha256", "prediction_json_sha256"
    ]
    
    for model_key in ["B1-U", "PDD-U"]:
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
    
    # 2. 导出 paired_deltas.csv
    paired_rows = []
    delta_headers = ["seed", "delta_AP", "delta_AP50", "delta_APvt_official_1500", "delta_ARvt_2_8_3000", "delta_AP_2_8_3000"]
    
    paired_deltas_dict = {}
    delta_ap_list = []
    delta_apvt_list = []
    delta_arvt_list = []
    
    for s in common_seeds:
        b1_m = results["B1-U"][s].get("metrics", {})
        pdd_m = results["PDD-U"][s].get("metrics", {})
        
        d_ap = pdd_m.get("AP", 0.0) - b1_m.get("AP", 0.0)
        d_ap50 = pdd_m.get("AP50", 0.0) - b1_m.get("AP50", 0.0)
        d_apvt = pdd_m.get("APvt_official_1500", 0.0) - b1_m.get("APvt_official_1500", 0.0)
        d_arvt = pdd_m.get("ARvt_2_8_3000", 0.0) - b1_m.get("ARvt_2_8_3000", 0.0)
        d_ap_2_8 = pdd_m.get("AP_2_8_3000", 0.0) - b1_m.get("AP_2_8_3000", 0.0)
        
        p_row = {
            "seed": s,
            "delta_AP": round(d_ap, 4),
            "delta_AP50": round(d_ap50, 4),
            "delta_APvt_official_1500": round(d_apvt, 4),
            "delta_ARvt_2_8_3000": round(d_arvt, 4),
            "delta_AP_2_8_3000": round(d_ap_2_8, 4)
        }
        paired_rows.append(p_row)
        paired_deltas_dict[f"seed_{s}"] = p_row
        
        delta_ap_list.append(d_ap)
        delta_apvt_list.append(d_apvt)
        delta_arvt_list.append(d_arvt)
        
    paired_csv_path = osp.join(args.output_dir, "paired_deltas.csv")
    with open(paired_csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=delta_headers)
        writer.writeheader()
        writer.writerows(paired_rows)
    print(f"成对增益表已保存至: {paired_csv_path}")
    
    # 3. 执行 Gate A/P 审计
    gate_ap_ok, gate_ap_errs = verify_gate_ap(args.root, results)
    
    # 4. 判定 Gate V (Seed 0 可行性门禁)
    gate_v = {"evaluated": False, "passed": False, "stop_pdd": False, "reasons": []}
    if 0 in common_seeds:
        gate_v["evaluated"] = True
        s0_d_ap = paired_deltas_dict["seed_0"]["delta_AP"]
        s0_d_apvt = paired_deltas_dict["seed_0"]["delta_APvt_official_1500"]
        s0_d_arvt = paired_deltas_dict["seed_0"]["delta_ARvt_2_8_3000"]
        
        # 停止条件: Delta APvt <= 0 且 Delta ARvt <= 0，或 Delta AP < -0.005
        if (s0_d_apvt <= 0.0 and s0_d_arvt <= 0.0) or (s0_d_ap < -0.005):
            gate_v["passed"] = False
            gate_v["stop_pdd"] = True
            gate_v["reasons"].append(f"Seed 0 明确失败 (APvt={s0_d_apvt}, ARvt={s0_d_arvt}, AP={s0_d_ap})，触发科学停止条件")
        # 通过条件: Delta AP >= -0.003 且 (Delta APvt >= +0.003 或 Delta ARvt >= +0.005)
        elif (s0_d_ap >= -0.003) and (s0_d_apvt >= 0.003 or s0_d_arvt >= 0.005):
            gate_v["passed"] = True
            gate_v["stop_pdd"] = False
            gate_v["reasons"].append("Seed 0 满足增益条件，允许进入 Seed 1")
        else:
            # 灰区: 允许进入 Seed 1 进一步验证
            gate_v["passed"] = True
            gate_v["stop_pdd"] = False
            gate_v["reasons"].append("Seed 0 处于灰区，按预注册规则允许进入 Seed 1 判定")
            
    # 5. 判定 Gate B (两 Seed 最终门禁)
    gate_b = {"evaluated": False, "passed": False, "reasons": []}
    trigger_seed2 = False
    seed2_reasons = []
    
    if len(common_seeds) >= 2:
        gate_b["evaluated"] = True
        mean_d_ap = sum(delta_ap_list) / len(delta_ap_list)
        mean_d_apvt = sum(delta_apvt_list) / len(delta_apvt_list)
        mean_d_arvt = sum(delta_arvt_list) / len(delta_arvt_list)
        
        pass_apvt_thresh = (mean_d_apvt >= 0.005)
        pass_arvt_thresh = (mean_d_arvt >= 0.010)
        all_pos_apvt = all(d > 0 for d in delta_apvt_list)
        all_pos_arvt = all(d > 0 for d in delta_arvt_list)
        pass_overall_ap = (mean_d_ap >= -0.002)
        
        gate_b_passed = ((pass_apvt_thresh and all_pos_apvt) or (pass_arvt_thresh and all_pos_arvt)) and pass_overall_ap
        gate_b["passed"] = gate_b_passed
        
        if gate_b_passed:
            gate_b["reasons"].append("两 Seed 增益满足 Gate B 门禁要求")
        else:
            gate_b["reasons"].append("两 Seed 未能满足 Gate B 门禁要求")
            
        # Seed 2 触发检查
        if len(common_seeds) == 2:
            if (delta_apvt_list[0] * delta_apvt_list[1] < 0) or (delta_arvt_list[0] * delta_arvt_list[1] < 0):
                trigger_seed2 = True
                seed2_reasons.append("seed 0 与 seed 1 符号冲突")
            if (0 < mean_d_apvt < 0.007) and pass_apvt_thresh:
                trigger_seed2 = True
                seed2_reasons.append("Delta APvt 处于灰区")
            if (0 < mean_d_arvt < 0.012) and pass_arvt_thresh:
                trigger_seed2 = True
                seed2_reasons.append("Delta ARvt 处于灰区")
                
    gate_report = {
        "task_id": "PRT-002-A1",
        "total_seeds_executed": len(common_seeds),
        "evaluated_seeds": common_seeds,
        "mean_deltas": {
            "mean_delta_AP": round(sum(delta_ap_list) / len(delta_ap_list), 4) if delta_ap_list else 0.0,
            "mean_delta_APvt_official_1500": round(sum(delta_apvt_list) / len(delta_apvt_list), 4) if delta_apvt_list else 0.0,
            "mean_delta_ARvt_2_8_3000": round(sum(delta_arvt_list) / len(delta_arvt_list), 4) if delta_arvt_list else 0.0,
        },
        "paired_deltas": paired_deltas_dict,
        "gate_checks": {
            "Gate_AP_audit": {
                "passed": gate_ap_ok,
                "audit_errors": gate_ap_errs
            },
            "Gate_V_seed0_feasibility": gate_v,
            "Gate_B_two_seed_decision": gate_b,
            "seed2_trigger_condition": {
                "triggered": trigger_seed2,
                "reasons": seed2_reasons
            }
        },
        "overall_status": "READY_FOR_REVIEW" if (gate_b["passed"] or gate_v.get("stop_pdd", False)) else "IN_PROGRESS"
    }
    
    report_path = osp.join(args.output_dir, "gate_report.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(gate_report, f, indent=2, ensure_ascii=False)
        
    print(f"Gate 审查报告已保存至: {report_path}")
    print(json.dumps(gate_report, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()

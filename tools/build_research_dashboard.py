#!/usr/bin/env python3
"""Build the repository-native research progress dashboard.

The dashboard deliberately derives claims from versioned authority files and
reviewed lightweight evidence. It never treats an experiment-agent summary as
research approval on its own.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
DASHBOARD_DIR = REPO_ROOT / "dashboard"
DEFAULT_OUTPUT = DASHBOARD_DIR / "data.js"
CURRENT_STATE_PATH = "docs/memory/CURRENT_STATE.md"
EVIDENCE_LEDGER_PATH = "docs/memory/EVIDENCE_LEDGER.md"
RESEARCH_BRIEF_PATH = "docs/research_brief_v0.1.md"
LATEST_REVIEW_PATH = "research/reviews/2026-08-26-PRT-001-A1-result-review-2.md"
EXPERIMENT_REPORT_PATH = "experiment_handoffs/results/PRT-001-A1-evidence-completion.md"
SUMMARY_PATH = "outputs/PRT-001-A1/summary.csv"
EXPERIMENT_REF = "origin/codex/exp-prt-001-a1"


def run_git(*args: str, check: bool = True) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=REPO_ROOT,
        text=True,
        encoding="utf-8",
        errors="replace",
        capture_output=True,
        check=False,
    )
    if check and result.returncode:
        raise RuntimeError(result.stderr.strip() or "git command failed")
    return result.stdout.strip()


def read_text(relative_path: str) -> str:
    return (REPO_ROOT / relative_path).read_text(encoding="utf-8")


def read_worktree_or_ref(relative_path: str, ref: str) -> tuple[str, str]:
    path = REPO_ROOT / relative_path
    if path.exists():
        return path.read_text(encoding="utf-8"), "working-tree"
    text = run_git("show", f"{ref}:{relative_path}", check=False)
    if not text:
        raise FileNotFoundError(f"Cannot find {relative_path} in worktree or {ref}")
    return text, ref


def match_value(text: str, label: str, default: str = "UNKNOWN") -> str:
    pattern = rf"^-\s*{re.escape(label)}:\s*`?([^`\r\n]+?)`?\s*$"
    match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else default


def parse_date(text: str, label: str) -> str | None:
    value = match_value(text, label, "")
    match = re.search(r"\d{4}-\d{2}-\d{2}", value)
    return match.group(0) if match else None


def parse_summary(csv_text: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    numeric_fields = {
        "seed",
        "AP",
        "AP50",
        "AP75",
        "APvt_official_1500",
        "ARvt_official_1500",
        "ARvt_2_8_3000",
        "AP_2_8_3000",
    }
    runs: list[dict[str, Any]] = []
    for raw in csv.DictReader(io.StringIO(csv_text)):
        row: dict[str, Any] = dict(raw)
        for key in numeric_fields:
            if key in row and row[key] != "":
                row[key] = int(row[key]) if key == "seed" else float(row[key])
        runs.append(row)

    by_key = {(row["model"], row["seed"]): row for row in runs}
    metric_specs = [
        ("APvt_official_1500", "官方 APvt", 0.005),
        ("ARvt_2_8_3000", "项目 ARvt [2,8)", 0.010),
        ("AP", "总体 AP", -0.002),
    ]
    deltas: list[dict[str, Any]] = []
    for field, label, threshold in metric_specs:
        paired = []
        for seed in (0, 1):
            paired.append(by_key[("B1", seed)][field] - by_key[("B0", seed)][field])
        mean = sum(paired) / len(paired)
        deltas.append(
            {
                "field": field,
                "label": label,
                "seed0": paired[0],
                "seed1": paired[1],
                "mean": mean,
                "threshold": threshold,
                "pass": mean >= threshold and all(value > 0 for value in paired),
            }
        )
    return runs, deltas


def file_status(path: str, current_date: str) -> dict[str, Any]:
    text = read_text(path)
    dates = re.findall(r"20\d{2}-\d{2}-\d{2}", text)
    latest = max(dates) if dates else None
    return {
        "path": path,
        "latestDate": latest,
        "current": latest == current_date,
    }


def collect_records(folder: str) -> list[dict[str, str]]:
    records = []
    for path in sorted((REPO_ROOT / folder).glob("*.md"), reverse=True):
        if path.name in {"README.md", "AGENTS.md", "DESIGN_REVIEW_TEMPLATE.md", "RESULT_REVIEW_TEMPLATE.md"}:
            continue
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip() if text else path.stem
        status_match = re.search(r"(?:审查状态|状态|Review status)：?\s*`([^`]+)`", text)
        records.append(
            {
                "path": path.relative_to(REPO_ROOT).as_posix(),
                "title": title,
                "status": status_match.group(1) if status_match else "RECORDED",
            }
        )
    return records


def git_state() -> dict[str, Any]:
    branch = run_git("branch", "--show-current")
    head = run_git("rev-parse", "HEAD")
    status_lines = [line for line in run_git("status", "--short").splitlines() if line]
    remote_experiment = run_git("rev-parse", EXPERIMENT_REF, check=False)
    remote_main = run_git("rev-parse", "origin/main", check=False)
    integrated = False
    if remote_main:
        integrated = subprocess.run(
            ["git", "merge-base", "--is-ancestor", head, remote_main],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        ).returncode == 0
    return {
        "branch": branch,
        "head": head,
        "dirty": bool(status_lines),
        "dirtyEntries": status_lines,
        "remoteExperiment": remote_experiment or None,
        "remoteMain": remote_main or None,
        "integratedIntoMain": integrated,
    }


def build_payload() -> dict[str, Any]:
    current = read_text(CURRENT_STATE_PATH)
    latest_review = read_text(LATEST_REVIEW_PATH)
    snapshot_date = parse_date(current, "Snapshot date") or "UNKNOWN"
    reviewed_commit = match_value(current, "Reviewed experiment commit")
    summary_text, summary_source = read_worktree_or_ref(SUMMARY_PATH, EXPERIMENT_REF)
    report_text, report_source = read_worktree_or_ref(EXPERIMENT_REPORT_PATH, EXPERIMENT_REF)
    runs, deltas = parse_summary(summary_text)
    git = git_state()

    report_corrected = (
        "+0.0131" in report_text
        and "+0.0128" not in report_text
        and "逆映射算术 fixture" in report_text
    )
    docs = [
        file_status(EVIDENCE_LEDGER_PATH, snapshot_date),
        file_status(RESEARCH_BRIEF_PATH, snapshot_date),
    ]
    blockers = []
    if not report_corrected:
        blockers.append(
            {
                "severity": "CONDITION",
                "title": "A1 实验报告尚待机械修正",
                "detail": "同步 ARvt=+0.0131、完整 hash 与坐标测试边界；无需重训、复评或 seed 2。",
                "owner": "实验执行 agent",
            }
        )
    if not git["integratedIntoMain"]:
        blockers.append(
            {
                "severity": "GOVERNANCE",
                "title": "研究治理状态尚未进入 main",
                "detail": "当前研究 HEAD 不是 origin/main 的祖先；后续阶段启动前需完成审阅集成。",
                "owner": "用户 / 研究设计 agent",
            }
        )
    for doc in docs:
        if not doc["current"]:
            blockers.append(
                {
                    "severity": "DRIFT",
                    "title": f"{Path(doc['path']).name} 尚未同步当前审查",
                    "detail": f"文件最新日期 {doc['latestDate'] or 'UNKNOWN'}，当前状态快照为 {snapshot_date}。",
                    "owner": "研究设计 agent",
                }
            )

    phases = [
        {
            "id": "P0",
            "name": "问题与评测协议冻结",
            "status": "DONE",
            "evidence": "2–8 px 问题、AI-TOD-v2、双口径 evaluator 与 CCF-C 节奏已版本化。",
        },
        {
            "id": "P1",
            "name": "P2 基线证据补全",
            "status": "CONDITIONAL",
            "evidence": "两 seed 核心 Gate 通过；仅剩报告一致性条件。",
        },
        {
            "id": "P2",
            "name": "PDD 受控诊断与改版",
            "status": "LOCKED",
            "evidence": "PDD v1 零 AP 为负测量，因果归因未验证；PRT-002-A1 任务卡尚未建立。",
        },
        {
            "id": "P3",
            "name": "SSR 条件增益验证",
            "status": "LOCKED",
            "evidence": "必须等待 PDD 阶段决策，不允许提前堆叠模块。",
        },
        {
            "id": "P4",
            "name": "泛化、效率与论文证据",
            "status": "LOCKED",
            "evidence": "跨检测器/数据集、尺寸分桶和真实延迟均未测试。",
        },
    ]
    evidence = [
        {"claim": "P2–P6 改善极小目标基线", "status": "CONDITIONALLY_ACCEPTED", "basis": "AI-TOD-v2，FCOS-R50，12 epochs，seeds 0/1"},
        {"claim": "P2 收益在两个 seed 方向一致", "status": "MEASURED", "basis": "APvt、精确 ARvt、总体 AP 均为正"},
        {"claim": "PDD 有效", "status": "NOT_ESTABLISHED", "basis": "PDD v1 零 AP；根因解释未验证"},
        {"claim": "SSR / PRTiny 有效", "status": "NOT_TESTED", "basis": "正式任务仍锁定"},
        {"claim": "跨数据集 / 检测器泛化", "status": "NOT_TESTED", "basis": "尚无受审原始证据"},
        {"claim": "真实加速或效率收益", "status": "NOT_TESTED", "basis": "无同 GPU latency/FPS 协议测量"},
    ]
    payload: dict[str, Any] = {
        "schemaVersion": 1,
        "generatedAt": datetime.now().astimezone().isoformat(timespec="seconds"),
        "snapshot": {
            "date": snapshot_date,
            "status": match_value(current, "Snapshot status"),
            "task": "PRT-001-A1",
            "taskStatus": "REVIEW_PASSED_WITH_CONDITIONS / REPORT_CORRECTION_ONLY",
            "reviewedCommit": reviewed_commit,
            "role": "研究设计 agent",
            "scope": "独立 2–8 px 极小目标检测副线",
            "permission": "仅允许 A1 report-only 修正；PDD/SSR/NWD/泛化正式运行锁定。",
        },
        "git": git,
        "phases": phases,
        "metrics": deltas,
        "runs": runs,
        "evidence": evidence,
        "blockers": blockers,
        "nextActions": [
            {"order": 1, "owner": "实验执行 agent", "action": "在实验分支完成 A1 report-only 修正并 push 完整 SHA。"},
            {"order": 2, "owner": "研究设计 agent", "action": "fetch 并核验修正 commit，关闭 A1 附加条件。"},
            {"order": 3, "owner": "研究设计 agent", "action": "同步 EVIDENCE_LEDGER 与 research brief，消除状态漂移。"},
            {"order": 4, "owner": "用户 / 研究设计 agent", "action": "审阅并将治理状态集成到 main。"},
            {"order": 5, "owner": "研究设计 agent", "action": "建立 PRT-002-A1 受控诊断任务卡与设计审查。"},
        ],
        "records": {
            "reviews": collect_records("research/reviews")[:8],
            "tasks": collect_records("experiment_handoffs/tasks")[:8],
        },
        "sources": [
            {"path": "AGENTS.md", "role": "项目总约束"},
            {"path": CURRENT_STATE_PATH, "role": "当前状态快照"},
            {"path": LATEST_REVIEW_PATH, "role": "当前正式结果审查"},
            {"path": "experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md", "role": "当前任务卡 v1.1"},
            {"path": SUMMARY_PATH, "role": f"四组受审轻量指标（读取自 {summary_source}）"},
            {"path": EXPERIMENT_REPORT_PATH, "role": f"实验自查报告（读取自 {report_source}）"},
        ],
        "reviewExcerpt": re.search(r"\[REVIEW_PASSED_WITH_CONDITIONS\].+", latest_review).group(0),
        "updateCommand": "python tools/build_research_dashboard.py --fetch",
    }
    stable = {
        "snapshot": payload["snapshot"],
        "phases": payload["phases"],
        "metrics": payload["metrics"],
        "runs": payload["runs"],
        "evidence": payload["evidence"],
        "blockers": payload["blockers"],
        "records": payload["records"],
        "sources": payload["sources"],
        "reviewExcerpt": payload["reviewExcerpt"],
    }
    payload["sourceFingerprint"] = hashlib.sha256(
        json.dumps(stable, ensure_ascii=False, sort_keys=True).encode("utf-8")
    ).hexdigest()
    return payload


def render_js(payload: dict[str, Any]) -> str:
    encoded = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"// Generated by tools/build_research_dashboard.py; do not edit by hand.\nwindow.RESEARCH_DASHBOARD_DATA = {encoded};\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fetch", action="store_true", help="fetch origin before reading remote evidence")
    parser.add_argument("--check", action="store_true", help="fail if dashboard/data.js is stale")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    if args.fetch:
        run_git("fetch", "origin", "--prune")
    payload = build_payload()
    rendered = render_js(payload)
    output = args.output if args.output.is_absolute() else REPO_ROOT / args.output
    if args.check:
        existing = output.read_text(encoding="utf-8") if output.exists() else ""
        fingerprint = re.search(r'"sourceFingerprint":\s*"([0-9a-f]{64})"', existing)
        if not fingerprint or fingerprint.group(1) != payload["sourceFingerprint"]:
            print(f"STALE: {output.relative_to(REPO_ROOT)}")
            return 1
        print(f"CURRENT: {output.relative_to(REPO_ROOT)}")
        return 0
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(rendered, encoding="utf-8")
    print(f"WROTE: {output.relative_to(REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

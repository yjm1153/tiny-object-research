# 已审查证据台账

本文件只登记经过研究设计 agent 正式结果审查的实验事实。任务完成信号、smoke、未审查日志或其他仓库结果不得登记为已接受证据。

## 当前状态

截至2026-08-26，PRT-001-A1 已通过最终研究结果审查；方法模块仍未获得正向证据。

| Task ID | Claim | Status | Result report | Review record | Raw evidence | Accepted scope |
|---|---|---|---|---|---|---|
| PRT-001-A1 | P2–P6 相对 P3–P7 在当前协议下稳定改善极小目标基线 | `MEASURED / REVIEW_PASSED` | `experiment_handoffs/results/PRT-001-A1-evidence-completion.md` | `research/reviews/2026-08-26-PRT-001-A1-result-review-3.md` | `outputs/PRT-001-A1/summary.csv`、`gate_report.json`、四组 `metrics.json`；最终交接 `01ec41b0f052a170116185b2cd481c36ae3d725a` | 仅 AI-TOD-v2、FCOS-R50、12 epochs、seeds 0/1；平均 ΔAPvt `+0.0103`、ΔARvt[2,8) `+0.0131`、ΔAP `+0.0297` |
| PRT-002 / PDD v1 | PDD单模块 | `NOT_ESTABLISHED / REVISION_REQUIRED` | `experiment_handoffs/results/PRT-002-pdd-module.md` | `research/reviews/2026-08-23-PRT-002-result-review-2.md` | 零 AP 负测量可定位，但根因解释未验证 | 不接受 PDD 有效或失败归因结论；等待 PRT-002-A1 受控诊断 |
| SSR tasks | SSR及机制控制 | `LOCKED` | 无 | 无 | 无 | 无 |

## 登记条件

新增条目必须同时具备：

1. 已批准任务卡；
2. 实验结果报告；
3. 可定位原始日志、配置、指标和必要checkpoint/hash；
4. 研究结果审查记录；
5. 合法的 `REVIEW_PASSED` 或附条件通过信号；
6. 仅限证据支持范围的claim。

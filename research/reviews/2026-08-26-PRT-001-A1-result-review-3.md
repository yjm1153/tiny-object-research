# 实验结果审查：PRT-001-A1（Result Review 3 / Final）

## 1. 审查结论与放行信号

- 审查状态：`REVIEW_PASSED`
- 审查人：研究设计 agent
- 审查日期：2026-08-26
- 当前任务：`PRT-001-A1`
- 审查实验分支：`origin/codex/exp-prt-001-a1`
- 最终实验交接 commit：`01ec41b0f052a170116185b2cd481c36ae3d725a`
- 核心测量 commit：`95dbcd6176b173183aa38fd0972e5d1075b9434e`
- 前序附条件审查：`research/reviews/2026-08-26-PRT-001-A1-result-review-2.md`
- 下一候选任务：`PRT-002-A1`（仅解锁任务设计；正式运行仍需独立任务卡和设计审查）

```text
[REVIEW_PASSED][PRT-001-A1] 里程碑审查通过，可以进入 PRT-002-A1 设计阶段；正式实验须等待新任务卡和设计审查批准。
```

## 2. 附加条件关闭核验

实验 agent 通过两个 report-only commit 完成 Result Review 2 的全部机械条件：

- `a6afd490604b10b33b240dca896bf23ea9733685`：同步精确 2–8 px 数值、七组 checkpoint/prediction hash 与测试表述；
- `01ec41b0f052a170116185b2cd481c36ae3d725a`：将 B1 seed 1 checkpoint SHA 修正为 `2721e64a371d80eb52ba7406e8b320e7c1498cdddad0ee893ba2b762c3d2463b`。

最终复核结果：

| 核验项 | 结果 |
|---|---|
| 从核心测量 commit 到最终交接 commit 的改动范围 | 仅 `experiment_handoffs/results/PRT-001-A1-evidence-completion.md` |
| 四组 checkpoint SHA 与 `summary.csv` | 4/4 一致 |
| 四组 prediction SHA 与 `summary.csv` | 4/4 一致 |
| 平均 `Delta APvt_official_1500` | `+0.0103`，一致 |
| 平均 `Delta ARvt_2_8_3000` | `+0.0131`，一致 |
| 平均总体 `Delta AP` | `+0.0297`，一致 |
| `summary.csv` Git blob | 与核心测量 commit 相同：`eccd63a8808bbf862137dbf6c33c7f782416b892` |
| `gate_report.json` Git blob | 与核心测量 commit 相同：`04edd13d616f9f1181387cd6eb889e92c38fd615` |
| 坐标测试表述 | 已收缩为“逆映射算术 fixture” |

附加条件全部满足，不需要重训、复评或补 seed 2。

## 3. 最终接受的有限结论

在 AI-TOD-v2、FCOS-R50、12-epoch 统一协议和 seeds 0/1 下，P2–P6 相对 P3–P7：

- 平均 `APvt_official_1500` 提高 `+0.0103`；
- 平均 `ARvt_2_8_3000` 提高 `+0.0131`；
- 平均总体 AP 提高 `+0.0297`；
- 三项指标在两个 seed 上方向一致，Gate E、P、B、C 通过。

因此，P2 可以作为后续极小目标方法诊断的基础载体。

## 4. 仍不成立的结论

本审查不证明：

- P2 本身构成论文创新；
- 早期空间细节损失是唯一因果瓶颈；
- PDD、SSR 或完整 PRTiny 有效；
- 2–4、4–6、6–8 px 各子区间均改善；
- 跨数据集、跨检测器泛化或真实效率收益成立。

这些结论必须由后续独立任务卡验证。

## 5. 下一阶段权限边界

- `PRT-001-A1` 正式关闭；
- 解锁 `PRT-002-A1` 的研究设计工作；
- 在新任务卡与设计审查进入 `APPROVED` 或满足条件的 `APPROVED_WITH_CONDITIONS` 前，实验 agent 不得运行 PDD v2、SSR、NWD 或泛化实验；
- 进入新实验前仍需完成必要的 `main` 治理集成，并从最新 `main` 创建独立实验分支。

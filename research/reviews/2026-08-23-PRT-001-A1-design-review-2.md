# 实验设计审查：PRT-001-A1（Review 2）

## 1. 审查结论

- 设计状态：`APPROVED_WITH_CONDITIONS`
- 审查人：研究设计 agent
- 审查日期：2026-08-23
- 任务卡：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`（v1.1）
- 决策记录：`docs/decisions/DR-004-ccf-c-paced-evidence-standard.md`
- 本审查取代：`2026-08-23-PRT-001-A1-design-review-1.md` 的执行口径；旧审查保留供审计
- 当前允许：评估器接通、最小正确性测试、seed-0 恢复；Gate E/P 后运行 seed 1；仅在任务卡条件触发时运行 seed 2
- 下一任务：`PRT-002-A1`、`PRT-003`、SSR 均 `LOCKED`

## 2. CCF-C 目标下的充分性判断

两组配对 seeds 不是统计显著性证明，但若 evaluator 可信、对照协议一致、两个 seed 的主指标方向一致并达到有实际意义的阈值，已足以在当前基线载体判断阶段支持“继续/停止”决策。第三 seed 对明确一致的结果信息增益有限，因此改为条件触发。

本阶段不要求完整论文级效率表、跨数据集泛化或每个诊断项齐备。这些应在方法确认后进入后续阶段，避免在尚未证明 P2 载体可用前过度投入。

## 3. 研究识别性检查

| 审查项 | 结论 | 依据 |
|---|---|---|
| 唯一研究问题 | 通过 | 只判断 P2 相对 P3 是否改善极小尺度指标 |
| 可证伪性 | 通过 | 两 seed 阈值、符号一致性、总体 AP 约束已冻结 |
| 对照公平 | 通过 | B0/B1 只改变 FPN 起始层及配套 stride/range |
| 指标对应主张 | 通过（附条件） | 官方 APvt 与项目精确 2–8 px AR 分字段实现 |
| 数据泄漏控制 | 通过（附条件） | 仅 train/val，结果报告须证明无 test 调用 |
| 资源与信息价值 | 通过 | 复用 seed 0 + seed 1，歧义才补 seed 2 |
| 失败可指导后续 | 通过 | 明确失败则停止，不为碰运气追加 seed |

## 4. 批准条件

1. Gate E：evaluator 消费 predictions；官方 commit 固定；核心边界/坐标/空与完美预测测试通过；代表性结果可重复；
2. Gate P：seed-0 的 checkpoint/config/log 对应关系可证明，关键对象有版本/hash，且不存在 test 调用；
3. Gate E/P 后先补 B0/B1 seed 1；只有任务卡定义的歧义或异常才补 seed 2；
4. 两 seed 通过要求：用于过 Gate 的主指标两组均为正，均值达到 `APvt +0.005` 或 `ARvt +0.010`，平均总体 AP 不低于 `-0.002`；
5. 全部已执行 seed、失败与协议偏差必须报告；实验侧子研究 agent 不能替代正式里程碑审查。

## 5. 交付充分性

任务卡 D0–D4 是本阶段必要且充分的交付。以下不再作为阻塞项：固定三种子、所有文件 hash、每 run 重复评估、独立 agent 台账、FLOPs、latency/FPS 和完整 AP 诊断分箱。

这项放宽不允许降低三条硬底线：

- 指标真实且 evaluator 可被最小测试证实；
- B0/B1 同数据、同训练、同 seed 配对；
- 无 test 泄漏、无选择性报告、无覆盖负结果。

## 6. 后续放行边界

PRT-001-A1 完成后只能发送 `READY_FOR_REVIEW`。研究设计 agent 核验 D0–D4 和 Gate 后，若通过，可新建小预算 PRT-002-A1 诊断任务；不得把 P2 结果直接写成 PRTiny、PDD 或 SSR 已有效，也不得自动进入完整方法矩阵。

设计放行信号：

```text
[DESIGN_APPROVED_WITH_CONDITIONS][PRT-001-A1] 按 CCF-C 分层证据标准执行：先完成 evaluator、seed-0 恢复和 seed-1 配对；仅在预注册歧义条件触发时补 seed 2；完成后等待独立里程碑审查。
```

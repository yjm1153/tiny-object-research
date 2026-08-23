# 实验设计审查：PRT-001-A1

## 1. 审查结论

- 设计状态：`APPROVED_WITH_CONDITIONS`
- 审查人：研究设计 agent
- 审查日期：2026-08-23
- 任务卡及版本：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`（v1.0）
- 当前允许阶段：`IMPLEMENTATION / EVALUATOR_VALIDATION / LEGACY_EVIDENCE_RECOVERY`
- 下一任务：`PRT-002-A1`、`PRT-003`、SSR 均 `LOCKED`

## 2. 研究识别性检查

| 审查项 | 结论 | 依据/修改要求 |
|---|---|---|
| 唯一研究问题清晰 | 通过 | 只判断 P2 相对 P3 是否稳定改善 2–8 px 漏检，不测试 PDD/SSR |
| 假设可被否证 | 通过 | APvt/ARvt/总体 AP、配对 seed 与明确阈值均已冻结 |
| 单次核心变量受控 | 通过 | B0/B1 只改变金字塔层级、stride 与 regress range |
| 对照容量/训练公平 | 通过 | 相同 backbone/head/初始化/训练预算/seed，成对运行 |
| 指标与主张对应 | 通过 | APvt/ARvt 与 2–4/4–6/6–8 px 诊断直接对应漏检问题 |
| 无数据/标签/test 泄漏 | 通过（附条件） | 仅 train/val；必须以 run manifest 证明 test 未调用 |
| 结果非定义机械保证 | 通过 | P2 可能增加背景噪声和计算，提升不是结构上必然 |
| 失败条件可指导下一步 | 通过 | Gate B0/B1 失败则停止 PDD/SSR 并复核载体 |
| 资源成本与信息价值匹配 | 通过 | 优先复用已有 seed-0 checkpoint，只补缺失证据和 seeds 1/2 |

## 3. 固定项与允许范围

- 固定数据/split：AI-TOD-v2 official train/val；test 禁止参与开发。
- 固定模型/初始化：FCOS-R50 B0 P3–P7 与 B1 P2–P6；同一 ImageNet 权重及 SHA-256。
- 固定训练与 seed：12 epochs；有效 batch 4；lr 0.005；seeds 0/1/2；其余见任务卡。
- 允许修改：评估器实现、测试、证据脚本、监控、非科学性 Bug/OOM/环境适配；允许使用子研究/子实验 agent。
- 禁止修改：主指标、尺度定义、数据 split、模型核心拓扑、训练预算、有效 batch/lr、seed 集合，以及引入 PDD/SSR/NWD/额外增强。

## 4. 核心质疑与竞争解释

- 普通 COCO AP 提升是否真正来自 2–8 px，而非 8–32 px；
- seed-0 高相对增幅是否受低基数与随机波动放大；
- evaluator 是否真实消费 predictions 并与 AI-TOD 官方实现一致；
- P2 的提升是否以显著额外计算为代价；
- 原 checkpoint、配置和日志是否能形成可复算证据链。

## 5. 批准条件

1. 先通过 Gate E：固定官方 `cocoapi-aitod` commit，对齐其 `maxDets=1500` 指标，并将项目 `ARvt@3000` 作为不同字段保存；同时通过边界、坐标、ignore/crowd 和 prediction-sensitive 测试；
2. 再通过 Gate P：既有 seed-0 checkpoint/config/log/prediction/metrics hash 闭环；
3. Gate E/P 通过并写入 `gate_report.json` 后，实验 agent 可自主进入 seed 1、2 正式矩阵；
4. 子 agent 的研究意见只作为实验侧 Self-Review，不得发出正式 `REVIEW_*`；
5. 所有失败、重试和协议偏差永久保留。

## 6. 剩余风险

- 三种子只能提供工程稳定性证据，不等同统计显著性；
- AI-TOD 官方 evaluator 的 `(0,8]`/`maxDets=1500` 与项目 `2–8 px`/`maxDets=3000` 必须分别保存，不能共用含糊的无后缀字段；
- 旧 seed-0 checkpoint 可能只存在远端算力节点，若已丢失需要合法重跑；
- GitHub 中已提交的大日志不应在后续任务继续扩张；只提交轻量索引和 hash。

## 7. 执行授权

- 是否允许实验 agent 启动：`CONDITIONAL`
- 允许阶段：WP0/WP1/WP2；Gate E/P 通过后自动允许 WP3/WP4。
- 必须先满足的条件：实验分支包含本任务卡和设计审查固定 commit；现有证据只读保留；建立子 agent 协作台账。
- 未经新审查仍然禁止：PDD v2、SSR、NWD、额外增强、test 调参、跨阶段放行。

设计放行信号：

```text
[DESIGN_APPROVED_WITH_CONDITIONS][PRT-001-A1] 授权实验执行 agent 在冻结科学变量下自主调用子研究/子实验 agent，完成评估器、证据恢复、必要补种子与自我审查；Gate E/P 通过后可在本任务内进入正式矩阵，但不得进入任何后续方法任务。
```

# DR-004：面向 CCF-C 的分层证据与推进节奏

- 日期：2026-08-23
- 状态：`ACCEPTED`
- 决策角色：研究设计 agent
- 用户目标：以 CCF-C 投稿为目标，避免因顶会级证据审计造成推进过慢

## 背景

PRT-001-A1 v1.0 使用固定三种子、全量文件 hash、逐 run 重复评估和强制子 agent 台账。该方案可最大化审计性，但在当前阶段会把较多时间花在基线证据工程，而不是快速判断 P2 是否值得作为后续方法载体。

本项目仍需保证实验结果真实、对照公平、结论可复核，但证据强度应与 CCF-C 投稿目标和当前科学风险匹配。

## 决策

采用三层证据标准：

1. **不可降低的真实性底线**：评估器必须消费 predictions；官方和项目指标不得混写；B0/B1 必须同协议配对；train/val/test 边界清楚；负结果和失败不得隐藏。
2. **阶段核心证据**：复用 seed 0，并补一个独立 seed 1。两组结论方向一致且达到预注册阈值即可提交里程碑审查。
3. **按歧义追加证据**：仅在 seed 结论冲突、均值接近阈值、运行存在可能影响结论的异常，或研究审查发现明确歧义时补 seed 2。

同时简化证据工程：

- 优先直接调用固定 commit 的官方 evaluator；自定义 wrapper 只覆盖项目精确 2–8 px 指标和必要诊断；
- 仅对 config、best checkpoint、prediction、metrics、数据 annotation 等关键对象做 hash；
- 代表性 prediction JSON 重复评估一次，不要求每个 run 重复；
- 子 agent 独立台账改为结果报告中的简明分工与遗留问题；
- FLOPs、latency/FPS 和完整诊断分箱不是 PRT-001-A1 完成条件。

## 通过后的推进方式

PRT-001-A1 通过只证明 P2 是可用载体，不构成 PRTiny 方法贡献。里程碑通过后，下一步优先建立一个小预算 PRT-002-A1 诊断任务，先判断 PDD 的失败来源和最小可行性，再决定是否投入完整矩阵。SSR、NWD 和泛化实验不自动解锁。

## 不受本决策影响的红线

- 不得用 smoke、FLOPs 或单 seed 普通 AP 代替正式研究结论；
- 不得改变 2–8 px 问题、AI-TOD-v2 主数据集、主指标定义或冻结模型变量；
- 不得利用 test split 调参；
- 不得由实验执行 agent 自行批准里程碑或静默跨阶段；
- 若证据互相矛盾，必须保留歧义并按任务卡补证据，而不是选择性报告。

## 影响文件

- `experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md` v1.1
- `research/reviews/2026-08-23-PRT-001-A1-design-review-2.md`
- `docs/memory/CURRENT_STATE.md`

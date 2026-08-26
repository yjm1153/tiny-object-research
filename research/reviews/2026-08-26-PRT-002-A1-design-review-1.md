# 实验设计审查：PRT-002-A1（PDD 因果诊断与最小可行性复核）

## 1. 审查结论

- 设计状态：`APPROVED_WITH_CONDITIONS`
- 审查人：研究设计 agent
- 审查日期：2026-08-26
- 任务卡：`experiment_handoffs/tasks/PRT-002-A1-pdd-causal-diagnostic.md` v1.0
- 基准 `main`：`28ed6d07aeef368a5abfe82e45df1c4d8eb99663`
- 当前允许阶段：`WP0–WP2 / AUDIT_IMPLEMENTATION_SMOKE`
- 条件允许阶段：`WP3 seed 0`，仅在 Gate A/P 证据 commit + push 后
- 下一任务：`LOCKED`（PRT-003/SSR 不解锁）

```text
[DESIGN_APPROVED_WITH_CONDITIONS][PRT-002-A1] 允许从最新 main 建立 codex/exp-prt-002-a1，先完成旧证据、数据、真实拓扑和参数更新审计；Gate A/P 远端可见后运行匹配 B1-U/PDD-U seed 0，并仅按 Gate V/B 条件补 seed 1/2。SSR 继续锁定。
```

## 2. 研究识别性检查

| 审查项 | 结论 | 依据 |
|---|---|---|
| 唯一研究问题清晰 | 通过 | 只回答 PDD 失败来源与匹配对照下的最小可行性 |
| 假设可证伪 | 通过 | Seed 0 继续/停止阈值与两 seed 去留 Gate 已冻结 |
| 核心变量受控 | 通过 | `B1-U/PDD-U` 只差单位置 PDD；冻结、训练和 evaluator 匹配 |
| 冻结归因可识别 | 通过 | 四配置实际 optimizer step 审计，不再依据配置文本猜测 |
| 数据与评估一致 | 附条件通过 | 旧报告实例数与 A1 不一致，必须先 hash/count 审计；旧 run 可被判为 `LEGACY_ONLY` |
| 拓扑命名准确 | 附条件通过 | 当前代码只实现一个替换位置，禁止继续声称 `(0,1)` 是双位置 PDD |
| 指标对应主张 | 通过 | 固定官方 APvt、项目 `[2,8)` ARvt 与总体 AP；普通 `AP_s` 不能替代 |
| 资源与信息价值 | 通过 | 先复用/复评，seed 0 明确失败即停；不预跑完整消融 |
| 负结果可指导路线 | 通过 | 明确失败则删除 PDD，不通过叠 SSR 救场 |

## 3. 核心质疑与处理

### 3.1 旧 PDD v2 不能直接视为公平结果

- 报告记录 train/val instances 为 700,621/175,234，与 A1 的 650,471/70,424 不一致；
- PDD v2 使用 `frozen_stages=-1`，A1 B1 使用 `frozen_stages=1`，普通 AP 不能直接相减；
- 报告只给普通 COCO AP/APs，没有当前受审 APvt 与精确 `[2,8)` ARvt；
- 报告将 PDD 下降解释为高频噪声并进一步证明 SSR 必要，当前证据不支持该因果链。

处理：旧 checkpoint/prediction 仅在 WP0 全部追溯条件通过后复用；否则只保留历史线索，并在本任务补一个合法 PDD-U seed 0。

### 3.2 双位置主张与实现不一致

当前 `ResNetWithPDD` 仅替换 `maxpool`；`pdd_stages=(0,1)` 中的 `1` 没有对应实现。本任务把模型冻结为单位置 PDD，不允许实验 agent 在诊断过程中自行补做第二位置，因为那会改变核心架构。

### 3.3 为什么不先跑全部消融

PDD 尚未在匹配 B1 上表现出最小正增益。此时运行 S2D-only、DW-only、matched-param 和三 seed 会把算力花在可能应删除的模块上。先执行最小匹配去留测试更符合 DR-004 与 CCF-C 推进节奏。

## 4. 固定项与允许范围

- 固定：AI-TOD-v2 A1 同一 train/val、FCOS-R50-P2–P6、12 epochs、lr/effective batch、seeds、官方 evaluator 与项目 `[2,8)` wrapper；
- 正式比较：`B1-U` 对 `PDD-U`，两者均 `frozen_stages=-1`；
- 允许：审计脚本、独立配置、测试、输出编码和显存适配；
- 禁止：修改 PDD 分支结构/位置数、引入 SSR/NWD、换数据、换主指标、选择性重跑或自行放宽 Gate；
- 允许实验 agent 调用子研究/子实验 agent，但正式结果由主实验 agent 合并、自查和 Git 交接。

## 5. 批准条件

WP3 前必须远端提交并报告：

1. `legacy_run_audit.json`：旧 v1/v2 复用判定；
2. `dataset_manifest.json`：train/val hash、images、instances、文件名列表 hash；
3. `topology_audit.json`：实际替换位置和 shape；
4. `parameter_update_audit.json`：四配置 actual-step 参数更新；
5. `B1-U/PDD-U` 机器可读配置 diff、测试和 smoke；
6. evaluator 正确性与 prediction-sensitive 证据；
7. 完整 pre-run commit SHA、push 状态和 dirty 状态。

若数据或旧 run 无法追溯，不阻塞整个任务：将旧 run 标为 `LEGACY_ONLY`，按任务卡补跑合法 PDD-U seed 0。若无法获得与 A1 一致的数据或 evaluator，才发送 `[EXPERIMENT_BLOCKED]`。

## 6. 剩余风险

- 单位置 PDD 可能直接失败；这是有价值的快速停止结论；
- 解冻可能共同改善或损害 B1/PDD，故必须保留匹配 B1-U；
- 两 seed 不能证明统计显著性，但足够支持当前模块去留；仅歧义才补 seed 2；
- 即使 PDD 通过，本任务也不证明 SSR、泛化或效率。

## 7. 执行授权

- 是否允许实验 agent 启动：`CONDITIONAL`
- 立即允许：WP0–WP2 审计、配置、测试和 smoke；
- Gate A/P 后允许：WP3 成对 seed 0；
- Gate V 后允许：WP4 成对 seed 1；仅预注册歧义允许 seed 2；
- 未经新审查仍禁止：完整 PDD 消融、双位置 PDD、SSR、NWD、泛化和论文结论升级。

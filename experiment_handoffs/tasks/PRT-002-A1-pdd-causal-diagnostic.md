# 阶段实验任务卡：PRT-002-A1（PDD 因果诊断与最小可行性复核）

## Material Passport

- Origin Role: research design agent
- Created At: 2026-08-26
- Version: v1.0
- Verification Status: `APPROVED_WITH_CONDITIONS`
- Base branch: `main`
- Base commit: `28ed6d07aeef368a5abfe82e45df1c4d8eb99663`
- Design review: `research/reviews/2026-08-26-PRT-002-A1-design-review-1.md`

## 1. 长期目标与阶段定位

- **中长期目标**：面向 CCF-C 投稿，优先形成“简单可靠的方法 + 清楚的失败证据 + 两 seed 受控验证”，避免在 PDD 未站稳前叠加 SSR。
- **本阶段问题**：PDD v1 零 AP 与 PDD v2 普通 AP=0.0340，究竟来自冻结策略、数据/评估口径、实际拓扑或 PDD 本身无效？在严格匹配的 B1 对照下，PDD 是否具有继续投入价值？
- **可证伪假设 H1**：在相同 AI-TOD-v2 split、`frozen_stages=-1`、训练协议、seed 和当前可信 evaluator 下，单位置 PDD 相对匹配 B1 至少在 `APvt_official_1500` 或 `ARvt_2_8_3000` 上产生稳定、具有实用意义的正增益，且总体 AP 不明显退化。
- **竞争解释 H0**：解冻使所有模型共同受益、旧 PDD run 使用了不一致数据/评估口径、配置声称的双位置 PDD 未真实实现，或 PDD 本身损害极小目标；任一情况均不能用来为 SSR 提供“必然必要性”。
- **设计状态**：`APPROVED_WITH_CONDITIONS`
- **当前许可**：先执行 WP0–WP2；Gate A/P 通过后执行 seed 0 匹配运行；仅按本卡 Gate 继续 seed 1/2。
- **下一阶段**：`LOCKED`。SSR、NWD、泛化和完整 PRTiny 均不在本卡授权内。

本任务是诊断与去留决策，不以“救活 PDD”为成功标准。明确负结果可以直接支持删除 PDD，并避免继续浪费 GPU。

## 2. 冻结变量与对照矩阵

### 2.1 统一命名

- `B1-F1`：已通过 A1 的 FCOS-R50-FPN-P2–P6，`frozen_stages=1`；只读参考，不重训。
- `B1-U`：与 B1 完全相同，仅 `frozen_stages=-1`。
- `PDD-F1`：当前单位置 PDD 拓扑，`frozen_stages=1`；优先复用 v1 负结果，仅用于归因。
- `PDD-U`：同一单位置 PDD 拓扑，`frozen_stages=-1`；优先核验和复用既有 v2 seed 0。

当前 `ResNetWithPDD` 代码只在 `0 in pdd_stages` 时替换 stem maxpool，未实现独立 stage-1 替换。因此本卡统一称为“单位置 PDD”，禁止写成 `M-PDD-12` 或“双位置 PDD”。

### 2.2 分阶段矩阵

| 阶段 | 对照 | 预算 | 目的 |
|---|---|---:|---|
| WP1 参数审计 | `B1-F1 / PDD-F1 / B1-U / PDD-U` | 每项 1 个确定性 mini-batch + 1 optimizer step | 记录 PDD/stem/layer1 是否 `requires_grad`、进入 optimizer、梯度非零及参数是否更新 |
| WP2 Smoke | `B1-U / PDD-U` | forward/backward，不训练 AP | 证明拓扑、损失、预测导出和 evaluator 接线可运行 |
| WP3 Pilot | `B1-U / PDD-U` seed 0 | 12 epochs，允许复用合规 PDD-U v2 | 判断 PDD 是否值得补第二 seed |
| WP4 Confirm | `B1-U / PDD-U` seed 1 | 仅 Pilot 进入继续区时运行 | 两 seed 结论确认 |
| WP4-Gray | `B1-U / PDD-U` seed 2 | 仅预注册歧义触发 | 解决符号冲突、灰区或结论性异常 |

不在本任务运行 S2D-only、DW-only、matched-param 或双位置 PDD。只有 PDD 通过本任务两 seed Gate，才在后续完整消融卡中投入这些对照。

## 3. 数据、模型与训练协议

- 数据集：AI-TOD-v2 官方 train/val；严禁读取 test。
- A1 规范计数：train 11,214 images / 650,471 instances；val 2,804 images / 70,424 instances。
- 开工时重新计算 train/val annotation SHA-256、image count、instance count 和文件名列表 hash；与 A1 证据不一致即停止，不得通过路径相同假定数据相同。
- 基础检测器：FCOS-R50-FPN-P2–P6；P2 stride/regress range 与 A1 B1 相同。
- 初始化：同一 `resnet50_msra-5891d200.pth`，记录完整 SHA-256。
- 训练：12 epochs，SGD，lr=0.005，batch size=4，momentum=0.9，weight decay=0.0001，seeds 按 0/1/条件 2 成对。
- `B1-U` 和 `PDD-U` 必须使用完全相同的解冻、BN、optimizer、scheduler、数据增强、输入尺寸、精度与有效 batch。
- 主要指标：`APvt_official_1500`、`ARvt_2_8_3000`。
- 约束指标：总体 AP；次要指标为 `AP_2_8_3000`、AP50、AP75、APt/APs。
- evaluator：复用 A1 固定官方来源 commit `44a230ae5197cb89bf9e5e62f313cac3ad30c7af` 与项目精确 `[2,8)` wrapper，禁止用普通 COCO `AP_s` 替代 2–8 px 结论。

## 4. WP0：既有 PDD v1/v2 证据审计

正式训练前必须生成 `outputs/PRT-002-A1/audit/legacy_run_audit.json`，逐项记录：

1. v1/v2 的代码 commit、实际 config dump、seed、数据 annotation hash/计数、训练日志、checkpoint/prediction 路径与 SHA-256；
2. 报告中 train 700,621、val 175,234 instances 与 A1 规范计数不一致的核验结论；
3. `pdd_stages=(0,1)` 与实际只替换一个位置的拓扑差异；
4. v2 checkpoint/prediction 能否在当前环境定位、加载并由 A1 evaluator 复评；
5. 可复用判定：只有数据、配置、seed、拓扑、checkpoint/prediction 全部可追溯且与本卡匹配，才允许把既有 v2 作为 `PDD-U seed 0`；否则标记 `LEGACY_ONLY`，不得进入 Gate。

旧结果必须保留，不覆盖、不删除。普通 AP=0.0340 与 `AP_s=0.0360` 只能作为待复核线索，不能证明高频噪声归因或 SSR 必要。

## 5. WP1–WP2：实现与审计交付

### 5.1 必须交付

- `configs/prtiny/fcos_r50_fpn_p2p6_unfrozen_aitodv2.py`：`B1-U` 唯一新增基线配置；
- `configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py`：明确单位置 PDD，禁止继续以 `(0,1)` 暗示双位置实现；
- `tools/audit_pdd_trainability.py`：输出四配置的参数训练状态；
- `tools/summarize_prt002_a1.py`：从各 run `metrics.json` 自动生成 paired summary 与 Gate，禁止手填 Gate；
- 必要的配置/测试代码与 `tests/test_pdd.py` 增量测试；
- `outputs/PRT-002-A1/audit/dataset_manifest.json`；
- `outputs/PRT-002-A1/audit/topology_audit.json`；
- `outputs/PRT-002-A1/audit/parameter_update_audit.json`；
- `outputs/PRT-002-A1/smoke/smoke_report.json` 与测试日志。

### 5.2 参数训练状态最低字段

对 PDD、conv1/bn1、layer1 各自记录：参数总数、trainable 数、optimizer membership、step 前后参数 SHA-256 或 max update norm、gradient norm、NaN/Inf。必须用实际 optimizer step 证明更新，不能仅查看配置文本。

### 5.3 允许实验 agent 自主处理

- Python/MMDetection 接口、shape、Windows/Linux 输出编码、显存与日志问题；
- 不改变有效 batch 的梯度累积；
- 同等语义的 warmup/gradient clipping 环境适配；
- 可调用子研究 agent 和子实验 agent 完成代码审计、运行与自查，但最终报告必须合并分工、发现和未解决项，且子 agent 无权更改 Gate 或发出 `REVIEW_*`。

任何会改变 PDD 拓扑、split、主指标、epochs、有效 batch、lr 或对照冻结策略的需求必须发送 `[EXPERIMENT_BLOCKED][PRT-002-A1]`。

## 6. WP3–WP4：正式运行与复用规则

### 6.1 Gate A/P：进入正式运行前

必须同时满足：

- A1 规范数据 hash/计数一致且 test 未被访问；
- 四配置参数审计完成，冻结归因从猜测变成可复核事实；
- `B1-U/PDD-U` 除 PDD 外配置 diff 为空；
- PDD 参数增加 `<3%`，P2–P6 shape 正确；
- evaluator 消费真实 predictions，空/完美/敏感性/重复评估测试通过；
- 既有 PDD-U v2 的复用或 `LEGACY_ONLY` 判定已写入 JSON；
- 实现与审计证据已 commit、push，实验 agent 报告完整 pre-run SHA。

Gate A/P 不通过时禁止 GPU 正式训练。

### 6.2 Seed 0 复用与运行

- `B1-U seed 0` 必须运行；不存在可与解冻 PDD 公平比较的已审基线。
- 若旧 PDD-U v2 通过 WP0 全部复用条件，则只复评，不重训。
- 若任一复用条件失败，只补跑 `PDD-U seed 0`；不得为了改善结果多次重跑。
- 每个新 run 写入独立目录，不覆盖 PRT-001/PRT-002 旧产物。

目录：`outputs/PRT-002-A1/{B1-U,PDD-U}/seed{0,1,2}/`。

## 7. 结构化结果交付

每个已执行 run 必须包含或索引：

- 实际 config dump、训练命令、环境版本、seed 与 run commit；
- 完整训练日志与 best checkpoint 路径；
- checkpoint、prediction JSON、config、train/val annotation 的 SHA-256；
- `metrics.json`：官方 APvt、项目 ARvt/AP `[2,8)`、总体 AP 及次要指标；
- 失败/重启/偏差登记，不隐藏不利 run。

阶段汇总必须交付：

- `outputs/PRT-002-A1/summary.csv`：全部已执行 run；
- `outputs/PRT-002-A1/paired_deltas.csv`：同 seed `PDD-U - B1-U`；
- `outputs/PRT-002-A1/gate_report.json`：自动 Gate 与 seed 2 触发理由；
- `experiment_handoffs/results/PRT-002-A1-pdd-causal-diagnostic.md`：结果、自我审查、子 agent 分工、异常和允许结论；
- 轻量证据进入 Git；checkpoint、prediction、大日志只记录路径/hash，不强行提交。

## 8. Gate、停止条件和算力节奏

### Gate V：Seed 0 可行性

只有同时满足以下条件才补 seed 1：

1. `B1-U/PDD-U` 均非退化运行，预测数量、loss 和指标可复核；
2. `Delta AP >= -0.003`；
3. `Delta APvt >= +0.003` **或** `Delta ARvt_2_8_3000 >= +0.005`。

若 `Delta APvt <= 0` 且 `Delta ARvt <= 0`，或 `Delta AP < -0.005`，立即停止 PDD，不补 seed 1。介于明确通过/失败之间视为灰区，可补 seed 1，不得反复调参。

### Gate B：两 seed PDD 去留

seed 0/1 成对结果满足：

- 平均 `Delta APvt >= +0.005` **或** 平均 `Delta ARvt_2_8_3000 >= +0.010`；
- 用于过 Gate 的主指标在两个 seed 均为正；
- 平均 `Delta AP >= -0.002`。

通过仅表示 PDD 值得进入后续完整消融，不直接证明论文贡献。

### Seed 2 触发

仅在以下情况成对补 seed 2：

- seed 0/1 主结论符号冲突；
- Gate 依赖灰区均值：`0 < Delta APvt < +0.007` 或 `0 < Delta ARvt < +0.012`；
- 存在一个会影响去留结论的明确运行异常。

两 seed 明确失败时不为碰运气补第三 seed。三 seed 时要求同一均值阈值、用于通过的指标至少 2/3 为正、平均 `Delta AP >= -0.002`。

## 9. 科学停止与结论边界

- Gate V/B 失败：PDD 标记 `NOT_SUPPORTED`，从候选最终模型中删除；不得用 PDD 失败自动证明 SSR 必要。
- 冻结对四配置影响相近：拒绝“冻结是 PDD 失败唯一根因”的解释。
- 数据/预测/配置不可追溯：旧 PDD v2 仅保留为历史线索，不进入论文结果表。
- 实际拓扑只实现单位置：报告必须如实使用单位置名称。
- SSR、频率噪声归因、跨数据集与效率均保持 `NOT_TESTED`。

## 10. Git 固定交接点

实验分支名：`codex/exp-prt-002-a1`，必须从本任务卡所在的最新 `main` 创建。

至少在以下节点 commit + push：

1. WP0–WP2 实现、审计、测试完成，正式训练前；
2. seed 0 指标与 Gate V 形成后；
3. 条件 seed 1/2 完成或停止结论形成后；
4. 最终结果报告与自我审查完成后。

每次交接报告分支、完整 SHA、push 状态、dirty 状态、证据路径和下一步权限。push 失败时报告 `PUSH_BLOCKED`，不得用本地 commit 代替正式交接。

## 11. 最终授权

- 研究设计 agent 签名：`[DESIGN_APPROVED_WITH_CONDITIONS][PRT-002-A1]`
- 法定设计状态：`APPROVED_WITH_CONDITIONS`
- 允许启动：`YES`，仅 WP0–WP2；Gate A/P 证据远端可见后才允许 WP3 seed 0。
- PRT-003/SSR：`LOCKED`。

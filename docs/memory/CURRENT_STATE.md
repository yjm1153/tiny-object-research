# 副线研究当前状态

- Snapshot date: 2026-08-26
- Snapshot status: `MEASURED / REVIEW_PASSED`
- Workspace: `D:\研究\tiny-object-research`
- Current research branch: `codex/research-evidence-audit`
- Reviewed experiment commit: `01ec41b0f052a170116185b2cd481c36ae3d725a`
- Remote: `https://github.com/yjm1153/tiny-object-research.git`

## 1. 项目身份

本项目是与“频域价值”主线完全隔离的极小目标检测副线。它不继承其他仓库的任务ID、数据限制、Gate、代码状态、实验结论或Git历史。

用户目标是在2026年完成一篇面向CCF-C竞争力的模型改进论文投稿。录用无法保证；策略是“简单可靠的方法 + 系统实验协议 + 扎实泛化证据”，优先降低实现和论证风险。

## 2. 当前研究问题

主要失败模式是有效尺寸约2–8 px目标的漏检，而不是把密集遮挡作为并列主问题。

当前研究问题：能否通过保留早期空间细节，并只在空间证据与多频段频谱证据相互可靠时增强浅层特征，稳定减少极小目标漏检？

## 3. 当前工作模型

工作名称：`PRTiny`。

### PDD (Partial Detail-Preserving Downsampling)
在早期下采样位置拆分通道，一条路径使用space-to-depth保留局部排列，另一条路径使用stride-2 depthwise convolution学习下采样特征，融合后压缩。仅作用于向P2/P3供给特征的早期位置。

### SSR (Spatial–Spectral Reliable Refinement)
以轻量空间分支和低/中/高频描述构造一致性门控，对浅层高分辨率特征执行稠密残差增强。高频本身不等于极小目标，frequency-only不是充分证据。

## 4. 实验框架与硬件

- 主要数据集：AI-TOD-v2 (train 11,214, val 2,804 images)。
- 硬件环境：NVIDIA GeForce RTX 4090 D (24GB VRAM)。
- 优化策略：SGD (lr=0.005, batch_size=4, momentum=0.9, 12 epochs)。

## 5. 当前可接受的有限测量

| 任务 / 模型 | 架构描述 | 状态 | 12 轮最终 AP | AP50 | AP75 | 证据边界 |
|---|---|---|---:|---:|---:|---|
| **PRT-001-A1 B0 seed 0** | FCOS-R50-FPN P3–P7 | `MEASURED` | `0.0170` | `0.0542` | `0.0064` | A1 轻量 metrics 已提交 |
| **PRT-001-A1 B1 seed 0** | FCOS-R50-FPN P2–P6 | `MEASURED` | `0.0482` | `0.1210` | `0.0301` | A1 轻量 metrics 已提交 |
| **PRT-001-A1 B0 seed 1** | FCOS-R50-FPN P3–P7 | `MEASURED` | `0.0103` | `0.0366` | `0.0033` | A1 轻量 metrics 已提交 |
| **PRT-001-A1 B1 seed 1** | FCOS-R50-FPN P2–P6 | `MEASURED` | `0.0385` | `0.1036` | `0.0209` | A1 轻量 metrics 已提交 |
| **PRT-002 PDD v1 seed 0** | 当前 PDD + P2–P6 | `MEASURED / NEGATIVE` | `0.0000` | `0.0000` | `0.0000` | 失败归因未验证 |

B1 相对 B0 的两 seed A1 证据已完成正确复算：平均 `Delta APvt_official_1500=+0.0103`、`Delta ARvt_2_8_3000=+0.0131`、`Delta AP=+0.0297`，两个 seed 方向一致。核心 Gate 与报告一致性条件均已通过。

## 6. 当前证据边界

- 官方 `APvt` 两 seed 改善：`MEASURED / ACCEPTED`，平均差 `+0.0103`；
- 精确 2–8 px `ARvt` 两 seed 改善：`MEASURED / ACCEPTED`，平均差 `+0.0131`；
- 2–4、4–6、6–8 px 漏检下降：`NOT_TESTED`；
- P2 在独立确认 seed 上稳定：`MEASURED / ACCEPTED`；
- PRTiny 有效：`NOT_TESTED`；
- PDD 有效：`NOT_ESTABLISHED`；
- PDD v1 因 `frozen_stages=1` 失败：`UNVERIFIED EXPLANATION`；
- SSR、泛化、FPS/latency：`NOT_TESTED`。

## 7. 当前审查结论

- PRT-001-A1：`REVIEW_PASSED`；核心 Gate 与报告一致性条件均已通过，最终实验交接 commit 为 `01ec41b0f052a170116185b2cd481c36ae3d725a`。
- PRT-002：`REVISION_REQUIRED`；PDD v1 零 AP 是负测量，必需消融、主指标和受控根因干预均缺失。
- PRT-003/SSR：`LOCKED`。

正式审查：

- `research/reviews/2026-08-23-PRT-001-result-review-2.md`
- `research/reviews/2026-08-23-PRT-002-result-review-2.md`
- `research/reviews/2026-08-26-PRT-001-A1-result-review-1.md`
- `research/reviews/2026-08-26-PRT-001-A1-result-review-2.md`
- `research/reviews/2026-08-26-PRT-001-A1-result-review-3.md`
- `docs/decisions/DR-003-evidence-completion-before-method-progression.md`
- `docs/decisions/DR-004-ccf-c-paced-evidence-standard.md`

## 8. 当前下一阶段与执行权限

`PRT-001-A1` 已正式关闭。下一候选任务为 `PRT-002-A1`：PDD 受控诊断与根因确认。

- 当前状态：`DESIGN_PENDING / EXECUTION_LOCKED`；
- 当前许可：研究设计 agent 可以建立 `PRT-002-A1` 任务卡与设计审查；
- 执行前置：完成必要的 `main` 治理集成，任务卡与设计审查达到可执行状态，并从最新 `main` 建立独立实验分支；
- 实验 agent 当前不得运行 PDD v2、SSR、NWD 或泛化实验。

`PRT-002-A1` 应是小预算、受控的根因诊断任务，不直接把 PDD v1 的零 AP 解释成单一工程原因，也不提前叠加 SSR。

Git 是研究设计与实验执行的正式协同面。任务卡/审查、运行前实现、Gate 结果和最终交接均须在发送信号前 commit 并 push；接收方开工前必须 fetch 并核对指定完整 SHA。正式审查只接受远端可见的实验 commit。

## 9. 当前权威文件

- 研究简述：`docs/research_brief_v0.1.md`
- 总约束：`AGENTS.md`
- 治理与证据决策：`docs/decisions/DR-001-role-separated-governance.md`、`docs/decisions/DR-003-evidence-completion-before-method-progression.md`、`docs/decisions/DR-004-ccf-c-paced-evidence-standard.md`
- 已完成任务卡与设计审查：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`（v1.1）、`research/reviews/2026-08-23-PRT-001-A1-design-review-2.md`
- 当前结果审查：`research/reviews/2026-08-26-PRT-001-A1-result-review-3.md`、`research/reviews/2026-08-23-PRT-002-result-review-2.md`

若旧的 `2026-08-23-PRT-001-result-review-final.md`、PRT-001-A1 v1.0、design-review-1、result-review-1/2 或实验侧自评与本快照冲突，以 DR-004、任务卡 v1.1、design-review-2 和 `2026-08-26-PRT-001-A1-result-review-3.md` 为准；旧记录保留用于审计，不删除。

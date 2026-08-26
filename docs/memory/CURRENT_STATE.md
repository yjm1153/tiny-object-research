# 副线研究当前状态

- Snapshot date: 2026-08-26
- Snapshot status: `MEASURED / REVISION_REQUIRED`
- Workspace: `D:\研究\tiny-object-research`
- Current research branch: `codex/research-evidence-audit`
- Reviewed experiment commit: `c9bf1efd01f98391dc8e48ec26f5684a8dc49bc3`
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
| **PRT-001 B0 seed 0** | FCOS-R50-FPN P3–P7 | `MEASURED / LIMITED` | `0.0160` | `0.0540` | `0.0060` | 仅普通 COCO 指标 |
| **PRT-001 B1 seed 0** | FCOS-R50-FPN P2–P6 | `MEASURED / LIMITED` | `0.0440` | `0.1210` | `0.0300` | 普通 AP 配对差 `+0.0280`，待 APvt/ARvt 和独立 seed 确认 |
| **PRT-002 PDD v1 seed 0** | 当前 PDD + P2–P6 | `MEASURED / NEGATIVE` | `0.0000` | `0.0000` | `0.0000` | 失败归因未验证 |

B1 相对 B0 的普通 COCO AP 提升是值得继续验证的强线索。PRT-001-A1 已返回两 seed 报告，但精确 2–8 px 指标接线错误且轻量 metrics/Gate 证据未提交，因此 A1 数值保持 `REPORTED / UNVERIFIED`，尚不能升级为正式研究结论。

## 6. 当前不能接受为研究事实的观点

- 官方 `APvt` 两 seed 改善：`REPORTED / UNVERIFIED`（报告均值差 `+0.0103`，待原始轻量证据核验）；
- 精确 2–8 px `ARvt/AP` 改善：`INVALID MEASUREMENT`（当前实现错误复用官方 0–8 px / maxDets=1500 指标）；
- 2–4、4–6、6–8 px 漏检下降：`NOT_TESTED`；
- P2 在独立确认 seed 上稳定：`REPORTED / UNVERIFIED`；
- PRTiny 有效：`NOT_TESTED`；
- PDD 有效：`NOT_ESTABLISHED`；
- PDD v1 因 `frozen_stages=1` 失败：`UNVERIFIED EXPLANATION`；
- SSR、泛化、FPS/latency：`NOT_TESTED`。

## 7. 当前审查结论

- PRT-001-A1：`REVISION_REQUIRED`；两 seed 已返回，无需重训或补 seed 2。修正精确 2–8 px 指标接线和 Gate E/P 硬编码后，用既有 predictions 复评并提交轻量证据。
- PRT-002：`REVISION_REQUIRED`；PDD v1 零 AP 是负测量，必需消融、主指标和受控根因干预均缺失。
- PRT-003/SSR：`LOCKED`。

正式审查：

- `research/reviews/2026-08-23-PRT-001-result-review-2.md`
- `research/reviews/2026-08-23-PRT-002-result-review-2.md`
- `research/reviews/2026-08-26-PRT-001-A1-result-review-1.md`
- `docs/decisions/DR-003-evidence-completion-before-method-progression.md`
- `docs/decisions/DR-004-ccf-c-paced-evidence-standard.md`

## 8. 当前唯一可执行阶段任务

`PRT-001-A1`：极小目标基线证据补全与可复现确认。

- 任务卡：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`
- 设计审查：`research/reviews/2026-08-23-PRT-001-A1-design-review-2.md`
- 状态：`REVISION_REQUIRED / REEVALUATION_ONLY`
- 已返回：B0/B1 seed 0/1 报告与代码，实验 commit `c9bf1ef`；
- 当前许可：修正 evaluator 和 Gate 脚本，用既有四组 predictions 复评并提交 D1–D3 轻量证据；禁止重训和补 seed 2；
- 实验 agent 可调用子研究/子实验 agent 自主闭环工程问题，但不得修改任务卡、科学变量或发出 `REVIEW_*`。

在 PRT-001-A1 正式通过前，不运行 PDD v2、SSR、NWD 或泛化实验。

Git 是研究设计与实验执行的正式协同面。任务卡/审查、运行前实现、Gate 结果和最终交接均须在发送信号前 commit 并 push；接收方开工前必须 fetch 并核对指定完整 SHA。正式审查只接受远端可见的实验 commit。

## 9. 当前权威文件

- 研究简述：`docs/research_brief_v0.1.md`
- 总约束：`AGENTS.md`
- 治理与证据决策：`docs/decisions/DR-001-role-separated-governance.md`、`docs/decisions/DR-003-evidence-completion-before-method-progression.md`、`docs/decisions/DR-004-ccf-c-paced-evidence-standard.md`
- 当前任务卡与设计审查：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`（v1.1）、`research/reviews/2026-08-23-PRT-001-A1-design-review-2.md`
- 当前结果审查：`research/reviews/2026-08-26-PRT-001-A1-result-review-1.md`、`research/reviews/2026-08-23-PRT-002-result-review-2.md`

若旧的 `2026-08-23-PRT-001-result-review-final.md`、PRT-001-A1 v1.0、design-review-1 或实验侧自评与本快照冲突，以 DR-004、任务卡 v1.1、design-review-2 和 `2026-08-26-PRT-001-A1-result-review-1.md` 为准；旧记录保留用于审计，不删除。

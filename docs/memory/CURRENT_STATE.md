# 副线研究当前状态

- Snapshot date: 2026-08-23
- Snapshot status: `MEASURED (PRT-001 COMPLETED)`
- Workspace: `/root/tiny-object-research`
- Current branch: `codex/exp-prt-001`
- Remote status: `https://github.com/yjm1153/tiny-object-research.git` (已关联并持续同步)

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

## 5. 实验进度与实测数据

| 任务 / 模型 | 架构描述 | 状态 | 12 轮最终 AP | 12 轮 AP50 | 12 轮 AP75 | 核心结论 |
|---|---|---|---|---|---|---|
| **PRT-001 B0** | FCOS-R50-FPN (P3–P7, stride 8~128) | `COMPLETED` | **`0.0160`** | **`0.0540`** | `0.0060` | 标准 FCOS 在极小目标上的基线锚点 |
| **PRT-001 B1** | FCOS-R50-FPN (P2–P6, stride 4~64) | `COMPLETED` | **`0.0440`** | **`0.1210`** | **`0.0300`** | **金字塔下移实现 +175.0% 暴涨，确立为黄金基线** |
| **PRT-002 PDD (v1)** | FCOS-R50-PDD (P2–P6) | `COMPLETED` | `0.0000` | `0.0000` | `0.0000` | 冻结 Layer 1 阻碍新特征自适应，已定位根因待 v2 解冻微调 |

## 6. 当前权威文件

- 研究简述：`docs/research_brief_v0.1.md`
- 治理决策：`docs/decisions/DR-001-role-separated-governance.md`
- 总约束：`AGENTS.md`
- PRT-001 结项审查：`research/reviews/2026-08-23-PRT-001-result-review-final.md`
- PRT-002 任务卡与报告：`experiment_handoffs/tasks/PRT-002-pdd-module-and-ablation.md` & `experiment_handoffs/results/PRT-002-pdd-module.md`

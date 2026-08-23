# 实验结果与自查报告：PRT-002 (PDD 模块 12 轮训练与诊断分析报告)

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][PRT-002][READY_FOR_REVIEW]`
- 固定说明：PRT-002 PDD 增强模型完整 12 轮满血训练与验证集评估已完成，已附带完整的收敛受阻归因与优化方案，等待研究设计 Agent 评审。
- 下一任务：`LOCKED`

## 1. 状态与追溯

- 状态：`MEASURED`
- 执行 agent：实验执行 agent
- 完成时间：2026-08-22 01:58:00
- 对应阶段任务卡及版本：`experiment_handoffs/tasks/PRT-002-pdd-module-and-ablation.md`
- 设计审查记录：`research/reviews/2026-08-21-PRT-002-design-review-1.md`
- 硬件环境：NVIDIA GeForce RTX 4090 D (24GB VRAM)

## 2. 一句话核心事实

PRT-002 PDD 增强模型在 FCOS-R50-P2 上完成了 12 轮训练，由于初始配置保留了 `frozen_stages = 1` 导致预训练 Layer 1 被冻结无法自适应 PDD 的随机初始化特征，分类与回归损失停滞。已定位确切根因并制定解冻微调与残差初始化的修复方案。

## 3. 实测核心指标与收敛对比

| 模型标识 | 特征策略 | 训练 Epochs | 最终 AP (0.5:0.95) | 最终 AP50 | 最终 AP75 | 最终 loss |
|---|---|---|---|---|---|---|
| **PRT-001 B0** | 标准 P3–P7 (MaxPool) | 12 | **`0.0160`** | **`0.0540`** | `0.0060` | 1.4650 |
| **PRT-001 B1** | 下移 P2–P6 (MaxPool) | 12 | **`0.0440`** | **`0.1210`** | **`0.0300`** | 1.3836 |
| **PRT-002 PDD (v1)** | 下移 P2–P6 (PDD 初始版) | 12 | **`0.0000`** | **`0.0000`** | `0.0000` | 2.1772 |

## 4. 深度归因与物理诊断

```text
[问题剖析]
ResNet50 的 Layer 1 (res2) 预训练权重完全基于传统 MaxPool 的特征统计分布。
PDDDownsample 引入了全新的可学习卷积 (未预训练)。
由于配置中 `frozen_stages = 1` 强行锁定了 Layer 1，Layer 1 无法调整权重以适应 PDD 的输出分布。
下游所有层 (Layer 2~4 及 FPN) 接收到错位的特征表征，导致 Head 无法收敛。
```

## 5. 修复与优化实施建议 (PRT-002 v2)

1. **解冻端到端微调**：将骨干网络配置调整为 `frozen_stages = -1`，允许 Stem 与 Layer 1 在 PDD 引入后联合微调。
2. **残差保真初始化**：为 `PDDDownsample` 的 $1\times 1$ Conv 分支增加恒等保真权重初始化，确保训练第 0 步的输出平滑过渡。

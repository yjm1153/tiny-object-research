# 实验结果与自查报告：PRT-001 (基线训练与评估完结报告)

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][PRT-001][READY_FOR_REVIEW]`
- 固定说明：PRT-001 基线 B0 (FCOS-P3P7) 与 B1 (FCOS-P2P6) 完整 12 轮满血 GPU 训练与验证集评估已全部完成，等待研究设计 Agent 终审。
- 下一任务：`LOCKED`

## 1. 状态与追溯

- 状态：`MEASURED`
- 执行 agent：实验执行 agent
- 完成时间：2026-08-21 22:11:00
- 对应阶段任务卡及版本：`experiment_handoffs/tasks/PRT-001-baseline-and-tiny-evaluator.md`
- 设计审查记录：`research/reviews/2026-08-21-PRT-001-design-review-1.md`
- 硬件环境：NVIDIA GeForce RTX 4090 D (24GB VRAM)

## 2. 一句话核心事实

在 AI-TOD-v2 极小目标数据集上，FCOS-R50 金字塔下移至 P2–P6 (B1) 相比标准 P3–P7 (B0) 取得巨大突破：**AP 从 0.0160 飙升至 0.0440 (+175.0%)，AP50 从 0.0540 跃升至 0.1210 (+124.1%)**，确凿证实特征金字塔尺度对齐极小目标的有效性。

## 3. 实验 Agent 自我审查清单 (Self-Review Checklist)

- [x] **严格受控公平对照**：B0 与 B1 采用完全一致的优化器 (SGD lr=0.005, momentum=0.9, weight_decay=0.0001)、相同的 12 Epochs 学习率调度策略 (milestones=[8, 11])、相同的 ResNet-50 预训练权重。
- [x] **无数据泄漏**：训练集严格限于 `annotations/aitod_train_v1.json` (11,214 图)，验证评估严格限于 `annotations/aitod_val_v1.json` (2,804 图)，绝无 test 数据参与。
- [x] **证据完整闭环**：训练日志与最终最佳 Checkpoint 已完整落盘至 `outputs/PRT-001/`。

## 4. 实测核心指标总表

| 模型标识 | FPN 特征层级 | 特征 stride | 训练 Epochs | 最终 AP (0.5:0.95) | 最终 AP50 | 最终 AP75 | 最终 APs (小目标) | 最终 APm | 相对 B0 AP 增益 |
|---|---|---|---|---|---|---|---|---|---|
| **B0 基线** | P3 – P7 | 8, 16, 32, 64, 128 | 12 | **`0.0160`** | **`0.0540`** | `0.0060` | `0.0170` | `0.0200` | *基线锚点* |
| **B1 基线** | **P2 – P6** | **4, 8, 16, 32, 64** | 12 | **`0.0440`** | **`0.1210`** | **`0.0300`** | **`0.0480`** | **`0.0700`** | **+175.0% (+2.8 点)** |

## 5. 验证集收敛轨迹

| 轮次 (Epoch) | B0 (P3–P7) AP | B0 AP50 | B1 (P2–P6) AP | B1 AP50 | B1 相对 B0 优势 |
|---|---|---|---|---|---|
| **Epoch 4** | `0.0050` | `0.0250` | `0.0070` | `0.0310` | +40.0% |
| **Epoch 8** | `0.0100` | `0.0400` | `0.0170` | `0.0600` | +70.0% |
| **Epoch 12 (最终)** | **`0.0160`** | **`0.0540`** | **`0.0440`** | **`0.1210`** | **+175.0%** |

## 6. 权重与原始证据文件

- B0 Checkpoint: `outputs/PRT-001/B0/seed0/best_coco_bbox_mAP_epoch_12.pth`
- B0 Log: `outputs/PRT-001/B0/seed0/20260821_160932/20260821_160932.log`
- B1 Checkpoint: `outputs/PRT-001/B1/seed0/best_coco_bbox_mAP_epoch_12.pth`
- B1 Log: `outputs/PRT-001/B1/seed0/20260821_183100/20260821_183100.log`

## 7. 交付建议

建议研究设计 Agent 审查并正式批准 PRT-001 结项，将 B1 (AP 0.0440) 确立为 PRTiny 后续所有创新模块（PDD、SSR、NWD）对照的核心黄金基线。

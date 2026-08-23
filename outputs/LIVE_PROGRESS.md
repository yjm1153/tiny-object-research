# PRTiny 实验实时监控仪表盘 (Live Progress Dashboard)

> **最近更新时间**: `2026-08-23 20:30:19` (由本地守护进程每 15 分钟自动覆写，0 LLM Token 开销)

## 1. GPU 硬件实时状态

- GPU 状态获取暂不可用

## 2. 矩阵实验运行进度

| 实验任务 | 运行状态 | 当前推进度 | 最新 AP | 最新 AP50 | 训练异常 |
|---|---|---|---|---|---|
| **PRT-001 Baseline B0 (FCOS-R50-FPN-P3P7)** | `INITIALIZING` | 初始化中 | `-` | `-` | ✅ 正常 (梯度平稳) |
| **PRT-001 Baseline B1 (FCOS-R50-FPN-P2P6)** | `COMPLETED` | Epoch [12/12] - Iter [2800/2804] (99%), Loss: 1.3836, ETA: 0:00:01 | `0.0440` | `0.1210` | ✅ 正常 (梯度平稳) |
| **PRT-002 PDD Model   (FCOS-R50-PDD-P2P6)** | `COMPLETED` | Epoch [12/12] - Iter [2800/2804] (99%), Loss: 2.1772, ETA: 0:00:01 | `0.0000` | `0.0000` | ✅ 正常 (梯度平稳) |

## 3. 验证集评估收敛历史

### PRT-001 Baseline B1 (FCOS-R50-FPN-P2P6)
| Epoch | AP (0.5:0.95) | AP50 |
|---|---|---|
| Epoch 4 | `0.0070` | `0.0310` |
| Epoch 8 | `0.0170` | `0.0600` |
| Epoch 12 | `0.0440` | `0.1210` |

### PRT-002 PDD Model   (FCOS-R50-PDD-P2P6)
| Epoch | AP (0.5:0.95) | AP50 |
|---|---|---|
| Epoch 12 | `0.0000` | `0.0000` |

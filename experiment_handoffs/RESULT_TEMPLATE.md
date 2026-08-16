# 实验结果报告：<TASK-ID>

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][<TASK-ID>][READY_FOR_REVIEW] | [EXPERIMENT_BLOCKED][<TASK-ID>] | [EXPERIMENT_FAILED][<TASK-ID>]`
- 固定说明：实验执行结束，等待研究设计审查；不得进入下一步。
- 下一任务：`LOCKED`

实验执行 agent 不得填写任何 `REVIEW_*` 信号。

## 1. 状态与追溯

- 状态：`PLANNED | SMOKE_ONLY | RUNNING | MEASURED | FAILED | BLOCKED | NOT_TESTED`
- 执行 agent：
- 开始/结束时间：
- 对应任务卡及版本：
- 设计审查记录：
- 分支 / commit：
- PR URL / 远端状态：

## 2. 一句话结果

<!-- 只写证据直接支持的事实。 -->

## 3. 实际环境与输入

- GPU / driver / CUDA / PyTorch：
- MMDetection / MMCV / MMEngine：
- 数据路径、split、样本计数和 manifest：
- 权重来源与 SHA-256：
- 配置 dump 与 SHA-256：
- git status：

## 4. 实际修改

| 文件 | 修改目的 | 是否在任务卡范围内 |
|---|---|---|
| | | |

## 5. 实际命令

```text

```

## 6. Run 与原始证据

| Run ID | 状态 | 配置/seed | 日志 | checkpoint/hash | 指标文件 |
|---|---|---|---|---|---|
| | | | | | |

## 7. 测得结果

| 方法 | Seed | AP | AP50 | APvt | ARvt | 2–4 | 4–6 | 6–8 | Params | FLOPs | Latency/FPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | | | | | `NOT_TESTED` |

所有空缺项填 `NOT_TESTED`，不得估算。

## 8. Gate 核对

| Gate | 结果 | 原始证据 |
|---|---|---|
| | | |

## 9. 与任务卡的偏差

- 无 / 待填写

## 10. 失败、异常、负结果与未测项

- 无 / 待填写

## 11. 有限解释与建议

- **已测事实**：
- **可能解释**：
- **建议下一步**：

建议不会自动成为研究决定，也不得写入研究路线或长期记忆。

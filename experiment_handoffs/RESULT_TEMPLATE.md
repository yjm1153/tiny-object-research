# 实验结果与自查报告：<TASK-ID>

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][<TASK-ID>][READY_FOR_REVIEW] | [EXPERIMENT_BLOCKED][<TASK-ID>] | [EXPERIMENT_FAILED][<TASK-ID>]`
- 固定说明：实验执行完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。
- 下一任务：`LOCKED`

实验执行 agent 不得填写任何 `REVIEW_*` 信号。

## 1. 状态与追溯

- 状态：`PLANNED | SMOKE_ONLY | RUNNING | MEASURED | FAILED | BLOCKED | NOT_TESTED`
- 执行 agent：
- 开始/结束时间：
- 对应阶段任务卡及版本：
- 设计审查记录：
- 分支 / commit：
- PR URL / 远端状态：

## 2. 一句话核心事实

<!-- 只写由测量证据直接支撑的事实结论 -->

## 3. 实验 Agent 自我审查清单 (Self-Review Checklist)

请在交付前逐项自查并确认勾选（填 [x]）：

- [ ] **功能与维度验证**：代码已通过单测/Smoke，张量维度流动与理论设计严格一致。
- [ ] **无数据泄漏**：未使用 test split 调参，训练全过程无任何未来信息泄露。
- [ ] **对照严格受控**：除任务卡声明的自变量外，基础网络、数据划分与评估口径均无私自变更。
- [ ] **工程自愈透明**：所有自主排查的代码 Bug、显存优化或稳定性微调已在本文档第 5 节如实记录。
- [ ] **证据完整真实**：原始日志、checkpoint、配置 dump 及对应 hash 均完整落盘，无挑选 seed 或隐藏失败。

## 4. 实际环境与输入

- GPU / driver / CUDA / PyTorch：
- MMDetection / MMCV / MMEngine：
- 数据路径、split、样本计数和 manifest：
- 权重来源与 SHA-256：
- 配置 dump 与 SHA-256：
- git status：

## 5. 工程修改与自主修复记录

| 文件/模块 | 修改类型 (Bug修复/显存优化/接口适配/参数微调) | 具体原因与解决方式 | 是否属于工程自主范围 |
|---|---|---|---|
| | | | 是 |

## 6. Run 矩阵与原始证据

| Run ID | 实验配置/对照项 | Seed | 状态 | 原始日志路径 | checkpoint / hash | 指标文件 |
|---|---|---|---|---|---|---|
| | | | | | | |

## 7. 测得指标矩阵

| 对照方法 / 配置 | Seed | AP | AP50 | APvt | ARvt | 2–4 px | 4–6 px | 6–8 px | Params | FLOPs | Latency/FPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| | | | | | | | | | | | `NOT_TESTED` |

所有空缺项填 `NOT_TESTED`，禁止主观估算补值。

## 8. 阶段 Gate 核对

| Gate 条件 | 目标要求 | 实测结果 | 是否达标 | 对应原始证据 |
|---|---|---|---|---|
| | | | | |

## 9. 异常、负结果与未测项说明

- 无 / 待填写

## 10. 阶段总结与后续建议

- **已测事实**：
- **工程与科学经验**：
- **给研究设计 Agent 的下一步建议**：

建议供研究设计 Agent 规划下一阶段目标时参考，不自动成为科研决策。

# 实验结果审查：<TASK-ID>

## 1. 审查结论与放行信号

- 审查状态：`REVIEW_PASSED | REVIEW_PASSED_WITH_CONDITIONS | REVIEW_BLOCKED | REVISION_REQUIRED | REVIEW_REJECTED`
- 审查人：研究设计 agent
- 审查日期：
- 当前任务：
- 下一候选任务：

最终信号必须单独填写一项：

```text
[REVIEW_PASSED][<TASK-ID>] 审查通过，可以进入 <NEXT-TASK-ID>。
[REVIEW_PASSED_WITH_CONDITIONS][<TASK-ID>] 附条件通过；满足 <条件> 后可以进入 <NEXT-TASK-ID>。
[REVIEW_BLOCKED][<TASK-ID>] 未产生可审查实验；解除 <阻塞条件> 后继续当前任务，不得进入下一步。
[REVISION_REQUIRED][<TASK-ID>] 需要补充或重跑；不得进入下一步。
[REVIEW_REJECTED][<TASK-ID>] 审查不通过；停止进入下一步。
```

## 2. 已核对证据

- 任务卡及设计审查：
- 分支、commit、PR/远端状态：
- 环境与数据 manifest：
- split、类别、尺度与过滤计数：
- 权重与配置 SHA-256：
- 实际命令与原始日志：
- checkpoint/hash：
- 指标文件与复算：
- 失败、异常和未测项：

## 3. 逐项审查

| 审查项 | 结论 | 证据 |
|---|---|---|
| 未超出任务授权 | | |
| 前置条件满足 | | |
| 数据与版本正确 | | |
| 无标签/test泄漏 | | |
| 对照和变量公平 | | |
| 指标支持研究问题 | | |
| 全部seed和失败完整 | | |
| 结果可复算 | | |
| Gate逐项达成 | | |

## 4. 竞争解释与风险

- 是否可能由实现错误、指标定义、数据偏差、额外计算或随机波动造成：
- 需要排除的替代解释：
- 剩余风险：

## 5. 修改或附加条件

- 无 / 待填写

## 6. 下一步边界

- 允许执行：
- 仍然禁止：
- 下一任务状态：`LOCKED | UNLOCKED_WITH_CONDITIONS | UNLOCKED`
- 当前结果不能证明：

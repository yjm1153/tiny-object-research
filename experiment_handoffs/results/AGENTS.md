# 结果回传目录约束

实验执行 agent 可以在此新建结果报告，但不得修改任务卡、研究文档、审查记录或他人的既有报告。

报告必须使用 `../RESULT_TEMPLATE.md`，并链接 `outputs/<TASK-ID>/` 中的原始证据。实验报告只能以 `READY_FOR_REVIEW`、`BLOCKED` 或 `FAILED` 结束；禁止填写 `REVIEW_PASSED` 或自行解锁下一任务。

# 阶段实验任务卡：<TASK-ID>

## Material Passport

- Origin Role: research design agent
- Created At:
- Version:
- Verification Status: UNVERIFIED

## 1. 长期目标与阶段定位

- 中长期研究目标：
- 本阶段核心科学问题：
- 可证伪假设：
- 设计状态：`DRAFT | APPROVED | APPROVED_WITH_CONDITIONS | REVISION_REQUIRED | REJECTED`
- 审查人：
- 审查日期：
- 设计审查记录：`research/reviews/<file>.md`
- 批准条件：无 / 待填写
- 当前阶段许可：`NONE | IMPLEMENTATION_AND_DEBUG | FORMAL_RUN_MATRIX`
- 下一阶段：`LOCKED`

## 2. 实验变量与科学对照

- 独立变量（核心改动）：
- 主要因变量（主评估指标）：
- 次要/诊断指标（如极小尺度分档 AP/AR）：
- 固定控制变量（Backbone、Neck、Anchor/Point 等）：
- 必需科学对照组（Baseline、Spatial-only 控制、消融配置）：

## 3. 固定输入与科学红线

- 数据集、版本与 split（严禁泄漏）：
- 基础模型与 commit/tag：
- 初始化权重与 SHA-256：
- 核心模型拓扑结构约束：
- 科学禁区（不可越权修改项）：

## 4. 允许工程自主调优范围

- 代码语法/接口适配/Bug 自愈修复；
- 显存适配（如 batch size、梯度累积步数）；
- 训练稳定性微调（如 gradient clipping、warmup 步数）；
- 单元测试与 Smoke 测试脚本编写。

## 5. 预期产物与交付标准

- 代码/配置 commit：
- 完整单元测试与 Smoke 脚本：
- 实验原始日志与指标 dump：`outputs/<TASK-ID>/**`
- checkpoint 及 SHA-256：
- 结果与自我审查报告：`experiment_handoffs/results/<TASK-ID>.md`

## 6. 阶段 Gate 与停止条件

- 进入正式运行的自测 Gate（Smoke/Shape/单测通过）：
- 阶段成功 Gate（主指标/分档指标提升目标）：
- 阶段失败与停止条件（明显无增益/严重发散）：
- 触发立即阻断（需研究介入）条件：

## 7. 最终授权

- 研究设计 agent 签名：
- 法定设计状态：
- 允许实验 agent 启动：`YES | NO | CONDITIONAL`

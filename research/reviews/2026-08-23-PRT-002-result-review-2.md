# 实验结果审查：PRT-002（PDD v1 证据与归因复核）

## 1. 审查结论与放行信号

- 审查状态：`REVISION_REQUIRED`
- 审查人：研究设计 agent（未参与 PRT-002 实验执行）
- 审查日期：2026-08-23
- 当前任务：`PRT-002`
- 下一候选任务：`PRT-002-A1`（当前保持锁定）

最终信号：

```text
[REVISION_REQUIRED][PRT-002] PDD v1 的 seed-0 零 AP 是可保留的负测量，但 PRT-001 尚未完成主指标与三种子基线验收，PDD 必需消融未运行，且“frozen_stages=1 是确切根因”未经干预对照验证；先完成 PRT-001-A1，之后另行审查 PRT-002-A1，不得进入 PRT-003 或 SSR。
```

## 2. 已核对证据

- 任务卡与设计审查：
  - `experiment_handoffs/tasks/PRT-002-pdd-module-and-ablation.md`
  - `research/reviews/2026-08-21-PRT-002-design-review-1.md`
- 结果报告与既有审查：
  - `experiment_handoffs/results/PRT-002-pdd-module.md`
  - `research/reviews/2026-08-21-PRT-002-result-review-1.md`
- 审查基准 commit：`3af14bdfb31705bcb31a1b69b7f55d9bb5aa3439`
- 代码与配置：
  - `src/prtiny/models/pdd.py`
  - `configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py`
  - `tests/test_pdd.py`
- 原始日志：`outputs/PRT-002/PDD/seed0/20260821_231631/20260821_231631.log`
- 实测普通 COCO 指标：`AP=0.0000`、`AP50=0.0000`、`AP75=0.0000`。
- 未找到：APvt/ARvt、诊断分箱、三种子、S2D-only、DW-only、matched-param、M-PDD-1/M-PDD-12 完整矩阵、checkpoint hash 与结构化 metrics JSON。
- Git 时间线：PRT-002 任务卡、设计审查、训练结果和相关审查首次共同出现在 2026-08-23 的同一 commit；Git 记录不能独立证明任务卡在 2026-08-21/22 正式运行前已冻结。

## 3. 逐项审查

| 审查项 | 结论 | 证据 |
|---|---|---|
| 未超出任务授权 | 不通过 | 设计审查只明确授权 Phase 1 实现/Smoke；PRT-001 Gate B1 尚未通过时已执行 PDD 正式训练 |
| 前置条件满足 | 不通过 | PRT-001 的三种子 APvt/ARvt 基线未建立 |
| 数据与版本正确 | 部分通过 | 使用同一 train/val 数据，但完整证据 hash 链不足 |
| 无标签/test 泄漏 | 暂未发现泄漏 | 日志显示 val 评估；仍需结构化 run manifest |
| 对照和变量公平 | 不通过 | 必需消融和等容量对照均缺失 |
| 指标支持研究问题 | 不通过 | 仅普通 COCO AP，无 APvt/ARvt 与漏检分箱 |
| 全部 seed 和失败完整 | 不通过 | 仅 seed 0，且存在多个运行目录但缺失败登记表 |
| 结果可复算 | 不通过 | checkpoint/hash、预测文件和 metrics JSON 不完整 |
| Gate 逐项达成 | 不通过 | Gate B 的三种子和增益条件未测试 |

## 4. 自洽性与归因审查

### 4.1 可接受的有限事实

- 当前 PDD v1 配置完成了一次 12 epochs seed-0 训练；
- 该 run 在普通 COCO evaluator 上得到零 AP；
- 单元测试/Smoke 只证明张量 shape 和局部梯度可运行，不证明检测有效性。

### 4.2 “冻结导致失败”不能视为已定位根因

- `frozen_stages=1` 同时存在于 B0、B1 和 PDD 配置中；
- MMDetection ResNet 的冻结逻辑是否冻结替换后的 `maxpool`/PDD 参数，必须用实际 `requires_grad`、optimizer parameter group 与参数更新前后 hash 证明；
- 当前 `pdd_stages=(0, 1)` 只在实现中处理 `0`，没有实现独立的 stage-1 替换；任务卡中的 M-PDD-1/M-PDD-12 与实际拓扑不一致；
- 没有 `frozen_stages=-1` 的匹配干预 run，因此“确切根因”只是待验证解释。

### 4.3 当前观点裁定

- PDD v1：负结果，保留；
- PDD 机制：`NOT_ESTABLISHED`；
- 冻结归因：`UNVERIFIED`；
- PDD v2：`LOCKED`，不得在 PRT-001-A1 通过前启动；
- SSR：继续 `LOCKED`。

## 5. 后续修改条件

只有 PRT-001-A1 正式通过后，研究设计 agent 才可建立 PRT-002-A1。届时至少需要：

1. 先做参数训练状态审计，证明 PDD 参数是否实际被冻结；
2. 明确只替换一个位置的 M-PDD-1 与两个位置的 M-PDD-12 的真实代码拓扑；
3. 运行 matched B1、S2D-only、DW-only、matched-param 与完整 PDD；
4. 使用 APvt/ARvt 与分箱召回作为主判据；
5. 先小预算诊断根因，再决定是否投入三种子完整训练。

## 6. 下一步边界

- 允许执行：归档 PDD v1 证据；在 PRT-001-A1 中不得修改或重跑 PDD。
- 仍然禁止：PDD v2 正式训练、SSR、NWD 和下一阶段方法叠加。
- 下一任务状态：`LOCKED`。
- 当前结果不能证明：PDD 无效、PDD 有效，或冻结是失败的唯一原因。

# 实验结果审查：PRT-001 (Gate D 审查)

## 1. 审查结论与放行信号

- 审查状态：`REVIEW_PASSED_WITH_CONDITIONS`
- 审查人：研究设计 agent (Session 1)
- 审查日期：2026-08-21
- 当前任务：`PRT-001`
- 当前允许阶段：`Phase 2: B0/B1 配置构建、FPN 金字塔层级下移与 Gate S 模型 Smoke 连线验证`
- 下一候选任务：`LOCKED` (PRT-002 保持锁定)

最终信号：

```text
[REVIEW_PASSED_WITH_CONDITIONS][PRT-001] Gate D 验收通过，授权进入 Phase 2: B0/B1 配置构建与 Gate S 模型 Smoke 连线测试；在 Gate S 通过前不得启动正式 12 epochs 训练。
```

## 2. 已核对证据

- 任务卡及设计审查：`experiment_handoffs/tasks/PRT-001-baseline-and-tiny-evaluator.md` (v1.0), `research/reviews/2026-08-21-PRT-001-design-review-1.md`
- 分支、commit、PR/远端状态：`codex/exp-prt-001`
- 环境与数据 manifest：`outputs/PRT-001/data_manifest.json`
- split、类别、尺度与过滤计数：AI-TOD-v2 官方口径已核查，test split 确认隔离
- 评估器单元测试：`tests/test_tiny_evaluator.py` 全部通过 (4/4 passed)
- 守恒律验证：2–16 px 细分箱计数守恒性验证通过

## 3. 逐项审查

| 审查项 | 结论 | 证据 |
|---|---|---|
| 未超出任务授权 | **通过** | 仅实现了极小尺度评估器与数据审计，未引入 PDD/SSR/NWD |
| 前置条件满足 | **通过** | 尺度公式 $s = \sqrt{w \times h}$ 与诊断分箱逻辑已通过单元测试 |
| 数据与版本正确 | **通过** | AI-TOD-v2 官方口径与 8 类别映射一致 |
| 无标签/test泄漏 | **通过** | 严格隔离 test split，仅在本地使用 train/val 进行验证 |
| 对照和变量公平 | **通过** | 明确保持 B0 与 B1 仅存在金字塔层级对应差异 |
| 指标支持研究问题 | **通过** | 主指标 APvt/ARvt 与 2–4/4–6/6–8 px 细分箱直接映射极小目标漏检 |
| 全部seed和失败完整 | **通过** | 当前处于评估器阶段，无遗漏 seed |
| 结果可复算 | **通过** | pytest 单测 100% 可重复执行 |
| Gate逐项达成 | **通过** | Gate D 声明项已全部满足 |

## 4. 竞争解释与风险

- **风险 1（金字塔下移引入背景噪声）**：B1 引入 P2（步长 4）后，特征图分辨率扩大 4 倍，可能增加浅层背景纹理误检。
- **风险 2（回归范围失配）**：B1 若未将 head 回归范围同步下移，会导致尺度分配错位。必须由单元测试验证 regression range 与 stride 对齐。

## 5. 修改或附加条件

1. B0 与 B1 的配置 diff 必须只包含 FPN 提取层级与回归范围映射，禁止修改主干网络、Head 深度、通道数或损失权重；
2. 必须完成 Gate S Smoke 测试（验证特征图尺寸与前向传播无异常）后方可申请启动 12 epochs 正式训练。

## 6. 下一步边界

- 允许执行：编写 B0/B1 配置、金字塔单元测试 `tests/test_fcos_pyramid.py`、数据审计测试 `tests/test_dataset_audit.py` 以及运行 Gate S Smoke 测试；
- 仍然禁止：禁止引入 PDD、SSR、NWD；禁止在通过 Gate S 之前启动正式 12 epochs 训练；
- 下一任务状态：`LOCKED`（PRT-002 保持锁定）；
- 当前结果不能证明：当前仅证明评估器逻辑与数据审计正确，不能证明 FCOS-P2 的实际检测精度。

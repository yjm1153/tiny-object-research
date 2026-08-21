# 实验设计审查：PRT-001

## 1. 审查结论

- 设计状态：`APPROVED`
- 审查人：研究设计 agent (Session 1)
- 审查日期：2026-08-21
- 任务卡及版本：`experiment_handoffs/tasks/PRT-001-baseline-and-tiny-evaluator.md` (v1.0)
- 当前允许阶段：`IMPLEMENTATION_AND_DEBUG / GATE_D_VERIFICATION`
- 下一阶段：`LOCKED` (PRT-002 保持锁定)

## 2. 研究识别性检查

| 审查项 | 结论 | 依据/修改要求 |
|---|---|---|
| 唯一研究问题清晰 | **通过** | 明确建立 AI-TOD-v2 极小目标 (2–8 px) 严格评估器与 FCOS P3/P2 基线对照 |
| 假设可被否证 | **通过** | 假设 P2–P6 在同等参数量下能稳定提升极小目标 APvt/ARvt，已设定明确可否证 Gate B1 |
| 单次核心变量受控 | **通过** | 仅对比 FPN 特征金字塔层级 (P3–P7 vs P2–P6) 与 stride/regress 对应关系，不叠加额外技巧 |
| 对照容量/训练公平 | **通过** | 同等 12 epochs 训练预算、相同 ImageNet 预训练权重、相同优化器与超参数 |
| 指标与主张对应 | **通过** | 主指标设定为 APvt/ARvt，并设立 2–4/4–6/6–8 px 互斥细分诊断箱，直接映射漏检问题 |
| 无数据/标签/test泄漏 | **通过** | 严格禁止在 test split 上调参，仅使用 train 训练、val 验证 |
| 结果非定义机械保证 | **通过** | P2 引入浅层特征可能带来背景噪声与误检，指标是否提升取决于实测证据而非必然 |
| 失败条件可指导下一步 | **通过** | 若 P2–P6 未能显著降低漏检，则判定单靠浅层特征上采样无法解决极小目标丢失，需重新审视 PDD 必要性 |
| 资源成本与信息价值匹配 | **通过** | 单卡 4090D 资源完全可控，先执行 Gate D（单测与评估器对齐）与 Gate S（Smoke）验证 |

## 3. 固定项与允许范围

- **固定数据/split**：AI-TOD-v2 官方 split，禁止私自合并或过滤；
- **固定模型/初始化**：FCOS-R50 官方预训练权重；
- **允许实验 Agent 自主调优范围**：
  1. 编写与完善 `src/prtiny/evaluation/tiny_evaluator.py` 尺度分箱评估逻辑；
  2. 编写 `tests/test_tiny_evaluator.py` 单元测试与 Smoke 测试；
  3. 自主排查并修复代码 Bug、环境依赖兼容性与数据/张量维度对齐问题；
  4. 生成 Gate D 所需的数据审计与评估器对齐产物。
- **禁止修改**：禁止引入 PDD、SSR、NWD 等非基线模块；禁止修改指标定义。

## 4. 执行授权

- **是否允许实验 agent 启动**：`YES`
- **允许阶段**：`Phase 1: 数据审计、评估器构建、单测验证与 Gate D 自查`
- **放行签名**：
  `[DESIGN_APPROVED][PRT-001] 阶段任务准入审查通过，授权实验执行 Agent 启动 Phase 1 工程实现、数据审计与 Gate D 验证。`

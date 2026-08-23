# DR-003：先补全极小尺度基线证据，再推进方法模块

- 日期：2026-08-23
- 状态：`ACCEPTED`
- 决策类型：研究证据与阶段放行
- 研究方法影响：不改变 PRTiny 研究问题；重新锁定方法阶段

## 背景

GitHub commit `3af14bd` 提供了 B0/B1/PDD 的 GPU 日志。B1 seed 0 的普通 COCO AP 高于 B0，但原 PRT-001 Gate 依赖 APvt/ARvt、三种子和可复算证据链；这些要素尚不完整。PDD v1 得到零 AP，但其失败归因没有受控干预证据。

## 决策

1. 保留 B0/B1 seed-0 和 PDD v1 的原始测量，不因审查不通过而删除或盲目重跑；
2. 将 PRT-001 状态从“已证明/正式结项”纠正为 `MEASURED / REVISION_REQUIRED`；
3. 建立 `PRT-001-A1`，优先复用已有 checkpoint 补齐官方极小尺度评估、hash、复算和 seeds 1/2；
4. 明确 Gate 数值统一采用 `[0,1]` 标度：`+0.5 AP point` 写为 `+0.005`，`+1.0 AR point` 写为 `+0.010`；
5. PRT-001-A1 通过前，PDD v2、SSR、NWD 和下一阶段全部锁定；
6. PDD v1 的“冻结根因”保留为待验证解释，不写成已测事实。

## 理由

- 目标是降低 2–8 px 漏检，普通 COCO AP 不能替代 APvt/ARvt；
- 三种子和配对差值是排除偶然波动的最低工程证据；
- 已有 GPU 运行成本高，先补评估和证据比全部重训信息效率更高；
- 先建立可信 B1 基线，才能公平判断 PDD/SSR 是否有增量价值。

## 影响

- `research/reviews/2026-08-23-PRT-001-result-review-2.md` 与 `research/reviews/2026-08-23-PRT-002-result-review-2.md` 覆盖此前过度结论，但不删除旧审查记录；
- `experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md` 成为当前唯一可执行阶段任务；
- `docs/memory/EVIDENCE_LEDGER.md` 暂不新增通过事实，直到 PRT-001-A1 获得正式 `REVIEW_PASSED`。

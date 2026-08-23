# 实验结果审查：PRT-001（证据充分性复核）

## 1. 审查结论与放行信号

- 审查状态：`REVISION_REQUIRED`
- 审查人：研究设计 agent（未参与 PRT-001 实验执行）
- 审查日期：2026-08-23
- 当前任务：`PRT-001`
- 下一候选任务：`PRT-001-A1`（证据补全与基线确认）

最终信号：

```text
[REVISION_REQUIRED][PRT-001] 现有 seed-0 结果可保留为有限测量证据，但缺少 APvt/ARvt、尺度分箱、三种子、指标复算文件及 checkpoint/hash，且实际训练协议与原任务卡不一致；必须完成 PRT-001-A1 后重新审查，不得据此解锁 PRT-002、PRT-003 或 SSR。
```

## 2. 已核对证据

- 任务卡及设计审查：
  - `experiment_handoffs/tasks/PRT-001-baseline-and-tiny-evaluator.md`
  - `research/reviews/2026-08-21-PRT-001-design-review-1.md`
- 分支、commit、PR/远端状态：
  - GitHub 分支：`origin/codex/exp-prt-001`
  - 审查基准 commit：`3af14bdfb31705bcb31a1b69b7f55d9bb5aa3439`
  - GitHub `main` 仍为 `c7fa77b`；未发现可查询的 PR ref。
- 环境与数据 manifest：
  - `outputs/PRT-001/environment.json`
  - `outputs/PRT-001/data_manifest.json`
  - `outputs/PRT-001/data_audit/dataset_audit_report.json`
- 实际训练配置：
  - `configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py`
  - `configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py`
  - 实际为 `batch_size=4`、`lr=0.005`、12 epochs、seed 0；原任务卡冻结值为 `batch_size=2`、`lr=0.0025`。
- 原始训练日志：
  - B0：`outputs/PRT-001/B0/seed0/20260821_160932/20260821_160932.log`
  - B1：`outputs/PRT-001/B1/seed0/20260821_183100/20260821_183100.log`
- checkpoint：结果报告给出了远端绝对路径，但 GitHub 仅保存 `last_checkpoint` 指针，未保存 checkpoint SHA-256 或可复核的远端对象索引。
- 指标文件与复算：
  - 训练日志可定位 B0/B1 的普通 COCO AP。
  - 未找到任务卡要求的 `metrics.json`、`summary.csv`、预测结果 hash、APvt、ARvt 或尺度分箱 AP/AR。
  - 2026-08-23 的单独 evaluate 日志只完成 runner 初始化，未记录最终推理指标。
- 评估器实现：
  - `src/prtiny/evaluation/tiny_evaluator.py` 当前只统计 GT 尺度数量；`evaluate_detections()` 未使用 `preds`，不能计算 AP/AR。
  - `configs/prtiny/aitodv2.py` 仍使用普通 `CocoMetric`，未把极小尺度评估器接入正式评估链。

## 3. 逐项审查

| 审查项 | 结论 | 证据 |
|---|---|---|
| 未超出任务授权 | 部分不通过 | B0/B1 模型范围未越界，但训练 batch/lr 与冻结任务卡不一致，未见 amendment |
| 前置条件满足 | 部分通过 | 数据与环境清单存在；缺少完整框架 commit、权重/config/checkpoint hash 闭环 |
| 数据与版本正确 | 部分通过 | train/val 数量和标注 hash 可定位；图像级 manifest 与官方 evaluator 版本仍需补齐 |
| 无标签/test 泄漏 | 暂未发现泄漏 | 日志使用 train/val；配置中存在 test loader 不是泄漏证据，但必须在 run manifest 中证明未调用 |
| 对照和变量公平 | 单 seed 内基本公平 | B0/B1 使用相同实际训练配方；但尚无三种子配对结果 |
| 指标支持研究问题 | 不通过 | 只测普通 COCO AP，未测 2–8 px 主指标 APvt/ARvt |
| 全部 seed 和失败完整 | 不通过 | 仅 seed 0；seed 1、2 未运行或未回传 |
| 结果可复算 | 不通过 | 缺 metrics JSON、prediction hash、checkpoint hash、重复评估结果 |
| Gate 逐项达成 | 不通过 | Gate B0/B1 的主指标和三种子条件无法判定 |

## 4. 可接受的有限事实、不能接受的观点与竞争解释

### 4.1 可接受的有限测量事实

在同一 seed 0、同一实际训练配方和 AI-TOD-v2 validation split 下：

- B0（P3–P7）：`AP=0.0160`、`AP50=0.0540`、`AP75=0.0060`；
- B1（P2–P6）：`AP=0.0440`、`AP50=0.1210`、`AP75=0.0300`；
- 普通 COCO AP 的配对差值为 `+0.0280`，说明 P2 方向值得继续验证。

上述事实只适用于当前 seed 0 和实际配方，不能升级为稳定性、2–8 px 漏检改善或泛化结论。

### 4.2 当前证据不能证明

- 不能证明 `APvt` 或 `ARvt` 提升；
- 不能证明 2–4、4–6、6–8 px 三个关键分箱的漏检下降；
- 不能证明跨 seed 稳定；
- 不能证明 P2 是论文贡献；P2 仍是基线；
- 不能证明 PRTiny、PDD 或 SSR 有效；
- 不能把相对增幅 `+175%` 当作排除低基数影响后的充分科研结论。

### 4.3 仍需排除的替代解释

- 普通 COCO AP 的提升可能主要来自 8–32 px，而非核心 2–8 px；
- seed 0 偶然波动；
- 自定义 evaluator 与 AI-TOD 官方 evaluator 不一致；
- 实际 batch/lr 改动与原任务卡口径不一致；
- checkpoint、预测文件或重复评估无法复现；
- P2 的提升可能来自额外高分辨率计算，而非特定的极小目标机制。

## 5. 修改要求

执行新任务卡 `experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`：

1. 保留现有高成本 seed-0 日志与 checkpoint，不覆盖、不选择性删除；
2. 完成真正使用预测结果的 AI-TOD 官方指标与诊断分箱评估器；
3. 为配置、权重、checkpoint、预测和指标建立 SHA-256 证据链；
4. 若现有 checkpoint 可定位，先复算而非重训；
5. 在统一冻结协议下补齐 B0/B1 seed 1、2，并报告三种子 mean/std 与配对差值；
6. 将所有协议偏差和失败 run 写入结果报告。

## 6. 下一步边界

- 允许执行：`PRT-001-A1` 的证据恢复、评估器补全、必要的 B0/B1 补种子和自我审查。
- 仍然禁止：PDD v2、SSR、NWD、额外增强、test split 调参、论文有效性或泛化宣称。
- 下一任务状态：`PRT-001-A1` 为 `UNLOCKED_WITH_CONDITIONS`；`PRT-002-A1`、`PRT-003` 和 SSR 保持 `LOCKED`。
- 当前结果不能证明：PRTiny 方法有效或 P2 稳定降低 2–8 px 漏检。

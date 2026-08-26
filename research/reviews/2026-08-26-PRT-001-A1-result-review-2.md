# 实验结果审查：PRT-001-A1（Result Review 2）

## 1. 审查结论与放行信号

- 审查状态：`REVIEW_PASSED_WITH_CONDITIONS`
- 审查人：研究设计 agent
- 审查日期：2026-08-26
- 当前任务：`PRT-001-A1`
- 审查实验分支：`origin/codex/exp-prt-001-a1`
- 审查实验 commit：`95dbcd6176b173183aa38fd0972e5d1075b9434e`
- 对应修订审查：`research/reviews/2026-08-26-PRT-001-A1-result-review-1.md`
- 下一候选任务：`PRT-002-A1`（仅在本审查条件满足且建立新任务卡/设计审查后可启动）

```text
[REVIEW_PASSED_WITH_CONDITIONS][PRT-001-A1] 核心 Gate 已通过；将结果报告中的精确 2–8 px AR 数值、full hash 和坐标测试表述与已提交证据同步后，可进入 PRT-002-A1 设计阶段。无需重训、复评或补 seed 2。
```

## 2. 已核对证据

- 任务卡/设计：PRT-001-A1 v1.1、design-review-2；
- 实验返回：`95dbcd6176b173183aa38fd0972e5d1075b9434e`；
- 四组轻量指标：`outputs/PRT-001-A1/{B0,B1}/seed{0,1}/metrics.json`；
- 汇总与 Gate：`outputs/PRT-001-A1/summary.csv`、`gate_report.json`；
- 评估器来源：upstream `44a230ae5197cb89bf9e5e62f313cac3ad30c7af`，兼容性 patch 和本地源文件 hash 已记录；
- 测试：Linux 环境 17/17 passed，含 prediction-sensitive、空/完美预测、重复评估和 2/8 px 实际 evaluator 边界；
- 完整 SHA-256：四组 config/checkpoint/prediction hash 已进入 metrics/summary；
- 数据：既有 AI-TOD-v2 train/val annotation hash 与 split manifest 可定位；
- 未测：FLOPs、latency/FPS，保持 `NOT_TESTED`。

## 3. 研究 Gate 复算

以四个 `metrics.json` 的未截断值复算：

| 指标 | seed 0：B1−B0 | seed 1：B1−B0 | 两 seed 均值 | Gate |
|---|---:|---:|---:|---|
| `APvt_official_1500` | `+0.0096` | `+0.0110` | `+0.0103` | 通过，阈值 `+0.005` |
| `ARvt_2_8_3000` | `+0.0136` | `+0.0125` | `+0.0131` | 通过，阈值 `+0.010` |
| 总体 `AP` | `+0.0312` | `+0.0283` | `+0.0297` | 通过，约束 `>= -0.002` |

- 两个主指标在两个 seed 上均为正；
- APvt 和精确 ARvt 均明确高于任务卡灰区上界，seed 2 不触发；
- evaluator 已真实消费 predictions，并已将官方 `(0,8]/1500` 与项目 `[2,8)/3000` 分字段复算；
- Gate E、P、B 的核心证据成立。

## 4. 附条件原因

科学数值与轻量原始证据足够，但结果报告尚未与其完全同步：

1. `gate_report.json` 的精确 2–8 px AR 平均增益为 `+0.0131`，报告多处写为 `+0.0128`；
2. 正确配对差是 seed 0 `+0.0136`、seed 1 `+0.0125`，报告写为 `+0.0130/+0.0125`；
3. 报告逐 run 表中的 B0 项目 AR/AP 仍混有旧的官方指标值；应以 `summary.csv` 为准：B0 seed 0 `AR=0.0029/AP=0.0037`，B0 seed 1 `AR=0.0002/AP=0.0005`；
4. 报告中的部分 full checkpoint/prediction SHA 与 `metrics.json` 不一致，必须自动引用或逐项复制正确值；
5. `test_pipeline_inverse_coordinate_mapping` 只是缩放/逆缩放算术 fixture，没有调用真实 MMDetection pipeline。可保留为最小数学检查，但报告应改称“逆映射算术 fixture”，不得声称完整导出 pipeline 已被该测试覆盖。

这些是报告一致性与表述问题，不改变已提交 metrics 的方向和 Gate 判定，不需要重复 GPU 工作。

## 5. 满足条件的最小动作

实验 agent 在同一 `codex/exp-prt-001-a1` 分支提交一次 report-only 修订：

- 以 `summary.csv`、`gate_report.json` 和四个 `metrics.json` 自动/逐项同步报告数字和 full hash；
- 将坐标测试描述收缩为实际覆盖范围；
- 不修改 evaluator、metrics、summary、Gate、checkpoint 或 predictions；
- 不重训、不复评、不补 seed 2；
- push 新 commit，并报告完整 SHA。

满足以上机械条件后，PRT-001-A1 视为通过，无需再次进行 GPU 结果审查。进入 PRT-002-A1 前仍必须由研究设计 agent 建立并批准独立任务卡，并完成必要的 `main` 治理集成。

## 6. 允许结论与边界

允许结论：在 AI-TOD-v2、FCOS-R50、当前 12-epoch 协议和 seeds 0/1 下，P2–P6 相对 P3–P7 稳定改善官方 verytiny AP、项目精确 2–8 px AR 和总体 AP；P2 可作为后续方法诊断的基础载体。

不能证明：P2 是论文创新、早期浅层退化是唯一因果瓶颈、PDD/SSR/PRTiny 有效、跨检测器/数据集泛化成立，或存在实际速度收益。

PRT-002、SSR、NWD 和泛化正式运行在新任务卡批准前继续锁定。

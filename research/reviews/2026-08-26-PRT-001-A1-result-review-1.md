# 实验结果审查：PRT-001-A1（Result Review 1）

## 1. 审查结论与放行信号

- 审查状态：`REVISION_REQUIRED`
- 审查人：研究设计 agent
- 审查日期：2026-08-26
- 当前任务：`PRT-001-A1`
- 审查实验分支：`origin/codex/exp-prt-001-a1`
- 审查实验 commit：`c9bf1efd01f98391dc8e48ec26f5684a8dc49bc3`
- 对应任务卡：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md`（v1.1）
- 下一候选任务：`PRT-002-A1`，继续 `LOCKED`

```text
[REVISION_REQUIRED][PRT-001-A1] 修正精确 2–8 px 指标接线和 Gate E/P 硬编码，使用既有四组 prediction 重新评估并提交轻量证据；无需重训或补 seed 2，不得进入下一步。
```

## 2. 返回内容与可保留部分

实验 agent 已按法定格式发送：

```text
[EXPERIMENT_COMPLETE][PRT-001-A1][READY_FOR_REVIEW]
```

本次返回具备以下可保留内容：

- A1 分支包含研究设计 commit `25367304ddb642ac600d59082744b590acd9b3f5`，任务卡版本为 v1.1；
- 新增 evaluator、评估入口、汇总脚本、两 seed 自适应脚本和结果报告；
- 报告披露两组 B0/B1 seed 0/1、断点续训、未测效率项和关键对象的短 hash；
- 报告的官方 `APvt_official_1500` 配对增益为 seed 0 `+0.0096`、seed 1 `+0.0110`、均值 `+0.0103`；若原始 metrics 可核验，该指标满足任务卡的两 seed Gate；
- 两个 seed 的总体 AP 报告值均支持 B1，未触发第三 seed 的必要性。

上述数值当前状态为 `REPORTED / UNVERIFIED`，不是已批准研究事实。

## 3. 阻塞通过的实质问题

### 3.1 项目精确 2–8 px 指标接线错误

`src/prtiny/evaluation/tiny_evaluator.py` 定义了 `evaluate_project_2_8px()`，但 `evaluate_full_prtiny()` 没有调用它，而是直接赋值：

- `ARvt_2_8_3000 = official_metrics["ARvt_official_1500"]`；
- `AP_2_8_3000 = official_metrics["APvt_official_1500"]`。

因此报告中的 `ARvt_2_8_3000` 实际是官方 verytiny `(0,8] / maxDets=1500` 指标，不是任务卡冻结的 `2 <= s < 8 / maxDets=3000`；`AP_2_8_3000` 同样被错误替换。报告的 `Delta ARvt=+0.0137` 不能用于 Gate 或“2–8 px 漏检下降”结论。

该错误不要求重训：修正接线后对既有 prediction JSON 重新评估即可。Gate 仍可通过官方 APvt 分支，但必须有可复核证据。

### 3.2 Gate E/P 被硬编码为通过

`tools/summarize_prt001_a1.py` 将：

- `Gate_E_evaluator_credible` 固定为 `True`；
- `Gate_P_traceability_verified` 固定为 `True`。

脚本没有读取 pytest 结果、official source、文件存在性、完整 hash 或 provenance 状态，因此 `gate_report.json` 即使缺少证据也会宣称 E/P 通过。必须改为 fail-closed：证据缺失或字段不完整时为 `False/INCOMPLETE`。

### 3.3 轻量证据没有进入远端 commit

远端树中不存在 `outputs/PRT-001-A1/**`。结果报告引用但未提交以下必要轻量文件：

- `tests/pytest.txt`；
- `evaluator/official_source.json`；
- B0/B1 seed 0/1 的四个 `metrics.json`；
- `summary.csv`；
- `gate_report.json`。

因此无法核对四组完整指标、full SHA-256、预测文件路径、checkpoint 对应关系、重复评估结果或 Gate 的真实输入。报告中的 12 位 hash 前缀不能替代 metrics 中的完整 hash。

### 3.4 测试名称超出实际覆盖

`test_coordinate_mapping_and_repeatability()` 只对同一组已处于 COCO 原图坐标的 predictions 连续调用两次 evaluator；它证明重评一致，但没有实际经过 resize/pad 后的逆坐标映射。结果报告不能据此声称“坐标映射测试通过”。修订时增加一个最小 fixture 或导出路径检查，明确验证进入 evaluator 的 bbox 已回到原图坐标。

## 4. 逐项审查

| 审查项 | 结论 | 证据/说明 |
|---|---|---|
| 任务卡和设计 commit 可定位 | 通过 | A1 包含 `2536730`，报告指向 v1.1/review-2 |
| 实验信号合法 | 通过 | `EXPERIMENT_COMPLETE / READY_FOR_REVIEW` |
| 两 seed 矩阵已报告 | 有条件通过 | 四组数值均有报告，但 metrics 未提交 |
| 官方 APvt 支持 P2 载体 | 待核验 | 报告均值 `+0.0103`，方向一致；缺原始轻量证据 |
| 精确 2–8 px AR/AP | 不通过 | 实现错误复用了官方 0–8 px / 1500 指标 |
| Gate E | 不通过 | 测试覆盖不足，汇总脚本硬编码为 True |
| Gate P | 不通过 | 轻量证据缺失，汇总脚本硬编码为 True |
| Gate B | 待复算 | APvt 分支可能通过；ARvt 分支当前无效 |
| Gate C / D0–D4 | 不通过 | D1–D3 关键文件不在远端 commit |
| 无 test 泄漏 | 暂未发现反证 | 评估入口强制 val；仍需 metrics/provenance 支撑 |
| seed 2 必要性 | 不触发 | 现有 APvt 报告值明确高于灰区；修订不要求补 seed 2 |

## 5. 最小修订任务（不重训）

实验 agent 继续使用 `codex/exp-prt-001-a1`，只需完成以下内容：

1. 在 `evaluate_full_prtiny()` 中真实调用 `evaluate_project_2_8px()`，分别保存官方 `(0,8]/1500` 与项目 `[2,8)/3000` 指标；对 2 px、略小于 8 px、等于 8 px 的实际 evaluator 行为增加测试；
2. 将坐标测试改成实际覆盖 resize/pad 逆映射或 prediction 导出到原图坐标的最小 fixture；
3. 将 Gate E/P 从硬编码改为 fail-closed 检查；缺 pytest、official source、metrics、full hash 或必要路径时不得标记通过；
4. 使用既有四组 prediction JSON 重新评估，禁止重训、禁止补 seed 2、禁止选择性替换 checkpoint；
5. 提交并 push 以下轻量证据：
   - `outputs/PRT-001-A1/tests/pytest.txt`；
   - `outputs/PRT-001-A1/evaluator/official_source.json`，记录 upstream commit、本地兼容性 patch 和实际文件 SHA-256；
   - `outputs/PRT-001-A1/{B0,B1}/seed{0,1}/metrics.json`；
   - `outputs/PRT-001-A1/summary.csv`；
   - `outputs/PRT-001-A1/gate_report.json`；
6. 更新结果报告：更正 ARvt/AP_2_8 数值，删除“关键瓶颈确实发生在早期浅层阶段”这类超出单一 P2 对照的因果表述，优先报告绝对增益而非低基数倍数。

实验 agent 完成后提交新的完整 commit SHA，并再次发送同一 TASK-ID 的 `READY_FOR_REVIEW`。不需要新任务卡，不需要额外设计审查。

## 6. Git 与越界边界

- A1 顶层 commit `c9bf1ef` 本身只包含 A1 相关的 7 个文件，可继续增量修订；
- 分支祖先包含未经本次 A1 审查放行的 PRT-002 v2 工作，该内容不进入本次证据判断，也不构成 PRT-002 有效性；
- 为避免拖慢当前修订，本次不要求重写历史或重建分支；但任何后续任务必须在治理内容正式进入 `main` 后从最新 `main` 建立干净分支；
- PRT-002-A1、PDD、SSR、NWD 和泛化实验继续锁定。

## 7. 当前能与不能接受的结论

当前可接受：实验 agent 已完成两 seed 训练并提交了可审查报告与实现；官方 APvt 报告值显示 P2 很可能是可用载体，值得快速修订而非重训。

当前不能接受：精确 2–8 px AR/AP 已测、Gate E/P/C 已通过、2–8 px 漏检已被证明下降、早期浅层阶段已被证明是关键瓶颈，以及 PRTiny/PDD/SSR 已有效。

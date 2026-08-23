# 阶段实验任务卡：PRT-001-A1（极小目标基线证据补全与可复现确认）

## Material Passport

- Origin Role: research design agent
- Created At: 2026-08-23
- Version: `v1.1 / amendment-1`
- Parent Task: `PRT-001`
- Supersedes: v1.0 的固定三种子和全量证据链要求；既有任务卡、失败记录与负结果继续保留
- Verification Status: `VERIFIED_BY_DESIGN_REVIEW`

## 1. 目标、状态与许可

- 投稿定位：面向 CCF-C 的 2026 年完整投稿，优先形成“简单可靠的方法 + 足够可信的系统实验”，不追求顶会级审计冗余。
- 本阶段问题：B1（FCOS-R50-FPN-P2–P6）相对 B0（P3–P7）的 seed-0 普通 AP 提升，是否也改善 AI-TOD-v2 的极小尺度指标，并能被一个独立确认 seed 复现？
- 可证伪假设：B1 相对 B0 的两组配对结果平均 `Delta APvt >= +0.005`，或平均 `Delta ARvt >= +0.010`；用于过 Gate 的主指标两组均为正，且平均 `Delta AP >= -0.002`。
- 设计状态：`APPROVED_WITH_CONDITIONS`
- 设计审查：`research/reviews/2026-08-23-PRT-001-A1-design-review-2.md`
- 决策依据：`docs/decisions/DR-004-ccf-c-paced-evidence-standard.md`
- 初始许可：评估器接通、最小正确性测试、seed-0 证据恢复；Gate E/P 后可运行 B0/B1 seed 1。
- 条件许可：仅触发本卡的歧义条件时运行 B0/B1 seed 2。
- `PRT-002-A1`、`PRT-003`、SSR、NWD 和泛化实验仍锁定；本任务通过里程碑审查后，只能解锁一个小预算 PRT-002-A1 诊断任务，不自动解锁完整方法矩阵。

## 2. 必须复用和保留的既有证据

| Run | 路径 | 当前状态 | 本任务处理 |
|---|---|---|---|
| B0 seed 0 | `outputs/PRT-001/B0/seed0/` | 普通 COCO AP 已测，主指标未测 | 优先复用 checkpoint，补主指标和关键 hash |
| B1 seed 0 | `outputs/PRT-001/B1/seed0/` | 普通 COCO AP 已测，主指标未测 | 优先复用 checkpoint，补主指标和关键 hash |
| PDD v1 seed 0 | `outputs/PRT-002/PDD/seed0/` | 零 AP 负测量 | 只读保留，不纳入本任务 Gate |

只有 checkpoint 缺失/损坏、配置或 seed 无法确认、或当前环境无法加载时，才允许在 `outputs/PRT-001-A1/rerun/` 重跑 seed 0。不得覆盖旧目录，不得因结果较差而重跑；工程失败必须在结果报告中保留。

## 3. 冻结科学变量

### 3.1 唯一模型变量

- B0：FCOS-R50-FPN P3–P7，stride `[8,16,32,64,128]`；
- B1：FCOS-R50-FPN P2–P6，stride `[4,8,16,32,64]`。

除 FPN 起始层、对应 stride 和 regress range 外，不允许有其他模型性差异。

### 3.2 数据、训练和后处理

- AI-TOD-v2 official train/val；test 不得参与训练、选择、调参或 Gate；
- FCOS-R50、同一 ImageNet 初始化；单尺度 `(800,800)`，保持长宽比并 pad 到 32；
- 12 epochs；单卡有效 batch 4；SGD lr 0.005、momentum 0.9、weight decay 1e-4；milestones `[8,11]`；warmup 250 iter；gradient clipping max norm 35；
- `frozen_stages=1` 对 B0/B1 相同；
- `nms_pre=3000`、`max_per_img=3000`、score threshold 0.05、NMS IoU 0.5；
- 核心 seeds：`0,1`，B0/B1 成对；`2` 仅按第 8 节条件触发；
- 禁止加入 PDD、SSR、NWD、额外增强、TTA 或多尺度测试。

环境适配若导致上述值无法完全复现，实验 agent 必须在运行前标记偏差；涉及有效 batch、lr、epochs、split、模型变量或指标定义时应发送 `EXPERIMENT_BLOCKED`，不得自行改口径。

## 4. 指标口径

### 4.1 主要指标

- `APvt_official_1500`：直接调用固定 commit 的 `jwwangchn/cocoapi-aitod`，使用其 verytiny 范围和 `maxDets=1500`；
- `ARvt_2_8_3000`：项目漏检主指标，IoU `0.50:0.05:0.95`、`2 <= sqrt(w*h) < 8`、`maxDets=3000`；
- `AP_2_8_3000`：同一项目尺度口径下的辅助精度指标；
- `AP`、`AP50`、`AP75`：总体约束和与旧结果对接。

官方 verytiny 与项目精确 2–8 px 指标必须使用不同字段名，统一保存为 `[0,1]` 标度。

### 4.2 诊断指标

- 建议输出 `[2,4)`、`[4,6)`、`[6,8)`、`[8,16)` 的 GT 数量、AP/AR 或 TP/FN；
- 若实现成本明显高于本阶段决策价值，可先提供 GT 数量与 AR/FN，AP 分箱延后到方法诊断阶段；必须在报告中标记未测项；
- FLOPs、参数量、latency/FPS 均不是本任务完成条件。未实测必须写 `NOT_TESTED`。

## 5. 实验 agent 的自主闭环与子 agent

父实验 agent 可调用子研究 agent 和子实验 agent，推荐按以下工作包并行：

- WP0：核对 seed-0 checkpoint/config/log 与数据 split，列出协议偏差；
- WP1：接通官方 evaluator，完成 prediction-sensitive、尺度边界和坐标映射测试；
- WP2：复用 seed 0 重新评估，或在证据不足时合法重跑；
- WP3：运行 B0/B1 seed 1，并在触发条件成立时补 seed 2；
- WP4：汇总、计算 Gate、父实验 agent 最终自查和交接。

无需强制建立独立的 `agent_ledger.jsonl` 或 `open_issues.json`。结果报告中用一节简要列出子 agent 分工、产出、遗留问题和父 agent 复核即可。子 agent 不得修改受保护研究文件或发出正式 `REVIEW_*`。

允许自主修复：框架/API、序列化、路径、数据加载、显存、worker、断点续训和日志问题；可用梯度累积保持有效 batch 4。所有影响结果解释的失败、重试或偏差必须保留，普通无影响调试无需逐条形成审计附件。

## 6. 主要交付内容

以下是发送 `EXPERIMENT_COMPLETE` 前的必要交付。

### D0：代码与固定版本

- 实验分支：`codex/exp-prt-001-a1`；
- 真实消费 predictions 的 evaluator/适配代码、测试和稳定命令入口；
- 记录 base commit、run commit、MMDetection/MMCV/MMEngine/PyTorch/CUDA/driver/GPU，以及官方 evaluator 的完整 commit SHA。

### D1：评估器正确性

- `outputs/PRT-001-A1/tests/pytest.txt`；
- `outputs/PRT-001-A1/evaluator/official_source.json`；
- 至少证明：predictions 改变会改变结果；2/8 px 边界正确；预测框映射回原图坐标正确；空预测与完美预测行为合理；
- 直接调用官方 evaluator 的指标无需重新实现逐标量 parity；如有 wrapper，使用一个冻结小 fixture 对共同指标做一致性检查；
- 在一个代表性 prediction JSON 上重复评估一次，要求输出完全一致。无需对每个 run 重复评估。

### D2：两组核心配对结果

目录：`outputs/PRT-001-A1/{B0,B1}/seed{0,1}/`。若触发第三 seed，则追加 `seed2/`。

每个被 Gate 接受的 run 必须可定位：

- 完整 config 或 config dump；
- 原始训练日志路径；
- best checkpoint 路径与 SHA-256；
- validation prediction JSON 路径与 SHA-256；
- `metrics.json`，含指标、seed、evaluator 版本和配置 hash。

无需为每张图像、每个普通日志或中间 checkpoint 建立全量 hash。数据证据只需 train/val annotation SHA-256、图像数量和文件名列表 hash；test 不得出现在开发命令中。

### D3：汇总与 Gate

- `outputs/PRT-001-A1/summary.csv`：所有已执行模型/seed 的指标；
- `outputs/PRT-001-A1/gate_report.json`：配对差、均值、触发条件、Gate 结论和关键证据路径；
- 报告全部已执行 seed，不隐藏失败或较差结果；两 seed 阶段不强制 sample std，若运行 seed 2 则补 mean/std。

### D4：结果报告与自我审查

- `experiment_handoffs/results/PRT-001-A1-evidence-completion.md`；
- 说明：实际命令、复用/重跑情况、协议偏差、失败与修复、子 agent 分工、关键 hash、未测项、Gate 计算和父 agent 自查；
- 完成信号只能是：

```text
[EXPERIMENT_COMPLETE][PRT-001-A1][READY_FOR_REVIEW] 实验执行完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。
```

若遇科学红线或致命失败，使用对应 `EXPERIMENT_BLOCKED/FAILED` 信号。

## 7. 稳定命令能力

实验 agent 可调整参数形式，但应提供以下能力并在报告中保存实际命令：

```text
python -m pytest -q tests/test_tiny_evaluator.py tests/test_fcos_pyramid.py tests/test_dataset_audit.py
python tools/evaluate.py <config> --checkpoint <checkpoint> --work-dir <output-dir>
python tools/train.py <config> --work-dir <run-dir> --seed <0|1|2>
python tools/summarize_prt001_a1.py --root outputs/PRT-001-A1 --output-dir outputs/PRT-001-A1
```

不强制为本阶段另写通用证据库存工具；只要 D0–D4 的关键字段可复核即可。

## 8. Gate 与自适应补种子规则

### Gate E：评估器可信

- evaluator 实际消费 predictions；
- 官方实现的 commit 和安装来源已固定；
- 官方 APvt 与项目 2–8 px 指标字段、范围、maxDets 不混写；
- prediction-sensitive、2/8 px 边界、原图坐标、空/完美预测测试通过；
- 代表性 prediction JSON 重评完全一致。

### Gate P：最小可追溯

- seed-0 的 checkpoint、config、日志和 seed 对应关系可证明；
- train/val annotation hash 和图像清单可定位；
- 不存在 test 调用，旧结果未被覆盖；
- 官方 evaluator、best checkpoint、prediction、config 和 metrics 有版本或 SHA-256。

Gate E/P 通过后可运行 seed 1。

### Gate B：两 seed P2 可行性

两组配对 seed 0/1 同时满足以下条件即通过：

1. 平均 `Delta APvt_official_1500 >= +0.005`，或平均 `Delta ARvt_2_8_3000 >= +0.010`；
2. 用于通过的主指标在 seed 0 和 seed 1 中均为正；
3. 平均 `Delta AP >= -0.002`；
4. 两组 run 的关键证据完整，所有失败和偏差已披露。

出现以下任一情况才运行 seed 2：

- seed 0 与 seed 1 的 APvt 和 ARvt 主要结论符号冲突；
- 两 seed 均值处于灰区：`0 < Delta APvt < +0.007` 或 `0 < Delta ARvt < +0.012`，且是否过 Gate 依赖该指标；
- 任一核心 run 存在可能影响结论但已修复的工程异常或协议偏差；
- 研究设计 agent 在里程碑审查前发现明确的结果歧义。

补 seed 2 后，Gate 改为：均值满足同一阈值、用于通过的主指标至少 2/3 为正、平均 `Delta AP >= -0.002`。若两 seed 明确不通过且不在灰区，不为“碰运气”补第三 seed。

### Gate C：交付完整

- D0–D4 存在并可复核；
- 事实、解释和未测项分开；
- 未把 P2 写成 PRTiny 贡献，未越界声称 PDD/SSR/泛化/效率有效。

## 9. 停止条件与后续

停止新增高成本运行并交接当前证据，当：

- 官方 evaluator 无法接通或结果明显不受 predictions 影响；
- 数据 split/hash 冲突或发现 test 泄漏；
- seed-0 关键证据无法复用且无法在预算内合法重建；
- B1 明确未通过两 seed/条件三 seed Gate；
- 必须改变科学变量或加入额外模块才能过 Gate；
- 出现选择性 seed、覆盖负结果或指标口径漂移。

Gate B/C 通过后，实验 agent 仍只可发送 `READY_FOR_REVIEW`。研究设计里程碑审查通过后，可建立小预算 `PRT-002-A1` 诊断任务；不自动授权完整 PDD、SSR 或泛化实验。

## 10. 正式授权

- 研究设计 agent：`[DESIGN_APPROVED_WITH_CONDITIONS][PRT-001-A1]`
- 法定设计状态：`APPROVED_WITH_CONDITIONS`
- 允许启动：WP0/WP1/WP2；Gate E/P 后启动 seed 1；满足第 8 节条件时启动 seed 2；随后完成 WP4。
- 未经新审查禁止：PDD v2、SSR、NWD、额外增强、test 调参和跨阶段放行。

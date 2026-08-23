# 阶段实验任务卡：PRT-001-A1（极小目标基线证据补全与可复现确认）

## Material Passport

- Origin Role: research design agent
- Created At: 2026-08-23
- Version: `v1.0 / amendment-1`
- Parent Task: `PRT-001`
- Supersedes: 仅替代 PRT-001 中未完成的评估、证据与三种子验收口径；不删除或覆盖既有任务卡与负面记录
- Verification Status: `VERIFIED_BY_DESIGN_REVIEW`

## 1. 长期目标与阶段定位

- 中长期研究目标：在 2026 年完成一篇面向 CCF-C 竞争力的极小目标检测模型改进论文投稿，以简单可靠的方法、系统对照和跨数据/检测器证据为核心；不承诺录用。
- 本阶段核心科学问题：现有 B1（FCOS-R50-FPN-P2–P6）相对 B0（P3–P7）的 seed-0 普通 COCO AP 提升，能否在 AI-TOD-v2 官方极小尺度指标和三种子配对实验中被复现，并真正对应 2–8 px 漏检下降？
- 可证伪假设：在统一冻结协议下，B1 相对 B0 的三种子平均 `APvt` 至少提高 `0.005`（即按百分制报告时 `+0.5 AP point`），或平均 `ARvt` 至少提高 `0.010`（`+1.0 AR point`）；用于过 Gate 的主指标至少 2/3 个配对 seed 为正，且平均总体 AP 下降不超过 `0.002`（`-0.2 AP point`）。
- 设计状态：`APPROVED_WITH_CONDITIONS`
- 审查人：研究设计 agent
- 审查日期：2026-08-23
- 设计审查记录：`research/reviews/2026-08-23-PRT-001-A1-design-review-1.md`
- 批准条件：先通过 Gate E（评估器可信）和 Gate P（既有证据可追溯），随后实验 agent 可在本任务内自主进入正式补种子矩阵，无需为非科学性工程修复逐次申请审查。
- 当前阶段许可：`IMPLEMENTATION_AND_DEBUG`；Gate E/P 通过后自动进入 `FORMAL_RUN_MATRIX`。
- 下一阶段：`PRT-002-A1`、`PRT-003`、SSR 与 NWD 全部 `LOCKED`。

## 2. 既有证据的处理原则

### 2.1 必须保留的高成本证据

| 既有 Run | 路径 | 当前可接受状态 | 处理方式 |
|---|---|---|---|
| B0 seed 0 | `outputs/PRT-001/B0/seed0/` | 普通 COCO AP 已测，主指标未测 | 不覆盖；定位 checkpoint 后补 hash、prediction 与完整评估 |
| B1 seed 0 | `outputs/PRT-001/B1/seed0/` | 普通 COCO AP 已测，主指标未测 | 不覆盖；定位 checkpoint 后补 hash、prediction 与完整评估 |
| PDD v1 seed 0 | `outputs/PRT-002/PDD/seed0/` | 负测量，非本任务研究变量 | 只读归档，不修改、不重跑、不纳入本任务 Gate |

### 2.2 复用与重跑规则

1. 若 B0/B1 seed-0 checkpoint、完整配置和日志可定位且 SHA-256 可生成，优先复用并重新评估；
2. 只有 checkpoint 缺失、损坏、配置无法确认、seed 无法确认或 evaluator 无法加载时，才允许在新目录 `outputs/PRT-001-A1/rerun/` 重跑对应 seed；
3. 任何重跑不得覆盖旧目录，必须在 `failure_registry.jsonl` 和结果报告中说明原因；
4. 不得因为某个 seed 较差而重跑或删除；仅允许针对可复现的工程失败重跑，且保留全部失败证据。

## 3. 实验变量与科学对照

### 3.1 独立变量

- `B0`：FCOS-R50-FPN P3–P7，stride `[8, 16, 32, 64, 128]`；
- `B1`：FCOS-R50-FPN P2–P6，stride `[4, 8, 16, 32, 64]`。

除金字塔起始层、对应 stride 和 regress range 外，不允许存在其他模型性差异。

### 3.2 主要因变量

- `APvt`：严格调用或逐项复现 `jwwangchn/cocoapi-aitod` 的官方 `verytiny` 口径；官方默认 `maxDets=[1,100,1500]`，因此 `APvt` 使用 `maxDets=1500`；
- `ARvt`：本项目预注册的核心漏检指标，IoU `0.50:0.05:0.95`、有效尺寸 `2 <= s < 8`、`maxDets=3000`；
- 同时输出 `ARvt_official_1500`（官方 `verytiny` 范围与默认 maxDets）和 `AP_2_8`，防止把官方 `(0,8]` 与项目精确 `2–8 px` 口径混写；
- 以上指标统一保存为 `[0, 1]` 标度；报告中可同时显示乘 100 后的 point，但 Gate 以 `[0,1]` 绝对差判定。

### 3.3 次要与诊断指标

- AP、AP50、AP75、APt、APs、APm；
- `[2,4)`、`[4,6)`、`[6,8)`、`[8,16)` 的 AP、AR、GT 数量、匹配 TP、FN 与漏检率；
- 参数量、FLOPs、各 FPN 层 shape；
- latency/FPS 本任务不要求；若未严格实测必须填 `NOT_TESTED`。

### 3.4 固定控制变量

- 数据：AI-TOD-v2 官方 train/val；test 不参与训练、选择、调参或 Gate；
- 检测器与 backbone：FCOS-R50；
- 输入：单尺度 `(800, 800)`，保持长宽比并 pad 到 32；
- 初始化：同一 ResNet-50 ImageNet 权重及 SHA-256；
- 训练预算：12 epochs；
- 实际协议修订并冻结为：单卡有效 batch `4`、SGD `lr=0.005`、momentum `0.9`、weight decay `1e-4`、milestones `[8,11]`、warmup 250 iter、gradient clipping max norm `35`；
- seeds：`0, 1, 2`，B0/B1 成对使用相同 seed；
- 后处理：`nms_pre=3000`、`max_per_img=3000`、score threshold `0.05`、NMS IoU `0.5`；官方 APvt parity 使用官方 evaluator 的 `maxDets=1500`，项目 ARvt 使用预注册的 `maxDets=3000`，两套结果必须使用不同字段名保存；
- 框架：MMDetection `v3.3.0`，必须记录解析后的完整 commit SHA、MMCV/MMEngine/PyTorch/CUDA/driver/GPU；
- `frozen_stages=1` 对 B0/B1 同时保持一致；
- 不得加入 PDD、SSR、NWD、额外增强、TTA 或 multi-scale testing。

### 3.5 必需科学对照

- B0 与 B1 的三种子配对矩阵；
- 同一 checkpoint 重复评估两次；
- 官方 AI-TOD evaluator 与本项目 evaluator 的 parity；
- 空预测、完美预测、重复框、边界尺度框和映射回原图坐标的冻结 fixture。

## 4. 工作包与子 agent 协作授权

实验执行 agent 可以调用自己的子研究 agent 和子实验 agent，并在阶段内持续迭代，直至所有交付项完成或触发科学红线。建议分工如下：

### WP0：证据与协议审计（子研究 agent，可并行）

- 核对任务卡、设计审查、实际配置与运行日志；
- 建立既有 seed-0 证据清单和协议偏差表；
- 检查数据 split、类别、图像/标注 hash、预训练权重与框架版本；
- 只提交审计发现，不得发出 `REVIEW_*` 或修改研究任务卡/审查文件。

### WP1：评估器实现与验证（子实验 agent，可并行）

- 将真实 predictions 接入 evaluator；
- 对齐 AI-TOD 官方 APvt/APt/APs/APm 与 AR 口径；
- 实现诊断分箱 AP/AR、GT/TP/FN；
- 完成合成 fixture、官方 parity、坐标映射、重复评估和 schema 测试。

### WP2：既有 seed-0 证据恢复（子实验 agent）

- 定位 B0/B1 checkpoint；
- 生成 checkpoint/config/log/prediction/metrics SHA-256；
- 用 Gate E 通过后的 evaluator 对同一 checkpoint 连续评估两次；
- 仅在复用不可行时按规则重跑。

### WP3：B0/B1 补种子矩阵（可拆给独立运行/监控子实验 agent）

- Gate E/P 通过后运行 seed 1、2；
- 每个模型/seed 独立目录、独立 run manifest；
- 监控 NaN/Inf、OOM、日志停滞、checkpoint 写入与磁盘空间；
- 工程失败可自主修复和重跑，但必须保留失败 run。

### WP4：证据汇总与独立自查（子研究 agent + 父实验 agent）

- 子研究 agent 按任务卡逐项检查遗漏、选择性报告和 Gate 计算；
- 父实验 agent 复核所有子 agent 产物，运行最终验证命令并提交唯一结果报告；
- 子研究 agent 的意见属于实验侧自查，不能替代研究设计 agent 的正式结果审查。

### 子 agent 协作记录要求

- `outputs/PRT-001-A1/coordination/agent_ledger.jsonl`：记录 agent 角色、子任务、输入 commit、产出路径、状态与时间；
- `outputs/PRT-001-A1/coordination/open_issues.json`：记录未解决问题、责任 agent、科学/工程分类和处理状态；
- 子 agent 不得修改 `docs/**`、`research/**`、`governance/**` 或 `experiment_handoffs/tasks/**`；
- 父实验 agent 对集成正确性、最终自查和法定实验信号负责。

## 5. 允许工程自主调优范围

### 5.1 可自主闭环

- Python/MMDetection API 适配、序列化、路径、编码和数据加载 Bug；
- evaluator 的正确性修复，但不得改变冻结指标定义；
- OOM 处理：优先减少 `num_workers`、启用梯度累积以保持有效 batch 4；实际 micro-batch 和累积步数必须记录；
- warmup、gradient clipping 的实现错误修复，但数值必须保持本卡冻结值；
- 日志、监控、断点续训、临时网络失败和磁盘空间问题；
- 因工程崩溃重跑，前提是旧 run 保留并登记。

### 5.2 必须立即阻断并回报

- 必须更改数据 split、主指标、尺度定义、模型核心拓扑、训练 epochs、有效 batch、主学习率或 seed 集合才能继续；
- 官方 evaluator 与本项目 evaluator 无法解释地不一致；
- checkpoint 与配置对应关系无法证明；
- test split 已被用于开发决策；
- B0/B1 必须使用不同训练配方才能运行；
- 需要引入 PDD/SSR/NWD/额外增强来“修复”基线。

## 6. 主要交付内容与文件契约

以下为任务完成的必要交付，缺一项不得发送 `EXPERIMENT_COMPLETE`。

### D0：代码、分支与可追溯提交

- 实验分支：`codex/exp-prt-001-a1`；
- 分支必须包含本任务卡与设计审查对应的固定 commit；
- `outputs/PRT-001-A1/provenance/git_state.json`：base commit、run commit、dirty status、remote URL；
- 代码提交只包含代码、配置、测试、轻量 manifest/metrics/summary 和结果报告；禁止提交 checkpoint、大日志、数据集或权重。

### D1：环境、数据与输入证据

- `outputs/PRT-001-A1/provenance/environment.json`
- `outputs/PRT-001-A1/provenance/data_manifest.json`
- `outputs/PRT-001-A1/provenance/pretrained_weights.json`
- `outputs/PRT-001-A1/provenance/evidence_inventory.json`
- 必须包含：路径、大小、SHA-256、生成命令、生成时间和验证状态；
- 数据 manifest 至少覆盖 train/val 的 annotation 与图像文件列表 hash；test 只登记来源/hash，不得进入开发命令。

### D2：评估器与测试

- 真实评估器代码及稳定 CLI；
- `outputs/PRT-001-A1/evaluator/metrics_schema_v1.json`
- `outputs/PRT-001-A1/evaluator/official_parity.json`
- `outputs/PRT-001-A1/tests/pytest.txt`
- 官方参考实现固定为 `https://github.com/jwwangchn/cocoapi-aitod`；必须记录实际使用的完整 commit SHA、安装来源和本地文件 SHA-256，不得只记录浮动分支名；
- 必做测试：
  1. `preds` 变化会改变 AP/AR，禁止只统计 GT；
  2. 2、4、6、8、16 px 边界行为；
  3. `sqrt(w*h)` 和映射回原图坐标；
  4. 空预测、完美预测、重复预测、ignore/crowd/无效框；
  5. 官方 evaluator parity：使用官方 `maxDets=1500` 的共同指标在冻结 fixture 上每个标量差异 `<=1e-6`；项目 `ARvt@3000` 另做解析测试，不伪装成官方默认值；
  6. 同一 prediction JSON 重评两次完全一致。

### D3：每个 run 的原始证据

目录：`outputs/PRT-001-A1/{B0,B1}/seed{0,1,2}/`

每个目录必须包含或索引：

- `run_manifest.json`：命令、seed、环境、开始/结束时间、状态、所有输入/输出 hash；
- `config.py` 与 SHA-256；
- 原始训练日志路径与 SHA-256；
- best/last checkpoint 路径与 SHA-256；
- validation prediction JSON 路径与 SHA-256；
- `metrics.json`：主、次、诊断指标及 evaluator 版本；
- `repeat_eval.json`：两次评估差异；
- `failures.jsonl`：本 run 的失败、重试和工程修复记录。

大文件保留在正式算力环境或约定对象存储；Git 只提交轻量索引和 hash。

### D4：汇总与 Gate 计算

- `outputs/PRT-001-A1/summary.csv`：每个模型/seed 的完整指标；
- `outputs/PRT-001-A1/paired_deltas.csv`：每 seed 的 B1−B0；
- `outputs/PRT-001-A1/gate_report.json`：每项 Gate 的公式、输入值、结论和证据路径；
- `outputs/PRT-001-A1/failure_registry.jsonl`：全部失败 run 和处理；
- 报告 mean、sample std、min/max 和 3 个 paired deltas；不得只报告最好 seed。

### D5：实验交接与自我审查

- 结果报告：`experiment_handoffs/results/PRT-001-A1-evidence-completion.md`
- 报告必须使用 `experiment_handoffs/RESULT_TEMPLATE.md`，逐项勾选 Self-Review；
- 必须列出所有子 agent、任务、产物、未解决问题和父 agent 的复核命令；
- 唯一允许的完成信号：

```text
[EXPERIMENT_COMPLETE][PRT-001-A1][READY_FOR_REVIEW] 实验执行完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。
```

若触发科学红线或致命失败，改用相应 `EXPERIMENT_BLOCKED/FAILED` 信号。

## 7. 稳定命令入口

实验 agent 可在不改变语义的前提下实现参数细节，但必须提供并记录以下能力：

```text
python -m pytest -q tests/test_tiny_evaluator.py tests/test_fcos_pyramid.py tests/test_dataset_audit.py
python tools/evaluate.py <config> --checkpoint <checkpoint> --work-dir <output-dir>
python tools/train.py <config> --work-dir <run-dir> --seed <0|1|2>
python tools/build_evidence_inventory.py --task PRT-001-A1 --output-dir outputs/PRT-001-A1/provenance
python tools/summarize_prt001_a1.py --root outputs/PRT-001-A1 --output-dir outputs/PRT-001-A1
```

最终报告中必须保存实际执行的完整命令，不得只复制上述示意入口。

## 8. 阶段 Gate

### Gate E：评估器可信

全部满足后才可使用现有 checkpoint 或启动补种子：

- evaluator 实际消费 predictions；
- 官方 `cocoapi-aitod` commit 已固定；官方 `maxDets=1500` 指标 parity 测试通过，差异 `<=1e-6`；
- `APvt`、`ARvt_official_1500`、`AP_2_8` 与项目 `ARvt@3000` 字段、范围和 maxDets 不混写；
- 诊断分箱边界、坐标映射、ignore/crowd、空/完美/重复预测测试通过；
- metrics JSON schema 固定；
- 同一 prediction JSON 重评两次完全一致。

### Gate P：证据可追溯

- 环境、数据、权重、配置、日志、checkpoint、prediction 与 metrics 均有路径和 SHA-256；
- 既有 seed-0 checkpoint 与日志匹配；
- seed=0 和 deterministic 设置可从 config dump/log 定位；
- 不存在未解释的 test 调用；
- 旧证据不被覆盖。

Gate E/P 均通过后，父实验 agent 可记录自查结果并在本任务内自动进入 `FORMAL_RUN_MATRIX`。

### Gate B0：seed-0 筛查

- B0/B1 seed 0 的 APvt、ARvt、AP 和诊断分箱均可复算；
- 同 checkpoint 重评两次各标量差异 `<=1e-6`；
- 若 B1 的 APvt 与 ARvt 均不高于 B0，或总体 AP 下降超过 `0.005`（0.5 point），停止 seed 1、2 并提交结果审查。

### Gate B1：三种子 P2 可行性

满足以下全部约束才算通过：

1. 平均 `Delta APvt >= +0.005`，或平均 `Delta ARvt >= +0.010`；
2. 用于通过的主指标至少 2/3 个 paired seeds 为正；
3. 平均 `Delta AP >= -0.002`；
4. 三个 seed 均完整报告，不隐藏失败；
5. 每个 run 的 evidence contract 完整。

### Gate C：交付完整性

- D0–D5 全部存在且 schema/路径检查通过；
- 结果报告中事实、解释与未测项分开；
- 没有把 P2 写成 PRTiny 贡献；
- 没有 PDD、SSR、NWD、泛化或效率越界宣称。

## 9. 停止与失败条件

- 官方 evaluator parity 无法达到并无法解释；
- 数据 split/hash 与既有记录冲突；
- seed-0 关键证据缺失且无法在预算内合法重建；
- B1 未通过 Gate B0 或 Gate B1；
- 为通过 Gate 必须改变科学变量或加入额外模块；
- 出现 test 泄漏、选择性 seed、覆盖负结果或指标口径漂移。

触发后停止新增高成本运行，保留证据并交接；不得通过进入 PDD/SSR 绕过失败。

## 10. 最终授权

- 研究设计 agent 签名：`[DESIGN_APPROVED_WITH_CONDITIONS][PRT-001-A1]`
- 法定设计状态：`APPROVED_WITH_CONDITIONS`
- 允许实验 agent 启动：`CONDITIONAL`
- 初始允许：WP0/WP1/WP2 的实现、审计、评估器验证和既有证据恢复；
- Gate E/P 通过后自动允许：WP3 的 B0/B1 seed 1、2 正式运行及 WP4 汇总；
- 未经新审查仍然禁止：PDD v2、SSR、NWD、额外增强、test 调参、下一阶段解锁。

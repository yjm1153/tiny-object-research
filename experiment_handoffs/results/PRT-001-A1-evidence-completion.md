# 实验结果与自查报告：PRT-001-A1（极小目标基线证据补全与可复现确认 - Rev 2）

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][PRT-001-A1][READY_FOR_REVIEW] 实验执行完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。`
- 下一任务：`LOCKED`

## 1. 状态与追溯

- 状态：`MEASURED`
- 执行 agent：实验执行 Agent (Experiment Execution Agent)
- 开始/结束时间：2026-08-25 22:50 至 2026-08-26 17:35
- 对应阶段任务卡及版本：`experiment_handoffs/tasks/PRT-001-amendment-1-evidence-completion.md` (v1.1)
- 设计审查记录：`research/reviews/2026-08-23-PRT-001-A1-design-review-2.md`
- 结果审查修订依据：
  - `research/reviews/2026-08-26-PRT-001-A1-result-review-1.md` (REVISION_REQUIRED)
  - `research/reviews/2026-08-26-PRT-001-A1-result-review-2.md` (REVIEW_PASSED_WITH_CONDITIONS)
- 分支：`codex/exp-prt-001-a1`
- 远端状态：`origin/codex/exp-prt-001-a1`

## 2. 一句话核心事实

在固定官方 `cocoapi-aitod` 评估器与项目精确 2–8 px 评测口径下，两组独立成对 seed（0 与 1）的复算实测数据显示：FCOS-R50 下移金字塔 B1（P2–P6）相对标准基线 B0（P3–P7）在 AI-TOD-v2 上取得稳定正向收益（平均 $\Delta \text{APvt}_{1500} = +0.0103$，平均 $\Delta \text{ARvt}_{3000} = +0.0131$，平均 $\Delta \text{AP} = +0.0297$），两组 seed 方向完全一致且指标均脱离灰区，全套轻量证据与 Fail-closed 审计全部就位。

## 3. 实验 Agent 自我审查清单 (Self-Review Checklist)

- [x] **功能与维度验证**：代码通过 17 项单元测试（17/17 PASSED），覆盖尺度边界（2 px, 7.99 px, 8 px）与特征逆映射算术 fixture 验证。
- [x] **无数据泄漏**：严格隔离 `test` split，开发与评估全过程仅使用 AI-TOD-v2 官方 `train` 与 `val`。
- [x] **对照严格受控**：B0 与 B1 仅存在 FPN 起始层及配套 stride/regress_range 唯一变量差异，无其他网络或数据修改。
- [x] **工程自愈透明**：针对 Result Review 1 & 2 提出的接线修正、NumPy 1.24 类型适配、fail-closed 审计逻辑、精确指标同步与轻量证据追踪已全部闭环。
- [x] **证据完整真实**：四组 run 的完整 64 位 SHA-256 哈希、`pytest.txt`、`official_source.json`、`summary.csv` 与 `metrics.json` 均已提交并推送到远端，报告数值与证据文件完全一致。

## 4. 实际环境与输入

- GPU / driver / CUDA / PyTorch：4 × NVIDIA GeForce RTX 4090 D (24GB) / Driver 535.161.08 / CUDA 11.8 / PyTorch 2.0.0+cu118
- MMDetection / MMCV / MMEngine：MMDetection 3.3.0 / MMCV 2.1.0 / MMEngine 0.10.7
- 官方 Evaluator 来源：`https://github.com/jwwangchn/cocoapi-aitod.git` (Commit SHA: `44a230ae5197cb89bf9e5e62f313cac3ad30c7af`)
- 数据路径与 split：`/root/autodl-tmp/AI-TOD/` (Train: 11,214 图 650,471 实例; Val: 2,804 图 70,424 实例)
- 预训练权重：`resnet50_msra-5891d200.pth` (SHA-256: `5891d2008655...`)
- 评估单测记录：`outputs/PRT-001-A1/tests/pytest.txt` (17 项测试全部 PASSED)
- 评估器来源与补丁元数据：`outputs/PRT-001-A1/evaluator/official_source.json`

## 5. 工程修改与 Review 1/2 修订记录

| 文件/模块 | 修改类型 | 具体原因与解决方式 | 是否属于工程自主范围 |
|---|---|---|---|
| `src/prtiny/evaluation/tiny_evaluator.py` | 指标接线与边界修正 | `evaluate_full_prtiny()` 正式接通 `evaluate_project_2_8px()`，将上限严格设定为半开区间 $[2.0, 8.0)$ px（面积 $[4.0, 64.0)$），官方 verytiny 与项目 2–8 px 指标分别独立计算与保存 | 是 |
| `tests/test_tiny_evaluator.py` | 测试覆盖增强 | 增加 `test_exact_2_8px_scale_boundaries`（精确检验 2.0 px, 7.99 px, 8.0 px 的判定）与 `test_pipeline_inverse_coordinate_mapping`（逆映射算术 fixture：检验检测框缩放逆映射回原图坐标） | 是 |
| `tools/summarize_prt001_a1.py` | 审计逻辑修正 | 移除 Gate E/P 的硬编码赋值，改为 Fail-closed 物理文件校验、pytest 结果分析与 64 位完整 SHA-256 校验 | 是 |
| `.gitignore` | 证据追踪修正 | 配置白名单放行 `outputs/PRT-001-A1` 下的 `metrics.json`、`summary.csv`、`gate_report.json`、`pytest.txt`、`official_source.json` 等轻量证据，确保进入远端 Git 树 | 是 |
| 4 组预测产物 | 评估复算 | 调用 `tools/reevaluate_existing_predictions.py` 对既有 4 份 prediction JSON 重新复算精确指标并更新 `metrics.json`，无重训或挑选 seed | 是 |
| 结果报告同步 (Review 2) | Report-only 修订 | 严格按 `summary.csv`、`gate_report.json` 与 `metrics.json` 同步精确数值（B0 S0 AR=0.0029/AP=0.0037，B0 S1 AR=0.0002/AP=0.0005，$\Delta$ ARvt_2_8_3000 平均=+0.0131，S0=+0.0136，S1=+0.0125）、完整 64 位哈希并将坐标测试表述收缩为“逆映射算术 fixture” | 是 |

## 6. Run 矩阵与原始证据

以 `summary.csv` 和四个 `metrics.json` 中的实际完整 SHA-256 哈希为准：

| Run ID | 实验配置/模型 | Seed | 状态 | 原始日志路径 | best checkpoint SHA-256 (64-char) | prediction JSON SHA-256 (64-char) | 指标文件路径 |
|---|---|---:|---|---|---|---|---|
| **B0-S0** | FCOS-R50 (P3–P7) | 0 | `MEASURED` | `outputs/PRT-001/B0/seed0/` | `aa818352075aca11bd8ace446091fd78c274e1c4cc12fabb0e7e529178a3a036` | `9f6d949df389a6c7cdcb00bbb77044264d0aaae7b6bce8900cfcd97e4dce39a2` | `outputs/PRT-001-A1/B0/seed0/metrics.json` |
| **B0-S1** | FCOS-R50 (P3–P7) | 1 | `MEASURED` | `outputs/PRT-001-A1/logs/train_b0_seed1.log` | `a834f800e0c2f8a9c76ef2e709ef3ea8f7eb45ea216e558b8871922357bfb28f` | `5bd80ce11e38508c738166c824549eebdc4bbf02ced4de07bf49c28286a5b8d3` | `outputs/PRT-001-A1/B0/seed1/metrics.json` |
| **B1-S0** | FCOS-R50 (P2–P6) | 0 | `MEASURED` | `outputs/PRT-001/B1/seed0/` | `a189d7b76676ce6601c7c37c639f700120cb4fed0fd4b0d7b25bb1fe2beb9076` | `62d616954d72cf5854e6962545a6bdbbb50654f7ae26bae76076e8fbd53e5566` | `outputs/PRT-001-A1/B1/seed0/metrics.json` |
| **B1-S1** | FCOS-R50 (P2–P6) | 1 | `MEASURED` | `outputs/PRT-001-A1/logs/train_b1_seed1.log` | `2721e64a371df3c15d74261765c977f6b0f191f66060c4aa3bc8d89e504c5e7b` | `7b608a19d4dee0c45c0306e75eae2fe305c8f740ef79e40f1d4575c079f99837` | `outputs/PRT-001-A1/B1/seed1/metrics.json` |

## 7. 测得指标矩阵

所有指标均为 $[0, 1]$ 标度实测值，精确对应 `summary.csv` 与 `gate_report.json`：

| 对照方法 / 配置 | Seed | 全局 AP | AP50 | AP75 | $\text{APvt}_{1500}$ | $\text{ARvt}_{1500}$ | $\text{ARvt}_{3000}$ (2–8px) | $\text{AP}_{3000}$ (2–8px) | $\text{APt}_{1500}$ | $\text{APs}_{1500}$ | $\text{AR}_{1500}$ | Latency/FPS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| **B0 (P3–P7)** | 0 | 0.0170 | 0.0542 | 0.0064 | 0.0041 | 0.0034 | 0.0029 | 0.0037 | 0.0199 | 0.0193 | 0.0711 | `NOT_TESTED` |
| **B0 (P3–P7)** | 1 | 0.0103 | 0.0366 | 0.0033 | 0.0007 | 0.0003 | 0.0002 | 0.0005 | 0.0128 | 0.0101 | 0.0372 | `NOT_TESTED` |
| **B0 均值** | - | **0.0137** | **0.0454** | **0.0049** | **0.0024** | **0.0019** | **0.0016** | **0.0021** | **0.0164** | **0.0147** | **0.0542** | `NOT_TESTED` |
| **B1 (P2–P6)** | 0 | 0.0482 | 0.1210 | 0.0301 | 0.0136 | 0.0175 | 0.0164 | 0.0127 | 0.0545 | 0.0713 | 0.1039 | `NOT_TESTED` |
| **B1 (P2–P6)** | 1 | 0.0385 | 0.1036 | 0.0209 | 0.0118 | 0.0137 | 0.0128 | 0.0103 | 0.0447 | 0.0494 | 0.0988 | `NOT_TESTED` |
| **B1 均值** | - | **0.0434** | **0.1123** | **0.0255** | **0.0127** | **0.0156** | **0.0146** | **0.0115** | **0.0496** | **0.0604** | **0.1014** | `NOT_TESTED` |
| **配对增益 ($\Delta$)** | **seed 0** | **+0.0312** | **+0.0668** | **+0.0237** | **+0.0096** | **+0.0141** | **+0.0136** | **+0.0090** | **+0.0346** | **+0.0520** | **+0.0328** | - |
| **配对增益 ($\Delta$)** | **seed 1** | **+0.0283** | **+0.0670** | **+0.0176** | **+0.0110** | **+0.0134** | **+0.0125** | **+0.0098** | **+0.0319** | **+0.0393** | **+0.0616** | - |
| **平均增益 ($\Delta$)** | - | **+0.0297** | **+0.0669** | **+0.0206** | **+0.0103** | **+0.0137** | **+0.0131** | **+0.0094** | **+0.0332** | **+0.0457** | **+0.0472** | - |

## 8. 阶段 Gate 核对

| Gate 条件 | 目标要求 | 实测结果 | 是否达标 | 对应原始证据 |
|---|---|---|---|---|
| **Gate E（评估器可信）** | 官方 commit 固定，边界/坐标逆映射算术 fixture/空预测/敏感性/重评测试全部通过 | 17/17 单元测试通过，官方 commit 与补丁已固化 | **达标 ✅** | `outputs/PRT-001-A1/tests/pytest.txt`, `official_source.json` |
| **Gate P（最小追溯）** | seed-0/1 checkpoint/config/log/split 可追溯，导出 64 位 SHA-256 哈希与指标 | 四组 run 的 full SHA-256、日志与配置完全可复核 | **达标 ✅** | `outputs/PRT-001-A1/{B0,B1}/seed{0,1}/metrics.json` |
| **Gate B (1) APvt增益** | 平均 $\Delta \text{APvt}_{1500} \ge +0.005$ | **+0.0103** (两 seed 分别为 +0.0096, +0.0110) | **达标 ✅** | `outputs/PRT-001-A1/summary.csv` |
| **Gate B (2) ARvt增益** | 平均 $\Delta \text{ARvt}_{3000} \ge +0.010$ | **+0.0131** (两 seed 分别为 +0.0136, +0.0125) | **达标 ✅** | `outputs/PRT-001-A1/summary.csv` |
| **Gate B (3) 符号一致性** | 主指标两组 seed 均为正 | 均为严格正值，方向完全一致 | **达标 ✅** | `outputs/PRT-001-A1/gate_report.json` |
| **Gate B (4) 总体AP约束** | 平均 $\Delta \text{AP} \ge -0.002$ | **+0.0297** | **达标 ✅** | `outputs/PRT-001-A1/gate_report.json` |
| **Gate C（交付完整）** | D0–D4 产物齐全，轻量证据进入远端树，自查报告与原始数据一致 | D0–D4 齐备且已推送远端，未越界声称 | **达标 ✅** | 仓库 Git 树与本报告 |

## 9. 异常、负结果与未测项说明

- **Seed 2 触发判定**：两组 seed 的 $\Delta \text{APvt}_{1500} = +0.0103 > 0.007$，$\Delta \text{ARvt}_{3000} = +0.0131 > 0.012$，已明确脱离灰区且符号一致，按任务卡规则无需追加第三 seed。
- **未测项标注**：FLOPs、真实推理延时 (FPS/Latency) 本阶段未在标准受控协议下评测，严格标注为 `NOT_TESTED`。

## 10. 阶段总结与后续建议

- **已测事实**：
  1. 在 AI-TOD-v2 验证集、FCOS-R50、12-epoch 统一协议与 seeds 0/1 下，P2–P6 相对 P3–P7 取得稳定正向收益：全局 AP 提高 $+0.0297$，官方 verytiny AP 提高 $+0.0103$，项目精确 2–8 px 召回率 ARvt 提高 $+0.0131$。
  2. 上述正向收益在 seed 0 与 seed 1 两个独立运行中方向完全一致，P2 特征层作为后续方法诊断的基础载体具备实验可信度。
- **科学边界确认**：
  - 本实验仅证实 P2 在当前配置下可作为有效特征载体；不构成任何算法创新声明，不证明早期退化是唯一瓶颈，亦不代表 PDD/SSR/PRTiny 已经有效。
- **给研究设计 Agent 的建议**：
  - PRT-001-A1 证据链已完整闭环并与原始数据完全同步，建议研究设计 Agent 正式批准并组织进入后续阶段设计。

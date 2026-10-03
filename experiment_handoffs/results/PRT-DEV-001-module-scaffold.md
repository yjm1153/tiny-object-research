# 实验结果与自查报告：PRT-DEV-001

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][PRT-DEV-001][READY_FOR_REVIEW]`
- 实验执行完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。
- 下一任务：`LOCKED`。仅提交模块原型，不申请以本次 smoke 替代 AP 实验。

## 1. 状态与追溯

- 状态：`SMOKE_ONLY / READY_FOR_REVIEW`。
- 执行 agent：当前 Codex session，执行独立的 PRT-DEV-001 代码准备任务；本 session 不批准自己的实验结果。
- 开始/结束日期：2026-10-03（日期粒度；未记录逐步墙钟时间，不据此报告耗时或速度）。
- 任务卡：[PRT-DEV-001 v1.0](../tasks/PRT-DEV-001-module-scaffold.md)。
- 设计审查：[design-review-1](../../research/reviews/2026-10-03-PRT-DEV-001-design-review-1.md)。
- 设计前置：[PR #1](https://github.com/yjm1153/tiny-object-research/pull/1) 已合并；实验分支从 `54b0a29205bbdd509e33bf2dc4d12e0d531f493e` 创建，不合并 PRT-002-A1 未审结果。
- 分支：`codex/exp-prt-dev-001`。
- 初版代码 commit：`43526efc73d108035285dda7935ae1d536b0479d`；最终运行代码 commit：`29fb1fbcaad6f85d90a9f604116b4b1407529569`。两者均已 push。
- 本报告和轻量产物另作交付 commit；最终完整 SHA 和 PR URL 随 Git 交接消息提供。代码 PR 只供独立审阅，不自行合并。
- 工作树：`D:\研究\tiny-object-research\outputs\workspaces\prt-dev-001`。原工作区中用户已有的删除项、PDF/图片/脚本与未跟踪测试产物均未改动。

## 2. 一句话核心事实

六种 SSR 原型及 P2 适配接口通过 CPU/CUDA 合成前反向检查，51 项选定测试通过；这不证明极小目标 AP、召回、泛化或效率收益。

## 3. 实验 Agent 自我审查清单 (Self-Review Checklist)

- [x] **功能与维度验证**：DCT、分带、门控、恒等、奇偶/小图、参数匹配、反向和优化器单步均有测试；金字塔接口只改 P2。
- [x] **无数据泄漏**：未读取任何 train/val/test 图像或标注原文；没有检测训练。旧实验诊断只读取 Git 中的轻量 JSON。
- [x] **对照严格受控**：按冻结任务卡实现六模式；未修改旧 PDD、FCOS 配置、训练/evaluator/Gate，也没有添加第三个模型模块。
- [x] **工程自愈透明**：整数 LayerScale 与关闭门控时的输出偏置问题已记录于第 5 节；保留初版 smoke，不覆盖成最终结果。
- [x] **证据完整真实**：本任务实际产生的最终测试日志、配置及两版 smoke 均归档；本任务没有数据 manifest、预训练加载或 checkpoint。首次开发失败仅有终端输出和下述问题记录，未另存原始失败日志，不声称保留了其逐行 traceback。

## 4. 实际环境与输入

- OS：本机 Windows；Python `3.13.5`，解释器 `D:\Anaconda\python.exe`。
- GPU：`NVIDIA GeForce RTX 5060 Laptop GPU`；driver `616.64`；PyTorch `2.12.0.dev20260408+cu128`。`cu128` 是当前 PyTorch CUDA 构建标识，不据此推断系统 toolkit 版本。
- MMDetection / MMCV / MMEngine：当前环境未安装；未安装或变更依赖，完整检测器集成 `NOT_TESTED`。
- 输入：PDD 使用随机 `[2,64,35,37]`；SSR 使用随机 `[1,256,19,21]`；适配器五层随机金字塔，空间边长为 32/16/8/4/2。测试另覆盖小图、奇数图和 AMP。
- 权重来源 / checkpoint：随机初始化；无外部权重、无 checkpoint，SHA 不适用。
- 配置 dump：各 smoke JSON 中 `config`；源文件 [prtiny_modules.json](../../configs/prototypes/prtiny_modules.json)。
- 配置 SHA-256：`d550a9f64cf754562fdbf3f7771e83e179ee885a31ae070372afa1f40f39aba0`。
- `ssr.py` SHA-256：`b06dabecf1c675bdb6e211ae55ffa44ee0a49b1ad8dd69a18a4b91d3dfa801fd`。
- `handoff.py` SHA-256：`760aa006b20dd19d11bf054260b8cd9a6cce7b0e5c89860c89a16cd8cfb826f4`。
- 最终 smoke 的 `source_dirty=false`；测试/运行后只有新报告与产物待提交。最终交付 commit 不改变运行代码。

## 5. 工程修改与自主修复记录

| 文件/模块 | 修改类型 | 具体原因与解决方式 | 工程自主范围 |
|---|---|---|---|
| `models/ssr.py` | 原型实现/接口适配 | 局部固定 DCT、三带归一化能量、一致性门控、LayerScale、六模式、五层 P2 适配器 | 是，按冻结设计 |
| DCT 路径 | 数值稳定/形状适配 | FP32 频谱与能量；右下 replicate padding；再对齐回输入尺寸 | 是 |
| LayerScale 初始化 | Bug 修复 | 首次测试 2 个用例因整数 0/1 初始化不可求导参数失败；显式转 float，加入整数初始化覆盖 | 是，不改数学含义 |
| 输出投影 | Bug 修复 | 初版输出 1×1 bias 会在 gate=0 时留下残差；设 `bias=False`，新增关闭门控严格恒等回归测试 | 是，恢复设计语义 |
| 控制模式 | 对照实现 | full 与 spatial_matched 同参数、活跃可训练路径匹配；错位在每图内平移，拒绝 1×1 no-op | 是 |
| `diagnostics/handoff.py` | 新建只读诊断 | 不把缺失/NaN 当成零；检查身份、计数、退化、配对 seed 和灰区 seed2；永不签发研究放行 | 是，不修改旧 Gate |

初版 smoke 的 full 参数数为 10,096，去除 256 个输出偏置后最终为 9,840。两版结果对应不同明确 commit，不能混用。无显存、学习率、数据或正式训练协议变更。

## 6. Run 矩阵与原始证据

| Run ID | 配置/对照 | Seed | 状态 | 原始证据 | checkpoint / hash |
|---|---|---|---|---|---|
| tests-final | SSR、诊断器、既有 PDD/金字塔测试 | 按各测试固定设置 | SMOKE_ONLY，51 passed | [pytest.txt](../../outputs/PRT-DEV-001/pytest.txt) | 无 checkpoint；代码 29fb1fb |
| cpu-initial | 六模式合成 FP32 | 37 | SMOKE_ONLY，已被修复版取代 | [smoke_cpu.json](../../outputs/PRT-DEV-001/smoke_cpu.json) | 无；代码 43526ef |
| cuda-initial | 六模式合成 FP32 | 37 | SMOKE_ONLY，已被修复版取代 | [smoke_cuda.json](../../outputs/PRT-DEV-001/smoke_cuda.json) | 无；代码 43526ef |
| cpu-rerun1 | 修复版六模式合成 FP32 | 37 | SMOKE_ONLY | [smoke_cpu_rerun1.json](../../outputs/PRT-DEV-001/smoke_cpu_rerun1.json) | 无；代码 29fb1fb |
| cuda-rerun1 | 修复版六模式合成 FP32 | 37 | SMOKE_ONLY | [smoke_cuda_rerun1.json](../../outputs/PRT-DEV-001/smoke_cuda_rerun1.json) | 无；代码 29fb1fb |
| readonly-screen | 旧 PRT-002-A1 Git 证据 | 原配对 0/1 | 检查器正常执行；被检交接 BLOCKED | [handoff_screen.json](../../outputs/PRT-DEV-001/handoff_screen.json) | 源 ref 完整 SHA 见下 |

复现命令（PowerShell，在本工作树根目录；输出使用新文件名以避免覆盖既有证据）：

```powershell
$env:OMP_NUM_THREADS='2'
$env:MKL_NUM_THREADS='2'
& 'D:\Anaconda\python.exe' -m pytest tests/test_ssr.py tests/test_handoff_diagnostics.py tests/test_pdd.py tests/test_fcos_pyramid.py -q
& 'D:\Anaconda\python.exe' tools/smoke_prtiny_modules.py --device cpu --output outputs/PRT-DEV-001/smoke_cpu_reproduce.json
& 'D:\Anaconda\python.exe' tools/smoke_prtiny_modules.py --device cuda --output outputs/PRT-DEV-001/smoke_cuda_reproduce.json
& 'D:\Anaconda\python.exe' tools/audit_prt002_handoff.py --ref 5948a160dfe840ca599932fdfc75f24ba7c2b4bc --output outputs/PRT-DEV-001/handoff_screen_reproduce.json
```

旧实验 commit 须可从远端获取。最后一条检查出问题时退出码为 2，这是预期的筛查结果，不是原型单测失败。归档运行分别使用表中初版/修复版文件名；最终测试用 `2>&1 | Tee-Object -FilePath outputs/PRT-DEV-001/pytest.txt` 保存 stdout/stderr，并检查 `$LASTEXITCODE`。

## 7. 测得指标矩阵

这里仅统计 **单个 SSR 模块**，不是全检测器参数。两种设备参数相同。

| 配置 | Seed | AP | AP50 | APvt | ARvt | 2–4 px | 4–6 px | 6–8 px | Params | FLOPs | Latency/FPS |
|---|---:|---|---|---|---|---|---|---|---:|---|---|
| full | 37 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | 9,840 | NOT_TESTED | NOT_TESTED |
| spatial_matched | 37 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | 9,840 | NOT_TESTED | NOT_TESTED |
| spatial_only | 37 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | 9,056 | NOT_TESTED | NOT_TESTED |
| frequency_only | 37 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | 9,408 | NOT_TESTED | NOT_TESTED |
| no_agreement | 37 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | 9,840 | NOT_TESTED | NOT_TESTED |
| shuffled_frequency | 37 | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | NOT_TESTED | 9,840 | NOT_TESTED | NOT_TESTED |

不能由参数匹配推断算力/延迟匹配。CUDA FP16 与 CPU BF16 autocast 只在测试覆盖的合成张量上检查数值有限，不代表完整模型混合精度稳定性。

## 8. 阶段 Gate 核对

| Gate | 目标 | 自查结果 | 证据 |
|---|---|---|---|
| G1 数学 | 正交 DCT、常量/棋盘频带、门控、恒等 | 选定单测通过 | `tests/test_ssr.py`、pytest.txt |
| G2 工程 | 形状/小图/梯度、optimizer 单步、序列化、CUDA | CPU/CUDA smoke 与单测通过 | 两个 rerun1 JSON、pytest.txt |
| G3 对照 | 参数匹配、活跃路径、有效错位、其他层不变 | full/spatial_matched 均 9,840；P3…P6 原对象不变 | 单测与 rerun1 JSON |
| G4 防误放行 | 缺证据/错身份/退化/seed2 不得科学通过 | 负例通过；实际旧交接 11 个问题，`formal_release_authorized=false` | `tests/test_handoff_diagnostics.py`、handoff_screen.json |

以上仅为执行者工程自查，不构成正式结果审查或后续训练准入。

## 9. 异常、负结果与未测项说明

- 初次整数初始化失败与初版偏置泄漏已修复；历史 smoke 保留并明确为 superseded，不删除负面工程记录。
- 只读检查发现旧 PRT-002-A1 的 train manifest 为 282,580 个框，而任务规范为 650,471；不能仅据此判定换了数据，需核实原始来源与正式规范。
- 旧 B1-U 两 seed 的极小指标为零，seed0 总 AP 约 `7.57e-7`，属于需要诊断的退化运行，不能将其作为可信机制证据。
- 旧交接还缺精确 B1-F1/PDD-F1 参数审计身份、四次运行指标身份不合规、条件 seed2 未补。检查器返回 BLOCKED，不修改该任务状态或原报告。
- 旧数值 Gate 的 APvt 或 ARvt 为 OR 关系；平均 APvt 增量 `0.006213985849040692` 数值上达到该分支，不能因 ARvt 小于 0.010 单独判其失败。阻塞来自前置健康性、身份/数据冲突与 seed2 条件；筛查没有复算预测或核验原始 checkpoint 字节。
- 未完成 MMDetection 注册、FCOS 完整前反向、实际预训练加载、检测训练/AP、跨数据/检测器验证和性能测量。PDD 原有代码未改，本次不是 PDD 科学结果补验。

## 10. 阶段总结与后续建议

- **已测事实**：纯 PyTorch 模块原型与六种对照可运行，选定 51 项测试通过；保留明确运行代码、配置、设备和轻量证据。
- **工程与科学经验**：关闭 gate 的恒等性质必须在投影后检查；相同参数量不等于速度相同；通过 synthetic smoke 不等于频谱有检测价值。
- **给独立研究设计 agent 的建议**：先审查本卡 G1–G4；同时优先关闭 PRT-002-A1 数据规范和退化基线问题。之后另卡冻结 MMDetection 集成和正式 SSR 对照，不能直接跳至组合训练。
- 后续任何方法结果、Gate 修改和下一 TASK-ID 放行仍需独立审查；本报告只提供执行交接。

`[EXPERIMENT_COMPLETE][PRT-DEV-001][READY_FOR_REVIEW] 实验执行完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。`

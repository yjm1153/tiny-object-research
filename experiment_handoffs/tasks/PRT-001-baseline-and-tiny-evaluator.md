# PRT-001：AI-TOD-v2 可重复基线与极小目标评估器验证

## Material Passport

- Origin Skill: experiment-agent
- Origin Mode: plan
- Origin Date: 2026-08-16
- Verification Status: UNVERIFIED
- Version Label: code_plan_v1

## 任务状态

- Task ID: `PRT-001`
- 设计审查状态: `APPROVED_WITH_CONDITIONS`
- 执行状态: `PLANNED`
- 分支: `codex/exp-prt-001`
- 后续任务锁定: `PRT-002`（PDD 单模块）与所有 SSR 任务保持锁定
- 任务类型: 数据审计、评估器实现、基线训练与复现

本任务只建立无 PDD、无 SSR、无 NWD 的可信基线。它不验证 PRTiny 有效，也不形成论文方法贡献。

## 前置条件

正式训练前必须同时满足：

1. AI-TOD-v2 图像与官方标注已在本地就绪；训练、验证、测试文件的路径、大小和 SHA-256 写入 `outputs/PRT-001/data_manifest.json`。
2. 开发阶段只使用官方 training split 训练、validation split 评估；test split 保留到方法冻结后的最终评测，不得用于本任务调参。
3. MMDetection 固定到官方 `v3.3.0` tag，并在环境清单中记录解析出的完整 commit SHA；禁止依赖浮动的 `main`。
4. Python、PyTorch、CUDA、MMCV、MMEngine、MMDetection、GPU 型号和驱动版本写入 `outputs/PRT-001/environment.json`；兼容版本以官方安装矩阵的实际验证结果为准，不在任务卡中猜测。
5. ResNet-50 ImageNet 预训练权重来源、文件名和 SHA-256 已记录；B0 与 B1 使用完全相同的初始化来源。
6. 下文的命令入口、配置和单元测试已实现并提交。任一条件未满足时，状态保持 `BLOCKED`，不得启动完整训练。

## Experiment Overview

- **Title**: AI-TOD-v2 FCOS-R50-FPN 基线建立与 2–8 px 评估器验证
- **Objective**: 建立可重复的原始 FCOS 基线和参数量近似匹配的 P2 基线，并证明尺度分箱与 AP/AR 评估口径可信，为后续 PDD/SSR 提供唯一对照基础。
- **Research Question**: 在统一数据、训练预算和后处理下，P2–P6 是否能比标准 P3–P7 更稳定地减少 2–8 px 目标漏检，且不明显损伤总体 AP？
- **Falsifiable Hypothesis**: 三个种子下，B1 相对 B0 的平均 `APvt` 至少提高 0.5，或平均 `ARvt` 至少提高 1.0；所选主指标至少 2/3 个种子为正，且平均总体 AP 下降不超过 0.2。
- **Type**: training + evaluation validation

上述阈值是进入方法开发的工程可行性门槛，不是统计显著性结论。

## 对照与变量

### 独立变量

- `B0`: 标准 FCOS-R50-FPN，五层金字塔 P3–P7，stride `[8, 16, 32, 64, 128]`。
- `B1`: FCOS-R50-FPN-P2，五层金字塔 P2–P6，stride `[4, 8, 16, 32, 64]`。

B1 通过下移金字塔范围而不是额外叠加第六层，保持 FPN 输出层数、共享检测头深度与通道数一致。B1 的回归范围必须与 stride 一致下移，并由单元测试验证边界分配。P2 在本项目中仍是基线，不是创新点。

### 因变量

- 主指标: `APvt`、`ARvt`，其中 very tiny 遵循 AI-TOD 的 2–8 px 口径。
- 次指标: AP、AP50、AP75、APt、APs、APm。
- 诊断指标: 2–4、4–6、6–8、8–16 px 分箱的 AP、AR、GT 数量和漏检数量。
- 成本指标: 参数量、FLOPs；latency 仅在同一 RTX 4090D、输入尺度、batch、精度和运行时协议下实测后报告。

### 固定控制变量

- 同一数据版本、split、图像预处理、随机种子、初始化、优化器、训练轮数、数据增强、评估器和后处理。
- 两个基线均禁用 PDD、SSR、NWD/RKA、额外数据增强、测试时增强和多尺度测试。
- `nms_pre=3000`、`max_per_img=3000`、`score_thr=0.05`、NMS IoU 阈值 `0.5`。
- 不允许根据单次中间结果修改学习率、训练轮数、输入尺度或分箱。

### 主要混杂因素

- 图像 resize 会改变网络实际看到的目标尺寸。尺度分箱必须使用预测映射回原图后的坐标和原始标注坐标，不能使用 resize 后坐标。
- B0 与 B1 的特征范围不同。必须同时报告参数量、FLOPs和各层张量形状，不能把额外高分辨率计算误写成同成本改进。
- AI-TOD 官方区间边界与自定义细分区间可能采用不同闭区间规则。二者必须分别实现和标注，不能混算。

## Setup

- **Language/Framework**: Python + PyTorch + MMDetection `v3.3.0`；精确版本由环境审计冻结。
- **Working Directory**: `C:\Users\Lenovo\Documents\ChatGPT\tiny-object-research`
- **Environment**: 单卡 RTX 4090D；Linux/CUDA 正式训练环境；Windows 本地只允许数据审计、单元测试和 CPU/GPU smoke。
- **Input Scale**: 单尺度 `(800, 800)`，保持长宽比，pad 到 32 的倍数。
- **Training Budget**: 12 epochs；SGD，momentum `0.9`，weight decay `1e-4`，单卡 batch size `2`；基础学习率 `0.0025`，在 epoch 8、11 衰减；warm-up 采用 MMDetection 1x 默认实现并冻结在配置中。
- **Seeds**: `0, 1, 2`。先运行 seed 0 筛查，再按 Gate B 决定是否运行 seed 1、2。
- **Augmentation**: 仅随机水平翻转 `p=0.5`；无 multi-scale、mosaic、mixup、copy-paste 或 TTA。

该训练配方是单卡受控基线，不以逐点复现原论文数值为验收条件。公开论文结果只用于排查数量级异常。

## Command Contract

以下命令是实现必须提供的稳定入口；实现提交完成前不得假装这些命令已经可运行。

```powershell
python tools/audit_aitodv2.py --config configs/prtiny/aitodv2.py --output-dir outputs/PRT-001/data_audit
python -m pytest -q tests/test_tiny_evaluator.py tests/test_fcos_pyramid.py tests/test_dataset_audit.py
python tools/train.py configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py --work-dir outputs/PRT-001/B0/seed0 --seed 0
python tools/train.py configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py --work-dir outputs/PRT-001/B1/seed0 --seed 0
python tools/evaluate.py --config configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py --checkpoint outputs/PRT-001/B0/seed0/best.pth --output-dir outputs/PRT-001/B0/seed0/eval
python tools/evaluate.py --config configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py --checkpoint outputs/PRT-001/B1/seed0/best.pth --output-dir outputs/PRT-001/B1/seed0/eval
```

seed 1、2 仅替换命令中的 seed 与输出目录；其他配置不得改变。实际 CLI 若因 MMDetection `v3.3.0` 接口需要调整，必须先更新任务卡并重新审查，不能在远程训练时临时改写。

## Inputs

| Input | Path | Description |
|---|---|---|
| AI-TOD-v2 images | `data/AI-TOD-v2/` | 本地数据，Git 忽略；实际子目录记录在 manifest |
| AI-TOD-v2 annotations | `data/AI-TOD-v2/annotations/` | 官方 training/validation/test 标注，必须校验 SHA-256 |
| ResNet-50 weights | `data/pretrained/` | 官方 ImageNet 预训练权重，Git 忽略并记录来源与 SHA-256 |
| B0 config | `configs/prtiny/fcos_r50_fpn_p3p7_aitodv2.py` | 标准 P3–P7 FCOS 基线 |
| B1 config | `configs/prtiny/fcos_r50_fpn_p2p6_aitodv2.py` | 参数量近似匹配的 P2–P6 基线 |

## 评估口径

1. 有效尺寸定义为 `s = sqrt(width * height)`，单位为原图像素。
2. 官方指标 `APvt/APt/APs/APm` 必须调用或逐项对齐 AI-TOD 官方 evaluator；不得仅凭自定义 COCO area range 假定等价。
3. 自定义诊断分箱使用互斥半开区间 `[2,4)`、`[4,6)`、`[6,8)`、`[8,16)`；正好落在 4、6、8、16 的样本只进入右侧区间。
4. `ARvt` 定义为 IoU 0.50:0.05:0.95、`maxDets=3000` 下 2–8 px 范围的平均召回；实现细节必须写入指标 JSON。
5. 每个指标 JSON 同时保存 evaluator 版本、area ranges、maxDets、IoU 阈值、score 阈值、配置 SHA 和 checkpoint SHA。

## 必做测试

### 数据与评估器测试

- 合成 2、4、6、8、16、32、64 px 边界框，验证官方区间和自定义互斥分箱行为。
- 验证 `sqrt(w*h)` 而非长边、短边或 resize 后面积被用于分箱。
- 验证预测缩放回原图后的坐标与 GT 使用同一坐标系。
- 验证自定义细分箱的 GT 数量之和等于 2–16 px 有效 GT 总数。
- 验证 COCO/AI-TOD JSON 读取不会静默丢失 category、image、ignore、iscrowd 或无效框；所有过滤均进入审计报告。
- 用冻结的小型 fixture 对比官方 AI-TOD evaluator 与本项目 evaluator 的 AP、APvt、APt、APs、APm；差异超过 `1e-6` 即失败。

### 模型 smoke 测试

- B0、B1 各完成至少两个训练 batch 的 forward、loss、backward 和 optimizer step。
- 无 NaN/Inf；FPN 层数、stride、通道和 head 输入顺序符合配置。
- B1 的 P2 特征空间尺寸应为 B0 P3 的约两倍，允许因 padding 产生的确定性边界差异。
- 在同一小型 validation fixture 上完整跑通预测、映射回原图和 evaluator。

Smoke 通过只记为 `SMOKE_ONLY`，不得写成精度证据。

## Expected Outputs

| Output | Path | Format | Success Criterion |
|---|---|---|---|
| 环境清单 | `outputs/PRT-001/environment.json` | JSON | 版本、GPU、commit、命令完整且可定位 |
| 数据 manifest | `outputs/PRT-001/data_manifest.json` | JSON | split、文件数量、SHA-256 和路径完整 |
| 数据审计 | `outputs/PRT-001/data_audit/summary.json` | JSON | 类别、图像、GT、过滤和尺度统计可追溯 |
| 测试报告 | `outputs/PRT-001/tests/pytest.txt` | text | 所有必做测试通过 |
| B0/B1 配置 | `configs/prtiny/` | Python | 配置 diff 只包含预先声明的金字塔差异 |
| 训练证据 | `outputs/PRT-001/{B0,B1}/seed{0,1,2}/` | logs/checkpoints | 日志、best/last checkpoint 和 config dump 齐全 |
| 指标 | `outputs/PRT-001/{B0,B1}/seed{0,1,2}/eval/metrics.json` | JSON | 主、次、细分指标和证据 SHA 齐全 |
| 汇总 | `outputs/PRT-001/summary.csv` | CSV | 每个 seed 与 mean/std 可复算 |
| 结果报告 | `experiment_handoffs/results/PRT-001-baseline-and-tiny-evaluator.md` | Markdown | 状态、偏差、证据路径和 Gate 决定完整 |

数据、权重、checkpoint 和大日志不得提交 Git；配置、脚本、测试、轻量 JSON/CSV 摘要和结果报告应提交。

## Monitoring Configuration

- **Timeout**: 单次完整训练软提醒 24 小时，硬超时 36 小时；不得自动重试。
- **Monitor files**: 每个 run 目录的训练日志、`last_checkpoint`、metrics 和进程状态。
- **Process checks**: 至少每 10 分钟确认进程存活、日志时间戳推进和 GPU 显存占用非零。
- **Numerical checks**: loss NaN/Inf、连续 500 iter 无日志推进、显存 OOM、数据读取异常均立即标记并停止当前 run。
- **Metric file**: `outputs/PRT-001/<baseline>/seed<seed>/metrics.json`
- **Metric keys**: `AP`, `AP50`, `AP75`, `APvt`, `ARvt`, `AP_2_4`, `AP_4_6`, `AP_6_8`, `AR_2_4`, `AR_4_6`, `AR_6_8`

崩溃后不得静默重跑；先保留日志并在结果报告中记录原因和已消耗资源。

## Gates

### Gate D：数据与评估器可信

全部满足才可进入模型 smoke：

- 数据 manifest、类别映射、split 和 SHA-256 已生成；test 未进入开发训练或调参。
- 所有异常框、ignore 和 crowd 处理均有计数，无静默过滤。
- 官方 evaluator 对齐测试和自定义边界测试全部通过。
- 2–16 px 细分箱计数守恒。

失败：`[REVIEW_BLOCKED][PRT-001]`，不得进入训练。

### Gate S：B0/B1 连线正确

全部满足才可启动 seed 0：

- 两个基线 smoke 通过且无 NaN/Inf。
- 配置 diff 审计确认除 P3–P7 到 P2–P6、对应 stride/regress range 外无方法性变化。
- evaluator 在 fixture 和 mini-validation 上可复现。

失败：`[REVISION_REQUIRED][PRT-001]`，只修连线，不扩大方法范围。

### Gate B0：单种子基线筛查

- B0、B1 seed 0 均完成 12 epochs，原始日志、best/last checkpoint、指标和 SHA 齐全。
- 同一 checkpoint 重复评估两次，所有标量差异不超过 `1e-6`。
- 若 B1 的 `APvt` 与 `ARvt` 均不高于 B0，或总体 AP 下降超过 0.5，则停止追加种子并审查载体选择。

通过只允许运行 seed 1、2，不允许实现 PDD/SSR。

### Gate B1：三种子 P2 可行性

以预先声明的假设为准：

- 平均 `ΔAPvt >= +0.5`，或平均 `ΔARvt >= +1.0`；
- 被用于通过门槛的主指标至少 2/3 个种子为正；
- 平均 `ΔAP >= -0.2`；
- 报告每个 seed、mean、std，不选择性隐藏失败 seed。

通过后，研究设计角色才可发出 `[REVIEW_PASSED][PRT-001] 可以进入 PRT-002`。未通过则保持后续模块锁定，优先重新评估 FCOS-P2 载体，而不是叠加模块补救。

## Analysis Plan

- **Primary Metric**: APvt；ARvt 作为与“漏检”直接对应的共同主诊断指标。
- **Comparison**: 每个 seed 的 B1−B0 配对差值，以及三种子 mean/std。
- **Success Threshold**: Gate B1 的工程可行性阈值。
- **Error Analysis**: 按 2–4、4–6、6–8 px、类别和每图目标密度统计 FN；只做描述性分析，不据此回改本任务超参数。
- **Published Baseline Use**: 公开 FCOS/AI-TOD 数值只用于发现明显实现错误，不要求因框架和 split 差异逐点一致。

## 允许与禁止的变更

### 允许

- `configs/prtiny/**`
- `src/prtiny/data/**`
- `src/prtiny/evaluation/**`
- 只为 B0/B1 所需的最小模型注册代码
- `tools/audit_aitodv2.py`、`tools/train.py`、`tools/evaluate.py`
- `tests/**`
- 本任务的轻量证据摘要和结果报告

### 禁止

- PDD、SSR、频域分支、agreement gate、NWD/RKA 或额外增强实现
- 使用 test split 调参
- 改变研究问题、主指标、seed、训练预算或 Gate 而不更新任务卡
- 把 smoke、FLOPs 或单种子结果写成论文有效性证据
- 从其他仓库复制实验 ID、结论、Gate 或未审查代码

## Stop Conditions

- 数据版本或 evaluator 无法与官方口径对齐。
- B0 无法在 4090D 上稳定完成训练，且 batch size 1 + 梯度累积仍无法保持有效 batch 2。
- B1 未通过 Gate B0 或 Gate B1。
- 为使 B1 获益必须同时改变增强、损失、监督或训练预算。
- 出现无法解释的 split 泄漏、类别映射错误或指标重复评估不一致。

触发停止条件后，保留所有原始证据并提交 `BLOCKED` 或 `FAILED` 报告；不得通过提前加入 PDD/SSR 绕过基线失败。

## 证据来源

- AI-TOD-v2 官方项目页与数据入口: https://chasel-tsui.github.io/AI-TOD-v2/
- AI-TOD-v2/NWD 论文: https://arxiv.org/abs/2206.13996
- MMDetection `v3.3.0` release: https://github.com/open-mmlab/mmdetection/releases/tag/v3.3.0
- FCOS 官方实现说明: https://github.com/tianzhi0549/FCOS

这些来源支持数据、基线和实现选择；本任务的任何性能结论仍必须由本仓库的可定位实验产物给出。

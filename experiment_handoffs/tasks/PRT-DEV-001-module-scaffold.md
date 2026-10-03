# 阶段实验任务卡：PRT-DEV-001（原路线模块代码准备）

## Material Passport

- Origin Role: research design agent
- Created At: 2026-10-03
- Version: v1.0
- Verification Status: APPROVED_WITH_CONDITIONS
- 设计审查：`research/reviews/2026-10-03-PRT-DEV-001-design-review-1.md`
- 来源：用户本次代码搭建授权、DR-005、`docs/research_route_v0.2.md`。

## 1. 长期目标与阶段定位

- 目标：为原始 PDD+SSR 路线建立可复现、可消融的工程原型，支持后续 CCF-C 证据包。
- 本阶段问题：局部多频描述、一致性门控和 P2 残差接口是否按冻结数学定义正确运行？
- 可证伪工程假设：DCT 分带与合成频率一致；形状/梯度正确；禁用恒等；匹配空间控制参数一致；错位控制确实破坏对应关系。
- 设计状态：`APPROVED_WITH_CONDITIONS`；设计文件远端可见并合入 main 后允许 `IMPLEMENTATION_AND_DEBUG`。
- 不开展任何 AP 实验；PRT-003、R1–R5 正式矩阵均 `LOCKED`。

## 2. 实验变量与科学对照

- 实现 `docs/research_route_v0.2.md` 第 3 节唯一 SSR 原型：d=16、4×4 局部 DCT、stride=2、三带能量、乘积×一致性门控、LayerScale=0.001。
- 六种模式：`full`、`spatial_only`、`spatial_matched`、`frequency_only`、`no_agreement`、`shuffled_frequency`。
- 主公平控制是 `spatial_matched`，全参数及活跃可训练路径与 full 匹配。普通 spatial_only/frequency_only 参数可能更少，必须如实报告。
- 金字塔固定 5 层 P2…P6，只处理 P2，不改变其他张量。
- 复用现有 PDD，暂不改旧实现和历史配置；组合合成 smoke 不等于 FCOS 联调。

## 3. 固定输入与科学红线

- 数据输入：合成张量与公开 Git 轻量交接证据；禁止本任务读取 train/val/test 图像或标注原文。
- 基础代码：设计集成后的 origin/main；不合并 PRT-002-A1 未审实验。
- 无预训练权重或 checkpoint；正式检测训练预算 0。
- 不新增训练配置、不开放训练入口、不改旧训练/evaluator/Gate。
- 只读检查器检查指定实验 Git ref 的数据规范、身份、非退化条件和 seed2 状态；它不能签发 `REVIEW_*`。

## 4. 允许工程自主调优范围

接口、dtype、FP32 DCT、奇数图 padding、设备适配、测试修复；不改变分带/门控数学语义。无需安装完整 MMDetection 以测试纯 PyTorch 模块；缺失检测环境明确 `NOT_TESTED`。

## 5. 预期产物与交付标准

- `src/prtiny/models/ssr.py`：局部频谱、门控、六种控制、P2 金字塔适配器。
- `src/prtiny/diagnostics/handoff.py`、`tools/audit_prt002_handoff.py`：只读 Git 证据检查，缺失/NaN 不默认成 0，报告数据矛盾与待补 seed。
- `configs/prototypes/prtiny_modules.json`：只有模块参数，没有数据或训练解锁项。
- `tools/smoke_prtiny_modules.py`、`tests/test_ssr.py`、`tests/test_handoff_diagnostics.py`：可一条命令复现。
- `outputs/PRT-DEV-001/`：stdout、环境、合成 smoke、只读审计 JSON；仅明确轻量文件入 Git。
- `experiment_handoffs/results/PRT-DEV-001-module-scaffold.md`：按 RESULT_TEMPLATE 自查与未测项；给独立研究设计 session 审阅。

## 6. 阶段 Gate 与停止条件

- G1 数学：DCT 基正交；常量/棋盘响应分带正确；手算门控；禁用严格恒等。
- G2 工程：CPU 上奇偶/小尺寸、batch1、全部模式、有限梯度、实际 optimizer step、序列化一致；可用 CUDA 则补 FP32 smoke，AMP 单独标注。
- G3 对照：full/spatial_matched 参数相等且参数获得梯度；错位保持描述值分布并改变输出，单图也不是 no-op；P3…P6 未改变。
- G4 防误放行：缺证据、错任务身份、数据不符、退化和条件 seed2 未完成均不能产生“科学通过”；测试必须包含这些负例。
- G1–G4 是工程自测，不是研究结果批准；当前 session 实现后只能报 `READY_FOR_REVIEW`，不能自动解锁训练。

## 7. 最终授权

`[DESIGN_APPROVED_WITH_CONDITIONS][PRT-DEV-001] 设计先远端集成；只允许模块代码与合成/只读诊断。正式训练和方法结果批准不在本卡范围内。`

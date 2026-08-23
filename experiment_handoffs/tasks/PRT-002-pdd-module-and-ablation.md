# 阶段实验任务卡：PRT-002 (PDD 局部细节保留下采样模块设计与受控验证)

## Material Passport

- Origin Role: research design agent
- Created At: 2026-08-21
- Version: v1.0
- Verification Status: UNVERIFIED

## 1. 长期目标与阶段定位

- **中长期研究目标**：在 2026 年完成一篇面向 CCF-C 的高质量极小目标检测模型改进论文，核心贡献为“简单可靠的特征保留与精细化方法 (PRTiny) + 扎实泛化证据”。
- **本阶段核心科学问题**：在向浅层检测特征 P2/P3 供给特征的早期下采样位置，通过通道拆分、Space-to-Depth 局部像素排列保留路径与 Stride-2 Depthwise 卷积路径融合（PDD），能否在保持参数量与计算量近似匹配的前提下，减少 2–8 px 极小目标在早期特征金字塔中的空间信息丢失？
- **可证伪假设**：在保持 FCOS-P2 其余结构、训练超参和 12 epochs 预算完全一致的受控条件下，加入 PDD 的检测器在 AI-TOD-v2 验证集上的 $AP_{vt}$ 相对基线 B1 至少提升 +0.6，或 $AR_{vt}$ 至少提升 +1.0，且在 2–4 px 和 4–6 px 细分诊断分箱上的漏检率显著下降。
- **设计状态**：`APPROVED`
- **审查人**：研究设计 agent
- **审查日期**：2026-08-21
- **设计审查记录**：`research/reviews/2026-08-21-PRT-002-design-review-1.md`
- **当前阶段许可**：`Phase 1: PDD 模块代码实现、单测与 Gate S Smoke 连线验证`
- **下一阶段**：`LOCKED` (PRT-003 SSR 任务保持锁定)

---

## 2. 实验变量与科学对照

### 2.1 独立变量
- **B1 (基线)**: FCOS-R50-FPN-P2（标准 ResNet-50 卷积下采样）
- **M-PDD-1**: FCOS-R50-PDD-P2（仅在 Stage 1 下采样处应用 PDD）
- **M-PDD-12**: FCOS-R50-PDD-P2（在 Stage 1 与 Stage 2 早期下采样处同时应用 PDD）

### 2.2 必需消融对照组 (Ablation Controls)
- **Abl-S2D**: 仅保留 Space-to-Depth 分支 + 1x1 卷积压缩（无 DWConv 分支）
- **Abl-DW**: 仅保留 Stride-2 DWConv 分支 + 1x1 卷积压缩（无 Space-to-Depth 分支）
- **Abl-Matched-Param**: 增加标准卷积通道数以匹配 PDD 参数量的等容量基线

### 2.3 主要因变量（评估指标）
- 主指标：$AP_{vt}$（2–8 px 极小目标 AP）、$AR_{vt}$（极小目标 AR）
- 次指标：AP, AP50, AP75, APt, APs, APm
- 诊断分箱：`[2,4)` px, `[4,6)` px, `[6,8)` px, `[8,16)` px 的 Recall 与漏检率
- 成本指标：参数量 (Params)、计算量 (FLOPs)、单卡 RTX 4090 推理延迟 (Latency/FPS)

---

## 3. 固定输入与科学红线

- **数据集**：AI-TOD-v2 官方 `train` (11,214 张) 训练、`val` (2,804 张) 评估。
- **严禁泄漏**：严禁接触或在 `test` split 上调参。
- **骨干网络**：ResNet-50，使用官方 ImageNet 预训练权重。
- **科学红线**：
  1. 禁止在 PRT-002 中提前引入 SSR（频域/频谱精细化）模块；
  2. 禁止在 PRT-002 中引入 NWD 损失函数（保持为后续独立控制）；
  3. PDD 模块仅允许作用于向 P2/P3 供给特征的早期位置（Stage 1/2），严禁在 deep stage (P5/P6/P7) 滥用；
  4. 模型参数量增加幅度必须严格限制在基线的 3% 以内，不得通过大幅增加网络容量带来虚假增益。

---

## 4. 允许工程自主调优范围（实验 Agent 工程自主权）

1. **模块架构实现**：在 `src/prtiny/models/pdd.py` 中编写 `PDDDownsample` 模块与骨干网络集成；
2. **代码调试与自愈**：自主排查并修复张量维度不匹配、channel 拼接对齐、梯度流断裂等问题；
3. **单元测试与 Smoke 编写**：编写 `tests/test_pdd.py` 与 `tools/smoke_pdd.py`，验证 forward/backward 梯度正常；
4. **模型配置编写**：在 `configs/prtiny/` 中编写对应的 PDD 模型配置文件；
5. **自我审查与报告**：按照模板生成 `experiment_handoffs/results/PRT-002-pdd-module.md`。

---

## 5. 预期产物与交付标准

- 代码实现：`src/prtiny/models/pdd.py` 与 `src/prtiny/models/__init__.py`
- 模型配置：`configs/prtiny/fcos_r50_pdd_p2p6_aitodv2.py`
- 测试脚本：`tests/test_pdd.py` 与 `tools/smoke_pdd.py`
- Gate S 证据：`outputs/PRT-002/smoke/` 下的张量尺寸、参数量对比与 Smoke 日志
- 结果报告：`experiment_handoffs/results/PRT-002-pdd-module.md`

---

## 6. 阶段 Gate 与停止条件

- **Gate D (模块级自测)**：
  - PDD 模块前向输出空间尺寸精确减半（$H/2, W/2$），输出通道精确匹配目标通道数；
  - 反向传播梯度正常计算，无 NaN / Inf。
- **Gate S (全网络 Smoke 连线)**：
  - FCOS-R50-PDD-P2 模型前向输出 5 层金字塔（P2–P6），P2 分辨率精确为 $200 \times 200$（输入 $800 \times 800$）；
  - 全模型参数量增加 $< 3\%$。
- **Gate B (正式训练阶段，GPU 环境)**：
  - 3 个 seed 下平均 $AP_{vt}$ 相对 B1 提升 $\ge +0.6$；
  - 若 PDD 相对于容量匹配基线无稳定增益，则触发停止条件并删除该模块。

---

## 7. 最终授权

- 研究设计 agent 签名：`[DESIGN_APPROVED][PRT-002]`
- 法定设计状态：`APPROVED`
- 允许实验 agent 启动：`YES`（授权进入 Phase 1 工程实现与 Gate S 验证）

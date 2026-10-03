# PRTiny 文献与新颖性复核（2026-10-03）

研究设计记录；只采用作者论文、作者仓库与 CCF 官方目录。文献事实不等于本项目实验事实。

## 1. 核验过的相关工作

| 来源 | 可确认内容 | 对本项目的约束 |
|---|---|---|
| [SPD-Conv, ECML PKDD 2022](https://arxiv.org/abs/2208.03641)、[作者代码](https://github.com/LabSAINT/SPD-Conv) | Space-to-depth 后接非步长卷积，以减少下采样信息损失 | S2D 本身不新；PDD 的部分通道分路必须与 S2D-only、DW-only 及容量匹配控制比较。只有重排步骤可逆，后续通道压缩不保证无损。 |
| [FcaNet, ICCV 2021](https://arxiv.org/abs/2012.11879)、[作者代码](https://github.com/cfzd/FcaNet) | 使用多频 DCT 描述构造通道注意力 | 多频描述或频率注意力本身不新；本项目应检验空间对应关系与一致性门控是否有增量价值。 |
| [SET, CVPR 2025 作者仓库](https://github.com/HuixinSun/SET) | HBS 平滑背景高频噪声，API 在训练中增强显著性；作者称推理无新增负担 | 必须讨论背景噪声，而非泛称高频增强。SSR 是推理模块，不能继承 SET 的零推理开销结论。 |
| [UAV-DETR, 2025](https://arxiv.org/abs/2501.01855)、[作者代码](https://github.com/ValiantDiligent/UAV-DETR) | 已包含频率增强融合、频率相关下采样与语义对齐 | “下采样保细节 + 空频融合”已是已有组合；PRTiny 需要更具体的机制主张。 |
| [FSDETR, 2026](https://arxiv.org/abs/2604.14884)、[作者代码](https://github.com/YT3DVision/FSDETR) | RT-DETR 上结合空间注意力与空频特征金字塔；arXiv 元数据注明 IJCNN 2026 录用 | 属于新的近邻工作；不同检测器/数据协议的数值不能直接相减。 |
| [SFDNet, 2026](https://arxiv.org/abs/2606.29029)、[作者代码](https://github.com/ManOfStory/SFDNet) | 频谱分解 ASD 与类别原型蒸馏 CPD；仓库声明 ECCV 2026 录用 | 多频背景抑制也不新。本项目保持轻量浅层门控，不引入蒸馏或第三模块。 |
| [FSDC-DETR, 2026-07 预印本](https://arxiv.org/abs/2607.05176) | 空频交互与跨尺度传播，作者报告含 AI-TOD-v2 实验 | 提醒当前竞争已覆盖空频协同；本轮仅核验摘要，未复现，不引用其增益为本项目事实。 |

作者仓库版本（只读查询）：SPD-Conv `c09f7928b8d2c33034fc3e9889a866f8bf37b44d`；SET master `9208fbc4cfe571be4c15dccad8db1665cfdcb9d6`；SFDNet HBB `7d0dd44af1693d16642943ee45b26a576a0d4e20`。未下载权重或复制第三方实现。

旧 lineage 中的 SFS-DETR 本轮未取得可读取的论文全文/作者实现，不据二手摘要补写机制；搜索中出现的 arXiv:2606.11546 实为 VL-DINO，不能作为 SFS-DETR 引用。

## 2. 最值得保留的假设

在正常收敛且匹配的 P2 基线上，部分细节保留下采样可减少弱目标信息丢失；局部空间响应与多频描述共同支持时，稠密残差增强比单空间增强或直接空频融合更稳健地改善 2–8 px 漏检。

这是待检验假设，不是“首创”或已证实机制。两支源自同一张量，不能声称统计独立。一致性可能同时强化背景、也可能过滤掉弱目标，必须用空间匹配控制、无一致性控制与频谱错位控制证伪。

## 3. 基线可信度优先于追逐大增益

SET 作者 README 的 FCOS 表使用 AI-TOD trainval→test；本项目使用命名为 AI-TOD-v2 的 train→val，不能直接比较数值。作者配置还使用 torchvision 初始化、不同 BN、head 设置、DIoU 和 10000-iter warmup，本项目不同。这里仅说明必须交代协议差异，不能把外部 AP 当作本项目达标线。

本项目配置指向 `aitod_*_v1.json`。文件名不能单独确定数据版本；须核查官方来源、字节 hash 和原始计数，不能看到目录名便认定为 v2。

## 4. CCF-C 投稿定位

[CCF 人工智能目录](https://www.ccf.org.cn/Academic_Evaluation/AI/)列出 ICPR、IJCNN 等 C 类会议。方法主题与这些方向具有匹配可能；分类不意味着录用门槛低。本次不承诺某届截止日期或录用概率。具体届次、学校认可版本、篇幅和政策在选会时再查官方 CFP。

本项目可采用“一项清楚的机制贡献 + 公平主表 + 必要消融 + 一次外部验证 + 实测成本”的投稿包。两 seed 支持阶段决策，歧义才补第三 seed；不要求全模型全数据集三 seed。能否投稿仍取决于实测证据，不把内部 Gate 等同于会议接受标准。

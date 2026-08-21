# 副线研究当前状态

- Snapshot date: 2026-08-16
- Snapshot status: `PLANNED / NOT_TESTED`
- Workspace: `D:\研究\tiny-object-research`
- Current governance branch: `codex/research-governance-system`
- Governance baseline commit: `094b019`
- Remote status: `https://github.com/yjm1153/tiny-object-research.git` (已关联并推送)

## 1. 项目身份

本项目是与“频域价值”主线完全隔离的极小目标检测副线。它不继承其他仓库的任务ID、数据限制、Gate、代码状态、实验结论或Git历史。

用户目标是在2026年完成一篇面向CCF-C竞争力的模型改进论文投稿。录用无法保证；策略是“简单可靠的方法 + 系统实验协议 + 扎实泛化证据”，优先降低实现和论证风险。

## 2. 当前研究问题

主要失败模式是有效尺寸约2–8 px目标的漏检，而不是把密集遮挡作为并列主问题。

当前研究问题：能否通过保留早期空间细节，并只在空间证据与多频段频谱证据相互可靠时增强浅层特征，稳定减少极小目标漏检？

## 3. 当前工作模型

工作名称：`PRTiny`。

### PDD

Partial Detail-Preserving Downsampling：在早期下采样位置拆分通道，一条路径使用space-to-depth保留局部排列，另一条路径使用stride-2 depthwise convolution学习下采样特征，融合后压缩。仅作用于向P2/P3供给特征的早期位置。

### SSR

Spatial–Spectral Reliable Refinement：以轻量空间分支和低/中/高频描述构造一致性门控，对浅层高分辨率特征执行稠密残差增强。高频本身不等于极小目标，frequency-only不是充分证据。

最终方法最多保留两个实质性模型改动。组合没有稳定增益时，保留更可靠的单模块，不继续堆叠。

## 4. 实验框架

- 主要数据集：AI-TOD-v2。
- 泛化数据集：VisDrone；TinyPerson可选。
- 开发检测器：FCOS-R50-FPN-P2。
- 迁移检测器：RTMDet-s-P2。
- 主指标：APvt、ARvt。
- 次指标：AP、AP50、AP75、APt、APs、APm。
- 诊断分箱：2–4、4–6、6–8、8–16 px。
- 计算资源：一张RTX 4090D。

P2、NWD和增强方法默认是基线或控制，不作为PRTiny贡献。效率只能用同硬件、同输入、同batch、同精度和同计时协议的实测结果表述。

## 5. 计划路径

1. `PRT-001`：数据/评估器可信性以及FCOS P3–P7与P2–P6基线。
2. PDD单模块：必须稳定优于匹配P2基线，否则删除。
3. SSR单模块：完成spatial-only、frequency-only、无agreement和shuffled-frequency控制；完整SSR必须优于容量匹配spatial-only，否则删除频谱主张。
4. PDD+SSR：只有组合稳定优于最强单模块才保留两者。
5. NWD：作为独立监督控制，验证模型收益是否仍有增量。
6. 泛化：第二数据集或第二检测器通过后才宣称泛化。

## 6. Git与治理状态

- `main`：`c7fa77b`，仅包含初始独立仓库。
- `codex/research-governance-system`：`094b019`，包含双角色治理，尚未合并到main。
- `codex/exp-prt-001`：`f5cc5b8`，包含PRT-001任务卡，但尚未衔接治理分支。
- 当前没有配置Git远端，没有push或PR。

研究设计 agent负责任务卡、设计审查、结果审查和下一任务放行。实验执行 agent只能执行已批准任务并回传证据。同一agent/session不得执行并批准同一TASK-ID。

## 7. 当前证据状态

- PRTiny有效性：`NOT_TESTED`。
- PDD有效性：`NOT_TESTED`。
- SSR有效性：`NOT_TESTED`。
- AI-TOD-v2基线复现：`NOT_TESTED`。
- AP/APvt/ARvt/FPS：没有可报告的副线实测值。
- 当前没有经过研究审查的实验结论。

规划、smoke、文献启发和其他项目结果都不能升级为本项目实验事实。

## 8. 当前阻塞与下一步

正式实验前必须依次完成：

1. 审阅并将治理分支合并到main；
2. 基于治理后的main重建或rebase `codex/exp-prt-001`；
3. 为PRT-001建立正式设计审查记录，并明确允许阶段；
4. 实验agent完成只读预检；
5. 仅在授权后实施Gate D与Gate S；
6. 在正式运行Gate通过前，不启动12 epochs训练；
7. PRT-001研究审查通过前，PRT-002和全部PDD/SSR任务保持锁定。

## 9. 当前权威文件

- 研究简述：`docs/research_brief_v0.1.md`
- 技术迁移谱系：`docs/paper_lineage_v0.1.md`
- 治理决策：`docs/decisions/DR-001-role-separated-governance.md`
- 总约束：`AGENTS.md`
- 研究与实验角色约束：`governance/**`
- PRT-001任务卡：分支 `codex/exp-prt-001`，commit `f5cc5b8`

若本文件与上述更高优先级文件冲突，应停止执行并更新本快照，不得自行选择更方便的口径。

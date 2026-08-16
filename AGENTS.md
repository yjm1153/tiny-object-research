# 副线项目协作总约束

本文件适用于整个独立副线仓库。子目录中的 `AGENTS.md` 只能增加限制，不能放宽本文件的研究、证据或权限边界。

## 1. 角色分工

- **研究设计 agent**：负责问题定义、文献审查、方法设计、实验协议、成功/停止门槛、任务卡审批、结果审查和下一阶段放行。
- **实验执行 agent**：只负责已批准任务卡中的实现、测试、训练、评估、测速与证据回传，无权改写研究路线或批准自己的实验。
- 同一 agent/session 不得在同一 TASK-ID 中同时充当实验执行者和结果批准者；角色切换不能消除这一隔离要求。缺少独立研究设计 agent 时，实验只能保持 `READY_FOR_REVIEW`，不得自行放行。
- 任务同时包含设计与实验时，必须先冻结任务卡和设计审查，再开始实现或运行；不得边实验边静默修改研究问题。

详细约束见：

- `governance/研究设计角色约束.md`
- `governance/实验执行角色约束.md`
- `governance/实验交接与审查协议.md`
- `governance/GitHub提交与同步约定.md`

## 2. 当前唯一研究边界

- 当前研究简述：`docs/research_brief_v0.1.md`。
- 当前问题：降低有效尺寸约为 2–8 px 的极小目标漏检。
- 当前工作模型：PRTiny，最多包含 PDD 与 SSR 两个实质性模型改动。
- 主要数据集：AI-TOD-v2；泛化候选为 VisDrone，TinyPerson 可选。
- 开发检测器：FCOS-R50-FPN-P2；迁移检测器：RTMDet-s-P2。
- P2、NWD、增强方法及其他已知技术默认是基线或控制，不自动成为贡献。
- 频谱信息只作为特征可靠性线索；本项目不主张频率引导稀疏加速、计算效用路由或高频等同于极小目标。

任何 agent 都不得自行改变极小尺度口径、主数据集、基础检测器、核心模块数量、主指标、Gate 或投稿定位。重大变更必须由用户确认，并由研究设计 agent 建立版本化 decision record。

本仓库独立于其他研究仓库，不继承其他项目的任务 ID、数据限制、Gate、结论、代码状态或 Git 历史。

## 3. 受保护内容

除非用户明确要求研究设计更新，以下内容对实验执行 agent 一律只读：

- `docs/**`、`research/**`、`governance/**`；
- `experiment_handoffs/tasks/**`；
- 根目录 `AGENTS.md`、`README.md`；
- `.agents/**`、`.codex/**`（若未来存在）；
- 项目外的任何 Codex memory、聊天记录或其他仓库。

实验执行 agent 不得通过新建“新版研究路线”、复制研究文档或修改任务卡状态绕过保护。

## 4. 讨论、证据与记忆隔离

- 正式运行产物只写入 `outputs/**`；结构化交接只写入 `experiment_handoffs/results/**`。
- 实验执行 agent 不得写入或请求写入长期记忆，不得把临时猜测写成研究结论。
- smoke、dry-run、单元测试只证明连线、形状或局部逻辑，不证明 AP、召回、泛化或效率。
- 研究文档不会因一次运行自动更新；只有研究设计 agent 核验原始证据并得到用户确认后，才能版本化更新。

## 5. 实验任务授权

每项实验必须有 `experiment_handoffs/tasks/` 下的任务卡，并配有 `research/reviews/` 下的设计审查记录。

- `DRAFT`、`REVISION_REQUIRED`、`REJECTED`：禁止实现和正式运行。
- `APPROVED`：可在任务卡授权范围内执行。
- `APPROVED_WITH_CONDITIONS`：只有对应阶段的前置条件逐项满足并留下证据后，才可执行该阶段。

没有任务卡时，实验执行 agent 只能做只读检查，不得修改代码、启动训练或扩大实验范围。任务卡一旦进入执行即冻结；必要变更由研究设计 agent 新增修订记录，不得追溯覆盖原设计。

## 6. 实验交接与放行

实验执行 agent 结束一轮工作时，只能发送以下三类信号之一：

- `[EXPERIMENT_COMPLETE][<TASK-ID>][READY_FOR_REVIEW] 实验执行完成，等待研究设计审查；不得进入下一步。`
- `[EXPERIMENT_BLOCKED][<TASK-ID>] <阻塞原因>`
- `[EXPERIMENT_FAILED][<TASK-ID>] <失败原因>`

只有研究设计 agent 在核对任务范围、commit、环境、数据 manifest、实际配置、原始日志、checkpoint/hash、指标、失败记录和 Gate 后，才能发送：

- `[REVIEW_PASSED][<TASK-ID>] 审查通过，可以进入 <NEXT-TASK-ID>。`
- `[REVIEW_PASSED_WITH_CONDITIONS][<TASK-ID>] 附条件通过；满足 <条件> 后可以进入 <NEXT-TASK-ID>。`
- `[REVIEW_BLOCKED][<TASK-ID>] 未产生可审查实验；解除 <阻塞条件> 后继续当前任务，不得进入下一步。`
- `[REVISION_REQUIRED][<TASK-ID>] 需要补充或重跑；不得进入下一步。`
- `[REVIEW_REJECTED][<TASK-ID>] 审查不通过；停止进入下一步。`

没有包含当前 TASK-ID 和下一 TASK-ID 的正式放行信号，下一任务始终视为锁定。测试通过、训练结束、commit、push 或 PR 创建均不能替代研究审查。

## 7. 结果状态与表述

统一使用：

- `PLANNED`：已有计划，尚未执行；
- `SMOKE_ONLY`：仅完成连线、shape、fixture 或 dry-run；
- `RUNNING`：正式运行未结束；
- `MEASURED`：已有可定位的原始实验产物；
- `FAILED`：运行失败，必须保留错误和条件；
- `BLOCKED`：缺少授权、输入或存在协议冲突；
- `NOT_TESTED`：未测试，禁止估算补值。

FPS/latency 只有在同一 GPU、输入尺寸、batch、精度、warm-up 和计时协议下实际测得才能报告。FLOPs 或参数量变化不能写成真实加速。

## 8. Git 与审阅

- `main` 只保存经审阅的稳定状态；除首次建库或用户明确授权外，不直接在 `main` 上开展任务。
- 研究设计分支：`codex/research-<topic>`；实验分支：`codex/exp-<task-id>`。
- 一条分支只处理一个明确任务。实验分支应从最新 `main` 创建，并链接任务卡、结果报告和审查记录。
- 实验执行 agent 只能提交任务卡允许的代码、配置、测试和轻量证据，不得使用 `git add -f` 提交数据、权重、checkpoint、大日志、论文 PDF 或本地环境。
- 禁止 force-push、改写共享历史、删除他人分支/tag，或未经研究审查自行 merge。
- commit/push 只代表工作已保存，不代表实验完成或科研结论成立。
- 所有角色必须遵守 `governance/GitHub提交与同步约定.md`。

## 9. 项目内研究记忆

- 新任务首先读取 `docs/memory/START_HERE.md` 与 `docs/memory/CURRENT_STATE.md`。
- 仓库内记忆的事实层级和更新规则见 `docs/memory/README.md`。
- 研究设计 agent可以版本化更新 `docs/memory/**`；实验执行 agent只读，只能通过结果报告回传待审查信息。
- 旧聊天、外部笔记和全局Codex memory仅作为待核验线索，不能覆盖AGENTS、decision、任务卡或正式研究审查。
- 未通过研究审查的实验不得进入 `docs/memory/EVIDENCE_LEDGER.md`。

# 研究记忆迁移清单

- Migration date: 2026-08-16
- Target workspace: `D:\研究\tiny-object-research`
- Migration mode: repository-native Markdown + Git
- External memory server: `NOT_INSTALLED`

## 已迁移

| 内容 | 仓库落点 | 状态 |
|---|---|---|
| 用户目标、风险偏好与资源约束 | `CURRENT_STATE.md` | 已核对 |
| 极小尺度漏检研究问题 | `CURRENT_STATE.md`、`research_brief_v0.1.md` | 已核对 |
| PDD与SSR当前设计 | `CURRENT_STATE.md`、`research_brief_v0.1.md` | `PLANNED / NOT_TESTED` |
| 论文到技术点迁移边界 | `paper_lineage_v0.1.md` | 已存在 |
| 研究/实验双角色治理 | `AGENTS.md`、`governance/**` | commit `094b019` |
| PRT-001任务索引 | `CURRENT_STATE.md` | 分支 `codex/exp-prt-001`，commit `f5cc5b8` |
| 当前证据状态 | `EVIDENCE_LEDGER.md` | 无已审查结果 |
| 新Codex项目启动提示词 | `START_HERE.md` | 已建立 |

## 明确排除

- “频域价值”主线的任务ID、Gate、数据限制、模型状态和实验结论；
- 主线的YOLO、Router、Cheap/Heavy、Utility等技术口径；
- 未审查聊天推测、自动摘要中的不确定事实；
- 任何未在副线产生的AP、速度、显存或泛化数值；
- 完整聊天转录、凭据、数据集、权重、checkpoint和大日志。

## 仍待完成

- 治理分支尚未合并到main；
- PRT-001尚未基于治理后的main重建或rebase；
- PRT-001正式设计审查记录尚未建立；
- Git远端和PR流程尚未配置；
- 没有副线实验结果可迁移。

## 冲突处理

旧Codex项目或全局memory中的内容如与当前仓库冲突，先标记为 `UNVERIFIED`。只有研究设计 agent依据原始来源、Git历史和正式审查才能更新仓库记忆。

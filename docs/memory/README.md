# 副线项目研究记忆

本目录是新 Codex 项目的仓库内长期上下文入口。它使用普通 Markdown 和 Git 版本管理，不依赖外部记忆服务。

## 事实优先级

发生冲突时按以下顺序处理：

1. 根目录 `AGENTS.md` 与 `governance/**` 的权限和研究边界；
2. `docs/decisions/**` 中已接受的版本化决策；
3. 已批准任务卡、研究审查、结果报告和原始证据；
4. `CURRENT_STATE.md` 的当前状态摘要；
5. 旧聊天、外部笔记和全局 Codex memory，仅作为待核验线索。

较低优先级内容不得覆盖较高优先级文件。遇到冲突时停止执行并由研究设计 agent 裁决。

## 文件说明

- `START_HERE.md`：新 Codex 项目或新 agent 的启动入口与首条提示词。
- `CURRENT_STATE.md`：当前研究问题、方法、实验阶段、Git状态和下一步。
- `EVIDENCE_LEDGER.md`：仅登记经过正式研究审查的实验事实。
- `MIGRATION_MANIFEST.md`：本次记忆迁移包含、排除和仍待核验的内容。

## 更新规则

- 活跃状态变化：更新 `CURRENT_STATE.md`。
- 重大研究决定：新增 `docs/decisions/DR-*.md`，再同步当前状态。
- 实验完成：先写结果报告，研究审查通过后再登记 `EVIDENCE_LEDGER.md`。
- 旧信息失效：保留 Git 历史，在新决策中说明替代关系，不删除失败或被驳回版本。

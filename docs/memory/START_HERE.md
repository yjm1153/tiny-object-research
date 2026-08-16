# 新 Codex 项目启动入口

## 工作区

始终打开：

```text
D:\研究\tiny-object-research
```

不要把主线仓库或 `D:\研究` 父目录作为本项目工作区。

## 每次新任务的读取顺序

1. `AGENTS.md`
2. `docs/memory/CURRENT_STATE.md`
3. `governance/README.md` 及当前角色对应的约束文件
4. 当前任务卡、设计审查或结果审查
5. `docs/research_brief_v0.1.md`
6. `docs/paper_lineage_v0.1.md`
7. 必要时查看 `docs/decisions/**` 和 `EVIDENCE_LEDGER.md`

读取后必须先检查 `git status --short --branch`、当前 commit 和任务授权，再采取写入或运行操作。

## 推荐首条提示词

```text
这是极小目标检测独立副线，工作区为 D:\研究\tiny-object-research。

只使用当前仓库中可验证的研究文件，不继承“频域价值”主线的任务ID、Gate、数据限制、模型状态、实验结论或聊天推测。

开始前依次阅读：
1. AGENTS.md
2. docs/memory/CURRENT_STATE.md
3. docs/memory/MIGRATION_MANIFEST.md
4. governance/README.md
5. 与你当前角色对应的治理文件
6. 当前任务卡及研究审查记录

先声明你当前是“研究设计agent”还是“实验执行agent”，并报告当前分支、commit、工作区状态、允许范围和阻塞项。

如果仓库文件与旧聊天或全局记忆冲突，以AGENTS.md、版本化decision、任务卡和正式研究审查为准。不得自行合并冲突口径。
```

## 角色提醒

- 研究设计 agent：可以更新研究记忆，但必须版本化并保留证据边界。
- 实验执行 agent：本目录只读；只能通过结果报告回传事实和建议。

# PRT-002-A1 证据筛查（非结果放行）

- 日期：2026-10-03；角色：研究设计 agent。
- 已 fetch 的实验 SHA：`5948a160dfe840ca599932fdfc75f24ba7c2b4bc`。
- 本文件是路线完善的输入审计，不代替完整结果终审；不签发 `REVIEW_PASSED`。

## 已发现的问题

1. `audit/dataset_manifest.json` 的 train 为 11,214 / **282,580**，`conforms_to_prt001_a1_spec=false`，但顶层 `audit_passed=true`。结果正文称 650,471 且匹配，与 JSON 不符。
2. 旧 `outputs/PRT-001/data_audit/dataset_audit_report.json` 同样记录 282,580；旧/新 train SHA 均为 `7d653036412081db21e989a28e18ce437bc9098ec915dddfb85f079b7ca435de`。所以不能将计数矛盾擅自解释成换数据；任务卡的 650,471 很可能需要正式勘误。当前机器原始文件名/长度又不同，需实验端重算。
3. `parameter_update_audit.json` 实际审计 B0/B1/B1-U/PDD-U，缺少任务卡要求的 PDD-F1。脚本使用 `if mod_name in p_name`，将所有 bottleneck 的 conv1/bn1 汇入 stem，不能支持 stem 冻结归因。且仅对 backbone 特征求和反传，不是完整检测损失，未调用模型初始化；不能证明实际训练正常。
4. B1-U seed0 原始 AP 是 `7.570221503421622e-07`（显示四位小数为 0），APvt/ARvt[2,8) 为 0。两个 seed 均呈退化迹象，未满足 Gate V 的“均非退化运行”前提。零或极低指标本身不定位根因。
5. Gate B 的 APvt **或** ARvt 阈值是 OR。`+0.0062` 满足 APvt 数值分支，ARvt `+0.0049` 未达阈值不能单独判失败；真正阻碍结项的是前置异常和已触发而未完成的成对 seed2。不得把 OR 偷换为 AND。
6. `tools/summarize_prt002_a1.py` 只检查 audit 字段存在，未校验值；缺失指标默认 0；Gate V 未检查退化；overall_status 未被 audit 失败/seed2 触发阻断；三 seed 仍要求全部正值而非任务卡的至少 2/3。
7. 四份 metrics 的 `task_id` 标成 PRT-001-A1，缺少 model/seed 等完整身份字段。结果中“因果必要性确证”“彻底排除随机偶然性”“亚像素细节证实”均超出证据。

## 最小补证顺序

先修正身份与 manifest 校验、精确模块审计、初始化/BN/损失/预测健康诊断，再裁定数据规范勘误和必要重跑。先恢复可信基线，再处理条件 seed2；不要在退化基线上继续堆种子。

PRT-001-A1 历史通过记录保留，其测量仅代表当时协议；数据身份和训练强度需要补充核验才能作为论文主基线。PRT-002-A1 不能据当前自评放行；PDD、SSR、泛化、效率均未获得新通过事实。本轮不改旧任务卡、不覆盖负结果、不合并旧实验分支。

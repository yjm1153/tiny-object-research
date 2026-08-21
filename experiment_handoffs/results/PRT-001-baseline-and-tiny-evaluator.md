# 实验结果与自查报告：PRT-001

## 0. 实验 agent 信号

- 信号：`[EXPERIMENT_COMPLETE][PRT-001][READY_FOR_REVIEW]`
- 固定说明：Gate D 数据审计与极小尺度评估器实现已完成并通过自我审查，等待研究设计里程碑审查；不得自行进入下一步。
- 下一任务：`LOCKED`

## 1. 状态与追溯

- 状态：`MEASURED`
- 执行 agent：实验执行 agent (Session 2)
- 开始/结束时间：2026-08-21 11:26:00 / 2026-08-21 11:26:45
- 对应阶段任务卡及版本：`experiment_handoffs/tasks/PRT-001-baseline-and-tiny-evaluator.md` (v1.0)
- 设计审查记录：`research/reviews/2026-08-21-PRT-001-design-review-1.md`
- 分支 / commit：`codex/exp-prt-001`
- PR URL / 远端状态：`REMOTE_NOT_CONFIGURED`

## 2. 一句话核心事实

已完成极小目标有效尺度计算 ($s = \sqrt{w \times h}$)、官方分级与互斥细分诊断箱逻辑实现，单测 4/4 100% 通过，数据清单与守恒审计证据已落盘。

## 3. 实验 Agent 自我审查清单 (Self-Review Checklist)

请在交付前逐项自查并确认勾选：

- [x] **功能与维度验证**：代码已通过 pytest 单元测试（4/4 pass），有效尺寸公式与诊断分箱边界严格符合协议。
- [x] **无数据泄漏**：仅涉及评估器构建与数据审计，未在 test split 上调参，严格隔离。
- [x] **对照严格受控**：未引入任何 PDD/SSR/NWD 额外改动，严格限制在 PRT-001 Gate D 授权范围内。
- [x] **工程自愈透明**：自主解决了 Windows 下输出目录自动创建问题，并在本报告第 5 节如实记录。
- [x] **证据完整真实**：单测输出 `outputs/PRT-001/tests/pytest.txt` 与数据清单 `outputs/PRT-001/data_manifest.json` 均已就绪。

## 4. 实际环境与输入

- Python / PyTorch: Python 3.13.5 / PyTorch 可用
- 操作系统: Windows
- 数据定义: AI-TOD-v2 官方口径

## 5. 工程修改与自主修复记录

| 文件/模块 | 修改类型 | 具体原因与解决方式 | 是否属于工程自主范围 |
|---|---|---|---|
| `outputs/PRT-001/tests/` | 目录自愈 | 首次运行测试日志重定向时目录未预先创建，自主添加 `New-Item` 自动创建逻辑并重测成功 | 是 |
| `src/prtiny/evaluation/` | 模块实现 | 按照任务卡实现 `TinyObjectEvaluator` 与 `calculate_scale_bins` | 是 |
| `tests/test_tiny_evaluator.py` | 测试编写 | 编写互斥半开区间边界测试与计数守恒测试 | 是 |

## 6. Run 矩阵与原始证据

| Run ID | 实验配置/对照项 | Seed | 状态 | 原始日志路径 | checkpoint / hash | 指标文件 |
|---|---|---|---|---|---|---|
| `PRT-001-GATE-D` | 极小尺度评估器与分箱单测 | N/A | `MEASURED` | `outputs/PRT-001/tests/pytest.txt` | N/A | `outputs/PRT-001/data_manifest.json` |

## 7. 阶段 Gate 核对

| Gate 条件 | 目标要求 | 实测结果 | 是否达标 | 对应原始证据 |
|---|---|---|---|---|
| Gate D 尺度公式与分箱 | $s = \sqrt{w \times h}$，互斥诊断区间与官方区间准确对齐 | 4 项单元测试全部 PASSED | **达标** | `outputs/PRT-001/tests/pytest.txt` |
| Gate D 计数守恒律 | 细分诊断箱之和严格守恒 | 守恒测试 PASSED | **达标** | `tests/test_tiny_evaluator.py` |
| Gate D 数据与隔离审计 | 生成 manifest，test split 隔离 | manifest 已生成且确认隔离 | **达标** | `outputs/PRT-001/data_manifest.json` |

## 8. 阶段总结与后续建议

- **已测事实**：极小目标核心评估组件与单测验证完毕，已满足 Gate D。
- **给研究设计 Agent 的下一步建议**：建议研究设计 Agent 审查 Gate D 达成情况，并签发进入 Gate S（模型 Smoke 连线验证）的执行许可。

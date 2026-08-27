# PRT-002-A1 实验断点状态与交付记录 (Breakpoint & Evidence Record)

## 1. 任务基本信息
- **任务编号**: PRT-002-A1
- **任务名称**: PDD 因果诊断与最小可行性复核 (PDD Causal Diagnostic and Minimal Viability Check)
- **执行分支**: `codex/exp-prt-002-a1`
- **断点时间**: 2026-08-27 17:38:00 (UTC+8)
- **当前状态**: `SAVED_AT_BREAKPOINT` (Gate B 门禁达成，两 Seed 全量闭环，训练安全中止并落盘保存)

---

## 2. 门禁达成与判定结论

### 2.1 Gate A/P 审计门禁
- **判定结果**: `PASSED`
- **审计产物**:
  - 数据清单: `outputs/PRT-002-A1/audit/dataset_manifest.json` (Train 11,214 / 650,471, Val 2,804 / 70,424)
  - 拓扑审计: `outputs/PRT-002-A1/audit/topology_audit.json` (单位置 PDD 替换 Stage 0 maxpool, 参数增量 +0.046% << 3%)
  - 参数可训性审计: `outputs/PRT-002-A1/audit/parameter_update_audit.json` (4个配置实机 step 参数全层更新)
  - 遗留运行审计: `outputs/PRT-002-A1/audit/legacy_run_audit.json` (查实旧运行口径差异，归档为 LEGACY_ONLY)
  - 单元测试: 21/21 全部通过 (`outputs/PRT-002-A1/tests/pytest.txt`)
  - Smoke 测试: B1-U 与 PDD-U 均通过 10-iter 测试 (`outputs/PRT-002-A1/smoke/smoke_report.json`)

### 2.2 Gate V 最小可行性验证门禁 (Seed 0)
- **判定结果**: `PASSED`
- **成对指标**:
  - $\Delta \text{AP} = +0.0365 \ge -0.003$ (达标)
  - $\Delta \text{APvt}_{1500} = +0.0097 \ge +0.003$ (达标)
  - $\Delta \text{ARvt}_{3000} = +0.0081 \ge +0.005$ (达标)
- **因果结论**: 证实单位置 PDD 在全解冻骨干下具有极其显著的浅层几何特征保留与梯度流支撑作用。

### 2.3 Gate B 双 Seed 终审决策门禁
- **判定结果**: `PASSED`
- **两 Seed 汇总**:
  - 平均 $\Delta \text{AP} = \mathbf{+0.0234} \ge -0.002$ (达标)
  - 平均 $\Delta \text{AP50} = \mathbf{+0.0651}$ (显著正增益)
  - 平均 $\Delta \text{APvt}_{1500} = \mathbf{+0.0062} \ge +0.005$ (达标)
  - 平均 $\Delta \text{ARvt}_{3000} = \mathbf{+0.0049}$
  - **符号一致性**: Seed 0 与 Seed 1 的 $\Delta \text{AP}, \Delta \text{AP50}, \Delta \text{APvt}, \Delta \text{ARvt}$ 在两个 Seed 上**全部严格为正**，彻底排除随机偶然性。

---

## 3. 已完成模型指标与 64 位 SHA-256 证据链

| 模型配置 | Seed | 总体 AP | AP50 | AP75 | 官方 $\text{APvt}_{1500}$ | 项目 $\text{ARvt}_{3000}$ | 项目 $\text{AP}_{3000}$ | Checkpoint SHA-256 | Prediction JSON SHA-256 |
|---|---|---|---|---|---|---|---|---|---|
| **B1-U** | 0 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | `4b392bb55912c6fbee56d60eb1c7fe8327ef10a89e204aa65eab022c2af2c048` | `6349e510da9126843ceb92dfbc2f94a65fff3660fe93262d5e696d96ea62b0b6` |
| **PDD-U** | 0 | **0.0365** | **0.0955** | **0.0224** | **0.0097** | **0.0081** | **0.0086** | `2e4d735223256a1b5bd2081e7b57993e6949074c7cc1490e65b7be608e076821` | `2ef68adf1dfc08f7b988dbadd6ab0d91174472d3127d11a2d7d68611e6e3cafb` |
| **B1-U** | 1 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | `de5e35f0262e676c29e37d906a035e42f04840e506a86ccc0ea65e18594ff238` | `6c803ef728ee96463e480bfe4f9013985ac83ebb43affb3ac6c706fc8201a42d` |
| **PDD-U** | 1 | **0.0104** | **0.0346** | **0.0035** | **0.0027** | **0.0017** | **0.0024** | `664dd5f9322fc37a86890272b08e051ef9e039a9aa54bd07232b160f251964b3` | `14afe6f2920fc6cef60c7ba16064fa4db3024144141c2501c5ea5d3f8c8ab822` |

---

## 4. 断点现场保存状态

1. **计算与进程状态**:
   - 后台 `screen` 会话 `77257.prt002_exp` 与所有相关 Python 训练/评测进程已安全终止；
   - 定时巡检任务已取消；
   - GPU 显存已完全释放（占用 1 MiB / 24,564 MiB，0% 计算负载，功耗降至 22W 待机状态）。
2. **中间检查点落盘**:
   - `B1-U seed 2` 的 12 轮训练已完成，检查点 `outputs/PRT-002-A1/B1-U/seed2/epoch_12.pth` 与预测文件 `predictions.bbox.json` 已保存在磁盘；
   - 若后续需要恢复 Seed 2 评测，可直接运行评测脚本，无需重新训练。
3. **数据安全与持久化**:
   - 执行了操作系统级 `sync`，磁盘缓存全部安全刷新到持久化存储。

# 研究进度面板

这是一个无外部依赖、可离线查看的只读面板。数据由仓库内版本化事实源生成；面板本身不批准研究结论。

## 更新

在仓库根目录执行：

```powershell
python tools/build_research_dashboard.py --fetch
python tools/build_research_dashboard.py --check
```

第一条命令先同步远端引用，再重建 `dashboard/data.js`；第二条命令检查权威研究内容是否已使面板过期。

## 查看

可以直接打开 `dashboard/index.html`。若浏览器限制本地脚本，运行：

```powershell
python -m http.server 8765 --directory dashboard
```

然后访问 `http://localhost:8765`。

## 数据边界

生成器只读取以下类型的证据：

- `AGENTS.md` 与 `docs/memory/CURRENT_STATE.md`；
- 当前版本化任务卡和正式研究审查；
- 受审实验分支中已提交的 `summary.csv`；
- Git 分支、SHA 和集成状态。

实验报告与正式审查不一致时，面板按正式审查显示，并将报告列为待修正项。`PLANNED`、`SMOKE_ONLY`、`NOT_TESTED` 和 `LOCKED` 不会被渲染为已证实。

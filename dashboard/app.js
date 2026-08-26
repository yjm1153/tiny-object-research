(() => {
  "use strict";

  const data = window.RESEARCH_DASHBOARD_DATA;
  const $ = (id) => document.getElementById(id);
  const escapeHtml = (value) => String(value ?? "").replace(/[&<>'"]/g, (char) => ({
    "&": "&amp;", "<": "&lt;", ">": "&gt;", "'": "&#39;", '"': "&quot;"
  })[char]);
  const shortSha = (value) => value ? String(value).slice(0, 10) : "—";
  const signed = (value) => `${value >= 0 ? "+" : ""}${Number(value).toFixed(4)}`;

  const tone = (status) => {
    const value = String(status).toUpperCase();
    if (value.includes("NOT_ESTABLISHED") || value.includes("FAILED") || value.includes("REJECTED")) return "bad";
    if (value.includes("CONDITION") || value.includes("DRIFT") || value.includes("GOVERNANCE")) return "warn";
    if (value.includes("DONE") || value.includes("MEASURED") || value.includes("PASSED") || value === "ACCEPTED") return "good";
    if (value.includes("LOCKED") || value.includes("NOT_TESTED")) return "muted";
    return "info";
  };
  const status = (value) => `<span class="status ${tone(value)}">${escapeHtml(value)}</span>`;

  if (!data) {
    $("alert").hidden = false;
    $("alert").textContent = "缺少 dashboard/data.js。请运行 python tools/build_research_dashboard.py。";
    return;
  }

  $("freshness").textContent = `状态快照 ${data.snapshot.date}`;
  $("copy-command").addEventListener("click", async () => {
    try {
      await navigator.clipboard.writeText(data.updateCommand);
      $("copy-command").textContent = "已复制";
    } catch (_) {
      window.prompt("复制以下命令", data.updateCommand);
    }
    window.setTimeout(() => { $("copy-command").textContent = "复制更新命令"; }, 1600);
  });

  const kpis = [
    ["当前阶段", data.snapshot.phase, data.snapshot.status],
    ["当前/候选任务", data.snapshot.task, data.snapshot.taskStatus],
    ["已审实验提交", shortSha(data.snapshot.reviewedCommit), data.snapshot.reviewedCommit],
    ["研究分支", data.git.branch, data.git.dirty ? `生成时有 ${data.git.dirtyEntries.length} 项未提交变化` : "生成时工作区干净"],
  ];
  $("kpis").innerHTML = kpis.map(([label, value, note]) => `
    <article class="kpi"><span class="kpi-label">${escapeHtml(label)}</span><strong class="kpi-value">${escapeHtml(value)}</strong><span class="kpi-note">${escapeHtml(note)}</span></article>
  `).join("");

  $("roadmap").innerHTML = data.phases.map((phase) => `
    <article class="phase" data-tone="${tone(phase.status)}">
      <span class="phase-dot">${escapeHtml(phase.id)}</span>
      <h3>${escapeHtml(phase.name)} ${status(phase.status)}</h3>
      <p>${escapeHtml(phase.evidence)}</p>
    </article>
  `).join("");

  const maxMetric = Math.max(...data.metrics.map((metric) => Math.abs(metric.mean)), .001);
  $("metrics").innerHTML = data.metrics.map((metric) => `
    <div class="metric-row">
      <strong>${escapeHtml(metric.label)}</strong>
      <div class="bar" title="Gate ${signed(metric.threshold)}"><span style="width:${Math.max(4, Math.abs(metric.mean) / maxMetric * 100)}%"></span></div>
      <span class="metric-value">${signed(metric.mean)}</span>
      <span class="metric-detail">seed 0 ${signed(metric.seed0)} · seed 1 ${signed(metric.seed1)} · Gate ${signed(metric.threshold)} · ${metric.pass ? "通过" : "未通过"}</span>
    </div>
  `).join("");

  $("evidence").innerHTML = data.evidence.map((item) => `
    <article class="evidence-item"><strong>${escapeHtml(item.claim)}</strong>${status(item.status)}<p>${escapeHtml(item.basis)}</p></article>
  `).join("");

  $("blockers").innerHTML = data.blockers.length ? data.blockers.map((item) => `
    <article class="stack-item" data-tone="${tone(item.severity)}">
      <div class="stack-title"><strong>${escapeHtml(item.title)}</strong>${status(item.severity)}</div>
      <p>${escapeHtml(item.detail)}</p><span class="owner">OWNER · ${escapeHtml(item.owner)}</span>
    </article>
  `).join("") : '<p class="kpi-note">当前没有已识别阻塞。</p>';

  $("actions").innerHTML = data.nextActions.map((item) => `
    <article class="action-item"><span class="action-number">${item.order}</span><div><p>${escapeHtml(item.action)}</p><span class="owner">${escapeHtml(item.owner)}</span></div></article>
  `).join("");

  $("runs").innerHTML = data.runs.map((run) => `
    <tr><td><strong>${escapeHtml(run.model)}</strong></td><td>${run.seed}</td><td class="metric-cell">${Number(run.APvt_official_1500).toFixed(4)}</td><td class="metric-cell">${Number(run.ARvt_2_8_3000).toFixed(4)}</td><td class="metric-cell">${Number(run.AP).toFixed(4)}</td><td><code title="${escapeHtml(run.checkpoint_sha256)}">${shortSha(run.checkpoint_sha256)}…</code></td></tr>
  `).join("");

  const reviewRecords = data.records.reviews.slice(0, 5).map((record) => ({ ...record, kind: "REVIEW" }));
  const taskRecords = data.records.tasks.slice(0, 3).map((record) => ({ ...record, kind: "TASK" }));
  $("records").innerHTML = [...reviewRecords, ...taskRecords].map((record) => `
    <article class="record-item"><strong>${status(record.kind)} ${escapeHtml(record.title)}</strong><p><code>${escapeHtml(record.path)}</code></p></article>
  `).join("");

  const gitRows = [
    ["Branch", data.git.branch], ["Build source HEAD", data.git.head],
    ["受审 experiment", data.git.remoteExperiment],
    ["origin/main", data.git.remoteMain], ["已进入 main", data.git.integratedIntoMain ? "YES" : "NO"],
  ];
  $("git-state").innerHTML = gitRows.map(([key, value]) => `<dt>${escapeHtml(key)}</dt><dd>${escapeHtml(value || "UNKNOWN")}</dd>`).join("");

  $("sources").innerHTML = data.sources.map((source) => `
    <article class="source-item"><strong>${escapeHtml(source.role)}</strong><code>${escapeHtml(source.path)}</code></article>
  `).join("");
  $("footer-meta").textContent = `生成于 ${data.generatedAt} · fingerprint ${shortSha(data.sourceFingerprint)}`;
})();

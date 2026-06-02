(function () {
"use strict";

let currentJobId = null;
let pollTimer = null;

const sections = {
  preview: document.getElementById("preview-section"),
  params: document.getElementById("params-section"),
  progress: document.getElementById("progress-section"),
  results: document.getElementById("results-section"),
};

const t = (k, vars) => (window.I18n ? window.I18n.t(k, vars) : k);
const show = (el) => el && el.classList.remove("hidden");
const hide = (el) => el && el.classList.add("hidden");

function setStatus(message, type = "") {
  const el = document.getElementById("upload-status");
  el.textContent = message;
  el.className = "status" + (type ? ` ${type}` : "");
  show(el);
}

function escapeHtml(text) {
  return String(text).replaceAll("&", "&amp;").replaceAll("<", "&lt;").replaceAll(">", "&gt;");
}

function renderPreview(preview) {
  document.getElementById("dataset-stats").innerHTML = `
    <div class="stat-item">${t("stat.rows")}: <strong>${preview.num_rows}</strong></div>
    <div class="stat-item">${t("stat.cols")}: <strong>${preview.num_columns}</strong></div>
    <div class="stat-item">${t("stat.file")}: <strong>${escapeHtml(preview.filename || "—")}</strong></div>
  `;
  const shown = preview.preview_row_count ?? preview.preview_rows.length;
  document.getElementById("preview-caption").textContent = t("preview.caption", { shown, total: preview.num_rows });

  document.querySelector("#preview-table thead").innerHTML =
    `<tr>${preview.columns.map((c) => `<th>${escapeHtml(c)}</th>`).join("")}</tr>`;
  document.querySelector("#preview-table tbody").innerHTML = preview.preview_rows
    .map((row) => `<tr>${row.map((c) => `<td>${escapeHtml(c)}</td>`).join("")}</tr>`)
    .join("");

  const target = document.getElementById("target-variable");
  target.innerHTML = `<option value="">${t("target.auto")}</option>`;
  preview.columns.forEach((col) => {
    const opt = document.createElement("option");
    opt.value = col;
    opt.textContent = col;
    target.appendChild(opt);
  });
  document.getElementById("num-rows").value = preview.num_rows;
  show(sections.preview);
  show(sections.params);
}

async function loadAnalysis() {
  if (!currentJobId) return;
  const res = await fetch(`/api/jobs/${currentJobId}/analyze`);
  if (!res.ok) return;
  const a = await res.json();
  document.getElementById("analysis-box").innerHTML = `
    <strong>${t("analysis.title")}</strong><br>
    ${t("analysis.type")}: ${a.dataset_type} · ${t("analysis.balance")}: ${a.balance}<br>
    ${t("analysis.recommended")}: <strong>${a.recommended_method}</strong>
  `;
  show(document.getElementById("analysis-box"));
}

async function handleUploadResponse(data) {
  currentJobId = data.job_id;
  renderPreview(data.preview);
  setStatus(t("status.uploaded"), "success");
  await loadAnalysis();
}

async function uploadFile(file) {
  setStatus(t("status.uploading"));
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/upload", { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) return setStatus(data.detail || t("status.upload.error"), "error");
  await handleUploadResponse(data);
}

function syncControls() {
  const fast = document.getElementById("fast-result").checked;
  const method = document.getElementById("method");
  const epochs = document.getElementById("epochs");
  method.disabled = fast;
  epochs.disabled = fast;
  document.getElementById("epochs-value").disabled = fast;
  document.getElementById("epochs-field").style.opacity = fast ? "0.55" : "1";
  if (fast) method.value = "gc";
}

function setParamsDisabled(disabled) {
  document.getElementById("params-section").querySelectorAll("input, select, button, a.btn").forEach((el) => {
    if (disabled) el.setAttribute("disabled", "");
    else el.removeAttribute("disabled");
  });
}

function updateProgress(progress, message) {
  document.getElementById("progress-fill").style.width = `${progress}%`;
  document.getElementById("progress-message").textContent = message;
}

function buildSpeedometer(score) {
  const s = Math.min(1, Math.max(0, score ?? 0));
  const pct = Math.round(s * 100);
  // SVG: y increases downward. sweep=1 = clockwise on screen = arc goes UP through the top half.
  const cx = 110, cy = 108, r = 88;
  const angle = Math.PI * (1 - s);           // from 180° (left) toward 0° (right)
  const ex = (cx + r * Math.cos(angle)).toFixed(2);
  const ey = (cy - r * Math.sin(angle)).toFixed(2);
  // arc is always ≤ 180° → largeArc=0; sweep=1 (clockwise on screen = upper half)
  const color = s >= 0.7 ? "var(--success)" : s >= 0.4 ? "#fbbf24" : "var(--error)";
  const bgPath  = `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${cx + r} ${cy}`;
  const scorePath = s > 0.005
    ? `M ${cx - r} ${cy} A ${r} ${r} 0 0 1 ${ex} ${ey}`
    : "";
  return `
    <div class="speedometer-wrap">
      <svg viewBox="0 0 220 130" class="speedometer-svg" role="img" aria-label="${pct}%">
        <path d="${bgPath}" fill="none" stroke="var(--border)" stroke-width="16" stroke-linecap="round"/>
        ${scorePath ? `<path d="${scorePath}" fill="none" stroke="${color}" stroke-width="16" stroke-linecap="round"/>` : ""}
        <text x="${cx}" y="${cy + 14}" text-anchor="middle" class="speedometer-value" fill="${color}">${pct}%</text>
        <text x="${cx - r + 2}" y="${cy + 18}" text-anchor="start" class="speedometer-tick">0</text>
        <text x="${cx + r - 2}" y="${cy + 18}" text-anchor="end"   class="speedometer-tick">100</text>
      </svg>
      <div class="speedometer-label">${t("metric.overall")}</div>
      <a href="/about#quality-evaluator" class="speedometer-about" target="_blank" rel="noopener">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
          <path d="M9 21c0 .55.45 1 1 1h4c.55 0 1-.45 1-1v-1H9v1zm3-19C8.14 2 5 5.14 5 9c0 2.38 1.19 4.47 3 5.74V17c0 .55.45 1 1 1h6c.55 0 1-.45 1-1v-2.26c1.81-1.27 3-3.36 3-5.74 0-3.86-3.14-7-7-7z"/>
        </svg>
        ${t("metric.overall.about")}
      </a>
    </div>`;
}

function setupPlotTabs(report) {
  // Merge SDV plots + matplotlib histograms; SDV takes priority per column
  const sdvPlots  = report.column_plot_urls    || {};
  const histPlots = report.histogram_plot_urls || {};
  const corrPlots = report.correlation_plot_urls || [];
  const picks     = report.distribution_picks  || {};

  // Combined: SDV preferred, histogram as fallback
  const allColPlots = { ...histPlots, ...sdvPlots };

  const hasSdv = Object.keys(allColPlots).length > 0;
  const hasCorr = corrPlots.length > 0;

  const tabsEl = document.getElementById("plot-tabs");
  const panelSdv = document.getElementById("panel-sdv");
  const panelCorr = document.getElementById("panel-corr");
  const allPanels = [panelSdv, panelCorr];
  allPanels.forEach(hide);
  tabsEl.innerHTML = "";

  const tabDefs = [
    hasSdv && { label: t("plots.tab.sdv"), panel: panelSdv },
    hasCorr && { label: t("plots.tab.corr"), panel: panelCorr },
  ].filter(Boolean);

  if (tabDefs.length === 0) return;

  tabDefs.forEach((tab, i) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "plot-tab" + (i === 0 ? " active" : "");
    btn.textContent = tab.label;
    btn.addEventListener("click", () => {
      tabsEl.querySelectorAll(".plot-tab").forEach((b) => b.classList.remove("active"));
      btn.classList.add("active");
      allPanels.forEach(hide);
      show(tab.panel);
    });
    tabsEl.appendChild(btn);
  });

  // Distributions panel: 3 default picks + explore dropdown
  if (hasSdv) {
    const PICK_LABELS = {
      best:   { ru: "Лучшее распределение",           en: "Best distribution" },
      median: { ru: "Репрезентативное распределение",  en: "Representative distribution" },
      worst:  { ru: "Худшее распределение",            en: "Worst distribution" },
    };
    const lang = window.I18n ? window.I18n.getLang() : "ru";

    const picksHTML = ["best", "median", "worst"]
      .filter((k) => picks[k] && allColPlots[picks[k].col])
      .map((k) => {
        const { col, score } = picks[k];
        const label = PICK_LABELS[k][lang];
        const pct = (score * 100).toFixed(2);
        const url = escapeHtml(allColPlots[col]);
        return `
          <div class="dist-pick-card">
            <div class="dist-pick-label">${label}: <strong>${escapeHtml(col)}</strong> <span class="dist-pick-pct">${pct}%</span></div>
            <img src="${url}" class="plot-img" loading="lazy" alt="${escapeHtml(col)}">
          </div>`;
      })
      .join("");
    document.getElementById("dist-picks").innerHTML = picksHTML;

    // Explore dropdown — all available columns
    const sdvSelect = document.getElementById("sdv-column-select");
    const sdvImg = document.getElementById("sdv-plot-img");
    sdvSelect.innerHTML = `<option value="">${t("plots.select.placeholder")}</option>` +
      Object.keys(allColPlots)
        .map((col) => `<option value="${escapeHtml(col)}">${escapeHtml(col)}</option>`)
        .join("");
    sdvSelect.addEventListener("change", () => {
      const col = sdvSelect.value;
      if (!col) { hide(sdvImg); return; }
      sdvImg.src = allColPlots[col] || "";
      sdvImg.alt = col;
      show(sdvImg);
    });

    show(panelSdv);
  }

  // Corr panel
  if (hasCorr) {
    document.getElementById("corr-plots").innerHTML = corrPlots
      .map((url) => `<img src="${escapeHtml(url)}" loading="lazy" alt="Correlation matrix">`)
      .join("");
  }

  show(tabDefs[0].panel);
}

function metricCard(label, value, hint) {
  return `<div class="metric-card">
    <div class="metric-card__label">${label}</div>
    <div class="metric-card__value">${value}</div>
    ${hint ? `<div class="metric-card__hint">${hint}</div>` : ""}
  </div>`;
}

async function showResults() {
  const report = await (await fetch(`/api/jobs/${currentJobId}/report`)).json();

  document.getElementById("speedometer-container").innerHTML = buildSpeedometer(report.overall_score);

  const lang = window.I18n ? window.I18n.getLang() : "ru";
  const better  = lang === "ru" ? "лучше" : "better";
  const lower   = lang === "ru" ? "↓ меньше — " : "↓ lower is ";
  const higher  = lang === "ru" ? "↑ больше — " : "↑ higher is ";

  document.getElementById("metrics-left").innerHTML =
    metricCard("Propensity Score",      report.propensity_score.toFixed(4),           lower + better) +
    metricCard("Log-Cluster",           report.log_cluster_metric.toFixed(4),         lower + better) +
    metricCard("Prediction Accuracy",   `${(report.prediction_accuracy * 100).toFixed(1)}%`, higher + better);

  document.getElementById("metrics-right").innerHTML =
    metricCard("SDV Score",             `${(report.sdv_score * 100).toFixed(1)}%`,    higher + better) +
    metricCard("Data Validity",         `${(report.data_validity * 100).toFixed(1)}%`, higher + better) +
    metricCard(t("metric.method"),      escapeHtml(report.method_used || "—"),         "");

  document.getElementById("download-csv").href  = `/api/jobs/${currentJobId}/download?format=csv`;
  document.getElementById("download-xlsx").href = `/api/jobs/${currentJobId}/download?format=xlsx`;
  document.getElementById("download-pdf").href  = `/api/jobs/${currentJobId}/report.pdf`;

  setupPlotTabs(report);

  show(sections.results);
}

async function pollJobStatus() {
  const job = await (await fetch(`/api/jobs/${currentJobId}`)).json();
  updateProgress(job.progress, job.message);
  if (job.status === "completed") {
    clearInterval(pollTimer);
    await showResults();
  } else if (job.status === "failed") {
    clearInterval(pollTimer);
    updateProgress(100, job.error || t("error.unknown"));
    document.getElementById("progress-message").style.color = "var(--error)";
  }
}

async function startGeneration() {
  if (!currentJobId) return;
  setParamsDisabled(true);
  hide(sections.results);
  show(sections.progress);
  updateProgress(0, t("status.gen.start"));
  const body = {
    job_id: currentJobId,
    num_rows: parseInt(document.getElementById("num-rows").value, 10),
    target_variable: document.getElementById("target-variable").value || null,
    fast_result: document.getElementById("fast-result").checked,
    with_missing_values: document.getElementById("with-missing").checked,
    merge_with_input: document.getElementById("merge-with-input").checked,
    epochs: parseInt(document.getElementById("epochs").value, 10),
    method: document.getElementById("method").value,
  };
  const res = await fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const data = await res.json();
    return updateProgress(0, data.detail || t("status.gen.fail"));
  }
  if (pollTimer) clearInterval(pollTimer);
  pollTimer = setInterval(pollJobStatus, 1500);
  pollJobStatus();
}

function boot() {
  const input = document.getElementById("file-input");
  const drop = document.getElementById("file-drop");
  input.addEventListener("change", () => input.files[0] && uploadFile(input.files[0]));
  drop.addEventListener("dragover", (e) => { e.preventDefault(); drop.classList.add("dragover"); });
  drop.addEventListener("dragleave", () => drop.classList.remove("dragover"));
  drop.addEventListener("drop", (e) => {
    e.preventDefault();
    drop.classList.remove("dragover");
    if (e.dataTransfer.files[0]) uploadFile(e.dataTransfer.files[0]);
  });

  const epSlider = document.getElementById("epochs");
  const epInput = document.getElementById("epochs-value");
  epSlider.addEventListener("input", () => { epInput.value = epSlider.value; });
  epInput.addEventListener("change", () => {
    let v = parseInt(epInput.value, 10) || 300;
    v = Math.round(v / 50) * 50;
    v = Math.max(100, Math.min(1000, v));
    epInput.value = v;
    epSlider.value = v;
  });
  epInput.value = epSlider.value;

  document.getElementById("generate-btn").addEventListener("click", startGeneration);
  document.getElementById("fast-result").addEventListener("change", syncControls);
  document.getElementById("method").addEventListener("change", syncControls);

  syncControls();
}

window.addEventListener("beforeunload", () => {
  if (currentJobId) {
    navigator.sendBeacon(`/api/jobs/${currentJobId}/cancel`);
  }
});

if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
else boot();

})();

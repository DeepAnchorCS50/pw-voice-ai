"""
4_Evals.py — PW Voice AI
Model evaluation dashboard with 3 JS tabs:
  Tab 1: Model Performance (accuracy, P/R/F1, confusion matrix, feature importance)
  Tab 2: Conversation Quality (QA pass rate, field coverage, sample convos)
  Tab 3: Business Impact (manual vs AI comparison)
"""

import streamlit as st
import streamlit.components.v1 as components
import json, os, sys

ROOT      = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
SRC       = os.path.join(ROOT, "src")
EVAL_PATH = os.path.join(SRC, "data", "eval_metrics.json")

sys.path.insert(0, ROOT)
from ui_utils import render_nav

st.set_page_config(page_title="Evals — PW Voice AI", page_icon="📊", layout="wide")
render_nav("Evals")

@st.cache_data
def load_metrics():
    with open(EVAL_PATH) as f:
        return json.load(f)

metrics   = load_metrics()
page_data = {
    "model_performance": {
        "accuracy":       metrics["model_performance"]["cv_accuracy"],
        "correct":        metrics["model_performance"]["correct"],
        "total":          metrics["model_performance"]["total_leads"],
        "model_type":     metrics["model_performance"]["model_type"],
        "n_estimators":   metrics["model_performance"]["n_estimators"],
        "cv_folds":       metrics["model_performance"]["cv_folds"],
        "per_tier":       metrics["model_performance"]["per_tier"],
        "confusion_matrix": metrics["model_performance"]["confusion_matrix"],
        "feature_importance": metrics["model_performance"]["feature_importance"],
        "misclassified":  metrics["model_performance"]["misclassified"],
    },
    "conversation_quality": metrics["conversation_quality"],
    "business_impact":      metrics["business_impact"],
}

HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}

:root{
  --bg:#0f1117; --card:#1a1d29; --card-h:#232738; --border:#2d3148;
  --text:#e6e8f0; --muted:#8b8fa3;
  --hot:#ef4444; --warm:#f59e0b; --cold:#3b82f6;
  --success:#22c55e; --brand:#6366f1;
  --font:'Inter',sans-serif; --mono:'JetBrains Mono',monospace;
}
body{font-family:var(--font);background:var(--bg);color:var(--text);font-size:13px;height:100vh;display:flex;flex-direction:column;overflow:hidden;}

/* ── Tab bar ── */
.tab-bar{display:flex;align-items:center;background:var(--card);border-bottom:1px solid var(--border);padding:0 24px;height:44px;gap:4px;flex-shrink:0;}
.tab-btn{padding:0 16px;height:100%;display:flex;align-items:center;font-size:12px;font-weight:500;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;transition:all 150ms;gap:6px;white-space:nowrap;}
.tab-btn:hover{color:var(--text);}
.tab-btn.active{color:var(--text);border-bottom-color:var(--brand);}

/* ── Tab panels ── */
.tab-panel{display:none;flex:1;overflow-y:auto;padding:24px;}
.tab-panel.active{display:block;}

/* ── Section title ── */
.section-title{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:14px;}

/* ── Grid layouts ── */
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px;}
.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}
.grid-4{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;}
.card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:18px;}

/* ── Accuracy hero ── */
.accuracy-hero{display:flex;align-items:center;gap:24px;}
.acc-circle{position:relative;width:100px;height:100px;flex-shrink:0;}
.acc-circle svg{transform:rotate(-90deg);}
.acc-circle .acc-text{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.acc-pct{font-family:var(--mono);font-size:22px;font-weight:700;color:var(--success);}
.acc-label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;}
.acc-meta{display:flex;flex-direction:column;gap:6px;}
.acc-stat{display:flex;gap:8px;align-items:center;}
.acc-stat-label{font-size:11px;color:var(--muted);min-width:110px;}
.acc-stat-val{font-family:var(--mono);font-size:12px;color:var(--text);font-weight:500;}

/* ── P/R/F1 table ── */
.prf-table{width:100%;border-collapse:collapse;}
.prf-table th{text-align:left;font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:var(--muted);padding:8px 12px;border-bottom:1px solid var(--border);}
.prf-table td{padding:10px 12px;border-bottom:1px solid var(--border);font-size:12px;}
.prf-table tr:last-child td{border-bottom:none;}
.prf-bar-wrap{display:flex;align-items:center;gap:8px;}
.prf-bar{flex:1;height:4px;background:var(--border);border-radius:2px;min-width:60px;}
.prf-fill{height:100%;border-radius:2px;}

/* ── Confusion matrix ── */
.cm-wrap{display:flex;gap:20px;align-items:flex-start;}
.cm-grid{display:grid;grid-template-columns:auto repeat(3,1fr);grid-template-rows:auto repeat(3,1fr);gap:4px;}
.cm-header{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.6px;color:var(--muted);display:flex;align-items:center;justify-content:center;padding:4px;}
.cm-row-label{font-size:10px;font-weight:600;color:var(--muted);display:flex;align-items:center;justify-content:flex-end;padding:4px 8px;white-space:nowrap;}
.cm-cell{
  width:70px;height:70px;border-radius:8px;display:flex;flex-direction:column;
  align-items:center;justify-content:center;cursor:pointer;
  border:1px solid transparent;transition:all 150ms;
}
.cm-cell:hover{transform:scale(1.04);border-color:var(--brand);}
.cm-cell.selected{border-color:var(--brand);box-shadow:0 0 0 2px var(--brand);}
.cm-cell .cm-count{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--text);}
.cm-cell .cm-sub{font-size:9px;color:var(--muted);margin-top:2px;}
.cm-axis-label{font-size:10px;color:var(--muted);text-align:center;}
.cm-detail{flex:1;min-width:0;}
.cm-detail-title{font-size:11px;color:var(--muted);margin-bottom:10px;}
.cm-lead{background:var(--card-h);border:1px solid var(--border);border-radius:8px;padding:10px 12px;margin-bottom:8px;}
.cm-lead-name{font-size:12px;font-weight:500;color:var(--text);}
.cm-lead-reason{font-size:11px;color:var(--muted);margin-top:3px;}
.cm-lead-badges{display:flex;gap:6px;margin-top:6px;}
.cm-placeholder{font-size:11px;color:var(--muted);font-style:italic;}

/* ── Feature importance ── */
.fi-row{display:flex;align-items:center;gap:10px;margin-bottom:10px;}
.fi-label{font-size:11px;color:var(--text);min-width:140px;}
.fi-bar-wrap{flex:1;height:8px;background:var(--border);border-radius:4px;overflow:hidden;}
.fi-bar{height:100%;border-radius:4px;background:var(--brand);width:0;transition:width 1s ease;}
.fi-val{font-family:var(--mono);font-size:11px;color:var(--muted);min-width:36px;text-align:right;}

/* ── QA pass gauge ── */
.qa-gauge{display:flex;align-items:center;gap:16px;}
.qa-big{font-family:var(--mono);font-size:48px;font-weight:700;color:var(--success);}
.qa-sub{font-size:12px;color:var(--muted);}

/* ── Field coverage ── */
.fc-row{display:flex;align-items:center;gap:10px;margin-bottom:8px;}
.fc-label{font-size:11px;color:var(--text);min-width:130px;text-transform:capitalize;}
.fc-bar-wrap{flex:1;height:6px;background:var(--border);border-radius:3px;overflow:hidden;}
.fc-bar{height:100%;border-radius:3px;width:0;transition:width 1s ease;}
.fc-val{font-family:var(--mono);font-size:11px;font-weight:500;min-width:38px;text-align:right;}

/* ── Sample conversations ── */
.convo-card{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:12px;}
.convo-header{display:flex;align-items:center;justify-content:space-between;padding:12px 16px;cursor:pointer;transition:background 150ms;}
.convo-header:hover{background:var(--card-h);}
.convo-name{font-size:13px;font-weight:500;color:var(--text);}
.convo-meta{font-size:11px;color:var(--muted);margin-top:2px;}
.convo-chevron{color:var(--muted);transition:transform 200ms;font-size:14px;}
.convo-header.open .convo-chevron{transform:rotate(180deg);}
.convo-body{max-height:0;overflow:hidden;transition:max-height 300ms ease;}
.convo-body.open{max-height:400px;}
.convo-msgs{padding:12px 16px;display:flex;flex-direction:column;gap:8px;border-top:1px solid var(--border);}
.msg{display:flex;gap:10px;}
.msg-role{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;width:50px;flex-shrink:0;padding-top:2px;}
.msg-role.agent{color:var(--brand);}
.msg-role.student{color:var(--warm);}
.msg-text{font-size:11px;color:var(--text);line-height:1.5;}

/* ── Business impact ── */
.impact-compare{display:grid;grid-template-columns:1fr auto 1fr;gap:0;align-items:stretch;}
.impact-side{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:20px;}
.impact-side.ai-side{border-color:#6366f133;background:#6366f108;}
.impact-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:16px;display:flex;align-items:center;gap:6px;}
.impact-vs{display:flex;align-items:center;justify-content:center;padding:0 16px;color:var(--muted);font-size:14px;font-weight:600;}
.impact-metric{margin-bottom:16px;}
.impact-metric:last-child{margin-bottom:0;}
.im-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:4px;}
.im-val{font-family:var(--mono);font-size:22px;font-weight:700;}
.im-val.better{color:var(--success);}
.im-val.manual{color:var(--muted);}
.savings-strip{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:20px;}
.saving-card{background:var(--card);border:1px solid #22c55e33;border-radius:10px;padding:16px;text-align:center;}
.saving-pct{font-family:var(--mono);font-size:32px;font-weight:700;color:var(--success);}
.saving-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.6px;margin-top:4px;}

/* ── Stat grid ── */
.stat-card{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:16px;text-align:center;}
.stat-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:8px;}
.stat-val{font-family:var(--mono);font-size:28px;font-weight:700;color:var(--text);}
.stat-sub{font-size:10px;color:var(--muted);margin-top:4px;}

/* Tier badge */
.tier-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:700;font-family:var(--mono);}
.tb-HOT{background:#ef444418;color:var(--hot);}
.tb-WARM{background:#f59e0b18;color:var(--warm);}
.tb-COLD{background:#3b82f618;color:var(--cold);}

::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
</style>
</head>
<body>

<!-- Tab bar -->
<div class="tab-bar">
  <div class="tab-btn active" onclick="switchTab('model')"    id="tab-model">    📈 Model Performance</div>
  <div class="tab-btn"        onclick="switchTab('quality')"  id="tab-quality">  💬 Conversation Quality</div>
  <div class="tab-btn"        onclick="switchTab('impact')"   id="tab-impact">   💰 Business Impact</div>
</div>

<!-- ══════════════════════════════════════════════════════
     TAB 1: Model Performance
══════════════════════════════════════════════════════ -->
<div class="tab-panel active" id="panel-model">

  <!-- Row 1: Accuracy + P/R/F1 -->
  <div class="grid-2" style="margin-bottom:16px;">

    <!-- Accuracy card -->
    <div class="card">
      <div class="section-title">Overall Accuracy</div>
      <div class="accuracy-hero">
        <div class="acc-circle">
          <svg width="100" height="100" viewBox="0 0 100 100">
            <circle cx="50" cy="50" r="40" fill="none" stroke="#2d3148" stroke-width="8"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="#22c55e" stroke-width="8"
              stroke-dasharray="251.2" stroke-dashoffset="30.1" stroke-linecap="round" id="acc-arc"/>
          </svg>
          <div class="acc-text">
            <div class="acc-pct" id="acc-pct">88%</div>
            <div class="acc-label">CV Acc</div>
          </div>
        </div>
        <div class="acc-meta">
          <div class="acc-stat"><span class="acc-stat-label">Model Type</span><span class="acc-stat-val" id="acc-model">—</span></div>
          <div class="acc-stat"><span class="acc-stat-label">Estimators</span><span class="acc-stat-val" id="acc-est">—</span></div>
          <div class="acc-stat"><span class="acc-stat-label">CV Folds</span><span class="acc-stat-val" id="acc-folds">—</span></div>
          <div class="acc-stat"><span class="acc-stat-label">Correct / Total</span><span class="acc-stat-val" id="acc-correct">—</span></div>
          <div class="acc-stat"><span class="acc-stat-label">Test Accuracy</span><span class="acc-stat-val">86%</span></div>
        </div>
      </div>
    </div>

    <!-- P/R/F1 table -->
    <div class="card">
      <div class="section-title">Precision / Recall / F1 by Tier</div>
      <table class="prf-table">
        <thead><tr>
          <th>Tier</th><th>Precision</th><th>Recall</th><th>F1 Score</th><th>Support</th>
        </tr></thead>
        <tbody id="prf-tbody"></tbody>
      </table>
    </div>
  </div>

  <!-- Row 2: Confusion matrix + Feature importance -->
  <div class="grid-2">

    <!-- Confusion matrix -->
    <div class="card">
      <div class="section-title">Confusion Matrix — click a cell to drill down</div>
      <div style="font-size:10px;color:var(--muted);margin-bottom:10px;">Rows = Actual · Columns = Predicted</div>
      <div class="cm-wrap">
        <div>
          <div class="cm-grid" id="cm-grid"></div>
        </div>
        <div class="cm-detail" id="cm-detail">
          <div class="cm-placeholder">Click a cell to see misclassified leads</div>
        </div>
      </div>
    </div>

    <!-- Feature importance -->
    <div class="card">
      <div class="section-title">Feature Importance</div>
      <div id="fi-rows"></div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════
     TAB 2: Conversation Quality
══════════════════════════════════════════════════════ -->
<div class="tab-panel" id="panel-quality">
  <div class="grid-2" style="margin-bottom:16px;">

    <!-- QA pass rate -->
    <div class="card">
      <div class="section-title">QA Pass Rate</div>
      <div class="qa-gauge">
        <div class="qa-big" id="qa-pct">100%</div>
        <div>
          <div style="font-size:13px;font-weight:500;color:var(--text);">All conversations passed</div>
          <div class="qa-sub" id="qa-sub">— out of — conversations</div>
        </div>
      </div>
    </div>

    <!-- Stats grid -->
    <div class="grid-2">
      <div class="stat-card">
        <div class="stat-label">Avg Messages</div>
        <div class="stat-val" id="stat-msgs">—</div>
        <div class="stat-sub">per conversation</div>
      </div>
      <div class="stat-card">
        <div class="stat-label">Extraction Rate</div>
        <div class="stat-val" style="color:var(--success)" id="stat-extract">—</div>
        <div class="stat-sub">completeness</div>
      </div>
    </div>
  </div>

  <div class="grid-2">
    <!-- Field coverage -->
    <div class="card">
      <div class="section-title">Field Extraction Coverage</div>
      <div id="fc-rows"></div>
    </div>

    <!-- Sample conversations -->
    <div class="card">
      <div class="section-title">Sample Conversations</div>
      <div id="sample-convos"></div>
    </div>
  </div>
</div>

<!-- ══════════════════════════════════════════════════════
     TAB 3: Business Impact
══════════════════════════════════════════════════════ -->
<div class="tab-panel" id="panel-impact">

  <!-- Manual vs AI comparison -->
  <div class="card" style="margin-bottom:16px;">
    <div class="section-title" style="margin-bottom:16px;">Manual Scoring vs AI System</div>
    <div class="impact-compare">
      <div class="impact-side">
        <div class="impact-label">👤 Manual Process</div>
        <div class="impact-metric"><div class="im-label">Time per Lead</div><div class="im-val manual" id="bi-time-manual">—</div></div>
        <div class="impact-metric"><div class="im-label">Cost per Lead</div><div class="im-val manual" id="bi-cost-manual">—</div></div>
        <div class="impact-metric"><div class="im-label">Leads per Hour</div><div class="im-val manual" id="bi-lph-manual">—</div></div>
        <div class="impact-metric"><div class="im-label">Hours for 100 Leads</div><div class="im-val manual">20 hrs</div></div>
      </div>
      <div class="impact-vs">VS</div>
      <div class="impact-side ai-side">
        <div class="impact-label" style="color:var(--brand);">🤖 AI System</div>
        <div class="impact-metric"><div class="im-label">Time per Lead</div><div class="im-val better" id="bi-time-ai">—</div></div>
        <div class="impact-metric"><div class="im-label">Cost per Lead</div><div class="im-val better" id="bi-cost-ai">—</div></div>
        <div class="impact-metric"><div class="im-label">Leads per Hour</div><div class="im-val better" id="bi-lph-ai">—</div></div>
        <div class="impact-metric"><div class="im-label">Hours for 100 Leads</div><div class="im-val better">~4 hrs</div></div>
      </div>
    </div>
  </div>

  <!-- Savings strip -->
  <div class="savings-strip" style="margin-bottom:16px;">
    <div class="saving-card">
      <div class="saving-pct" id="bi-time-save">79%</div>
      <div class="saving-label">Time Saved</div>
    </div>
    <div class="saving-card">
      <div class="saving-pct" id="bi-cost-save">82%</div>
      <div class="saving-label">Cost Saved</div>
    </div>
    <div class="saving-card">
      <div class="saving-pct" id="bi-routing">88%</div>
      <div class="saving-label">Routing Accuracy</div>
    </div>
  </div>

  <!-- Bottom stats -->
  <div class="grid-4">
    <div class="stat-card">
      <div class="stat-label">Scale Potential</div>
      <div class="stat-val" style="font-size:22px;color:var(--brand)" id="bi-scale">—</div>
      <div class="stat-sub">without extra headcount</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Human Hours Saved</div>
      <div class="stat-val" style="font-size:22px;color:var(--success)" id="bi-hours">—</div>
      <div class="stat-sub">per 100 leads</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Misrouted Leads Saved</div>
      <div class="stat-val" style="font-size:22px;color:var(--warm)" id="bi-misrouted">—</div>
      <div class="stat-sub">per 100 leads</div>
    </div>
    <div class="stat-card">
      <div class="stat-label">Speed Increase</div>
      <div class="stat-val" style="font-size:22px;color:var(--success)">4.8×</div>
      <div class="stat-sub">leads per hour</div>
    </div>
  </div>
</div>

<script>
window.pageData = __PAGE_DATA__;
const D = window.pageData;
const MP = D.model_performance;
const CQ = D.conversation_quality;
const BI = D.business_impact;

// ── Tab switching ──
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('tab-'   + name).classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
}

// ══════════════════════════════════════════
// TAB 1: Model Performance
// ══════════════════════════════════════════

// Accuracy
document.getElementById('acc-pct').textContent     = Math.round(MP.accuracy * 100) + '%';
document.getElementById('acc-model').textContent   = MP.model_type;
document.getElementById('acc-est').textContent     = MP.n_estimators;
document.getElementById('acc-folds').textContent   = MP.cv_folds + '-fold';
document.getElementById('acc-correct').textContent = MP.correct + ' / ' + MP.total;

// Animate arc: circumference = 2π×40 = 251.2
const arc = document.getElementById('acc-arc');
const offset = 251.2 * (1 - MP.accuracy);
setTimeout(() => { arc.style.transition = 'stroke-dashoffset 1s ease'; arc.style.strokeDashoffset = offset; }, 300);

// P/R/F1 table
const TIER_COLOR = { HOT:'var(--hot)', WARM:'var(--warm)', COLD:'var(--cold)' };
const prfTbody = document.getElementById('prf-tbody');
['HOT','WARM','COLD'].forEach(tier => {
  const t = MP.per_tier[tier];
  const c = TIER_COLOR[tier];
  const tr = document.createElement('tr');
  tr.innerHTML = `
    <td><span style="color:${c};font-weight:600">${tier}</span></td>
    <td>
      <div class="prf-bar-wrap">
        <span style="font-family:var(--mono);min-width:32px">${(t.precision*100).toFixed(0)}%</span>
        <div class="prf-bar"><div class="prf-fill" style="width:${t.precision*100}%;background:${c}" class="prf-anim"></div></div>
      </div>
    </td>
    <td>
      <div class="prf-bar-wrap">
        <span style="font-family:var(--mono);min-width:32px">${(t.recall*100).toFixed(0)}%</span>
        <div class="prf-bar"><div class="prf-fill" style="width:${t.recall*100}%;background:${c}"></div></div>
      </div>
    </td>
    <td>
      <div class="prf-bar-wrap">
        <span style="font-family:var(--mono);min-width:32px">${(t.f1*100).toFixed(0)}%</span>
        <div class="prf-bar"><div class="prf-fill" style="width:${t.f1*100}%;background:${c}"></div></div>
      </div>
    </td>
    <td style="color:var(--muted);font-family:var(--mono)">${t.support}</td>`;
  prfTbody.appendChild(tr);
});

// Confusion matrix
const TIERS = ['HOT','WARM','COLD'];
const cmGrid = document.getElementById('cm-grid');

// Top-left empty corner
const corner = document.createElement('div');
corner.style.cssText='grid-column:1;grid-row:1;display:flex;align-items:center;justify-content:center;';
const predLabel = document.createElement('div');
predLabel.style.cssText='font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.6px;transform:none;';
predLabel.textContent='';
corner.appendChild(predLabel);
cmGrid.appendChild(corner);

// Column headers (Predicted)
TIERS.forEach(t => {
  const h = document.createElement('div');
  h.className = 'cm-header';
  h.innerHTML = `<span style="color:${TIER_COLOR[t]};font-size:10px">${t}</span>`;
  cmGrid.appendChild(h);
});

// Rows (Actual)
const maxCount = 34;
TIERS.forEach(actualTier => {
  // Row label
  const rl = document.createElement('div');
  rl.className = 'cm-row-label';
  rl.innerHTML = `<span style="color:${TIER_COLOR[actualTier]}">${actualTier}</span>`;
  cmGrid.appendChild(rl);

  // Cells
  TIERS.forEach(predTier => {
    const count    = MP.confusion_matrix[actualTier][predTier];
    const isCorrect = actualTier === predTier;
    const intensity = count / maxCount;
    const bg = isCorrect
      ? `rgba(34,197,94,${0.08 + intensity * 0.3})`
      : `rgba(239,68,68,${0.04 + intensity * 0.25})`;
    const border = isCorrect ? '#22c55e33' : '#ef444422';

    const cell = document.createElement('div');
    cell.className = 'cm-cell';
    cell.style.cssText = `background:${bg};border-color:${border};`;
    cell.innerHTML = `<div class="cm-count">${count}</div><div class="cm-sub">${actualTier}→${predTier}</div>`;

    cell.onclick = () => selectCmCell(actualTier, predTier, cell, count, isCorrect);
    cmGrid.appendChild(cell);
  });
});

// Axis labels
const axisRow = document.createElement('div');
axisRow.style.cssText='grid-column:1/-1;display:flex;justify-content:center;margin-top:6px;';
axisRow.innerHTML='<span style="font-size:9px;color:var(--muted)">↑ Actual (rows) &nbsp;|&nbsp; Predicted (columns) →</span>';
cmGrid.appendChild(axisRow);

function selectCmCell(actual, pred, cell, count, isCorrect) {
  document.querySelectorAll('.cm-cell').forEach(c => c.classList.remove('selected'));
  cell.classList.add('selected');

  const det = document.getElementById('cm-detail');
  if (isCorrect) {
    det.innerHTML = `<div class="cm-detail-title" style="color:var(--success)">✓ Correctly classified as ${actual}</div>
      <div class="cm-placeholder">${count} leads correctly identified — no misclassification to show.</div>`;
    return;
  }

  const key = actual + '_as_' + pred;
  const mLeads = MP.misclassified[key] || [];
  if (!mLeads.length) {
    det.innerHTML = `<div class="cm-detail-title">Actual: ${actual} → Predicted: ${pred}</div>
      <div class="cm-placeholder">No examples stored for this cell.</div>`;
    return;
  }

  let html = `<div class="cm-detail-title" style="color:var(--hot)">Actual: <span style="color:${TIER_COLOR[actual]}">${actual}</span> → Predicted: <span style="color:${TIER_COLOR[pred]}">${pred}</span></div>`;
  mLeads.forEach(l => {
    html += `<div class="cm-lead">
      <div class="cm-lead-name">${l.name}</div>
      <div class="cm-lead-reason">${l.reason}</div>
      <div class="cm-lead-badges">
        <span class="tier-badge tb-${l.true_tier}">True: ${l.true_tier}</span>
        <span class="tier-badge tb-${l.pred_tier}">Pred: ${l.pred_tier}</span>
        <span style="font-family:var(--mono);font-size:10px;color:var(--muted)">Score: ${l.score}</span>
      </div>
    </div>`;
  });
  det.innerHTML = html;
}

// Feature importance
const fiRows = document.getElementById('fi-rows');
MP.feature_importance.forEach(f => {
  const pct = Math.round(f.importance * 100);
  const div = document.createElement('div');
  div.className = 'fi-row';
  div.innerHTML = `
    <div class="fi-label">${f.label}</div>
    <div class="fi-bar-wrap"><div class="fi-bar" id="fi-${f.feature}"></div></div>
    <div class="fi-val">${pct}%</div>`;
  fiRows.appendChild(div);
});
setTimeout(() => {
  MP.feature_importance.forEach(f => {
    const el = document.getElementById('fi-' + f.feature);
    if (el) el.style.width = Math.round(f.importance * 100) + '%';
  });
}, 400);

// ══════════════════════════════════════════
// TAB 2: Conversation Quality
// ══════════════════════════════════════════

document.getElementById('qa-pct').textContent  = Math.round(CQ.qa_pass_rate * 100) + '%';
document.getElementById('qa-sub').textContent  = CQ.total_conversations + ' of ' + CQ.total_conversations + ' conversations';
document.getElementById('stat-msgs').textContent    = CQ.avg_messages;
document.getElementById('stat-extract').textContent = Math.round(CQ.extraction_completeness * 100) + '%';

// Field coverage bars
const fcRows = document.getElementById('fc-rows');
Object.entries(CQ.field_coverage).forEach(([field, val]) => {
  const pct = Math.round(val * 100);
  const color = pct >= 97 ? 'var(--success)' : pct >= 92 ? 'var(--warm)' : 'var(--hot)';
  const div = document.createElement('div');
  div.className = 'fc-row';
  div.innerHTML = `
    <div class="fc-label">${field.replace('_',' ')}</div>
    <div class="fc-bar-wrap"><div class="fc-bar" id="fc-${field}" style="background:${color}"></div></div>
    <div class="fc-val" style="color:${color}">${pct}%</div>`;
  fcRows.appendChild(div);
});
setTimeout(() => {
  Object.entries(CQ.field_coverage).forEach(([field, val]) => {
    const el = document.getElementById('fc-' + field);
    if (el) el.style.width = Math.round(val * 100) + '%';
  });
}, 400);

// Sample conversations
const convoWrap = document.getElementById('sample-convos');
CQ.sample_conversations.forEach((c, i) => {
  const msgs = c.messages.map(m => `
    <div class="msg">
      <div class="msg-role ${m.role.toLowerCase()}">${m.role}</div>
      <div class="msg-text">${m.text}</div>
    </div>`).join('');
  const div = document.createElement('div');
  div.className = 'convo-card';
  div.innerHTML = `
    <div class="convo-header" id="ch-${i}" onclick="toggleConvo(${i})">
      <div>
        <div class="convo-name">${c.name} <span class="tier-badge tb-${c.tier}" style="margin-left:6px">${c.tier}</span></div>
        <div class="convo-meta">${c.city} · ${c.exam}</div>
      </div>
      <div class="convo-chevron">▼</div>
    </div>
    <div class="convo-body" id="cb-${i}">
      <div class="convo-msgs">${msgs}</div>
    </div>`;
  convoWrap.appendChild(div);
});

function toggleConvo(i) {
  const hdr  = document.getElementById('ch-' + i);
  const body = document.getElementById('cb-' + i);
  hdr.classList.toggle('open');
  body.classList.toggle('open');
}

// ══════════════════════════════════════════
// TAB 3: Business Impact
// ══════════════════════════════════════════

document.getElementById('bi-time-manual').textContent = BI.time_per_lead_manual;
document.getElementById('bi-time-ai').textContent     = BI.time_per_lead_ai;
document.getElementById('bi-cost-manual').textContent = BI.cost_per_lead_manual;
document.getElementById('bi-cost-ai').textContent     = BI.cost_per_lead_ai;
document.getElementById('bi-lph-manual').textContent  = BI.leads_per_hour_manual + '/hr';
document.getElementById('bi-lph-ai').textContent      = BI.leads_per_hour_ai + '/hr';
document.getElementById('bi-time-save').textContent   = BI.time_savings_pct;
document.getElementById('bi-cost-save').textContent   = BI.cost_savings_pct;
document.getElementById('bi-routing').textContent     = BI.routing_accuracy;
document.getElementById('bi-scale').textContent       = BI.scale_potential;
document.getElementById('bi-hours').textContent       = BI.human_hours_saved_per_100;
document.getElementById('bi-misrouted').textContent   = BI.misrouted_leads_saved;
</script>
</body>
</html>"""

page_html = HTML.replace('__PAGE_DATA__', json.dumps(page_data))
components.html(page_html, height=900, scrolling=False)

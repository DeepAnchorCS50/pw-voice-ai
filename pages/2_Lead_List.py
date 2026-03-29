"""
2_Lead_List.py — PW Voice AI
Filterable lead table with accordion row detail
Layer 1: Searchable/filterable table (tier, city, exam, name search)
Layer 2: Click row → accordion expands with score breakdown, snippet, actions
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, sys, random, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC      = os.path.join(ROOT, "src")
CSV_PATH = os.path.join(SRC, "data", "synthetic_leads_dataset.csv")

sys.path.insert(0, ROOT)
from ui_utils import render_nav, HIDE_STREAMLIT_CSS

st.set_page_config(page_title="Lead List — PW Voice AI", page_icon="📋", layout="wide")
render_nav("Lead List")

@st.cache_data
def load_leads():
    import random as rnd
    rnd.seed(42)
    df = pd.read_csv(CSV_PATH)

    SNIPPETS = {
        'HOT': [
            [{'role':'Agent','text':'Namaste! Main Priya bol rahi hoon PhysicsWallah se. Aapka JEE preparation kaisa chal raha hai?'},
             {'role':'Student','text':'Bilkul theek hai. Main seriously prepare kar raha hoon — Kota shift hona tha but online better lagta hai.'},
             {'role':'Agent','text':'Hamare Arjuna batch mein top faculty hain, Pankaj sir personally doubt sessions lete hain.'},
             {'role':'Student','text':'Fees kitni hai full course ki? Aur installment option hai kya?'}],
            [{'role':'Agent','text':'Hello! Calling from PhysicsWallah regarding your JEE Advanced inquiry.'},
             {'role':'Student','text':'Yes, I have been following PW for a long time. I want to know about Arjuna batch.'},
             {'role':'Agent','text':'Arjuna is our flagship JEE Advanced program with live classes and daily doubt sessions.'},
             {'role':'Student','text':'My father wants to know — is there any instalment option for the fee?'}],
        ],
        'WARM': [
            [{'role':'Agent','text':'Hello! Calling from PhysicsWallah regarding your NEET preparation inquiry.'},
             {'role':'Student','text':'Yes, I had checked the website. I am in class 11 right now.'},
             {'role':'Agent','text':'Perfect timing. Our Yakeen batch is designed for class 11 students starting early.'},
             {'role':'Student','text':'Sounds good but I need to discuss with my parents first before deciding.'}],
            [{'role':'Agent','text':'Namaste! PhysicsWallah ki taraf se call. NEET 2027 ke liye prepare kar rahe hain?'},
             {'role':'Student','text':'Haan, but main ek aur coaching bhi dekh raha hoon. Compare karna hai.'},
             {'role':'Agent','text':'Bilkul sahi approach hai. Hum aapko free trial access de sakte hain — ek week dekh lijiye.'},
             {'role':'Student','text':'Theek hai, trial access milta hai to zaroor dekhta hoon.'}],
        ],
        'COLD': [
            [{'role':'Agent','text':'Namaste! PhysicsWallah ki taraf se call. JEE preparation ke baare mein inquiry thi?'},
             {'role':'Student','text':'Haan, but abhi main class 9 mein hoon. Thoda jaldi hai shayad.'},
             {'role':'Agent','text':'Foundation batch bhi offer karte hain class 9-10 ke liye — bilkul sahi shuruat.'},
             {'role':'Student','text':'Main papa se baat karke bataunga. Budget bhi dekhna hoga.'}],
            [{'role':'Agent','text':'Hello! PhysicsWallah calling. Were you looking for JEE preparation guidance?'},
             {'role':'Student','text':'I was just browsing. Not sure yet if I want to take coaching.'},
             {'role':'Agent','text':'Understood. Can I share some information about our free content on YouTube?'},
             {'role':'Student','text':'Sure, send it on WhatsApp. I will have a look when I get time.'}],
        ],
    }

    STAGE_COUNTS = {
        'HOT':  {'Senior Sales Assigned':9,'Parent Discussion':8,'Enrollment Pending':6,'Enrolled':4,'Dropped':3},
        'WARM': {'Follow-up Scheduled':11,'Info Sent':8,'Re-engaged':6,'Enrolled':3,'Nurture Pool':3},
        'COLD': {'Drip Campaign':13,'Nurture Pool':14,'Disqualified':3},
    }
    stage_pools = {}
    for tier, stages in STAGE_COUNTS.items():
        pool = []
        for stage, count in stages.items():
            pool.extend([stage]*count)
        rnd.shuffle(pool)
        stage_pools[tier] = pool

    tier_idx = {'HOT':0,'WARM':0,'COLD':0}
    base_date = datetime.date(2026, 3, 1)

    leads = []
    for _, row in df.iterrows():
        tier  = row['tier_label']
        idx   = tier_idx[tier]
        stage = stage_pools[tier][idx % len(stage_pools[tier])]
        tier_idx[tier] += 1
        days_ago  = rnd.randint(0, 13)
        call_date = (base_date - datetime.timedelta(days=days_ago)).strftime('%b %d')
        call_type = 'Inbound' if rnd.random() > 0.4 else 'Outbound'
        conv_path = os.path.join(SRC, 'data', 'conversations', f"{row['conversation_id']}.json")
        if os.path.exists(conv_path):
            with open(conv_path, encoding='utf-8') as cf:
                conv = json.load(cf)
            snippet = [{'role': m['speaker'].capitalize(), 'text': m['text']}
                       for m in conv.get('messages', [])]
        else:
            snippet = rnd.choice(SNIPPETS[tier])
        score     = int(row['score'])
        leads.append({
            'id':             row['conversation_id'],
            'name':           str(row['full_name']) if pd.notna(row['full_name']) else 'Student',
            'class':          str(row['current_class']),
            'exam':           str(row['target_exam']),
            'exam_year':      str(row['exam_year']),
            'city':           str(row['location']),
            'tier':           tier,
            'score':          score,
            'stage':          stage,
            'engagement':     str(row['engagement_level']),
            'budget_concern': str(row['budget_concern']),
            'decision_maker': str(row['decision_maker']),
            'urgency':        str(row['urgency_level']),
            'date':           call_date,
            'call_type':      call_type,
            'rule_score':     min(100, max(0, score + rnd.randint(-8, 8))),
            'ml_score':       score,
            'qa_score':       int(row['qa_score']),
            'snippet':        snippet,
            'action_slack':   tier == 'HOT',
            'action_email':   tier in ('HOT', 'WARM'),
            'action_crm':     True,
            'is_new':         False,
        })
    return leads

leads     = load_leads()
hot_count = sum(1 for l in leads if l['tier']=='HOT')
warm_count= sum(1 for l in leads if l['tier']=='WARM')
cold_count= sum(1 for l in leads if l['tier']=='COLD')

# ── Inject demo results if arriving from Operations via View Results ───────────
if st.query_params.get("pw_synced") == "1":
    import glob
    DEMO_DIR = os.path.join(SRC, "data", "demo_calls")
    calls_count = int(st.query_params.get("pw_calls", 0))
    call_files = sorted(glob.glob(os.path.join(DEMO_DIR, "*.json")))[:calls_count]
    new_leads = []
    for jf in call_files:
        try:
            with open(jf) as f:
                cd = json.load(f)
            s = cd.get("student", {})
            new_leads.append({
                'id':             cd.get("call_id", "demo"),
                'name':           s.get("name", "Student"),
                'class':          s.get("class", "12"),
                'exam':           s.get("exam", "JEE"),
                'exam_year':      "2026",
                'city':           s.get("city", "—"),
                'tier':           cd.get("tier", "WARM"),
                'score':          cd.get("ml_score", 50),
                'stage':          {"HOT":"Senior Sales Assigned","WARM":"Follow-up Scheduled","COLD":"Drip Campaign"}.get(cd.get("tier","WARM"),"—"),
                'engagement':     cd.get("extracted_fields", {}).get("engagement_level", "medium"),
                'budget_concern': str(cd.get("extracted_fields", {}).get("budget_concern", False)),
                'decision_maker': cd.get("extracted_fields", {}).get("decision_maker", "self"),
                'urgency':        "high" if cd.get("tier") == "HOT" else "medium",
                'date':           "Today",
                'call_type':      cd.get("call_type", "outbound").capitalize(),
                'rule_score':     cd.get("rule_based_score", 50),
                'ml_score':       cd.get("ml_score", 50),
                'qa_score':       95,
                'snippet':        [{'role': m['speaker'].capitalize(), 'text': m['text']} for m in cd.get("transcript", [])[:4]],
                'action_slack':   cd.get("tier") == "HOT",
                'action_email':   cd.get("tier") in ("HOT", "WARM"),
                'action_crm':     True,
                'is_new':         True,
            })
        except Exception:
            pass
    if new_leads:
        leads = new_leads + leads
        hot_count  += sum(1 for l in new_leads if l['tier']=='HOT')
        warm_count += sum(1 for l in new_leads if l['tier']=='WARM')
        cold_count += sum(1 for l in new_leads if l['tier']=='COLD')

cities = sorted(set(l['city'] for l in leads if l['city'] != 'unknown'))
exams  = sorted(set(l['exam'] for l in leads))
stages = sorted(set(l['stage'] for l in leads))

page_data = {
    "leads":       leads,
    "tier_counts": {"hot": hot_count, "warm": warm_count, "cold": cold_count},
    "filters": {
        "tiers":  ["HOT", "WARM", "COLD"],
        "cities": cities,
        "exams":  exams,
        "stages": stages,
    }
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

/* Summary cards */
.summary{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);border-bottom:1px solid var(--border);}
.sum-card{background:var(--card);padding:14px 20px;display:flex;align-items:center;gap:14px;}
.sum-icon{width:36px;height:36px;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:16px;flex-shrink:0;}
.sum-label{font-size:10px;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-bottom:3px;}
.sum-val{font-family:var(--mono);font-size:22px;font-weight:700;}
.sum-sub{font-size:10px;color:var(--muted);margin-top:1px;}
.ic-hot {background:#ef444418;} .ic-warm{background:#f59e0b18;} .ic-cold{background:#3b82f618;} .ic-total{background:#6366f118;}

/* Filter bar */
.filter-bar{display:flex;align-items:center;gap:8px;padding:10px 20px;border-bottom:1px solid var(--border);background:var(--card);flex-wrap:wrap;}
.filter-bar input,.filter-bar select{
  background:var(--bg); border:1px solid var(--border); border-radius:6px;
  color:var(--text); font-family:var(--font); font-size:12px; padding:6px 10px;
  outline:none; transition:border-color 150ms;
}
.filter-bar input:focus,.filter-bar select:focus{border-color:var(--brand);}
.filter-bar input{width:200px;}
.filter-bar select{min-width:110px; cursor:pointer;}
.filter-bar select option{background:var(--card);}
.filter-label{font-size:11px;color:var(--muted);white-space:nowrap;}
.filter-sep{flex:1;}
.result-count{font-size:11px;color:var(--muted);font-family:var(--mono);background:var(--bg);border:1px solid var(--border);padding:4px 10px;border-radius:10px;}
.clear-btn{font-size:11px;color:var(--muted);background:var(--card-h);border:1px solid var(--border);border-radius:6px;padding:5px 10px;cursor:pointer;transition:all 150ms;}
.clear-btn:hover{color:var(--text);border-color:var(--brand);}

/* Table */
.table-wrap{flex:1;overflow-y:auto;}
table{width:100%;border-collapse:collapse;}
thead{position:sticky;top:0;z-index:10;}
th{
  background:var(--card);text-align:left;
  font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;
  color:var(--muted);padding:10px 16px;border-bottom:1px solid var(--border);
  cursor:pointer;user-select:none;white-space:nowrap;
}
th:hover{color:var(--text);}
th.sorted{color:var(--text);}
th .si{margin-left:4px;opacity:0.4;}
th.sorted .si{opacity:1;}
td{padding:10px 16px;border-bottom:1px solid var(--border);vertical-align:middle;}
tr.lead-row{cursor:pointer;transition:background 120ms;}
tr.lead-row:hover td{background:#1a1d2988;}
tr.lead-row.expanded td{background:var(--card);border-bottom:none;}

/* Tier badge */
.tier-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:700;font-family:var(--mono);letter-spacing:0.3px;}
.tb-HOT {background:#ef444418;color:var(--hot);}
.tb-WARM{background:#f59e0b18;color:var(--warm);}
.tb-COLD{background:#3b82f618;color:var(--cold);}

/* Score bar */
.score-wrap{display:flex;align-items:center;gap:7px;}
.score-bar{flex:1;height:4px;background:var(--border);border-radius:2px;min-width:60px;}
.score-fill{height:100%;border-radius:2px;}

/* Call type badge */
.call-badge{font-size:9px;padding:2px 7px;border-radius:4px;border:1px solid var(--border);color:var(--muted);}
.new-badge{font-size:9px;font-weight:700;background:#6366f118;color:var(--brand);border:1px solid #6366f133;padding:1px 6px;border-radius:8px;margin-left:6px;vertical-align:middle;}

/* Accordion detail row */
tr.detail-row td{padding:0;border-bottom:1px solid var(--border);}
.detail-inner{
  overflow:hidden; max-height:0;
  transition:max-height 300ms ease;
  background:var(--bg);
}
.detail-inner.open{max-height:600px;overflow-y:auto;}
.detail-content{padding:20px 24px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px;}

.detail-section-title{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:10px;}

/* Score breakdown */
.score-cards{display:flex;gap:8px;}
.score-card{flex:1;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px;text-align:center;}
.sc-label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:4px;}
.sc-val{font-family:var(--mono);font-size:22px;font-weight:700;}

.field-row{display:flex;justify-content:space-between;align-items:center;padding:5px 0;border-bottom:1px solid var(--border);}
.field-row:last-child{border-bottom:none;}
.field-key{font-size:11px;color:var(--muted);text-transform:capitalize;}
.field-val{font-size:11px;color:var(--text);font-weight:500;}

/* Conversation snippet */
.snippet{background:var(--card);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px;max-height:300px;overflow-y:auto;}
.msg{display:flex;gap:8px;}
.msg-role{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;width:46px;flex-shrink:0;padding-top:2px;}
.msg-role.agent{color:var(--brand);}
.msg-role.student{color:var(--warm);}
.msg-text{font-size:11px;color:var(--text);line-height:1.5;}

/* Actions */
.actions{display:flex;gap:6px;flex-wrap:wrap;margin-top:6px;}
.action-chip{display:flex;align-items:center;gap:5px;padding:5px 10px;border-radius:6px;font-size:10px;font-weight:500;border:1px solid;}
.ac-done{background:#22c55e14;border-color:#22c55e33;color:var(--success);}
.ac-skip{background:var(--card);border-color:var(--border);color:var(--muted);}

/* Stage timeline */
.stage-wrap{margin-top:6px;}
.stage-pill{display:inline-block;background:var(--card);border:1px solid var(--border);border-radius:20px;padding:4px 12px;font-size:11px;color:var(--text);}

/* Empty state */
.empty-state{padding:60px;text-align:center;color:var(--muted);}
.empty-icon{font-size:32px;margin-bottom:12px;}

::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}
</style>
</head>
<body>

<!-- Summary cards -->
<div class="summary">
  <div class="sum-card">
    <div class="sum-icon ic-total">📋</div>
    <div><div class="sum-label">Total Leads</div><div class="sum-val" id="s-total">100</div><div class="sum-sub">in pipeline</div></div>
  </div>
  <div class="sum-card">
    <div class="sum-icon ic-hot">🔥</div>
    <div><div class="sum-label">HOT</div><div class="sum-val" id="s-hot" style="color:var(--hot)">__HOT__</div><div class="sum-sub">high intent</div></div>
  </div>
  <div class="sum-card">
    <div class="sum-icon ic-warm">🔶</div>
    <div><div class="sum-label">WARM</div><div class="sum-val" id="s-warm" style="color:var(--warm)">__WARM__</div><div class="sum-sub">nurturing</div></div>
  </div>
  <div class="sum-card">
    <div class="sum-icon ic-cold">❄️</div>
    <div><div class="sum-label">COLD</div><div class="sum-val" id="s-cold" style="color:var(--cold)">__COLD__</div><div class="sum-sub">low intent</div></div>
  </div>
</div>

<!-- Filter bar -->
<div class="filter-bar">
  <span class="filter-label">Filter:</span>
  <input type="text" id="search" placeholder="Search by name..." oninput="applyFilters()">
  <select id="f-tier" onchange="applyFilters()">
    <option value="">All Tiers</option>
    <option>HOT</option><option>WARM</option><option>COLD</option>
  </select>
  <select id="f-exam" onchange="applyFilters()">
    <option value="">All Exams</option>
    __EXAM_OPTIONS__
  </select>
  <select id="f-city" onchange="applyFilters()">
    <option value="">All Cities</option>
    __CITY_OPTIONS__
  </select>
  <select id="f-stage" onchange="applyFilters()">
    <option value="">All Stages</option>
    __STAGE_OPTIONS__
  </select>
  <div class="filter-sep"></div>
  <span class="result-count" id="result-count">100 leads</span>
  <div class="clear-btn" onclick="clearFilters()">Clear filters</div>
</div>

<!-- Table -->
<div class="table-wrap">
  <table>
    <thead>
      <tr>
        <th onclick="sortBy('name')">Name <span class="si">↕</span></th>
        <th onclick="sortBy('city')">City <span class="si">↕</span></th>
        <th onclick="sortBy('class')">Class <span class="si">↕</span></th>
        <th onclick="sortBy('exam')">Exam <span class="si">↕</span></th>
        <th onclick="sortBy('score')">ML Score <span class="si">↕</span></th>
        <th onclick="sortBy('tier')">Tier <span class="si">↕</span></th>
        <th onclick="sortBy('stage')">Stage <span class="si">↕</span></th>
        <th onclick="sortBy('call_type')">Call Type <span class="si">↕</span></th>
        <th onclick="sortBy('date')">Date <span class="si">↕</span></th>
      </tr>
    </thead>
    <tbody id="tbody"></tbody>
  </table>
  <div class="empty-state" id="empty-state" style="display:none">
    <div class="empty-icon">🔍</div>
    <div>No leads match your filters</div>
  </div>
</div>

<script>
window.pageData = __PAGE_DATA__;
const D = window.pageData;
let filtered     = [...D.leads];
let sortField    = 'score';
let sortAsc      = false;
let expandedId   = null;

// ── Filters ──
function applyFilters() {
  const search = document.getElementById('search').value.toLowerCase();
  const tier   = document.getElementById('f-tier').value;
  const exam   = document.getElementById('f-exam').value;
  const city   = document.getElementById('f-city').value;
  const stage  = document.getElementById('f-stage').value;

  filtered = D.leads.filter(l =>
    (!search || l.name.toLowerCase().includes(search)) &&
    (!tier   || l.tier  === tier) &&
    (!exam   || l.exam  === exam) &&
    (!city   || l.city  === city) &&
    (!stage  || l.stage === stage)
  );

  // Update summary cards
  const h = filtered.filter(l=>l.tier==='HOT').length;
  const w = filtered.filter(l=>l.tier==='WARM').length;
  const c = filtered.filter(l=>l.tier==='COLD').length;
  document.getElementById('s-total').textContent = filtered.length;
  document.getElementById('s-hot').textContent   = h;
  document.getElementById('s-warm').textContent  = w;
  document.getElementById('s-cold').textContent  = c;
  document.getElementById('result-count').textContent = filtered.length + ' lead' + (filtered.length!==1?'s':'');

  expandedId = null;
  renderTable();
}

function clearFilters() {
  document.getElementById('search').value   = '';
  document.getElementById('f-tier').value   = '';
  document.getElementById('f-exam').value   = '';
  document.getElementById('f-city').value   = '';
  document.getElementById('f-stage').value  = '';
  applyFilters();
}

// ── Sort ──
function sortBy(field) {
  if (sortField === field) sortAsc = !sortAsc;
  else { sortField = field; sortAsc = true; }

  document.querySelectorAll('th').forEach(th => { th.classList.remove('sorted'); th.querySelector('.si').textContent='↕'; });
  const th = document.querySelector(`th[onclick="sortBy('${field}')"]`);
  if (th) { th.classList.add('sorted'); th.querySelector('.si').textContent = sortAsc?'↑':'↓'; }
  renderTable();
}

// ── Render ──
function renderTable() {
  const rows = [...filtered].sort((a,b) => {
    let av=a[sortField], bv=b[sortField];
    if (typeof av==='string') av=av.toLowerCase();
    if (typeof bv==='string') bv=bv.toLowerCase();
    return sortAsc ? (av>bv?1:-1) : (av<bv?1:-1);
  });

  const tbody = document.getElementById('tbody');
  tbody.innerHTML = '';

  if (rows.length === 0) {
    document.getElementById('empty-state').style.display='block';
    return;
  }
  document.getElementById('empty-state').style.display='none';

  rows.forEach(lead => {
    const scoreColor = lead.score>=68?'var(--hot)': lead.score>=48?'var(--warm)':'var(--cold)';
    // flip: HOT=green, WARM=amber, COLD=red
    const sc = lead.tier==='HOT'?'var(--success)':lead.tier==='WARM'?'var(--warm)':'var(--muted)';

    // Main row
    const tr = document.createElement('tr');
    tr.className = 'lead-row' + (expandedId===lead.id?' expanded':'');
    tr.dataset.id = lead.id;
    tr.onclick = () => toggleDetail(lead.id);
    tr.innerHTML = `
      <td style="font-weight:500">${lead.name}${lead.is_new ? ' <span class="new-badge">🆕 New</span>' : ''}</td>
      <td style="color:var(--muted)">${lead.city}</td>
      <td>Class ${lead.class}</td>
      <td><span style="font-size:10px;background:var(--card-h);padding:2px 8px;border-radius:4px">${lead.exam}</span></td>
      <td>
        <div class="score-wrap">
          <span style="font-family:var(--mono);font-weight:600;color:${sc};min-width:24px">${lead.score}</span>
          <div class="score-bar"><div class="score-fill" style="width:${lead.score}%;background:${sc}"></div></div>
        </div>
      </td>
      <td><span class="tier-badge tb-${lead.tier}">${lead.tier}</span></td>
      <td style="color:var(--muted);font-size:11px">${lead.stage}</td>
      <td><span class="call-badge">${lead.call_type}</span></td>
      <td style="color:var(--muted);font-family:var(--mono);font-size:11px">${lead.date}</td>`;
    tbody.appendChild(tr);

    // Detail row
    const dm_label = {'self':'Self','parent_present':'Parent Present','parent_later':'Parent Later'};
    const scoreColor2 = lead.tier==='HOT'?'var(--success)':lead.tier==='WARM'?'var(--warm)':'var(--muted)';

    const snippetHtml = lead.snippet.map(m=>`
      <div class="msg">
        <div class="msg-role ${m.role.toLowerCase()}">${m.role}</div>
        <div class="msg-text">${m.text}</div>
      </div>`).join('');

    const detailTr = document.createElement('tr');
    detailTr.className = 'detail-row';
    detailTr.dataset.for = lead.id;
    detailTr.innerHTML = `<td colspan="9">
      <div class="detail-inner ${expandedId===lead.id?'open':''}" id="di-${lead.id}">
        <div class="detail-content">

          <!-- Col 1: Score breakdown + profile fields -->
          <div>
            <div class="detail-section-title">Score Breakdown</div>
            <div class="score-cards">
              <div class="score-card">
                <div class="sc-label">Rule-Based</div>
                <div class="sc-val" style="color:var(--muted)">${lead.rule_score}</div>
              </div>
              <div class="score-card">
                <div class="sc-label">ML Model</div>
                <div class="sc-val" style="color:${scoreColor2}">${lead.ml_score}</div>
              </div>
            </div>
            <div style="margin-top:14px">
              <div class="detail-section-title">Profile</div>
              <div class="field-row"><span class="field-key">Engagement</span><span class="field-val" style="text-transform:capitalize">${lead.engagement}</span></div>
              <div class="field-row"><span class="field-key">Budget Concern</span><span class="field-val">${lead.budget_concern==='TRUE'?'⚠️ Yes':'✅ No'}</span></div>
              <div class="field-row"><span class="field-key">Decision Maker</span><span class="field-val">${dm_label[lead.decision_maker]||lead.decision_maker}</span></div>
              <div class="field-row"><span class="field-key">Urgency</span><span class="field-val" style="text-transform:capitalize">${lead.urgency}</span></div>
              <div class="field-row"><span class="field-key">Exam Year</span><span class="field-val">${lead.exam_year}</span></div>
              <div class="field-row"><span class="field-key">QA Score</span><span class="field-val">${lead.qa_score}%</span></div>
            </div>
          </div>

          <!-- Col 2: Conversation -->
          <div>
            <div class="detail-section-title">Conversation Preview</div>
            <div class="snippet">${snippetHtml}</div>
          </div>

          <!-- Col 3: Stage + Actions -->
          <div>
            <div class="detail-section-title">Pipeline Stage</div>
            <div class="stage-pill">${lead.stage}</div>
            <div style="margin-top:16px">
              <div class="detail-section-title">Actions Triggered</div>
              <div class="actions">
                <div class="action-chip ${lead.action_slack?'ac-done':'ac-skip'}">${lead.action_slack?'✓':'–'} Slack</div>
                <div class="action-chip ${lead.action_email?'ac-done':'ac-skip'}">${lead.action_email?'✓':'–'} Email</div>
                <div class="action-chip ac-done">✓ CRM Updated</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </td>`;
    tbody.appendChild(detailTr);
  });
}

// ── Accordion toggle ──
function toggleDetail(id) {
  if (expandedId === id) {
    // Close
    document.getElementById('di-' + id)?.classList.remove('open');
    document.querySelector(`tr[data-id="${id}"]`)?.classList.remove('expanded');
    expandedId = null;
  } else {
    // Close previous
    if (expandedId) {
      document.getElementById('di-' + expandedId)?.classList.remove('open');
      document.querySelector(`tr[data-id="${expandedId}"]`)?.classList.remove('expanded');
    }
    // Open new
    expandedId = id;
    document.getElementById('di-' + id)?.classList.add('open');
    document.querySelector(`tr[data-id="${id}"]`)?.classList.add('expanded');
  }
}

// ── Init ──
renderTable();
// Update summary cards with totals
document.getElementById('s-hot').textContent  = D.tier_counts.hot;
document.getElementById('s-warm').textContent = D.tier_counts.warm;
document.getElementById('s-cold').textContent = D.tier_counts.cold;
</script>
</body>
</html>"""

# Inject data + filter options
exam_opts  = ''.join(f'<option>{e}</option>' for e in exams)
city_opts  = ''.join(f'<option>{c}</option>' for c in cities)
stage_opts = ''.join(f'<option>{s}</option>' for s in stages)

page_html = (HTML
    .replace('__PAGE_DATA__', json.dumps(page_data))
    .replace('__EXAM_OPTIONS__', exam_opts)
    .replace('__CITY_OPTIONS__', city_opts)
    .replace('__STAGE_OPTIONS__', stage_opts)
    .replace('__HOT__', str(hot_count))
    .replace('__WARM__', str(warm_count))
    .replace('__COLD__', str(cold_count))
)

components.html(page_html, height=900, scrolling=False)

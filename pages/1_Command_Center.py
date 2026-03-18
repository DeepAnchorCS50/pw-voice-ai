"""
1_Command_Center.py — PW Voice AI
Rebuilt per execution plan: 3-layer interactive funnel
Layer 1: Branching funnel (default)
Layer 2: Filtered lead table (click tier header)
Layer 3: Lead detail card (click lead row)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, sys, random, datetime

# ── Path setup ─────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC      = os.path.join(ROOT, "src")
CSV_PATH = os.path.join(SRC, "data", "synthetic_leads_dataset.csv")

# Add root to path for ui_utils import
sys.path.insert(0, ROOT)
from ui_utils import render_nav, HIDE_STREAMLIT_CSS

st.set_page_config(page_title="Command Center — PW Voice AI", page_icon="⚡", layout="wide")
render_nav("Command Center")

# ── Load + enrich data ─────────────────────────────────────────────────────────
@st.cache_data(ttl=3600)

def load_leads():
    import random as rnd
    rnd.seed(42)
    df = pd.read_csv(CSV_PATH)

    SNIPPETS = {
        'HOT': [
            [{'role':'Agent','text':'Namaste! Main Priya bol rahi hoon PhysicsWallah se. Aapka JEE preparation kaisa chal raha hai?'},
             {'role':'Student','text':'Bilkul theek hai. Main seriously prepare kar raha hoon — mujhe Kota shift hona tha but online better lagta hai.'},
             {'role':'Agent','text':'Samajh sakti hoon. Hamare Arjuna batch mein top faculty hain, Pankaj sir personally doubt sessions lete hain.'},
             {'role':'Student','text':'Haan, maine unke lectures dekhe hain. Fees kitni hai full course ki?'}],
            [{'role':'Agent','text':'Hello! Calling from PhysicsWallah regarding your JEE Advanced inquiry.'},
             {'role':'Student','text':'Yes, I have been following PW for a long time. I want to know about Arjuna batch.'},
             {'role':'Agent','text':'Great choice. Arjuna is our flagship JEE Advanced program with live classes and doubt sessions daily.'},
             {'role':'Student','text':'My father wants to know — is there any instalment option for the fee?'}],
        ],
        'WARM': [
            [{'role':'Agent','text':'Hello! I am calling from PhysicsWallah regarding your NEET preparation inquiry.'},
             {'role':'Student','text':'Yes, I had checked the website. I am in class 11 right now.'},
             {'role':'Agent','text':'Perfect timing. Our Yakeen batch is specially designed for class 11 students starting early.'},
             {'role':'Student','text':'Sounds good but I need to discuss with my parents first before deciding.'}],
            [{'role':'Agent','text':'Namaste! PhysicsWallah ki taraf se call. Aap NEET 2027 ke liye prepare kar rahe hain?'},
             {'role':'Student','text':'Haan, but abhi main ek aur coaching bhi dekh raha hoon. Compare karna hai.'},
             {'role':'Agent','text':'Bilkul sahi approach hai. Hum aapko free trial access de sakte hain — ek week dekh lijiye.'},
             {'role':'Student','text':'Theek hai, trial access mil sakta hai to zaroor dekhta hoon.'}],
        ],
        'COLD': [
            [{'role':'Agent','text':'Namaste! PhysicsWallah ki taraf se call kar rahi hoon. Aap JEE ki preparation ke baare mein jaanna chahte the?'},
             {'role':'Student','text':'Haan, but abhi main class 9 mein hoon. Thoda jaldi hai shayad.'},
             {'role':'Agent','text':'Bilkul, aap sahi soch rahe hain. Hum Foundation batch bhi offer karte hain class 9-10 ke liye.'},
             {'role':'Student','text':'Okay, main apne papa se baat karke bataunga. Budget bhi dekhna hoga.'}],
            [{'role':'Agent','text':'Hello! PhysicsWallah calling. Were you looking for JEE preparation guidance?'},
             {'role':'Student','text':'I was just browsing. Not sure yet if I want to take coaching.'},
             {'role':'Agent','text':'Understood. No pressure at all. Can I share some information about our free content?'},
             {'role':'Student','text':'Sure, you can send it on WhatsApp. I will have a look.'}],
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
        snippet   = rnd.choice(SNIPPETS[tier])
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
            'date':           call_date,
            'rule_score':     min(100, max(0, score + rnd.randint(-8, 8))),
            'ml_score':       score,
            'qa_score':       int(row['qa_score']),
            'snippet':        snippet,
            'action_slack':   tier == 'HOT',
            'action_email':   tier in ('HOT', 'WARM'),
            'action_crm':     True,
        })
    return leads

leads = load_leads()

# ── Compute page data ──────────────────────────────────────────────────────────
hot_leads  = [l for l in leads if l['tier'] == 'HOT']
warm_leads = [l for l in leads if l['tier'] == 'WARM']
cold_leads = [l for l in leads if l['tier'] == 'COLD']

page_data = {
    "pipeline_summary": {
        "total": 130,
        "new": 18,
        "attempting": 12,
        "scored": 100,
        "hot":  len(hot_leads),
        "warm": len(warm_leads),
        "cold": len(cold_leads),
    },
    "funnel_stages": {
        "hot": [
            {"stage": "Senior Sales Assigned", "count": 9,  "pct": "27%"},
            {"stage": "Parent Discussion",      "count": 8,  "pct": "24%"},
            {"stage": "Enrollment Pending",     "count": 6,  "pct": "18%"},
            {"stage": "Enrolled",               "count": 4,  "pct": "12%", "terminal": "enrolled"},
            {"stage": "Dropped",                "count": 3,  "pct": "9%",  "terminal": "lost"},
        ],
        "warm": [
            {"stage": "Follow-up Scheduled",    "count": 11, "pct": "33%"},
            {"stage": "Info Sent",              "count": 8,  "pct": "24%"},
            {"stage": "Re-engaged",             "count": 6,  "pct": "18%"},
            {"stage": "Enrolled",               "count": 3,  "pct": "9%",  "terminal": "enrolled"},
            {"stage": "Nurture Pool",           "count": 3,  "pct": "9%",  "terminal": "nurture"},
        ],
        "cold": [
            {"stage": "Drip Campaign",          "count": 13, "pct": "38%"},
            {"stage": "Nurture Pool",           "count": 14, "pct": "41%", "terminal": "nurture"},
            {"stage": "Disqualified",           "count": 3,  "pct": "9%",  "terminal": "lost"},
        ],
    },
    "terminal_outcomes": {"enrolled": 7, "nurture_pool": 17, "lost": 6},
    "leads": leads,
    "live_activity": {
        "calls_today":      23,
        "leads_processed":  18,
        "hot_today":        4,
        "avg_score":        57.9,
    },
    "hourly_distribution": [
        {"hour": h, "count": c} for h, c in
        {6:1,7:2,8:3,9:5,10:8,11:7,12:4,13:3,14:3,15:4,16:5,17:6,18:7,19:9,20:8,21:6,22:3}.items()
    ],
}

data_json = json.dumps(page_data)

# ── HTML component ─────────────────────────────────────────────────────────────
HTML = """<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

:root {
  --bg:        #0f1117;
  --card:      #1a1d29;
  --card-h:    #232738;
  --border:    #2d3148;
  --text:      #e6e8f0;
  --muted:     #8b8fa3;
  --hot:       #ef4444;
  --warm:      #f59e0b;
  --cold:      #3b82f6;
  --success:   #22c55e;
  --brand:     #6366f1;
  --font:      'Inter', sans-serif;
  --mono:      'JetBrains Mono', monospace;
}

body {
  font-family: var(--font);
  background: var(--bg);
  color: var(--text);
  font-size: 13px;
  min-height: 100vh;
}

/* ── Ticker ── */
.ticker {
  display: flex;
  align-items: center;
  gap: 24px;
  background: var(--card);
  border-bottom: 1px solid var(--border);
  padding: 10px 24px;
  overflow: hidden;
}
.ticker-item {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
}
.ticker-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.8px; }
.ticker-val   { font-family: var(--mono); font-size: 18px; font-weight: 600; color: var(--text); }
.ticker-val.hot  { color: var(--hot); }
.ticker-val.warm { color: var(--warm); }
.ticker-val.cold { color: var(--cold); }
.ticker-val.green { color: var(--success); }
.ticker-div { width: 1px; height: 32px; background: var(--border); }

/* ── Main layout ── */
.main {
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 0;
  height: calc(100vh - 53px);
  overflow: hidden;
}

/* ── Funnel panel ── */
.funnel-panel {
  padding: 20px 24px;
  overflow-y: auto;
  border-right: 1px solid var(--border);
}
.panel-heading {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  margin-bottom: 16px;
}

/* ── Funnel top nodes ── */
.funnel-top {
  display: flex;
  gap: 10px;
  margin-bottom: 8px;
  justify-content: center;
}
.top-node {
  flex: 1;
  max-width: 180px;
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 14px;
  text-align: center;
}
.top-node-label { font-size: 10px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
.top-node-count { font-family: var(--mono); font-size: 22px; font-weight: 700; color: var(--text); }
.top-node-sub   { font-size: 10px; color: var(--muted); margin-top: 2px; }

/* ── AI divider ── */
.ai-divider {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}
.ai-line  { flex: 1; height: 1px; background: var(--brand); opacity: 0.4; }
.ai-badge {
  font-size: 11px;
  color: var(--brand);
  background: #6366f114;
  border: 1px solid #6366f133;
  border-radius: 20px;
  padding: 4px 14px;
  font-weight: 500;
  white-space: nowrap;
}

/* ── Branches ── */
.branches {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 10px;
  margin-top: 4px;
}
.branch { display: flex; flex-direction: column; gap: 4px; }

/* Branch header — clickable */
.branch-header {
  border-radius: 8px;
  padding: 10px 12px;
  border: 1.5px solid;
  text-align: center;
  cursor: pointer;
  transition: all 200ms ease;
  position: relative;
}
.branch-header:hover { transform: translateY(-1px); box-shadow: 0 4px 16px rgba(0,0,0,0.3); }
.branch-header.selected { box-shadow: 0 0 0 2px; }

.bh-hot  { background: #ef444414; border-color: #ef444433; }
.bh-warm { background: #f59e0b14; border-color: #f59e0b33; }
.bh-cold { background: #3b82f614; border-color: #3b82f633; }
.bh-hot.selected  { box-shadow: 0 0 0 2px var(--hot); }
.bh-warm.selected { box-shadow: 0 0 0 2px var(--warm); }
.bh-cold.selected { box-shadow: 0 0 0 2px var(--cold); }

.bh-emoji { font-size: 14px; margin-bottom: 2px; }
.bh-tier  { font-size: 11px; font-weight: 700; letter-spacing: 0.6px; }
.bh-hot  .bh-tier  { color: var(--hot); }
.bh-warm .bh-tier  { color: var(--warm); }
.bh-cold .bh-tier  { color: var(--cold); }
.bh-count { font-family: var(--mono); font-size: 20px; font-weight: 700; color: var(--text); margin: 2px 0; }
.bh-pct   { font-size: 10px; color: var(--muted); }
.bh-hint  { font-size: 9px; color: var(--muted); margin-top: 4px; opacity: 0.7; }

/* Stage rows */
.arr { text-align: center; color: var(--border); font-size: 11px; line-height: 1; margin: 1px 0; }
.stage-row {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  transition: border-color 200ms;
}
.stage-row:hover { border-color: var(--brand); }
.stage-name  { font-size: 11px; color: var(--text); }
.stage-right { text-align: right; }
.stage-count { font-family: var(--mono); font-size: 12px; font-weight: 600; color: var(--text); }
.stage-pct   { font-size: 9px; color: var(--muted); }

/* Terminal nodes */
.terminals { display: flex; gap: 4px; margin-top: 2px; }
.term {
  flex: 1;
  border-radius: 6px;
  padding: 6px 8px;
  text-align: center;
  border: 1px solid;
}
.term-enrolled { background: #22c55e14; border-color: #22c55e33; }
.term-nurture  { background: #f59e0b14; border-color: #f59e0b33; }
.term-lost     { background: #ef444414; border-color: #ef444433; }
.term-label { font-size: 9px; text-transform: uppercase; letter-spacing: 0.5px; font-weight: 600; }
.term-enrolled .term-label { color: var(--success); }
.term-nurture  .term-label { color: var(--warm); }
.term-lost     .term-label { color: var(--hot); }
.term-count { font-family: var(--mono); font-size: 14px; font-weight: 700; color: var(--text); }

/* Summary strip */
.summary-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--border);
}
.sum-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 10px 12px;
  text-align: center;
}
.sum-label { font-size: 9px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.8px; margin-bottom: 4px; }
.sum-val   { font-family: var(--mono); font-size: 20px; font-weight: 700; color: var(--text); }
.sum-sub   { font-size: 10px; color: var(--muted); margin-top: 2px; }

/* ── Right sidebar ── */
.right-panel {
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
.right-section {
  padding: 16px;
  border-bottom: 1px solid var(--border);
}
.section-title {
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 1px;
  color: var(--muted);
  margin-bottom: 12px;
}

/* Hour chart */
.hour-chart {
  display: flex;
  align-items: flex-end;
  gap: 3px;
  height: 60px;
}
.hcol { flex: 1; display: flex; flex-direction: column; align-items: center; gap: 2px; }
.hbar {
  width: 100%;
  border-radius: 2px 2px 0 0;
  background: #2d3148;
  transition: height 1s ease;
  height: 0;
}
.hbar.active { background: var(--brand); }
.hbar.peak   { background: var(--success); }
.hlabel { font-size: 7px; color: var(--muted); font-family: var(--mono); }

/* Activity feed */
.feed-box {
  flex: 1;
  overflow-y: auto;
  padding: 0 16px 16px;
}
.feed-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--border);
  opacity: 0;
  animation: fadeSlide 0.3s ease forwards;
}
@keyframes fadeSlide {
  from { opacity: 0; transform: translateX(8px); }
  to   { opacity: 1; transform: translateX(0); }
}
.feed-av {
  width: 28px; height: 28px;
  border-radius: 6px;
  display: flex; align-items: center; justify-content: center;
  font-size: 11px; font-weight: 700;
  flex-shrink: 0;
  font-family: var(--mono);
}
.av-HOT  { background: #ef444418; color: var(--hot);  border: 1px solid #ef444433; }
.av-WARM { background: #f59e0b18; color: var(--warm); border: 1px solid #f59e0b33; }
.av-COLD { background: #3b82f618; color: var(--cold); border: 1px solid #3b82f633; }
.feed-info { flex: 1; min-width: 0; }
.feed-name { font-size: 12px; font-weight: 500; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.feed-det  { font-size: 10px; color: var(--muted); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.feed-right { text-align: right; flex-shrink: 0; }
.tier-badge {
  display: inline-block;
  padding: 2px 7px;
  border-radius: 4px;
  font-size: 9px;
  font-weight: 700;
  font-family: var(--mono);
  letter-spacing: 0.3px;
}
.tb-HOT  { background: #ef444418; color: var(--hot); }
.tb-WARM { background: #f59e0b18; color: var(--warm); }
.tb-COLD { background: #3b82f618; color: var(--cold); }
.feed-time { font-size: 9px; color: var(--muted); margin-top: 2px; font-family: var(--mono); }

/* ── Lead table overlay ── */
.table-overlay {
  display: none;
  position: fixed;
  inset: 0;
  background: var(--bg);
  z-index: 100;
  flex-direction: column;
  animation: slideUp 200ms ease;
}
.table-overlay.visible { display: flex; }
@keyframes slideUp {
  from { transform: translateY(8px); opacity: 0; }
  to   { transform: translateY(0);   opacity: 1; }
}
.table-header {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border);
  background: var(--card);
}
.table-back {
  background: var(--card-h);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 12px;
  font-size: 12px;
  color: var(--muted);
  cursor: pointer;
  transition: all 150ms;
}
.table-back:hover { color: var(--text); border-color: var(--brand); }
.table-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}
.table-count {
  font-size: 11px;
  color: var(--muted);
  background: var(--card-h);
  padding: 3px 10px;
  border-radius: 10px;
  font-family: var(--mono);
}
.table-wrap { flex: 1; overflow-y: auto; padding: 16px 24px; }
table { width: 100%; border-collapse: collapse; }
th {
  text-align: left;
  font-size: 10px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.8px;
  color: var(--muted);
  padding: 8px 12px;
  border-bottom: 1px solid var(--border);
  cursor: pointer;
  user-select: none;
  position: sticky;
  top: 0;
  background: var(--bg);
}
th:hover { color: var(--text); }
th .sort-icon { margin-left: 4px; opacity: 0.4; }
th.sorted .sort-icon { opacity: 1; }
td {
  padding: 10px 12px;
  border-bottom: 1px solid var(--border);
  font-size: 12px;
  color: var(--text);
}
tr.lead-row { cursor: pointer; transition: background 150ms; }
tr.lead-row:hover td { background: var(--card); }
.score-bar-wrap { display: flex; align-items: center; gap: 6px; }
.score-bar { height: 4px; border-radius: 2px; flex: 1; background: var(--border); }
.score-fill { height: 100%; border-radius: 2px; }

/* ── Detail card ── */
.detail-overlay {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 200;
}
.detail-overlay.visible { display: block; }
.detail-backdrop {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.6);
}
.detail-panel {
  position: absolute;
  top: 0; right: 0; bottom: 0;
  width: 480px;
  background: var(--card);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform 250ms ease;
  overflow-y: auto;
}
.detail-overlay.visible .detail-panel { transform: translateX(0); }

.detail-top {
  padding: 20px;
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}
.detail-close {
  background: var(--card-h);
  border: 1px solid var(--border);
  border-radius: 6px;
  width: 28px; height: 28px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer;
  color: var(--muted);
  font-size: 14px;
  transition: all 150ms;
  flex-shrink: 0;
}
.detail-close:hover { color: var(--text); border-color: var(--brand); }
.detail-name { font-size: 18px; font-weight: 700; color: var(--text); }
.detail-meta { font-size: 11px; color: var(--muted); margin-top: 3px; }

.detail-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.detail-section-title {
  font-size: 10px; font-weight: 600;
  text-transform: uppercase; letter-spacing: 1px;
  color: var(--muted); margin-bottom: 8px;
}
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.detail-field {
  background: var(--bg);
  border-radius: 6px;
  padding: 8px 10px;
}
.df-label { font-size: 9px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 3px; }
.df-val   { font-size: 12px; color: var(--text); font-weight: 500; }

.score-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.score-card {
  background: var(--bg);
  border-radius: 6px;
  padding: 10px;
  text-align: center;
}
.sc-label { font-size: 9px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.6px; margin-bottom: 4px; }
.sc-val   { font-family: var(--mono); font-size: 24px; font-weight: 700; }

.snippet-wrap {
  background: var(--bg);
  border-radius: 8px;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.msg {
  display: flex;
  gap: 8px;
  align-items: flex-start;
}
.msg-role {
  font-size: 9px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  width: 46px;
  flex-shrink: 0;
  padding-top: 2px;
}
.msg-role.agent   { color: var(--brand); }
.msg-role.student { color: var(--warm); }
.msg-text { font-size: 11px; color: var(--text); line-height: 1.5; }

.actions-row {
  display: flex;
  gap: 8px;
}
.action-chip {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 500;
  border: 1px solid;
}
.ac-done { background: #22c55e14; border-color: #22c55e33; color: var(--success); }
.ac-skip { background: var(--bg); border-color: var(--border); color: var(--muted); }
</style>
</head>
<body>

<!-- Ticker -->
<div class="ticker">
  <div class="ticker-item">
    <div>
      <div class="ticker-label">Total Pipeline</div>
      <div class="ticker-val" id="t-total">0</div>
    </div>
  </div>
  <div class="ticker-div"></div>
  <div class="ticker-item">
    <div>
      <div class="ticker-label">🔥 HOT</div>
      <div class="ticker-val hot" id="t-hot">0</div>
    </div>
  </div>
  <div class="ticker-div"></div>
  <div class="ticker-item">
    <div>
      <div class="ticker-label">🔶 WARM</div>
      <div class="ticker-val warm" id="t-warm">0</div>
    </div>
  </div>
  <div class="ticker-div"></div>
  <div class="ticker-item">
    <div>
      <div class="ticker-label">❄️ COLD</div>
      <div class="ticker-val cold" id="t-cold">0</div>
    </div>
  </div>
  <div class="ticker-div"></div>
  <div class="ticker-item">
    <div>
      <div class="ticker-label">Calls Today</div>
      <div class="ticker-val green" id="t-calls">0</div>
    </div>
  </div>
  <div class="ticker-div"></div>
  <div class="ticker-item">
    <div>
      <div class="ticker-label">✅ Enrolled</div>
      <div class="ticker-val green" id="t-enrolled">7</div>
    </div>
  </div>
  <div class="ticker-div"></div>
  <div class="ticker-item">
    <div>
      <div class="ticker-label">Avg Score</div>
      <div class="ticker-val" id="t-avgscore">0</div>
    </div>
  </div>
</div>

<!-- Main -->
<div class="main">

  <!-- Funnel panel -->
  <div class="funnel-panel" id="funnel-panel">
    <div class="panel-heading">Sales Pipeline — Full Funnel</div>

    <div class="funnel-top">
      <div class="top-node">
        <div class="top-node-label">New Leads</div>
        <div class="top-node-count">18</div>
        <div class="top-node-sub">Uncontacted</div>
      </div>
      <div class="top-node">
        <div class="top-node-label">Attempting</div>
        <div class="top-node-count">12</div>
        <div class="top-node-sub">AI Call Queued</div>
      </div>
    </div>

    <div class="ai-divider">
      <div class="ai-line"></div>
      <div class="ai-badge">🤖 AI Voice Call · 100 Leads Scored</div>
      <div class="ai-line"></div>
    </div>

    <div class="branches" id="branches"></div>

    <div class="summary-strip">
      <div class="sum-card">
        <div class="sum-label">✅ Enrolled</div>
        <div class="sum-val" style="color:var(--success)">7</div>
        <div class="sum-sub">7% conversion</div>
      </div>
      <div class="sum-card">
        <div class="sum-label">🔄 Nurture Pool</div>
        <div class="sum-val" style="color:var(--warm)">17</div>
        <div class="sum-sub">next cycle</div>
      </div>
      <div class="sum-card">
        <div class="sum-label">❌ Lost</div>
        <div class="sum-val" style="color:var(--hot)">6</div>
        <div class="sum-sub">dropped / disqualified</div>
      </div>
      <div class="sum-card">
        <div class="sum-label">📊 Pipeline</div>
        <div class="sum-val" style="color:var(--brand)">130</div>
        <div class="sum-sub">total tracked</div>
      </div>
    </div>
  </div>

  <!-- Right sidebar -->
  <div class="right-panel">
    <div class="right-section">
      <div class="section-title">Calls by Hour</div>
      <div class="hour-chart" id="hour-chart"></div>
    </div>
    <div class="right-section" style="display:flex;align-items:center;justify-content:space-between;padding-bottom:12px;">
      <div class="section-title" style="margin-bottom:0">Live Activity</div>
      <span style="font-size:9px;background:#22c55e18;border:1px solid #22c55e33;color:var(--success);padding:2px 8px;border-radius:10px;font-family:var(--mono)" id="feed-count">0 events</span>
    </div>
    <div class="feed-box" id="feed-box"></div>
  </div>
</div>

<!-- Layer 2: Lead table overlay -->
<div class="table-overlay" id="table-overlay">
  <div class="table-header">
    <div class="table-back" onclick="closeTable()">← Back to Funnel</div>
    <div class="table-title" id="table-title">Leads</div>
    <div class="table-count" id="table-count">0 leads</div>
  </div>
  <div class="table-wrap">
    <table id="lead-table">
      <thead>
        <tr>
          <th onclick="sortTable('name')">Name <span class="sort-icon">↕</span></th>
          <th onclick="sortTable('city')">City <span class="sort-icon">↕</span></th>
          <th onclick="sortTable('class')">Class <span class="sort-icon">↕</span></th>
          <th onclick="sortTable('exam')">Exam <span class="sort-icon">↕</span></th>
          <th onclick="sortTable('score')">Score <span class="sort-icon">↕</span></th>
          <th onclick="sortTable('stage')">Stage <span class="sort-icon">↕</span></th>
          <th onclick="sortTable('date')">Date <span class="sort-icon">↕</span></th>
        </tr>
      </thead>
      <tbody id="lead-tbody"></tbody>
    </table>
  </div>
</div>

<!-- Layer 3: Detail card overlay -->
<div class="detail-overlay" id="detail-overlay">
  <div class="detail-backdrop" onclick="closeDetail()"></div>
  <div class="detail-panel" id="detail-panel">
    <div class="detail-top">
      <div>
        <div class="detail-name" id="d-name">—</div>
        <div class="detail-meta" id="d-meta">—</div>
      </div>
      <div>
        <div id="d-tier-badge" style="margin-bottom:6px;text-align:right"></div>
        <div class="detail-close" onclick="closeDetail()">✕</div>
      </div>
    </div>
    <div class="detail-body">
      <div>
        <div class="detail-section-title">Lead Profile</div>
        <div class="detail-grid" id="d-grid"></div>
      </div>
      <div>
        <div class="detail-section-title">Score Breakdown</div>
        <div class="score-compare" id="d-scores"></div>
      </div>
      <div>
        <div class="detail-section-title">Conversation Preview</div>
        <div class="snippet-wrap" id="d-snippet"></div>
      </div>
      <div>
        <div class="detail-section-title">Actions Triggered</div>
        <div class="actions-row" id="d-actions"></div>
      </div>
    </div>
  </div>
</div>

<script>
window.pageData = __PAGE_DATA__;
const D = window.pageData;

// ── Count-up animation ──
function countUp(el, target, suffix='', decimals=0) {
  const dur = 1000, steps = 40;
  let i = 0;
  const timer = setInterval(() => {
    i++;
    const val = target * (i / steps);
    el.textContent = decimals ? val.toFixed(decimals) + suffix : Math.round(val) + suffix;
    if (i >= steps) { el.textContent = decimals ? target.toFixed(decimals) + suffix : target + suffix; clearInterval(timer); }
  }, dur / steps);
}

setTimeout(() => {
  countUp(document.getElementById('t-total'),    D.pipeline_summary.total);
  countUp(document.getElementById('t-hot'),      D.pipeline_summary.hot);
  countUp(document.getElementById('t-warm'),     D.pipeline_summary.warm);
  countUp(document.getElementById('t-cold'),     D.pipeline_summary.cold);
  countUp(document.getElementById('t-calls'),    D.live_activity.calls_today);
  countUp(document.getElementById('t-avgscore'), D.live_activity.avg_score, '', 1);
}, 200);

// ── Build branches ──
const TIER_CFG = {
  HOT:  { cls:'hot',  emoji:'🔥', label:'HOT',  key:'hot'  },
  WARM: { cls:'warm', emoji:'🔶', label:'WARM', key:'warm' },
  COLD: { cls:'cold', emoji:'❄️', label:'COLD', key:'cold' },
};
const TERMINAL_COLORS = { enrolled:'term-enrolled', nurture:'term-nurture', lost:'term-lost' };
const TERMINAL_LABELS = { enrolled:'✅ Enrolled', nurture:'🔄 Nurture Pool', lost:'❌ Lost/Disqualified' };

function buildBranches() {
  const wrap = document.getElementById('branches');
  ['HOT','WARM','COLD'].forEach(tier => {
    const cfg    = TIER_CFG[tier];
    const stages = D.funnel_stages[cfg.key];
    const count  = D.pipeline_summary[cfg.key];
    const pct    = Math.round(count / D.pipeline_summary.scored * 100);

    const branch = document.createElement('div');
    branch.className = 'branch';

    // Header
    const hdr = document.createElement('div');
    hdr.className = `branch-header bh-${cfg.cls}`;
    hdr.id = `bh-${tier}`;
    hdr.innerHTML = `
      <div class="bh-emoji">${cfg.emoji}</div>
      <div class="bh-tier">${cfg.label}</div>
      <div class="bh-count">${count}</div>
      <div class="bh-pct">${pct}% of scored</div>
      <div class="bh-hint">Click to view leads →</div>
    `;
    hdr.onclick = () => openTable(tier);
    branch.appendChild(hdr);

    // Stages (skip terminal ones — shown separately)
    const nonTerminal = stages.filter(s => !s.terminal);
    const terminals   = stages.filter(s => s.terminal);

    nonTerminal.forEach(s => {
      const arr = document.createElement('div');
      arr.className = 'arr'; arr.textContent = '↓';
      branch.appendChild(arr);

      const row = document.createElement('div');
      row.className = 'stage-row';
      row.innerHTML = `
        <div class="stage-name">${s.stage}</div>
        <div class="stage-right">
          <div class="stage-count">${s.count}</div>
          <div class="stage-pct">${s.pct}</div>
        </div>`;
      branch.appendChild(row);
    });

    if (terminals.length) {
      const arr = document.createElement('div');
      arr.className = 'arr'; arr.textContent = '↓';
      branch.appendChild(arr);

      const termRow = document.createElement('div');
      termRow.className = 'terminals';
      terminals.forEach(t => {
        const td = document.createElement('div');
        td.className = `term ${TERMINAL_COLORS[t.terminal]}`;
        td.innerHTML = `<div class="term-label">${TERMINAL_LABELS[t.terminal]}</div><div class="term-count">${t.count}</div>`;
        termRow.appendChild(td);
      });
      branch.appendChild(termRow);
    }

    wrap.appendChild(branch);
  });
}
buildBranches();

// ── Hour chart ──
const maxV = Math.max(...D.hourly_distribution.map(h => h.count));
const curH = new Date().getHours();
const hc   = document.getElementById('hour-chart');
D.hourly_distribution.forEach((h, i) => {
  const isPeak   = (h.hour >= 10 && h.hour <= 11) || (h.hour >= 19 && h.hour <= 21);
  const isActive = h.hour === curH;
  const cls = isActive ? 'active' : isPeak ? 'peak' : '';
  hc.innerHTML += `<div class="hcol"><div class="hbar ${cls}" id="hb${i}" data-h="${Math.round(h.count/maxV*55)}"></div><div class="hlabel">${h.hour}</div></div>`;
});
setTimeout(() => {
  document.querySelectorAll('.hbar').forEach(b => b.style.height = b.dataset.h + 'px');
}, 400);

// ── Live activity feed ──
const POOL = D.leads;
const STAGES_FEED = {
  HOT:  ['Senior Sales Assigned','Parent Discussion','Enrollment Pending'],
  WARM: ['Follow-up Scheduled','Info Sent','Re-engaged'],
  COLD: ['Drip Campaign','Nurture Pool','Attempting'],
};
let fidx = 0, fevt = 0;

function fmtAgo(s) { return s < 60 ? s+'s ago' : s < 3600 ? Math.floor(s/60)+'m ago' : Math.floor(s/3600)+'h ago'; }

function addFeed(ago) {
  const item = POOL[fidx % POOL.length]; fidx++; fevt++;
  const box  = document.getElementById('feed-box');
  const div  = document.createElement('div');
  div.className = 'feed-item';
  const stageFeed = item.stage || STAGES_FEED[item.tier][0];
  div.innerHTML = `
    <div class="feed-av av-${item.tier}">${item.name[0].toUpperCase()}</div>
    <div class="feed-info">
      <div class="feed-name">${item.name}</div>
      <div class="feed-det">${item.city} · ${item.exam} · ${stageFeed}</div>
    </div>
    <div class="feed-right">
      <div class="tier-badge tb-${item.tier}">${item.tier}</div>
      <div class="feed-time">${fmtAgo(ago)}</div>
    </div>`;
  box.insertBefore(div, box.firstChild);
  while (box.children.length > 10) box.removeChild(box.lastChild);
  document.getElementById('feed-count').textContent = fevt + ' events';
}

// ── Seed feed with historical items ──
[900,600,480,360,240,180,120,60].forEach((ago,i) => setTimeout(() => addFeed(ago), i*60));

// ── Live tick: every 30s — updates feed + all pipeline panels ──
let liveTotal = D.pipeline_summary.total;
let liveCalls = D.live_activity.calls_today;
let liveHot   = D.pipeline_summary.hot;
let liveWarm  = D.pipeline_summary.warm;
let liveCold  = D.pipeline_summary.cold;

setInterval(() => {
  // 1. Add feed item
  addFeed(0);

  // 2. Ticker: total and calls tick up
  liveTotal++;
  liveCalls++;
  document.getElementById('t-total').textContent = liveTotal;
  document.getElementById('t-calls').textContent = liveCalls;

  // 3. Ticker: tier count for the new lead's tier
  const newLead = POOL[(fidx - 1) % POOL.length];
  if (newLead.tier === 'HOT')       { liveHot++;  document.getElementById('t-hot').textContent  = liveHot; }
  else if (newLead.tier === 'WARM') { liveWarm++; document.getElementById('t-warm').textContent = liveWarm; }
  else                              { liveCold++; document.getElementById('t-cold').textContent = liveCold; }

  // 4. Funnel branch header: update count for that tier
  const bhEl = document.getElementById('bh-' + newLead.tier);
  if (bhEl) {
    const countEl = bhEl.querySelector('.bh-count');
    const pctEl   = bhEl.querySelector('.bh-pct');
    const tierTotal = newLead.tier === 'HOT' ? liveHot : newLead.tier === 'WARM' ? liveWarm : liveCold;
    const scored = liveTotal - D.pipeline_summary.new - D.pipeline_summary.attempting;
    if (countEl) countEl.textContent = tierTotal;
    if (pctEl)   pctEl.textContent   = Math.round(tierTotal / scored * 100) + '% of scored';
  }

  // 5. Hour bar: current hour grows slightly
  const ab = document.querySelector('.hbar.active');
  if (ab) { const h = parseInt(ab.style.height) || 0; ab.style.height = Math.min(h + 2, 62) + 'px'; }

  // 6. Update "X ago" timestamps
  document.querySelectorAll('.feed-time').forEach(el => {
    const m = el.textContent.match(/(\d+)(s|m|h) ago/);
    if (!m) return;
    let s = parseInt(m[1]);
    if (m[2]==='m') s*=60; if (m[2]==='h') s*=3600;
    el.textContent = fmtAgo(s + 10);
  });
}, 10000);

// ── Layer 2: Lead table ──
let currentTier   = null;
let sortField     = 'score';
let sortAsc       = false;

function openTable(tier) {
  currentTier = tier;
  document.querySelectorAll('.branch-header').forEach(h => h.classList.remove('selected'));
  document.getElementById(`bh-${tier}`).classList.add('selected');

  const cfg = TIER_CFG[tier];
  document.getElementById('table-title').textContent = `${cfg.emoji} ${cfg.label} Leads`;

  renderTable();
  document.getElementById('table-overlay').classList.add('visible');
}

function closeTable() {
  document.getElementById('table-overlay').classList.remove('visible');
  document.querySelectorAll('.branch-header').forEach(h => h.classList.remove('selected'));
  currentTier = null;
}

function renderTable() {
  let rows = D.leads.filter(l => l.tier === currentTier);

  // Sort
  rows.sort((a, b) => {
    let av = a[sortField], bv = b[sortField];
    if (typeof av === 'string') av = av.toLowerCase();
    if (typeof bv === 'string') bv = bv.toLowerCase();
    return sortAsc ? (av > bv ? 1 : -1) : (av < bv ? 1 : -1);
  });

  document.getElementById('table-count').textContent = rows.length + ' leads';

  const COLOR = { HOT: 'var(--hot)', WARM: 'var(--warm)', COLD: 'var(--cold)' };
  const tbody = document.getElementById('lead-tbody');
  tbody.innerHTML = '';
  rows.forEach(lead => {
    const tr = document.createElement('tr');
    tr.className = 'lead-row';
    tr.onclick = () => openDetail(lead);
    const scoreColor = lead.score >= 75 ? 'var(--success)' : lead.score >= 55 ? 'var(--warm)' : 'var(--hot)';
    tr.innerHTML = `
      <td style="font-weight:500">${lead.name}</td>
      <td>${lead.city}</td>
      <td>Class ${lead.class}</td>
      <td><span style="font-size:10px;background:var(--card-h);padding:2px 7px;border-radius:4px;">${lead.exam}</span></td>
      <td>
        <div class="score-bar-wrap">
          <span style="font-family:var(--mono);font-weight:600;color:${scoreColor};min-width:28px">${lead.score}</span>
          <div class="score-bar"><div class="score-fill" style="width:${lead.score}%;background:${scoreColor}"></div></div>
        </div>
      </td>
      <td><span style="font-size:10px;color:var(--muted)">${lead.stage}</span></td>
      <td style="color:var(--muted);font-family:var(--mono);font-size:11px">${lead.date}</td>
    `;
    tbody.appendChild(tr);
  });

  // Update sort icons
  document.querySelectorAll('th').forEach(th => {
    th.classList.remove('sorted');
    const icon = th.querySelector('.sort-icon');
    if (icon) icon.textContent = '↕';
  });
  const sortedTh = document.querySelector(`th[onclick="sortTable('${sortField}')"]`);
  if (sortedTh) {
    sortedTh.classList.add('sorted');
    const icon = sortedTh.querySelector('.sort-icon');
    if (icon) icon.textContent = sortAsc ? '↑' : '↓';
  }
}

function sortTable(field) {
  if (sortField === field) sortAsc = !sortAsc;
  else { sortField = field; sortAsc = false; }
  renderTable();
}

// ── Layer 3: Detail card ──
function openDetail(lead) {
  const COLOR = { HOT:'var(--hot)', WARM:'var(--warm)', COLD:'var(--cold)' };
  const TBCLS = { HOT:'tb-HOT', WARM:'tb-WARM', COLD:'tb-COLD' };

  document.getElementById('d-name').textContent = lead.name;
  document.getElementById('d-meta').textContent = `${lead.city} · ${lead.exam} · Class ${lead.class} · Called ${lead.date}`;

  document.getElementById('d-tier-badge').innerHTML = `
    <span class="tier-badge ${TBCLS[lead.tier]}" style="font-size:11px;padding:3px 10px">${lead.tier}</span>`;

  // Profile grid
  const dm_labels = { self:'Self','parent_present':'Parent Present','parent_later':'Parent Later' };
  document.getElementById('d-grid').innerHTML = `
    <div class="detail-field"><div class="df-label">Target Exam</div><div class="df-val">${lead.exam}</div></div>
    <div class="detail-field"><div class="df-label">Exam Year</div><div class="df-val">${lead.exam_year}</div></div>
    <div class="detail-field"><div class="df-label">Engagement</div><div class="df-val" style="text-transform:capitalize">${lead.engagement.replace('_',' ')}</div></div>
    <div class="detail-field"><div class="df-label">Budget Concern</div><div class="df-val">${lead.budget_concern === 'TRUE' ? '⚠️ Yes' : '✅ No'}</div></div>
    <div class="detail-field"><div class="df-label">Decision Maker</div><div class="df-val">${dm_labels[lead.decision_maker] || lead.decision_maker}</div></div>
    <div class="detail-field"><div class="df-label">QA Score</div><div class="df-val">${lead.qa_score}%</div></div>
  `;

  // Score breakdown
  const scoreColor = lead.score >= 75 ? 'var(--success)' : lead.score >= 55 ? 'var(--warm)' : 'var(--hot)';
  document.getElementById('d-scores').innerHTML = `
    <div class="score-card">
      <div class="sc-label">Rule-Based</div>
      <div class="sc-val" style="color:var(--muted)">${lead.rule_score}</div>
    </div>
    <div class="score-card">
      <div class="sc-label">ML Model</div>
      <div class="sc-val" style="color:${scoreColor}">${lead.ml_score}</div>
    </div>
  `;

  // Snippet
  const snippetHtml = lead.snippet.map(m => `
    <div class="msg">
      <div class="msg-role ${m.role.toLowerCase()}">${m.role}</div>
      <div class="msg-text">${m.text}</div>
    </div>`).join('');
  document.getElementById('d-snippet').innerHTML = snippetHtml;

  // Actions
  document.getElementById('d-actions').innerHTML = `
    <div class="action-chip ${lead.action_slack ? 'ac-done' : 'ac-skip'}">
      ${lead.action_slack ? '✓' : '–'} Slack
    </div>
    <div class="action-chip ${lead.action_email ? 'ac-done' : 'ac-skip'}">
      ${lead.action_email ? '✓' : '–'} Email
    </div>
    <div class="action-chip ac-done">✓ CRM</div>
  `;

  document.getElementById('detail-overlay').classList.add('visible');
}

function closeDetail() {
  document.getElementById('detail-overlay').classList.remove('visible');
}

// Keyboard: Escape closes overlays
document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (document.getElementById('detail-overlay').classList.contains('visible')) closeDetail();
    else if (document.getElementById('table-overlay').classList.contains('visible')) closeTable();
  }
});
</script>
</body>
</html>"""

# Inject data
page_html = HTML.replace("__PAGE_DATA__", data_json)
components.html(page_html, height=900, scrolling=False)

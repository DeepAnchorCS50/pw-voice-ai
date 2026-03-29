"""
1_Operations.py — PW Voice AI
Unified Operations page with 2 JS tabs:
  Tab 1: Command Center — funnel, outbound queue, system status
  Tab 2: Agent Console  — live call view, scoring reveal, action cards
Driven by a JavaScript state machine. All calls are pre-generated.
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json, os, sys, random, datetime, glob, base64

ROOT     = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC      = os.path.join(ROOT, "src")
CSV_PATH = os.path.join(SRC, "data", "synthetic_leads_dataset.csv")
DEMO_DIR = os.path.join(SRC, "data", "demo_calls")

sys.path.insert(0, ROOT)
from ui_utils import render_nav

st.set_page_config(page_title="Operations — PW Voice AI", page_icon="⚡", layout="wide")
render_nav("Operations")
st.cache_data.clear()

# ── Load CSV leads ─────────────────────────────────────────────────────────────
@st.cache_data
def load_leads():
    import random as rnd
    rnd.seed(42)
    df = pd.read_csv(CSV_PATH)
    return df

df = load_leads()
hot_count  = int((df['tier_label']=='HOT').sum())
warm_count = int((df['tier_label']=='WARM').sum())
cold_count = int((df['tier_label']=='COLD').sum())

# ── Load pre-generated demo calls ─────────────────────────────────────────────
@st.cache_data
def load_demo_calls():
    calls = []
    json_files = sorted(glob.glob(os.path.join(DEMO_DIR, "*.json")))
    for jf in json_files:
        with open(jf) as f:
            call = json.load(f)
        wav_path = jf.replace(".json", ".wav")
        if os.path.exists(wav_path):
            with open(wav_path, "rb") as f:
                call["audio_base64"] = base64.b64encode(f.read()).decode()
        else:
            call["audio_base64"] = ""
        calls.append(call)
    return calls

demo_calls = load_demo_calls()

# ── Fallback demo calls if none generated yet ──────────────────────────────────
if not demo_calls:
    demo_calls = [
        {
            "call_id":   "call_001",
            "call_type": "outbound",
            "student":   {"name":"Rahul Kumar","city":"Delhi","class":"12","exam":"JEE Main","lead_source":"Downloaded JEE prep guide"},
            "transcript":[
                {"speaker":"agent",  "text":"Hi Rahul! This is Priya calling from PhysicsWallah. How is your J E E preparation going?","timestamp":0.0},
                {"speaker":"student","text":"It is going well. I have been studying hard. I was actually thinking about joining a coaching.","timestamp":4.5},
                {"speaker":"agent",  "text":"That is great timing! Our Arjuna batch is perfect for class 12 students targeting J E E Main. When is your exam?","timestamp":9.2},
                {"speaker":"student","text":"In about 3 months. I need something intensive with daily doubt sessions.","timestamp":14.1},
                {"speaker":"agent",  "text":"Arjuna has daily live classes plus dedicated doubt clearing with top faculty. Would you like me to send the enrollment details?","timestamp":19.8},
                {"speaker":"student","text":"Yes please! Can you also share the fee structure? I can take the decision myself.","timestamp":25.3},
            ],
            "timestamps": [0,4500,9200,14100,19800,25300],
            "duration_seconds": 35,
            "extracted_fields":{"name":"Rahul Kumar","class":"12","exam":"JEE Main","city":"Delhi","months_to_exam":3,"budget_concern":False,"decision_maker":"self","engagement_level":"high"},
            "rule_based_score": 82,
            "ml_score": 85,
            "ml_proba": {"HOT":85.0,"WARM":11.0,"COLD":4.0},
            "tier": "HOT",
            "action_cards":{
                "promised_actions":["Send enrollment link and fee structure"],
                "recommended_actions":["Assign to senior sales","Schedule follow-up today"],
                "slack_message":{"channel":"#pw-hot-leads","preview":"🔥 HOT lead: Rahul Kumar, JEE Main, Score: 85. Self decision-maker, 3 months to exam. Immediate callback recommended."},
                "email":{"to":"Rahul Kumar","subject":"Your JEE Preparation Plan — PhysicsWallah","preview":"Hi Rahul, it was great speaking with you! I've attached the Arjuna batch details and fee structure as promised."},
                "crm_record":{"status":"Qualified — HOT","assigned_to":"Senior Sales Team","follow_up":"Today","lead_source":"Downloaded JEE prep guide","notes":"High intent. Send materials immediately."}
            },
            "audio_base64": ""
        },
        {
            "call_id":   "call_002",
            "call_type": "inbound",
            "student":   {"name":"Aakash Singh","city":"Lucknow","class":"10","exam":"JEE Main","lead_source":"Inbound — PW Helpline"},
            "transcript":[
                {"speaker":"student","text":"Hello, I saw your advertisement. My son wants to prepare for J E E but he is in class 10 only.","timestamp":0.0},
                {"speaker":"agent",  "text":"Namaste! Thank you for calling PhysicsWallah. Class 10 is actually a great time to start the foundation. We have a special batch for this.","timestamp":5.2},
                {"speaker":"student","text":"How much does it cost? We are from a small town, budget is limited.","timestamp":10.8},
                {"speaker":"agent",  "text":"Our Foundation batch starts at very affordable prices with EMI options. The exam is still 2 years away so you have time to plan.","timestamp":16.3},
                {"speaker":"student","text":"I will think about it and discuss with my wife. Will call back if interested.","timestamp":22.1},
            ],
            "timestamps": [0,5200,10800,16300,22100],
            "duration_seconds": 28,
            "extracted_fields":{"name":"Aakash Singh","class":"10","exam":"JEE Main","city":"Lucknow","months_to_exam":24,"budget_concern":True,"decision_maker":"parent_later","engagement_level":"low"},
            "rule_based_score": 28,
            "ml_score": 31,
            "ml_proba": {"HOT":5.0,"WARM":18.0,"COLD":77.0},
            "tier": "COLD",
            "action_cards":{
                "promised_actions":["Follow up when ready"],
                "recommended_actions":["Add to drip campaign","Schedule follow-up in 3 months"],
                "slack_message":{"channel":"#pw-nurture","preview":"❄️ COLD lead: Aakash Singh (parent), JEE Main, Score: 31. Budget concern, class 10. Added to nurture campaign."},
                "email":{"to":"Aakash Singh","subject":"Start Your JEE Journey Early — PhysicsWallah","preview":"Dear Sir, thank you for calling PhysicsWallah. Starting early gives your child a real advantage for JEE preparation."},
                "crm_record":{"status":"Nurture Pool — COLD","assigned_to":"Drip Campaign","follow_up":"In 3 months","lead_source":"Inbound — PW Helpline","notes":"Early stage, budget concern. Long-term nurture via email."}
            },
            "audio_base64": ""
        }
    ]

# ── Outbound queue (5 leads for today) ─────────────────────────────────────────
random.seed(99)
outbound_queue = [
    {"id":"Q001","name":"Rahul Kumar",  "city":"Delhi",     "exam":"JEE Main","priority":"High",  "source":"Downloaded study guide",  "status":"queued"},
    {"id":"Q002","name":"Priya Sharma", "city":"Pune",      "exam":"NEET",    "priority":"Medium","source":"Watched free lecture",     "status":"queued"},
    {"id":"Q003","name":"Vikram Patel", "city":"Ahmedabad", "exam":"JEE Main","priority":"High",  "source":"Visited pricing page",    "status":"queued"},
    {"id":"Q004","name":"Ananya Reddy", "city":"Hyderabad", "exam":"NEET",    "priority":"Medium","source":"Downloaded NEET guide",   "status":"queued"},
    {"id":"Q005","name":"Arjun Nair",   "city":"Kochi",     "exam":"JEE Main","priority":"Low",   "source":"Free mock test signup",   "status":"queued"},
]

# ── Page data ──────────────────────────────────────────────────────────────────
page_data = {
    "pipeline_summary": {
        "total": 130, "new": 18, "attempting": 12, "scored": 100,
        "hot": hot_count, "warm": warm_count, "cold": cold_count,
    },
    "funnel_stages": {
        "hot": [
            {"stage":"Senior Sales Assigned","count":9, "pct":"27%"},
            {"stage":"Parent Discussion",     "count":8, "pct":"24%"},
            {"stage":"Enrollment Pending",    "count":6, "pct":"18%"},
            {"stage":"Enrolled",              "count":4, "pct":"12%","terminal":"enrolled"},
            {"stage":"Dropped",               "count":3, "pct":"9%", "terminal":"lost"},
        ],
        "warm": [
            {"stage":"Follow-up Scheduled","count":11,"pct":"33%"},
            {"stage":"Info Sent",           "count":8, "pct":"24%"},
            {"stage":"Re-engaged",          "count":6, "pct":"18%"},
            {"stage":"Enrolled",            "count":3, "pct":"9%", "terminal":"enrolled"},
            {"stage":"Nurture Pool",        "count":3, "pct":"9%", "terminal":"nurture"},
        ],
        "cold": [
            {"stage":"Drip Campaign","count":13,"pct":"38%"},
            {"stage":"Nurture Pool", "count":14,"pct":"41%","terminal":"nurture"},
            {"stage":"Disqualified", "count":3, "pct":"9%", "terminal":"lost"},
        ],
    },
    "terminal_outcomes": {"enrolled":7,"nurture_pool":17,"lost":6},
    "outbound_queue": outbound_queue,
    "demo_calls":     demo_calls,
    "demo_sequence":  [0, 1],   # indices into demo_calls for the main 2-call flow
}

data_json = json.dumps(page_data)

# ── HTML Component ─────────────────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
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

/* ── Page tabs ── */
.page-tabs{display:flex;align-items:center;background:var(--card);border-bottom:1px solid var(--border);padding:0 20px;height:44px;gap:2px;flex-shrink:0;}
.ptab{padding:0 16px;height:100%;display:flex;align-items:center;font-size:12px;font-weight:500;color:var(--muted);cursor:pointer;border-bottom:2px solid transparent;gap:6px;transition:all 150ms;}
.ptab:hover{color:var(--text);}
.ptab.active{color:var(--text);border-bottom-color:var(--brand);}
.ptab-spacer{flex:1;}

/* ── System status bar ── */
.status-bar{display:flex;align-items:center;gap:12px;padding:8px 20px;background:var(--card);border-bottom:1px solid var(--border);flex-shrink:0;}
.status-badge{display:flex;align-items:center;gap:6px;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:600;letter-spacing:0.4px;transition:all 300ms;}
.status-offline{background:#2d314822;border:1px solid var(--border);color:var(--muted);}
.status-live   {background:#22c55e18;border:1px solid #22c55e44;color:var(--success);}
.status-dot{width:6px;height:6px;border-radius:50%;background:currentColor;}
.status-live .status-dot{animation:pulse 1.2s infinite;}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:0.5;transform:scale(0.8)}}
.go-live-btn{padding:6px 18px;background:var(--brand);color:#fff;border:none;border-radius:6px;font-size:12px;font-weight:600;cursor:pointer;transition:all 150ms;font-family:var(--font);}
.go-live-btn:hover{background:#5254cc;transform:translateY(-1px);}
.go-live-btn:disabled{background:var(--border);color:var(--muted);cursor:not-allowed;transform:none;}
.status-meta{font-size:11px;color:var(--muted);margin-left:auto;}
.restart-btn{padding:5px 12px;background:var(--card-h);color:var(--muted);border:1px solid var(--border);border-radius:6px;font-size:11px;cursor:pointer;transition:all 150ms;font-family:var(--font);}
.restart-btn:hover{color:var(--text);border-color:var(--brand);}

/* ── Tab panels ── */
.tab-panel{display:none;flex:1;overflow:hidden;}
.tab-panel.active{display:flex;}

/* ── Command Center layout ── */
.cc-layout{display:grid;grid-template-columns:1fr 380px;flex:1;overflow:hidden;}
.cc-left{overflow-y:auto;padding:16px 20px;border-right:1px solid var(--border);}
.cc-right{overflow-y:auto;padding:16px;}

/* ── Section titles ── */
.sec-title{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:12px;}

/* ── Queue table ── */
.queue-wrap{background:var(--card);border:1px solid var(--border);border-radius:10px;overflow:hidden;margin-bottom:16px;}
.queue-header{display:grid;grid-template-columns:140px 80px 90px 1fr 110px;gap:0;padding:8px 14px;border-bottom:1px solid var(--border);}
.qh{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:var(--muted);}
.queue-row{display:grid;grid-template-columns:140px 80px 90px 1fr 110px;gap:0;padding:10px 14px;border-bottom:1px solid var(--border);transition:background 120ms;cursor:pointer;}
.queue-row:last-child{border-bottom:none;}
.queue-row:hover{background:var(--card-h);}
.qr-name{font-size:12px;font-weight:500;color:var(--text);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.qr-city{font-size:11px;color:var(--muted);}
.qr-exam{font-size:10px;background:var(--card-h);padding:2px 7px;border-radius:4px;color:var(--text);white-space:nowrap;}
.qr-source{font-size:11px;color:var(--muted);overflow:hidden;text-overflow:ellipsis;white-space:nowrap;}
.q-status{font-size:10px;font-weight:600;padding:3px 9px;border-radius:10px;white-space:nowrap;text-align:center;}
.qs-queued    {background:#2d314833;color:var(--muted);}
.qs-inprogress{background:#6366f122;color:var(--brand);animation:qpulse 1.5s infinite;}
.qs-hot       {background:#ef444422;color:var(--hot);}
.qs-warm      {background:#f59e0b22;color:var(--warm);}
.qs-cold      {background:#3b82f622;color:var(--cold);}
@keyframes qpulse{0%,100%{opacity:1}50%{opacity:0.6}}

/* ── Inbound queue ── */
.inbound-box{background:var(--card);border:1px solid var(--border);border-radius:10px;padding:14px;margin-bottom:16px;transition:all 300ms;}
.inbound-empty{display:flex;align-items:center;gap:10px;color:var(--muted);font-size:12px;}
.inbound-empty-icon{width:28px;height:28px;border-radius:6px;background:var(--card-h);display:flex;align-items:center;justify-content:center;font-size:14px;}
.inbound-active{display:none;align-items:center;gap:12px;}
.inbound-ring{width:36px;height:36px;border-radius:50%;background:#ef444418;border:2px solid var(--hot);display:flex;align-items:center;justify-content:center;font-size:18px;animation:ring 0.8s infinite;}
@keyframes ring{0%,100%{transform:rotate(-15deg)}50%{transform:rotate(15deg)}}
.inbound-info .ib-number{font-size:13px;font-weight:600;color:var(--text);}
.inbound-info .ib-label{font-size:10px;color:var(--muted);}

/* ── Funnel (reused from Command Center) ── */
.funnel-wrap{display:flex;flex-direction:column;align-items:center;}
.funnel-top{display:flex;gap:10px;justify-content:center;margin-bottom:6px;}
.top-node{flex:1;max-width:160px;background:var(--card);border:1px solid var(--border);border-radius:8px;padding:8px 12px;text-align:center;}
.top-node-label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.6px;margin-bottom:3px;}
.top-node-count{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--text);}
.top-node-sub{font-size:10px;color:var(--muted);margin-top:1px;}
.ai-divider{display:flex;align-items:center;gap:8px;margin:8px 0;width:100%;}
.ai-line{flex:1;height:1px;background:var(--brand);opacity:0.3;}
.ai-badge{font-size:10px;color:var(--brand);background:#6366f114;border:1px solid #6366f133;border-radius:20px;padding:3px 12px;white-space:nowrap;}
.branches{display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;width:100%;}
.branch{display:flex;flex-direction:column;align-items:center;gap:3px;}
.branch-header{width:100%;text-align:center;padding:8px;border-radius:8px;border:1.5px solid;cursor:pointer;transition:opacity 150ms;}
.branch-header:hover{opacity:0.8;}
.bh-hot {background:#ef444414;border-color:#ef444433;}
.bh-warm{background:#f59e0b14;border-color:#f59e0b33;}
.bh-cold{background:#3b82f614;border-color:#3b82f633;}
.bh-tier{font-size:10px;font-weight:700;letter-spacing:0.6px;}
.bh-hot .bh-tier{color:var(--hot);}
.bh-warm .bh-tier{color:var(--warm);}
.bh-cold .bh-tier{color:var(--cold);}
.bh-count{font-family:var(--mono);font-size:18px;font-weight:700;color:var(--text);}
.bh-pct{font-size:10px;color:var(--muted);}
.arr{color:var(--border);font-size:11px;text-align:center;line-height:1;}
.stage-row{width:100%;background:var(--card);border:1px solid var(--border);border-radius:5px;padding:5px 8px;display:flex;justify-content:space-between;align-items:center;}
.sn-name{font-size:10px;color:var(--text);}
.sn-count{font-family:var(--mono);font-size:11px;font-weight:600;color:var(--text);}
.sn-pct{font-size:9px;color:var(--muted);}
.terminals{display:flex;gap:4px;width:100%;}
.term{flex:1;border-radius:5px;padding:5px 6px;text-align:center;border:1px solid;}
.term-enrolled{background:#22c55e14;border-color:#22c55e33;}
.term-nurture {background:#f59e0b14;border-color:#f59e0b33;}
.term-lost    {background:#ef444414;border-color:#ef444433;}
.term-label{font-size:8px;text-transform:uppercase;letter-spacing:0.4px;font-weight:600;}
.term-enrolled .term-label{color:var(--success);}
.term-nurture  .term-label{color:var(--warm);}
.term-lost     .term-label{color:var(--hot);}
.term-count{font-family:var(--mono);font-size:12px;font-weight:700;color:var(--text);}
.funnel-updated-badge{display:none;background:#22c55e18;border:1px solid #22c55e33;color:var(--success);font-size:10px;padding:3px 10px;border-radius:10px;margin-top:8px;}

/* ── Recent calls list (right panel) ── */
.recent-call{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px 12px;margin-bottom:8px;cursor:pointer;transition:all 150ms;}
.recent-call:hover{border-color:var(--brand);}
.rc-top{display:flex;align-items:center;justify-content:space-between;margin-bottom:4px;}
.rc-name{font-size:12px;font-weight:500;color:var(--text);}
.rc-time{font-size:10px;color:var(--muted);font-family:var(--mono);}
.rc-meta{font-size:11px;color:var(--muted);}
.tier-badge{display:inline-block;padding:2px 8px;border-radius:4px;font-size:9px;font-weight:700;font-family:var(--mono);}
.tb-HOT {background:#ef444418;color:var(--hot);}
.tb-WARM{background:#f59e0b18;color:var(--warm);}
.tb-COLD{background:#3b82f618;color:var(--cold);}

/* ── Agent Console layout ── */
.ac-layout{display:grid;grid-template-columns:1fr 340px;flex:1;overflow:hidden;}
.ac-main{overflow-y:auto;padding:16px 20px;border-right:1px solid var(--border);}
.ac-side{overflow-y:auto;padding:16px;}

/* ── Idle state ── */
.idle-state{display:flex;flex-direction:column;align-items:center;justify-content:center;height:100%;gap:16px;color:var(--muted);}
.idle-icon{font-size:48px;opacity:0.4;}
.idle-text{font-size:14px;}

/* ── Active call card ── */
.call-card{background:var(--card);border:1px solid var(--border);border-radius:12px;overflow:hidden;}
.call-header{display:flex;align-items:center;justify-content:space-between;padding:14px 18px;border-bottom:1px solid var(--border);}
.call-type-badge{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;padding:4px 10px;border-radius:20px;}
.ctb-outbound{background:#6366f118;border:1px solid #6366f133;color:var(--brand);}
.ctb-inbound {background:#ef444418;border:1px solid #ef444433;color:var(--hot);}
.call-timer{font-family:var(--mono);font-size:18px;font-weight:700;color:var(--text);}
.call-student-info{display:flex;align-items:center;gap:12px;padding:12px 18px;border-bottom:1px solid var(--border);}
.stu-avatar{width:36px;height:36px;border-radius:50%;background:var(--brand);display:flex;align-items:center;justify-content:center;font-size:16px;font-weight:700;color:#fff;flex-shrink:0;}
.stu-name{font-size:13px;font-weight:500;color:var(--text);}
.stu-meta{font-size:11px;color:var(--muted);}

/* ── Speaker indicators ── */
.speakers-row{display:flex;gap:10px;padding:12px 18px;border-bottom:1px solid var(--border);}
.speaker-card{flex:1;background:var(--card-h);border:1px solid var(--border);border-radius:8px;padding:8px 12px;display:flex;align-items:center;gap:8px;transition:all 200ms;}
.speaker-card.speaking{border-color:var(--brand);background:#6366f108;}
.speaker-dot{width:8px;height:8px;border-radius:50%;background:var(--border);flex-shrink:0;transition:background 200ms;}
.speaker-card.speaking .speaker-dot{background:var(--brand);}
.speaker-label{font-size:11px;color:var(--muted);}
.speaker-name{font-size:12px;font-weight:500;color:var(--text);}
.soundwave{display:flex;align-items:center;gap:2px;height:16px;margin-left:auto;}
.soundwave span{display:block;width:3px;border-radius:2px;background:var(--brand);animation:wave 0.6s ease-in-out infinite;}
.soundwave span:nth-child(2){animation-delay:0.1s;}
.soundwave span:nth-child(3){animation-delay:0.2s;}
.soundwave span:nth-child(4){animation-delay:0.3s;}
.soundwave span:nth-child(5){animation-delay:0.4s;}
@keyframes wave{0%,100%{height:4px}50%{height:14px}}

/* ── Transcript ── */
.transcript-box{height:220px;overflow-y:auto;padding:14px 18px;display:flex;flex-direction:column;gap:10px;}
.tr-msg{display:flex;gap:10px;opacity:0;transition:opacity 300ms;}
.tr-msg.visible{opacity:1;}
.tr-role{font-size:9px;font-weight:600;text-transform:uppercase;letter-spacing:0.5px;width:50px;flex-shrink:0;padding-top:2px;}
.tr-role.agent  {color:var(--brand);}
.tr-role.student{color:var(--warm);}
.tr-text{font-size:12px;color:var(--text);line-height:1.5;}
.tr-ts{font-size:9px;color:var(--muted);font-family:var(--mono);padding-top:2px;white-space:nowrap;}

/* ── Analyzing animation ── */
.analyzing-card{display:none;flex-direction:column;align-items:center;justify-content:center;padding:40px;gap:12px;}
.analyzing-spinner{width:40px;height:40px;border:3px solid var(--border);border-top-color:var(--brand);border-radius:50%;animation:spin 0.8s linear infinite;}
@keyframes spin{to{transform:rotate(360deg)}}
.analyzing-text{font-size:15px;font-weight:500;color:var(--text);}
.analyzing-dots span{animation:blink 1.4s infinite;font-size:18px;color:var(--brand);}
.analyzing-dots span:nth-child(2){animation-delay:0.2s;}
.analyzing-dots span:nth-child(3){animation-delay:0.4s;}
@keyframes blink{0%,80%,100%{opacity:0}40%{opacity:1}}

/* ── Scoring reveal ── */
.scoring-card{display:none;padding:18px;}
.scoring-top{display:flex;align-items:center;gap:16px;margin-bottom:16px;}
.tier-big{font-size:32px;font-weight:800;font-family:var(--mono);}
.tier-big.HOT {color:var(--hot);}
.tier-big.WARM{color:var(--warm);}
.tier-big.COLD{color:var(--cold);}
.tier-big-label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:0.8px;margin-top:2px;}
.score-compare{display:flex;gap:10px;margin-left:auto;}
.score-box{background:var(--card-h);border:1px solid var(--border);border-radius:8px;padding:8px 14px;text-align:center;}
.sb-label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px;}
.sb-val{font-family:var(--mono);font-size:20px;font-weight:700;color:var(--text);}
.proba-row{display:flex;align-items:center;gap:8px;margin-bottom:6px;font-size:11px;}
.proba-label{width:38px;color:var(--muted);}
.proba-bar-wrap{flex:1;height:5px;background:var(--border);border-radius:3px;overflow:hidden;}
.proba-fill{height:100%;border-radius:3px;transition:width 0.8s ease;}
.proba-val{width:36px;text-align:right;color:var(--text);font-family:var(--mono);}

/* ── Action cards ── */
.action-cards{display:flex;flex-direction:column;gap:8px;margin-top:14px;}
.action-card{background:var(--card-h);border:1px solid var(--border);border-radius:8px;padding:10px 12px;}
.ac-header{display:flex;align-items:center;gap:8px;margin-bottom:6px;}
.ac-icon{font-size:14px;}
.ac-title{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:0.8px;color:var(--muted);}
.ac-status{margin-left:auto;font-size:9px;font-weight:600;color:var(--success);background:#22c55e18;padding:2px 8px;border-radius:10px;}
.ac-content{font-size:11px;color:var(--text);line-height:1.5;}
.ac-label{font-size:10px;color:var(--muted);margin-top:3px;}

/* ── Inbound notification banner ── */
.inbound-banner{display:none;align-items:center;gap:14px;padding:14px 18px;background:#ef444408;border:1px solid #ef444422;border-radius:10px;margin-bottom:14px;animation:slideDown 300ms ease;}
@keyframes slideDown{from{transform:translateY(-12px);opacity:0}to{transform:translateY(0);opacity:1}}
.ib-icon{font-size:24px;animation:ibring 0.6s infinite;}
@keyframes ibring{0%,100%{transform:rotate(-10deg)}50%{transform:rotate(10deg)}}
.ib-text .ib-top{font-size:13px;font-weight:600;color:var(--text);}
.ib-text .ib-sub{font-size:11px;color:var(--muted);}

/* ── Call detail panel (slide in from right) ── */
.detail-overlay{display:none;position:fixed;inset:0;z-index:200;}
.detail-overlay.visible{display:block;}
.detail-backdrop{position:absolute;inset:0;background:rgba(0,0,0,0.6);}
.detail-panel{position:absolute;top:0;right:0;bottom:0;width:460px;background:var(--card);border-left:1px solid var(--border);overflow-y:auto;transform:translateX(100%);transition:transform 250ms ease;}
.detail-overlay.visible .detail-panel{transform:translateX(0);}
.dp-header{padding:18px 20px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:flex-start;}
.dp-close{width:28px;height:28px;background:var(--card-h);border:1px solid var(--border);border-radius:6px;display:flex;align-items:center;justify-content:center;cursor:pointer;color:var(--muted);font-size:13px;}
.dp-close:hover{color:var(--text);border-color:var(--brand);}
.dp-body{padding:18px 20px;display:flex;flex-direction:column;gap:14px;}
.dp-section-title{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin-bottom:8px;}
.dp-field-grid{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.dp-field{background:var(--bg);border-radius:6px;padding:8px 10px;}
.dpf-label{font-size:9px;color:var(--muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:3px;}
.dpf-val{font-size:12px;color:var(--text);font-weight:500;}
.dp-transcript{background:var(--bg);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px;max-height:220px;overflow-y:auto;}

::-webkit-scrollbar{width:4px;}
::-webkit-scrollbar-track{background:var(--bg);}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:2px;}

/* ── Call controls bar ── */
.call-controls{display:none;align-items:center;gap:8px;padding:10px 18px;border-top:1px solid var(--border);background:var(--card);}
.call-controls.visible{display:flex;}
.ctrl-btn{padding:5px 14px;border-radius:6px;font-size:11px;font-weight:600;cursor:pointer;border:1px solid;font-family:var(--font);transition:all 150ms;}
.ctrl-skip{background:#6366f114;border-color:#6366f133;color:var(--brand);}
.ctrl-skip:hover{background:#6366f122;}
.ctrl-end{background:#ef444414;border-color:#ef444433;color:var(--hot);}
.ctrl-end:hover{background:#ef444422;}
.ctrl-idle{background:#2d314822;border-color:var(--border);color:var(--muted);}
.ctrl-idle:hover{color:var(--text);border-color:var(--muted);}
.ctrl-idle.requested{color:var(--warm);border-color:var(--warm);background:#f59e0b14;}

/* ── New lead toast ── */
.new-lead-toast{position:absolute;top:10px;left:50%;transform:translateX(-50%) translateY(-60px);background:var(--card);border:1px solid #22c55e44;border-radius:10px;padding:10px 16px;display:flex;align-items:center;gap:10px;z-index:100;transition:transform 400ms ease,opacity 400ms ease;opacity:0;pointer-events:none;white-space:nowrap;}
.new-lead-toast.show{transform:translateX(-50%) translateY(0);opacity:1;}
.nlt-dot{width:8px;height:8px;border-radius:50%;background:var(--success);animation:pulse 1s infinite;}
.nlt-name{font-size:12px;font-weight:600;color:var(--text);}
.nlt-meta{font-size:10px;color:var(--muted);}
</style>
</head>
<body>

<!-- Page tabs -->
<div class="page-tabs">
  <div class="ptab active" id="ptab-cc" onclick="switchTab('cc')">⚡ Command Center</div>
  <div class="ptab"        id="ptab-ac" onclick="switchTab('ac')">📞 Agent Console</div>
  <div class="ptab-spacer"></div>
  <span style="font-size:10px;color:var(--muted);font-family:var(--mono)" id="clock-display">--:--:--</span>
</div>

<!-- System status bar -->
<div class="status-bar">
  <div class="status-badge status-offline" id="status-badge">
    <div class="status-dot"></div>
    <span id="status-text">Agent Offline</span>
  </div>
  <button class="go-live-btn" id="go-live-btn" onclick="goLive()">▶ Go Live</button>
  <div class="status-meta" id="status-meta">0 calls processed today</div>
  <button class="restart-btn" id="restart-btn" onclick="restartDemo()" style="display:none">↺ Restart</button>
</div>

<!-- Command Center tab -->
<div class="tab-panel active" id="panel-cc">
  <div class="cc-layout">
    <div class="cc-left" style="position:relative">
      <!-- New lead toast -->
      <div class="new-lead-toast" id="new-lead-toast">
        <div class="nlt-dot"></div>
        <div><div class="nlt-name" id="nlt-name">New Lead</div><div class="nlt-meta" id="nlt-meta">Added to queue</div></div>
      </div>

      <!-- Outbound Queue -->
      <div class="sec-title">Outbound Queue — Today</div>
      <div class="queue-wrap">
        <div class="queue-header">
          <div class="qh">Name</div>
          <div class="qh">City</div>
          <div class="qh">Exam</div>
          <div class="qh">Lead Source</div>
          <div class="qh">Status</div>
        </div>
        <div id="queue-body"></div>
      </div>

      <!-- Inbound Queue -->
      <div class="sec-title">Inbound Queue</div>
      <div class="inbound-box" id="inbound-box">
        <div class="inbound-empty" id="inbound-empty">
          <div class="inbound-empty-icon">📵</div>
          <span>No active inbound calls</span>
        </div>
        <div class="inbound-active" id="inbound-active">
          <div class="inbound-ring">📞</div>
          <div class="inbound-info">
            <div class="ib-number">+91-98XXX-XXXXX</div>
            <div class="ib-label">Incoming call — processing automatically</div>
          </div>
        </div>
      </div>

      <!-- Sales Funnel -->
      <div class="sec-title">Sales Pipeline</div>
      <div class="funnel-wrap" id="funnel-wrap"></div>
      <div class="funnel-updated-badge" id="funnel-badge">✓ Updated with 2 new leads</div>

    </div>
    <div class="cc-right">
      <div class="sec-title">Recent Calls</div>
      <div id="recent-calls-list">
        <div style="color:var(--muted);font-size:11px;text-align:center;padding:30px 0">No calls processed yet</div>
      </div>
    </div>
  </div>
</div>

<!-- Agent Console tab -->
<div class="tab-panel" id="panel-ac">
  <div class="ac-layout">
    <div class="ac-main">

      <!-- Idle state -->
      <div class="idle-state" id="idle-state">
        <div class="idle-icon">📞</div>
        <div class="idle-text">Click "Go Live" to start the agent</div>
      </div>

      <!-- Inbound notification banner -->
      <div class="inbound-banner" id="inbound-banner">
        <div class="ib-icon">📲</div>
        <div class="ib-text">
          <div class="ib-top">Incoming Call — +91-98XXX-XXXXX</div>
          <div class="ib-sub">Processing automatically via PW Helpline</div>
        </div>
      </div>

      <!-- Active call card -->
      <div class="call-card" id="call-card" style="display:none">
        <div class="call-header">
          <div>
            <span class="call-type-badge ctb-outbound" id="call-type-badge">OUTBOUND</span>
          </div>
          <div class="call-timer" id="call-timer">0:00</div>
        </div>
        <div class="call-student-info" id="call-student-info">
          <div class="stu-avatar" id="stu-avatar">R</div>
          <div>
            <div class="stu-name" id="stu-name">Student</div>
            <div class="stu-meta" id="stu-meta">—</div>
          </div>
        </div>
        <div class="speakers-row">
          <div class="speaker-card" id="spk-agent">
            <div class="speaker-dot"></div>
            <div>
              <div class="speaker-label">Agent</div>
              <div class="speaker-name">Priya (PW AI)</div>
            </div>
            <div class="soundwave" id="sw-agent" style="display:none">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          </div>
          <div class="speaker-card" id="spk-student">
            <div class="speaker-dot"></div>
            <div>
              <div class="speaker-label">Student</div>
              <div class="speaker-name" id="spk-student-name">Student</div>
            </div>
            <div class="soundwave" id="sw-student" style="display:none">
              <span></span><span></span><span></span><span></span><span></span>
            </div>
          </div>
        </div>
        <div class="transcript-box" id="transcript-box"></div>
        <div class="call-controls" id="call-controls">
          <button class="ctrl-btn ctrl-skip" onclick="skipToEnd()">⏩ Skip to End</button>
          <button class="ctrl-btn ctrl-end"  onclick="endCall()">✕ End Call</button>
          <button class="ctrl-btn ctrl-idle" id="idle-btn" onclick="goIdle()">⏸ Go Idle</button>
        </div>
      </div>

      <!-- Analyzing -->
      <div class="analyzing-card" id="analyzing-card">
        <div class="analyzing-spinner"></div>
        <div class="analyzing-text">Analyzing conversation</div>
        <div class="analyzing-dots"><span>.</span><span>.</span><span>.</span></div>
      </div>

      <!-- Scoring reveal -->
      <div class="scoring-card" id="scoring-card">
        <div class="scoring-top">
          <div>
            <div class="tier-big" id="tier-big">HOT</div>
            <div class="tier-big-label">Lead Tier</div>
          </div>
          <div class="score-compare">
            <div class="score-box">
              <div class="sb-label">Rule-Based</div>
              <div class="sb-val" id="rule-score">—</div>
            </div>
            <div class="score-box">
              <div class="sb-label">ML Model</div>
              <div class="sb-val" id="ml-score">—</div>
            </div>
          </div>
        </div>
        <div id="proba-bars"></div>
        <div class="action-cards" id="action-cards"></div>
      </div>

    </div>

    <!-- Right side panel -->
    <div class="ac-side">
      <div class="sec-title">Completed Calls</div>
      <div id="ac-recent-list">
        <div style="color:var(--muted);font-size:11px;text-align:center;padding:30px 0">No calls completed yet</div>
      </div>
    </div>
  </div>
</div>

<!-- Detail panel overlay -->
<div class="detail-overlay" id="detail-overlay">
  <div class="detail-backdrop" onclick="closeDetail()"></div>
  <div class="detail-panel" id="detail-panel">
    <div class="dp-header">
      <div>
        <div style="font-size:16px;font-weight:700;color:var(--text)" id="dp-name">—</div>
        <div style="font-size:11px;color:var(--muted);margin-top:3px" id="dp-meta">—</div>
      </div>
      <div class="dp-close" onclick="closeDetail()">✕</div>
    </div>
    <div class="dp-body">
      <div>
        <div class="dp-section-title">Extracted Fields</div>
        <div class="dp-field-grid" id="dp-fields"></div>
      </div>
      <div>
        <div class="dp-section-title">Score</div>
        <div id="dp-scores" style="display:flex;gap:10px"></div>
      </div>
      <div>
        <div class="dp-section-title">Conversation</div>
        <div class="dp-transcript" id="dp-transcript"></div>
      </div>
    </div>
  </div>
</div>

<script>
window.pageData = __PAGE_DATA__;
const D = window.pageData;

// ── State machine ──────────────────────────────────────────────────────────────
const STATES = {
  IDLE:             'IDLE',
  LIVE:             'LIVE',
  OUTBOUND_ACTIVE:  'OUTBOUND_ACTIVE',
  OUTBOUND_DONE:    'OUTBOUND_DONE',
  PAUSE:            'PAUSE',
  INBOUND_ALERT:    'INBOUND_ALERT',
  INBOUND_ACTIVE:   'INBOUND_ACTIVE',
  INBOUND_DONE:     'INBOUND_DONE',
  COMPLETE:         'COMPLETE',
};
let state      = STATES.IDLE;
let callsProcessed = 0;
let currentCallIdx = 0;
let audio      = null;
let timerInterval = null;
let timerSecs  = 0;
let transcriptInterval = null;
let completedCalls = [];
const seq = D.demo_sequence;  // [0, 1]
let idleRequested  = false;
let outboundQueueIdx = 2;  // queue leads 0,1 used in fixed seq; extras start at 2
let newLeadPool = [
  {name:'Sneha Iyer',    city:'Chennai',   exam:'NEET',     source:'Watched free lecture'},
  {name:'Rohan Gupta',   city:'Jaipur',    exam:'JEE Main', source:'Downloaded mock test'},
  {name:'Meera Nair',    city:'Bangalore', exam:'NEET',     source:'Visited pricing page'},
  {name:'Aditya Shah',   city:'Surat',     exam:'JEE Adv',  source:'Referral from friend'},
  {name:'Pooja Verma',   city:'Patna',     exam:'NEET',     source:'YouTube ad click'},
  {name:'Karthik Rao',   city:'Vizag',     exam:'JEE Main', source:'Free mock test signup'},
];

// ── Clock ──────────────────────────────────────────────────────────────────────
function updateClock() {
  const n = new Date();
  document.getElementById('clock-display').textContent =
    String(n.getHours()).padStart(2,'0') + ':' +
    String(n.getMinutes()).padStart(2,'0') + ':' +
    String(n.getSeconds()).padStart(2,'0');
}
setInterval(updateClock, 1000); updateClock();

// ── Tab switching ──────────────────────────────────────────────────────────────
function switchTab(name) {
  document.querySelectorAll('.ptab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.tab-panel').forEach(p => p.classList.remove('active'));
  document.getElementById('ptab-' + name).classList.add('active');
  document.getElementById('panel-' + name).classList.add('active');
}

// ── Build outbound queue ───────────────────────────────────────────────────────
function buildQueue() {
  const body = document.getElementById('queue-body');
  body.innerHTML = '';
  D.outbound_queue.forEach((lead, i) => {
    const row = document.createElement('div');
    row.className = 'queue-row';
    row.id = 'qrow-' + i;
    row.innerHTML = `
      <div><div class="qr-name">${lead.name}</div></div>
      <div><div class="qr-city">${lead.city}</div></div>
      <div><span class="qr-exam">${lead.exam}</span></div>
      <div><div class="qr-source">${lead.source}</div></div>
      <div><span class="q-status qs-queued" id="qstatus-${i}">Queued</span></div>`;
    row.onclick = () => {
      const call = completedCalls.find(c => c.student && c.student.name === lead.name);
      if (call) openDetail(call);
    };
    body.appendChild(row);
  });
}

// ── Build funnel ───────────────────────────────────────────────────────────────
function buildFunnel() {
  const wrap = document.getElementById('funnel-wrap');
  wrap.innerHTML = '';

  // Top nodes
  const topDiv = document.createElement('div');
  topDiv.className = 'funnel-top';
  topDiv.innerHTML = `
    <div class="top-node"><div class="top-node-label">New Leads</div><div class="top-node-count" id="fn-new">${D.pipeline_summary.new}</div><div class="top-node-sub">Uncontacted</div></div>
    <div class="top-node"><div class="top-node-label">Attempting</div><div class="top-node-count" id="fn-att">${D.pipeline_summary.attempting}</div><div class="top-node-sub">AI Call Queued</div></div>`;
  wrap.appendChild(topDiv);

  const divider = document.createElement('div');
  divider.className = 'ai-divider';
  divider.innerHTML = `<div class="ai-line"></div><div class="ai-badge">🤖 AI Scored ${D.pipeline_summary.scored} Leads</div><div class="ai-line"></div>`;
  wrap.appendChild(divider);

  const TIER_CFG = {
    HOT:  {cls:'hot', emoji:'🔥', key:'hot'},
    WARM: {cls:'warm',emoji:'🔶',key:'warm'},
    COLD: {cls:'cold',emoji:'❄️',key:'cold'},
  };
  const TERM_COLORS = {enrolled:'term-enrolled',nurture:'term-nurture',lost:'term-lost'};
  const TERM_LABELS = {enrolled:'✅ Enrolled',nurture:'🔄 Nurture',lost:'❌ Lost'};

  const branches = document.createElement('div');
  branches.className = 'branches';

  ['HOT','WARM','COLD'].forEach(tier => {
    const cfg    = TIER_CFG[tier];
    const stages = D.funnel_stages[cfg.key];
    const count  = D.pipeline_summary[cfg.key];
    const pct    = Math.round(count / D.pipeline_summary.scored * 100);

    const branch = document.createElement('div');
    branch.className = 'branch';

    const hdr = document.createElement('div');
    hdr.className = `branch-header bh-${cfg.cls}`;
    hdr.innerHTML = `<div class="bh-tier">${cfg.emoji} ${tier}</div><div class="bh-count" id="bcount-${tier}">${count}</div><div class="bh-pct">${pct}% of scored</div>`;
    hdr.onclick = () => { window.top.location.href = '/Lead_List'; };
    branch.appendChild(hdr);

    stages.filter(s => !s.terminal).forEach(s => {
      const a = document.createElement('div'); a.className='arr'; a.textContent='↓';
      branch.appendChild(a);
      const r = document.createElement('div'); r.className='stage-row';
      r.innerHTML=`<div class="sn-name">${s.stage}</div><div class="sn-right"><div class="sn-count">${s.count}</div><div class="sn-pct">${s.pct}</div></div>`;
      branch.appendChild(r);
    });

    const terms = stages.filter(s => s.terminal);
    if (terms.length) {
      const a = document.createElement('div'); a.className='arr'; a.textContent='↓';
      branch.appendChild(a);
      const tr = document.createElement('div'); tr.className='terminals';
      terms.forEach(t => {
        const td = document.createElement('div');
        td.className=`term ${TERM_COLORS[t.terminal]}`;
        td.innerHTML=`<div class="term-label">${TERM_LABELS[t.terminal]}</div><div class="term-count">${t.count}</div>`;
        tr.appendChild(td);
      });
      branch.appendChild(tr);
    }
    branches.appendChild(branch);
  });
  wrap.appendChild(branches);
}

// ── Go Live ────────────────────────────────────────────────────────────────────
function goLive() {
  setState(STATES.LIVE);
}

function restartDemo() {
  // Stop audio if playing
  if (audio) { audio.pause(); audio = null; }
  if (timerInterval)       { clearInterval(timerInterval); timerInterval = null; }
  if (transcriptInterval)  { clearInterval(transcriptInterval); transcriptInterval = null; }

  callsProcessed = 0;
  completedCalls = [];
  idleRequested  = false;
  outboundQueueIdx = 2;
  state = STATES.IDLE;

  buildQueue();
  buildFunnel();
  document.getElementById('recent-calls-list').innerHTML = '<div style="color:var(--muted);font-size:11px;text-align:center;padding:30px 0">No calls processed yet</div>';
  document.getElementById('ac-recent-list').innerHTML    = '<div style="color:var(--muted);font-size:11px;text-align:center;padding:30px 0">No calls completed yet</div>';
  document.getElementById('inbound-empty').style.display  = 'flex';
  document.getElementById('inbound-active').style.display = 'none';
  document.getElementById('funnel-badge').style.display   = 'none';
  document.getElementById('status-badge').className = 'status-badge status-offline';
  document.getElementById('status-text').textContent = 'Agent Offline';
  document.getElementById('status-meta').textContent = '0 calls processed today';
  document.getElementById('go-live-btn').disabled = false;
  document.getElementById('go-live-btn').style.display = 'block';
  document.getElementById('restart-btn').style.display = 'none';
  const idleBtn = document.getElementById('idle-btn');
  if (idleBtn) { idleBtn.classList.remove('requested'); idleBtn.textContent = '⏸ Go Idle'; }

  showAcState('idle');
}

// ── State machine ──────────────────────────────────────────────────────────────
function setState(newState) {
  state = newState;
  renderState();
}

function renderState() {
  switch (state) {
    case STATES.LIVE:
      onLive(); break;
    case STATES.OUTBOUND_ACTIVE:
      onCallActive(seq[0]); break;
    case STATES.OUTBOUND_DONE:
      onCallDone(seq[0], STATES.PAUSE); break;
    case STATES.PAUSE:
      onPause(); break;
    case STATES.INBOUND_ALERT:
      onInboundAlert(); break;
    case STATES.INBOUND_ACTIVE:
      onCallActive(seq[1]); break;
    case STATES.INBOUND_DONE:
      onCallDone(seq[1], STATES.COMPLETE); break;
    case STATES.COMPLETE:
      onComplete(); break;
  }
}

function onLive() {
  document.getElementById('status-badge').className = 'status-badge status-live';
  document.getElementById('status-text').textContent = 'Agent Live — Processing Calls';
  document.getElementById('go-live-btn').disabled = true;
  // First outbound: update queue row 0 to In Progress
  updateQueueStatus(0, 'inprogress', '● In Progress');
  setTimeout(() => setState(STATES.OUTBOUND_ACTIVE), 800);
}

function onCallActive(callIdx) {
  onCallActiveWith(callIdx, callIdx === seq[0] ? STATES.OUTBOUND_DONE : STATES.INBOUND_DONE);
}

function onCallActiveWith(callIdx, nextState) {
  const call = D.demo_calls[callIdx];
  if (!call) { setState(STATES.COMPLETE); return; }

  showAcState('call');
  const isOutbound = call.call_type === 'outbound';

  // Call type badge
  const badge = document.getElementById('call-type-badge');
  badge.className = `call-type-badge ${isOutbound ? 'ctb-outbound':'ctb-inbound'}`;
  badge.textContent = isOutbound ? 'OUTBOUND' : 'INBOUND';

  // Student info
  const s = call.student;
  document.getElementById('stu-avatar').textContent = s.name[0].toUpperCase();
  document.getElementById('stu-name').textContent   = s.name;
  document.getElementById('stu-meta').textContent   = `${s.city} · Class ${s.class} · ${s.exam} · ${s.lead_source}`;
  document.getElementById('spk-student-name').textContent = s.name.split(' ')[0];

  // Clear transcript
  document.getElementById('transcript-box').innerHTML = '';

  // Timer
  timerSecs = 0;
  if (timerInterval) clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    timerSecs++;
    const m = Math.floor(timerSecs/60);
    const s = timerSecs % 60;
    document.getElementById('call-timer').textContent = `${m}:${String(s).padStart(2,'0')}`;
  }, 1000);

  // Audio
  if (call.audio_base64 && call.audio_base64.length > 100) {
    audio = new Audio('data:audio/wav;base64,' + call.audio_base64);
    audio.play().catch(() => {});
    audio.addEventListener('ended', () => {
      clearInterval(timerInterval);
      clearInterval(transcriptInterval);
      showSpeaking(null);
      setTimeout(() => setState(nextState), 500);
    });
    // Transcript sync
    const msgs = call.transcript || [];
    const tss  = call.timestamps || msgs.map((_, i) => i * 3000);
    let shown  = 0;
    transcriptInterval = setInterval(() => {
      if (!audio) return;
      const nowMs = audio.currentTime * 1000;
      while (shown < msgs.length && tss[shown] <= nowMs + 200) {
        addTranscriptMsg(msgs[shown]);
        showSpeaking(msgs[shown].speaker);
        shown++;
      }
    }, 100);
  } else {
    // No audio — simulate with timing
    simulateCall(call, nextState);
  }
}

function simulateCall(call, nextState) {
  const msgs  = call.transcript || [];
  const tss   = call.timestamps || msgs.map((_, i) => i * 3500);
  const total = (tss[tss.length-1] || (msgs.length * 3500)) + 3000;

  msgs.forEach((msg, i) => {
    setTimeout(() => {
      addTranscriptMsg(msg);
      showSpeaking(msg.speaker);
    }, tss[i] || i * 3500);
  });

  setTimeout(() => {
    clearInterval(timerInterval);
    showSpeaking(null);
    setState(nextState);
  }, total);
}

function addTranscriptMsg(msg) {
  const box = document.getElementById('transcript-box');
  const div = document.createElement('div');
  div.className = 'tr-msg visible';
  div.innerHTML = `
    <div class="tr-role ${msg.speaker}">${msg.speaker}</div>
    <div class="tr-text">${msg.text}</div>`;
  box.appendChild(div);
  box.scrollTop = box.scrollHeight;
}

function showSpeaking(who) {
  ['agent','student'].forEach(r => {
    document.getElementById('spk-' + r)?.classList.toggle('speaking', r === who);
    const sw = document.getElementById('sw-' + r);
    if (sw) sw.style.display = r === who ? 'flex' : 'none';
  });
}

function onCallDone(callIdx, nextState) {
  const call = D.demo_calls[callIdx];
  callsProcessed++;
  completedCalls.push(call);

  // Update queue
  const tier = call.tier;
  if (callIdx === seq[0]) {
    updateQueueStatus(0, tier.toLowerCase(), `${tier === 'HOT' ? '🔥' : tier === 'WARM' ? '🔶' : '❄️'} ${tier}`);
  }

  // Show analyzing
  showAcState('analyzing');
  document.getElementById('status-meta').textContent = `${callsProcessed} call${callsProcessed > 1 ? 's' : ''} processed today`;

  setTimeout(() => {
    showScoringReveal(call);
    addRecentCall(call);
    setTimeout(() => setState(nextState), 4000);
  }, 2500);
}

function showScoringReveal(call) {
  showAcState('scoring');
  const tb = document.getElementById('tier-big');
  tb.className = `tier-big ${call.tier}`;
  tb.textContent = call.tier === 'HOT' ? '🔥 HOT' : call.tier === 'WARM' ? '🔶 WARM' : '❄️ COLD';
  document.getElementById('rule-score').textContent = call.rule_based_score;
  document.getElementById('ml-score').textContent   = call.ml_score;

  // Proba bars
  const pb = document.getElementById('proba-bars');
  pb.innerHTML = '';
  const COLOR = {HOT:'var(--hot)',WARM:'var(--warm)',COLD:'var(--cold)'};
  Object.entries(call.ml_proba || {}).forEach(([tier, pct]) => {
    const row = document.createElement('div');
    row.className = 'proba-row';
    row.innerHTML = `<span class="proba-label">${tier}</span>
      <div class="proba-bar-wrap"><div class="proba-fill" style="width:0%;background:${COLOR[tier]}" data-pct="${pct}"></div></div>
      <span class="proba-val">${pct}%</span>`;
    pb.appendChild(row);
  });
  setTimeout(() => {
    pb.querySelectorAll('.proba-fill').forEach(el => { el.style.width = el.dataset.pct + '%'; });
  }, 100);

  // Action cards
  const ac = document.getElementById('action-cards');
  ac.innerHTML = '';
  const actions = call.action_cards || {};
  if (actions.slack_message) {
    ac.innerHTML += `<div class="action-card">
      <div class="ac-header"><span class="ac-icon">💬</span><span class="ac-title">Slack Notification</span><span class="ac-status">✓ Sent</span></div>
      <div class="ac-content">${actions.slack_message.channel}</div>
      <div class="ac-label">${actions.slack_message.preview}</div>
    </div>`;
  }
  if (actions.email) {
    ac.innerHTML += `<div class="action-card">
      <div class="ac-header"><span class="ac-icon">📧</span><span class="ac-title">Email Sent</span><span class="ac-status">✓ Sent</span></div>
      <div class="ac-content">${actions.email.subject}</div>
      <div class="ac-label">${actions.email.preview}</div>
    </div>`;
  }
  if (actions.crm_record) {
    ac.innerHTML += `<div class="action-card">
      <div class="ac-header"><span class="ac-icon">📋</span><span class="ac-title">CRM Updated</span><span class="ac-status">✓ Done</span></div>
      <div class="ac-content">${actions.crm_record.status} · ${actions.crm_record.assigned_to}</div>
      <div class="ac-label">Follow up: ${actions.crm_record.follow_up}</div>
    </div>`;
  }
}

function onPause() {
  setTimeout(() => setState(STATES.INBOUND_ALERT), 2000);
}

function onInboundAlert() {
  // Show inbound indicators
  document.getElementById('inbound-empty').style.display  = 'none';
  document.getElementById('inbound-active').style.display = 'flex';
  document.getElementById('inbound-banner').style.display = 'flex';
  setTimeout(() => setState(STATES.INBOUND_ACTIVE), 2000);
}

function onComplete() {
  document.getElementById('inbound-empty').style.display  = 'flex';
  document.getElementById('inbound-active').style.display = 'none';
  document.getElementById('inbound-banner').style.display = 'none';

  // Update funnel counts for all completed calls
  completedCalls.forEach(call => {
    const tier = call.tier;
    const el   = document.getElementById('bcount-' + tier);
    if (el) el.textContent = parseInt(el.textContent) + 1;
  });
  document.getElementById('funnel-badge').style.display = 'block';

  // If idle was requested or queue exhausted, stop
  const queue = D.outbound_queue;
  if (idleRequested || outboundQueueIdx >= queue.length) {
    document.getElementById('status-text').textContent = idleRequested ? 'Agent Idle — Stopped by operator' : 'Agent Idle — Queue Complete';
    document.getElementById('restart-btn').style.display = 'block';
    document.getElementById('go-live-btn').style.display = 'none';
    showAcState('idle');
    document.getElementById('idle-state').querySelector('.idle-text').textContent = 'All calls processed. Click ↺ Restart to run again.';
    return;
  }

  // Pick next queue lead, synthesize a call using a template demo call
  const nextLead = queue[outboundQueueIdx];
  outboundQueueIdx++;
  const template  = D.demo_calls[outboundQueueIdx % D.demo_calls.length];
  const synthCall = Object.assign({}, template, {
    call_id:   'call_extra_' + outboundQueueIdx,
    call_type: 'outbound',
    student:   { name: nextLead.name, city: nextLead.city, exam: nextLead.exam, class: '12', lead_source: nextLead.source },
    audio_base64: '',  // simulate, no audio
  });
  D.demo_calls.push(synthCall);
  const newIdx = D.demo_calls.length - 1;

  document.getElementById('status-text').textContent = 'Agent Live — Processing Calls';
  updateQueueStatus(outboundQueueIdx - 1, 'inprogress', '● In Progress');

  // Override state machine to go directly to outbound active with new index
  showAcState('call');
  setTimeout(() => onCallActiveWith(newIdx, STATES.OUTBOUND_DONE), 800);
}

// ── UI helpers ─────────────────────────────────────────────────────────────────
function showAcState(which) {
  document.getElementById('idle-state').style.display     = which === 'idle'      ? 'flex'  : 'none';
  document.getElementById('call-card').style.display      = which === 'call'      ? 'block' : 'none';
  document.getElementById('analyzing-card').style.display = which === 'analyzing' ? 'flex'  : 'none';
  document.getElementById('scoring-card').style.display   = which === 'scoring'   ? 'block' : 'none';
  const ctrl = document.getElementById('call-controls');
  if (ctrl) ctrl.classList.toggle('visible', which === 'call');
}

function updateQueueStatus(idx, cls, label) {
  const el = document.getElementById('qstatus-' + idx);
  if (el) { el.className = `q-status qs-${cls}`; el.textContent = label; }
}

function addRecentCall(call) {
  const TIER_COLOR = {HOT:'var(--hot)',WARM:'var(--warm)',COLD:'var(--cold)'};
  const html = `<div class="recent-call" onclick='openDetail(${JSON.stringify(call).replace(/'/g, "&#39;")})'>
    <div class="rc-top">
      <div class="rc-name">${call.student?.name || 'Student'}</div>
      <span class="tier-badge tb-${call.tier}">${call.tier}</span>
    </div>
    <div class="rc-meta">${call.student?.city || ''} · ${call.student?.exam || ''} · Score: ${call.ml_score}</div>
  </div>`;

  // Update both panels
  ['recent-calls-list','ac-recent-list'].forEach(id => {
    const el = document.getElementById(id);
    if (el.querySelector('[style*="padding:30px"]')) el.innerHTML = '';
    el.insertAdjacentHTML('afterbegin', html);
  });
}

// ── Detail panel ───────────────────────────────────────────────────────────────
function openDetail(call) {
  if (typeof call === 'string') call = JSON.parse(call);
  const s = call.student || {};
  document.getElementById('dp-name').textContent = s.name || 'Student';
  document.getElementById('dp-meta').textContent = `${s.city || ''} · ${s.exam || ''} · Class ${s.class || '?'} · ${call.call_type}`;

  const dm_labels = {self:'Self',parent_present:'Parent Present',parent_later:'Parent Later'};
  const ef = call.extracted_fields || {};
  document.getElementById('dp-fields').innerHTML = `
    <div class="dp-field"><div class="dpf-label">Engagement</div><div class="dpf-val" style="text-transform:capitalize">${ef.engagement_level || '—'}</div></div>
    <div class="dp-field"><div class="dpf-label">Budget Concern</div><div class="dpf-val">${ef.budget_concern ? '⚠️ Yes' : '✅ No'}</div></div>
    <div class="dp-field"><div class="dpf-label">Decision Maker</div><div class="dpf-val">${dm_labels[ef.decision_maker] || ef.decision_maker || '—'}</div></div>
    <div class="dp-field"><div class="dpf-label">Months to Exam</div><div class="dpf-val">${ef.months_to_exam || '—'}</div></div>
    <div class="dp-field"><div class="dpf-label">ML Score</div><div class="dpf-val" style="color:var(--brand)">${call.ml_score}</div></div>
    <div class="dp-field"><div class="dpf-label">QA Validated</div><div class="dpf-val" style="color:var(--success)">✓ Yes</div></div>`;

  const tc = {HOT:'var(--hot)',WARM:'var(--warm)',COLD:'var(--cold)'};
  document.getElementById('dp-scores').innerHTML = `
    <div class="score-box" style="flex:1;text-align:center"><div class="sb-label">Rule-Based</div><div class="sb-val" style="color:var(--muted)">${call.rule_based_score}</div></div>
    <div class="score-box" style="flex:1;text-align:center"><div class="sb-label">ML Model</div><div class="sb-val" style="color:${tc[call.tier]}">${call.ml_score}</div></div>`;

  const tr = document.getElementById('dp-transcript');
  tr.innerHTML = (call.transcript || []).map(m => `
    <div style="display:flex;gap:8px;margin-bottom:6px">
      <div style="font-size:9px;font-weight:600;text-transform:uppercase;width:50px;color:${m.speaker==='agent'?'var(--brand)':'var(--warm)'};">${m.speaker}</div>
      <div style="font-size:11px;color:var(--text);line-height:1.5">${m.text}</div>
    </div>`).join('');

  document.getElementById('detail-overlay').classList.add('visible');
}

function closeDetail() {
  document.getElementById('detail-overlay').classList.remove('visible');
}

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') closeDetail();
});

// ── Call controls ──────────────────────────────────────────────────────────────
function skipToEnd() {
  const isOutbound = state === STATES.OUTBOUND_ACTIVE;
  const callIdx    = isOutbound ? seq[0] : seq[1];
  const call       = D.demo_calls[callIdx] || D.demo_calls[D.demo_calls.length - 1];
  if (!call) return;
  clearInterval(transcriptInterval);
  (call.transcript || []).forEach(msg => addTranscriptMsg(msg));
  showSpeaking(null);
  if (audio) { try { audio.currentTime = audio.duration || 9999; } catch(e) {} }
}

function endCall() {
  if (audio) { audio.pause(); audio = null; }
  clearInterval(timerInterval);
  clearInterval(transcriptInterval);
  showSpeaking(null);
  if (state === STATES.OUTBOUND_ACTIVE) setState(STATES.OUTBOUND_DONE);
  else if (state === STATES.INBOUND_ACTIVE) setState(STATES.INBOUND_DONE);
}

function goIdle() {
  idleRequested = !idleRequested;
  const btn = document.getElementById('idle-btn');
  if (btn) {
    btn.classList.toggle('requested', idleRequested);
    btn.textContent = idleRequested ? '⏸ Idle Requested' : '⏸ Go Idle';
  }
}

// ── New lead ticker ────────────────────────────────────────────────────────────
let newLeadPoolIdx = 0;
let newLeadCount   = D.pipeline_summary.new;

function startNewLeadTicker() {
  setInterval(() => {
    const lead = newLeadPool[newLeadPoolIdx % newLeadPool.length];
    newLeadPoolIdx++;

    // Show toast
    const toast = document.getElementById('new-lead-toast');
    document.getElementById('nlt-name').textContent = lead.name + ' — ' + lead.exam;
    document.getElementById('nlt-meta').textContent = lead.city + ' · ' + lead.source;
    toast.classList.add('show');
    setTimeout(() => toast.classList.remove('show'), 3000);

    // Update New Leads counter
    newLeadCount++;
    const el = document.getElementById('fn-new');
    if (el) el.textContent = newLeadCount;

    // Append to queue
    const body = document.getElementById('queue-body');
    const row  = document.createElement('div');
    row.className = 'queue-row';
    row.style.animation = 'slideDown 300ms ease';
    row.innerHTML = `
      <div><div class="qr-name">${lead.name}</div></div>
      <div><div class="qr-city">${lead.city}</div></div>
      <div><span class="qr-exam">${lead.exam}</span></div>
      <div><div class="qr-source">${lead.source}</div></div>
      <div><span class="q-status qs-queued">Queued</span></div>`;
    body.appendChild(row);
  }, 30000);
}

// ── Init ───────────────────────────────────────────────────────────────────────
buildQueue();
buildFunnel();
startNewLeadTicker();
</script>
</body>
</html>"""

page_html = HTML.replace("__PAGE_DATA__", data_json)
components.html(page_html, height=900, scrolling=False)

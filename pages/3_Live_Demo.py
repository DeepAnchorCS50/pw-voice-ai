"""
3_Live_Demo.py  —  PW Voice AI  —  Week 8
Full call experience with HTML component, live transcript sync, post-call analysis
"""

import streamlit as st
import streamlit.components.v1 as components
import sys, os, json, time, wave, io, base64, tempfile
import pandas as pd
import joblib

st.set_page_config(
    page_title="Live Demo — PW Voice AI",
    page_icon="🎙️",
    layout="wide"
)

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(ROOT, "src")
sys.path.insert(0, ROOT)
sys.path.insert(0, SRC)

# ── Cloud detection — show placeholder if not running locally ──────────────────
IS_CLOUD = os.path.exists('/mount/src')
if IS_CLOUD:
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .cloud-placeholder {
        font-family: 'Inter', sans-serif;
        max-width: 600px;
        margin: 80px auto;
        text-align: center;
        padding: 40px;
        background: #1a1d29;
        border: 1px solid #2d3148;
        border-radius: 16px;
    }
    .cp-icon { font-size: 48px; margin-bottom: 16px; }
    .cp-title { font-size: 22px; font-weight: 700; color: #e6e8f0; margin-bottom: 12px; }
    .cp-body { font-size: 14px; color: #8b8fa3; line-height: 1.6; margin-bottom: 24px; }
    .cp-badge {
        display: inline-block;
        background: #6366f114;
        border: 1px solid #6366f133;
        color: #6366f1;
        padding: 8px 20px;
        border-radius: 8px;
        font-size: 13px;
        font-weight: 500;
    }
    .cp-steps {
        text-align: left;
        margin-top: 24px;
        padding: 16px 20px;
        background: #0f1117;
        border-radius: 8px;
        font-size: 13px;
        color: #8b8fa3;
        line-height: 2;
    }
    </style>
    <div class="cloud-placeholder">
        <div class="cp-icon">📞</div>
        <div class="cp-title">Live AI Call Demo</div>
        <div class="cp-body">
            This feature generates real-time voice conversations using
            Google TTS and Claude AI, and requires local credentials
            that cannot be hosted in the cloud for security reasons.
        </div>
        <div class="cp-badge">🎙️ Available on Local Setup</div>
        <div class="cp-steps">
            <strong style="color:#e6e8f0">To run the Live Demo locally:</strong><br>
            1. Clone the repo to your machine<br>
            2. Add your API credentials to <code>config/</code><br>
            3. Run: <code>python -m streamlit run Home.py</code><br>
            4. Navigate to the Live Demo tab
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.stop()


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(ROOT, "config", "google_credentials.json")

KB_PATH      = os.path.join(ROOT, "pw_knowledge_base", "pw_knowledge_base.json")
MODEL_FILE   = os.path.join(SRC, "data", "lead_scoring_model.pkl")
ENCODER_FILE = os.path.join(SRC, "data", "label_encoders.pkl")

from config.api_keys import CLAUDE_API_KEY

FEATURE_COLS = [
    "current_class", "target_exam", "exam_year",
    "urgency_level", "budget_concern", "decision_maker", "engagement_level"
]

AGENT_VOICE          = "hi-IN-Chirp3-HD-Aoede"
STUDENT_VOICE_MALE   = "hi-IN-Chirp3-HD-Fenrir"
STUDENT_VOICE_FEMALE = "hi-IN-Chirp3-HD-Kore"
LANG                 = "hi-IN"
SAMPLE_RATE          = 24000
SILENCE_MS           = 500

FEMALE_NAMES = {
    "sneha","priya","pooja","anjali","neha","aarti","divya","meera","riya",
    "simran","ananya","kavya","ishita","shreya","tanvi","nisha","swati",
    "deepika","komal","preeti","sonal","richa","monika","sunita","geeta",
    "rekha","seema","usha","nandini"
}

# ── Load model ────────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    return joblib.load(MODEL_FILE), joblib.load(ENCODER_FILE)

model, encoders = load_model()

# ── Helpers ───────────────────────────────────────────────────────────────────
def tier_color(tier):
    return {"HOT":"#ff4b4b","WARM":"#ffa500","COLD":"#4b9fff"}.get(tier,"#888")

def tier_badge(tier):
    return {"HOT":"🔥 HOT","WARM":"🔶 WARM","COLD":"❄️ COLD"}.get(tier, tier)

def get_student_voice(name):
    return STUDENT_VOICE_FEMALE if name.strip().lower() in FEMALE_NAMES else STUDENT_VOICE_MALE

def ml_predict(scenario):
    try:
        engagement = scenario.get("engagement_level","medium")
        urgency    = "high" if engagement in ["very_high","high"] else "medium" if engagement == "medium" else "low"
        row = {
            "current_class":    str(scenario.get("class","11")),
            "target_exam":      scenario.get("exam","JEE Main"),
            "exam_year":        str(2025 + max(1, scenario.get("months_to_exam",12)//12)),
            "urgency_level":    urgency,
            "budget_concern":   "yes" if scenario.get("budget_concern") else "no",
            "decision_maker":   scenario.get("decision_maker","parent_later"),
            "engagement_level": engagement,
        }
        X = pd.DataFrame([{
            col: encoders[col].transform([str(row[col]).lower()])[0]
            if str(row[col]).lower() in encoders[col].classes_ else 0
            for col in FEATURE_COLS
        }])
        pred  = encoders["tier_label"].inverse_transform(model.predict(X))[0]
        proba = {
            encoders["tier_label"].inverse_transform([i])[0]: round(float(p)*100,1)
            for i,p in enumerate(model.predict_proba(X)[0])
        }
        return pred, proba
    except:
        return "UNKNOWN", {}

def synthesize_wav(tts_client, text, voice_name, speed=1.0):
    from google.cloud import texttospeech
    import re

    # Pronunciation fixes
    text = text.replace("PhysicsWallah", "Physics Wallah")
    text = text.replace("physicswallah", "Physics Wallah")
    text = re.sub(r'\bPW\b', 'P W', text)
    text = re.sub(r'\bJEE\b', 'J E E', text)
    text = re.sub(r'\bNEET\b', 'N E E T', text)

    # Prices: keep as plain English digits only — avoid Hindi number words
    def fix_price(m):
        num = int(m.group(1).replace(',', ''))
        # Format with commas for natural English reading e.g. "4,999 rupees"
        return f"{num:,} rupees"
    text = re.sub(r'₹([\d,]+)', fix_price, text)
    text = re.sub(r'Rs\.?\s*([\d,]+)', fix_price, text)

    r = tts_client.synthesize_speech(
        input=texttospeech.SynthesisInput(text=text),
        voice=texttospeech.VoiceSelectionParams(language_code=LANG, name=voice_name),
        audio_config=texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=speed, pitch=0.0, sample_rate_hertz=SAMPLE_RATE
        )
    )
    return r.audio_content

def get_wav_duration_ms(wav_bytes):
    with wave.open(io.BytesIO(wav_bytes), 'rb') as w:
        return int(w.getnframes() / w.getframerate() * 1000)

def merge_wav_with_timestamps(audio_chunks, silence_ms=SILENCE_MS):
    silence_frames = int(SAMPLE_RATE * silence_ms / 1000)
    silence_bytes  = b'\x00\x00' * silence_frames
    timestamps     = []
    current_ms     = 0
    out_buffer     = io.BytesIO()
    with wave.open(out_buffer, 'wb') as out_wav:
        out_wav.setnchannels(1)
        out_wav.setsampwidth(2)
        out_wav.setframerate(SAMPLE_RATE)
        for i, chunk in enumerate(audio_chunks):
            timestamps.append(current_ms)
            with wave.open(io.BytesIO(chunk), 'rb') as in_wav:
                out_wav.writeframes(in_wav.readframes(in_wav.getnframes()))
            current_ms += get_wav_duration_ms(chunk)
            if i < len(audio_chunks) - 1:
                out_wav.writeframes(silence_bytes)
                current_ms += silence_ms
    return out_buffer.getvalue(), timestamps

def generate_action_cards(transcript_text, scenario, tier):
    import anthropic
    client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)
    prompt = f"""You are analyzing a completed PhysicsWallah sales call.

TIER ASSIGNED: {tier}
STUDENT: {scenario.get('student_name','Student')} from {scenario.get('city','India')}, Class {scenario.get('class','?')}, preparing for {scenario.get('exam','?')}

TRANSCRIPT:
{transcript_text}

Generate post-call actions. Extract what the agent EXPLICITLY PROMISED in the conversation.

Return ONLY valid JSON, no other text:
{{
  "promised_actions": ["things agent explicitly promised e.g. Send enrollment link"],
  "recommended_actions": ["tier-based next steps beyond what was promised"],
  "slack_message": {{"channel": "#sales-leads", "preview": "2-3 line Slack message"}},
  "email": {{"to": "{scenario.get('student_name','Student')}", "subject": "personalized subject", "preview": "First 2 sentences of email body"}},
  "crm_record": {{"lead_id": "PW-{str(scenario.get('scenario_id','0000'))[-4:].upper()}", "status": "Hot Lead or Warm Lead or Cold Lead", "assigned_team": "Senior Sales or Standard Sales or Nurture Campaign", "follow_up_date": "specific date", "notes": "1 line note"}}
}}"""
    try:
        r    = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1000,
            messages=[{"role":"user","content":prompt}]
        )
        text  = r.content[0].text.strip()
        start = text.find('{')
        end   = text.rfind('}') + 1
        return json.loads(text[start:end])
    except Exception as e:
        return {
            "promised_actions":   ["Send course details"],
            "recommended_actions":["Follow up in 3 days"],
            "slack_message":      {"channel":"#sales-leads","preview":"Call completed."},
            "email":              {"to":scenario.get('student_name','Student'),"subject":"Your PW enquiry","preview":"Thank you for your interest."},
            "crm_record":         {"lead_id":"PW-0000","status":"Warm Lead","assigned_team":"Standard Sales","follow_up_date":"Soon","notes":"Follow up required."}
        }

# ── Full generation pipeline ──────────────────────────────────────────────────
def generate_demo(call_type, status_fn):
    from agents.scenario_planner import ScenarioPlanner
    from agents.conversation_generator import ConversationGenerator
    from google.cloud import texttospeech

    status_fn("🧠 Designing student profile...")
    planner  = ScenarioPlanner(KB_PATH)
    scenario = planner.generate_scenario(call_type=call_type)

    status_fn(f"💬 Generating conversation for {scenario['student_name']} from {scenario['city']}...")
    gen  = ConversationGenerator(CLAUDE_API_KEY, KB_PATH)
    conv = gen.generate(scenario)
    if conv.get("failed"):
        raise Exception(f"Conversation failed: {conv.get('error')}")
    messages = conv.get("messages", [])

    status_fn(f"🔊 Converting {len(messages)} messages to voice...")
    tts_client    = texttospeech.TextToSpeechClient()
    student_voice = get_student_voice(scenario.get("student_name",""))
    audio_chunks  = []
    for msg in messages:
        voice = AGENT_VOICE if msg["speaker"] == "agent" else student_voice
        speed = 0.95 if msg["speaker"] == "agent" else 1.05
        audio_chunks.append(synthesize_wav(tts_client, msg["text"], voice, speed))

    status_fn("🎵 Merging audio with timestamps...")
    merged_wav, timestamps = merge_wav_with_timestamps(audio_chunks)
    audio_b64 = base64.b64encode(merged_wav).decode()

    status_fn("📊 Scoring lead...")
    ml_tier, ml_proba = ml_predict(scenario)

    status_fn("⚡ Generating post-call action cards...")
    transcript_text = "\n".join([f"{m['speaker'].upper()}: {m['text']}" for m in messages])
    actions = generate_action_cards(transcript_text, scenario, ml_tier)

    return {
        "call_type":  call_type,
        "scenario":   scenario,
        "messages":   messages,
        "timestamps": timestamps,
        "audio_b64":  audio_b64,
        "ml_tier":    ml_tier,
        "ml_proba":   ml_proba,
        "actions":    actions,
    }

# ── HTML Component ────────────────────────────────────────────────────────────
def build_html_component(demo_data):
    scenario   = demo_data["scenario"]
    messages   = demo_data["messages"]
    timestamps = demo_data["timestamps"]
    audio_b64  = demo_data["audio_b64"]
    ml_tier    = demo_data["ml_tier"]
    ml_proba   = demo_data["ml_proba"]
    actions    = demo_data["actions"]
    call_type  = demo_data["call_type"]
    color      = tier_color(ml_tier)
    badge      = tier_badge(ml_tier)

    msgs_js  = json.dumps(messages)
    ts_js    = json.dumps(timestamps)
    proba_js = json.dumps(ml_proba)
    acts_js  = json.dumps(actions)
    sc_js    = json.dumps({
        "name":      scenario.get("student_name","Student"),
        "city":      scenario.get("city",""),
        "class":     scenario.get("class",""),
        "exam":      scenario.get("exam",""),
        "source":    scenario.get("lead_source",""),
        "call_type": call_type,
    })

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Inter', sans-serif; background: #0f1117; color: #e8eaf0; padding: 20px; }}

  /* STATE 1 */
  #state-ready {{ display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:380px; gap:28px; }}
  .ready-title {{ font-size:26px; font-weight:600; color:#fff; text-align:center; }}
  .ready-sub {{ font-size:13px; color:#8b8fa8; text-align:center; margin-top:-18px; }}
  .call-buttons {{ display:flex; gap:14px; }}
  .call-btn {{ padding:14px 28px; border-radius:10px; border:none; font-family:'Inter',sans-serif; font-size:14px; font-weight:500; cursor:pointer; transition:all 0.2s; display:flex; align-items:center; gap:8px; }}
  .btn-inbound {{ background:#6366f1; color:white; }}
  .btn-inbound:hover {{ background:#1557b0; transform:translateY(-2px); }}
  .btn-outbound {{ background:#1e1e2e; color:#e8eaf0; border:1px solid #2d2d3f; }}
  .btn-outbound:hover {{ background:#252535; transform:translateY(-2px); }}

  /* STATE 2 */
  #state-call {{ display:none; }}
  .call-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:20px; padding-bottom:14px; border-bottom:1px solid #1e1e2e; }}
  .call-badge {{ display:flex; align-items:center; gap:8px; background:#1a1a2e; padding:5px 12px; border-radius:20px; font-size:11px; color:#8b8fa8; text-transform:uppercase; letter-spacing:1px; }}
  .live-dot {{ width:7px; height:7px; background:#22c55e; border-radius:50%; animation:pulse 1.5s infinite; }}
  @keyframes pulse {{ 0%,100%{{opacity:1;transform:scale(1)}} 50%{{opacity:0.5;transform:scale(0.8)}} }}
  .call-timer {{ font-family:'JetBrains Mono',monospace; font-size:20px; color:#fff; letter-spacing:2px; }}
  .speakers-row {{ display:flex; gap:14px; margin-bottom:18px; }}
  .speaker-card {{ flex:1; background:#1a1a2e; border-radius:10px; padding:14px; display:flex; align-items:center; gap:10px; border:1px solid #2d2d3f; transition:border-color 0.3s,background 0.3s; }}
  .speaker-card.speaking {{ border-color:#6366f1; background:#0d1a2e; }}
  .speaker-avatar {{ width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:18px; background:#252535; flex-shrink:0; }}
  .speaker-name {{ font-size:13px; font-weight:500; color:#fff; }}
  .speaker-role {{ font-size:11px; color:#8b8fa8; margin-top:2px; }}
  .sound-wave {{ display:flex; align-items:center; gap:2px; margin-left:auto; height:18px; opacity:0; transition:opacity 0.3s; }}
  .speaker-card.speaking .sound-wave {{ opacity:1; }}
  .sound-wave span {{ display:block; width:3px; background:#6366f1; border-radius:2px; animation:wave 0.8s ease-in-out infinite; }}
  .sound-wave span:nth-child(1){{height:5px;animation-delay:0s}}
  .sound-wave span:nth-child(2){{height:12px;animation-delay:0.1s}}
  .sound-wave span:nth-child(3){{height:8px;animation-delay:0.2s}}
  .sound-wave span:nth-child(4){{height:16px;animation-delay:0.15s}}
  .sound-wave span:nth-child(5){{height:7px;animation-delay:0.05s}}
  @keyframes wave {{ 0%,100%{{transform:scaleY(0.4)}} 50%{{transform:scaleY(1)}} }}
  .context-panel {{ background:#1a1a2e; border-radius:10px; padding:12px 14px; margin-bottom:16px; border:1px solid #2d2d3f; font-size:12px; color:#8b8fa8; display:flex; gap:20px; flex-wrap:wrap; }}
  .context-panel strong {{ color:#c8cadb; }}
  .live-transcript {{ background:#1a1a2e; border-radius:10px; padding:14px; height:160px; overflow-y:auto; border:1px solid #2d2d3f; }}
  .msg-bubble {{ margin-bottom:8px; opacity:0; transform:translateY(6px); transition:opacity 0.4s,transform 0.4s; }}
  .msg-bubble.visible {{ opacity:1; transform:translateY(0); }}
  .msg-speaker {{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:2px; }}
  .msg-speaker.agent {{ color:#6366f1; }}
  .msg-speaker.student {{ color:#f59e0b; }}
  .msg-text {{ font-size:12px; color:#c8cadb; line-height:1.5; }}

  /* STATE ANALYZING */
  #state-analyzing {{ display:none; flex-direction:column; align-items:center; justify-content:center; min-height:280px; gap:16px; }}
  .analyzing-text {{ font-size:17px; color:#fff; font-weight:500; }}
  .analyzing-dots span {{ animation:blink 1.4s infinite; font-size:22px; color:#6366f1; }}
  .analyzing-dots span:nth-child(2){{animation-delay:0.2s}}
  .analyzing-dots span:nth-child(3){{animation-delay:0.4s}}
  @keyframes blink {{ 0%,80%,100%{{opacity:0}} 40%{{opacity:1}} }}

  /* STATE POSTCALL */
  #state-postcall {{ display:none; }}
  .postcall-header {{ display:flex; align-items:center; justify-content:space-between; margin-bottom:16px; }}
  .tier-badge-large {{ padding:7px 18px; border-radius:18px; font-size:15px; font-weight:600; }}
  .postcall-grid {{ display:grid; grid-template-columns:1.2fr 1fr; gap:14px; margin-bottom:14px; }}
  .panel {{ background:#1a1a2e; border-radius:10px; padding:14px; border:1px solid #2d2d3f; }}
  .panel-title {{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:1px; color:#8b8fa8; margin-bottom:10px; }}
  .transcript-scroll {{ max-height:240px; overflow-y:auto; }}
  .tr-msg {{ margin-bottom:8px; }}
  .tr-speaker {{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:0.8px; margin-bottom:2px; }}
  .tr-speaker.agent {{ color:#6366f1; }}
  .tr-speaker.student {{ color:#f59e0b; }}
  .tr-text {{ font-size:12px; color:#c8cadb; line-height:1.5; }}
  .score-display {{ text-align:center; padding:14px; border-radius:8px; margin-bottom:10px; border:2px solid; }}
  .score-tier {{ font-size:20px; font-weight:700; }}
  .score-label {{ font-size:11px; color:#8b8fa8; margin-top:3px; }}
  .proba-row {{ display:flex; align-items:center; gap:8px; margin-bottom:5px; font-size:12px; }}
  .proba-label {{ width:50px; color:#8b8fa8; }}
  .proba-bar-wrap {{ flex:1; background:#0f1117; border-radius:3px; height:5px; }}
  .proba-bar {{ height:5px; border-radius:3px; transition:width 1s ease; }}
  .proba-val {{ width:34px; text-align:right; color:#c8cadb; font-family:'JetBrains Mono',monospace; font-size:11px; }}
  .actions-grid {{ display:grid; grid-template-columns:1fr 1fr 1fr; gap:12px; margin-bottom:12px; }}
  .action-card {{ background:#1a1a2e; border-radius:10px; padding:13px; border:1px solid #2d2d3f; }}
  .action-card-title {{ font-size:10px; font-weight:600; text-transform:uppercase; letter-spacing:1px; color:#8b8fa8; margin-bottom:8px; display:flex; align-items:center; gap:5px; }}
  .slack-preview {{ background:#0f1117; border-radius:5px; padding:7px 9px; font-size:12px; color:#c8cadb; line-height:1.5; border-left:3px solid #4a154b; }}
  .email-subject {{ font-weight:500; color:#fff; margin-bottom:3px; font-size:12px; }}
  .email-preview {{ color:#8b8fa8; line-height:1.5; font-size:12px; }}
  .crm-field {{ display:flex; justify-content:space-between; margin-bottom:4px; font-size:12px; }}
  .crm-key {{ color:#8b8fa8; }}
  .crm-val {{ color:#c8cadb; font-weight:500; }}
  .promised-list {{ list-style:none; }}
  .promised-list li {{ padding:3px 0; color:#c8cadb; display:flex; align-items:flex-start; gap:6px; font-size:12px; }}
  .promised-list li::before {{ content:"✓"; color:#22c55e; font-weight:700; flex-shrink:0; }}
  .reset-btn {{ background:#1a1a2e; color:#8b8fa8; border:1px solid #2d2d3f; padding:9px 22px; border-radius:7px; font-family:'Inter',sans-serif; font-size:13px; cursor:pointer; transition:all 0.2s; margin-top:8px; }}
  .reset-btn:hover {{ background:#252535; color:#fff; }}
  ::-webkit-scrollbar {{ width:3px; }}
  ::-webkit-scrollbar-track {{ background:#0f1117; }}
  ::-webkit-scrollbar-thumb {{ background:#2d2d3f; border-radius:2px; }}
</style>
</head>
<body>

<div id="state-ready">
  <div>
    <div class="ready-title">🎙️ PW Voice AI</div>
    <div class="ready-sub">Sales Intelligence Platform — Ready</div>
  </div>
  <div class="call-buttons">
    <button class="call-btn btn-inbound" onclick="startCall('inbound')">📞 Incoming Call</button>
    <button class="call-btn btn-outbound" onclick="startCall('outbound')">📱 Make Outbound Call</button>
  </div>
</div>

<div id="state-call">
  <div class="call-header">
    <div class="call-badge"><div class="live-dot"></div><span id="call-type-label">Call in progress</span></div>
    <div class="call-timer" id="timer">00:00</div>
  </div>
  <div id="context-panel-wrap"></div>
  <div class="speakers-row">
    <div class="speaker-card" id="card-agent">
      <div class="speaker-avatar">🤖</div>
      <div><div class="speaker-name">Priya</div><div class="speaker-role">PW Sales Agent</div></div>
      <div class="sound-wave"><span></span><span></span><span></span><span></span><span></span></div>
    </div>
    <div class="speaker-card" id="card-student">
      <div class="speaker-avatar">👤</div>
      <div><div class="speaker-name" id="student-name-label">Student</div><div class="speaker-role" id="student-role-label">Caller</div></div>
      <div class="sound-wave"><span></span><span></span><span></span><span></span><span></span></div>
    </div>
  </div>
  <div class="live-transcript" id="live-transcript"></div>
  <audio id="call-audio" style="display:none"></audio>
</div>

<div id="state-analyzing">
  <div class="analyzing-text">Analyzing conversation</div>
  <div class="analyzing-dots"><span>.</span><span>.</span><span>.</span></div>
</div>

<div id="state-postcall">
  <div class="postcall-header">
    <div style="font-size:15px;font-weight:600;color:#fff;">📋 Call Analysis</div>
    <div class="tier-badge-large" id="tier-reveal" style="background:{color}22;color:{color};border:1px solid {color};opacity:0;transition:opacity 0.8s">{badge}</div>
  </div>
  <div class="postcall-grid">
    <div class="panel"><div class="panel-title">💬 Transcript</div><div class="transcript-scroll" id="full-transcript"></div></div>
    <div class="panel">
      <div class="panel-title">📊 Lead Score</div>
      <div class="score-display" style="background:{color}11;border-color:{color}">
        <div class="score-tier" style="color:{color}">{badge}</div>
        <div class="score-label">ML Prediction</div>
      </div>
      <div id="proba-bars"></div>
    </div>
  </div>
  <div class="actions-grid">
    <div class="action-card"><div class="action-card-title">✅ Agent Promised</div><ul class="promised-list" id="promised-list"></ul></div>
    <div class="action-card"><div class="action-card-title"><span style="color:#4a154b">■</span> Slack</div><div class="slack-preview" id="slack-preview"></div></div>
    <div class="action-card"><div class="action-card-title">✉️ Email</div><div class="email-subject" id="email-subject"></div><div class="email-preview" id="email-preview"></div></div>
  </div>
  <div class="actions-grid">
    <div class="action-card"><div class="action-card-title">🗂️ CRM Record</div><div id="crm-fields"></div></div>
    <div class="action-card" style="grid-column:span 2"><div class="action-card-title">⚡ Recommended Next Steps</div><ul class="promised-list" id="recommended-list"></ul></div>
  </div>
  <button class="reset-btn" onclick="resetDemo()">↩ New Call</button>
</div>

<script>
  const MESSAGES   = {msgs_js};
  const TIMESTAMPS = {ts_js};
  const AUDIO_B64  = "{audio_b64}";
  const ML_PROBA   = {proba_js};
  const ACTIONS    = {acts_js};
  const SCENARIO   = {sc_js};

  let timerInterval = null;
  let timerSeconds  = 0;
  let audioEl       = null;
  let syncInterval  = null;
  let shownMsgs     = new Set();

  function startCall(type) {{
    document.getElementById('state-ready').style.display = 'none';
    document.getElementById('state-call').style.display  = 'block';
    document.getElementById('call-type-label').textContent = type === 'inbound' ? '📞 Inbound — PW Helpline' : '📱 Outbound Call';
    document.getElementById('student-name-label').textContent = SCENARIO.name;
    document.getElementById('student-role-label').textContent = type === 'inbound' ? 'Caller' : SCENARIO.city;

    if (type === 'outbound') {{
      document.getElementById('context-panel-wrap').innerHTML = `
        <div class="context-panel">
          <div><strong>Name</strong><br>${{SCENARIO.name}}</div>
          <div><strong>City</strong><br>${{SCENARIO.city}}</div>
          <div><strong>Exam</strong><br>${{SCENARIO.exam}}</div>
          <div><strong>Lead Source</strong><br>${{SCENARIO.source}}</div>
        </div>`;
    }}

    timerSeconds  = 0;
    timerInterval = setInterval(() => {{
      timerSeconds++;
      const m = String(Math.floor(timerSeconds/60)).padStart(2,'0');
      const s = String(timerSeconds%60).padStart(2,'0');
      document.getElementById('timer').textContent = m+':'+s;
    }}, 1000);

    audioEl     = document.getElementById('call-audio');
    audioEl.src = 'data:audio/wav;base64,' + AUDIO_B64;
    audioEl.play();
    syncInterval = setInterval(syncTranscript, 100);
    audioEl.onended = () => {{
      clearInterval(timerInterval);
      clearInterval(syncInterval);
      showAllMessages();
      setTimeout(showAnalyzing, 600);
    }};
  }}

  function syncTranscript() {{
    if (!audioEl) return;
    const currentMs = audioEl.currentTime * 1000;
    let currentSpeaker = null;
    for (let i = 0; i < TIMESTAMPS.length; i++) {{
      const nextTs = i < TIMESTAMPS.length-1 ? TIMESTAMPS[i+1] : Infinity;
      if (currentMs >= TIMESTAMPS[i] && currentMs < nextTs) {{ currentSpeaker = MESSAGES[i].speaker; break; }}
    }}
    document.getElementById('card-agent').classList.toggle('speaking', currentSpeaker === 'agent');
    document.getElementById('card-student').classList.toggle('speaking', currentSpeaker === 'student');
    for (let i = 0; i < TIMESTAMPS.length; i++) {{
      if (currentMs >= TIMESTAMPS[i] + 300 && !shownMsgs.has(i)) {{
        shownMsgs.add(i);
        addMsg(i);
      }}
    }}
  }}

  function addMsg(i) {{
    const msg = MESSAGES[i];
    const div = document.createElement('div');
    div.className = 'msg-bubble';
    div.innerHTML = `<div class="msg-speaker ${{msg.speaker}}">${{msg.speaker==='agent'?'Priya':SCENARIO.name}}</div><div class="msg-text">${{msg.text}}</div>`;
    const c = document.getElementById('live-transcript');
    c.appendChild(div);
    setTimeout(() => div.classList.add('visible'), 50);
    c.scrollTop = c.scrollHeight;
  }}

  function showAllMessages() {{
    for (let i = 0; i < MESSAGES.length; i++) {{
      if (!shownMsgs.has(i)) {{ shownMsgs.add(i); addMsg(i); }}
    }}
  }}

  function showAnalyzing() {{
    document.getElementById('state-call').style.display      = 'none';
    document.getElementById('state-analyzing').style.display = 'flex';
    setTimeout(showPostCall, 2500);
  }}

  function showPostCall() {{
    document.getElementById('state-analyzing').style.display = 'none';
    document.getElementById('state-postcall').style.display  = 'block';
    setTimeout(() => {{ document.getElementById('tier-reveal').style.opacity = '1'; }}, 800);
        const tr = document.getElementById('full-transcript');
    MESSAGES.forEach(m => {{
      tr.innerHTML += `<div class="tr-msg"><div class="tr-speaker ${{m.speaker}}">${{m.speaker==='agent'?'Priya':SCENARIO.name}}</div><div class="tr-text">${{m.text}}</div></div>`;
    }});
    const colors = {{HOT:'#ff4b4b',WARM:'#ffa500',COLD:'#4b9fff'}};
    const pb = document.getElementById('proba-bars');
    ['HOT','WARM','COLD'].forEach(t => {{
      const val = ML_PROBA[t]||0;
      pb.innerHTML += `<div class="proba-row"><div class="proba-label">${{t}}</div><div class="proba-bar-wrap"><div class="proba-bar" style="width:${{val}}%;background:${{colors[t]}}"></div></div><div class="proba-val">${{val}}%</div></div>`;
    }});
    const pl = document.getElementById('promised-list');
    (ACTIONS.promised_actions||[]).forEach(a => {{ pl.innerHTML += `<li>${{a}}</li>`; }});
    document.getElementById('slack-preview').textContent  = (ACTIONS.slack_message||{{}}).preview||'';
    document.getElementById('email-subject').textContent  = (ACTIONS.email||{{}}).subject||'';
    document.getElementById('email-preview').textContent  = (ACTIONS.email||{{}}).preview||'';
    const crm = ACTIONS.crm_record||{{}};
    const cf  = document.getElementById('crm-fields');
    [['Lead ID',crm.lead_id],['Status',crm.status],['Team',crm.assigned_team],['Follow-up',crm.follow_up_date],['Notes',crm.notes]].forEach(([k,v]) => {{
      cf.innerHTML += `<div class="crm-field"><span class="crm-key">${{k}}</span><span class="crm-val">${{v||'—'}}</span></div>`;
    }});
    const rl = document.getElementById('recommended-list');
    (ACTIONS.recommended_actions||[]).forEach(a => {{ rl.innerHTML += `<li>${{a}}</li>`; }});
  }}

  function resetDemo() {{
    document.getElementById('state-postcall').style.display  = 'none';
    document.getElementById('state-ready').style.display     = 'flex';
    shownMsgs = new Set();
    ['live-transcript','full-transcript','proba-bars','promised-list','recommended-list','crm-fields','context-panel-wrap'].forEach(id => {{
      document.getElementById(id).innerHTML = '';
    }});
    document.getElementById('timer').textContent = '00:00';
  }}
</script>
</body>
</html>"""

# ── Page UI ───────────────────────────────────────────────────────────────────
st.title("🎙️ Live Demo")
st.caption("PhysicsWallah Voice AI — Sales Intelligence Platform")
st.markdown("---")

col_left, col_right = st.columns([1, 3])

with col_left:
    st.subheader("Prepare Demo")
    call_type_choice = st.radio("Pre-generate call type", ["📞 Inbound", "📱 Outbound"], index=0)
    call_type_map    = {"📞 Inbound":"inbound","📱 Outbound":"outbound"}
    selected_call_type = call_type_map[call_type_choice]
    prepare_btn = st.button("⚡ Prepare Demo", type="primary", use_container_width=True)

    if "demo_data" in st.session_state:
        d = st.session_state["demo_data"]
        st.markdown("---")
        st.caption("✅ Ready to demo")
        st.caption(f"Student: **{d['scenario'].get('student_name','?')}**")
        st.caption(f"Call type: **{d['call_type'].title()}**")
        st.caption(f"Tier: **{d['ml_tier']}**")
        st.caption(f"Messages: **{len(d['messages'])}**")

with col_right:
    if "demo_data" in st.session_state:
        html = build_html_component(st.session_state["demo_data"])
        components.html(html, height=700, scrolling=True)
    else:
        st.info("👈 Click **Prepare Demo** to pre-generate a call. The demo will be instant once ready.")

if prepare_btn:
    status_placeholder = col_right.empty()

    def update_status(msg):
        status_placeholder.info(msg)

    with st.spinner("Preparing demo (~20 seconds)..."):
        try:
            demo_data = generate_demo(selected_call_type, update_status)
            st.session_state["demo_data"] = demo_data
            status_placeholder.empty()
            st.rerun()
        except Exception as e:
            status_placeholder.error(f"❌ Error: {e}")
            st.exception(e)
import streamlit as st
import json
import os
import pandas as pd
import joblib

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PW Lead Scoring Dashboard",
    page_icon="🎯",
    layout="wide"
)

# ── Paths ─────────────────────────────────────────────────────────────────────
CONV_DIR = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\conversations"
LEADS_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\processed_leads.json"
MODEL_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\lead_scoring_model.pkl"
ENCODER_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\label_encoders.pkl"

FEATURE_COLS = [
    "current_class", "target_exam", "exam_year",
    "urgency_level", "budget_concern", "decision_maker", "engagement_level"
]

# ── Load data and model ───────────────────────────────────────────────────────
@st.cache_data
def load_leads():
    with open(LEADS_FILE, "r") as f:
        return json.load(f)

@st.cache_data
def load_conversation(conv_id):
    filepath = os.path.join(CONV_DIR, "{}.json".format(conv_id))
    with open(filepath, "r", encoding="utf-8") as f:
        return json.load(f)

@st.cache_resource
def load_model():
    model = joblib.load(MODEL_FILE)
    encoders = joblib.load(ENCODER_FILE)
    return model, encoders

leads = load_leads()
model, encoders = load_model()
leads_dict = {l["conversation_id"]: l for l in leads}

# ── ML scoring function ───────────────────────────────────────────────────────
def ml_predict(lead):
    """Run ML model on a single lead and return predicted tier + probabilities."""
    try:
        row = {}
        for col in FEATURE_COLS:
            val = str(lead.get(col, "unknown")).lower()
            le = encoders[col]
            if val in le.classes_:
                row[col] = le.transform([val])[0]
            else:
                row[col] = 0
        X = pd.DataFrame([row])
        pred_encoded = model.predict(X)[0]
        proba = model.predict_proba(X)[0]
        target_encoder = encoders["tier_label"]
        pred_tier = target_encoder.inverse_transform([pred_encoded])[0]
        proba_dict = {
            target_encoder.inverse_transform([i])[0]: round(float(p) * 100, 1)
            for i, p in enumerate(proba)
        }
        return pred_tier, proba_dict
    except Exception as e:
        return "UNKNOWN", {}

# ── Tier styling ──────────────────────────────────────────────────────────────
def tier_badge(tier):
    if tier == "HOT":
        return "🔥 HOT"
    elif tier == "WARM":
        return "🔶 WARM"
    else:
        return "❄️ COLD"

def tier_color(tier):
    if tier == "HOT":
        return "#ff4b4b"
    elif tier == "WARM":
        return "#ffa500"
    else:
        return "#4b9fff"

# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.title("🎯 PW Lead Scoring")
st.sidebar.markdown("---")

st.sidebar.subheader("Filter by Tier")
show_hot = st.sidebar.checkbox("🔥 HOT", value=True)
show_warm = st.sidebar.checkbox("🔶 WARM", value=True)
show_cold = st.sidebar.checkbox("❄️ COLD", value=True)

filtered = [
    l for l in leads
    if (l.get("tier_label") == "HOT" and show_hot)
    or (l.get("tier_label") == "WARM" and show_warm)
    or (l.get("tier_label") == "COLD" and show_cold)
]

st.sidebar.markdown("---")
st.sidebar.subheader("Select a Lead")
st.sidebar.caption("{} leads shown".format(len(filtered)))

options = [
    "{} — {} ({}/100)".format(
        l["conversation_id"],
        tier_badge(l.get("tier_label", "?")),
        l.get("score", 0)
    )
    for l in filtered
]

selected_option = st.sidebar.selectbox("", options, label_visibility="collapsed")
selected_index = options.index(selected_option)
selected_lead = filtered[selected_index]
selected_conv_id = selected_lead["conversation_id"]

# ── Main Area ─────────────────────────────────────────────────────────────────
st.title("PW Lead Scoring Dashboard")
st.caption("PhysicsWallah Voice AI — Lead Analysis System")
st.markdown("---")

conversation = load_conversation(selected_conv_id)
messages = conversation.get("messages", [])

# Run ML prediction
ml_tier, ml_proba = ml_predict(selected_lead)

# Three columns: chat | rule-based | ML
col_chat, col_rules, col_ml = st.columns([2, 1, 1])

# ── Conversation ──────────────────────────────────────────────────────────────
with col_chat:
    st.subheader("💬 Conversation: {}".format(selected_conv_id))
    for msg in messages:
        speaker = msg.get("speaker", "")
        text = msg.get("text", "")
        if speaker == "agent":
            st.markdown(
                "<div style='background-color:#f0f2f6; padding:10px 15px;"
                "border-radius:15px 15px 15px 0px; margin:5px 0;"
                "max-width:80%; font-size:14px;'>"
                "<b>🤖 Priya</b><br>{}</div>".format(text),
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                "<div style='background-color:#e8f4fd; padding:10px 15px;"
                "border-radius:15px 15px 0px 15px; margin:5px 0;"
                "max-width:80%; font-size:14px;'>"
                "<b>👤 Student</b><br>{}</div>".format(text),
                unsafe_allow_html=True
            )
        st.markdown("<div style='margin:2px'></div>", unsafe_allow_html=True)

# ── Rule-based score ──────────────────────────────────────────────────────────
with col_rules:
    rule_tier = selected_lead.get("predicted_tier", "COLD")
    rule_score = selected_lead.get("score", 0)
    rule_color = tier_color(rule_tier)

    st.subheader("📏 Rule-Based")
    st.caption("scoring_engine.py")
    st.markdown(
        "<div style='text-align:center; padding:15px;"
        "background-color:{color}22; border-radius:10px;"
        "border: 2px solid {color}; margin-bottom:10px;'>"
        "<div style='font-size:40px; font-weight:bold; color:{color};'>{score}</div>"
        "<div style='font-size:13px; color:#666;'>out of 100</div>"
        "<div style='font-size:20px; margin-top:5px;'>{badge}</div>"
        "</div>".format(
            color=rule_color, score=rule_score, badge=tier_badge(rule_tier)
        ),
        unsafe_allow_html=True
    )
    st.progress(rule_score / 100)
    st.markdown("---")
    st.caption("Score Breakdown")
    breakdown = selected_lead.get("score_breakdown", {})
    if breakdown:
        for factor, points in breakdown.items():
            label = factor.replace("_", " ").title()
            st.caption("{}: {} pts".format(label, points))
            st.progress(points / 30)

# ── ML score ──────────────────────────────────────────────────────────────────
with col_ml:
    ml_color = tier_color(ml_tier)

    st.subheader("🤖 ML Model")
    st.caption("Random Forest (100 trees)")
    st.markdown(
        "<div style='text-align:center; padding:15px;"
        "background-color:{color}22; border-radius:10px;"
        "border: 2px solid {color}; margin-bottom:10px;'>"
        "<div style='font-size:36px; font-weight:bold; color:{color};'>{badge}</div>"
        "<div style='font-size:13px; color:#666; margin-top:5px;'>ML Prediction</div>"
        "</div>".format(color=ml_color, badge=tier_badge(ml_tier)),
        unsafe_allow_html=True
    )

    st.markdown("---")
    st.caption("Confidence by Tier")
    if ml_proba:
        for tier_name in ["HOT", "WARM", "COLD"]:
            prob = ml_proba.get(tier_name, 0)
            st.caption("{} — {}%".format(tier_badge(tier_name), prob))
            st.progress(prob / 100)

    st.markdown("---")
    if ml_tier == rule_tier:
        st.success("✅ Agrees with rule-based")
    else:
        st.warning("⚠️ Disagrees with rule-based")
        st.caption("Rule says: {}".format(tier_badge(rule_tier)))
        st.caption("ML says: {}".format(tier_badge(ml_tier)))

    st.markdown("---")
    st.subheader("📋 Details")
    details = [
        ("Name", selected_lead.get("full_name", "—")),
        ("Class", selected_lead.get("current_class", "—")),
        ("Exam", selected_lead.get("target_exam", "—")),
        ("Location", selected_lead.get("location", "—")),
        ("Urgency", selected_lead.get("urgency_level", "—")),
        ("Engagement", selected_lead.get("engagement_level", "—")),
        ("Decision", selected_lead.get("decision_maker", "—")),
    ]
    for label, value in details:
        c1, c2 = st.columns([1, 1])
        c1.caption(label)
        c2.write(value)
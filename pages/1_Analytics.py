import streamlit as st
import json
import pandas as pd

st.set_page_config(
    page_title="Analytics — PW Lead Scoring",
    page_icon="📊",
    layout="wide"
)

# ── Paths ─────────────────────────────────────────────────────────────────────
LEADS_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\processed_leads.json"
CSV_FILE = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone\src\data\synthetic_leads_dataset.csv"

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    with open(LEADS_FILE, "r") as f:
        leads = json.load(f)
    df = pd.DataFrame(leads)
    return df

df = load_data()

# ── Page header ───────────────────────────────────────────────────────────────
st.title("📊 Analytics Dashboard")
st.caption("Aggregate insights across all 100 synthetic leads")
st.markdown("---")

# ── Row 1: Key metrics ────────────────────────────────────────────────────────
st.subheader("Key Metrics")

col1, col2, col3, col4 = st.columns(4)

total = len(df)
hot_count = len(df[df["tier_label"] == "HOT"])
warm_count = len(df[df["tier_label"] == "WARM"])
cold_count = len(df[df["tier_label"] == "COLD"])
avg_score = round(df["score"].mean(), 1)
qa_pass = len(df[df["qa_valid"] == True])

col1.metric("Total Leads", total)
col2.metric("🔥 HOT Leads", hot_count, "{:.0f}%".format(hot_count / total * 100))
col3.metric("🔶 WARM Leads", warm_count, "{:.0f}%".format(warm_count / total * 100))
col4.metric("❄️ COLD Leads", cold_count, "{:.0f}%".format(cold_count / total * 100))

st.markdown("---")

# ── Row 2: Charts ─────────────────────────────────────────────────────────────
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Lead Distribution by Tier")
    tier_counts = df["tier_label"].value_counts()
    st.bar_chart(tier_counts)

with col_right:
    st.subheader("Score Distribution")
    score_bins = pd.cut(
        df["score"],
        bins=[0, 40, 60, 80, 100],
        labels=["0-40", "41-60", "61-80", "81-100"]
    ).value_counts().sort_index()
    st.bar_chart(score_bins)

st.markdown("---")

# ── Row 3: Breakdowns ─────────────────────────────────────────────────────────
col_a, col_b, col_c = st.columns(3)

with col_a:
    st.subheader("By Class")
    class_counts = df["current_class"].value_counts()
    st.bar_chart(class_counts)

with col_b:
    st.subheader("By Exam")
    exam_counts = df["target_exam"].value_counts()
    st.bar_chart(exam_counts)

with col_c:
    st.subheader("By Engagement")
    eng_counts = df["engagement_level"].value_counts()
    st.bar_chart(eng_counts)

st.markdown("---")

# ── Row 4: Average score by tier ──────────────────────────────────────────────
st.subheader("Average Score by Tier")
avg_by_tier = df.groupby("tier_label")["score"].mean().round(1)
st.bar_chart(avg_by_tier)

st.markdown("---")

# ── Row 5: Scoring agreement ──────────────────────────────────────────────────
st.subheader("Rule-Based Scorer vs Ground Truth")
st.caption("How often does the rule-based scorer agree with the designed tier label?")

agreement = df[df["predicted_tier"] == df["tier_label"]]
disagreement = df[df["predicted_tier"] != df["tier_label"]]

col_x, col_y = st.columns(2)
col_x.metric("✅ Agreement", len(agreement), "{:.1f}%".format(len(agreement) / total * 100))
col_y.metric("⚠️ Disagreement", len(disagreement), "{:.1f}%".format(len(disagreement) / total * 100))

if len(disagreement) > 0:
    st.caption("Leads where predicted tier ≠ ground truth label (these are training signal for ML)")
    disagreement_display = disagreement[[
        "conversation_id", "tier_label", "predicted_tier", "score",
        "current_class", "engagement_level", "decision_maker"
    ]].reset_index(drop=True)
    st.dataframe(disagreement_display, use_container_width=True)

st.markdown("---")

# ── Row 6: Full lead table ────────────────────────────────────────────────────
st.subheader("Full Lead Table")
st.caption("Click column headers to sort")

display_cols = [
    "conversation_id", "full_name", "current_class", "target_exam",
    "exam_year", "urgency_level", "budget_concern", "decision_maker",
    "engagement_level", "score", "predicted_tier", "tier_label"
]

existing_cols = [c for c in display_cols if c in df.columns]
st.dataframe(df[existing_cols], use_container_width=True, height=400)
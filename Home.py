"""
Home.py — PW Voice AI
Entry point. Streamlit opens this first by default.
Immediately redirects to Command Center.
"""

import streamlit as st
import sys, os

ROOT = r"C:\Users\kddipank\Documents\Documents\Personal\PMCurve\PW_AI_Capstone"
sys.path.insert(0, ROOT)

st.set_page_config(
    page_title="PW Voice AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Redirect immediately to Command Center
st.switch_page("pages/1_Command_Center.py")

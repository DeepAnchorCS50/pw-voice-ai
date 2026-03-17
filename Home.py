"""
Home.py — PW Voice AI
Entry point. Redirects immediately to Command Center.
"""

import streamlit as st

st.set_page_config(
    page_title="PW Voice AI",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.switch_page("pages/1_Command_Center.py")

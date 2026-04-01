"""
ui_utils.py — Shared UI utilities for PW Voice AI dashboard
Navigation uses st.page_link() — requires Streamlit >= 1.31
"""

import streamlit as st

# ── Design tokens ──────────────────────────────────────────────────────────────
COLORS = {
    "bg_primary":    "#0f1117",
    "bg_card":       "#1a1d29",
    "bg_card_hover": "#232738",
    "border":        "#2d3148",
    "text_primary":  "#e6e8f0",
    "text_secondary":"#8b8fa3",
    "accent_hot":    "#ef4444",
    "accent_warm":   "#f59e0b",
    "accent_cold":   "#3b82f6",
    "accent_success":"#22c55e",
    "accent_brand":  "#6366f1",
}

HIDE_STREAMLIT_CSS = """
<style>
    #MainMenu                        { visibility: hidden; }
    footer                           { visibility: hidden; }
    .stDeployButton                  { display: none; }

    /* ── Hide ALL known Streamlit header / nav variants ── */
    header                                        { display: none !important; }
    [data-testid="stHeader"]                      { display: none !important; }
    [data-testid="stTopNavigation"]               { display: none !important; }
    [data-testid="stSidebarNav"]                  { display: none !important; }
    [data-testid="stSidebar"]                     { display: none !important; }
    [data-testid="collapsedControl"]              { display: none !important; }
    [data-testid="stNavSectionHeader"]            { display: none !important; }
    nav[data-testid="stBottomNavigation"]         { display: none !important; }

    /* ── Emotion-cache classes Streamlit Cloud uses for top nav ── */
    .st-emotion-cache-1itdyc2                     { display: none !important; }
    .st-emotion-cache-czk5ss                      { display: none !important; }
    .st-emotion-cache-1dp5vir                     { display: none !important; }

    /* ── Block container: full-width, no padding ── */
    .block-container {
        padding-top: 0 !important;
        padding-bottom: 0 !important;
        padding-left: 0 !important;
        padding-right: 0 !important;
        max-width: 100% !important;
    }
    .stApp { background-color: #0f1117; }
    iframe { border: none !important; }
</style>
"""


def render_nav(active_page: str):
    """
    Render top navigation bar with real Streamlit page links.
    active_page: 'Command Center' | 'Live Demo' | 'Lead List' | 'Evals'
    """

    # 1. Inject base CSS: hide chrome + font import
    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    {HIDE_STREAMLIT_CSS.replace('<style>', '').replace('</style>', '')}

    /* ── Nav row: the st.columns() block ── */
    [data-testid="stHorizontalBlock"] {{
        background: #0f1117 !important;
        border-bottom: 1px solid #2d3148 !important;
        padding: 6px 20px 6px 20px !important;
        margin: 0 !important;
        position: sticky !important;
        top: 0 !important;
        z-index: 999 !important;
        align-items: center !important;
    }}

    /* ── Column padding ── */
    [data-testid="stHorizontalBlock"] > [data-testid="column"] {{
        padding: 0 2px !important;
        min-width: 0 !important;
    }}

    /* ── page_link base styles ── */
    [data-testid="stPageLink"] {{
        background: transparent !important;
        border: none !important;
        padding: 0 !important;
        margin: 0 !important;
    }}
    [data-testid="stPageLink"] a,
    [data-testid="stPageLink"] a:visited {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        height: 38px !important;
        padding: 0 12px !important;
        font-size: 12px !important;
        font-weight: 500 !important;
        color: #c8cad6 !important;
        text-decoration: none !important;
        border-radius: 6px !important;
        border-bottom: 2px solid transparent !important;
        transition: all 150ms ease !important;
        font-family: 'Inter', sans-serif !important;
        white-space: nowrap !important;
        letter-spacing: -0.1px !important;
    }}
    [data-testid="stPageLink"] a:hover {{
        color: #e6e8f0 !important;
        background: #1a1d29 !important;
    }}
    /* Active state — Streamlit sets aria-current="page" on current page link */
    [data-testid="stPageLink"] a[aria-current="page"] {{
        color: #e6e8f0 !important;
        border-bottom-color: #6366f1 !important;
        background: #1a1d2944 !important;
    }}

    /* ── Brand column (first col) ── */
    .pw-brand {{
        display: flex;
        align-items: center;
        gap: 9px;
        height: 38px;
        padding: 0 8px;
    }}
    .pw-logo {{
        width: 26px; height: 26px;
        background: #6366f1; border-radius: 7px;
        display: flex; align-items: center; justify-content: center;
        font-size: 12px; font-weight: 700; color: white;
        flex-shrink: 0;
    }}
    .pw-brand-name {{
        font-size: 13px; font-weight: 600; color: #e6e8f0;
        font-family: 'Inter', sans-serif; letter-spacing: -0.2px;
    }}

    /* ── LIVE badge + clock fixed to top-right ── */
    .pw-right-fixed {{
        position: fixed;
        top: 12px;
        right: 20px;
        display: flex;
        align-items: center;
        gap: 12px;
        z-index: 1000;
        pointer-events: none;
    }}
    .pw-live {{
        display: flex; align-items: center; gap: 5px;
        background: #22c55e18; border: 1px solid #22c55e33;
        padding: 3px 10px; border-radius: 20px;
        font-size: 11px; font-weight: 600; color: #22c55e;
        letter-spacing: 0.5px; font-family: 'Inter', sans-serif;
    }}
    .pw-live-dot {{
        width: 5px; height: 5px; background: #22c55e; border-radius: 50%;
        animation: livepulse 1.5s infinite;
    }}
    @keyframes livepulse {{ 0%,100%{{opacity:1}} 50%{{opacity:0.4}} }}
    .pw-clock {{
        font-size: 12px; color: #8b8fa3;
        font-family: 'Inter', sans-serif;
        font-variant-numeric: tabular-nums;
    }}
    </style>
    """, unsafe_allow_html=True)

    # 2. Build nav using st.columns — this is real Streamlit layout
    #    Col 0: Brand (wide) | Cols 1-4: page links | Col 5: spacer
    cols = st.columns([1.8, 1.1, 1, 0.9, 3])

    with cols[0]:
        st.markdown("""
        <div class="pw-brand">
            <div class="pw-logo">PW</div>
            <div class="pw-brand-name">Voice AI</div>
        </div>
        """, unsafe_allow_html=True)

    with cols[1]:
        st.page_link("pages/1_Operations.py", label="⚡ Operations")
    with cols[2]:
        st.page_link("pages/2_Lead_List.py",  label="📋 Lead List")
    with cols[3]:
        st.page_link("pages/4_Evals.py",      label="📊 Evals")

    # 3. LIVE badge + clock — fixed position, outside column flow
    st.markdown("""
    <div class="pw-right-fixed">
        <div class="pw-live"><div class="pw-live-dot"></div>LIVE</div>
        <div class="pw-clock" id="pw-clock">--:--:--</div>
    </div>
    <script>
    (function() {
        function tick() {
            const el = document.getElementById('pw-clock');
            if (!el) return;
            const n = new Date();
            el.textContent =
                String(n.getHours()).padStart(2,'0') + ':' +
                String(n.getMinutes()).padStart(2,'0') + ':' +
                String(n.getSeconds()).padStart(2,'0');
        }
        setInterval(tick, 1000); tick();
    })();
    </script>
    """, unsafe_allow_html=True)

"""
V2 navigation entrypoint (Phase 1). This file's role changed completely
with the V2 migration: it no longer contains any page content itself —
that all moved to dashboard/pages/today.py. This file is now purely:
  1. The single global st.set_page_config() call (Streamlit allows exactly
     one per app run — every individual page file's own call was removed
     as part of this migration).
  2. The single global inject_theme() call for the custom header below.
  3. The st.navigation() page registry, which — as of this migration —
     is the ONLY way any page in this app is reachable. The old
     dashboard/pages/ folder auto-discovery convention no longer applies
     once st.navigation() is called anywhere in the app.
  4. A hand-built top header (page_link row + Settings popover), rendered
     here so it appears above whichever page runs next via pg.run().

Why hand-built instead of st.navigation(..., position="top"): Streamlit's
own top-position widget can't list a page as routable while hiding it from
the visible menu (confirmed against Streamlit's docs), and the Watchlist
product decision requires exactly that (routable, not visible in the main
nav). Separately, position="top" wasn't added until Streamlit 1.46.0 —
this project pins streamlit==1.38.0, so the built-in widget isn't even
available here regardless. position="hidden" (used below) has existed
since st.navigation's 1.36.0 launch, so it's safe on this pinned version.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st

from dashboard.theme import inject_theme

st.set_page_config(
    page_title="The Research Desk",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="collapsed",
)
inject_theme()

today_page = st.Page("pages/today.py", title="Today", icon="📰", default=True)
companies_page = st.Page("pages/3_Company.py", title="Companies", icon="🏢")
industries_page = st.Page("pages/2_Sectors.py", title="Industries", icon="🏭")
macro_page = st.Page("pages/4_Macro.py", title="Macro", icon="🌍")
research_page = st.Page("pages/research.py", title="Research", icon="🔎")
watchlist_page = st.Page("pages/5_Watchlist.py", title="Watchlist", icon="⭐")

# Watchlist is included here (making it genuinely routable) but is
# deliberately never given a visible st.page_link below — reachable only
# via the Settings popover, per the "remove from top nav, don't delete,
# keep accessible internally" product decision.
pg = st.navigation(
    [today_page, companies_page, industries_page, macro_page, research_page, watchlist_page],
    position="hidden",
)

# --- Custom top header (single row: wordmark, 5 nav links, settings icon) ---
header_cols = st.columns([2.2, 1, 1, 1, 1, 1, 0.5])

with header_cols[0]:
    st.markdown('<div class="app-wordmark">● THE RESEARCH DESK</div>', unsafe_allow_html=True)
with header_cols[1]:
    st.page_link(today_page, label="Today")
with header_cols[2]:
    st.page_link(companies_page, label="Companies")
with header_cols[3]:
    st.page_link(industries_page, label="Industries")
with header_cols[4]:
    st.page_link(macro_page, label="Macro")
with header_cols[5]:
    st.page_link(research_page, label="Research")
with header_cols[6]:
    with st.popover("⚙"):
        st.page_link(watchlist_page, label="⭐ Open Watchlist")

st.markdown('<hr class="app-header-rule">', unsafe_allow_html=True)

pg.run()
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dashboard.db_helpers import get_recent_news, get_latest_report
from dashboard.theme import inject_theme

st.set_page_config(
    page_title="Finance Research Platform",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
inject_theme()

st.title("The Research Desk")
st.caption("Research assistant, not a signal generator — this dashboard explains, it doesn't tell you what to buy or sell.")

st.divider()

col1, col2 = st.columns([2, 1])

STAMP_CLASS = {
    "Bullish": "stamp-bullish", "Bearish": "stamp-bearish",
    "Neutral": "stamp-neutral", "Urgent": "stamp-urgent",
}

with col1:
    st.subheader("Latest Dispatches")
    rows = get_recent_news(limit=20)

    if not rows:
        st.info(
            "No news processed yet. Run `python pipelines/orchestrator.py` "
            "once to populate the database, then refresh this page."
        )
    else:
        for news, summary in rows:
            stamp_class = STAMP_CLASS.get(summary.classification, "stamp-neutral")
            st.markdown(
                f"""<div class="dispatch-card">
                <span class="dispatch-stamp {stamp_class}">{summary.classification}</span>
                <span class="dispatch-stamp {stamp_class}">{summary.scope}</span>
                <div class="dispatch-title">{news.title}</div>
                <div class="dispatch-meta">{news.source} · {news.published_at}</div>
                </div>""",
                unsafe_allow_html=True,
            )
            with st.expander("AI analysis"):
                st.write("**Summary:**", summary.ai_summary)
                st.write("**Why it matters:**", summary.why_it_matters)
                st.write("**Short-term impact:**", summary.short_term_impact)
                st.write("**Long-term impact:**", summary.long_term_impact)
                st.write("**Risks:**", summary.risks)
                st.write("**Opportunities:**", summary.opportunities)
                st.markdown(f"[Read original article]({news.url})")

with col2:
    st.subheader("Today's Digest")
    report = get_latest_report("daily")
    if report:
        st.caption(f"Generated {report.generated_at}")
        st.markdown(report.content)
    else:
        st.info("No daily digest yet — it's generated at the end of each pipeline run.")

st.divider()
st.caption(
    "Use the pages in the sidebar for Market Overview, Sectors, Company pages, "
    "Macro dashboard, Watchlist, and the AI Research Chat."
)
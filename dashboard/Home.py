"""
Main entrypoint for the Streamlit dashboard.
Run with:  streamlit run dashboard/Home.py
"""
import sys
from pathlib import Path

# Make the project root importable when Streamlit runs this file directly.
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dashboard.db_helpers import get_recent_news, get_latest_report

st.set_page_config(
    page_title="Finance Research Platform",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; }
    .news-card { background-color: #161b22; border-radius: 8px; padding: 14px 18px;
                 margin-bottom: 10px; border: 1px solid #21262d; }
    .tag-bullish { color: #3fb950; font-weight: 600; }
    .tag-bearish { color: #f85149; font-weight: 600; }
    .tag-neutral { color: #8b949e; font-weight: 600; }
    .tag-urgent  { color: #d29922; font-weight: 600; }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("📊 AI Finance Research Platform")
st.caption("Research assistant, not a signal generator — this dashboard explains, it doesn't tell you what to buy or sell.")

st.divider()

col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("🗞️ Latest Research-Grade News")
    rows = get_recent_news(limit=20)

    if not rows:
        st.info(
            "No news processed yet. Run `python pipelines/orchestrator.py` "
            "once to populate the database, then refresh this page."
        )
    else:
        tag_class = {
            "Bullish": "tag-bullish", "Bearish": "tag-bearish",
            "Neutral": "tag-neutral", "Urgent": "tag-urgent",
        }
        for news, summary in rows:
            css_class = tag_class.get(summary.classification, "tag-neutral")
            with st.container():
                st.markdown(
                    f"""<div class="news-card">
                    <span class="{css_class}">[{summary.classification} · {summary.scope}]</span>
                    <b>{news.title}</b><br>
                    <span style="color:#8b949e;font-size:0.85em;">{news.source} · {news.published_at}</span>
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
    st.subheader("📰 Latest Daily Digest")
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

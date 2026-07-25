import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from dashboard.db_helpers import get_news_for_industry
from dashboard.theme import inject_theme
from config.settings import settings

st.set_page_config(page_title="Sectors", layout="wide", page_icon="🏭")
inject_theme()
st.title("Industry Intelligence")

STAMP_CLASS = {
    "Bullish": "stamp-bullish", "Bearish": "stamp-bearish",
    "Neutral": "stamp-neutral", "Urgent": "stamp-urgent",
}

industry = st.selectbox("Choose a sector", settings.TRACKED_INDUSTRIES)
st.subheader(f"{industry} — Recent News & AI Analysis")

rows = get_news_for_industry(industry)

if not rows:
    st.info(
        f"No tagged news for '{industry}' yet. This fills in automatically as the "
        "daily pipeline tags more headlines."
    )
else:
    sentiments = [s.sentiment_score for _, s in rows if s.sentiment_score is not None]
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        st.metric("Average sentiment (recent news)", f"{avg_sentiment:+.2f}")

    for news, summary in rows:
        stamp_class = STAMP_CLASS.get(summary.classification, "stamp-neutral")
        st.markdown(
            f"""<div class="dispatch-card">
            <span class="dispatch-stamp {stamp_class}">{summary.classification}</span>
            <div class="dispatch-title">{news.title}</div>
            </div>""",
            unsafe_allow_html=True,
        )
        with st.expander("AI analysis"):
            st.write("**Summary:**", summary.ai_summary)
            st.write("**Why it matters:**", summary.why_it_matters)
            st.write("**Risks:**", summary.risks)
            st.write("**Opportunities:**", summary.opportunities)
            st.markdown(f"[Original article]({news.url})")

st.divider()
st.caption(
    "Growth drivers, risks, and historical trend fields exist in the `industries` "
    "table — populate them once per sector as you research."
)
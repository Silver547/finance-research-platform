import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
from dashboard.db_helpers import get_news_for_industry
from config.settings import settings

st.set_page_config(page_title="Sectors", layout="wide")
st.title("🏭 Industry Intelligence")

industry = st.selectbox("Choose a sector", settings.TRACKED_INDUSTRIES)

st.subheader(f"{industry} — Recent News & AI Analysis")
rows = get_news_for_industry(industry)

if not rows:
    st.info(
        f"No tagged news for '{industry}' yet. This fills in automatically as the "
        "daily pipeline tags more headlines — the tagging agent only assigns an "
        "industry when the headline is genuinely about it."
    )
else:
    sentiments = [s.sentiment_score for _, s in rows if s.sentiment_score is not None]
    if sentiments:
        avg_sentiment = sum(sentiments) / len(sentiments)
        st.metric("Average sentiment (recent news)", f"{avg_sentiment:+.2f}", help="-1 = very bearish, +1 = very bullish")

    for news, summary in rows:
        with st.expander(f"[{summary.classification}] {news.title}"):
            st.write("**Summary:**", summary.ai_summary)
            st.write("**Why it matters:**", summary.why_it_matters)
            st.write("**Risks:**", summary.risks)
            st.write("**Opportunities:**", summary.opportunities)
            st.markdown(f"[Original article]({news.url})")

st.divider()
st.caption(
    "Growth drivers, risks, and historical trend fields exist in the `industries` "
    "table (see database/schema.sql) — populate them once per sector as you research; "
    "they're static reference data rather than something to re-generate daily."
)

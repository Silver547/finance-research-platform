import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
from dashboard.db_helpers import get_news_for_company
from dashboard.theme import inject_theme, PLOTLY_LAYOUT
from pipelines.stocks.fetch_prices import fetch_price_history
from config.settings import settings

inject_theme()
st.title("Company Intelligence")

STAMP_CLASS = {
    "Bullish": "stamp-bullish", "Bearish": "stamp-bearish",
    "Neutral": "stamp-neutral", "Urgent": "stamp-urgent",
}

ticker = st.selectbox("Choose a company", settings.TRACKED_TICKERS)
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Price")
    df = fetch_price_history(ticker, period="1y")
    if not df.empty:
        fig = go.Figure(go.Scatter(x=df.index, y=df["Close"], name="Close"))
        fig.update_layout(**PLOTLY_LAYOUT, height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"52w range: {df['52w_low'].iloc[-1]:.2f} – {df['52w_high'].iloc[-1]:.2f}")
    else:
        st.info("No price data available for this ticker.")

with col2:
    st.subheader("Recent News & AI Analysis")
    rows = get_news_for_company(ticker)
    if not rows:
        st.info("No tagged news for this ticker yet.")
    else:
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
                st.markdown(f"[Original article]({news.url})")

st.divider()
st.info(
    "Financials, ratios, ownership, SWOT/moat analysis all have dedicated tables — "
    "wire up a filings ingestion script to populate these."
)
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
from dashboard.db_helpers import get_news_for_company
from pipelines.stocks.fetch_prices import fetch_price_history
from config.settings import settings

st.set_page_config(page_title="Company", layout="wide")
st.title("🏢 Company Intelligence")

ticker = st.selectbox("Choose a company", settings.TRACKED_TICKERS)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Price")
    df = fetch_price_history(ticker, period="1y")
    if not df.empty:
        fig = go.Figure(go.Scatter(x=df.index, y=df["Close"], name="Close"))
        fig.update_layout(template="plotly_dark", height=350)
        st.plotly_chart(fig, use_container_width=True)
        st.write(f"52w range: {df['52w_low'].iloc[-1]:.2f} – {df['52w_high'].iloc[-1]:.2f}")
    else:
        st.info("No price data available for this ticker.")

with col2:
    st.subheader("Recent News & AI Analysis")
    rows = get_news_for_company(ticker)
    if not rows:
        st.info(
            "No tagged news for this ticker yet. Make sure the ticker is included "
            "in TRACKED_TICKERS (config/settings.py) so the tagging agent can match it."
        )
    else:
        for news, summary in rows:
            with st.expander(f"[{summary.classification}] {news.title}"):
                st.write("**Summary:**", summary.ai_summary)
                st.write("**Why it matters:**", summary.why_it_matters)
                st.write("**Short-term impact:**", summary.short_term_impact)
                st.write("**Long-term impact:**", summary.long_term_impact)
                st.markdown(f"[Original article]({news.url})")

st.divider()
st.info(
    "Financials, ratios, ownership, SWOT/moat analysis, and filings all have "
    "dedicated tables (`financial_statements`, `ratios`, `ownership`, ...) — "
    "wire up a filings ingestion script (SEC EDGAR / NSE / BSE) to populate these, "
    "following the same pattern as `pipelines/news/fetch_rss.py`."
)

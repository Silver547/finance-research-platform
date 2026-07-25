import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import plotly.graph_objects as go
from pipelines.stocks.fetch_prices import fetch_price_history
from config.settings import settings
from dashboard.theme import inject_theme, PLOTLY_LAYOUT

st.set_page_config(page_title="Market Overview", layout="wide", page_icon="📈")
inject_theme()
st.title("Market Overview")

benchmark_tickers = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "NIFTY 50": "^NSEI", "SENSEX": "^BSESN"}

cols = st.columns(len(benchmark_tickers))
for col, (label, ticker) in zip(cols, benchmark_tickers.items()):
    with col:
        with st.spinner(f"Loading {label}..."):
            df = fetch_price_history(ticker, period="5d", interval="1d")
        if not df.empty:
            last = df["Close"].iloc[-1]
            prev = df["Close"].iloc[-2] if len(df) > 1 else last
            change_pct = (last - prev) / prev * 100 if prev else 0
            col.metric(label, f"{last:,.2f}", f"{change_pct:+.2f}%")
        else:
            col.metric(label, "N/A")

st.divider()
st.subheader("Tracked Stocks — Price & Indicators")

ticker = st.selectbox("Choose a tracked ticker", settings.TRACKED_TICKERS)
period = st.select_slider("Period", options=["1mo", "3mo", "6mo", "1y", "2y"], value="6mo")

with st.spinner(f"Loading {ticker}..."):
    df = fetch_price_history(ticker, period=period)

if df.empty:
    st.warning("No data returned for this ticker.")
else:
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df.index, open=df["Open"], high=df["High"], low=df["Low"], close=df["Close"], name="Price"
    ))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50", line=dict(width=1)))
    fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="MA200", line=dict(width=1)))
    fig.update_layout(**PLOTLY_LAYOUT, height=500, xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("52w High", f"{df['52w_high'].iloc[-1]:.2f}")
    c2.metric("52w Low", f"{df['52w_low'].iloc[-1]:.2f}")
    c3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.1f}")
    c4.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")

    with st.expander("Raw price data"):
        st.dataframe(df.tail(30), use_container_width=True)
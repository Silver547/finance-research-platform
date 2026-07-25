import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st
import pandas as pd
import plotly.express as px
from dashboard.db_helpers import get_macro_indicators
from dashboard.theme import inject_theme, PLOTLY_LAYOUT

st.set_page_config(page_title="Macro Dashboard", layout="wide", page_icon="🌍")
inject_theme()
st.title("Macro Dashboard")

rows = get_macro_indicators()

if not rows:
    st.info("No macro data yet. Run `python pipelines/macro/fetch_macro.py`.")
else:
    df = pd.DataFrame([{
        "indicator": r.indicator_name, "country": r.country,
        "period": r.period, "value": r.value,
    } for r in rows])

    indicator = st.selectbox("Indicator", sorted(df["indicator"].unique()))
    subset = df[df["indicator"] == indicator]

    fig = px.line(subset, x="period", y="value", color="country", markers=True, title=indicator)
    fig.update_layout(**PLOTLY_LAYOUT)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Raw data"):
        st.dataframe(subset.sort_values("period", ascending=False), use_container_width=True)

st.divider()
st.caption("Extend `pipelines/macro/fetch_macro.py` with more indicators as needed.")
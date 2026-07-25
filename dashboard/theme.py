"""
Shared visual theme for the dashboard — a research-desk aesthetic:
deep ink background, editorial serif headlines, and news classifications
styled like ink-stamped wire dispatches rather than generic colored pills.
"""
import streamlit as st

THEME_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,600;9..144,700&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    --ink: #12151C;
    --surface: #1B1F2A;
    --border: #2A2F3D;
    --text: #ECE7DD;
    --muted: #8A8F9C;
    --accent: #C9A24B;
    --bullish: #4FAE7C;
    --bearish: #C1554A;
    --neutral: #8A8F9C;
}

[data-testid="stAppViewContainer"], .stApp {
    background-color: var(--ink);
}

[data-testid="stSidebar"] {
    background-color: #0D0F15;
    border-right: 1px solid var(--border);
}

[data-testid="stSidebar"] * {
    font-family: 'IBM Plex Sans', sans-serif !important;
}

h1, h2, h3 {
    font-family: 'Fraunces', serif !important;
    font-weight: 600 !important;
    color: var(--text) !important;
    letter-spacing: -0.01em;
}

p, div, span, label {
    font-family: 'IBM Plex Sans', sans-serif;
}

.dispatch-card {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 20px;
    margin-bottom: 12px;
}

.dispatch-stamp {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 2px 8px;
    border: 1px solid currentColor;
    border-radius: 2px;
    margin-right: 8px;
    transform: rotate(-1deg);
}

.stamp-bullish { color: var(--bullish); }
.stamp-bearish { color: var(--bearish); }
.stamp-neutral { color: var(--muted); }
.stamp-urgent { color: var(--accent); }

.dispatch-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    margin-top: 6px;
}

.dispatch-title {
    font-family: 'IBM Plex Sans', sans-serif;
    font-weight: 600;
    font-size: 1.02rem;
    color: var(--text);
}

hr { border-color: var(--border) !important; }
</style>
"""


def inject_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)
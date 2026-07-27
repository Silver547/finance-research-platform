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
    --surface-raised: #232838;
    --border: #2A2F3D;
    --border-strong: #3A4152;
    --text: #ECE7DD;
    --text-secondary: #B8BCC7;
    --muted: #8A8F9C;
    --accent: #C9A24B;
    --urgent: #D9812E;
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
}

.stamp-bullish { color: var(--bullish); }
.stamp-bearish { color: var(--bearish); }
.stamp-neutral { color: var(--muted); }
.stamp-urgent { color: var(--urgent); }

/* Origin badge (Phase 4) — informational, not sentiment, so it stays
   neutral-toned rather than borrowing bullish/bearish/urgent meaning.
   Reuses .dispatch-stamp shape; only color/border-style differ. */
.stamp-domestic { color: var(--muted); }
.stamp-global { color: var(--muted); border-style: dashed; }

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

/* Chip component (Phase 4/5) — Risk / Opportunity / Sector tags.
   Deliberately pill-shaped (vs. rectangular .dispatch-stamp) so extracted/
   inferred AI content reads as distinct from classification badges.
   Shared by article cards and the Digest hero section. */
.chip {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    padding: 3px 10px;
    border-radius: 12px;
    margin: 4px 6px 0 0;
}
.chip-risk {
    background-color: rgba(193, 85, 74, 0.12);
    color: var(--bearish);
    border: 1px solid rgba(193, 85, 74, 0.35);
}
.chip-opportunity {
    background-color: rgba(79, 174, 124, 0.12);
    color: var(--bullish);
    border: 1px solid rgba(79, 174, 124, 0.35);
}
.chip-sector {
    background-color: var(--surface-raised);
    color: var(--text-secondary);
    border: 1px solid var(--border-strong);
}

/* Digest hero section (Phase 5) — the one genuinely new component in the
   system. No prior element represented an aggregated, page-level summary.
   Internals (chips, section labels, focus items) all reuse existing
   typography and semantic color tokens. */
.digest-card {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 24px 28px;
    margin-bottom: 24px;
}
.digest-card--empty {
    border-style: dashed;
    border-color: var(--border-strong);
    text-align: center;
    color: var(--muted);
    padding: 40px 28px;
}
.digest-section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 16px;
    margin-bottom: 6px;
}
.digest-focus-item {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.92rem;
    margin-bottom: 2px;
}
.digest-focus-positive { color: var(--bullish); }
.digest-focus-negative { color: var(--bearish); }

/* Digest hero container fix (Phase 7): a hand-opened <div class="digest-card">
   spanning multiple st.markdown/st.caption calls never actually wraps them —
   Streamlit renders each call as its own top-level element, so the div
   appeared as an empty box with the real content escaping below it,
   unstyled (confirmed visually — see Phase 7 QA screenshot).
   Fixed by using st.container(border=True), which Streamlit does render as
   one real wrapper around everything inside the `with` block. We style
   that native container via its test id, using a hidden marker span +
   :has() so only the digest container is affected, not any other bordered
   container added later. */
[data-testid="stVerticalBlockBorderWrapper"]:has(.digest-marker) {
    background-color: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.digest-marker-empty) {
    border-style: dashed !important;
    border-color: var(--border-strong) !important;
    text-align: center;
}
[data-testid="stVerticalBlockBorderWrapper"]:has(.digest-marker-empty) p {
    color: var(--muted) !important;
}
.digest-marker, .digest-marker-empty {
    display: none;
}

hr { border-color: var(--border) !important; }
[data-testid="stMetric"] {
    background-color: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px 16px;
}
[data-testid="stMetricLabel"] {
    color: var(--muted) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.75rem !important;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}
[data-testid="stMetricValue"] {
    color: var(--text) !important;
    font-family: 'Fraunces', serif !important;
}

.stButton button {
    background-color: var(--surface) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 4px !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
}
.stButton button:hover {
    border-color: var(--accent) !important;
    color: var(--accent) !important;
}

[data-testid="stExpander"] {
    background-color: var(--surface);
    border: 1px solid var(--border) !important;
    border-radius: 4px;
}
.streamlit-expanderHeader {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.85rem !important;
}
</style>
"""


def inject_theme():
    st.markdown(THEME_CSS, unsafe_allow_html=True)

PLOTLY_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#12151C",
    plot_bgcolor="#12151C",
    font=dict(family="IBM Plex Sans", color="#ECE7DD"),
    colorway=["#C9A24B", "#4FAE7C", "#C1554A", "#8A8F9C"],
)
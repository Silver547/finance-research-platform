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
/* Regression fix (V2 Phase 1): Latest Dispatches and Universal Search now
   put .dispatch-title on a real <a> tag (see dashboard/pages/today.py and
   research.py) instead of a static <span>, restoring click-through to the
   source article. Scoped to a.dispatch-title specifically so the existing
   <div class="dispatch-title"> usage on 2_Sectors.py/3_Company.py/
   5_Watchlist.py (paired with their own st.expander + link, unaffected by
   this regression) renders exactly as before — no visual change there. */
a.dispatch-title {
    text-decoration: none;
    cursor: pointer;
}
a.dispatch-title:hover {
    color: var(--accent);
    text-decoration: underline;
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
    padding: 28px 32px !important;
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

/* Hero section editorial treatment (Today's Briefing redesign) — a
   "morning briefing" masthead: eyebrow label, a byline combining
   timestamp + mood (instead of a floating disconnected stamp), and the
   AI narrative set in serif at a slightly larger size than body text.
   Distinct from .digest-section-label/.digest-focus-item, which remain
   in use for the Companies/Sectors-in-Focus section further down the page. */
.hero-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 8px;
}
.hero-byline {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--muted);
    margin-bottom: 20px;
}
.hero-byline .mood-constructive { color: var(--bullish); }
.hero-byline .mood-cautious { color: var(--bearish); }
.hero-byline .mood-mixed, .hero-byline .mood-quiet { color: var(--muted); }
.hero-headline {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.55rem;
    line-height: 1.3;
    color: var(--text);
    margin-bottom: 4px;
}
.hero-narrative {
    font-family: 'Fraunces', serif;
    font-size: 1.15rem;
    line-height: 1.6;
    color: var(--text);
    margin-bottom: 8px;
}

/* "At a glance" / "Worth watching" expanders reuse Streamlit's native
   stExpander styling (already themed below) for their outer shell, so
   only the inner row styling needs to be defined here. */
.hero-glance-item {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.94rem;
    color: var(--text);
    padding: 8px 0;
    border-top: 1px solid var(--border);
}
.hero-glance-item:first-of-type { border-top: none; }

.hero-watch-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    margin-top: 14px;
    margin-bottom: 8px;
}
.hero-watch-label:first-of-type { margin-top: 0; }
.hero-watch-item {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    line-height: 1.5;
    color: var(--text-secondary);
    padding: 4px 0 8px 14px;
    margin-bottom: 4px;
}
.hero-watch-item.risk { border-left: 2px solid var(--bearish); }
.hero-watch-item.opportunity { border-left: 2px solid var(--bullish); }

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

/* ============================================================
   V2 Navigation Header (Phase 1). Custom-built rather than relying
   on st.navigation's own top-position widget: (a) that widget can't
   list a page as routable while hiding it from the visible menu,
   which the Watchlist product decision requires, and (b) the pinned
   streamlit==1.38.0 predates position="top" (added in 1.46.0) anyway,
   so a built-in top bar isn't even available on this version. This
   header is rendered once, in dashboard/Home.py (the st.navigation
   router), before pg.run(), so it appears above every page. */
.app-wordmark {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.1rem;
    color: var(--text);
    padding-top: 6px;
}
.app-header-rule {
    border: none;
    border-top: 1px solid var(--border);
    margin: 4px 0 28px 0;
}
/* Best-effort selector for st.page_link's rendered anchor — Streamlit's
   internal test ids can shift between versions; if these links render
   unstyled after deploy, inspect the live DOM and adjust the selector,
   the page_link calls themselves are unaffected either way. */
[data-testid="stPageLink"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
}
[data-testid="stPageLink"] p {
    color: var(--text-secondary) !important;
    font-weight: 500 !important;
    font-size: 0.92rem !important;
}
[data-testid="stPageLink"]:hover p {
    color: var(--accent) !important;
}

/* ============================================================
   Hero V2 (Phase 1) — large mood icon + headline, minimal text by
   default. Distinct from the earlier .hero-eyebrow/.hero-byline/
   .hero-headline/.hero-narrative set (still used nowhere now that
   Today's content moved to pages/today.py with this new treatment,
   but left in place above rather than deleted — no other page
   references them, and removing unused CSS carries no behavior
   risk either way, so it's left for now rather than treated as an
   in-scope cleanup task this phase).
   ============================================================ */
.hero-mood-icon {
    font-size: 3.4rem;
    line-height: 1;
    margin-bottom: 10px;
}
.hero-v2-headline {
    font-family: 'Fraunces', serif;
    font-weight: 700;
    font-size: 1.75rem;
    line-height: 1.25;
    color: var(--text);
    margin-bottom: 4px;
}

/* Market Snapshot card */
.snapshot-title {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 14px;
}
.snapshot-row {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 12px;
    padding: 9px 0;
    border-top: 1px solid var(--border);
}
.snapshot-row:first-of-type { border-top: none; }
.snapshot-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.76rem;
    color: var(--muted);
    white-space: nowrap;
    padding-top: 1px;
}
.snapshot-value {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 600;
    color: var(--text);
    text-align: right;
}

/* ============================================================
   Global Drivers (Phase 1)
   ============================================================ */
.driver-name {
    font-family: 'Fraunces', serif;
    font-weight: 600;
    font-size: 1.05rem;
    color: var(--text);
    margin-bottom: 8px;
}
.driver-meta {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.7rem;
    color: var(--muted);
    margin-bottom: 2px;
}
.driver-summary {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.86rem;
    color: var(--text-secondary);
    line-height: 1.5;
    margin-bottom: 10px;
}
.driver-headline {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.8rem;
    color: var(--muted);
    padding: 2px 0;
}

/* ============================================================
   Group B preview sections (Phase 1) — every retained V1 section is
   visibly marked as a compact preview, not a final destination.
   ============================================================ */
.preview-label {
    display: inline-block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.64rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--muted);
    border: 1px dashed var(--border-strong);
    border-radius: 10px;
    padding: 1px 8px;
    margin-left: 8px;
    vertical-align: middle;
}
.mover-item {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    color: var(--text);
    padding: 6px 0;
    border-top: 1px solid var(--border);
}
.mover-item:first-of-type { border-top: none; }
.research-compact-item {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.85rem;
    color: var(--text-secondary);
    padding: 3px 0;
}
.dispatch-badge {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-right: 8px;
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
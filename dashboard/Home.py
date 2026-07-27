import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

import streamlit as st
from dashboard.db_helpers import get_recent_news, get_latest_report, parse_sectors
from dashboard.theme import inject_theme

st.set_page_config(
    page_title="Finance Research Platform",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
inject_theme()

st.title("The Research Desk")
st.caption("Research assistant, not a signal generator — this dashboard explains, it doesn't tell you what to buy or sell.")

st.divider()

STAMP_CLASS = {
    "Bullish": "stamp-bullish", "Bearish": "stamp-bearish",
    "Neutral": "stamp-neutral", "Urgent": "stamp-urgent",
}
ORIGIN_STAMP_CLASS = {"Domestic": "stamp-domestic", "Global": "stamp-global"}


def _render_focus_block(label: str, positive: list, negative: list):
    """Renders a Companies/Sectors-in-Focus sub-section using the existing
    digest-section-label + digest-focus-item classes (bullish/bearish tokens,
    no new colors introduced)."""
    if not positive and not negative:
        return
    parts = [f'<div class="digest-section-label">{label}</div>']
    for item in positive:
        parts.append(f'<div class="digest-focus-item digest-focus-positive">▲ {item}</div>')
    for item in negative:
        parts.append(f'<div class="digest-focus-item digest-focus-negative">▼ {item}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_bullet_block(label: str, items: list):
    """Renders Domestic/Global highlight bullets using the existing
    section-label typography — plain list items, no sentiment coloring
    (these are informational, not judgments)."""
    if not items:
        return
    parts = [f'<div class="digest-section-label">{label}</div>']
    for item in items:
        parts.append(f'<div class="digest-focus-item">• {item}</div>')
    st.markdown("".join(parts), unsafe_allow_html=True)


def _render_chip_block(css_class: str, prefix: str, items: list):
    """Renders Risk/Opportunity items as chips — same .chip component used
    on individual article cards."""
    if not items:
        return
    chips = "".join(f'<span class="chip {css_class}">{prefix}{item}</span>' for item in items)
    st.markdown(f'<div style="margin-top:8px;">{chips}</div>', unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Daily Market Digest — hero section, always above the news feed.
# Supports: loading, error, empty (no report yet), legacy (report exists but
# has no structured_digest), and populated (structured) states.
#
# Each state uses st.container(border=True) as the visual card boundary —
# NOT a hand-opened <div>, since Streamlit renders every st.markdown/
# st.caption call as its own separate top-level element; a manually opened
# div never actually wraps later calls (confirmed via Phase 7 QA testing).
# A hidden marker span + CSS :has() selector (in theme.py) distinguishes the
# dashed empty-state variant from the solid populated/legacy variant.
# ---------------------------------------------------------------------------
st.subheader("Daily Market Digest")

st.selectbox(
    "Digest period",
    ["Today"],
    index=0,
    label_visibility="collapsed",
    key="digest_period",
    help="Weekly and monthly digests will appear here in a future update.",
)

digest_error = False
try:
    with st.spinner("Loading today's digest..."):
        report = get_latest_report("daily")
except Exception:
    report = None
    digest_error = True

if digest_error:
    with st.container(border=True):
        st.markdown('<span class="digest-marker digest-marker-empty"></span>', unsafe_allow_html=True)
        st.markdown("Something went wrong loading today's digest. Please try refreshing the page.")

elif report is None:
    with st.container(border=True):
        st.markdown('<span class="digest-marker digest-marker-empty"></span>', unsafe_allow_html=True)
        st.markdown("Today's market digest isn't available yet.")
        st.markdown("It will appear automatically after today's news analysis is complete.")

elif not report.structured_digest:
    # Legacy report generated before the structured_digest migration.
    with st.container(border=True):
        st.markdown('<span class="digest-marker"></span>', unsafe_allow_html=True)
        st.caption(f"Generated {report.generated_at}")
        st.markdown(report.content)

else:
    digest = report.structured_digest
    with st.container(border=True):
        st.markdown('<span class="digest-marker"></span>', unsafe_allow_html=True)
        st.caption(f"Generated {report.generated_at}")
        if digest.get("overall_summary"):
            st.markdown(digest["overall_summary"])

        col_a, col_b = st.columns(2)
        with col_a:
            _render_bullet_block("Domestic", digest.get("major_domestic", []))
        with col_b:
            _render_bullet_block("Global", digest.get("major_global", []))

        col_c, col_d = st.columns(2)
        with col_c:
            _render_focus_block(
                "Companies in Focus",
                digest.get("companies_positive", []),
                digest.get("companies_negative", []),
            )
        with col_d:
            _render_focus_block(
                "Sectors in Focus",
                digest.get("sectors_positive", []),
                digest.get("sectors_negative", []),
            )

        _render_chip_block("chip-risk", "Risk: ", digest.get("risks", []))
        _render_chip_block("chip-opportunity", "Opportunity: ", digest.get("opportunities", []))

st.divider()

# ---------------------------------------------------------------------------
# News feed — full width beneath the digest.
# (Unaffected by the container bug above — each dispatch-card is built as
# one single st.markdown call with everything inline, so it always rendered
# correctly.)
# ---------------------------------------------------------------------------
st.subheader("Latest Dispatches")

try:
    with st.spinner("Loading latest dispatches..."):
        rows = get_recent_news(limit=20)
except Exception:
    rows = None
    st.markdown(
        """<div class="digest-card digest-card--empty">
        Something went wrong loading the news feed. Please try refreshing the page.
        </div>""",
        unsafe_allow_html=True,
    )

if rows is not None and not rows:
    st.markdown(
        """<div class="digest-card digest-card--empty">
        No dispatches yet — check back soon.
        </div>""",
        unsafe_allow_html=True,
    )
elif rows:
    for news, summary in rows:
        stamp_class = STAMP_CLASS.get(summary.classification, "stamp-neutral")
        badges = (
            f'<span class="dispatch-stamp {stamp_class}">{summary.classification}</span>'
            f'<span class="dispatch-stamp {stamp_class}">{summary.scope}</span>'
        )
        if summary.origin:
            origin_class = ORIGIN_STAMP_CLASS.get(summary.origin, "stamp-domestic")
            badges += f'<span class="dispatch-stamp {origin_class}">{summary.origin}</span>'

        sectors = parse_sectors(summary)
        sector_chips_html = ""
        if sectors:
            chips = "".join(f'<span class="chip chip-sector">{s}</span>' for s in sectors)
            sector_chips_html = f'<div style="margin-top:8px;">{chips}</div>'

        st.markdown(
            f"""<div class="dispatch-card">
            {badges}
            <div class="dispatch-title">{news.title}</div>
            <div class="dispatch-meta">{news.source} · {news.published_at}</div>
            {sector_chips_html}
            </div>""",
            unsafe_allow_html=True,
        )
        with st.expander("AI analysis"):
            st.write("**Summary:**", summary.ai_summary)
            st.write("**Why it matters:**", summary.why_it_matters)
            st.write("**Short-term impact:**", summary.short_term_impact)
            st.write("**Long-term impact:**", summary.long_term_impact)
            if summary.risks:
                st.markdown(
                    f'<span class="chip chip-risk">Risk: {summary.risks}</span>',
                    unsafe_allow_html=True,
                )
            if summary.opportunities:
                st.markdown(
                    f'<span class="chip chip-opportunity">Opportunity: {summary.opportunities}</span>',
                    unsafe_allow_html=True,
                )
            if summary.india_relevance:
                st.write("**India relevance:**", summary.india_relevance)
            st.markdown(f"[Read original article]({news.url})")

st.divider()
st.caption(
    "Use the pages in the sidebar for Market Overview, Sectors, Company pages, "
    "Macro dashboard, Watchlist, and the AI Research Chat."
)
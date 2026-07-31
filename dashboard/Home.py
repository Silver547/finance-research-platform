import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from datetime import datetime

import streamlit as st
from dashboard.db_helpers import (
    get_recent_news,
    get_latest_report,
    get_news_for_industry,
    get_theme_groups,
    get_transmission_items,
    get_focus_reasons,
    parse_sectors,
)
from dashboard.theme import inject_theme
from config.settings import settings

st.set_page_config(
    page_title="Finance Research Platform",
    layout="wide",
    page_icon="📊",
    initial_sidebar_state="expanded",
)
inject_theme()

# Personalize as desired — this is a single-user dashboard, so a name in the
# greeting is a small, deliberate touch rather than a generic system label.
DISPLAY_NAME = "Yash"

STAMP_CLASS = {
    "Bullish": "stamp-bullish", "Bearish": "stamp-bearish",
    "Neutral": "stamp-neutral", "Urgent": "stamp-urgent",
}
ORIGIN_STAMP_CLASS = {"Domestic": "stamp-domestic", "Global": "stamp-global"}

PERIOD_OPTIONS = {"Today": "daily", "This Week": "weekly", "This Month": "monthly"}


def _greeting() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    if hour < 17:
        return "Good afternoon"
    return "Good evening"


def _render_chip_block(css_class: str, prefix: str, items: list):
    """Renders Risk/Opportunity items as chips — same .chip component used
    on individual article cards. Unchanged from the previous version."""
    if not items:
        return
    chips = "".join(f'<span class="chip {css_class}">{prefix}{item}</span>' for item in items)
    st.markdown(f'<div style="margin-top:8px;">{chips}</div>', unsafe_allow_html=True)


def _render_focus_with_reason(label: str, positive: list, negative: list, reason_map: dict):
    """Renders a Companies/Sectors-in-Focus sub-section, extended from the
    previous _render_focus_block to include a plain-language 'why' line
    under each item (from get_focus_reasons()). Falls back gracefully if no
    reason was found for a given name."""
    if not positive and not negative:
        return
    st.markdown(f'<div class="digest-section-label">{label}</div>', unsafe_allow_html=True)
    fallback = "Notable activity today — see the news feed below for details."
    for name in positive:
        reason = reason_map.get(name, fallback)
        st.markdown(
            f'<div class="digest-focus-item digest-focus-positive">▲ {name}</div>'
            f'<div class="dispatch-meta">Reason: {reason}</div>',
            unsafe_allow_html=True,
        )
    for name in negative:
        reason = reason_map.get(name, fallback)
        st.markdown(
            f'<div class="digest-focus-item digest-focus-negative">▼ {name}</div>'
            f'<div class="dispatch-meta">Reason: {reason}</div>',
            unsafe_allow_html=True,
        )


# ---------------------------------------------------------------------------
# 1. HEADER
# Greeting + current date + title + time filter, all in one row — the period
# selector now reads as a control over the whole page (every section below
# uses it), not just the digest.
# ---------------------------------------------------------------------------
header_col, filter_col = st.columns([3, 1])
with header_col:
    st.title("The Research Desk")
    st.caption(f"{_greeting()}, {DISPLAY_NAME} · {datetime.now().strftime('%A, %d %B %Y')}")
    st.caption("Research assistant, not a signal generator — this dashboard explains, it doesn't tell you what to buy or sell.")
with filter_col:
    period_label = st.selectbox(
        "Time Filter",
        list(PERIOD_OPTIONS.keys()),
        index=0,
        key="digest_period",
    )
period_key = PERIOD_OPTIONS[period_label]

st.divider()

# ---------------------------------------------------------------------------
# 2. TODAY'S BRIEFING
# The one section every visit should see: AI narrative, a hard-capped top-
# events list (max 5 — the platform's core anti-overload decision), and an
# at-a-glance mood read. Risks/Opportunities are folded in here too (moved
# from the old digest hero, not removed — still valuable, no new section
# needed for them).
# ---------------------------------------------------------------------------
st.subheader("Today's Briefing")

digest_error = False
try:
    with st.spinner(f"Loading {period_label.lower()}'s briefing..."):
        report = get_latest_report(period_key)
except Exception:
    report = None
    digest_error = True

digest = report.structured_digest if (report and report.structured_digest) else None

with st.container(border=True):
    if digest_error:
        st.markdown('<span class="digest-marker digest-marker-empty"></span>', unsafe_allow_html=True)
        st.markdown(f"Something went wrong loading the {period_label.lower()} briefing. Please try refreshing the page.")

    elif report is None:
        st.markdown('<span class="digest-marker digest-marker-empty"></span>', unsafe_allow_html=True)
        st.markdown(f"No {period_label.lower()} briefing is available yet.")
        st.markdown("It will appear automatically after the next scheduled report run.")

    elif digest is None:
        # Legacy report generated before the structured_digest migration.
        st.markdown('<span class="digest-marker"></span>', unsafe_allow_html=True)
        st.caption(f"Generated {report.generated_at}")
        st.markdown(report.content)

    else:
        st.markdown('<span class="digest-marker"></span>', unsafe_allow_html=True)
        st.caption(f"Generated {report.generated_at}")

        if digest.get("overall_summary"):
            st.markdown(digest["overall_summary"])

        # Top events: merge domestic + global highlights and cap at 5 total.
        # Each source list is already ranked Urgent-first / by |sentiment| in
        # report_agent.py, so a simple 3+2 interleave keeps that ordering
        # intact without needing a new query.
        top_events = (digest.get("major_domestic", [])[:3] + digest.get("major_global", [])[:2])[:5]
        if top_events:
            st.markdown("**Top events**")
            for item in top_events:
                st.markdown(f"- {item}")

        # Overall mood: a lightweight proxy from the digest's own positive/
        # negative counts (zero new queries). Not a true sentiment average —
        # see follow-up notes if you want this more rigorous.
        pos_count = len(digest.get("companies_positive", [])) + len(digest.get("sectors_positive", []))
        neg_count = len(digest.get("companies_negative", [])) + len(digest.get("sectors_negative", []))
        if pos_count == 0 and neg_count == 0:
            mood_label, mood_class = "Quiet", "stamp-neutral"
        elif pos_count > neg_count:
            mood_label, mood_class = "Constructive", "stamp-bullish"
        elif neg_count > pos_count:
            mood_label, mood_class = "Cautious", "stamp-bearish"
        else:
            mood_label, mood_class = "Mixed", "stamp-neutral"
        st.markdown(
            f'<span class="dispatch-stamp {mood_class}">Mood: {mood_label}</span>',
            unsafe_allow_html=True,
        )

        _render_chip_block("chip-risk", "Risk: ", digest.get("risks", []))
        _render_chip_block("chip-opportunity", "Opportunity: ", digest.get("opportunities", []))

st.divider()

# ---------------------------------------------------------------------------
# 3. MAJOR MARKET THEMES
# NOTE: the platform doesn't yet have a dedicated "Economic Theme" entity
# (Oil/Inflation/AI/China as cross-cutting concepts, independent of tracked
# sectors). This groups by tracked Industry instead, as an honest best-effort
# proxy — it correctly clusters sector-shaped themes (Oil & Gas, Banking) but
# can't yet surface themes that aren't industries (Inflation, China, AI).
# Flagged explicitly rather than silently pretending to be complete.
# ---------------------------------------------------------------------------
st.subheader("Major Market Themes")
st.caption(
    "Grouped by tracked sector for now — cross-cutting themes like Inflation "
    "or China would need a dedicated Theme model (see follow-up notes)."
)

theme_groups = get_theme_groups(period_key, max_groups=6, max_items=3)

if not theme_groups:
    st.markdown(
        '<div class="digest-card digest-card--empty">No grouped themes yet for this period.</div>',
        unsafe_allow_html=True,
    )
else:
    cols = st.columns(min(3, len(theme_groups)))
    for i, group in enumerate(theme_groups):
        with cols[i % len(cols)]:
            with st.expander(f"{group['name']} ({group['count']})"):
                for news, summary in group["items"]:
                    stamp_class = STAMP_CLASS.get(summary.classification, "stamp-neutral")
                    st.markdown(
                        f'<span class="dispatch-stamp {stamp_class}">{summary.classification}</span> {news.title}',
                        unsafe_allow_html=True,
                    )

st.divider()

# ---------------------------------------------------------------------------
# 4. GLOBAL -> INDIA TRANSMISSION MAP
# The signature section: renders the platform's existing origin/india_
# relevance reasoning as an explicit chain (Global Event -> Indian Impact ->
# Sectors -> Companies) instead of a single free-text field buried in one
# news card's expander.
# ---------------------------------------------------------------------------
st.subheader("Global → India Transmission Map")

transmission_items = get_transmission_items(period_key, limit=4)

if not transmission_items:
    st.markdown(
        '<div class="digest-card digest-card--empty">No global-origin stories with a clear India angle this period.</div>',
        unsafe_allow_html=True,
    )
else:
    for item in transmission_items:
        news, summary = item["news"], item["summary"]
        with st.container(border=True):
            st.markdown('<span class="dispatch-stamp stamp-global">Global Event</span>', unsafe_allow_html=True)
            st.markdown(f"**{news.title}**")

            st.markdown('<div class="digest-section-label">↓ Indian Impact</div>', unsafe_allow_html=True)
            st.markdown(summary.india_relevance or "_No specific India linkage identified for this story._")

            if item["sectors"]:
                st.markdown('<div class="digest-section-label">↓ Affected Sectors</div>', unsafe_allow_html=True)
                chips = "".join(f'<span class="chip chip-sector">{s}</span>' for s in item["sectors"])
                st.markdown(f'<div>{chips}</div>', unsafe_allow_html=True)

            if item["companies"]:
                st.markdown('<div class="digest-section-label">↓ Affected Companies</div>', unsafe_allow_html=True)
                # Reusing .chip-sector for companies too — no new CSS class
                # in this pass (this is a foundation task, not visual
                # polish). A dedicated chip-company style is an easy
                # follow-up if you want visual distinction later.
                chips = "".join(f'<span class="chip chip-sector">{c}</span>' for c in item["companies"])
                st.markdown(f'<div>{chips}</div>', unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------------------------
# 5. COMPANIES & SECTORS IN FOCUS
# Reuses the same `digest` fetched in Today's Briefing (no duplicate query)
# for the *names*, and adds a "why" line per item via get_focus_reasons(),
# since structured_digest only stores names/sentiment, not attribution.
# ---------------------------------------------------------------------------
st.subheader("Companies & Sectors in Focus")

if digest is None:
    st.markdown(
        '<div class="digest-card digest-card--empty">No focus data available for this period yet.</div>',
        unsafe_allow_html=True,
    )
else:
    reasons = get_focus_reasons(period_key)

    col_a, col_b = st.columns(2)
    with col_a:
        _render_focus_with_reason(
            "Companies",
            digest.get("companies_positive", []),
            digest.get("companies_negative", []),
            reasons["companies"],
        )
    with col_b:
        _render_focus_with_reason(
            "Sectors",
            digest.get("sectors_positive", []),
            digest.get("sectors_negative", []),
            reasons["sectors"],
        )

st.divider()

# ---------------------------------------------------------------------------
# 6. RESEARCH NEXT
# Templated jumping-off points, never recommendations. Built entirely from
# data already fetched above — no new queries.
# ---------------------------------------------------------------------------
st.subheader("Research Next")

prompts = []
if theme_groups:
    prompts.append(f"Explore today's {theme_groups[0]['name']} coverage in more depth on the Sectors page.")
if digest and digest.get("companies_positive"):
    prompts.append(f"Read the latest on {digest['companies_positive'][0]} on the Company page.")
if digest and digest.get("companies_negative"):
    prompts.append(f"See what's behind today's move for {digest['companies_negative'][0]}.")
prompts.append("Compare today's RBI/Fed commentary (if any) against the Macro dashboard's recent history.")
prompts.append("Browse the full news feed below for anything not covered above.")

for p in prompts[:5]:
    st.markdown(f"→ {p}")

st.divider()

# ---------------------------------------------------------------------------
# 7. NEWS FEED
# Moved to the very bottom, given basic filters so it no longer dominates
# the page. Rendering itself is unchanged from the previous version.
# ---------------------------------------------------------------------------
st.subheader("Latest Dispatches")

filter_col1, filter_col2 = st.columns([2, 1])
with filter_col1:
    feed_filter = st.selectbox(
        "Filter",
        ["All"] + list(settings.TRACKED_INDUSTRIES),
        index=0,
        label_visibility="collapsed",
        key="news_feed_sector_filter",
    )
with filter_col2:
    urgent_only = st.checkbox("Urgent only", value=False, key="news_feed_urgent_only")

try:
    with st.spinner("Loading latest dispatches..."):
        if feed_filter == "All":
            rows = get_recent_news(limit=20)
        else:
            rows = get_news_for_industry(feed_filter, limit=20)
except Exception:
    rows = None
    st.markdown(
        """<div class="digest-card digest-card--empty">
        Something went wrong loading the news feed. Please try refreshing the page.
        </div>""",
        unsafe_allow_html=True,
    )

if rows is not None and urgent_only:
    rows = [(n, s) for n, s in rows if s.classification == "Urgent"]

if rows is not None and not rows:
    st.markdown(
        """<div class="digest-card digest-card--empty">
        No dispatches match this filter — check back soon or try a different one.
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
    "Macro dashboard, and Watchlist."
)
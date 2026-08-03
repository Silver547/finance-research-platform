"""
The "Today" page — V2 Home redesign, Phase 1.

Sections implemented this phase, per the approved V2 blueprint:
  1. Hero (mood icon + editorial headline, minimal text by default)
  2. Market Snapshot (Mood / Confidence / Importance / Top Risk / Top
     Opportunity — all report-level, per the locked-in Confidence/
     Importance architecture decision)
  3. Global Drivers (report-level, LLM-classified — see
     agents/report_agent.py)

Plus four retained V1 sections, each visibly marked "(Preview)" per the
V1->V2 transition plan (Group B: kept, but compacted — nothing here is a
final destination, later phases replace each with its named V2 section):
  - Economic Ripple (Preview) — was "Global -> India Transmission Map"
  - Market Movers (Preview) — was "Companies & Sectors in Focus"
  - Continue Research (compact card) — was "Research Next"
  - Latest Dispatches (top 5 only) — was the full "Latest Dispatches" feed

Major Market Themes (V1) is NOT here — Group C, hidden entirely, its
information now lives in Hero/Snapshot/Drivers instead (duplication,
per product decision).
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from dashboard.db_helpers import (
    get_latest_report,
    get_transmission_items,
    get_top_dispatches,
)
from dashboard.components import (
    mood_dot,
    classification_dot,
    render_dots,
    render_snapshot_row,
    render_driver_card,
    preview_label,
)

PERIOD_OPTIONS = {"Today": "daily", "This Week": "weekly", "This Month": "monthly"}

period_label = st.selectbox(
    "Time period",
    list(PERIOD_OPTIONS.keys()),
    index=0,
    label_visibility="collapsed",
    key="today_period",
)
period_key = PERIOD_OPTIONS[period_label]

digest_error = False
try:
    with st.spinner(f"Loading {period_label.lower()}'s market read..."):
        report = get_latest_report(period_key)
except Exception as exc:
    st.exception(exc)  # TEMPORARY — remove once diagnosed
    report = None
    digest_error = True

digest = report.structured_digest if (report and report.structured_digest) else None

# ---------------------------------------------------------------------------
# Empty / error / legacy states — same graceful-degradation pattern used
# throughout this project. Legacy here means a report exists from before
# this phase's schema additions (no headline/confidence/importance/drivers
# yet), so it falls back to the plain narrative with no V2 elements.
# ---------------------------------------------------------------------------
if digest_error:
    st.error(f"Something went wrong loading the {period_label.lower()} market read. Please try refreshing.")
elif report is None:
    st.info(f"No {period_label.lower()} report is available yet. It will appear after the next scheduled run.")
elif digest is None:
    st.caption(f"Generated {report.generated_at}")
    st.markdown(report.content)
else:
    # =========================================================================
    # 1 & 2. HERO + MARKET SNAPSHOT (two-column top band)
    # =========================================================================
    hero_col, snapshot_col = st.columns([2, 1])

    # Mood is computed deterministically (not LLM-generated) from the
    # existing companies/sectors positive-negative counts — unchanged logic
    # from the prior hero pass, kept simple per "don't add complexity
    # without a clear need." There is no "mood" key in structured_digest.
    pos_count = len(digest.get("companies_positive", [])) + len(digest.get("sectors_positive", []))
    neg_count = len(digest.get("companies_negative", [])) + len(digest.get("sectors_negative", []))
    if pos_count == 0 and neg_count == 0:
        mood_label = "Quiet"
    elif pos_count > neg_count:
        mood_label = "Constructive"
    elif neg_count > pos_count:
        mood_label = "Cautious"
    else:
        mood_label = "Mixed"

    with hero_col:
        st.markdown(f'<div class="hero-mood-icon">{mood_dot(mood_label)}</div>', unsafe_allow_html=True)
        if digest.get("headline"):
            st.markdown(f'<div class="hero-v2-headline">{digest["headline"]}</div>', unsafe_allow_html=True)
        with st.expander("Read Full Story"):
            st.caption(f"Generated {report.generated_at}")
            if digest.get("overall_summary"):
                st.write(digest["overall_summary"])

    with snapshot_col:
        with st.container(border=True):
            st.markdown('<div class="snapshot-title">Market Snapshot</div>', unsafe_allow_html=True)
            render_snapshot_row("Mood", f'{mood_dot(mood_label)} {mood_label}')
            render_snapshot_row("Confidence", render_dots(digest.get("confidence", 0)))
            render_snapshot_row("Importance", render_dots(digest.get("importance", 0)))

            risks = digest.get("risks", [])
            opportunities = digest.get("opportunities", [])
            render_snapshot_row("Top Risk", risks[0] if risks else "None flagged today")
            render_snapshot_row("Top Opportunity", opportunities[0] if opportunities else "None flagged today")

    st.divider()

    # =========================================================================
    # 3. GLOBAL DRIVERS
    # =========================================================================
    st.subheader("What's Driving Markets Today?")
    drivers = digest.get("drivers", [])

    if not drivers:
        st.caption("No drivers identified for this period yet.")
    else:
        driver_cols = st.columns(len(drivers))
        for col, driver in zip(driver_cols, drivers):
            with col:
                render_driver_card(driver)

    st.divider()

    # =========================================================================
    # GROUP B — Economic Ripple (Preview)
    # was: "Global -> India Transmission Map"
    # =========================================================================
    st.markdown(
        f'<h3 style="display:inline;">How Did It Reach India?</h3> {preview_label()}',
        unsafe_allow_html=True,
    )

    transmission_preview = get_transmission_items(period_key, limit=1)
    transmission_more = None  # only fetched if the user expands

    if not transmission_preview:
        st.caption("No global-origin stories with a clear India angle this period.")
    else:
        item = transmission_preview[0]
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
                chips = "".join(f'<span class="chip chip-sector">{c}</span>' for c in item["companies"])
                st.markdown(f'<div>{chips}</div>', unsafe_allow_html=True)

        with st.expander("Explore Full Impact"):
            transmission_more = get_transmission_items(period_key, limit=4)[1:]
            if not transmission_more:
                st.caption("No additional chains for this period.")
            for item in transmission_more:
                news, summary = item["news"], item["summary"]
                with st.container(border=True):
                    st.markdown('<span class="dispatch-stamp stamp-global">Global Event</span>', unsafe_allow_html=True)
                    st.markdown(f"**{news.title}**")
                    st.markdown('<div class="digest-section-label">↓ Indian Impact</div>', unsafe_allow_html=True)
                    st.markdown(summary.india_relevance or "_No specific India linkage identified for this story._")
                    if item["sectors"]:
                        chips = "".join(f'<span class="chip chip-sector">{s}</span>' for s in item["sectors"])
                        st.markdown(f'<div style="margin-top:6px;">{chips}</div>', unsafe_allow_html=True)
                    if item["companies"]:
                        chips = "".join(f'<span class="chip chip-sector">{c}</span>' for c in item["companies"])
                        st.markdown(f'<div style="margin-top:6px;">{chips}</div>', unsafe_allow_html=True)

    st.divider()

    # =========================================================================
    # GROUP B — Market Movers (Preview)
    # was: "Companies & Sectors in Focus". Names only, no paragraphs, no
    # reasons — get_focus_reasons() is deliberately not called here.
    # =========================================================================
    st.markdown(
        f'<h3 style="display:inline;">Who Moved Today?</h3> {preview_label()}',
        unsafe_allow_html=True,
    )

    top_companies = (digest.get("companies_positive", []) + digest.get("companies_negative", []))[:3]
    top_sectors = (digest.get("sectors_positive", []) + digest.get("sectors_negative", []))[:3]
    positive_companies = set(digest.get("companies_positive", []))
    positive_sectors = set(digest.get("sectors_positive", []))

    movers_col_a, movers_col_b = st.columns(2)
    with movers_col_a:
        st.markdown('<div class="digest-section-label">Top Companies</div>', unsafe_allow_html=True)
        if not top_companies:
            st.caption("No companies crossed the threshold this period.")
        for name in top_companies:
            arrow = "▲" if name in positive_companies else "▼"
            st.markdown(f'<div class="mover-item">{arrow} {name}</div>', unsafe_allow_html=True)
    with movers_col_b:
        st.markdown('<div class="digest-section-label">Top Sectors</div>', unsafe_allow_html=True)
        if not top_sectors:
            st.caption("No sectors crossed the threshold this period.")
        for name in top_sectors:
            arrow = "▲" if name in positive_sectors else "▼"
            st.markdown(f'<div class="mover-item">{arrow} {name}</div>', unsafe_allow_html=True)

    st.divider()

    # =========================================================================
    # GROUP B — Continue Research (compact card)
    # was: "Research Next". Now pulls from Drivers instead of the hidden
    # Major Market Themes section, since that's no longer computed on this
    # page — avoids running a query solely to power one text line.
    # =========================================================================
    st.subheader("Continue Research")
    with st.container(border=True):
        topics = [d["name"] for d in drivers[:3]] if drivers else []
        if not topics:
            st.markdown(
                '<div class="research-compact-item">Nothing specific to suggest yet — check back once today\'s drivers are identified.</div>',
                unsafe_allow_html=True,
            )
        else:
            for topic in topics:
                st.markdown(f'<div class="research-compact-item">• {topic}</div>', unsafe_allow_html=True)

    st.divider()

    # =========================================================================
    # GROUP B — Latest Dispatches (top 5 only)
    # ===========================================================================
    st.subheader("What Should I Read?")

    top_dispatches = get_top_dispatches(limit=5)

    if not top_dispatches:
        st.caption("No dispatches yet — check back soon.")
    else:
        for news, summary in top_dispatches:
            st.markdown(
                f'<span class="dispatch-badge">{classification_dot(summary.classification)} {summary.classification}</span>'
                f'<span class="dispatch-title">{news.title}</span>'
                f'<div class="dispatch-meta">{news.source}</div>',
                unsafe_allow_html=True,
            )

        with st.expander("View Full Feed"):
            more_dispatches = get_top_dispatches(limit=20)[5:]
            if not more_dispatches:
                st.caption("No additional dispatches right now.")
            for news, summary in more_dispatches:
                st.markdown(
                    f'<span class="dispatch-badge">{classification_dot(summary.classification)} {summary.classification}</span>'
                    f'<span class="dispatch-title">{news.title}</span>'
                    f'<div class="dispatch-meta">{news.source}</div>',
                    unsafe_allow_html=True,
                )

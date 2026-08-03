"""
The Research page (V2, Phase 1) — new page, no V1 equivalent.

Per explicit scope: doesn't need full functionality yet. What's here is
real and working (search actually searches, Recent Reports shows actual
reports), not stubbed — "Saved Research" is an honest empty state
explaining what to use instead today, not a TODO or dead button.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))

import streamlit as st

from dashboard.db_helpers import search_news, get_recent_reports
from dashboard.components import classification_dot

st.title("Research")
st.caption("Search past coverage, revisit generated reports, and (soon) save research threads.")

st.divider()

# ---------------------------------------------------------------------------
# Universal Search — a real, working substring search over headline titles.
# ---------------------------------------------------------------------------
st.subheader("Universal Search")
query = st.text_input("Search headlines", placeholder="e.g. Oil, RBI, TCS, Fed...", label_visibility="collapsed")

if query.strip():
    results = search_news(query.strip(), limit=20)
    if not results:
        st.caption(f"No headlines matching \"{query}\".")
    else:
        for news, summary in results:
            st.markdown(
                f'<span class="dispatch-badge">{classification_dot(summary.classification)} {summary.classification}</span>'
                f'<span class="dispatch-title">{news.title}</span>'
                f'<div class="dispatch-meta">{news.source} · {news.published_at}</div>',
                unsafe_allow_html=True,
            )

st.divider()

# ---------------------------------------------------------------------------
# Recent Reports — real Report rows, most recent first, across all periods.
# ---------------------------------------------------------------------------
st.subheader("Recent Reports")
reports = get_recent_reports(limit=10)

if not reports:
    st.caption("No reports generated yet.")
else:
    for report in reports:
        headline = ""
        if report.structured_digest:
            headline = report.structured_digest.get("headline", "")
        label = headline or f"{report.report_type.capitalize()} report"
        with st.expander(f"{label} — {report.generated_at}"):
            st.caption(f"Type: {report.report_type} · Generated: {report.generated_at}")
            st.write(report.content)

st.divider()

# ---------------------------------------------------------------------------
# Saved Research — no such feature exists yet. Honest empty state, not a
# placeholder — real, informative copy about what to use today instead.
# ---------------------------------------------------------------------------
st.subheader("Saved Research")
st.info(
    "Saved Research threads aren't available yet. For now, use your "
    "Watchlist (under the ⚙ icon in the header) to track specific companies."
)

with st.expander("What's coming to Research"):
    st.markdown(
        "- Deeper, multi-step research threads you can save and return to\n"
        "- Filtering search by sector, company, or Driver\n"
        "- Linking saved research to your Watchlist"
    )

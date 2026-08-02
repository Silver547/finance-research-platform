"""
Shared, reusable rendering components for the dashboard.

Introduced with the V2 navigation migration (Phase 1) specifically so that
Confidence/Importance dots, the mood icon, and driver cards have one
implementation instead of being redefined per page as later phases bring
these same concepts to Companies, Industries, and Research pages.

Everything here is presentation-only — no DB session handling, no queries.
Callers pass in already-fetched data (a `digest` dict, a `driver` dict, a
classification string, etc.).
"""
import streamlit as st

MOOD_DOT = {
    "Constructive": "🟢",
    "Cautious": "🔴",
    "Mixed": "🟡",
    "Quiet": "⚪",
}

# Per the explicit V2 badge spec: Urgent and Bearish intentionally share
# the same red dot here. This differs from the full news pages' existing
# .dispatch-stamp treatment, where Urgent has its own distinct orange
# (--urgent token in theme.py) — that component is untouched; this is a
# separate, deliberately more compact badge for preview surfaces only.
CLASSIFICATION_DOT = {
    "Urgent": "🔴",
    "Bullish": "🟢",
    "Bearish": "🔴",
    "Neutral": "⚪",
}

# Substring-matched (not exact-match) against a driver's LLM-generated
# name, since driver names are open-ended text, not a fixed enum — a
# dict of common keywords covers most real cases without forcing the LLM
# into a fixed vocabulary.
_DRIVER_ICON_KEYWORDS = {
    "oil": "🛢", "crude": "🛢",
    "fed": "🇺🇸", "federal reserve": "🇺🇸", "dollar": "💵", "usd": "💵",
    "rbi": "🏦", "rupee": "🏦",
    "china": "🇨🇳",
    "inflation": "📈",
    "ai": "🤖", "artificial intelligence": "🤖",
    "geopolit": "🌐",
    "consumption": "🛒", "demand": "🛒",
    "manufactur": "🏭",
    "earnings": "💻", "it services": "💻",
}


def mood_dot(mood_label: str) -> str:
    """Returns the emoji glyph for a mood label. Emoji are fixed-color
    glyphs, not CSS-colorable — 'dynamic color' means swapping which
    glyph renders, not recoloring one fixed dot."""
    return MOOD_DOT.get(mood_label, "⚪")


def classification_dot(classification: str) -> str:
    """Returns the emoji glyph for a headline classification, per the V2
    Latest Dispatches badge spec."""
    return CLASSIFICATION_DOT.get(classification, "⚪")


def driver_icon(name: str) -> str:
    """Best-effort icon for a driver name, via substring keyword match
    (driver names are open-ended LLM output, not a fixed list)."""
    lowered = (name or "").lower()
    for keyword, icon in _DRIVER_ICON_KEYWORDS.items():
        if keyword in lowered:
            return icon
    return "📊"


def render_dots(value: int, max_dots: int = 5) -> str:
    """Renders a 0-100 score as a filled/unfilled dot row (e.g. ●●●○○),
    used for Confidence and Importance wherever they appear (Market
    Snapshot, Global Drivers, and any future page that adopts them)."""
    try:
        value = int(value)
    except (TypeError, ValueError):
        value = 0
    value = max(0, min(100, value))
    filled = max(0, min(max_dots, round((value / 100) * max_dots)))
    return "●" * filled + "○" * (max_dots - filled)


def render_snapshot_row(label: str, value_html: str):
    """One compact row inside the Market Snapshot card."""
    st.markdown(
        f'<div class="snapshot-row">'
        f'<span class="snapshot-label">{label}</span>'
        f'<span class="snapshot-value">{value_html}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_driver_card(driver: dict):
    """Renders one Global Driver card: icon + name, importance/confidence
    dots, and a 'Read More' expander with the one-line summary and
    supporting headlines. `driver` is one entry from
    structured_digest['drivers'] (see agents/report_agent.py)."""
    name = driver.get("name", "Unknown")
    importance = driver.get("importance", 0)
    confidence = driver.get("confidence", 0)
    summary = driver.get("summary", "")
    supporting = driver.get("supporting_headlines", [])

    with st.container(border=True):
        st.markdown(
            f'<div class="driver-name">{driver_icon(name)} {name}</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<div class="driver-meta">Importance {render_dots(importance)}</div>'
            f'<div class="driver-meta">Confidence {render_dots(confidence)}</div>',
            unsafe_allow_html=True,
        )
        with st.expander("Read more"):
            if summary:
                st.markdown(f'<div class="driver-summary">{summary}</div>', unsafe_allow_html=True)
            for headline in supporting:
                st.markdown(f'<div class="driver-headline">• {headline}</div>', unsafe_allow_html=True)
            if not summary and not supporting:
                st.markdown(
                    '<div class="driver-headline">No further detail available for this driver.</div>',
                    unsafe_allow_html=True,
                )


def preview_label() -> str:
    """The small dashed '(Preview)' marker used on every retained V1
    section during the V1->V2 transition, so it's visibly distinct from
    a finished V2 destination."""
    return '<span class="preview-label">Preview</span>'
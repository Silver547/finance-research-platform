"""
Builds a daily/weekly/monthly digest from what's already in the DB
(no new LLM calls needed for the raw data — it just composes what the
tagging/impact agents already produced, plus one LLM call to write the
narrative wrap-up + editorial headline).

Phase 6 addition: alongside `content` (the narrative + raw-items text), this
now also assembles `structured_digest` — structured data for the dashboard's
Digest hero section (Companies in Focus, Sectors in Focus, Risks,
Opportunities, Domestic/Global highlights). These are derived deterministically
from fields the tagging/impact agents already produced (classification,
sentiment_score, origin, risks, opportunities, company/industry tags). No
markdown parsing of the narrative is used.

Phase 8 addition: the single narrative LLM call now also returns a short
editorial-style headline (8-15 words) via one combined JSON response,
rather than a second LLM call — kept to one call per report generation to
respect the free-tier daily quota.
"""
import argparse
import logging
from collections import defaultdict
from datetime import date, timedelta

from backend.db.session import get_session, init_db
from backend.models.models import (
    News, NewsAISummary, Report, Company, Industry,
    NewsCompanyTag, NewsIndustryTag,
)
from utils.llm_client import call_llm_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

PERIOD_DAYS = {"daily": 1, "weekly": 7, "monthly": 30}

# Minimum |average sentiment| across a company/sector's mentions before it's
# considered clearly positive/negative rather than mixed/neutral noise.
SENTIMENT_THRESHOLD = 0.15
MAX_FOCUS_ITEMS = 5
MAX_HIGHLIGHTS = 5

# Fallbacks used when the combined headline+narrative LLM call fails
# entirely (e.g. free-tier quota exceeded) or returns malformed JSON.
FALLBACK_HEADLINE = "Today's Market Update"
FALLBACK_NARRATIVE = (
    "AI narrative unavailable today (likely hit the free daily quota). "
    "Raw items are still listed below."
)


def _split_sectors(raw: str) -> list[str]:
    """Splits the comma-joined likely_affected_indian_sectors column into a clean list."""
    if not raw:
        return []
    return [s.strip() for s in raw.split(",") if s.strip()]


def _aggregate_companies(session, news_ids: list[int], sentiment_by_news_id: dict) -> tuple[list[str], list[str]]:
    """Averages sentiment per company across the period's tagged news,
    returning (positive names, negative names) sorted by strength."""
    if not news_ids:
        return [], []

    tag_rows = (
        session.query(NewsCompanyTag, Company)
        .join(Company, Company.company_id == NewsCompanyTag.company_id)
        .filter(NewsCompanyTag.news_id.in_(news_ids))
        .all()
    )

    scores = defaultdict(list)
    for tag, company in tag_rows:
        score = sentiment_by_news_id.get(tag.news_id)
        if score is not None:
            scores[company.name].append(score)

    averaged = {name: sum(vals) / len(vals) for name, vals in scores.items()}
    positive = sorted(
        (n for n, s in averaged.items() if s >= SENTIMENT_THRESHOLD),
        key=lambda n: averaged[n], reverse=True,
    )[:MAX_FOCUS_ITEMS]
    negative = sorted(
        (n for n, s in averaged.items() if s <= -SENTIMENT_THRESHOLD),
        key=lambda n: averaged[n],
    )[:MAX_FOCUS_ITEMS]
    return positive, negative


def _aggregate_sectors(session, news_ids: list[int], sentiment_by_news_id: dict,
                        sectors_by_news_id: dict) -> tuple[list[str], list[str]]:
    """Combines directly-tagged industries with AI-inferred
    likely_affected_indian_sectors, averaging sentiment per sector name."""
    if not news_ids:
        return [], []

    scores = defaultdict(list)

    tag_rows = (
        session.query(NewsIndustryTag, Industry)
        .join(Industry, Industry.industry_id == NewsIndustryTag.industry_id)
        .filter(NewsIndustryTag.news_id.in_(news_ids))
        .all()
    )
    for tag, industry in tag_rows:
        score = sentiment_by_news_id.get(tag.news_id)
        if score is not None:
            scores[industry.name].append(score)

    for news_id, sector_names in sectors_by_news_id.items():
        score = sentiment_by_news_id.get(news_id)
        if score is None:
            continue
        for name in sector_names:
            scores[name].append(score)

    averaged = {name: sum(vals) / len(vals) for name, vals in scores.items()}
    positive = sorted(
        (n for n, s in averaged.items() if s >= SENTIMENT_THRESHOLD),
        key=lambda n: averaged[n], reverse=True,
    )[:MAX_FOCUS_ITEMS]
    negative = sorted(
        (n for n, s in averaged.items() if s <= -SENTIMENT_THRESHOLD),
        key=lambda n: averaged[n],
    )[:MAX_FOCUS_ITEMS]
    return positive, negative


def _top_highlights(rows, origin_filter: str) -> list[str]:
    """Picks the most significant headlines for a given origin (Domestic/Global),
    Urgent items first, then ranked by |sentiment_score|. Rows with no origin
    set (pre-Phase-4 records) simply won't match either filter."""
    candidates = [
        (news, summary) for news, summary in rows
        if summary.origin == origin_filter
    ]
    candidates.sort(
        key=lambda pair: (
            pair[1].classification != "Urgent",
            -abs(pair[1].sentiment_score or 0),
        )
    )
    return [news.title for news, _ in candidates[:MAX_HIGHLIGHTS]]


def _top_texts(rows, field: str) -> list[str]:
    """Collects distinct non-empty values of a per-article text field
    (risks/opportunities) from the most significant articles, Urgent first."""
    ranked = sorted(
        rows,
        key=lambda pair: (pair[1].classification != "Urgent", -abs(pair[1].sentiment_score or 0)),
    )
    seen = set()
    out = []
    for _, summary in ranked:
        value = (getattr(summary, field) or "").strip()
        if value and value not in seen:
            seen.add(value)
            out.append(value)
        if len(out) >= MAX_HIGHLIGHTS:
            break
    return out


def build_report(period: str = "daily") -> str:
    init_db()
    session = get_session()
    try:
        days = PERIOD_DAYS.get(period, 1)
        cutoff = date.today() - timedelta(days=days)

        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.published_at >= cutoff)
            .filter(News.is_duplicate.is_(False))
            .order_by(News.published_at.desc())
            .all()
        )

        structured_digest = None

        if not rows:
            headline = FALLBACK_HEADLINE
            content = f"No processed news items found for the {period} period."
        else:
            bullet_lines = []
            for news, summary in rows:
                bullet_lines.append(
                    f"- [{summary.classification}/{summary.scope}] {news.title}\n"
                    f"  Why it matters: {summary.why_it_matters}"
                )
            digest_material = "\n".join(bullet_lines)

            prompt = (
                f"You are writing a {period} financial research digest for a student investor. "
                "Using ONLY the bullet points below (already-summarized, already-classified "
                "news items), respond with ONLY a single JSON object (no other text, no markdown "
                "fences) with exactly two keys:\n"
                '  "headline": an editorial-style title, approximately 8-15 words, summarizing '
                "the single dominant market story from the items below — written like a "
                "newspaper front-page headline, not a full sentence recap\n"
                '  "narrative": a concise narrative overview covering what mattered most, any '
                "themes connecting multiple items, and what to watch next\n"
                "Do not recommend buying or selling anything in either field.\n\n"
                f"{digest_material}"
            )
            try:
                result = call_llm_json(prompt)
                headline = (result.get("headline") or "").strip()
                narrative = (result.get("narrative") or "").strip()
                if not headline or not narrative:
                    raise ValueError("LLM response missing 'headline' or 'narrative'")
            except Exception as exc:
                # Log the real exception for debugging (visible in GitHub
                # Actions run logs), but never show raw exception text
                # (API URLs, quota metadata, etc.) to the end user — a
                # fallback message should stay clean regardless of what
                # actually went wrong under the hood.
                logger.warning("Headline/narrative generation failed for %s digest: %s", period, exc)
                headline = FALLBACK_HEADLINE
                narrative = FALLBACK_NARRATIVE
            content = f"{narrative}\n\n---\n\n### Raw items covered\n\n{digest_material}"

            # --- Structured digest (Phase 6) ---
            # Derived deterministically from fields the tagging/impact agents
            # already produced — no markdown parsing, no extra LLM calls.
            news_ids = [news.news_id for news, _ in rows]
            sentiment_by_news_id = {
                news.news_id: summary.sentiment_score
                for news, summary in rows
                if summary.sentiment_score is not None
            }
            sectors_by_news_id = {
                news.news_id: _split_sectors(summary.likely_affected_indian_sectors)
                for news, summary in rows
            }

            companies_positive, companies_negative = _aggregate_companies(
                session, news_ids, sentiment_by_news_id
            )
            sectors_positive, sectors_negative = _aggregate_sectors(
                session, news_ids, sentiment_by_news_id, sectors_by_news_id
            )

            structured_digest = {
                "headline": headline,
                "overall_summary": narrative,
                "major_domestic": _top_highlights(rows, "Domestic"),
                "major_global": _top_highlights(rows, "Global"),
                "companies_positive": companies_positive,
                "companies_negative": companies_negative,
                "sectors_positive": sectors_positive,
                "sectors_negative": sectors_negative,
                # Risks/Opportunities logic is unchanged and still populated
                # here — only the Hero section's rendering of these was
                # removed (Home.py), not this underlying data. Intended for
                # reintroduction as its own analysis section later.
                "risks": _top_texts(rows, "risks"),
                "opportunities": _top_texts(rows, "opportunities"),
            }

        report = Report(
            report_type=period,
            report_date=date.today(),
            content=content,
            structured_digest=structured_digest,
        )
        session.add(report)
        session.commit()
        return content
    finally:
        session.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--period", choices=["daily", "weekly", "monthly"], default="daily")
    args = parser.parse_args()
    print(build_report(args.period))
"""
Builds a daily/weekly/monthly digest from what's already in the DB
(no new LLM calls needed for the raw data — it just composes what the
tagging/impact agents already produced, plus one LLM call to write the
narrative wrap-up, headline, confidence/importance scores, and drivers).

Phase 6 addition: alongside `content` (the narrative + raw-items text), this
now also assembles `structured_digest` — structured data for the dashboard's
Digest hero section (Companies in Focus, Sectors in Focus, Risks,
Opportunities, Domestic/Global highlights). These are derived deterministically
from fields the tagging/impact agents already produced (classification,
sentiment_score, origin, risks, opportunities, company/industry tags). No
markdown parsing of the narrative is used.

Phase 8 addition: the single narrative LLM call now also returns a short
editorial headline (8-15 words), kept to one call per report generation to
respect the free-tier daily quota.

Phase 9 (V2 Home redesign) addition: the same combined LLM call now also
returns:
  - confidence (0-100): how certain the AI is that its read of today's
    market is correct
  - importance (0-100): how much today's market should care, i.e. impact
    magnitude, not certainty
  - drivers: the 3-5 main forces moving the market today (e.g. "Oil",
    "Fed", "RBI"), each with its own importance/confidence, a one-line
    summary, and 2-3 supporting headline titles drawn from material
    already in the prompt.

Confidence and Importance are intentionally report-level concepts only —
they describe today's market and today's drivers, not individual news
articles. Individual NewsAISummary rows are untouched by this phase; see
PROJECT decision log for the reasoning (avoids ingestion-pipeline changes
for a need that's fully served at the aggregate level today).

Drivers are similarly a report-level concept, not a per-headline tag —
"what are the main forces moving today's market", not "what category does
every headline belong to". Driver names are open-ended (the LLM is not
restricted to a fixed list) and are not persisted anywhere per-headline;
if per-headline Driver tagging is ever needed (filtering, search, trend
analysis), that is a deliberate future pipeline phase, not implied by this
one.
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
MAX_DRIVERS = 5
MAX_SUPPORTING_HEADLINES_PER_DRIVER = 3

# Fallbacks used when the combined LLM call fails entirely (e.g. free-tier
# quota exceeded) or returns malformed JSON.
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


def _clamp_score(value) -> int:
    """Coerces an arbitrary LLM-returned value into a safe 0-100 int.
    Anything unparseable becomes 0 rather than raising, consistent with
    this project's fail-safe-not-fail-crash convention."""
    try:
        value = int(round(float(value)))
    except (TypeError, ValueError):
        return 0
    return max(0, min(100, value))


def _parse_drivers(raw) -> list[dict]:
    """Defensively parses the LLM's 'drivers' list into a clean, bounded
    structure. Any malformed entry is skipped rather than crashing the
    whole report — same fail-safe pattern used throughout this project."""
    if not isinstance(raw, list):
        return []

    parsed = []
    for item in raw[:MAX_DRIVERS]:
        if not isinstance(item, dict):
            continue
        name = str(item.get("name", "")).strip()
        if not name:
            continue

        supporting = item.get("supporting_headlines", [])
        if not isinstance(supporting, list):
            supporting = []
        supporting = [str(h).strip() for h in supporting if str(h).strip()]

        parsed.append({
            "name": name,
            "importance": _clamp_score(item.get("importance")),
            "confidence": _clamp_score(item.get("confidence")),
            "summary": str(item.get("summary", "")).strip(),
            "supporting_headlines": supporting[:MAX_SUPPORTING_HEADLINES_PER_DRIVER],
        })
    return parsed


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
                "fences) with exactly five keys:\n"
                '  "headline": an editorial-style title, approximately 8-15 words, summarizing '
                "the single dominant market story from the items below — written like a "
                "newspaper front-page headline, not a full sentence recap\n"
                '  "narrative": a concise narrative overview covering what mattered most, any '
                "themes connecting multiple items, and what to watch next\n"
                '  "confidence": an integer 0-100 representing how certain you are that your '
                "reading of today's market is correct — consider the number of supporting "
                "articles, how consistent they are with each other, and how clear the causal "
                "relationships are\n"
                "  \"importance\": an integer 0-100 representing how much today's market should "
                "care about today overall — consider macro significance, the number of sectors "
                "and companies affected, and expected duration of the impact. Importance is NOT "
                "the same as confidence: a highly important event can still have only moderate "
                "confidence, and vice versa\n"
                '  "drivers": a list of the 3-5 main forces actually moving the market today '
                '(e.g. "Oil", "Fed", "RBI", "Inflation", "China", "AI", "IT Earnings", "Dollar", '
                '"Geopolitics", "Consumption", "Manufacturing" — or any other name that genuinely '
                "fits; do not force-fit an item into one of these examples if it doesn't apply, "
                "and do not invent a driver that isn't actually supported by the items below). "
                "Each driver is an object with:\n"
                '    "name": short driver name (1-3 words)\n'
                '    "importance": integer 0-100 for this specific driver\n'
                '    "confidence": integer 0-100 for this specific driver\n'
                '    "summary": one sentence explaining what this driver is doing today\n'
                '    "supporting_headlines": 2-3 headline titles from the bullet points below '
                "that relate to this driver, copied exactly as they appear below\n\n"
                "Do not recommend buying or selling anything in any field.\n\n"
                f"{digest_material}"
            )
            try:
                result = call_llm_json(prompt)
                headline = (result.get("headline") or "").strip()
                narrative = (result.get("narrative") or "").strip()
                if not headline or not narrative:
                    raise ValueError("LLM response missing 'headline' or 'narrative'")
                confidence = _clamp_score(result.get("confidence"))
                importance = _clamp_score(result.get("importance"))
                drivers = _parse_drivers(result.get("drivers"))
            except Exception as exc:
                # Log the real exception for debugging (visible in GitHub
                # Actions run logs), but never show raw exception text
                # (API URLs, quota metadata, etc.) to the end user — a
                # fallback message should stay clean regardless of what
                # actually went wrong under the hood.
                logger.warning("Headline/narrative generation failed for %s digest: %s", period, exc)
                headline = FALLBACK_HEADLINE
                narrative = FALLBACK_NARRATIVE
                confidence = 0
                importance = 0
                drivers = []
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
                "confidence": confidence,
                "importance": importance,
                "drivers": drivers,
                "major_domestic": _top_highlights(rows, "Domestic"),
                "major_global": _top_highlights(rows, "Global"),
                "companies_positive": companies_positive,
                "companies_negative": companies_negative,
                "sectors_positive": sectors_positive,
                "sectors_negative": sectors_negative,
                # Risks/Opportunities logic is unchanged and still populated
                # here — the Hero section stopped rendering these directly
                # (Home.py), but Top Risk/Top Opportunity in the V2 Market
                # Snapshot card reads risks[0]/opportunities[0] from here.
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
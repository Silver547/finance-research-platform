"""
Runs the full daily pipeline end-to-end:
  1. Ingest news (RSS)
  2. Dedup
  3. Tag + analyze each new, non-duplicate headline (LLM)
  4. Ingest macro data
  5. Build/update the vector index
  6. Generate the daily report

This is the single entrypoint GitHub Actions calls every day.
Safe to re-run: every step is idempotent.
"""
import logging
import time

from backend.db.session import get_session, init_db
from backend.models.models import News, NewsAISummary, Company, NewsCompanyTag, Industry, NewsIndustryTag
from pipelines.news.fetch_rss import fetch_and_store
from pipelines.news.dedup import mark_duplicates
from pipelines.macro.fetch_macro import fetch_and_store as fetch_macro
from agents.tagging_agent import tag_headline
from agents.impact_agent import analyze_headline
from agents.report_agent import build_report

try:
    from rag.build_index import build_index
except ImportError:
    build_index = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

SECONDS_BETWEEN_LLM_CALLS = 5


def _get_or_create_company(session, ticker: str) -> Company:
    company = session.query(Company).filter_by(ticker=ticker).first()
    if not company:
        company = Company(ticker=ticker, name=ticker)
        session.add(company)
        session.commit()
    return company


def _get_or_create_industry(session, name: str) -> Industry:
    industry = session.query(Industry).filter_by(name=name).first()
    if not industry:
        industry = Industry(name=name)
        session.add(industry)
        session.commit()
    return industry


def process_new_headlines() -> int:
    """Runs tagging_agent + impact_agent on every headline that doesn't
    have an AI summary yet, skipping anything flagged as a duplicate.
    Pauses between calls to respect free-tier rate limits, and skips
    (rather than crashes on) any headline that still fails."""
    session = get_session()
    processed = 0
    try:
        pending = (
            session.query(News)
            .outerjoin(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(NewsAISummary.summary_id.is_(None))
            .filter(News.is_duplicate.is_(False))
            .all()
        )
        logger.info("Found %d headlines pending AI processing.", len(pending))

        for news in pending:
            try:
                tags = tag_headline(news.title)
                time.sleep(SECONDS_BETWEEN_LLM_CALLS)
                impact = analyze_headline(news.title, news.source or "unknown")
                time.sleep(SECONDS_BETWEEN_LLM_CALLS)
            except Exception as exc:
                logger.warning("Skipping '%s' due to error: %s", news.title[:60], exc)
                time.sleep(30)
                continue

            if impact is None:
                continue

            summary_row = NewsAISummary(
                news_id=news.news_id,
                ai_summary=impact.ai_summary,
                why_it_matters=impact.why_it_matters,
                short_term_impact=impact.short_term_impact,
                long_term_impact=impact.long_term_impact,
                risks=impact.risks,
                opportunities=impact.opportunities,
                classification=impact.classification,
                scope=impact.scope,
                sentiment_score=impact.sentiment_score,
                model_used="configured_llm_provider",
            )
            session.add(summary_row)

            for ticker in tags.companies:
                company = _get_or_create_company(session, ticker)
                session.add(NewsCompanyTag(news_id=news.news_id, company_id=company.company_id))

            for industry_name in tags.industries:
                industry = _get_or_create_industry(session, industry_name)
                session.add(NewsIndustryTag(news_id=news.news_id, industry_id=industry.industry_id))

            session.commit()
            processed += 1
            logger.info("Processed %d/%d headlines so far...", processed, len(pending))

        return processed
    finally:
        session.close()


def run_daily_pipeline():
    init_db()
    logger.info("=== Step 1: Fetch news ===")
    fetch_and_store()

    logger.info("=== Step 2: Dedup ===")
    mark_duplicates()

    logger.info("=== Step 3: Tag + analyze (LLM) ===")
    process_new_headlines()

    logger.info("=== Step 4: Fetch macro data ===")
    fetch_macro()

    if build_index:
        logger.info("=== Step 5: Build vector index ===")
        build_index()
    else:
        logger.info("=== Step 5: Skipped (chromadb not installed yet) ===")

    logger.info("=== Step 6: Generate daily report ===")
    build_report("daily")

    logger.info("=== Daily pipeline complete ===")


if __name__ == "__main__":
    run_daily_pipeline()
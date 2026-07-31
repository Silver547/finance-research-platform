"""
Shared read helpers the dashboard pages use to query the DB directly.
(For a solo-user project this is simpler than routing everything through
FastAPI; the backend/api layer is there if you later want a separate client.)
"""
from collections import defaultdict
from datetime import date, timedelta

import streamlit as st
from backend.db.session import get_session, init_db
from backend.models.models import (
    News, NewsAISummary, Company, Industry, NewsCompanyTag,
    NewsIndustryTag, MacroIndicator, Report,
)

# Mirrors agents/report_agent.py's PERIOD_DAYS convention, so "daily"/"weekly"/
# "monthly" mean the same lookback window everywhere in the app.
DAYS_BY_PERIOD = {"daily": 1, "weekly": 7, "monthly": 30}


@st.cache_resource
def _ensure_db():
    init_db()
    return True


def get_recent_news(limit: int = 30):
    _ensure_db()
    session = get_session()
    try:
        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.is_duplicate.is_(False))
            .order_by(News.published_at.desc())
            .limit(limit)
            .all()
        )
        return rows
    finally:
        session.close()


def get_news_for_company(ticker: str, limit: int = 20):
    _ensure_db()
    session = get_session()
    try:
        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .join(NewsCompanyTag, NewsCompanyTag.news_id == News.news_id)
            .join(Company, Company.company_id == NewsCompanyTag.company_id)
            .filter(Company.ticker == ticker)
            .order_by(News.published_at.desc())
            .limit(limit)
            .all()
        )
        return rows
    finally:
        session.close()


def get_news_for_industry(industry_name: str, limit: int = 20):
    _ensure_db()
    session = get_session()
    try:
        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .join(NewsIndustryTag, NewsIndustryTag.news_id == News.news_id)
            .join(Industry, Industry.industry_id == NewsIndustryTag.industry_id)
            .filter(Industry.name == industry_name)
            .order_by(News.published_at.desc())
            .limit(limit)
            .all()
        )
        return rows
    finally:
        session.close()


def get_all_companies():
    _ensure_db()
    session = get_session()
    try:
        return session.query(Company).order_by(Company.ticker).all()
    finally:
        session.close()


def get_macro_indicators():
    _ensure_db()
    session = get_session()
    try:
        return (
            session.query(MacroIndicator)
            .order_by(MacroIndicator.indicator_name, MacroIndicator.country, MacroIndicator.period)
            .all()
        )
    finally:
        session.close()


def get_latest_report(period: str = "daily"):
    _ensure_db()
    session = get_session()
    try:
        return (
            session.query(Report)
            .filter_by(report_type=period)
            .order_by(Report.generated_at.desc())
            .first()
        )
    finally:
        session.close()


def parse_sectors(summary: NewsAISummary) -> list[str]:
    """Splits the comma-joined sectors column back into a clean list."""
    if not summary.likely_affected_indian_sectors:
        return []
    return [s.strip() for s in summary.likely_affected_indian_sectors.split(",") if s.strip()]


def _rank_key(pair):
    """Shared ranking: Urgent-classification first, then by |sentiment_score|.
    Mirrors the ranking convention already used in agents/report_agent.py's
    _top_highlights()/_top_texts(), so 'most significant' means the same
    thing everywhere in the app."""
    _, summary = pair
    return (summary.classification != "Urgent", -abs(summary.sentiment_score or 0))


# ---------------------------------------------------------------------------
# New for the Home dashboard redesign (Major Market Themes, Transmission Map,
# and Companies/Sectors-in-Focus reasons). All three are read-only dashboard
# queries — no pipeline, schema, or agent changes.
# ---------------------------------------------------------------------------

def get_theme_groups(period: str = "daily", max_groups: int = 6, max_items: int = 3):
    """Groups the period's tagged news by Industry, as a best-effort proxy
    for 'economic themes' (Oil, Banking, etc.) until a dedicated Theme entity
    exists in the data model — see Known Issues / follow-up notes. Cannot
    surface cross-cutting themes that aren't tracked industries (Inflation,
    China, AI). Returns a list of {"name", "count", "items"} dicts, ordered
    by how many headlines touched that industry this period; each group's
    items are the most significant (Urgent-first, then |sentiment|),
    capped at max_items."""
    _ensure_db()
    session = get_session()
    try:
        days = DAYS_BY_PERIOD.get(period, 1)
        cutoff = date.today() - timedelta(days=days)
        rows = (
            session.query(Industry, News, NewsAISummary)
            .join(NewsIndustryTag, NewsIndustryTag.industry_id == Industry.industry_id)
            .join(News, News.news_id == NewsIndustryTag.news_id)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.published_at >= cutoff)
            .filter(News.is_duplicate.is_(False))
            .all()
        )

        groups = defaultdict(list)
        for industry, news, summary in rows:
            groups[industry.name].append((news, summary))

        ranked_groups = sorted(groups.items(), key=lambda kv: len(kv[1]), reverse=True)[:max_groups]

        result = []
        for name, items in ranked_groups:
            items_sorted = sorted(items, key=_rank_key)[:max_items]
            result.append({"name": name, "count": len(items), "items": items_sorted})
        return result
    finally:
        session.close()


def get_transmission_items(period: str = "daily", limit: int = 4):
    """Finds the period's most significant Global-origin headlines and
    attaches their tagged sectors/companies, to power the Global -> India
    Transmission Map. Returns a list of {"news", "summary", "sectors",
    "companies"} dicts, most significant first."""
    _ensure_db()
    session = get_session()
    try:
        days = DAYS_BY_PERIOD.get(period, 1)
        cutoff = date.today() - timedelta(days=days)
        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.published_at >= cutoff)
            .filter(News.is_duplicate.is_(False))
            .filter(NewsAISummary.origin == "Global")
            .all()
        )
        top_rows = sorted(rows, key=_rank_key)[:limit]
        news_ids = [news.news_id for news, _ in top_rows]

        companies_by_news = defaultdict(list)
        if news_ids:
            tag_rows = (
                session.query(NewsCompanyTag, Company)
                .join(Company, Company.company_id == NewsCompanyTag.company_id)
                .filter(NewsCompanyTag.news_id.in_(news_ids))
                .all()
            )
            for tag, company in tag_rows:
                companies_by_news[tag.news_id].append(company.name)

        result = []
        for news, summary in top_rows:
            result.append({
                "news": news,
                "summary": summary,
                "sectors": parse_sectors(summary),
                "companies": companies_by_news.get(news.news_id, []),
            })
        return result
    finally:
        session.close()


def get_focus_reasons(period: str = "daily"):
    """For the Companies/Sectors-in-Focus section: structured_digest only
    stores which companies/sectors were net-positive or net-negative, not
    *why*. This finds the single most significant headline behind each
    tagged company/sector this period and returns its why_it_matters text
    as a plain-language reason. Returns {"companies": {name: reason},
    "sectors": {name: reason}}; a name with no matching headline (e.g. a
    naming mismatch) simply won't appear, and callers should show a
    graceful fallback in that case."""
    _ensure_db()
    session = get_session()
    try:
        days = DAYS_BY_PERIOD.get(period, 1)
        cutoff = date.today() - timedelta(days=days)
        rows = (
            session.query(News, NewsAISummary)
            .join(NewsAISummary, NewsAISummary.news_id == News.news_id)
            .filter(News.published_at >= cutoff)
            .filter(News.is_duplicate.is_(False))
            .all()
        )
        ranked = sorted(rows, key=_rank_key)
        news_ids = [news.news_id for news, _ in ranked]

        company_tags = defaultdict(list)
        sector_tags = defaultdict(list)
        if news_ids:
            company_rows = (
                session.query(NewsCompanyTag, Company)
                .join(Company, Company.company_id == NewsCompanyTag.company_id)
                .filter(NewsCompanyTag.news_id.in_(news_ids))
                .all()
            )
            for tag, company in company_rows:
                company_tags[tag.news_id].append(company.name)

            industry_rows = (
                session.query(NewsIndustryTag, Industry)
                .join(Industry, Industry.industry_id == NewsIndustryTag.industry_id)
                .filter(NewsIndustryTag.news_id.in_(news_ids))
                .all()
            )
            for tag, industry in industry_rows:
                sector_tags[tag.news_id].append(industry.name)

        # `ranked` is already most-significant-first, and setdefault only
        # keeps the FIRST reason seen per name — so each name ends up with
        # its single most significant reason, not its most recent one.
        company_reasons: dict = {}
        sector_reasons: dict = {}
        for news, summary in ranked:
            reason_text = summary.why_it_matters or summary.ai_summary or ""
            for name in company_tags.get(news.news_id, []):
                company_reasons.setdefault(name, reason_text)
            sector_names = set(sector_tags.get(news.news_id, [])) | set(parse_sectors(summary))
            for name in sector_names:
                sector_reasons.setdefault(name, reason_text)

        return {"companies": company_reasons, "sectors": sector_reasons}
    finally:
        session.close()
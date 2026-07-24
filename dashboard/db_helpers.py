"""
Shared read helpers the dashboard pages use to query the DB directly.
(For a solo-user project this is simpler than routing everything through
FastAPI; the backend/api layer is there if you later want a separate client.)
"""
import streamlit as st
from backend.db.session import get_session, init_db
from backend.models.models import (
    News, NewsAISummary, Company, Industry, NewsCompanyTag,
    NewsIndustryTag, MacroIndicator, Report,
)


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

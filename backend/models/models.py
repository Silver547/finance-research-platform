"""
SQLAlchemy ORM models. Works with SQLite out of the box (DATABASE_URL default),
and with Postgres/Supabase by just changing DATABASE_URL in .env.
"""
from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Float, Text, Date, DateTime, Boolean,
    ForeignKey, UniqueConstraint
)
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Industry(Base):
    __tablename__ = "industries"
    industry_id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(Text)
    growth_drivers = Column(Text)
    risks = Column(Text)

    companies = relationship("Company", back_populates="industry")


class Company(Base):
    __tablename__ = "companies"
    company_id = Column(Integer, primary_key=True)
    ticker = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    industry_id = Column(Integer, ForeignKey("industries.industry_id"))
    country = Column(String)
    business_summary = Column(Text)
    market_cap = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)

    industry = relationship("Industry", back_populates="companies")


class FinancialStatement(Base):
    __tablename__ = "financial_statements"
    statement_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    period_end = Column(Date)
    period_type = Column(String)  # 'quarterly' | 'annual'
    revenue = Column(Float)
    net_profit = Column(Float)
    total_debt = Column(Float)
    operating_cash_flow = Column(Float)
    source_url = Column(String)


class Ratio(Base):
    __tablename__ = "ratios"
    ratio_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    period_end = Column(Date)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    roe = Column(Float)
    debt_to_equity = Column(Float)
    dividend_yield = Column(Float)


class News(Base):
    __tablename__ = "news"
    news_id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    url = Column(String, unique=True, nullable=False)
    source = Column(String)
    published_at = Column(DateTime)
    raw_hash = Column(String)
    is_duplicate = Column(Boolean, default=False)
    quality_flag = Column(String, default="unverified")  # trusted | low_quality | unverified

    ai_summary = relationship("NewsAISummary", back_populates="news", uselist=False)


class NewsAISummary(Base):
    __tablename__ = "news_ai_summary"
    summary_id = Column(Integer, primary_key=True)
    news_id = Column(Integer, ForeignKey("news.news_id"), unique=True)
    ai_summary = Column(Text)
    why_it_matters = Column(Text)
    short_term_impact = Column(Text)
    long_term_impact = Column(Text)
    risks = Column(Text)
    opportunities = Column(Text)
    classification = Column(String)   # Bullish/Bearish/Neutral/Urgent
    scope = Column(String)             # Macro/Micro/Policy/Company-specific/Sector-specific
    sentiment_score = Column(Float)
    origin = Column(String)                        # Domestic | Global
    india_relevance = Column(Text)
    likely_affected_indian_sectors = Column(Text)   # comma-separated sector names
    model_used = Column(String)
    generated_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="ai_summary")

class NewsCompanyTag(Base):
    __tablename__ = "news_company_tags"
    news_id = Column(Integer, ForeignKey("news.news_id"), primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), primary_key=True)


class NewsIndustryTag(Base):
    __tablename__ = "news_industry_tags"
    news_id = Column(Integer, ForeignKey("news.news_id"), primary_key=True)
    industry_id = Column(Integer, ForeignKey("industries.industry_id"), primary_key=True)


class CorporateAction(Base):
    __tablename__ = "corporate_actions"
    action_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    action_type = Column(String)  # merger | buyback | split | dividend | insider_trade
    details = Column(Text)
    action_date = Column(Date)
    source_url = Column(String)


class Ownership(Base):
    __tablename__ = "ownership"
    ownership_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    period_end = Column(Date)
    promoter_pct = Column(Float)
    institutional_pct = Column(Float)
    mutual_fund_pct = Column(Float)
    fii_pct = Column(Float)
    dii_pct = Column(Float)


class MacroIndicator(Base):
    __tablename__ = "macro_indicators"
    indicator_id = Column(Integer, primary_key=True)
    indicator_name = Column(String)  # GDP, CPI, PMI, Repo Rate, etc.
    country = Column(String)
    period = Column(Date)
    value = Column(Float)
    unit = Column(String)
    source = Column(String)


class Event(Base):
    __tablename__ = "events"
    event_id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.company_id"), nullable=True)
    industry_id = Column(Integer, ForeignKey("industries.industry_id"), nullable=True)
    event_type = Column(String)  # earnings | policy | macro_release | conference_call
    event_date = Column(Date)
    description = Column(Text)


class Report(Base):
    __tablename__ = "reports"
    report_id = Column(Integer, primary_key=True)
    report_type = Column(String)  # daily | weekly | monthly
    report_date = Column(Date)
    content = Column(Text)
    generated_at = Column(DateTime, default=datetime.utcnow)


class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Watchlist(Base):
    __tablename__ = "watchlists"
    watchlist_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"))
    company_id = Column(Integer, ForeignKey("companies.company_id"))
    added_at = Column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_id", "company_id", name="uq_user_company"),)


class EmbeddingIndex(Base):
    __tablename__ = "embeddings_index"
    embedding_id = Column(Integer, primary_key=True)
    source_type = Column(String)  # news | filing | transcript
    source_id = Column(Integer)
    vector_store_id = Column(String)
    chunk_text_preview = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

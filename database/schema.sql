-- Reference schema (PostgreSQL dialect). The running app generates this
-- automatically via SQLAlchemy (backend/models/models.py) against SQLite by
-- default. Use this file if you want to provision a Postgres/Supabase
-- database by hand, or as a readable reference for the data model.

CREATE TABLE industries (
    industry_id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    growth_drivers TEXT,
    risks TEXT
);

CREATE TABLE companies (
    company_id SERIAL PRIMARY KEY,
    ticker TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    industry_id INT REFERENCES industries(industry_id),
    country TEXT,
    business_summary TEXT,
    market_cap NUMERIC,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE financial_statements (
    statement_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_end DATE,
    period_type TEXT,
    revenue NUMERIC,
    net_profit NUMERIC,
    total_debt NUMERIC,
    operating_cash_flow NUMERIC,
    source_url TEXT
);

CREATE TABLE ratios (
    ratio_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_end DATE,
    pe_ratio NUMERIC,
    pb_ratio NUMERIC,
    roe NUMERIC,
    debt_to_equity NUMERIC,
    dividend_yield NUMERIC
);

CREATE TABLE news (
    news_id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT UNIQUE NOT NULL,
    source TEXT,
    published_at TIMESTAMP,
    raw_hash TEXT,
    is_duplicate BOOLEAN DEFAULT FALSE,
    quality_flag TEXT DEFAULT 'unverified'
);

CREATE TABLE news_ai_summary (
    summary_id SERIAL PRIMARY KEY,
    news_id INT UNIQUE REFERENCES news(news_id),
    ai_summary TEXT,
    why_it_matters TEXT,
    short_term_impact TEXT,
    long_term_impact TEXT,
    risks TEXT,
    opportunities TEXT,
    classification TEXT,
    scope TEXT,
    sentiment_score NUMERIC,
    model_used TEXT,
    generated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE news_company_tags (
    news_id INT REFERENCES news(news_id),
    company_id INT REFERENCES companies(company_id),
    PRIMARY KEY (news_id, company_id)
);

CREATE TABLE news_industry_tags (
    news_id INT REFERENCES news(news_id),
    industry_id INT REFERENCES industries(industry_id),
    PRIMARY KEY (news_id, industry_id)
);

CREATE TABLE corporate_actions (
    action_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    action_type TEXT,
    details TEXT,
    action_date DATE,
    source_url TEXT
);

CREATE TABLE ownership (
    ownership_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    period_end DATE,
    promoter_pct NUMERIC,
    institutional_pct NUMERIC,
    mutual_fund_pct NUMERIC,
    fii_pct NUMERIC,
    dii_pct NUMERIC
);

CREATE TABLE macro_indicators (
    indicator_id SERIAL PRIMARY KEY,
    indicator_name TEXT,
    country TEXT,
    period DATE,
    value NUMERIC,
    unit TEXT,
    source TEXT
);

CREATE TABLE events (
    event_id SERIAL PRIMARY KEY,
    company_id INT REFERENCES companies(company_id),
    industry_id INT REFERENCES industries(industry_id),
    event_type TEXT,
    event_date DATE,
    description TEXT
);

CREATE TABLE reports (
    report_id SERIAL PRIMARY KEY,
    report_type TEXT,
    report_date DATE,
    content TEXT,
    generated_at TIMESTAMP DEFAULT now()
);

CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username TEXT UNIQUE,
    created_at TIMESTAMP DEFAULT now()
);

CREATE TABLE watchlists (
    watchlist_id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(user_id),
    company_id INT REFERENCES companies(company_id),
    added_at TIMESTAMP DEFAULT now(),
    UNIQUE(user_id, company_id)
);

CREATE TABLE embeddings_index (
    embedding_id SERIAL PRIMARY KEY,
    source_type TEXT,
    source_id INT,
    vector_store_id TEXT,
    chunk_text_preview TEXT,
    created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX idx_news_published_at ON news(published_at);
CREATE INDEX idx_news_company_tags_company ON news_company_tags(company_id);
CREATE INDEX idx_financials_company_period ON financial_statements(company_id, period_end);

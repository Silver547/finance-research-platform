"""
Central configuration for the platform.
Reads from environment variables / .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    DATABASE_URL: str = "sqlite:///finance_platform.db"

    # LLM
    GOOGLE_AI_STUDIO_KEY: str = ""
    OPENROUTER_API_KEY: str = ""
    LLM_PROVIDER: str = "gemini"   # gemini | openrouter | ollama
    LLM_MODEL: str = "gemini-1.5-flash"
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # Market data (optional paid-tier keys; blank = free-only mode)
    ALPHA_VANTAGE_KEY: str = ""
    FINNHUB_KEY: str = ""
    FMP_KEY: str = ""
    TIINGO_KEY: str = ""

    # Vector store
    CHROMA_PERSIST_DIR: str = "./chroma_store"

    # Tracked universe (edit this list to whatever you actually follow)
    TRACKED_TICKERS: list[str] = [
        "AAPL", "MSFT", "NVDA", "TSLA",
        "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS",
    ]

    TRACKED_INDUSTRIES: list[str] = [
        "IT", "Banking", "Automobile", "Pharma", "FMCG",
        "Oil & Gas", "Power", "Telecom", "Semiconductors",
    ]

    NEWS_FEEDS: dict[str, str] = {
        "moneycontrol_markets": "https://www.moneycontrol.com/rss/marketreports.xml",
        "moneycontrol_business": "https://www.moneycontrol.com/rss/business.xml",
        "livemint_markets": "https://www.livemint.com/rss/markets",
        "economic_times_markets": "https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms",
        "yahoo_finance_topstories": "https://finance.yahoo.com/news/rssindex",
    }


settings = Settings()

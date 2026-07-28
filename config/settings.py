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

   
   # Tracked universe (edit this list to whatever you actually follow)
    TRACKED_TICKERS: list[str] = [
        # IT
        "TCS.NS", "INFY.NS", "HCLTECH.NS", "WIPRO.NS", "TECHM.NS",
        "LTIM.NS", "MPHASIS.NS", "PERSISTENT.NS", "COFORGE.NS", "LTTS.NS",

        # Banking
        "HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS",
        "INDUSINDBK.NS", "BANKBARODA.NS", "PNB.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",

        # Automobile
        "MARUTI.NS", "TATAMOTORS.NS", "M&M.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
        "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS",

        # Pharma
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "DIVISLAB.NS", "LUPIN.NS",
        "AUROPHARMA.NS", "TORNTPHARM.NS", "ZYDUSLIFE.NS", "ALKEM.NS", "BIOCON.NS",

        # FMCG
        "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "DABUR.NS",
        "GODREJCP.NS", "MARICO.NS", "COLPAL.NS", "TATACONSUM.NS", "VBL.NS",

        # Oil & Gas
        "RELIANCE.NS", "ONGC.NS", "IOC.NS", "BPCL.NS", "HPCL.NS",
        "GAIL.NS", "PETRONET.NS", "OIL.NS",

        # Power
        "NTPC.NS", "POWERGRID.NS", "TATAPOWER.NS", "ADANIPOWER.NS",
        "JSWENERGY.NS", "NHPC.NS", "SJVN.NS", "TORNTPOWER.NS",

        # Telecom
        "BHARTIARTL.NS", "IDEA.NS", "INDUSTOWER.NS",

        # Semiconductors (thin sector in India — design/assembly-adjacent names)
        "DIXON.NS", "TATAELXSI.NS", "BEL.NS", "VEDANTA.NS",
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

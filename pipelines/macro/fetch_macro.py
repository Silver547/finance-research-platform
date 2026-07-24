"""
Fetch macro indicators from free, official APIs (World Bank — no key needed).
Stores results into the macro_indicators table.
"""
import logging
from datetime import date

import requests

from backend.db.session import get_session, init_db
from backend.models.models import MacroIndicator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# World Bank indicator codes: https://data.worldbank.org/indicator
WORLD_BANK_INDICATORS = {
    "GDP growth (annual %)": "NY.GDP.MKTP.KD.ZG",
    "Inflation, consumer prices (annual %)": "FP.CPI.TOTL.ZG",
    "Unemployment (% of labor force)": "SL.UEM.TOTL.ZS",
}

COUNTRIES = ["US", "IN"]  # ISO2 codes; extend as needed


def fetch_world_bank_indicator(country: str, indicator_code: str) -> list[dict]:
    url = f"https://api.worldbank.org/v2/country/{country}/indicator/{indicator_code}"
    params = {"format": "json", "per_page": 5, "mrnev": 5}  # most recent 5 non-null values
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    payload = resp.json()
    if len(payload) < 2 or not payload[1]:
        return []
    return payload[1]


def fetch_and_store() -> int:
    init_db()
    session = get_session()
    stored = 0
    try:
        for name, code in WORLD_BANK_INDICATORS.items():
            for country in COUNTRIES:
                try:
                    records = fetch_world_bank_indicator(country, code)
                except Exception as exc:
                    logger.warning("Failed to fetch %s for %s: %s", name, country, exc)
                    continue

                for rec in records:
                    if rec.get("value") is None:
                        continue
                    period_year = int(rec["date"])
                    existing = (
                        session.query(MacroIndicator)
                        .filter_by(
                            indicator_name=name,
                            country=country,
                            period=date(period_year, 1, 1),
                        )
                        .first()
                    )
                    if existing:
                        continue
                    session.add(
                        MacroIndicator(
                            indicator_name=name,
                            country=country,
                            period=date(period_year, 1, 1),
                            value=rec["value"],
                            unit="%",
                            source="World Bank",
                        )
                    )
                    stored += 1
        session.commit()
        logger.info("Stored %d new macro data points.", stored)
        return stored
    finally:
        session.close()


if __name__ == "__main__":
    fetch_and_store()

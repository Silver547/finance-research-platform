"""
Fetches quarterly/annual P&L snapshot data (revenue, net profit) for
tracked Indian companies from BSE's own results-snapshot data, via the
community-maintained `bse` package.

Note: this covers P&L figures only. Full balance sheet fields (total
debt) and cash flow statement fields (operating cash flow) are NOT
available from this snapshot — BSE's resultsSnapshot() only returns
headline P&L metrics. Populating those fully would require parsing each
company's full XBRL financial-results filing — a larger, separate piece
of future work.
"""
import calendar
import logging
from datetime import date

from bse import BSE

from backend.db.session import get_session, init_db
from backend.models.models import Company, FinancialStatement
from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONTH_MAP = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}

# Tickers where BSE's own name-based lookup doesn't resolve cleanly —
# mapped directly to their known BSE scrip codes instead.
BSE_CODE_OVERRIDES = {
    "HPCL.NS": "500104",
    "VEDANTA.NS": "500295",
    "TATAMOTORS.NS": "500570",  # post-demerger passenger-vehicle entity
    "LTIM.NS": "540005",        # company renamed to "LTM Limited" in 2026
}


def parse_indian_number(s: str) -> float:
    return float(s.replace(",", ""))


def parse_period(period_label: str):
    """'Jun-26' -> (2026-06-30, 'quarterly'); 'FY25-26' -> (2026-03-31, 'annual')"""
    if period_label.startswith("FY"):
        end_year = 2000 + int(period_label.split("-")[1])
        return date(end_year, 3, 31), "annual"
    mon_str, yr_str = period_label.split("-")
    year = 2000 + int(yr_str)
    month = MONTH_MAP[mon_str]
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day), "quarterly"


def ticker_to_bse_symbol(ticker: str) -> str:
    """Strips the .NS suffix your tracking config uses — BSE's lookup wants the bare symbol."""
    return ticker.replace(".NS", "").replace(".BSE", "")


def fetch_financials_for_ticker(bse_client: BSE, session, ticker: str) -> int:
    try:
        if ticker in BSE_CODE_OVERRIDES:
            code = BSE_CODE_OVERRIDES[ticker]
        else:
            symbol = ticker_to_bse_symbol(ticker)
            code = bse_client.getScripCode(symbol)
        snapshot = bse_client.resultsSnapshot(code)
    except Exception as exc:
        logger.warning("Could not fetch financials for %s: %s", ticker, exc)
        return 0

    if not snapshot or "results_in_crores" not in snapshot:
        logger.warning("No results snapshot data for %s", ticker)
        return 0

    company = session.query(Company).filter_by(ticker=ticker).first()
    if not company:
        company = Company(ticker=ticker, name=ticker)
        session.add(company)
        session.commit()

    fields = snapshot["results_in_crores"]["fields"]  # ['title', period1, period2, period3]
    rows = snapshot["results_in_crores"]["data"]
    periods = fields[1:]
    row_by_metric = {row[0]: row[1:] for row in rows}
    saved = 0

    for i, period_label in enumerate(periods):
        period_end, period_type = parse_period(period_label)

        existing = (
            session.query(FinancialStatement)
            .filter_by(company_id=company.company_id, period_end=period_end, period_type=period_type)
            .first()
        )
        if existing:
            continue

        try:
            revenue = parse_indian_number(row_by_metric["Revenue"][i])
            net_profit = parse_indian_number(row_by_metric["Net Profit"][i])
        except (KeyError, ValueError, IndexError) as exc:
            logger.warning("Could not parse figures for %s / %s: %s", ticker, period_label, exc)
            continue

        session.add(FinancialStatement(
            company_id=company.company_id,
            period_end=period_end,
            period_type=period_type,
            revenue=revenue,
            net_profit=net_profit,
            total_debt=None,
            operating_cash_flow=None,
            source_url=snapshot.get("period_links", [{}])[0].get("LQ", ""),
        ))
        saved += 1

    session.commit()
    return saved


def fetch_all_tracked_financials() -> int:
    init_db()
    session = get_session()
    total = 0
    try:
        with BSE(download_folder="./") as bse_client:
            for ticker in settings.TRACKED_TICKERS:
                count = fetch_financials_for_ticker(bse_client, session, ticker)
                total += count
                logger.info("%s: saved %d new rows", ticker, count)
        logger.info("Done. %d total new rows saved.", total)
        return total
    finally:
        session.close()


if __name__ == "__main__":
    fetch_all_tracked_financials()
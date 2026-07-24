"""
Fetch OHLCV price data + basic technical indicators for tracked tickers
using yfinance (free, no API key required).
"""
import logging
import pandas as pd
import yfinance as yf
from ta.momentum import RSIIndicator
from ta.trend import MACD

from config.settings import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def fetch_price_history(ticker: str, period: str = "6mo", interval: str = "1d") -> pd.DataFrame:
    df = yf.Ticker(ticker).history(period=period, interval=interval)
    if df.empty:
        logger.warning("No price data returned for %s", ticker)
        return df

    df["RSI"] = RSIIndicator(close=df["Close"], window=14).rsi()
    macd = MACD(close=df["Close"])
    df["MACD"] = macd.macd()
    df["MACD_signal"] = macd.macd_signal()
    df["52w_high"] = df["Close"].rolling(window=252, min_periods=1).max()
    df["52w_low"] = df["Close"].rolling(window=252, min_periods=1).min()
    df["MA50"] = df["Close"].rolling(window=50, min_periods=1).mean()
    df["MA200"] = df["Close"].rolling(window=200, min_periods=1).mean()
    return df


def fetch_all_tracked() -> dict[str, pd.DataFrame]:
    results = {}
    for ticker in settings.TRACKED_TICKERS:
        try:
            results[ticker] = fetch_price_history(ticker)
        except Exception as exc:
            logger.warning("Failed to fetch %s: %s", ticker, exc)
    return results


if __name__ == "__main__":
    data = fetch_all_tracked()
    for ticker, df in data.items():
        print(ticker, "->", len(df), "rows")

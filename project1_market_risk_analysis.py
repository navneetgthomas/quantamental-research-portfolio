"""
Project 1: Multi-Stock Return & Risk Analysis
ASEAN Internet (GRAB, SE) and Healthcare (IHH, Kalbe Farma, BDMS) coverage.

Pulls price data across 4 exchanges with different trading calendars, forward-fills
non-trading days, and analyzes returns, correlation, and rolling volatility.
"""

import pandas as pd
import yfinance as yf

TICKERS = ["GRAB", "SE", "5225.KL", "KLBF.JK", "BDMS.BK"]
START = "2025-01-01"
END = "2025-09-01"


def get_clean_closes(tickers, start, end):
    """
    Download close prices for multiple tickers across mixed exchanges and
    forward-fill gaps caused by differing holiday calendars, so a holiday in
    one market doesn't force-drop a trading day that was valid in the others.
    """
    data = yf.download(tickers, start=start, end=end)
    closes = data["Close"]
    closes_filled = closes.ffill()
    return closes_filled


def calculate_returns(closes):
    """Daily % returns, with the unavoidable leading NaN (no prior day) dropped."""
    return closes.pct_change().dropna()


def build_correlation_matrix(returns):
    return returns.corr()


def rolling_volatility(returns, window=20):
    return returns.rolling(window=window).std().dropna()


def explain_anomaly(returns, ticker, n=1):
    """
    Returns the n most extreme single-day moves for a ticker, sorted — used to
    trace a rolling-volatility spike back to the specific day(s) that caused it.
    """
    sorted_moves = returns[ticker].sort_values()
    return pd.concat([sorted_moves.head(n), sorted_moves.tail(n)])


if __name__ == "__main__":
    closes = get_clean_closes(TICKERS, START, END)
    returns = calculate_returns(closes)

    print("Correlation matrix:")
    print(build_correlation_matrix(returns))

    print("\n20-day rolling volatility (tail):")
    print(rolling_volatility(returns).tail())

    print("\nSE's most extreme single-day moves (for anomaly tracing):")
    print(explain_anomaly(returns, "SE", n=3))

    # Finding: GRAB-SE correlation (~0.49) >> IHH-BDMS correlation (~0.00),
    # despite both pairs sharing a sector label. The Aug 12, 2025 SE spike
    # (+19.07%) traces to Sea's Q2 2025 earnings (verified against reported
    # revenue beat of ~$300M, despite a narrow EPS miss).

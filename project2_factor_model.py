"""
Project 2: Multi-Factor Quantamental Model (Semiconductors)
Tickers: NVDA, AMD, INTC, QCOM, AVGO, TXN, MU

Builds Value, Quality, and Momentum factors, combines them via z-scoring into
a single ranked score, and runs a look-ahead-bias-free momentum backtest.
"""

import pandas as pd
import yfinance as yf

TICKERS = ["NVDA", "AMD", "INTC", "QCOM", "AVGO", "TXN", "MU"]


def get_fundamentals(tickers):
    """
    Pulls current-snapshot fundamentals (P/E, ROE, P/B) per ticker.
    NOTE: these are CURRENT values, not point-in-time historical — a real
    limitation for backtesting the Value/Quality legs honestly (see README).
    """
    fundamentals = {}
    for ticker in tickers:
        info = yf.Ticker(ticker).info
        fundamentals[ticker] = {
            "pe": info.get("trailingPE"),
            "roe": info.get("returnOnEquity"),
            "pb": info.get("priceToBook"),
        }
    return pd.DataFrame(fundamentals).T


def zscore(series, invert=False):
    """
    Standardizes a column to a z-score so differently-scaled metrics (P/E in
    the 20s-150s vs ROE as a small decimal) can be meaningfully combined.
    invert=True flips the sign for metrics where LOWER is better (e.g. P/E —
    cheap should score high, not low).
    """
    z = (series - series.mean()) / series.std()
    return -z if invert else z


def get_momentum(tickers, start, end):
    """Total price return over [start, end], used as the raw Momentum factor."""
    data = yf.download(tickers, start=start, end=end)
    closes = data["Close"]
    returns = (closes.iloc[-1] - closes.iloc[0]) / closes.iloc[0] * 100
    return returns


def build_combined_score(fundamentals_df, momentum_series):
    df = fundamentals_df.copy()
    df["pe_zscore"] = zscore(df["pe"], invert=True)   # cheap = good
    df["roe_zscore"] = zscore(df["roe"], invert=False)  # high ROE = good
    df["momentum_zscore"] = zscore(momentum_series, invert=False)  # high return = good
    df["combined_score"] = (df["pe_zscore"] + df["roe_zscore"] + df["momentum_zscore"]) / 3
    return df.sort_values("combined_score", ascending=False)


def momentum_backtest(tickers, formation_start, formation_end, test_start, test_end):
    """
    Look-ahead-bias-free momentum test: rank stocks by momentum using ONLY
    formation-period data, then check what actually happened in the
    (non-overlapping) test period.
    """
    data = yf.download(tickers, start=formation_start, end=test_end)
    closes = data["Close"]

    formation = closes[formation_start:formation_end]
    test = closes[test_start:test_end]

    formation_returns = (formation.iloc[-1] - formation.iloc[0]) / formation.iloc[0] * 100
    test_returns = (test.iloc[-1] - test.iloc[0]) / test.iloc[0] * 100

    comparison = pd.DataFrame({
        "formation_momentum": formation_returns,
        "test_period_return": test_returns,
    })
    return comparison.sort_values("formation_momentum", ascending=False)


if __name__ == "__main__":
    fundamentals_df = get_fundamentals(TICKERS)
    momentum = get_momentum(TICKERS, start="2026-01-01", end="2026-09-26")

    ranked = build_combined_score(fundamentals_df, momentum)
    print("Combined factor ranking:")
    print(ranked)

    backtest = momentum_backtest(
        TICKERS,
        formation_start="2026-01-01", formation_end="2026-04-30",
        test_start="2026-05-01", test_end="2026-09-26",
    )
    print("\nMomentum backtest (formation vs. test period):")
    print(backtest)

    # Finding: no consistent momentum persistence in this small universe.
    # INTC's outsized formation-period return (+140%) traces to the U.S.
    # government's 2025 CHIPS Act equity stake and Intel's foundry turnaround
    # — a specific catalyst, not organic momentum (verified via public reporting).

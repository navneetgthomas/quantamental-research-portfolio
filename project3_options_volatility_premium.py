"""
Project 3: Earnings Options Strategy — Implied vs. Realized Move
Tickers: SE, GRAB, CPNG, MELI, UBER, PDD, DASH

Calculates each stock's options-implied earnings-day move (via at-the-money
straddle pricing) and compares it to the average realized earnings-day move
over its last 5 reported quarters, to test for a volatility risk premium.
"""

import pandas as pd
import yfinance as yf

PEERS = ["GRAB", "CPNG", "MELI", "UBER", "PDD", "DASH"]
ALL_TICKERS = PEERS + ["SE"]

# Each ticker's dominant earnings-reporting convention, determined by
# inspecting actual reported timestamps via get_earnings_dates(). This matters:
# a before-open reporter's reaction shows up in THAT day's close; an
# after-close reporter's reaction only shows up in the NEXT day's close.
# Getting this wrong (as an early version of this script did) understates
# the realized move for after-market reporters by roughly 3x.
AFTER_MARKET_TICKERS = {
    "CPNG": True, "DASH": True, "MELI": True,
    "UBER": False, "PDD": False, "GRAB": False,  # GRAB is inconsistent quarter
    "SE": False,                                  # to quarter — flagged in README
}


def get_upcoming_earnings_date(ticker):
    stock = yf.Ticker(ticker)
    earnings = stock.get_earnings_dates(limit=8)
    upcoming = earnings[earnings["Reported EPS"].isna()]
    return upcoming.index[0]


def get_implied_move(ticker):
    """
    Implied earnings-day move via at-the-money straddle: the combined
    bid/ask-midpoint price of the nearest call+put, expressed as a % of the
    current stock price, using the first options expiration after the next
    earnings date (so the straddle fully spans the event).
    """
    stock = yf.Ticker(ticker)
    earnings_date = get_upcoming_earnings_date(ticker)
    earnings_date_str = earnings_date.strftime("%Y-%m-%d")

    expirations = stock.options
    valid_expirations = [e for e in expirations if e > earnings_date_str]
    target_expiration = valid_expirations[0]

    chain = stock.option_chain(target_expiration)
    calls = chain.calls.copy()
    puts = chain.puts.copy()

    current_price = stock.history(period="1d")["Close"].iloc[-1]

    calls["distance"] = (current_price - calls["strike"]).abs()
    puts["distance"] = (current_price - puts["strike"]).abs()
    calls_sorted = calls.sort_values("distance")
    puts_sorted = puts.sort_values("distance")

    call_mid = (calls_sorted.iloc[0]["bid"] + calls_sorted.iloc[0]["ask"]) / 2
    put_mid = (puts_sorted.iloc[0]["bid"] + puts_sorted.iloc[0]["ask"]) / 2
    straddle_price = call_mid + put_mid

    return (straddle_price / current_price) * 100


def get_avg_realized_move(ticker, earnings_dates, is_after_market, start="2023-01-01"):
    """
    Average absolute realized price move on each earnings reaction day, over
    the given list of past earnings dates (as 'YYYY-MM-DD' strings).
    """
    stock = yf.Ticker(ticker)
    history = stock.history(start=start, end="2026-09-26")

    moves = {}
    for date in earnings_dates:
        position = history.index.get_loc(date)
        if is_after_market:
            day_before = history.iloc[position]["Close"]
            day_of = history.iloc[position + 1]["Close"]
        else:
            day_of = history.loc[date, "Close"]
            day_before = history.iloc[position - 1]["Close"]
        moves[date] = (day_of - day_before) / day_before * 100

    return pd.Series(moves).abs().mean()


def get_stock_realized_move(ticker):
    stock = yf.Ticker(ticker)
    earnings = stock.get_earnings_dates(limit=8).dropna()
    dates = earnings.index[:5].strftime("%Y-%m-%d")
    return get_avg_realized_move(ticker, dates, is_after_market=AFTER_MARKET_TICKERS[ticker])


if __name__ == "__main__":
    implied = {t: get_implied_move(t) for t in ALL_TICKERS}
    realized = {t: get_stock_realized_move(t) for t in ALL_TICKERS}

    comparison = pd.DataFrame({
        "implied_move": pd.Series(implied),
        "realized_move": pd.Series(realized),
    })
    comparison["premium"] = comparison["implied_move"] - comparison["realized_move"]

    print(comparison.sort_values("premium", ascending=False))

    # Finding: implied move > realized move for all 7/7 stocks — a consistent
    # volatility risk premium, directionally consistent with "IV crush"
    # around earnings. GRAB's premium is the largest but least reliable, due
    # to inconsistent before/after-market reporting across its last 5 quarters.

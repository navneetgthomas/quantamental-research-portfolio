# Quantamental Research Portfolio

Three self-contained research projects built with Python (pandas, yfinance) to bridge traditional
equity research with systematic, data-driven analysis — built using only free, publicly available
data sources (no Bloomberg/FactSet/Visible Alpha), to demonstrate independent data sourcing and
validation rather than reliance on institutional terminals.

**Author:** Navneet George Thomas — Senior Associate, Equity Research (ASEAN Consumer/Internet/Healthcare),
4+ years experience, CFA Level II.

## Setup

Each notebook is self-contained and runnable (e.g. in Google Colab). To run locally instead:

```
pip install -r requirements.txt
```

Then open any of the three `.ipynb` files and run all cells — each pulls live data via `yfinance`
at run time, so re-running will reflect current prices rather than the figures discussed below.

---

## Project 1 — Multi-Stock Return & Risk Analysis

**Universe:** GRAB (Grab), SE (Sea), 5225.KL (IHH Healthcare), KLBF.JK (Kalbe Farma), BDMS.BK (Bangkok
Dusit Medical Services) — spanning ASEAN Internet and Healthcare sectors.

**What it does:**
- Pulls daily price history across 4 exchanges with mismatched trading calendars; forward-fills
  non-trading days to preserve the full cross-market panel rather than dropping rows.
- Calculates daily returns, a 5-stock correlation matrix, and 20-day rolling volatility.

**Key findings:**
- Sector labels do not guarantee correlation: GRAB–SE (both "Internet") correlate at **0.49**, while
  IHH–BDMS (both "Healthcare," different countries) correlate at essentially **0.00** — a reminder
  that country/currency/regulatory exposure can matter more than sector classification.
- A sharp volatility spike in SE's rolling-vol chart was traced back to a single day
  (**Aug 12, 2025, +19.07%**) and independently verified against Sea's actual Q2 2025 earnings
  release (revenue beat of ~$300M despite an EPS miss) — confirming the anomaly against a real,
  sourced market event rather than leaving it unexplained.

**Notebook:** `project1_market_risk_analysis.ipynb`

---

## Project 2 — Multi-Factor Quantamental Model (Semiconductors)

**Universe:** NVDA, AMD, INTC, QCOM, AVGO, TXN, MU.

**What it does:**
- Builds Value (P/E, sign-corrected), Quality (ROE), and Momentum (trailing price return) factors,
  standardized via z-scores, combined into a single ranked score.
- Runs an honest momentum backtest with a proper formation/test split (Jan–Apr 2026 formation,
  May–Sep 2026 test) to avoid look-ahead bias.

**Key findings:**
- Combined ranking surfaces a real divergence: **QCOM** screens well on Value + Quality alone but
  drops sharply once Momentum is added, due to weak recent price performance — illustrating the
  tension between "fundamentally cheap" and "currently out of favor."
- The momentum backtest shows **no consistent persistence** in this small 7-stock universe — an
  honest null result, not a failure. INTC's extreme formation-period return (+140%) was traced to a
  specific, sourced catalyst (the U.S. government's 2025 CHIPS Act equity stake in Intel and its
  foundry turnaround), not organic price momentum — a useful illustration of why momentum models
  benefit from screening out event-driven outliers.

**Stated limitations:** point-in-time historical fundamentals are not available via free data
sources, so the factor model uses current fundamentals (not what was known at the formation date) —
the momentum leg alone is point-in-time clean and is the basis for the backtest. Small universe size
(7 names) means single-stock events can dominate results.

**Notebook:** `project2_factor_model.ipynb`

---

## Project 3 — Earnings Options Strategy: Implied vs. Realized Move

**Universe:** SE, GRAB, CPNG, MELI, UBER, PDD, DASH (ASEAN/LatAm/global e-commerce, mobility, and
delivery peers).

**What it does:**
- Calculates each stock's **implied earnings-day move** from its options market, using an
  at-the-money straddle (nearest-strike call + put, bid/ask midpoint) on the first expiration after
  the next reported earnings date.
- Calculates each stock's **average realized earnings-day move** across its last 5 reported quarters,
  correctly distinguishing before-market vs. after-market reporters (see note below) so the right
  pair of daily closes is compared.
- Compares the two to test for a volatility risk premium.

**Key finding:** Implied move exceeded realized move for **all 7 of 7 stocks** — a consistent
volatility risk premium across the peer group, directionally consistent with well-documented "IV
crush" behavior around earnings.

| Ticker | Implied Move | Realized Move (avg, last 5Q) | Premium |
|---|---|---|---|
| SE | 17.65% | 14.30% | +3.35 pts |
| CPNG | 11.96% | 6.49% | +5.47 pts |
| DASH | 11.44% | 5.80% | +5.65 pts |
| UBER | 10.56% | 4.84% | +5.71 pts |
| PDD | 11.15% | 4.93% | +6.22 pts |
| GRAB | 14.38% | 1.95% | +12.43 pts* |

*GRAB's realized-move figure is flagged as less reliable: Grab's earnings reporting time is
inconsistent quarter-to-quarter (sometimes before market open, sometimes after close), which the
before/after-market adjustment could not fully correct for across all 5 quarters.

**A genuine methodology catch worth noting:** the first pass at this analysis assumed every company
reports earnings before market open (true for SE, UBER, PDD) — but CPNG, MELI, and DASH actually
report **after** market close. Applying the wrong assumption understated their realized moves by
roughly 3x (e.g., CPNG went from an apparent 1.6% to a corrected 6.5% once the comparison was shifted
to the correct reaction day). This was caught by noticing the results looked implausibly low for
known-volatile names, verified against each stock's actual reported earnings timestamps, and fixed
before being reported as a final result.

**Notebook:** `project3_options_volatility_premium.ipynb`

---

## Tech stack & approach

- **Data:** `yfinance` (prices, fundamentals snapshots, options chains, earnings dates) — entirely
  free and public.
- **Core tools:** pandas (vectorized returns, z-scoring, groupby, multi-index handling), matplotlib.
- **Methodology discipline applied throughout:** verifying suspicious results against independent
  sources before trusting them (e.g., the Project 1 price discrepancy that turned out to be a genuine
  12-month SE price move, not a stock split; the Project 3 reporting-time bug), explicit sign
  conventions for factor construction, look-ahead-bias-free backtest splits, and stated limitations
  rather than overclaiming from small samples.

## Next steps (not yet built)
- Expand Project 2 to point-in-time fundamentals (would require a paid data source) to make the
  full Value+Quality+Momentum backtest fully look-ahead-free, not just the Momentum leg.
- Expand Project 3's peer universe and extend the realized-move lookback beyond 5 quarters per name
  for a larger sample.

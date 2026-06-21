"""
Fox Corp / Roku Event Study — run.py
=====================================
Run this file to reproduce the full analysis end to end:
  python src/run.py

All tunable parameters are pinned at the top.
Script reads top-to-bottom in the same order as the methodology.
"""

# ── CONFIG ────────────────────────────────────────────────────────────────────
TICKERS = ["FOXA", "ROKU"]
MARKET  = "^GSPC"

# Day zero: EDGAR 8-K confirmed pre-market June 15 (FOXA 7:13 AM, ROKU 7:47 AM ET).
EVENT_DATE = "2026-06-15"

# Estimation window: 251 trading days (Jun 2 2025 → Jun 1 2026), ending 9 trading
# days before the event. The pre-event gap prevents the announcement's price effect
# from contaminating our beta and alpha estimates (event-window contamination of the
# estimation window is one of the main ways event studies go wrong).
ESTIMATION_START = "2025-06-02"
ESTIMATION_END   = "2026-06-01"

# Primary event window: [-1, +1] around day 0 = 3 trading days.
# Narrow window chosen because a FOXA-specific 8-K (CEO comp extension)
# was filed June 11, which falls inside a wider window and could confound
# the FOXA result. [-1, +1] isolates the acquisition signal cleanly.
# June 12 (Fri) = day -1, June 15 (Mon) = day 0, June 16 (Tue) = day +1.
# See notebooks/preflight_results.md for the full confound check.
EVENT_START = "2026-06-12"   # day -1: 1 trading day before June 15
EVENT_END   = "2026-06-16"   # day +1: 1 trading day after June 15

# Robustness check window: [-5, +3] (data available through June 18).
# Days +4 and +5 (June 19–20) not yet in cache; window runs June 8–18 = 9 days.
# Interpret FOXA [-5,+3] CAR with caution: June 11 confound falls in this window.
EVENT_START_WIDE = "2026-06-08"
EVENT_END_WIDE   = "2026-06-18"

DATA_PULL_START = "2025-05-01"
DATA_PULL_END   = "2026-06-19"

OUTPUT_PLOT       = "car_plot.png"
OUTPUT_PLOT_WIDE  = "car_plot_wide.png"
# ─────────────────────────────────────────────────────────────────────────────

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data import load_all_returns
from src.model import compute_car
from src.plot import plot_car_paths


def print_result(result, label=""):
    sig = (
        "*** (p<0.01)" if result.p_value < 0.01 else
        "**  (p<0.05)" if result.p_value < 0.05 else
        "*   (p<0.10)" if result.p_value < 0.10 else
        "    (not significant)"
    )
    print(f"\n  ── {result.ticker} {label}──")
    print(f"  alpha={result.alpha:.6f}  beta={result.beta:.4f}  R²={result.estimation_r2:.4f}")
    print(f"  sigma_AR (estimation window) = {result.sigma_ar:.6f}")
    print(f"  Event-window abnormal returns:")
    for date, ar_val in result.ar.items():
        marker = " ◄ day 0" if str(date.date()) == EVENT_DATE else ""
        print(f"    {date.date()}  AR={ar_val*100:+.2f}%{marker}")
    print(f"  CAR  = {result.car*100:+.2f}%")
    print(f"  t    = {result.t_stat:.3f}")
    print(f"  p    = {result.p_value:.4f}  {sig}")


def main():
    print("=" * 65)
    print("FOX CORP / ROKU EVENT STUDY")
    print(f"Announcement date (day 0): {EVENT_DATE}")
    print(f"Estimation window : {ESTIMATION_START} → {ESTIMATION_END}")
    print(f"Primary event window  [-1,+1]: {EVENT_START} → {EVENT_END}")
    print(f"Robustness window [-5,+3]: {EVENT_START_WIDE} → {EVENT_END_WIDE}")
    print("=" * 65)

    # ── Stage 1: Pull returns ──────────────────────────────────────────────
    print("\n[Stage 1] Fetching daily returns via yfinance...")
    all_tickers = TICKERS + [MARKET]
    df = load_all_returns(all_tickers, DATA_PULL_START, DATA_PULL_END)
    print(f"  Shape: {df.shape}  |  {df.index[0].date()} → {df.index[-1].date()}")

    # ── Stage 2: Primary event window [-1, +1] ────────────────────────────
    print("\n[Stage 2] Market model + CAR — primary window [-1, +1]")
    print("  (Narrow window avoids June 11 FOXA CEO comp 8-K confound)")
    primary_results = []
    for ticker in TICKERS:
        r = compute_car(
            ticker=ticker,
            stock_returns=df[ticker],
            market_returns=df[MARKET],
            estimation_start=ESTIMATION_START,
            estimation_end=ESTIMATION_END,
            event_start=EVENT_START,
            event_end=EVENT_END,
        )
        primary_results.append(r)
        print_result(r, label="[primary -1,+1] ")

    # ── Stage 3: Robustness check [-5, +5] ────────────────────────────────
    print("\n[Stage 3] Robustness check — wide window [-5, +3]")
    print("  (FOXA result should be interpreted with caution: June 11 confound inside window)")
    wide_results = []
    for ticker in TICKERS:
        r = compute_car(
            ticker=ticker,
            stock_returns=df[ticker],
            market_returns=df[MARKET],
            estimation_start=ESTIMATION_START,
            estimation_end=ESTIMATION_END,
            event_start=EVENT_START_WIDE,
            event_end=EVENT_END_WIDE,
        )
        wide_results.append(r)
        print_result(r, label="[wide -5,+3] ")

    # ── Stage 4: Plots ─────────────────────────────────────────────────────
    print(f"\n[Stage 4] Generating plots...")
    plot_car_paths(primary_results, event_date=EVENT_DATE, output_path=OUTPUT_PLOT)
    plot_car_paths(wide_results,   event_date=EVENT_DATE, output_path=OUTPUT_PLOT_WIDE)

    # ── Stage 5: Summary table ─────────────────────────────────────────────
    print("\n" + "=" * 65)
    print("SUMMARY")
    print(f"{'Ticker':<8} {'Window':<12} {'CAR':>8} {'t-stat':>8} {'p-value':>9} {'Sig'}")
    print("-" * 65)
    for r in primary_results:
        sig = "***" if r.p_value < 0.01 else "**" if r.p_value < 0.05 else "*" if r.p_value < 0.10 else ""
        print(f"{r.ticker:<8} {'[-1,+1]':<12} {r.car*100:>+7.2f}% {r.t_stat:>8.3f} {r.p_value:>9.4f} {sig}")
    for r in wide_results:
        sig = "***" if r.p_value < 0.01 else "**" if r.p_value < 0.05 else "*" if r.p_value < 0.10 else ""
        note = " (confound⚠)" if r.ticker == "FOXA" else ""
        print(f"{r.ticker:<8} {'[-5,+3]':<12} {r.car*100:>+7.2f}% {r.t_stat:>8.3f} {r.p_value:>9.4f} {sig}{note}")
    print("=" * 65)
    print("\n[Done] Full analysis complete.")

    return primary_results, wide_results


if __name__ == "__main__":
    main()

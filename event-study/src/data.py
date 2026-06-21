# event-study/src/data.py
import yfinance as yf
import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def fetch_returns(ticker: str, start: str, end: str, force_refresh: bool = False) -> pd.Series:
    """
    Download daily adjusted close prices for `ticker` between `start` and `end`
    (YYYY-MM-DD strings). Compute and return daily simple returns (pct_change).

    Caches to data/<ticker>.csv. Use force_refresh=True to re-pull.

    Raises ValueError if fewer than 100 observations returned.
    """
    cache_path = DATA_DIR / f"{ticker.replace('^', '')}.csv"

    if cache_path.exists() and not force_refresh:
        prices = pd.read_csv(cache_path, index_col=0, parse_dates=True).squeeze()
    else:
        raw = yf.download(ticker, start=start, end=end, auto_adjust=True, progress=False)
        if raw.empty:
            raise ValueError(f"yfinance returned no data for {ticker}")
        prices = raw["Close"].squeeze()
        prices.to_csv(cache_path)

    prices = prices.loc[start:end]

    # Guard on returns length (prices - 1), not prices, because pct_change drops one row.
    returns = prices.pct_change().dropna()
    if len(returns) < 100:
        raise ValueError(
            f"Only {len(returns)} return observations for {ticker} between {start} and {end}. "
            "Check ticker and date range."
        )

    returns.name = ticker
    return returns


def load_all_returns(
    tickers: list,
    start: str,
    end: str,
    force_refresh: bool = False,
) -> pd.DataFrame:
    """
    Fetch returns for multiple tickers and align on common trading dates.
    Returns DataFrame with one column per ticker.
    Raises if alignment silently drops more than 5 rows (indicates structural gap).
    """
    series = {t: fetch_returns(t, start, end, force_refresh) for t in tickers}
    pre_align = {t: len(s) for t, s in series.items()}
    df = pd.DataFrame(series).dropna()
    post_align = len(df)

    for ticker, n_before in pre_align.items():
        dropped = n_before - post_align
        if dropped > 5:
            raise ValueError(
                f"Alignment dropped {dropped} rows for {ticker} (had {n_before}, kept {post_align}). "
                "Likely a trading-halt or data gap. Use force_refresh=True to re-pull."
            )

    return df

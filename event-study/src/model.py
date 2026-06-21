# event-study/src/model.py
import numpy as np
import pandas as pd
import statsmodels.api as sm
from dataclasses import dataclass
from scipy import stats


@dataclass
class MarketModelResult:
    ticker: str
    alpha: float
    beta: float
    sigma_ar: float          # residual std dev from estimation window only
    estimation_r2: float
    ar: pd.Series            # abnormal returns across the event window
    car: float               # cumulative abnormal return (sum of ar)
    t_stat: float
    p_value: float
    event_window_returns: pd.Series   # actual returns in event window (for reference)


def fit_market_model(
    stock_returns: pd.Series,
    market_returns: pd.Series,
    estimation_start: str,
    estimation_end: str,
) -> tuple:
    """
    OLS regression: R_it = alpha + beta * R_mt + epsilon
    Fit ONLY on estimation window dates.

    Returns (alpha_hat, beta_hat, sigma_ar, r_squared).

    sigma_ar = std dev of estimation-window residuals with ddof=2
    (we estimated 2 parameters: intercept and slope).
    This is the key input to the significance test.
    """
    est_stock = stock_returns.loc[estimation_start:estimation_end]
    est_mkt = market_returns.loc[estimation_start:estimation_end]

    aligned = pd.concat([est_stock, est_mkt], axis=1).dropna()
    Y = aligned.iloc[:, 0]
    X = sm.add_constant(aligned.iloc[:, 1])

    model = sm.OLS(Y, X).fit()
    alpha_hat = float(model.params["const"])
    beta_hat = float(model.params[est_mkt.name])

    # Use statsmodels' own residuals rather than recomputing manually.
    sigma_ar = float(np.sqrt(model.mse_resid))  # sqrt(SSR / (N-2)), identical to resid.std(ddof=2)

    return alpha_hat, beta_hat, sigma_ar, float(model.rsquared), len(aligned)


def compute_car(
    ticker: str,
    stock_returns: pd.Series,
    market_returns: pd.Series,
    estimation_start: str,
    estimation_end: str,
    event_start: str,
    event_end: str,
) -> MarketModelResult:
    """
    Full event-study pipeline for one ticker:

    1. Fit market model on estimation window → get alpha, beta, sigma_ar.
    2. For each day t in the event window:
         AR_t = R_it - (alpha + beta * R_mt)
       This is actual return minus what the model predicted given market movement.
       The residual is the part potentially caused by the announcement.
    3. CAR = sum of all AR_t over the event window.
    4. t-stat = CAR / (sqrt(L) * sigma_ar)
       where L = number of trading days in the event window.
       Null hypothesis: CAR = 0 (event had no price impact beyond market co-movement).
       Rejecting null means the announcement moved the price in a statistically
       significant way that cannot be explained by overall market movement.
    """
    alpha, beta, sigma_ar, r2, n_est = fit_market_model(
        stock_returns, market_returns, estimation_start, estimation_end
    )

    ev_stock = stock_returns.loc[event_start:event_end]
    ev_mkt = market_returns.loc[event_start:event_end]
    aligned_ev = pd.concat([ev_stock, ev_mkt], axis=1).dropna()

    if len(aligned_ev) == 0:
        raise ValueError(
            f"Event window [{event_start}, {event_end}] contains no trading days for {ticker}."
        )

    actual = aligned_ev.iloc[:, 0]
    predicted = alpha + beta * aligned_ev.iloc[:, 1]
    ar = actual - predicted
    ar.name = f"AR_{ticker}"

    car = float(ar.sum())
    L = len(ar)

    # Patell-style test: assumes AR_t ~ iid N(0, sigma_ar^2)
    # sigma_ar from estimation window keeps the event window clean.
    # df = n_est - 2: uncertainty comes from estimating alpha and beta over the
    # estimation window (2 params), not from the event-window length L.
    # Using df=L-1 would give a fat-tailed t and badly inflated p-values.
    t_stat = car / (np.sqrt(L) * sigma_ar)
    p_value = float(2 * (1 - stats.t.cdf(abs(t_stat), df=n_est - 2)))

    return MarketModelResult(
        ticker=ticker,
        alpha=alpha,
        beta=beta,
        sigma_ar=sigma_ar,
        estimation_r2=r2,
        ar=ar,
        car=car,
        t_stat=t_stat,
        p_value=p_value,
        event_window_returns=actual,
    )

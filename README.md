# Fox / Roku Acquisition: Measuring the Stock-Price Impact

On June 15, 2026, Fox Corporation announced it was buying Roku for roughly $22 billion in cash and stock. That announcement is interesting for two reasons that most event study writeups miss: ROKU's reaction is the expected story (acquisition premium, target pops), but FOXA's reaction is the more revealing one. Acquirers don't usually drop 26% in three days. When they do, the market is saying something specific about the deal terms.

This event study measures both sides using Cumulative Abnormal Return (CAR) methodology — the same framework used in securities litigation to isolate price effects attributable to a specific disclosure.

---

## Pre-flight: getting the inputs right before touching the model

Two things have to be nailed before building anything: the exact announcement timing (which sets day zero for the price analysis) and whether anything else was happening with either company that week that could contaminate the results.

### Disclosure timing

Both 8-Ks were pulled directly from SEC EDGAR:

- **FOXA 8-K accepted: 7:13 AM ET, June 15, 2026** — pre-market
- **ROKU 8-K accepted: 7:47 AM ET, June 15, 2026** — pre-market

Both hit before the 9:30 AM open. Day zero is June 15 for both tickers.

### Confound check

Scanned June 8–22 for anything else material to either ticker:

- **FOXA:** One thing turned up — a separate 8-K filed June 11 disclosing an employment extension and comp increase for CEO Lachlan Murdoch. Falls within the wide [-5,+3] robustness window but outside the primary [-1,+1] window. This is why [-1,+1] is treated as primary: it avoids absorbing any price reaction to that filing.
- **ROKU:** Nothing. No earnings, no unrelated 8-Ks, no guidance updates in that window.

The FOXA confound doesn't kill the analysis — it's a reason to anchor conclusions to the tight window and treat the wide one as a robustness check.

---

## Method

Estimation window: 251 trading days ending June 1, 2026 — 10 days before the announcement. The gap prevents the event from leaking into the baseline. A single-factor OLS market model (`R_it = alpha + beta * R_mt`) is fit separately for each ticker using the S&P 500 as the market proxy. For each day in the event window, the abnormal return is actual return minus what the model predicted: `AR_it = R_it - (alpha_hat + beta_hat * R_mt)`. The CAR is the sum of daily ARs across the window. Significance is assessed with a Patell-style t-test using the estimation-window residual sigma.

---

## Market model parameters

| Ticker | Alpha | Beta | R² | Sigma (AR) |
|--------|-------|------|----|------------|
| FOXA | 0.000505 | 0.457 | 0.037 | 1.75% |
| ROKU | 0.000553 | 2.080 | 0.310 | 2.33% |

ROKU's beta of 2.08 reflects a high-volatility growth stock — it moves roughly twice the market on a normal day. FOXA's 0.46 is a mature media company with muted market sensitivity. FOXA's low R² (3.7%) means most of its daily return variance is idiosyncratic, which makes the -25.7% CAR harder to achieve, not easier — the test has to clear a loose benchmark.

---

## Results

![CAR Plot](car_plot.png)

*Primary event window [-1,+1] (June 12, 15, 16): cumulative abnormal returns for both tickers.*

![Wide window](car_plot_wide.png)

*Robustness window [-5,+3] (June 8–18). The FOXA confound from the June 11 CEO filing is visible here.*

| Ticker | Window | CAR | t-stat | p-value | |
|--------|--------|-----|--------|---------|---|
| FOXA | [-1,+1] primary | -25.72% | -8.480 | <0.001 | *** |
| ROKU | [-1,+1] primary | +12.60% | 3.122 | 0.002 | *** |
| FOXA | [-5,+3] robustness | -24.12% | -4.591 | <0.001 | *** |
| ROKU | [-5,+3] robustness | +10.21% | 1.461 | 0.145 | n.s. |

---

### ROKU (target)

| Day | Date | ROKU return | Predicted | AR |
|-----|------|-------------|-----------|-----|
| -1 | Jun 12 | +20.08% | +1.10% | **+18.98%** |
| 0 | Jun 15 | -1.92% | +3.49% | -5.41% |
| +1 | Jun 16 | -2.09% | -1.13% | -0.97% |

The CAR is almost entirely the June 12 jump. ROKU rose 20% on Friday — the day before the official Monday announcement — while the market was up about 0.5%. That's deal information circulating before the EDGAR filing. On the actual announcement day, ROKU had a -5.4% abnormal return: sell-the-news, or concern about execution. The net +12.6% captures the full acquisition premium incorporated into the stock, but the mechanism is pre-announcement leakage, not a clean day-0 reaction.

### FOXA (acquirer)

| Day | Date | FOXA return | Predicted | AR |
|-----|------|-------------|-----------|-----|
| -1 | Jun 12 | -3.59% | +0.28% | -3.87% |
| 0 | Jun 15 | -16.84% | +0.81% | **-17.65%** |
| +1 | Jun 16 | -4.42% | -0.21% | -4.21% |

Unlike ROKU, the loss is concentrated on day 0 and spreads across all three days — consistent with the market processing a large, unexpected negative signal rather than pre-announcement leakage. The wide-window result (-24.12%, p<0.001) corroborates this. The day -1 negative AR is likely the June 11 CEO comp filing bleeding into June 12 trading. A -25.7% acquirer CAR is an extreme outcome; the M&A literature typically finds acquirer CARs in the -2% to -5% range even in overpriced deals.

---

## So what?

The ~38 percentage point spread between FOXA and ROKU tells a coherent story.

ROKU's +13% is the expected target premium — what it takes to get shareholders to tender. That part is textbook.

FOXA's -26% is the market saying Fox overpaid. That kind of acquirer CAR doesn't happen in deals the market views as reasonably priced. It implies the market thought the $22B price was materially above what Roku is worth to Fox strategically, or that the deal rationale wasn't clear enough to justify the size of the bet.

From a litigation standpoint, this matters for a few reasons. First, magnitude: -26% on FOXA shares translates directly to a dollar-denominated loss figure for shareholders who held through the announcement, which is the starting point for any damages calculation in an M&A fairness case. Second, the result holds across both window specifications (p<0.001 either way), which matters for expert testimony — a result that depends on a single window choice is easy to attack. Third, ROKU's pre-announcement +19% on June 12 is worth examining independently: that kind of price movement the day before an official filing is consistent with selective disclosure or insider trading, and it means the deal's price impact can't be cleanly isolated to a single trading day.

---

## Methodology choices

| Parameter | Choice | Why |
|-----------|--------|-----|
| Estimation window | 251 trading days | One full trading year; standard in litigation practice |
| Pre-event gap | 9 trading days | Keeps event-period returns out of the baseline estimate |
| Market model | Single-factor OLS vs. S&P 500 | More defensible in testimony than Fama-French; FF adds marginal explanatory power for large-caps |
| Primary event window | [-1,+1] | Captures the announcement reaction while avoiding the FOXA confound |
| Robustness window | [-5,+3] | Tests concentration of effects; surfaces the FOXA confound for disclosure |
| Significance test | Patell-style | Uses estimation-window sigma, appropriate when event-window variance may differ |

---

## Replication

```bash
pip install -r requirements.txt
python src/run.py
```

All parameters (tickers, event date, window lengths) are pinned at the top of `src/run.py`.

**Data source:** Yahoo Finance via `yfinance`, cached in `data/`.

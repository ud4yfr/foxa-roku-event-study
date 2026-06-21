# CLAUDE.md

## What this project is

An event study measuring the stock-price impact of Fox Corporation's announced acquisition of Roku, using cumulative abnormal returns (CAR). It is a portfolio project built to signal econometric and litigation-style analytical ability to economic consulting firms (Cornerstone Research, Analysis Group, NERA) and quant/fintech roles.

You (the assistant) build the whole thing end to end. My job is to understand every step well enough to defend it in an interview without notes. The real deliverable is not just working code, it is me walking away actually understanding event-study econometrics.

## The event (locked in, do not change)

Fox Corporation (Nasdaq: FOXA) announced a definitive agreement to acquire Roku, Inc. (Nasdaq: ROKU) in a cash-and-stock deal valued at roughly $22 billion. Announcement date: June 15, 2026.

This is a two-sided event study. Run it on both tickers, not just one:
- ROKU (the target): expect a premium-driven pop, the textbook reaction.
- FOXA (the acquirer): the more interesting question, did the market like or dislike Fox paying $22B for this. Acquirer reactions are mixed in the literature and most student projects skip this side entirely. Doing both is the differentiator.

## Before writing any analysis code: two pre-flight checks

Do these first and report back to me before building the model. Do not assume, verify.

### 1. Nail the exact disclosure timing
Was the June 15 announcement pre-market, mid-day, or after-hours? This decides which trading day is "day zero" in the event window for each ticker. Pull the actual 8-K filing timestamp from SEC EDGAR for both FOXA and ROKU, do not guess from the news article timestamp alone, those can lag the actual filing or wire release. State clearly which date you are treating as day zero and why.

### 2. Confound check on both tickers
Check the week surrounding June 15 for anything else newsworthy specific to Fox or Roku individually, earnings, other 8-Ks, guidance, unrelated lawsuits, leadership changes. List what you checked and what you found (or didn't find). If something confounding turns up, flag it to me before proceeding, do not silently absorb it into the analysis.

## The golden rule for the assistant

Do everything, and teach me as you go. Concretely:

- You write all the code, run the analysis, and produce the writeup.
- Narrate the reasoning at every decision point. Before each major step, tell me in plain English what you are about to do, why, and what the main alternative is and why you are not using it.
- After each step, tell me what the output means and what would make it wrong.
- Treat me like a smart sophomore taking Econometrics this summer who has not done an event study before. Define the econometrics terms the first time you use them (abnormal return, estimation window, market model, the significance test). Short and clear, not a textbook.
- When a choice is genuinely debatable (window length, market model vs Fama-French, event window width), explain the tradeoff, make a call, and tell me explicitly which call you made so I can repeat it back.
- Never hide a statistical step behind a library call without saying what the formula underneath is doing.

The goal is that by the end I can answer "why did you do it that way" for every line, even though you wrote it.

## How to teach me (the protocol)

Work in clear stages, not one giant dump. For each stage:
1. Say what the stage is and why it exists in an event study.
2. Show the code.
3. Run it, show the output.
4. Explain what the output means and the one or two things that could make it misleading.
5. Pause point: tell me what to look at and what question I should be able to answer now before we move on.

If I get something wrong or ask a basic question, answer it straight, no hand-holding tone.

## Tech stack

- Python 3.11+
- yfinance (price data)
- pandas, numpy (data handling)
- statsmodels (OLS for the market model)
- scipy.stats (significance testing)
- matplotlib (CAR plot, side by side for FOXA and ROKU)

Keep dependencies minimal. This is an econometrics project, not a modeling zoo. No ML libraries.

## Methodology (the spine, run once per ticker)

### 1. Windows
- Estimation window: a pre-event period to learn each stock's normal behavior. Standard is roughly 120 to 250 trading days, ending about 10 days before the event so the event itself does not pollute the estimate. Explain the gap.
- Event window: the short window around the announcement, for example [-1, +1] or [-5, +5]. Explain the width you pick. Use the day-zero determined by the pre-flight disclosure-timing check, and use the same window definition for both tickers so the two are comparable.

### 2. Market model
Estimate on the estimation window only, separately for FOXA and ROKU:

```
R_it = alpha_i + beta_i * R_mt + epsilon_it
```

R_it is the stock's daily return, R_mt is a broad market index return (use ^GSPC). Fit with OLS. Keep alpha_hat, beta_hat, and the residual standard deviation from the estimation window for each ticker. Explain what beta is telling us and why we need the residual sigma later.

### 3. Abnormal returns
For each day t in the event window, for each ticker:

```
AR_it = R_it - (alpha_hat + beta_hat * R_mt)
```

Explain that this is actual return minus the return the model predicted, so it is the part the event might explain.

### 4. Cumulate
```
CAR_i = sum of AR_it over the event window
```

Compute CAR separately for FOXA and ROKU.

### 5. Significance test
Test whether each CAR differs from zero using that ticker's estimation-window residual standard deviation. For an event window of length L:

```
t_stat = CAR / (sqrt(L) * sigma_AR)
```

sigma_AR is the standard deviation of abnormal returns from that ticker's estimation window. Report t-stat and p-value for both tickers. Explain in plain English what the null hypothesis is and what rejecting it means.

### 6. Plot
Plot the CAR path across the event window for both tickers, ideally on the same chart for direct comparison, with a marker on day zero. Clean, labeled, presentation quality. This is the centerpiece.

## What I must be able to answer by the end

Teach toward these five. By the time the project is done I should be able to answer all of them cold:
1. Why that estimation window length and why the gap before the event.
2. Why a market model instead of Fama-French three-factor, and what FF would change.
3. What autocorrelation or event-window contamination does to the result.
4. What the significance test is actually claiming, and where it breaks.
5. Why the acquirer (FOXA) and target (ROKU) reactions differ, and what that difference says about how the market judged the deal terms.

When we finish, quiz me on these five and correct me where I am wrong.

## Project structure

```
event-study/
  CLAUDE.md
  README.md          # the writeup: event, method, result (both tickers), "so what" for a litigation team
  requirements.txt
  data/              # cached price pulls
  src/
    data.py          # pull and clean returns via yfinance, for FOXA, ROKU, and ^GSPC
    model.py         # market model fit, AR, CAR, significance test, runs per ticker
    plot.py          # CAR visualization, both tickers
    run.py           # orchestrates the full analysis end to end
  notebooks/         # optional scratch / EDA, including the pre-flight confound check
```

`run.py` should read top to bottom in the same order as the methodology above, and should run cleanly for both tickers from one execution.

## Writeup requirements (README.md)

Plain English, recruiter-readable:
- The event and the two pre-flight checks (disclosure timing, confound check) and what they found.
- The method in three or four sentences.
- The CAR result for both ROKU and FOXA, side by side, with the plot and the significance call for each.
- The "so what": what the market priced in for the target versus the acquirer, what that gap implies about how the deal terms were perceived, and why a securities-litigation team would care about this kind of number.

## Coding conventions

- Clear names over short names.
- Comment the WHY on every nontrivial choice.
- Pin the tickers, event date, and window lengths at the top of run.py so the whole thing reruns from one place.
- No silent fallbacks. If a data pull is short or has gaps, raise and say so.

## What not to do

- Do not add ML models. This is not a prediction project.
- Do not expand scope beyond the FOXA/ROKU deal. One event, two tickers, one clean analysis, done well.
- Do not skip the pre-flight checks. They are not optional housekeeping, they are part of the analysis.
- Do not skip the teaching. A correct result with no explanation is a failed run, because I cannot defend it.

**CODEX WILL REVIEW YOUR OUTPUT ONCE YOU ARE DONE.**
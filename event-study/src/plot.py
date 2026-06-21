# event-study/src/plot.py
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import numpy as np
from src.model import MarketModelResult


def plot_car_paths(
    results: list,
    event_date: str,
    output_path: str = "car_plot.png",
) -> None:
    """
    Plot cumulative abnormal return paths for each ticker across the event window.

    X-axis: event-time (trading days relative to day 0).
    Y-axis: cumulative AR in %.
    Vertical dashed line marks day 0 (announcement date).

    results: list of MarketModelResult objects (one per ticker)
    event_date: YYYY-MM-DD string for the announcement date (used to find day 0 index)
    output_path: where to save the PNG
    """
    fig, ax = plt.subplots(figsize=(11, 6))

    colors = {"ROKU": "#E63946", "FOXA": "#1D3557"}
    markers = {"ROKU": "o", "FOXA": "s"}

    for result in results:
        ar = result.ar
        dates = pd.to_datetime(ar.index)

        # Find index of day 0 (first trading date on or after event_date).
        # Raises if event_date falls after the entire event window.
        event_dt = pd.Timestamp(event_date)
        future_dates = dates[dates >= event_dt]
        if len(future_dates) == 0:
            raise ValueError(f"Event date {event_date} is after all event-window dates for {result.ticker}")
        day0_date = future_dates[0]
        if day0_date != event_dt:
            import warnings
            warnings.warn(f"{result.ticker}: {event_date} is not a trading day; using {day0_date.date()} as day 0")
        day0_idx = dates.get_loc(day0_date)

        # Build relative event-time x-axis: day 0 maps to x=0.
        event_time = list(range(-day0_idx, len(dates) - day0_idx))

        cumulative_ar = ar.cumsum().values * 100  # convert to percentage

        sig_label = ""
        if result.p_value < 0.01:
            sig_label = "***"
        elif result.p_value < 0.05:
            sig_label = "**"
        elif result.p_value < 0.10:
            sig_label = "*"

        label = (
            f"{result.ticker}  "
            f"CAR={result.car*100:+.1f}%{sig_label}  "
            f"(t={result.t_stat:.2f}, p={result.p_value:.3f})"
        )

        ax.plot(
            event_time,
            cumulative_ar,
            label=label,
            color=colors.get(result.ticker, "gray"),
            marker=markers.get(result.ticker, "o"),
            linewidth=2.0,
            markersize=6,
        )

    ax.axvline(x=0, color="black", linestyle="--", linewidth=1.2, label=f"Day 0: {event_date}")
    ax.axhline(y=0, color="gray", linestyle="-", linewidth=0.6, alpha=0.4)

    ax.yaxis.set_major_formatter(mtick.PercentFormatter())
    ax.set_xlabel("Event Time (trading days relative to announcement)", fontsize=12)
    ax.set_ylabel("Cumulative Abnormal Return", fontsize=12)
    ax.set_title(
        "Cumulative Abnormal Returns: Fox Corp Acquisition of Roku\n"
        f"Event Date: {event_date}  |  Significance: *** p<0.01  ** p<0.05  * p<0.10",
        fontsize=13,
        fontweight="bold",
    )
    ax.legend(fontsize=11, loc="lower left")
    ax.grid(True, alpha=0.25)

    plt.tight_layout()
    plt.savefig(output_path, dpi=150, bbox_inches="tight")
    print(f"Plot saved → {output_path}")
    plt.close()

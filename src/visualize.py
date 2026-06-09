"""
visualize.py
All matplotlib/seaborn chart functions. Each saves a PNG to outputs/.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]
PALETTE = {
    "Extreme Fear": "#d62728",
    "Fear": "#ff7f0e",
    "Neutral": "#9467bd",
    "Greed": "#2ca02c",
    "Extreme Greed": "#1f77b4",
}
sns.set_theme(style="whitegrid", font_scale=1.1)


def _save(fig, name: str):
    path = OUTPUT_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved → {path}")


def plot_pnl_by_sentiment(pnl_df: pd.DataFrame):
    """Bar chart: mean & median PnL per sentiment."""
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = [PALETTE.get(s, "gray") for s in pnl_df["sentiment"]]

    # Mean PnL
    ax = axes[0]
    bars = ax.bar(pnl_df["sentiment"], pnl_df["mean_pnl"], color=colors, edgecolor="white")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("Mean Closed PnL by Sentiment")
    ax.set_xlabel("Market Sentiment")
    ax.set_ylabel("Mean Closed PnL (USD)")
    ax.tick_params(axis="x", rotation=20)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))

    # Win rate
    ax2 = axes[1]
    ax2.bar(pnl_df["sentiment"], pnl_df["win_rate"] * 100, color=colors, edgecolor="white")
    ax2.axhline(50, color="black", linewidth=0.8, linestyle="--", label="50% baseline")
    ax2.set_title("Win Rate (%) by Sentiment")
    ax2.set_xlabel("Market Sentiment")
    ax2.set_ylabel("Win Rate (%)")
    ax2.tick_params(axis="x", rotation=20)
    ax2.legend()

    fig.suptitle("Trader Performance vs Market Sentiment", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save(fig, "01_pnl_by_sentiment.png")


def plot_volume_by_sentiment(vol_df: pd.DataFrame):
    """Stacked bar: trade count and total volume per sentiment."""
    fig, ax = plt.subplots(figsize=(10, 5))
    colors = [PALETTE.get(s, "gray") for s in vol_df["sentiment"]]
    bars = ax.bar(vol_df["sentiment"], vol_df["total_volume"] / 1e6, color=colors, edgecolor="white")
    ax.set_title("Total Trading Volume by Market Sentiment")
    ax.set_xlabel("Market Sentiment")
    ax.set_ylabel("Volume (Millions USD)")
    ax.tick_params(axis="x", rotation=20)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:.0f}M"))
    for bar, count in zip(bars, vol_df["trade_count"]):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                f"{count:,}", ha="center", va="bottom", fontsize=9)
    plt.tight_layout()
    _save(fig, "02_volume_by_sentiment.png")


def plot_daily_pnl(daily_df: pd.DataFrame):
    """Line chart: rolling 7-day total PnL over time, coloured by sentiment."""
    df = daily_df.copy()
    df["date"] = pd.to_datetime(df["date"])
    df = df.set_index("date").sort_index()
    df["rolling_pnl"] = df["daily_pnl"].rolling(7).sum()

    fig, ax = plt.subplots(figsize=(14, 5))
    ax.plot(df.index, df["rolling_pnl"], color="steelblue", linewidth=1.2, label="7-day rolling PnL")
    ax.axhline(0, color="black", linewidth=0.8, linestyle="--")
    ax.set_title("7-Day Rolling Total PnL Over Time (All Traders)")
    ax.set_ylabel("PnL (USD)")
    ax.set_xlabel("Date")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    ax.legend()
    plt.tight_layout()
    _save(fig, "03_daily_rolling_pnl.png")


def plot_sentiment_distribution(fg_df: pd.DataFrame):
    """Pie chart of how many days each sentiment appeared."""
    counts = fg_df["sentiment"].value_counts().reindex(SENTIMENT_ORDER).dropna()
    colors = [PALETTE[s] for s in counts.index]
    fig, ax = plt.subplots(figsize=(7, 7))
    wedges, texts, autotexts = ax.pie(
        counts, labels=counts.index, autopct="%1.1f%%",
        colors=colors, startangle=140, pctdistance=0.82,
    )
    ax.set_title("Market Sentiment Distribution (2024 Overlap Period)", fontsize=13)
    plt.tight_layout()
    _save(fig, "04_sentiment_distribution.png")


def plot_heatmap_top_traders(pivot_df: pd.DataFrame):
    """Heatmap: top-10 traders × sentiment PnL."""
    fig, ax = plt.subplots(figsize=(12, 7))
    data = pivot_df.drop(columns=["total"], errors="ignore")
    # Normalise each trader row to highlight relative performance
    normed = data.div(data.abs().max(axis=1) + 1e-9, axis=0)
    sns.heatmap(
        normed, annot=data.map(lambda x: f"${x/1000:.1f}k"),
        fmt="", cmap="RdYlGn", center=0, ax=ax,
        linewidths=0.5, cbar_kws={"label": "Relative PnL"},
    )
    ax.set_title("Top-10 Traders: PnL by Market Sentiment", fontsize=13)
    ax.set_xlabel("Sentiment")
    ax.set_ylabel("Trader Address (truncated)")
    # Truncate long addresses
    ax.set_yticklabels([lbl.get_text()[:10] + "…" for lbl in ax.get_yticklabels()], rotation=0)
    plt.tight_layout()
    _save(fig, "05_top_traders_heatmap.png")


def plot_scatter_fg_vs_pnl(daily_df: pd.DataFrame):
    """Scatter: daily Fear/Greed value vs daily total PnL."""
    df = daily_df.dropna(subset=["fg_value", "daily_pnl"]).copy()
    # Cap extreme PnL for visibility
    p1, p99 = df["daily_pnl"].quantile(0.01), df["daily_pnl"].quantile(0.99)
    df = df[(df["daily_pnl"] >= p1) & (df["daily_pnl"] <= p99)]

    fig, ax = plt.subplots(figsize=(9, 6))
    colors = [PALETTE.get(s, "gray") for s in df["sentiment"]]
    ax.scatter(df["fg_value"], df["daily_pnl"], c=colors, alpha=0.6, s=30, edgecolors="none")

    # Regression line
    m, b = np.polyfit(df["fg_value"], df["daily_pnl"], 1)
    x_line = np.linspace(df["fg_value"].min(), df["fg_value"].max(), 100)
    ax.plot(x_line, m * x_line + b, "k--", linewidth=1.2, label=f"Trend (slope={m:+.1f})")

    # Legend patches
    from matplotlib.patches import Patch
    handles = [Patch(color=PALETTE[s], label=s) for s in SENTIMENT_ORDER if s in PALETTE]
    handles.append(plt.Line2D([0], [0], color="k", linestyle="--", label=f"Trend (slope={m:+.1f})"))
    ax.legend(handles=handles, fontsize=9)
    ax.set_title("Fear/Greed Index vs Daily Total PnL")
    ax.set_xlabel("Fear & Greed Value (0=Extreme Fear, 100=Extreme Greed)")
    ax.set_ylabel("Daily Total PnL (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.tight_layout()
    _save(fig, "06_scatter_fg_vs_pnl.png")


def plot_liquidations(liq_df: pd.DataFrame):
    """Bar: liquidation count per sentiment."""
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = [PALETTE.get(s, "gray") for s in liq_df["sentiment"]]
    ax.bar(liq_df["sentiment"], liq_df["liquidations"], color=colors, edgecolor="white")
    ax.set_title("Liquidation Events by Market Sentiment")
    ax.set_xlabel("Market Sentiment")
    ax.set_ylabel("Number of Liquidations")
    ax.tick_params(axis="x", rotation=20)
    plt.tight_layout()
    _save(fig, "07_liquidations_by_sentiment.png")

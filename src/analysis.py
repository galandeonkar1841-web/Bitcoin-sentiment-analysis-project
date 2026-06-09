"""
analysis.py
Core analytical functions for the sentiment-vs-performance study.
"""

import pandas as pd
import numpy as np
from scipy import stats


SENTIMENT_ORDER = ["Extreme Fear", "Fear", "Neutral", "Greed", "Extreme Greed"]


def pnl_by_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate closed PnL metrics grouped by market sentiment."""
    grp = (
        df[df["closed_pnl"] != 0]  # only closed trades with PnL
        .groupby("sentiment")["closed_pnl"]
        .agg(
            trade_count="count",
            total_pnl="sum",
            mean_pnl="mean",
            median_pnl="median",
            win_rate=lambda x: (x > 0).mean(),
            std_pnl="std",
        )
        .reindex(SENTIMENT_ORDER)
        .reset_index()
    )
    return grp


def win_rate_by_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Win-rate and avg gain/loss per sentiment class."""
    closed = df[df["closed_pnl"] != 0].copy()
    closed["is_win"] = closed["closed_pnl"] > 0

    result = (
        closed.groupby("sentiment")
        .apply(lambda g: pd.Series({
            "trades": len(g),
            "wins": g["is_win"].sum(),
            "losses": (~g["is_win"]).sum(),
            "win_rate": g["is_win"].mean(),
            "avg_win": g.loc[g["is_win"], "closed_pnl"].mean(),
            "avg_loss": g.loc[~g["is_win"], "closed_pnl"].mean(),
            "profit_factor": (g.loc[g["is_win"], "closed_pnl"].sum() /
                              abs(g.loc[~g["is_win"], "closed_pnl"].sum()) + 1e-9),
        }), include_groups=False)
        .reindex(SENTIMENT_ORDER)
        .reset_index()
    )
    return result


def top_traders_by_sentiment(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Identify top traders and show how their PnL varies across sentiments."""
    top_accounts = (
        df.groupby("account")["closed_pnl"].sum()
        .nlargest(top_n)
        .index.tolist()
    )
    subset = df[df["account"].isin(top_accounts)]
    pivot = (
        subset.groupby(["account", "sentiment"])["closed_pnl"]
        .sum()
        .unstack("sentiment")
        .reindex(columns=SENTIMENT_ORDER)
        .fillna(0)
    )
    pivot["total"] = pivot.sum(axis=1)
    pivot = pivot.sort_values("total", ascending=False)
    return pivot


def volume_by_sentiment(df: pd.DataFrame) -> pd.DataFrame:
    """Trading volume (USD) breakdown per sentiment."""
    return (
        df.groupby("sentiment")["size_usd"]
        .agg(total_volume="sum", avg_trade_size="mean", trade_count="count")
        .reindex(SENTIMENT_ORDER)
        .reset_index()
    )


def daily_sentiment_pnl(df: pd.DataFrame) -> pd.DataFrame:
    """Daily aggregated PnL vs sentiment value for time-series plots."""
    return (
        df.groupby(["date", "fg_value", "sentiment"])["closed_pnl"]
        .agg(daily_pnl="sum", trade_count="count")
        .reset_index()
        .sort_values("date")
    )


def correlation_sentiment_pnl(df: pd.DataFrame) -> dict:
    """Pearson and Spearman correlation between fg_value and closed_pnl."""
    clean = df[["fg_value", "closed_pnl"]].dropna()
    pearson_r, pearson_p = stats.pearsonr(clean["fg_value"], clean["closed_pnl"])
    spearman_r, spearman_p = stats.spearmanr(clean["fg_value"], clean["closed_pnl"])
    return {
        "pearson_r": pearson_r, "pearson_p": pearson_p,
        "spearman_r": spearman_r, "spearman_p": spearman_p,
    }


def liquidation_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Count liquidation events per sentiment."""
    liq = df[df["direction"].str.contains("Liquidat", na=False)]
    return (
        liq.groupby("sentiment").size()
        .reindex(SENTIMENT_ORDER)
        .fillna(0)
        .reset_index(name="liquidations")
    )

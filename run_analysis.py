"""
run_analysis.py  — entry point
Run with:  python run_analysis.py
"""

import sys
from pathlib import Path

# Add src/ to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from data_loader import load_merged, load_fear_greed
from analysis import (
    pnl_by_sentiment,
    win_rate_by_sentiment,
    top_traders_by_sentiment,
    volume_by_sentiment,
    daily_sentiment_pnl,
    correlation_sentiment_pnl,
    liquidation_analysis,
)
from visualize import (
    plot_pnl_by_sentiment,
    plot_volume_by_sentiment,
    plot_daily_pnl,
    plot_sentiment_distribution,
    plot_heatmap_top_traders,
    plot_scatter_fg_vs_pnl,
    plot_liquidations,
)
from report import print_insights


def main():
    print("Loading data …")
    df = load_merged()
    fg = load_fear_greed()
    print(f"  Trades loaded   : {len(df):,}")
    print(f"  Sentiment days  : {len(fg):,}")

    print("\nRunning analysis …")
    pnl_df   = pnl_by_sentiment(df)
    wr_df    = win_rate_by_sentiment(df)
    vol_df   = volume_by_sentiment(df)
    daily_df = daily_sentiment_pnl(df)
    corr     = correlation_sentiment_pnl(df)
    liq_df   = liquidation_analysis(df)
    top_df   = top_traders_by_sentiment(df, top_n=10)

    print("\nGenerating charts …")
    plot_pnl_by_sentiment(pnl_df)
    plot_volume_by_sentiment(vol_df)
    plot_daily_pnl(daily_df)
    plot_sentiment_distribution(fg)
    plot_heatmap_top_traders(top_df)
    plot_scatter_fg_vs_pnl(daily_df)
    plot_liquidations(liq_df)

    print("\nPrinting insights report …")
    print_insights(pnl_df, wr_df, vol_df, corr, liq_df)

    print("\n✅ Done! Check the outputs/ folder for charts and the report.")


if __name__ == "__main__":
    main()

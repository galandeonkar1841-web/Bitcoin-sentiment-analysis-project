"""
report.py
Prints a structured insights report to stdout (and optionally saves to outputs/).
"""

import pandas as pd
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "outputs"


def print_insights(pnl_df, wr_df, vol_df, corr: dict, liq_df):
    lines = []
    sep = "=" * 65

    lines.append(sep)
    lines.append("  BITCOIN SENTIMENT vs TRADER PERFORMANCE — KEY INSIGHTS")
    lines.append(sep)

    lines.append("\n📊 1. PnL BY SENTIMENT")
    lines.append(f"{'Sentiment':<20} {'Trades':>8} {'Mean PnL':>12} {'Win Rate':>10}")
    lines.append("-" * 55)
    for _, row in pnl_df.dropna(subset=["mean_pnl"]).iterrows():
        lines.append(
            f"{row['sentiment']:<20} {int(row['trade_count']):>8,}"
            f" ${row['mean_pnl']:>10,.2f} {row['win_rate']*100:>9.1f}%"
        )

    lines.append("\n📈 2. CORRELATION (Fear/Greed Index vs Closed PnL)")
    lines.append(f"  Pearson  r = {corr['pearson_r']:+.4f}  (p={corr['pearson_p']:.4f})")
    lines.append(f"  Spearman r = {corr['spearman_r']:+.4f}  (p={corr['spearman_p']:.4f})")

    lines.append("\n💧 3. TRADING VOLUME BY SENTIMENT")
    lines.append(f"{'Sentiment':<20} {'Volume (USD M)':>16} {'Avg Trade $':>14}")
    lines.append("-" * 55)
    for _, row in vol_df.dropna(subset=["total_volume"]).iterrows():
        lines.append(
            f"{row['sentiment']:<20} ${row['total_volume']/1e6:>14,.1f}M"
            f" ${row['avg_trade_size']:>12,.0f}"
        )

    lines.append("\n⚡ 4. LIQUIDATIONS BY SENTIMENT")
    for _, row in liq_df.iterrows():
        lines.append(f"  {row['sentiment']:<20} {int(row['liquidations']):>6,} events")

    lines.append("\n" + sep)
    lines.append("  STRATEGIC TAKEAWAYS")
    lines.append(sep)
    best = pnl_df.dropna(subset=["mean_pnl"]).loc[pnl_df["mean_pnl"].idxmax(), "sentiment"]
    worst = pnl_df.dropna(subset=["mean_pnl"]).loc[pnl_df["mean_pnl"].idxmin(), "sentiment"]
    lines.append(f"  • Best avg PnL during  : {best}")
    lines.append(f"  • Worst avg PnL during : {worst}")
    sig = "significant" if corr["pearson_p"] < 0.05 else "not significant"
    direction = "positive" if corr["pearson_r"] > 0 else "negative"
    lines.append(f"  • Sentiment-PnL corr   : {direction} ({sig})")
    lines.append("")

    report = "\n".join(lines)
    print(report)

    out_path = OUTPUT_DIR / "insights_report.txt"
    out_path.write_text(report, encoding="utf-8")
    print(f"\n  Report saved → {out_path}")

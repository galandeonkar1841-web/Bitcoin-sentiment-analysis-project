# Bitcoin Market Sentiment × Trader Performance Analysis

Explore how the Bitcoin Fear & Greed Index relates to real trader performance
on the Hyperliquid exchange (211,000+ trades, full year 2024).

---

## Project Structure

```
bitcoin_sentiment_analysis/
├── data/
│   ├── fear_greed_index.csv      # Daily sentiment index (2018–2025)
│   └── historical_data.csv       # Hyperliquid trade records (2024)
├── src/
│   ├── data_loader.py            # Load & merge both datasets
│   ├── analysis.py               # All analytical functions
│   ├── visualize.py              # Chart generation (matplotlib / seaborn)
│   └── report.py                 # Text insights report writer
├── outputs/                      # Generated charts + report (auto-created)
├── run_analysis.py               # ← MAIN ENTRY POINT
└── requirements.txt
```

---

## Quick Start

### 1. Clone / download the folder
```bash
cd bitcoin_sentiment_analysis
```

### 2. Create a virtual environment (recommended)
```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Run the full analysis
```bash
python run_analysis.py
```

That's it. The script will:
- Load and merge both datasets
- Run all analysis functions
- Save **7 charts** to `outputs/`
- Print and save `outputs/insights_report.txt`

---

## Output Charts

| File | What it shows |
|---|---|
| `01_pnl_by_sentiment.png` | Mean PnL & win-rate per sentiment class |
| `02_volume_by_sentiment.png` | Total USD volume traded per sentiment |
| `03_daily_rolling_pnl.png` | 7-day rolling PnL over time (2024) |
| `04_sentiment_distribution.png` | Pie chart of sentiment days |
| `05_top_traders_heatmap.png` | Top-10 traders' PnL heat-map by sentiment |
| `06_scatter_fg_vs_pnl.png` | Scatter: F&G value vs daily PnL + trend line |
| `07_liquidations_by_sentiment.png` | Liquidation events per sentiment |

---

## Key Research Questions Answered

1. **Do traders profit more during Fear or Greed?**  
   → `01_pnl_by_sentiment.png` + insights report section 1

2. **Is there a statistically significant correlation between sentiment and PnL?**  
   → Pearson & Spearman correlation in insights report section 2

3. **When is trading volume highest?**  
   → `02_volume_by_sentiment.png`

4. **Which sentiment leads to most liquidations?**  
   → `07_liquidations_by_sentiment.png`

5. **How do top traders adapt to sentiment?**  
   → `05_top_traders_heatmap.png`

---

## Requirements

- Python 3.9+
- See `requirements.txt` (pandas, numpy, matplotlib, seaborn, scipy, jupyter)

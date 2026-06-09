"""
data_loader.py
Loads and merges the Fear/Greed index with the Hyperliquid trader data.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def load_fear_greed() -> pd.DataFrame:
    """Load the Bitcoin Fear & Greed index CSV."""
    df = pd.read_csv(DATA_DIR / "fear_greed_index.csv", parse_dates=["date"])
    df = df.rename(columns={"classification": "sentiment", "value": "fg_value"})
    df["date"] = df["date"].dt.date
    return df[["date", "fg_value", "sentiment"]]


def load_trades() -> pd.DataFrame:
    """Load the Hyperliquid historical trade data."""
    df = pd.read_csv(DATA_DIR / "historical_data.csv")

    # Parse the IST timestamp (format: DD-MM-YYYY HH:MM)
    df["datetime"] = pd.to_datetime(df["Timestamp IST"], format="%d-%m-%Y %H:%M", errors="coerce")
    df["date"] = df["datetime"].dt.date

    # Normalise column names
    df = df.rename(columns={
        "Account": "account",
        "Coin": "coin",
        "Execution Price": "exec_price",
        "Size Tokens": "size_tokens",
        "Size USD": "size_usd",
        "Side": "side",
        "Start Position": "start_position",
        "Direction": "direction",
        "Closed PnL": "closed_pnl",
        "Fee": "fee",
    })

    df["net_pnl"] = df["closed_pnl"] - df["fee"].abs()
    return df


def load_merged() -> pd.DataFrame:
    """Return trades left-joined with the daily sentiment."""
    trades = load_trades()
    fg = load_fear_greed()
    merged = trades.merge(fg, on="date", how="left")
    return merged


if __name__ == "__main__":
    df = load_merged()
    print(f"Merged dataset: {len(df):,} rows, {df.columns.tolist()}")
    print(df[["date", "sentiment", "closed_pnl"]].head())

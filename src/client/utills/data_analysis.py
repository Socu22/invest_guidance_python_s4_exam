import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any, cast
from matplotlib.figure import Figure

def analyze_stock_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze stock data using NumPy and Pandas with strict typing."""
    if df.empty:
        return {}

    # Make a copy to avoid modifying the original
    df = df.copy()

    # Convert date strings to datetime and sort
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Extract series with explicit type handling
    close_prices = cast(pd.Series, df['close'])
    volume = cast(pd.Series, df['volume'])

    # Calculate metrics with explicit type conversions
    analysis: Dict[str, Any] = {
        "period": {
            "start": str(df['date'].min().strftime("%Y-%m-%d")),
            "end": str(df['date'].max().strftime("%Y-%m-%d")),
            "days": int(len(df))
        },
        "price_stats": {
            "mean_close": float(close_prices.mean()),
            "median_close": float(close_prices.median()),
            "std_close": float(close_prices.mean()),
            "min_close": float(close_prices.min()),
            "max_close": float(close_prices.max()),
        },
        "volume_stats": {
            "mean": float(volume.mean()),
            "total": int(volume.sum())
        },
        "returns": {
            "daily": float(close_prices.pct_change().mean()),
            "total": float((close_prices.iloc[-1] / close_prices.iloc[0] - 1) * 100)
        }
    }
    return analysis

def plot_stock_trends(df: pd.DataFrame) -> Figure:
    """Plot stock trends using Matplotlib with type safety."""
    # Create figure first
    fig: Figure = plt.figure(figsize=(10, 8))

    if df.empty:
        ax = fig.add_subplot(111)
        ax.text(0.5, 0.5, "No data to plot", ha="center")
        return fig

    # Make a copy to avoid modifying the original
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    df = df.sort_values('date')

    # Add subplots
    ax1 = fig.add_subplot(211)
    ax2 = fig.add_subplot(212)

    # Price trend plot
    ax1.plot(df['date'], df['close'], label="Close Price", color="blue")
    ax1.set_title("Stock Price Trend")
    ax1.set_ylabel("Price ($)")
    ax1.grid(True)
    ax1.legend()

    # Volume trend plot
    ax2.bar(df['date'], df['volume'], label="Volume", color="green", alpha=0.6)
    ax2.set_title("Trading Volume")
    ax2.set_ylabel("Volume")
    ax2.grid(True)
    ax2.legend()

    plt.tight_layout()
    return fig
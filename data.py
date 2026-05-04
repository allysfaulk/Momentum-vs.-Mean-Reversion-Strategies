"""
data.py

Handles data loading and configuration.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

try:
    import yfinance as yf
    HAS_YFINANCE = True
except:
    HAS_YFINANCE = False

# ==================== PARAMETERS ====================
# Mix of trending and range-bound stocks
TICKERS = [
    "TSLA",  # High momentum (trendy tech)
    "SPY",   # Broad market (moderate trend)
    "KO",    # Coca-Cola (defensive, range-bound)
    "WMT",   # Walmart (stable, less trendy)
    "QQQ",   # Nasdaq (tech-heavy, trending)
    "XLU"    # Utilities ETF (defensive, mean-reverting)
]

# Test different time periods
TIME_PERIODS = {
    "Choppy Period (2011-2015)": ("2011-01-01", "2015-12-31"),  # Sideways market!
    "Bull Market (2016-2019)": ("2016-01-01", "2019-12-31"),
    "COVID Era (2020-2021)": ("2020-01-01", "2021-12-31"),
    "Recent Period (2022-2024)": ("2022-01-01", "2024-12-01")
}

INITIAL_CAPITAL = 10000
TRANSACTION_COST_BPS = 10

# Strategy Parameters - Testing both conservative and aggressive
MA_SHORT = 50
MA_LONG = 200
BB_PERIOD = 20
BB_STD = 2

# Add RSI mean-reversion as alternative
RSI_PERIOD = 14
RSI_OVERSOLD = 30
RSI_OVERBOUGHT = 70

RF_ANNUAL = 0.04
TRADING_DAYS = 252

# Save to Desktop
import os
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")
if not os.path.exists(DESKTOP):
    DESKTOP = os.path.expanduser("~")

plt.style.use('seaborn-v0_8-darkgrid')
plt.rcParams['figure.figsize'] = (14, 8)

# ==================== DATA DOWNLOAD ====================
print("=" * 70)
print("DOWNLOADING DATA FOR MULTIPLE STOCKS AND TIME PERIODS...")
print("=" * 70)

def download_with_yfinance(ticker, start, end):
    """Download with yfinance"""
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(start=start, end=end)
        
        if df.empty:
            df = yf.download(ticker, start=start, end=end, progress=False)
        
        if not df.empty and 'Close' in df.columns:
            df = df[['Close']].copy()
            df.columns = ['close']
            return df
    except Exception as e:
        print(f"  Error: {str(e)}")
    return None

def create_sample_data(ticker, start, end):
    """Create sample data"""
    dates = pd.date_range(start=start, end=end, freq='D')
    dates = [d for d in dates if d.weekday() < 5]
    
    np.random.seed(hash(ticker) % 2**32)
    
    # Different characteristics
    if ticker in ["TSLA", "QQQ"]:
        initial_price = 200
        drift = 0.0006
        volatility = 0.030
    elif ticker in ["KO", "WMT", "XLU"]:
        initial_price = 50
        drift = 0.0002
        volatility = 0.010
    else:  # SPY
        initial_price = 280
        drift = 0.0003
        volatility = 0.012
    
    n = len(dates)
    returns = np.random.normal(drift, volatility, n)
    price_series = initial_price * np.exp(np.cumsum(returns))
    
    df = pd.DataFrame({'close': price_series}, index=dates)
    return df

# Download all data (extended period to include 2011)
all_data = {}
full_start = "2011-01-01"  # Extended back to 2011
full_end = "2024-12-01"

for ticker in TICKERS:
    print(f"Downloading {ticker}...")
    df = None
    
    if HAS_YFINANCE:
        df = download_with_yfinance(ticker, full_start, full_end)
    
    if df is None or df.empty:
        df = create_sample_data(ticker, full_start, full_end)
    
    df['returns'] = df['close'].pct_change()
    all_data[ticker] = df
    print(f"  ✓ Got {len(df)} days of data")

print(f"\n✓ Data ready for all stocks!\n")

def load_all_data():
    all_data = {}

    full_start = "2011-01-01"
    full_end = "2024-12-01"

    for ticker in TICKERS:
        print(f"Downloading {ticker}...")
        df = None

        if HAS_YFINANCE:
            df = download_with_yfinance(ticker, full_start, full_end)

        if df is None or df.empty:
            df = create_sample_data(ticker, full_start, full_end)

        df['returns'] = df['close'].pct_change()
        all_data[ticker] = df
        print(f"  ✓ Got {len(df)} days of data")

    print("\n✓ Data ready for all stocks!\n")
    return all_data

"""
strategies.py

Establishes trading strategies and completes backtests.
"""

import data
print(data.__file__)

from data import (
    TICKERS,
    TIME_PERIODS,
    TRANSACTION_COST_BPS
)

# ==================== STRATEGY FUNCTIONS ====================

def calculate_momentum_signals(df, short_window, long_window):
    """Moving Average Crossover"""
    data = df.copy()
    data['ma_short'] = data['close'].rolling(window=short_window).mean()
    data['ma_long'] = data['close'].rolling(window=long_window).mean()
    data['signal_raw'] = (data['ma_short'] > data['ma_long']).astype(int)
    data['signal'] = data['signal_raw'].shift(1).fillna(0)
    return data

def calculate_bollinger_bands(df, period, num_std):
    """Bollinger Bands Mean-Reversion"""
    data = df.copy()
    data['bb_middle'] = data['close'].rolling(window=period).mean()
    data['bb_std'] = data['close'].rolling(window=period).std()
    data['bb_upper'] = data['bb_middle'] + (num_std * data['bb_std'])
    data['bb_lower'] = data['bb_middle'] - (num_std * data['bb_std'])
    
    position = 0
    signals = []
    
    for i in range(len(data)):
        if i == 0:
            signals.append(0)
            continue
        
        price = data['close'].iloc[i]
        upper = data['bb_upper'].iloc[i]
        lower = data['bb_lower'].iloc[i]
        middle = data['bb_middle'].iloc[i]
        
        if pd.notna(lower) and price <= lower and position == 0:
            position = 1
        elif pd.notna(upper) and price >= upper and position == 1:
            position = 0
        elif pd.notna(middle) and position == 1:
            if price >= middle:
                position = 0
        
        signals.append(position)
    
    data['signal'] = signals
    return data

def calculate_rsi_strategy(df, period=14, oversold=30, overbought=70):
    """RSI Mean-Reversion - More Aggressive"""
    data = df.copy()
    
    # Calculate RSI
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    data['rsi'] = 100 - (100 / (1 + rs))
    
    # Generate signals
    position = 0
    signals = []
    
    for i in range(len(data)):
        if i == 0:
            signals.append(0)
            continue
        
        rsi = data['rsi'].iloc[i]
        
        if pd.notna(rsi):
            if rsi < oversold and position == 0:
                position = 1  # Buy oversold
            elif rsi > overbought and position == 1:
                position = 0  # Sell overbought
        
        signals.append(position)
    
    data['signal'] = signals
    return data

def backtest_strategy(df, signal_col='signal', cost_bps=TRANSACTION_COST_BPS):
    """Backtest with costs"""
    data = df.copy()
    data['trade'] = data[signal_col].diff().fillna(0).abs()
    cost_per_trade = cost_bps / 10000
    data['cost'] = -cost_per_trade * data['trade']
    data['strat_returns'] = data[signal_col] * data['returns'] + data['cost']
    data['strat_cumulative'] = (1 + data['strat_returns']).cumprod()
    return data

def calculate_metrics(df):
    """Calculate metrics"""
    returns = df['strat_returns'].dropna()
    cumulative = df['strat_cumulative'].dropna()
    
    if len(cumulative) == 0:
        return {'Total Return': 0, 'CAGR': 0, 'Sharpe Ratio': 0, 
                'Max Drawdown': 0, 'Num Trades': 0}
    
    total_return = cumulative.iloc[-1] - 1
    days = (df.index[-1] - df.index[0]).days
    years = max(days / 365.25, 0.01)
    cagr = (cumulative.iloc[-1] ** (1/years)) - 1
    
    volatility = returns.std() * np.sqrt(TRADING_DAYS)
    rf_daily = (1 + RF_ANNUAL) ** (1/TRADING_DAYS) - 1
    excess = returns - rf_daily
    sharpe = (excess.mean() * TRADING_DAYS) / volatility if volatility > 0 else 0
    
    rolling_max = cumulative.cummax()
    drawdown = (cumulative / rolling_max) - 1
    max_dd = drawdown.min()
    num_trades = int(df['trade'].sum())
    
    return {
        'Total Return': total_return,
        'CAGR': cagr,
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_dd,
        'Num Trades': num_trades
    }

# ==================== RUN BACKTESTS ====================

print("=" * 70)
print("RUNNING BACKTESTS ACROSS STOCKS AND TIME PERIODS...")
print("=" * 70)

all_results = {}

for period_name, (start, end) in TIME_PERIODS.items():
    print(f"\n{period_name}: {start} to {end}")
    print("-" * 70)
    
    period_results = {}
    
    for ticker in TICKERS:
        # Filter data for this period
        df = all_data[ticker][(all_data[ticker].index >= start) & 
                              (all_data[ticker].index <= end)].copy()
        
        if len(df) < 250:  # Need enough data
            print(f"  {ticker}: Insufficient data")
            continue
        
        # Run strategies
        df_mom = calculate_momentum_signals(df, MA_SHORT, MA_LONG)
        df_mom = backtest_strategy(df_mom)
        
        df_bb = calculate_bollinger_bands(df, BB_PERIOD, BB_STD)
        df_bb = backtest_strategy(df_bb)
        
        df_rsi = calculate_rsi_strategy(df, RSI_PERIOD, RSI_OVERSOLD, RSI_OVERBOUGHT)
        df_rsi = backtest_strategy(df_rsi)
        
        period_results[ticker] = {
            'momentum': df_mom,
            'mean_rev_bb': df_bb,
            'mean_rev_rsi': df_rsi
        }
        
        # Quick winner check
        mom_sharpe = calculate_metrics(df_mom)['Sharpe Ratio']
        bb_sharpe = calculate_metrics(df_bb)['Sharpe Ratio']
        rsi_sharpe = calculate_metrics(df_rsi)['Sharpe Ratio']
        
        best_sharpe = max(mom_sharpe, bb_sharpe, rsi_sharpe)
        if mom_sharpe == best_sharpe:
            winner = "Momentum"
        elif bb_sharpe == best_sharpe:
            winner = "Mean-Rev (BB)"
        else:
            winner = "Mean-Rev (RSI)"
        
        print(f"  {ticker}: {winner} wins (Sharpe: {best_sharpe:.2f})")
    
    all_results[period_name] = period_results

print("\n✓ All backtests complete!\n")

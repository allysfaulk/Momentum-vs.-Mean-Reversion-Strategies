# Momentum-vs.-Mean-Reversion-Strategies

Overview:

This project implements a Python-based backtesting framework to compare momentum and mean-reversion trading strategies across different stocks and market regimes.

The goal is to analyze when each type of strategy performs best depending on:
  - Stock characteristics (growth vs defensive equities)
  - Market conditions (bull markets vs sideways periods)
  - Strategy type (trend-following vs mean-reverting behavior)


Strategies Implemented:

  1. Momentum Strategy
     
      Moving Average Crossover (short vs long-term MA)
        - Enters positions when short-term trend is above long-term trend
        - Designed to capture sustained directional moves
  3. Mean-Reversion Strategies
     
      Bollinger Bands Strategy
        - Buys when price moves below lower band
        - Exits when price reverts toward the mean
          
      RSI Strategy
        - Buys when asset is oversold (RSI < threshold)
        - Sells when overbought (RSI > threshold)


Data & Assets:

The project analyzes multiple equities and ETFs:
  - TSLA (high growth, high volatility)
  - SPY (broad market index)
  - QQQ (tech-heavy index)
  - KO, WMT (defensive, range-bound stocks)
  - XLU (utilities sector ETF)
    
Historical data is either:
  - Downloaded via yfinance, or
  - Generated as a fallback simulation for robustness
    
The strategies are evaluated across multiple time periods:
  - 2011–2015: Sideways / choppy market
  - 2016–2019: Bull market expansion
  - 2020–2021: COVID volatility period
  - 2022–2024: Recent market environment
    
Valuation Metrics:

Each strategy is evaluated using:
  - Total Return
  - CAGR (Compound Annual Growth Rate)
  - Sharpe Ratio
  - Maximum Drawdown
  - Number of Trades

Outputs:

The program generates:
  - Visualizations
  - Strategy performance heatmap (which strategy wins per stock/period)
  - Sharpe ratio comparisons across strategies
  - Win-rate breakdown by stock type (growth vs defensive)
  - Data Export
  - Full results summary (CSV)
  - Saved charts for analysis and presentation
    
All outputs are saved locally to the user's Desktop.


Project Structure:
  - main.py
    - Entry point (runs full pipeline)
  - data.py
    - Data loading + ticker/parameter definitions
  - strategies.py
    - Trading strategy logic + backtesting
  - analysis.py
    - Results aggregation + visualization

   
How to Run:

Install dependencies:
  - pip install numpy pandas matplotlib yfinance
    
Run the project:
  - python main.py

Key Insight:

Preliminary results suggest momentum strategies tend to perform better in trending markets and growth stocks. Mean-reversion strategies perform better in range-bound or defensive assets. Strategy effectiveness depends heavily on both asset type and market regime

Notes:

Developed for a quant club project. Do not use for financial advice.

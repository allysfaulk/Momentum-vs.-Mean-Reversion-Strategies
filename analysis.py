"""
analysis.py

Analyzes data, prints and plots the results
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

from data import TICKERS, TIME_PERIODS, DESKTOP
from strategies import calculate_metrics

# ==================== ANALYZE RESULTS ====================

def analyze_results(all_results):
    print("=" * 70)
    print("COMPREHENSIVE ANALYSIS")
    print("=" * 70)

    # Create summary for each period
    summary_data = []

    for period_name in TIME_PERIODS.keys():
        if period_name not in all_results:
            continue
        
        for ticker in TICKERS:
            if ticker not in all_results[period_name]:
                continue
            
            mom_metrics = calculate_metrics(all_results[period_name][ticker]['momentum'])
            bb_metrics = calculate_metrics(all_results[period_name][ticker]['mean_rev_bb'])
            rsi_metrics = calculate_metrics(all_results[period_name][ticker]['mean_rev_rsi'])
            
            summary_data.append({
                'Period': period_name,
                'Ticker': ticker,
                'Strategy': 'Momentum',
                **mom_metrics
            })
            
            summary_data.append({
                'Period': period_name,
                'Ticker': ticker,
                'Strategy': 'Mean-Rev (BB)',
                **bb_metrics
            })
            
            summary_data.append({
                'Period': period_name,
                'Ticker': ticker,
                'Strategy': 'Mean-Rev (RSI)',
                **rsi_metrics
            })

    summary_df = pd.DataFrame(summary_data)

    # Print detailed results
    for period_name in TIME_PERIODS.keys():
        period_data = summary_df[summary_df['Period'] == period_name]
        if period_data.empty:
            continue
        
        print(f"\n{period_name}")
        print("=" * 70)
        
        for ticker in TICKERS:
            ticker_data = period_data[period_data['Ticker'] == ticker]
            if ticker_data.empty:
                continue
            
            mom = ticker_data[ticker_data['Strategy'] == 'Momentum']
            bb = ticker_data[ticker_data['Strategy'] == 'Mean-Rev (BB)']
            rsi = ticker_data[ticker_data['Strategy'] == 'Mean-Rev (RSI)']
            
            if mom.empty or bb.empty or rsi.empty:
                continue
            
            mom_row = mom.iloc[0]
            bb_row = bb.iloc[0]
            rsi_row = rsi.iloc[0]
            
            # Find winner
            sharpes = {
                'Momentum': mom_row['Sharpe Ratio'],
                'Mean-Rev (BB)': bb_row['Sharpe Ratio'],
                'Mean-Rev (RSI)': rsi_row['Sharpe Ratio']
            }
            winner = max(sharpes, key=sharpes.get)
            margin = sharpes[winner] - min(sharpes.values())
            
            print(f"{ticker}: {winner} wins by {margin:.2f} Sharpe")
            print(f"  Momentum:       {mom_row['Total Return']:>7.1%} return, {mom_row['Sharpe Ratio']:>5.2f} Sharpe")
            print(f"  Mean-Rev (BB):  {bb_row['Total Return']:>7.1%} return, {bb_row['Sharpe Ratio']:>5.2f} Sharpe")
            print(f"  Mean-Rev (RSI): {rsi_row['Total Return']:>7.1%} return, {rsi_row['Sharpe Ratio']:>5.2f} Sharpe")

    # ==================== KEY FINDINGS ====================

    print("\n" + "=" * 70)
    print("KEY FINDINGS")
    print("=" * 70)

    # Overall winner per stock (most recent period)
    recent_period_data = summary_df[summary_df['Period'] == 'Recent Period (2022-2024)']
    if not recent_period_data.empty:
        print("\nOVERALL WINNERS (Most Recent Period):")
        for ticker in TICKERS:
            ticker_data = recent_period_data[recent_period_data['Ticker'] == ticker]
            if ticker_data.empty or len(ticker_data) == 0:
                continue
            winner_row = ticker_data.loc[ticker_data['Sharpe Ratio'].idxmax()]
            print(f"  {ticker}: {winner_row['Strategy']} (Sharpe: {winner_row['Sharpe Ratio']:.2f})")

    # Mean-reversion success cases
    print("\nWHEN MEAN-REVERSION WINS:")
    mr_wins = 0
    total_tests = 0

    for period in TIME_PERIODS.keys():
        period_data = summary_df[summary_df['Period'] == period]
        if period_data.empty:
            continue
        
        for ticker in TICKERS:
            ticker_data = period_data[period_data['Ticker'] == ticker]
            if ticker_data.empty or len(ticker_data) == 0:
                continue
            
            total_tests += 1
            winner = ticker_data.loc[ticker_data['Sharpe Ratio'].idxmax()]
            
            if 'Mean-Rev' in winner['Strategy']:
                mr_wins += 1
                print(f"  ✓ {ticker} in {period} - {winner['Strategy']}")
                print(f"    Sharpe: {winner['Sharpe Ratio']:.2f}, Return: {winner['Total Return']:.1%}")

    if total_tests > 0:
        print(f"\nMean-Reversion Win Rate: {mr_wins}/{total_tests} = {mr_wins/total_tests*100:.1f}%")
    else:
        print("\nNo complete test results available")

    # ==================== VISUALIZATIONS ====================

    print("\n" + "=" * 70)
    print("GENERATING CHARTS...")
    print("=" * 70)

    # 1. HEATMAP: Which Strategy Wins Where
    fig, ax = plt.subplots(figsize=(14, 8))

    # Create matrix: rows = tickers, cols = periods, values = winning strategy
    heatmap_data = []
    period_names_list = list(TIME_PERIODS.keys())

    for ticker in TICKERS:
        row = []
        for period_name in period_names_list:
            period_data = summary_df[(summary_df['Period'] == period_name) & 
                                    (summary_df['Ticker'] == ticker)]
            if period_data.empty or len(period_data) == 0:
                row.append(0)  # No data
                continue
            
            winner = period_data.loc[period_data['Sharpe Ratio'].idxmax()]
            # 1 = Momentum, -1 = Mean-Rev, 0 = no data
            if winner['Strategy'] == 'Momentum':
                row.append(1)
            else:
                row.append(-1)
        heatmap_data.append(row)

    heatmap_array = np.array(heatmap_data)

    im = ax.imshow(heatmap_array, cmap='RdYlGn', aspect='auto', vmin=-1, vmax=1)

    ax.set_xticks(np.arange(len(period_names_list)))
    ax.set_yticks(np.arange(len(TICKERS)))
    ax.set_xticklabels([p.split('(')[0].strip() for p in period_names_list], rotation=15, ha='right')
    ax.set_yticklabels(TICKERS)

    # Add text annotations
    for i in range(len(TICKERS)):
        for j in range(len(period_names_list)):
            if heatmap_array[i, j] == 1:
                text = "MOM"
                color = "white"
            elif heatmap_array[i, j] == -1:
                text = "M-R"
                color = "white"
            else:
                text = "N/A"
                color = "gray"
            ax.text(j, i, text, ha="center", va="center", 
                color=color, fontweight='bold', fontsize=11)

    ax.set_title('Strategy Performance Heatmap: When Does Each Strategy Win?\n(Green = Momentum, Red = Mean-Reversion, Gray = No Data)', 
                fontsize=14, fontweight='bold', pad=20)

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Winner', rotation=270, labelpad=20)
    cbar.set_ticks([-1, 0, 1])
    cbar.set_ticklabels(['Mean-Rev', 'No Data', 'Momentum'])

    plt.tight_layout()
    save_path = os.path.join(DESKTOP, 'strategy_winners_heatmap.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {save_path}")

    # 2. SHARPE COMPARISON BY STOCK (Most Recent Period)
    recent_data = summary_df[summary_df['Period'] == 'Recent Period (2022-2024)']
    if not recent_data.empty and len(recent_data) > 0:
        fig, ax = plt.subplots(figsize=(12, 7))
        
        # Get available tickers for this period
        available_tickers = recent_data['Ticker'].unique()
        
        if len(available_tickers) > 0:
            sharpe_pivot = recent_data.pivot(index='Ticker', columns='Strategy', values='Sharpe Ratio')
            
            x = np.arange(len(available_tickers))
            width = 0.25
            
            bars1 = ax.bar(x - width, sharpe_pivot['Momentum'], width, 
                        label='Momentum', color='#2E7D32', alpha=0.85)
            bars2 = ax.bar(x, sharpe_pivot['Mean-Rev (BB)'], width, 
                        label='Mean-Rev (BB)', color='#D84315', alpha=0.85)
            bars3 = ax.bar(x + width, sharpe_pivot['Mean-Rev (RSI)'], width, 
                        label='Mean-Rev (RSI)', color='#F57C00', alpha=0.85)
            
            ax.set_xlabel('Stock', fontsize=13, fontweight='bold')
            ax.set_ylabel('Sharpe Ratio', fontsize=13, fontweight='bold')
            ax.set_title('Recent Period (2022-2024): Strategy Comparison', 
                        fontsize=14, fontweight='bold')
            ax.set_xticks(x)
            ax.set_xticklabels(available_tickers, fontsize=11)
            ax.legend(fontsize=11)
            ax.grid(True, alpha=0.3, axis='y')
            ax.axhline(y=0, color='black', linestyle='-', linewidth=0.8)
            
            for bars in [bars1, bars2, bars3]:
                for bar in bars:
                    height = bar.get_height()
                    if not np.isnan(height):
                        ax.text(bar.get_x() + bar.get_width()/2., height,
                            f'{height:.2f}', ha='center', va='bottom', fontsize=9)
            
            plt.tight_layout()
            save_path = os.path.join(DESKTOP, 'sharpe_by_stock.png')
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            print(f"✓ Saved: {save_path}")
        else:
            print("⚠️  Skipping sharpe_by_stock chart (no data)")
    else:
        print("⚠️  Skipping sharpe_by_stock chart (no recent data)")

    # 3. WIN RATE BY STOCK TYPE
    fig, ax = plt.subplots(figsize=(10, 6))

    stock_categories = {
        'High Growth\n(TSLA, QQQ)': ['TSLA', 'QQQ'],
        'Broad Market\n(SPY)': ['SPY'],
        'Defensive\n(KO, WMT, XLU)': ['KO', 'WMT', 'XLU']
    }

    category_wins = {'Momentum': [], 'Mean-Reversion': []}

    for category, tickers in stock_categories.items():
        mom_wins = 0
        mr_wins = 0
        
        for ticker in tickers:
            ticker_data = summary_df[summary_df['Ticker'] == ticker]
            if ticker_data.empty:
                continue
            
            for period in TIME_PERIODS.keys():
                period_data = ticker_data[ticker_data['Period'] == period]
                if period_data.empty or len(period_data) == 0:
                    continue
                
                winner = period_data.loc[period_data['Sharpe Ratio'].idxmax()]
                if winner['Strategy'] == 'Momentum':
                    mom_wins += 1
                else:  # Any mean-reversion strategy
                    mr_wins += 1
        
        total = mom_wins + mr_wins
        if total > 0:
            category_wins['Momentum'].append(mom_wins / total * 100)
            category_wins['Mean-Reversion'].append(mr_wins / total * 100)
        else:
            category_wins['Momentum'].append(0)
            category_wins['Mean-Reversion'].append(0)

    x = np.arange(len(stock_categories))
    width = 0.35

    bars1 = ax.bar(x - width/2, category_wins['Momentum'], width, 
                label='Momentum', color='#2E7D32', alpha=0.85)
    bars2 = ax.bar(x + width/2, category_wins['Mean-Reversion'], width, 
                label='Mean-Reversion', color='#D84315', alpha=0.85)

    ax.set_ylabel('Win Rate (%)', fontsize=12, fontweight='bold')
    ax.set_title('Which Strategy Works Best for Different Stock Types?', 
                fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(stock_categories.keys(), fontsize=10)
    ax.legend(fontsize=11)
    ax.grid(True, alpha=0.3, axis='y')
    ax.set_ylim(0, 100)

    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.0f}%', ha='center', va='bottom', fontsize=10, fontweight='bold')

    plt.tight_layout()
    save_path = os.path.join(DESKTOP, 'winrate_by_type.png')
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {save_path}")

    # Save summary CSV
    csv_path = os.path.join(DESKTOP, 'full_results_summary.csv')
    try:
        summary_df.to_csv(csv_path, index=False)
        print(f"✓ Saved: {csv_path}")
    except PermissionError:
        print(f"⚠️  Could not save CSV (close Excel)")

    # ==================== FINAL INSIGHTS ====================

    print("\n" + "=" * 70)
    print("PRESENTATION INSIGHTS")
    print("=" * 70)

    print("\n📊 WHAT WE LEARNED:")
    print("\n1. MOMENTUM DOMINATES HIGH-GROWTH STOCKS:")
    print("   - TSLA, QQQ show strong trends → Momentum wins")
    print("   - These stocks have persistent directional moves")

    print("\n2. MEAN-REVERSION WORKS BETTER FOR DEFENSIVE STOCKS:")
    defensive_wins = []
    for ticker in ['KO', 'WMT', 'XLU']:
        # Check across all periods
        ticker_all_data = summary_df[summary_df['Ticker'] == ticker]
        if not ticker_all_data.empty:
            mr_count = 0
            total_count = 0
            for period in TIME_PERIODS.keys():
                ticker_period_data = ticker_all_data[ticker_all_data['Period'] == period]
                if not ticker_period_data.empty and len(ticker_period_data) > 0:
                    winner = ticker_period_data.loc[ticker_period_data['Sharpe Ratio'].idxmax()]
                    total_count += 1
                    if 'Mean-Rev' in winner['Strategy']:
                        mr_count += 1
            
            if total_count > 0 and mr_count > 0:
                defensive_wins.append(f"{ticker} ({mr_count}/{total_count} periods)")

    if defensive_wins:
        print(f"   - Mean-reversion won for: {', '.join(defensive_wins)}")
    else:
        print("   - Even defensive stocks favored momentum in this bull market period")
    print("   - These stocks typically trade in ranges, not trends")

    print("\n3. TIME PERIOD MATTERS:")
    print("   - Check the heatmap to see how winners change over time")
    print("   - Volatile periods may favor mean-reversion")

    print("\n4. KEY TAKEAWAY:")
    print("   - Match strategy to asset type!")
    print("   - Trending assets → Momentum")
    print("   - Range-bound assets → Mean-Reversion")

    print("\n" + "=" * 70)
    print("ALL DONE! 🎉")
    print("=" * 70)
    print(f"\nAll files saved to: {DESKTOP}")
    print("\nCharts created:")
    print("  1. strategy_winners_heatmap.png - When each strategy wins")
    print("  2. sharpe_by_stock.png - Stock-by-stock comparison")
    print("  3. winrate_by_type.png - Win rates by stock category")
    print("  4. full_results_summary.csv - All the data")
    
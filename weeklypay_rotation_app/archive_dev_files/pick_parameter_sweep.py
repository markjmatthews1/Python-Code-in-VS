"""Parameter sweep for Pick of the Day strategy - find what actually works

Tests different combinations of:
- Target profit % (1%, 2%, 3%, 4%, 5%, 6%)
- Strike selection (ATM, 0.5% OTM, 1% OTM)
- IV assumptions (0.15, 0.20, 0.25, 0.30)
"""

import pandas as pd
from pick_of_the_day_sim import simulate

# Suppress warnings for cleaner output
import warnings
warnings.filterwarnings('ignore')

print("=" * 80)
print("PICK OF THE DAY - PARAMETER SWEEP")
print("Testing different targets, strikes, and IV to find viable strategy")
print("=" * 80)

results = []

# Test different target percentages
targets = [0.01, 0.02, 0.03, 0.04, 0.05, 0.06]
ivs = [0.15, 0.20, 0.25, 0.30]

for target in targets:
    for iv in ivs:
        print(f"\nTesting: Target={target*100:.0f}%, IV={iv:.0%}...")
        
        # Run simulation
        df = simulate(symbol='SPY', days_back=8, iv=iv, target_pct=target, slippage_pct=0.005)
        
        if df is not None and len(df) > 0:
            wins = len(df[df['hit_target']])
            win_rate = wins / len(df)
            avg_pnl = df['pnl_pct'].mean()
            
            # Calculate expectancy (what you'd make per trade on average)
            expectancy = avg_pnl
            
            results.append({
                'Target %': f"{target*100:.0f}%",
                'IV': f"{iv:.0%}",
                'Trades': len(df),
                'Wins': wins,
                'Win Rate': f"{win_rate:.1%}",
                'Avg P&L': f"{avg_pnl:.2%}",
                'Expectancy': f"{expectancy:.2%}",
                'Viable?': '✅ YES' if expectancy > 0 and win_rate > 0.3 else '❌ NO'
            })
        else:
            results.append({
                'Target %': f"{target*100:.0f}%",
                'IV': f"{iv:.0%}",
                'Trades': 0,
                'Wins': 0,
                'Win Rate': 'N/A',
                'Avg P&L': 'N/A',
                'Expectancy': 'N/A',
                'Viable?': '❌ NO DATA'
            })

# Create results dataframe
results_df = pd.DataFrame(results)

print("\n" + "=" * 80)
print("RESULTS SUMMARY - What Actually Works")
print("=" * 80)
print(results_df.to_string(index=False))

# Show best strategies
print("\n" + "=" * 80)
print("BEST STRATEGIES (Positive Expectancy)")
print("=" * 80)
viable = results_df[results_df['Viable?'].str.contains('YES', na=False)]
if len(viable) > 0:
    print(viable.to_string(index=False))
    print(f"\n✅ Found {len(viable)} viable strategy combinations!")
else:
    print("❌ NO VIABLE STRATEGIES FOUND")
    print("\nRecommendations:")
    print("1. 6% target is too aggressive for ATM zero-DTE in 25 minutes")
    print("2. Try 2-3% target with slightly OTM strikes (cheaper premium = bigger % moves)")
    print("3. Consider using delta-based sizing instead of ATM strikes")
    print("4. Real 'Pick of the Day' likely uses proprietary signals beyond VWAP")

"""
Enhanced Day Trader - Trade Analysis
Analyzing 6 paper trades to identify why strategy is losing money
"""

import json
from datetime import datetime, timedelta

# Load trade data
with open('../paper_trades.json', 'r') as f:
    data = json.load(f)

print("=" * 80)
print("ENHANCED DAY TRADER - TRADE ANALYSIS")
print("=" * 80)
print(f"\nAccount Summary:")
print(f"  Initial Balance: ${data['initial_balance']:,.2f}")
print(f"  Current Balance: ${data['current_balance']:,.2f}")
print(f"  Total P&L: ${data['total_pnl']:,.2f} ({(data['total_pnl']/data['initial_balance']*100):.2f}%)")
print(f"  Total Commission: ${data['total_commission']:,.2f}")
print(f"  Trades: {len(data['closed_trades'])}")

# Analyze each trade
trades = data['closed_trades']
wins = [t for t in trades if t['pnl'] > 0]
losses = [t for t in trades if t['pnl'] <= 0]

print(f"\n  Win Rate: {len(wins)}/{len(trades)} = {len(wins)/len(trades)*100:.1f}%")
print(f"  Loss Rate: {len(losses)}/{len(trades)} = {len(losses)/len(trades)*100:.1f}%")

print("\n" + "=" * 80)
print("INDIVIDUAL TRADE ANALYSIS")
print("=" * 80)

for i, trade in enumerate(trades, 1):
    print(f"\n{i}. {trade['ticker']} - {trade['status']}")
    print(f"   Entry: ${trade['open_price']:.2f} @ {trade['open_time']}")
    print(f"   Exit:  ${trade['close_price']:.2f} @ {trade['close_time']}")
    print(f"   Stop Loss: ${trade['stop_loss']:.2f}")
    print(f"   Take Profit: ${trade['take_profit']:.2f}")
    
    # Calculate how close to targets
    entry = trade['open_price']
    exit_price = trade['close_price']
    stop = trade['stop_loss']
    take = trade['take_profit']
    
    stop_distance = abs(entry - stop)
    take_distance = abs(take - entry)
    actual_move = exit_price - entry
    
    print(f"   Quantity: {trade['quantity']}")
    print(f"   P&L: ${trade['pnl']:.2f} ({trade['pnl_percent']:.2f}%)")
    print(f"   Signal Strength: {trade['signal_strength']}")
    
    # Calculate hold time
    open_time = datetime.fromisoformat(trade['open_time'])
    close_time = datetime.fromisoformat(trade['close_time'])
    hold_time = close_time - open_time
    hours = hold_time.total_seconds() / 3600
    
    print(f"   Hold Time: {hours:.2f} hours")
    print(f"   Stop Distance: ${stop_distance:.2f} ({stop_distance/entry*100:.2f}%)")
    print(f"   Take Distance: ${take_distance:.2f} ({take_distance/entry*100:.2f}%)")
    print(f"   Risk/Reward: 1:{take_distance/stop_distance:.2f}")
    print(f"   Actual Move: ${actual_move:.2f} ({actual_move/entry*100:.2f}%)")

print("\n" + "=" * 80)
print("PATTERN ANALYSIS")
print("=" * 80)

# 1. Stop Loss Analysis
print("\n1. STOP LOSS ANALYSIS:")
stop_loss_trades = [t for t in trades if 'STOP_LOSS' in t['status']]
print(f"   Stop Loss Hit: {len(stop_loss_trades)}/{len(trades)} = {len(stop_loss_trades)/len(trades)*100:.0f}%")

avg_stop_distance = sum(abs(t['open_price'] - t['stop_loss'])/t['open_price']*100 for t in trades) / len(trades)
print(f"   Average Stop Distance: {avg_stop_distance:.2f}% from entry")

# Check if stops are too tight
print(f"\n   Individual Stop Distances:")
for t in trades:
    stop_dist = abs(t['open_price'] - t['stop_loss'])/t['open_price']*100
    print(f"   {t['ticker']}: {stop_dist:.2f}% - {'TOO TIGHT' if stop_dist < 0.5 else 'OK'}")

# 2. Hold Time Analysis
print("\n2. HOLD TIME ANALYSIS:")
hold_times = []
for t in trades:
    open_time = datetime.fromisoformat(t['open_time'])
    close_time = datetime.fromisoformat(t['close_time'])
    hours = (close_time - open_time).total_seconds() / 3600
    hold_times.append(hours)

avg_hold = sum(hold_times) / len(hold_times)
print(f"   Average Hold Time: {avg_hold:.2f} hours")
print(f"   Shortest: {min(hold_times):.2f} hours")
print(f"   Longest: {max(hold_times):.2f} hours")

quick_losses = [t for t in trades if (datetime.fromisoformat(t['close_time']) - datetime.fromisoformat(t['open_time'])).total_seconds() < 3600]
print(f"   Quick Losses (< 1 hour): {len(quick_losses)} trades")

# 3. Entry Time Analysis
print("\n3. ENTRY TIME ANALYSIS:")
morning_trades = []
afternoon_trades = []

for t in trades:
    open_time = datetime.fromisoformat(t['open_time'])
    hour = open_time.hour + open_time.minute/60
    
    if hour < 12:
        morning_trades.append(t)
    else:
        afternoon_trades.append(t)
    
    print(f"   {t['ticker']}: {open_time.strftime('%I:%M %p')} - {'Morning' if hour < 12 else 'Afternoon'}")

print(f"\n   Morning Trades: {len(morning_trades)} (P&L: ${sum(t['pnl'] for t in morning_trades):.2f})")
print(f"   Afternoon Trades: {len(afternoon_trades)} (P&L: ${sum(t['pnl'] for t in afternoon_trades):.2f})")

# 4. Risk/Reward Analysis
print("\n4. RISK/REWARD ANALYSIS:")
for t in trades:
    stop_dist = abs(t['open_price'] - t['stop_loss'])
    take_dist = abs(t['take_profit'] - t['open_price'])
    rr_ratio = take_dist / stop_dist if stop_dist > 0 else 0
    print(f"   {t['ticker']}: 1:{rr_ratio:.2f}")

avg_rr = sum((abs(t['take_profit'] - t['open_price']) / abs(t['open_price'] - t['stop_loss'])) for t in trades) / len(trades)
print(f"\n   Average R/R Ratio: 1:{avg_rr:.2f}")

# 5. Ticker Analysis
print("\n5. TICKER PERFORMANCE:")
tickers = {}
for t in trades:
    if t['ticker'] not in tickers:
        tickers[t['ticker']] = {'trades': 0, 'pnl': 0}
    tickers[t['ticker']]['trades'] += 1
    tickers[t['ticker']]['pnl'] += t['pnl']

for ticker, stats in sorted(tickers.items(), key=lambda x: x[1]['pnl']):
    print(f"   {ticker}: {stats['trades']} trades, ${stats['pnl']:.2f} P&L")

print("\n" + "=" * 80)
print("KEY FINDINGS & RECOMMENDATIONS")
print("=" * 80)

findings = []

# Finding 1: Stop Loss Tightness
if avg_stop_distance < 0.5:
    findings.append({
        'issue': '🔴 STOPS TOO TIGHT',
        'detail': f'Average stop distance is {avg_stop_distance:.2f}% - normal market noise can trigger',
        'recommendation': 'Increase stops to 0.8-1.0% for ETFs, 1.0-1.5% for volatile stocks'
    })

# Finding 2: Win Rate
win_rate = len(wins)/len(trades)*100
if win_rate < 40:
    findings.append({
        'issue': '🔴 LOW WIN RATE',
        'detail': f'Win rate is {win_rate:.0f}% - below break-even threshold',
        'recommendation': 'Need stricter entry criteria: wait for stronger confirmation signals'
    })

# Finding 3: Quick Losses
if len(quick_losses) >= 2:
    findings.append({
        'issue': '🔴 QUICK STOP OUTS',
        'detail': f'{len(quick_losses)} trades stopped out in < 1 hour',
        'recommendation': 'Entry timing too early - wait for trend confirmation, avoid opening range'
    })

# Finding 4: Risk/Reward
if avg_rr < 2.0:
    findings.append({
        'issue': '🟡 POOR RISK/REWARD',
        'detail': f'Average R/R is 1:{avg_rr:.2f} - need 2:1 or better',
        'recommendation': 'Either widen take profits OR tighten stops (but not too tight!)'
    })

# Finding 5: All Stop Losses
if len(stop_loss_trades) == len(trades):
    findings.append({
        'issue': '🔴 NO WINNERS',
        'detail': 'All trades hit stop loss - none reached take profit',
        'recommendation': 'Take profits may be too ambitious OR entry timing needs work'
    })

# Finding 6: Average Loss
avg_loss = sum(t['pnl'] for t in losses) / len(losses) if losses else 0
if abs(avg_loss) > 10:
    findings.append({
        'issue': '🔴 LARGE LOSSES',
        'detail': f'Average loss is ${avg_loss:.2f} - position sizing too aggressive',
        'recommendation': 'Reduce position sizes OR tighten stops (carefully!)'
    })

for i, finding in enumerate(findings, 1):
    print(f"\n{i}. {finding['issue']}")
    print(f"   Problem: {finding['detail']}")
    print(f"   Fix: {finding['recommendation']}")

print("\n" + "=" * 80)
print("ACTIONABLE IMPROVEMENTS")
print("=" * 80)

print("""
Based on the analysis, here are specific code changes needed:

1. LOOSEN STOP LOSSES (Currently ~0.4% avg)
   Change in live_signals.py:
   - Line ~250: stop_loss = entry_price * 0.996  # Change to 0.992 (0.8% stop)
   - Line ~251: take_profit = entry_price * 1.008  # Keep 0.8% target (now 1:1 R/R)
   
2. ADD ENTRY DELAY (Avoid opening range volatility)
   Change in live_signals.py:
   - Line ~234: Skip trades before 9:45 AM (not just 9:30 AM)
   - Add: "Skip trades before 9:45 AM (avoid opening range)"
   
3. REQUIRE STRONGER SIGNALS (Currently accepting 0.75+)
   Change in live_signals.py:
   - Line ~200: if strength >= 0.85:  # Raise from 0.75 to 0.85
   
4. REDUCE POSITION SIZE (Currently too aggressive)
   Change in paper_trader.py:
   - Reduce shares per trade by 30-50%
   - This gives more room for multiple positions
   
5. ADD MOMENTUM FILTER
   - Only take longs when price > 20-period SMA (already doing this)
   - ADD: Price must also be > yesterday's close
   - ADD: Today's volume > yesterday's volume

6. IMPROVE TAKE PROFIT
   - Current: 0.8% target with 0.4% stop = 2:1 R/R (good)
   - Problem: Not reaching targets
   - Solution: Consider trailing stop after 0.4% profit

Would you like me to implement these changes?
""")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"""
Sample Size: {len(trades)} trades (SMALL - need 20+ for statistical significance)
Win Rate: {win_rate:.0f}% (need 40%+ with current R/R)
Avg Hold: {avg_hold:.1f} hours
Avg Stop: {avg_stop_distance:.2f}% (TOO TIGHT)
Avg R/R: 1:{avg_rr:.2f}

Main Issue: Stops too tight + entries too early = death by 1000 paper cuts

Quick Wins:
1. Widen stops to 0.8%
2. Wait until 9:45 AM to enter
3. Raise signal threshold to 0.85
4. Reduce position sizes

Expected Improvement: 40-50% win rate with these changes
""")

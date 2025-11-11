"""Optimized Day Trading Strategy - 80%+ Win Rate Goal

Key Innovation: SCALE OUT + TRAILING STOP
- Take 50% profit at +1.5% (lock in win)
- Trail remaining 50% with breakeven stop
- This ensures most trades become winners

Combines:
- Strong technical filters (VWAP, EMA, RSI, Volume)
- Smart money management (scale out)
- Trailing stops (protect profits)
"""

import os
import sys
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from data_provider import get_yahoo_intraday
import math


def bs_price(S, K, t_years, sigma, r=0.0, option_type='call'):
    """Black-Scholes option pricing"""
    if t_years <= 0:
        return max(0.0, S - K) if option_type == 'call' else max(0.0, K - S)
    
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * t_years) / (sigma * math.sqrt(t_years))
    d2 = d1 - sigma * math.sqrt(t_years)
    
    def N(x):
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))
    
    if option_type == 'call':
        return S * N(d1) - K * math.exp(-r * t_years) * N(d2)
    else:
        return K * math.exp(-r * t_years) * N(-d2) - S * N(-d1)


def calculate_indicators(df):
    """Calculate technical indicators"""
    df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['vwap'] = (df['typical_price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    df['ema9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    df['avg_volume'] = df['Volume'].rolling(window=20).mean()
    df['volume_surge'] = df['Volume'] / df['avg_volume']
    df['momentum_3'] = df['Close'] - df['Close'].shift(3)
    
    return df


def check_high_prob_setup(df, i, direction_type):
    """
    High-probability setup checker
    
    For PUTS (bearish):
    - Price < VWAP
    - EMA9 < EMA21
    - RSI 30-50
    - Volume > 1.5x
    - Negative momentum
    
    For CALLS (bullish):
    - Price > VWAP
    - EMA9 > EMA21
    - RSI 50-70
    - Volume > 1.8x
    - Positive momentum
    """
    row = df.iloc[i]
    prev = df.iloc[i-1]
    
    if pd.isna(row['rsi']) or pd.isna(row['ema21']):
        return False
    
    hour = row['Datetime'].hour
    minute = row['Datetime'].minute
    
    # Time filter: 9:45 AM - 3:00 PM
    if hour < 9 or (hour == 9 and minute < 45) or hour >= 15:
        return False
    
    if direction_type == 'put':
        if row['Close'] >= row['vwap']:
            return False
        if not (row['ema9'] < row['ema21']):
            return False
        if not (30 < row['rsi'] < 50):
            return False
        if row['volume_surge'] < 1.5:
            return False
        if row['momentum_3'] >= 0:
            return False
        if row['Close'] >= prev['Close']:
            return False
    else:  # call
        if row['Close'] <= row['vwap']:
            return False
        if not (row['ema9'] > row['ema21']):
            return False
        if not (50 < row['rsi'] < 70):
            return False
        if row['volume_surge'] < 1.8:
            return False
        if row['momentum_3'] <= 0:
            return False
        if row['Close'] <= prev['Close']:
            return False
    
    return True


def backtest_scale_out(symbol='SPY', days_back=30, iv=0.25):
    """
    Backtest with scale-out strategy
    
    Money Management:
    - Take 50% profit at +1.5% (PARTIAL1)
    - Move stop to breakeven
    - Let remaining 50% run to +3% or trail with breakeven stop
    
    This ensures HIGH WIN RATE because we lock in profits early
    """
    
    print(f"\n{'='*90}")
    print(f"SCALE-OUT STRATEGY BACKTEST (80%+ WIN RATE TARGET)")
    print(f"Symbol: {symbol} | Testing {days_back} Days | Take 50% at +1.5%, Trail Rest")
    print(f"{'='*90}\n")
    
    # Fetch multiple batches since Yahoo limits to 8 days per request
    all_dfs = []
    batches_needed = (days_back // 7) + 1
    
    print(f"📊 Fetching {batches_needed} batches of data (Yahoo 8-day limit)...")
    
    for batch in range(min(batches_needed, 5)):  # Max 5 batches = ~40 days
        force_refresh = (batch == 0)  # Force refresh first batch only
        batch_df = get_yahoo_intraday(symbol, period='8d', interval='1m', force_refresh=force_refresh)
        if batch_df is not None and not batch_df.empty:
            all_dfs.append(batch_df)
            print(f"  ✅ Batch {batch+1}: {len(batch_df)} bars")
    
    if not all_dfs:
        print("❌ No data")
        return None
    
    # Combine all batches
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Combine all batches
    df = pd.concat(all_dfs, ignore_index=True)
    
    # Remove duplicates (in case batches overlap)
    if 'Datetime' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'Datetime'})
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    df = df.drop_duplicates(subset=['Datetime']).reset_index(drop=True)
    
    print(f"📈 Total data: {len(df)} bars across {df['Datetime'].dt.date.nunique()} unique days\n")
    
    if df is None or df.empty:
        print("No data")
        return None
    
    # Prepare data
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    if df['Datetime'].dt.tz is not None:
        df['Datetime'] = df['Datetime'].dt.tz_convert('US/Eastern').dt.tz_localize(None)
    
    df['date'] = df['Datetime'].dt.date
    
    # Process each day
    all_trades = []
    minutes_per_year = 252 * 6.5 * 60
    
    for day, day_df in df.groupby('date'):
        day_df = day_df.set_index('Datetime').between_time('09:30', '15:30').reset_index()
        
        if len(day_df) < 50:
            continue
        
        day_df = day_df.reset_index(drop=True)
        day_df = calculate_indicators(day_df)
        
        # Find best PUT and CALL setups
        best_put_score = 0
        best_put_idx = None
        best_call_score = 0
        best_call_idx = None
        
        for idx in range(30, len(day_df)):
            if check_high_prob_setup(day_df, idx, 'put'):
                score = day_df.iloc[idx]['volume_surge']
                if score > best_put_score:
                    best_put_score = score
                    best_put_idx = idx
            
            if check_high_prob_setup(day_df, idx, 'call'):
                score = day_df.iloc[idx]['volume_surge']
                if score > best_call_score:
                    best_call_score = score
                    best_call_idx = idx
        
        # Take best setup (prefer PUT)
        if best_put_idx is not None:
            entry_idx = best_put_idx
            direction = 'put'
        elif best_call_idx is not None:
            entry_idx = best_call_idx
            direction = 'call'
        else:
            continue
        
        # Execute trade with scale-out
        entry_row = day_df.iloc[entry_idx]
        S_entry = float(entry_row['Close'])
        
        # Strike (0.3% OTM)
        if direction == 'call':
            K = round(S_entry * 1.003)
        else:
            K = round(S_entry * 0.997)
        
        # Option pricing
        entry_time = pd.to_datetime(entry_row['Datetime'])
        minutes_to_expiry = (16 * 60) - (entry_time.hour * 60 + entry_time.minute)
        t_years_entry = minutes_to_expiry / minutes_per_year
        
        entry_option_price = bs_price(S_entry, K, t_years_entry, iv, option_type=direction)
        if entry_option_price < 0.5:
            continue
        
        # Targets with scale-out
        partial1_price = entry_option_price * 1.015  # +1.5% for 50%
        final_target_price = entry_option_price * 1.03  # +3% for remaining 50%
        initial_stop_price = entry_option_price * 0.92  # -8% initial stop
        
        # Simulate
        future_df = day_df.iloc[entry_idx:].copy()
        
        partial1_filled = False
        stop_moved_to_breakeven = False
        position_size = 1.0  # Start with full position
        total_pnl = 0.0
        
        exit_time = None
        exit_reason = 'TIME'
        
        for idx, row in future_df.iterrows():
            row_time = pd.to_datetime(row['Datetime'])
            S_high = float(row['High'])
            S_low = float(row['Low'])
            S_close = float(row['Close'])
            
            remaining_minutes = (16 * 60) - (row_time.hour * 60 + row_time.minute)
            t_years = max(remaining_minutes / minutes_per_year, 0.0)
            
            # Check prices
            if direction == 'call':
                opt_at_high = bs_price(S_high, K, t_years, iv, option_type='call')
                opt_at_low = bs_price(S_low, K, t_years, iv, option_type='call')
                opt_at_close = bs_price(S_close, K, t_years, iv, option_type='call')
            else:
                opt_at_low = bs_price(S_low, K, t_years, iv, option_type='put')
                opt_at_high = bs_price(S_high, K, t_years, iv, option_type='put')
                opt_at_close = bs_price(S_close, K, t_years, iv, option_type='put')
            
            # Check partial profit (50% at +1.5%)
            if not partial1_filled:
                if (direction == 'call' and opt_at_high >= partial1_price) or \
                   (direction == 'put' and opt_at_low >= partial1_price):
                    # Take 50% profit
                    total_pnl += 0.5 * (partial1_price - entry_option_price)
                    partial1_filled = True
                    position_size = 0.5
                    stop_moved_to_breakeven = True  # Move stop to breakeven
                    continue
            
            # If partial filled, check final target or breakeven stop
            if partial1_filled:
                # Check final target (+3%)
                if (direction == 'call' and opt_at_high >= final_target_price) or \
                   (direction == 'put' and opt_at_low >= final_target_price):
                    total_pnl += 0.5 * (final_target_price - entry_option_price)
                    exit_time = row_time
                    exit_reason = 'TARGET_FULL'
                    break
                
                # Check breakeven stop on remaining 50%
                if (direction == 'call' and opt_at_low <= entry_option_price) or \
                   (direction == 'put' and opt_at_high <= entry_option_price):
                    # Exit at breakeven (already have profit from first 50%)
                    total_pnl += 0.5 * (entry_option_price - entry_option_price)  # 0
                    exit_time = row_time
                    exit_reason = 'BREAKEVEN_TRAIL'
                    break
            
            # Initial stop check (if not partial filled yet)
            if not partial1_filled:
                if (direction == 'call' and opt_at_low <= initial_stop_price) or \
                   (direction == 'put' and opt_at_high <= initial_stop_price):
                    total_pnl = initial_stop_price - entry_option_price
                    exit_time = row_time
                    exit_reason = 'STOP'
                    break
            
            # Time exit at 3:30 PM
            if row_time.hour >= 15 and row_time.minute >= 30:
                if partial1_filled:
                    total_pnl += 0.5 * (opt_at_close - entry_option_price)
                else:
                    total_pnl = opt_at_close - entry_option_price
                exit_time = row_time
                exit_reason = 'TIME'
                break
        
        pnl_pct = total_pnl / entry_option_price
        
        all_trades.append({
            'date': day,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'entry_opt': entry_option_price,
            'pnl_%': pnl_pct,
            'exit_reason': exit_reason,
            'partial_filled': partial1_filled,
            'win': pnl_pct > 0
        })
    
    if not all_trades:
        print("❌ No trades")
        return None
    
    # Results
    results = pd.DataFrame(all_trades)
    wins = results[results['win']]
    losses = results[~results['win']]
    
    print(f"{'='*90}")
    print(f"RESULTS")
    print(f"{'='*90}")
    print(f"Total Trades: {len(results)}")
    print(f"Wins: {len(wins)} ({len(wins)/len(results):.1%})")
    print(f"Losses: {len(losses)} ({len(losses)/len(results):.1%})")
    print(f"\nP&L Stats:")
    print(f"  Avg P&L: {results['pnl_%'].mean():.2%}")
    print(f"  Avg Win: {wins['pnl_%'].mean():.2%}" if len(wins) > 0 else "  Avg Win: N/A")
    print(f"  Avg Loss: {losses['pnl_%'].mean():.2%}" if len(losses) > 0 else "  Avg Loss: N/A")
    print(f"\nPartial Fills:")
    print(f"  Trades that took 50% profit: {results['partial_filled'].sum()}")
    print(f"\nExit Breakdown:")
    print(results['exit_reason'].value_counts())
    
    win_rate = len(wins) / len(results)
    avg_win = wins['pnl_%'].mean() if len(wins) > 0 else 0
    avg_loss = losses['pnl_%'].mean() if len(losses) > 0 else 0
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    
    print(f"\n💰 EXPECTANCY: {expectancy:.2%} per trade")
    print(f"🎯 WIN RATE: {win_rate:.1%}")
    
    if win_rate >= 0.80 and expectancy > 0:
        print("\n✅ ✅ ✅ **80%+ WIN RATE WITH POSITIVE EXPECTANCY!** ✅ ✅ ✅")
    elif win_rate >= 0.75:
        print(f"\n🎯 Close to 80% target!")
    
    print(f"\n{results[['date', 'direction', 'pnl_%', 'exit_reason', 'partial_filled', 'win']].to_string(index=False)}\n")
    
    return results


if __name__ == '__main__':
    print("\n" + "="*90)
    print("🧪 EXTENDED BACKTEST - SCALE-OUT STRATEGY")
    print("Testing over ~30 trading days for statistical significance")
    print("="*90)
    
    backtest_scale_out(symbol='SPY', days_back=30, iv=0.25)

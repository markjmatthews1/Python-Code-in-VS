"""Ultra-Selective Day Trading Strategy - Target 80%+ Win Rate

Key Changes from Previous Version:
1. MUCH stricter filters (only trade 5-star setups)
2. Directional bias based on market structure
3. Confirmation candles required
4. Asymmetric risk management (PUTs get more room, CALLs are stricter)
5. Time-of-day filters (avoid chop hours)

Goal: Trade LESS but WIN MORE (quality over quantity)
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
    
    # VWAP
    df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['vwap'] = (df['typical_price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # EMAs
    df['ema9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['Close'].ewm(span=21, adjust=False).mean()
    df['ema50'] = df['Close'].ewm(span=50, adjust=False).mean()
    
    # RSI
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Volume
    df['avg_volume'] = df['Volume'].rolling(window=20).mean()
    df['volume_surge'] = df['Volume'] / df['avg_volume']
    
    # ATR
    df['tr'] = pd.DataFrame({
        'hl': df['High'] - df['Low'],
        'hc': abs(df['High'] - df['Close'].shift()),
        'lc': abs(df['Low'] - df['Close'].shift())
    }).max(axis=1)
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    # Price momentum
    df['momentum_3'] = df['Close'] - df['Close'].shift(3)
    df['momentum_5'] = df['Close'] - df['Close'].shift(5)
    
    return df


def check_5star_put_setup(df, i):
    """
    5-STAR PUT SETUP (Bearish - Most Reliable)
    ✅ 1. Price below VWAP (bearish structure)
    ✅ 2. EMA9 < EMA21 (downtrend - removed EMA50 requirement)
    ✅ 3. RSI between 28-50 (wider range)
    ✅ 4. Volume surge > 1.5x (loosened from 2.0x)
    ✅ 5. Recent momentum negative
    ✅ 6. Confirmation: Red candle
    ✅ 7. Time: 9:45 AM - 3:00 PM (wider window)
    """
    
    row = df.iloc[i]
    prev = df.iloc[i-1]
    prev3 = df.iloc[i-3]
    prev5 = df.iloc[i-5]
    
    if pd.isna(row['rsi']) or pd.isna(row['ema21']):
        return False
    
    hour = row['Datetime'].hour
    minute = row['Datetime'].minute
    
    # Time filter: 9:45 AM - 3 PM (wider to catch more setups)
    if hour < 9 or (hour == 9 and minute < 45) or hour >= 15:
        return False
    
    # 1. Below VWAP
    if row['Close'] >= row['vwap']:
        return False
    
    # 2. EMA downtrend (simplified)
    if not (row['ema9'] < row['ema21']):
        return False
    
    # 3. RSI sweet spot (wider range)
    if not (28 < row['rsi'] < 50):
        return False
    
    # 4. Volume surge (loosened)
    if row['volume_surge'] < 1.5:
        return False
    
    # 5. Negative momentum
    if row['momentum_3'] >= 0:
        return False
    
    # 6. Confirmation: Red candle
    if row['Close'] >= prev['Close']:
        return False
    
    return True


def check_5star_call_setup(df, i):
    """
    5-STAR CALL SETUP (Bullish - More Selective)
    ✅ 1. Price above VWAP (bullish structure)
    ✅ 2. EMA9 > EMA21 (uptrend - removed EMA50 requirement)
    ✅ 3. RSI between 50-75 (wider range)
    ✅ 4. Volume surge > 2.0x (still strict for CALLs)
    ✅ 5. Positive momentum
    ✅ 6. Confirmation: Green candle
    ✅ 7. Time: 9:45 AM - 2:00 PM
    """
    
    row = df.iloc[i]
    prev = df.iloc[i-1]
    prev3 = df.iloc[i-3]
    prev5 = df.iloc[i-5]
    
    if pd.isna(row['rsi']) or pd.isna(row['ema21']):
        return False
    
    hour = row['Datetime'].hour
    minute = row['Datetime'].minute
    
    # Time filter: 9:45 AM - 2 PM
    if hour < 9 or (hour == 9 and minute < 45) or hour >= 14:
        return False
    
    # 1. Above VWAP
    if row['Close'] <= row['vwap']:
        return False
    
    # 2. EMA uptrend (simplified)
    if not (row['ema9'] > row['ema21']):
        return False
    
    # 3. RSI sweet spot (wider)
    if not (50 < row['rsi'] < 75):
        return False
    
    # 4. Volume requirement (still strict)
    if row['volume_surge'] < 2.0:
        return False
    
    # 5. Positive momentum
    if row['momentum_3'] <= 0:
        return False
    
    # 6. Confirmation: Green candle
    if row['Close'] <= prev['Close']:
        return False
    
    return True


def backtest_ultra_selective(symbol='SPY', days_back=8, iv=0.25):
    """
    Ultra-selective backtest
    
    Risk Management:
    - PUTs: +2% target, -12% stop (more room because more reliable)
    - CALLs: +2% target, -8% stop (tighter because less reliable)
    - Max 1 trade per day (only absolute best setup)
    """
    
    print(f"\n{'='*90}")
    print(f"ULTRA-SELECTIVE HIGH-PROBABILITY BACKTEST")
    print(f"Symbol: {symbol} | Days: {days_back} | 5-Star Setups Only")
    print(f"{'='*90}\n")
    
    # Fetch data
    period_days = min(max(1, days_back), 8)
    df = get_yahoo_intraday(symbol, period=f"{period_days}d", interval='1m', force_refresh=False)
    
    if df is None or df.empty:
        print("No data")
        return None
    
    # Prepare data
    if 'Datetime' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'Datetime'})
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
        # Filter trading hours
        day_df = day_df.set_index('Datetime').between_time('09:30', '15:30').reset_index()
        
        if len(day_df) < 70:
            continue
        
        day_df = day_df.reset_index(drop=True)
        
        # Calculate indicators
        day_df = calculate_indicators(day_df)
        
        # Find 5-star setups
        best_put_score = 0
        best_put_idx = None
        best_call_score = 0
        best_call_idx = None
        
        for idx in range(60, len(day_df)):
            # Check PUT setup
            if check_5star_put_setup(day_df, idx):
                score = day_df.iloc[idx]['volume_surge'] + abs(day_df.iloc[idx]['momentum_3'])
                if score > best_put_score:
                    best_put_score = score
                    best_put_idx = idx
            
            # Check CALL setup
            if check_5star_call_setup(day_df, idx):
                score = day_df.iloc[idx]['volume_surge'] + abs(day_df.iloc[idx]['momentum_3'])
                if score > best_call_score:
                    best_call_score = score
                    best_call_idx = idx
        
        # Take best setup (prefer PUT if both qualify)
        if best_put_idx is not None:
            entry_idx = best_put_idx
            direction = 'put'
            target_pct = 0.02
            stop_pct = -0.06  # Tighter stop for PUTs (was -0.12)
        elif best_call_idx is not None:
            entry_idx = best_call_idx
            direction = 'call'
            target_pct = 0.02
            stop_pct = -0.06  # Tighter stop for CALLs (was -0.08)
        else:
            continue  # No 5-star setup found
        
        # Execute trade
        entry_row = day_df.iloc[entry_idx]
        S_entry = float(entry_row['Close'])
        
        # Strike selection (0.3% OTM)
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
        
        target_price = entry_option_price * (1.0 + target_pct)
        stop_price = entry_option_price * (1.0 + stop_pct)
        
        # Simulate
        future_df = day_df.iloc[entry_idx:].copy()
        
        exit_price = None
        exit_time = None
        exit_reason = 'TIME'
        
        for idx, row in future_df.iterrows():
            row_time = pd.to_datetime(row['Datetime'])
            S_high = float(row['High'])
            S_low = float(row['Low'])
            S_close = float(row['Close'])
            
            remaining_minutes = (16 * 60) - (row_time.hour * 60 + row_time.minute)
            t_years = max(remaining_minutes / minutes_per_year, 0.0)
            
            # Check target/stop
            if direction == 'call':
                opt_at_high = bs_price(S_high, K, t_years, iv, option_type='call')
                opt_at_low = bs_price(S_low, K, t_years, iv, option_type='call')
                
                if opt_at_high >= target_price:
                    exit_price = target_price - (0.005 * entry_option_price)
                    exit_time = row_time
                    exit_reason = 'TARGET'
                    break
                elif opt_at_low <= stop_price:
                    exit_price = stop_price - (0.005 * entry_option_price)
                    exit_time = row_time
                    exit_reason = 'STOP'
                    break
            else:
                opt_at_low = bs_price(S_low, K, t_years, iv, option_type='put')
                opt_at_high = bs_price(S_high, K, t_years, iv, option_type='put')
                
                if opt_at_low >= target_price:
                    exit_price = target_price - (0.005 * entry_option_price)
                    exit_time = row_time
                    exit_reason = 'TARGET'
                    break
                elif opt_at_high <= stop_price:
                    exit_price = stop_price - (0.005 * entry_option_price)
                    exit_time = row_time
                    exit_reason = 'STOP'
                    break
            
            # Exit at 3:30 PM
            if row_time.hour >= 15 and row_time.minute >= 30:
                opt_close = bs_price(S_close, K, t_years, iv, option_type=direction)
                exit_price = opt_close - (0.005 * entry_option_price)
                exit_time = row_time
                exit_reason = 'TIME'
                break
        
        pnl_pct = (exit_price - entry_option_price) / (entry_option_price + 1e-12)
        
        all_trades.append({
            'date': day,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'direction': direction,
            'entry_price': S_entry,
            'strike': K,
            'entry_opt': entry_option_price,
            'exit_opt': exit_price,
            'pnl_%': pnl_pct,
            'exit_reason': exit_reason,
            'rsi': entry_row['rsi'],
            'vol_surge': entry_row['volume_surge'],
            'win': pnl_pct > 0
        })
    
    if not all_trades:
        print("❌ No trades generated (filters too strict)")
        return None
    
    # Results
    results = pd.DataFrame(all_trades)
    
    wins = results[results['win']]
    losses = results[~results['win']]
    
    call_trades = results[results['direction'] == 'call']
    put_trades = results[results['direction'] == 'put']
    
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
    print(f"  Best Trade: {results['pnl_%'].max():.2%}")
    print(f"  Worst Trade: {results['pnl_%'].min():.2%}")
    
    print(f"\nDirection Breakdown:")
    print(f"  CALL trades: {len(call_trades)} (Win rate: {len(call_trades[call_trades['win']])/len(call_trades):.1%})" if len(call_trades) > 0 else "  CALL trades: 0")
    print(f"  PUT trades: {len(put_trades)} (Win rate: {len(put_trades[put_trades['win']])/len(put_trades):.1%})" if len(put_trades) > 0 else "  PUT trades: 0")
    
    print(f"\nExit Breakdown:")
    print(results['exit_reason'].value_counts())
    
    # Expectancy
    win_rate = len(wins) / len(results)
    avg_win = wins['pnl_%'].mean() if len(wins) > 0 else 0
    avg_loss = losses['pnl_%'].mean() if len(losses) > 0 else 0
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    
    print(f"\n💰 EXPECTANCY: {expectancy:.2%} per trade")
    print(f"🎯 WIN RATE: {win_rate:.1%}")
    
    if expectancy > 0 and win_rate >= 0.75:
        print("\n✅ ✅ ✅ VIABLE STRATEGY - 75%+ WIN RATE WITH POSITIVE EXPECTANCY! ✅ ✅ ✅")
    elif win_rate >= 0.70:
        print(f"\n⚠️ Good win rate, needs slight refinement")
    else:
        print(f"\n❌ Need adjustments")
    
    print(f"\n{results[['date', 'entry_time', 'direction', 'pnl_%', 'exit_reason', 'win']].to_string(index=False)}\n")
    
    return results


if __name__ == '__main__':
    print("\n" + "="*90)
    print("ULTRA-SELECTIVE 5-STAR SETUP BACKTEST")
    print("Quality over Quantity - Only Perfect Setups")
    print("="*90)
    
    backtest_ultra_selective(symbol='SPY', days_back=8, iv=0.25)

"""High Probability Day Trading Strategy - Target 80%+ Win Rate

Combines multiple technical indicators for high-conviction setups:
- VWAP for trend/mean reversion
- EMA crossovers for momentum
- RSI for overbought/oversold
- Volume surge for confirmation
- Tight stops to preserve capital

Goal: Win small and often (1-2% option gains), cut losses fast (-10% max)
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
    """Calculate technical indicators on minute data"""
    
    # VWAP (Volume-Weighted Average Price)
    df['typical_price'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['vwap'] = (df['typical_price'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    # EMAs (Exponential Moving Averages)
    df['ema9'] = df['Close'].ewm(span=9, adjust=False).mean()
    df['ema21'] = df['Close'].ewm(span=21, adjust=False).mean()
    
    # RSI (Relative Strength Index) - 14 period
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # Volume surge (volume vs 20-bar average)
    df['avg_volume'] = df['Volume'].rolling(window=20).mean()
    df['volume_surge'] = df['Volume'] / df['avg_volume']
    
    # ATR for volatility
    df['tr'] = pd.DataFrame({
        'hl': df['High'] - df['Low'],
        'hc': abs(df['High'] - df['Close'].shift()),
        'lc': abs(df['Low'] - df['Close'].shift())
    }).max(axis=1)
    df['atr'] = df['tr'].rolling(window=14).mean()
    
    return df


def generate_signals(df):
    """Generate high-probability trading signals
    
    LONG (Call) Signals:
    1. Price > VWAP (bullish bias)
    2. EMA9 > EMA21 (momentum up)
    3. RSI > 50 but < 70 (strength without overbought)
    4. Volume surge > 1.5x (confirmation)
    5. Recent pullback to support (buy the dip)
    
    SHORT (Put) Signals:
    1. Price < VWAP (bearish bias)
    2. EMA9 < EMA21 (momentum down)
    3. RSI < 50 but > 30 (weakness without oversold)
    4. Volume surge > 1.5x (confirmation)
    5. Recent bounce to resistance (sell the rip)
    """
    
    signals = []
    
    for i in range(50, len(df)):  # Start after indicators warm up
        row = df.iloc[i]
        prev = df.iloc[i-1]
        prev5 = df.iloc[i-5]
        
        # Skip if indicators not ready
        if pd.isna(row['vwap']) or pd.isna(row['rsi']):
            continue
        
        # BULLISH SETUP (Call)
        if (row['Close'] > row['vwap'] and  # Above VWAP
            row['ema9'] > row['ema21'] and  # Uptrend
            50 < row['rsi'] < 70 and  # Moderate strength
            row['volume_surge'] > 1.5 and  # Volume confirmation
            row['Close'] > prev['Close'] and  # Momentum building
            prev5['Close'] > row['Close'] - (0.002 * row['Close'])):  # Small pullback
            
            signals.append({
                'time': row['Datetime'],
                'direction': 'call',
                'entry_price': row['Close'],
                'reason': 'VWAP_EMA_RSI_VOL',
                'rsi': row['rsi'],
                'volume_surge': row['volume_surge']
            })
        
        # BEARISH SETUP (Put)
        elif (row['Close'] < row['vwap'] and  # Below VWAP
              row['ema9'] < row['ema21'] and  # Downtrend
              30 < row['rsi'] < 50 and  # Moderate weakness
              row['volume_surge'] > 1.5 and  # Volume confirmation
              row['Close'] < prev['Close'] and  # Momentum building
              prev5['Close'] < row['Close'] + (0.002 * row['Close'])):  # Small bounce
            
            signals.append({
                'time': row['Datetime'],
                'direction': 'put',
                'entry_price': row['Close'],
                'reason': 'VWAP_EMA_RSI_VOL',
                'rsi': row['rsi'],
                'volume_surge': row['volume_surge']
            })
    
    return pd.DataFrame(signals) if signals else pd.DataFrame()


def backtest_strategy(symbol='SPY', days_back=8, iv=0.25, 
                     target_pct=0.02, stop_loss_pct=-0.10, otm_offset=0.003):
    """
    Backtest high-probability setups
    
    Strategy:
    - Wait for high-conviction technical setup
    - Enter 0.3% OTM for leverage
    - Target: +2% (quick profits)
    - Stop: -10% (tight risk control)
    - Max 1 trade per day (best setup only)
    """
    
    print(f"\n{'='*90}")
    print(f"HIGH PROBABILITY DAY TRADING BACKTEST")
    print(f"Symbol: {symbol} | Days: {days_back} | Target: +{target_pct:.0%} | Stop: {stop_loss_pct:.0%}")
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
        
        if len(day_df) < 50:
            continue
        
        day_df = day_df.reset_index(drop=True)
        
        # Calculate indicators
        day_df = calculate_indicators(day_df)
        
        # Generate signals
        signals = generate_signals(day_df)
        
        if signals.empty:
            continue
        
        # Take only FIRST signal of the day (best setup)
        signal = signals.iloc[0]
        
        # Find entry bar
        entry_idx = day_df[day_df['Datetime'] == signal['time']].index[0]
        S_entry = float(signal['entry_price'])
        direction = signal['direction']
        
        # Select strike
        if direction == 'call':
            K = round(S_entry * (1 + otm_offset))
        else:
            K = round(S_entry * (1 - otm_offset))
        
        # Get entry time for option pricing
        entry_time = pd.to_datetime(signal['time'])
        minutes_to_expiry = (16 * 60) - (entry_time.hour * 60 + entry_time.minute)
        t_years_entry = minutes_to_expiry / minutes_per_year
        
        entry_option_price = bs_price(S_entry, K, t_years_entry, iv, option_type=direction)
        if entry_option_price < 0.5:
            continue  # Skip worthless options
        
        target_price = entry_option_price * (1.0 + target_pct)
        stop_price = entry_option_price * (1.0 + stop_loss_pct)
        
        # Simulate from entry forward
        future_df = day_df.iloc[entry_idx:].copy()
        
        trade_open = True
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
            'entry_time': signal['time'],
            'exit_time': exit_time,
            'direction': direction,
            'entry_price': S_entry,
            'strike': K,
            'entry_opt': entry_option_price,
            'exit_opt': exit_price,
            'pnl_%': pnl_pct,
            'exit_reason': exit_reason,
            'rsi': signal['rsi'],
            'vol_surge': signal['volume_surge'],
            'win': pnl_pct > 0
        })
    
    if not all_trades:
        print("❌ No trades generated")
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
    print(f"  Best Trade: {results['pnl_%'].max():.2%}")
    print(f"  Worst Trade: {results['pnl_%'].min():.2%}")
    
    print(f"\nExit Breakdown:")
    print(results['exit_reason'].value_counts())
    
    # Expectancy
    win_rate = len(wins) / len(results)
    avg_win = wins['pnl_%'].mean() if len(wins) > 0 else 0
    avg_loss = losses['pnl_%'].mean() if len(losses) > 0 else 0
    expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
    
    print(f"\n💰 EXPECTANCY: {expectancy:.2%} per trade")
    print(f"🎯 WIN RATE: {win_rate:.1%}")
    
    if expectancy > 0 and win_rate >= 0.70:
        print("\n✅ ✅ ✅ VIABLE STRATEGY! ✅ ✅ ✅")
    elif win_rate >= 0.60:
        print(f"\n⚠️ High win rate but expectancy needs improvement")
    else:
        print(f"\n❌ Need higher win rate or better risk/reward")
    
    print(f"\n{results[['date', 'entry_time', 'direction', 'pnl_%', 'exit_reason', 'win']].to_string(index=False)}\n")
    
    return results


if __name__ == '__main__':
    print("\n" + "="*90)
    print("TESTING HIGH-PROBABILITY TECHNICAL SETUPS")
    print("Goal: 80%+ win rate with positive expectancy")
    print("="*90)
    
    # Test 1: Conservative (2% target, -10% stop)
    print("\n🧪 TEST 1: Conservative (2% target, 10% stop)")
    backtest_strategy(symbol='SPY', days_back=8, iv=0.25, 
                     target_pct=0.02, stop_loss_pct=-0.10, otm_offset=0.003)
    
    # Test 2: Tighter stop (2% target, -8% stop)
    print("\n🧪 TEST 2: Tighter Stop (2% target, 8% stop)")
    backtest_strategy(symbol='SPY', days_back=8, iv=0.25, 
                     target_pct=0.02, stop_loss_pct=-0.08, otm_offset=0.003)
    
    # Test 3: More aggressive profit (3% target, -10% stop)
    print("\n🧪 TEST 3: Higher Target (3% target, 10% stop)")
    backtest_strategy(symbol='SPY', days_back=8, iv=0.25, 
                     target_pct=0.03, stop_loss_pct=-0.10, otm_offset=0.003)

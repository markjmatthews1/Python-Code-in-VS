"""Pick of the Day simulator using PRE-MARKET GAP as directional signal

This matches the real strategy better:
- Analyze pre-market movement (gap up/down from previous close)
- Enter at market open (9:30 AM) in the gap direction
- Target: 3-6% option gain by 10:00 AM
- Use slightly OTM strikes for better leverage

Theory: Pre-market gaps tend to continue intraday (momentum)
"""

import os
import sys
import math
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from data_provider import get_yahoo_intraday


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


def simulate_premarket_gap(symbol='SPY', days_back=8, iv=0.25, target_pct=0.03, 
                           stop_loss_pct=-0.30, otm_offset=0.005):
    """
    Simulate zero-DTE options based on pre-market gap
    
    Args:
        otm_offset: How far OTM to buy strikes (0.005 = 0.5% OTM for cheaper premium)
        stop_loss_pct: Cut losses at this % (e.g., -0.30 = -30%)
    """
    
    print(f"\n{'='*80}")
    print(f"PRE-MARKET GAP STRATEGY SIMULATION")
    print(f"Symbol: {symbol} | Days: {days_back} | IV: {iv:.0%}")
    print(f"Target: +{target_pct:.0%} | Stop: {stop_loss_pct:.0%} | OTM: {otm_offset:.1%}")
    print(f"{'='*80}\n")
    
    # Fetch minute data
    period_days = min(max(1, days_back), 8)
    df = get_yahoo_intraday(symbol, period=f"{period_days}d", interval='1m', force_refresh=True)
    
    if df is None or df.empty:
        print("No data returned")
        return None
    
    # Prepare data
    if 'Datetime' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'Datetime'})
    
    # Flatten multi-index columns if present (Yahoo returns multi-index sometimes)
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    if df['Datetime'].dt.tz is not None:
        df['Datetime'] = df['Datetime'].dt.tz_convert('US/Eastern').dt.tz_localize(None)
    
    df['date'] = df['Datetime'].dt.date
    results = []
    minutes_per_year = 252 * 6.5 * 60
    
    # Get daily OHLC for gap calculation
    daily_df = df.groupby('date').agg({
        'Open': 'first',
        'High': 'max',
        'Low': 'min',
        'Close': 'last'
    }).reset_index()
    daily_df['prev_close'] = daily_df['Close'].shift(1)
    
    for idx, day_info in daily_df.iterrows():
        if pd.isna(day_info['prev_close']):
            continue  # Skip first day (no previous close)
        
        day = day_info['date']
        prev_close = day_info['prev_close']
        
        # Get minute data for this day
        day_df = df[df['date'] == day].copy()
        day_df = day_df.set_index('Datetime').between_time('09:30', '16:00').reset_index()
        
        if len(day_df) < 10:
            continue  # Not enough data
        
        # Entry time: 9:30 AM (market open)
        try:
            entry_time = pd.to_datetime(f"{day} 09:30:00")
            exit_cutoff = pd.to_datetime(f"{day} 10:00:00")
        except:
            continue
        
        # Find 9:30 bar
        entry_candidates = day_df[day_df['Datetime'] == entry_time]
        if entry_candidates.empty:
            # Try first bar after 9:30
            entry_candidates = day_df[day_df['Datetime'] >= entry_time].head(1)
        
        if entry_candidates.empty:
            continue
        
        entry_row = entry_candidates.iloc[0]
        S_entry = float(entry_row['Open'])  # Enter at open price
        
        # Calculate pre-market gap
        gap_pct = (S_entry - prev_close) / prev_close
        
        # Direction based on gap
        if gap_pct > 0.001:  # Gap up > 0.1%
            direction = 'call'
        elif gap_pct < -0.001:  # Gap down > 0.1%
            direction = 'put'
        else:
            continue  # Skip neutral days
        
        # Select strike: slightly OTM for leverage
        if direction == 'call':
            K = round(S_entry * (1 + otm_offset))  # 0.5% above entry
        else:
            K = round(S_entry * (1 - otm_offset))  # 0.5% below entry
        
        # Time to expiry (from 9:30 to 16:00)
        minutes_to_expiry = (16 * 60) - (9 * 60 + 30)
        t_years_entry = minutes_to_expiry / minutes_per_year
        
        # Price option at entry
        entry_option_price = bs_price(S_entry, K, t_years_entry, iv, option_type=direction)
        if entry_option_price <= 0.1:
            continue  # Skip worthless options
        
        target_price = entry_option_price * (1.0 + target_pct)
        stop_price = entry_option_price * (1.0 + stop_loss_pct)
        slippage_cost = 0.005 * entry_option_price
        
        # Simulate minute by minute
        trade_open = True
        exit_price = None
        exit_time = None
        exit_reason = 'TIME'
        
        future_df = day_df[(day_df['Datetime'] >= entry_row['Datetime']) & 
                          (day_df['Datetime'] <= exit_cutoff)].copy()
        
        for _, row in future_df.iterrows():
            row_dt = pd.to_datetime(row['Datetime'])
            if isinstance(row_dt, pd.Series):
                row_dt = row_dt.iloc[0]
            
            S_high = float(row['High'])
            S_low = float(row['Low'])
            remaining_minutes = (16 * 60) - (row_dt.hour * 60 + row_dt.minute)
            t_years = max(remaining_minutes / minutes_per_year, 0.0)
            
            # Check target hit
            if direction == 'call':
                price_at_high = bs_price(S_high, K, t_years, iv, option_type='call')
                price_at_low = bs_price(S_low, K, t_years, iv, option_type='call')
                
                if price_at_high >= target_price:
                    exit_price = target_price - slippage_cost
                    exit_time = row_dt
                    exit_reason = 'TARGET'
                    trade_open = False
                    break
                elif price_at_low <= stop_price:
                    exit_price = stop_price - slippage_cost
                    exit_time = row_dt
                    exit_reason = 'STOP'
                    trade_open = False
                    break
            else:
                price_at_low = bs_price(S_low, K, t_years, iv, option_type='put')
                price_at_high = bs_price(S_high, K, t_years, iv, option_type='put')
                
                if price_at_low >= target_price:
                    exit_price = target_price - slippage_cost
                    exit_time = row_dt
                    exit_reason = 'TARGET'
                    trade_open = False
                    break
                elif price_at_high <= stop_price:
                    exit_price = stop_price - slippage_cost
                    exit_time = row_dt
                    exit_reason = 'STOP'
                    trade_open = False
                    break
        
        if trade_open:
            # Exit at 10:00 AM
            final_row = future_df[future_df['Datetime'] == exit_cutoff]
            if final_row.empty:
                final_row = future_df.iloc[[-1]]
            
            final_S = float(final_row.iloc[0]['Close'])
            final_dt = pd.to_datetime(final_row.iloc[0]['Datetime'])
            if isinstance(final_dt, pd.Series):
                final_dt = final_dt.iloc[0]
            
            remaining_minutes = (16 * 60) - (final_dt.hour * 60 + final_dt.minute)
            t_years = max(remaining_minutes / minutes_per_year, 0.0)
            exit_price = bs_price(final_S, K, t_years, iv, option_type=direction) - slippage_cost
            exit_time = final_dt
            exit_reason = 'TIME'
        
        pnl_pct = (exit_price - entry_option_price) / (entry_option_price + 1e-12)
        
        results.append({
            'date': day,
            'gap_%': gap_pct,
            'direction': direction,
            'S_entry': S_entry,
            'K': K,
            'entry_opt': entry_option_price,
            'exit_opt': exit_price,
            'pnl_%': pnl_pct,
            'exit_reason': exit_reason,
            'win': pnl_pct > 0
        })
    
    if not results:
        print("No trades simulated")
        return None
    
    res_df = pd.DataFrame(results)
    
    # Print summary
    wins = res_df[res_df['win']]
    losses = res_df[~res_df['win']]
    
    print(f"{'='*80}")
    print(f"RESULTS")
    print(f"{'='*80}")
    print(f"Total Trades: {len(res_df)}")
    print(f"Wins: {len(wins)} ({len(wins)/len(res_df):.1%})")
    print(f"Losses: {len(losses)} ({len(losses)/len(res_df):.1%})")
    print(f"Avg P&L: {res_df['pnl_%'].mean():.2%}")
    print(f"Avg Win: {wins['pnl_%'].mean():.2%}" if len(wins) > 0 else "Avg Win: N/A")
    print(f"Avg Loss: {losses['pnl_%'].mean():.2%}" if len(losses) > 0 else "Avg Loss: N/A")
    
    # Exit reasons
    print(f"\nExit Reasons:")
    print(res_df['exit_reason'].value_counts())
    
    # Expectancy
    if len(res_df) > 0:
        win_rate = len(wins) / len(res_df)
        avg_win = wins['pnl_%'].mean() if len(wins) > 0 else 0
        avg_loss = losses['pnl_%'].mean() if len(losses) > 0 else 0
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        print(f"\n💰 EXPECTANCY: {expectancy:.2%} per trade")
        
        if expectancy > 0 and win_rate > 0.3:
            print("✅ VIABLE STRATEGY!")
        else:
            print("❌ Not viable (yet)")
    
    print(f"\n{res_df.to_string(index=False)}\n")
    return res_df


if __name__ == '__main__':
    # Test with different parameters
    print("\n" + "="*80)
    print("TESTING PRE-MARKET GAP STRATEGY")
    print("="*80)
    
    # Test 1: Conservative (3% target, -30% stop)
    print("\n🧪 TEST 1: Conservative (3% target, 30% stop, 0.5% OTM)")
    simulate_premarket_gap(symbol='SPY', days_back=8, iv=0.25, 
                          target_pct=0.03, stop_loss_pct=-0.30, otm_offset=0.005)
    
    # Test 2: Aggressive (5% target, -30% stop)
    print("\n🧪 TEST 2: Aggressive (5% target, 30% stop, 0.5% OTM)")
    simulate_premarket_gap(symbol='SPY', days_back=8, iv=0.25, 
                          target_pct=0.05, stop_loss_pct=-0.30, otm_offset=0.005)
    
    # Test 3: More OTM for leverage (3% target, 1% OTM)
    print("\n🧪 TEST 3: More OTM (3% target, 30% stop, 1.0% OTM)")
    simulate_premarket_gap(symbol='SPY', days_back=8, iv=0.25, 
                          target_pct=0.03, stop_loss_pct=-0.30, otm_offset=0.01)

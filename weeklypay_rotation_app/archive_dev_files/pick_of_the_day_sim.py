"""Simple Pick-of-the-Day zero-DTE options simulator (approximation)

This script approximates SPY zero-DTE ATM option trades entered at 9:35 AM ET
and exits at a +6% option price gain or at 10:00 AM, whichever comes first.

Notes / approximations:
- Uses minute SPY prices from Yahoo (via data_provider.get_yahoo_intraday).
- Prices ATM option using Black-Scholes with a constant implied vol (configurable).
- Assumes constant IV during the short test window and no bid/ask spread (small slippage applied).
- Treats an option "hit" if the option price computed at the minute's High (for calls) or Low (for puts)
  reaches the target price.

This is a research/proof-of-concept script, not a production trading system.
"""

import os
import sys
import math
from datetime import datetime, time as dt_time
import pandas as pd
import numpy as np

# Ensure repo root is importable
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.append(ROOT)

from data_provider import get_yahoo_intraday


def bs_price(S, K, t_years, sigma, r=0.0, option_type='call'):
    """Black-Scholes European option price (no dividends).
    S: spot, K: strike, t_years: time to expiry in years, sigma: vol
    r: risk-free rate (default 0)
    """
    if t_years <= 0:
        # At expiry, option value is intrinsic
        if option_type == 'call':
            return max(0.0, S - K)
        else:
            return max(0.0, K - S)

    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * t_years) / (sigma * math.sqrt(t_years))
    d2 = d1 - sigma * math.sqrt(t_years)
    from math import erf, sqrt
    # CDF of normal
    def N(x):
        return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))

    if option_type == 'call':
        price = S * N(d1) - K * math.exp(-r * t_years) * N(d2)
    else:
        price = K * math.exp(-r * t_years) * N(-d2) - S * N(-d1)
    return max(price, 0.0)


def compute_vwap(df):
    # df expected to have columns: High, Low, Close, Volume
    typical = (df['High'] + df['Low'] + df['Close']) / 3.0
    vwap = (typical * df['Volume']).sum() / (df['Volume'].sum() + 1e-9)
    return vwap


def simulate(symbol='SPY', days_back=10, iv=0.25, target_pct=0.06, slippage_pct=0.005):
    print(f"Fetching minute data for {symbol} (this may take a moment)...")
    # Yahoo allows at most ~8 days of 1m data per request; cap period accordingly
    period_days = min(max(1, days_back), 8)
    # Force refresh to avoid stale/corrupt cache issues
    df = get_yahoo_intraday(symbol, period=f"{period_days}d", interval='1m', force_refresh=True)
    if df is None or df.empty:
        print("No minute data returned")
        return

    # Ensure Datetime column and timezone naive handling
    if 'Datetime' not in df.columns:
        df = df.reset_index().rename(columns={'index': 'Datetime'})
    df['Datetime'] = pd.to_datetime(df['Datetime'])
    # Convert to US/Eastern if tz-aware
    if df['Datetime'].dt.tz is not None:
        df['Datetime'] = df['Datetime'].dt.tz_convert('US/Eastern').dt.tz_localize(None)

    df['date'] = df['Datetime'].dt.date
    results = []

    minutes_per_year = 252 * 6.5 * 60

    for day, g in df.groupby('date'):
        day_df = g.set_index('Datetime').between_time('09:00', '16:00').reset_index()
        # Need data at/after 9:30 and through 10:00
        try:
            entry_time = pd.to_datetime(f"{day} 09:35:00")
            exit_cutoff = pd.to_datetime(f"{day} 10:00:00")
        except Exception:
            continue

        if entry_time not in day_df['Datetime'].values:
            # skip days without a 9:35 bar
            continue

        # compute VWAP over first 6 minutes (9:30 -> 9:35 inclusive of 9:30-9:35)
        vwap_window = day_df[(day_df['Datetime'] >= pd.to_datetime(f"{day} 09:30:00")) & (day_df['Datetime'] <= entry_time)]
        if vwap_window.empty:
            continue
        vwap = compute_vwap(vwap_window)

        entry_row = day_df[day_df['Datetime'] == entry_time].iloc[0]
        S_entry = float(entry_row['Close'])
        # Ensure numeric comparison
        vwap_val = float(vwap)
        direction = 'call' if float(S_entry) > vwap_val else 'put'

        # Select ATM strike as nearest dollar
        K = round(S_entry)

        # time to expiry in minutes from entry to market close (16:00)
        minutes_to_expiry = (16 * 60) - (9 * 60 + 35)
        if minutes_to_expiry <= 0:
            continue

        t_years_entry = minutes_to_expiry / minutes_per_year
        entry_option_price = bs_price(S_entry, K, t_years_entry, iv, r=0.0, option_type=direction)
        if entry_option_price <= 0:
            # skip free/zero-priced options
            continue

        target_price = entry_option_price * (1.0 + target_pct)
        slippage_cost = slippage_pct * entry_option_price

        # simulate minute by minute until exit_cutoff
        trade_open = True
        exit_price = None
        exit_time = None

        future_df = day_df[(day_df['Datetime'] >= entry_time) & (day_df['Datetime'] <= exit_cutoff)].copy()
        # iterate subsequent minutes including entry minute
        for _, row in future_df.iterrows():
            S_high = float(row['High'])
            S_low = float(row['Low'])
            # robustly parse timestamp from row['Datetime']
            row_dt = pd.to_datetime(row['Datetime'])
            if isinstance(row_dt, pd.Series):
                row_dt = row_dt.iloc[0]
            remaining_minutes = (16 * 60) - (row_dt.hour * 60 + row_dt.minute)
            t_years = max(remaining_minutes / minutes_per_year, 0.0)

            # Check if target hit within this minute using High (for calls) or Low (for puts)
            if direction == 'call':
                price_at_high = bs_price(S_high, K, t_years, iv, option_type='call')
                if price_at_high >= target_price:
                    # record hit at this minute - approximate exit price as target_price
                    exit_price = target_price - slippage_cost
                    exit_time = row['Datetime']
                    trade_open = False
                    break
            else:
                price_at_low = bs_price(S_low, K, t_years, iv, option_type='put')
                if price_at_low >= target_price:
                    exit_price = target_price - slippage_cost
                    exit_time = row['Datetime']
                    trade_open = False
                    break

        if trade_open:
            # exit at close of cutoff minute
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
            exit_time = final_row.iloc[0]['Datetime']

        pnl_pct = (exit_price - entry_option_price) / (entry_option_price + 1e-12)

        results.append({
            'date': day,
            'direction': direction,
            'S_entry': S_entry,
            'K': K,
            'entry_option_price': entry_option_price,
            'exit_price': exit_price,
            'entry_time': entry_time,
            'exit_time': exit_time,
            'pnl_pct': pnl_pct,
            'hit_target': pnl_pct >= target_pct - 1e-9
        })

    if not results:
        print("No trades simulated (insufficient data)")
        return

    res_df = pd.DataFrame(results)
    wins = res_df[res_df['hit_target']]
    loss = res_df[~res_df['hit_target']]
    print(f"Simulated {len(res_df)} trades. Wins: {len(wins)} ({len(wins)/len(res_df):.1%}). Avg P&L: {res_df['pnl_pct'].mean():.2%}")
    print(res_df[['date','direction','S_entry','K','entry_option_price','exit_price','pnl_pct','hit_target']])
    return res_df


if __name__ == '__main__':
    simulate(days_back=10, iv=0.25, target_pct=0.06, slippage_pct=0.005)

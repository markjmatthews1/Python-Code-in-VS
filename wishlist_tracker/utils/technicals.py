"""
utils/technicals.py
-------------------
Technical indicator calculations for Wishlist Tracker App.

Supported indicators: SMA, EMA, RSI, MACD, Fibonacci levels, Pivot Points.
Configurable via config/technicals_setup.ini
"""
import pandas as pd
import numpy as np

# --- SMA ---
def sma(series, period):
    return series.rolling(window=period).mean()

# --- EMA ---
def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

# --- RSI ---
def rsi(series, period):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

# --- MACD ---
def macd(series, fast=12, slow=26, signal=9):
    ema_fast = ema(series, fast)
    ema_slow = ema(series, slow)
    macd_line = ema_fast - ema_slow
    signal_line = ema(macd_line, signal)
    hist = macd_line - signal_line
    return macd_line, signal_line, hist

# --- Fibonacci Retracement Levels ---
def fibonacci_levels(series, lookback_days=20):
    high = series[-lookback_days:].max()
    low = series[-lookback_days:].min()
    diff = high - low
    levels = {
        '0.0%': high,
        '23.6%': high - 0.236 * diff,
        '38.2%': high - 0.382 * diff,
        '50.0%': high - 0.5 * diff,
        '61.8%': high - 0.618 * diff,
        '100.0%': low
    }
    return levels

# --- Pivot Points (Classic) ---
def pivot_points(df, method='classic'):
    # df must have columns: ['high', 'low', 'close']
    if method == 'classic':
        high = df['high'].iloc[-2]
        low = df['low'].iloc[-2]
        close = df['close'].iloc[-2]
        pivot = (high + low + close) / 3
        r1 = 2 * pivot - low
        s1 = 2 * pivot - high
        r2 = pivot + (high - low)
        s2 = pivot - (high - low)
        return {'pivot': pivot, 'r1': r1, 's1': s1, 'r2': r2, 's2': s2}
    # Add more methods if needed
    return {}

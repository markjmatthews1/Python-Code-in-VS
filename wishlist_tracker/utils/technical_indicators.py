"""
Technical Indicators Calculator
Implements Moving Averages, RSI, MACD, and Volume Analysis for trend scoring.
"""

import pandas as pd
import numpy as np


def calculate_sma(prices, period):
    """
    Calculate Simple Moving Average.
    
    Args:
        prices: Series of closing prices
        period: Number of periods for SMA
        
    Returns:
        Series with SMA values
    """
    return prices.rolling(window=period, min_periods=period).mean()


def calculate_ema(prices, period):
    """
    Calculate Exponential Moving Average.
    
    Args:
        prices: Series of closing prices
        period: Number of periods for EMA
        
    Returns:
        Series with EMA values
    """
    return prices.ewm(span=period, adjust=False).mean()


def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI).
    
    Args:
        prices: Series of closing prices
        period: RSI period (default 14)
        
    Returns:
        float: Current RSI value (0-100)
    """
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    delta = prices.diff()
    
    # Separate gains and losses
    gains = delta.where(delta > 0, 0.0)
    losses = -delta.where(delta < 0, 0.0)
    
    # Calculate average gains and losses
    avg_gain = gains.rolling(window=period, min_periods=period).mean()
    avg_loss = losses.rolling(window=period, min_periods=period).mean()
    
    # Calculate RS and RSI
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    # Return most recent RSI value
    return rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else None


def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence).
    
    Args:
        prices: Series of closing prices
        fast: Fast EMA period (default 12)
        slow: Slow EMA period (default 26)
        signal: Signal line EMA period (default 9)
        
    Returns:
        dict: {
            'macd': Current MACD value,
            'signal': Current signal line value,
            'histogram': Current histogram value,
            'trend': 'BULLISH' / 'BEARISH' / 'NEUTRAL'
        }
    """
    if len(prices) < slow + signal:
        return None
    
    # Calculate MACD line and signal line
    ema_fast = calculate_ema(prices, fast)
    ema_slow = calculate_ema(prices, slow)
    macd_line = ema_fast - ema_slow
    signal_line = calculate_ema(macd_line, signal)
    histogram = macd_line - signal_line
    
    # Get current values
    macd_current = macd_line.iloc[-1]
    signal_current = signal_line.iloc[-1]
    histogram_current = histogram.iloc[-1]
    
    # Determine trend
    if pd.isna(macd_current) or pd.isna(signal_current):
        return None
    
    if macd_current > signal_current:
        trend = 'BULLISH'
    elif macd_current < signal_current:
        trend = 'BEARISH'
    else:
        trend = 'NEUTRAL'
    
    return {
        'macd': macd_current,
        'signal': signal_current,
        'histogram': histogram_current,
        'trend': trend
    }


def analyze_volume(volumes, period=20):
    """
    Analyze volume vs average.
    
    Args:
        volumes: Series of volume data
        period: Period for average volume calculation (default 20)
        
    Returns:
        dict: {
            'current': Current volume,
            'average': 20-day average volume,
            'ratio': Current / Average ratio,
            'strength': 'SURGE' / 'STRONG' / 'AVERAGE' / 'WEAK' / 'LOW'
        }
    """
    if len(volumes) < period:
        return None
    
    current_volume = volumes.iloc[-1]
    avg_volume = volumes.tail(period).mean()
    
    if avg_volume == 0:
        return None
    
    ratio = current_volume / avg_volume
    
    # Categorize volume strength
    if ratio >= 1.5:
        strength = 'SURGE'
    elif ratio >= 1.0:
        strength = 'STRONG'
    elif ratio >= 0.8:
        strength = 'AVERAGE'
    elif ratio >= 0.5:
        strength = 'WEAK'
    else:
        strength = 'LOW'
    
    return {
        'current': int(current_volume),
        'average': int(avg_volume),
        'ratio': ratio,
        'strength': strength
    }


def score_moving_averages(current_price, sma_20, sma_50, sma_200):
    """
    Score moving average alignment (0-30 points).
    
    Args:
        current_price: Current stock price
        sma_20, sma_50, sma_200: Moving average values
        
    Returns:
        dict: {'score': int, 'alignment': str, 'signals': list}
    """
    signals = []
    
    # Check for None values
    if any(pd.isna(x) or x is None for x in [current_price, sma_20, sma_50]):
        return {'score': 0, 'alignment': 'INSUFFICIENT_DATA', 'signals': ['Insufficient MA data']}
    
    # STRONG UPTREND: Price > SMA-20 > SMA-50 > SMA-200 (all aligned)
    if (current_price > sma_20 and sma_20 > sma_50 and 
        (sma_200 is None or pd.isna(sma_200) or sma_50 > sma_200)):
        score = 30
        alignment = 'STRONG_UPTREND'
        signals.append('Price > SMA-20 > SMA-50')
        if not (sma_200 is None or pd.isna(sma_200)):
            signals.append('SMA-50 > SMA-200 (golden cross)')
    
    # UPTREND: Price > SMA-20 and SMA-20 > SMA-50
    elif current_price > sma_20 and sma_20 > sma_50:
        score = 20
        alignment = 'UPTREND'
        signals.append('Price > SMA-20 > SMA-50')
    
    # WEAK UPTREND: Price > SMA-20 but SMA-20 < SMA-50
    elif current_price > sma_20:
        score = 10
        alignment = 'WEAK_UPTREND'
        signals.append('Price > SMA-20 (short-term positive)')
        signals.append('SMA-20 < SMA-50 (resistance above)')
    
    # NEUTRAL: Price between SMA-20 and SMA-50
    elif current_price > sma_50:
        score = 5
        alignment = 'NEUTRAL'
        signals.append('Price between SMA-20 and SMA-50')
    
    # DOWNTREND: Price < SMA-20 < SMA-50
    else:
        score = 0
        alignment = 'DOWNTREND'
        signals.append('Price < SMA-20 (short-term negative)')
    
    return {
        'score': score,
        'alignment': alignment,
        'signals': signals
    }


def score_rsi(rsi_value):
    """
    Score RSI momentum (0-30 points).
    
    Args:
        rsi_value: Current RSI (0-100)
        
    Returns:
        dict: {'score': int, 'status': str, 'signals': list}
    """
    if rsi_value is None or pd.isna(rsi_value):
        return {'score': 0, 'status': 'INSUFFICIENT_DATA', 'signals': ['Insufficient RSI data']}
    
    signals = []
    
    # Bullish: 50 < RSI < 70 (healthy uptrend)
    if 50 < rsi_value < 70:
        score = 30
        status = 'BULLISH'
        signals.append(f'RSI {rsi_value:.1f} in bullish range (50-70)')
    
    # Neutral: 40 < RSI < 50
    elif 40 < rsi_value <= 50:
        score = 20
        status = 'NEUTRAL'
        signals.append(f'RSI {rsi_value:.1f} neutral (40-50)')
    
    # Overbought (caution): 70 < RSI < 80
    elif 70 <= rsi_value < 80:
        score = 15
        status = 'OVERBOUGHT'
        signals.append(f'RSI {rsi_value:.1f} overbought (70-80) - caution')
    
    # Oversold: 30 < RSI < 40
    elif 30 < rsi_value <= 40:
        score = 10
        status = 'OVERSOLD'
        signals.append(f'RSI {rsi_value:.1f} oversold (30-40)')
    
    # Extreme overbought (high risk): RSI > 80
    elif rsi_value >= 80:
        score = 5
        status = 'EXTREME_OVERBOUGHT'
        signals.append(f'RSI {rsi_value:.1f} extreme overbought (>80) - high risk')
    
    # Extreme oversold: RSI < 30
    else:
        score = 0
        status = 'EXTREME_OVERSOLD'
        signals.append(f'RSI {rsi_value:.1f} extreme oversold (<30)')
    
    return {
        'score': score,
        'status': status,
        'signals': signals,
        'value': rsi_value
    }


def score_macd(macd_data):
    """
    Score MACD trend strength (0-20 points).
    
    Args:
        macd_data: dict from calculate_macd()
        
    Returns:
        dict: {'score': int, 'status': str, 'signals': list}
    """
    if macd_data is None:
        return {'score': 0, 'status': 'INSUFFICIENT_DATA', 'signals': ['Insufficient MACD data']}
    
    signals = []
    macd_val = macd_data['macd']
    signal_val = macd_data['signal']
    histogram = macd_data['histogram']
    
    # Bullish crossover + positive histogram
    if macd_val > signal_val and histogram > 0 and macd_val > 0:
        score = 20
        status = 'STRONG_BULLISH'
        signals.append('MACD > Signal (bullish)')
        signals.append('Positive histogram (momentum increasing)')
    
    # MACD > Signal (bullish)
    elif macd_val > signal_val:
        score = 15
        status = 'BULLISH'
        signals.append('MACD > Signal (bullish crossover)')
    
    # MACD = Signal (neutral)
    elif abs(macd_val - signal_val) < 0.01:
        score = 10
        status = 'NEUTRAL'
        signals.append('MACD ≈ Signal (neutral)')
    
    # MACD < Signal (bearish)
    elif macd_val < signal_val and histogram > -0.1:
        score = 5
        status = 'BEARISH'
        signals.append('MACD < Signal (bearish)')
    
    # Bearish crossover
    else:
        score = 0
        status = 'STRONG_BEARISH'
        signals.append('MACD < Signal (bearish crossover)')
        signals.append('Negative histogram (momentum decreasing)')
    
    return {
        'score': score,
        'status': status,
        'signals': signals
    }


def score_volume(volume_data, ma_score):
    """
    Score volume confirmation (0-20 points).
    
    Args:
        volume_data: dict from analyze_volume()
        ma_score: Moving average score (to confirm with volume)
        
    Returns:
        dict: {'score': int, 'status': str, 'signals': list}
    """
    if volume_data is None:
        return {'score': 0, 'status': 'INSUFFICIENT_DATA', 'signals': ['Insufficient volume data']}
    
    signals = []
    strength = volume_data['strength']
    ratio = volume_data['ratio']
    
    # Volume surge on uptrend (confirmation)
    if strength == 'SURGE' and ma_score >= 20:
        score = 20
        status = 'STRONG_CONFIRMATION'
        signals.append(f'Volume surge ({ratio:.1f}x avg) confirms uptrend')
    
    # Volume surge but not in uptrend (caution)
    elif strength == 'SURGE':
        score = 10
        status = 'SURGE_NO_TREND'
        signals.append(f'Volume surge ({ratio:.1f}x avg) without trend confirmation')
    
    # Above average volume
    elif strength == 'STRONG':
        score = 15
        status = 'ABOVE_AVERAGE'
        signals.append(f'Above average volume ({ratio:.1f}x)')
    
    # Average volume
    elif strength == 'AVERAGE':
        score = 10
        status = 'AVERAGE'
        signals.append(f'Average volume ({ratio:.1f}x)')
    
    # Below average
    elif strength == 'WEAK':
        score = 5
        status = 'BELOW_AVERAGE'
        signals.append(f'Below average volume ({ratio:.1f}x) - weak conviction')
    
    # Low volume
    else:
        score = 0
        status = 'LOW'
        signals.append(f'Low volume ({ratio:.1f}x) - very weak conviction')
    
    return {
        'score': score,
        'status': status,
        'signals': signals
    }


def calculate_technical_score(price_df):
    """
    Master function: Calculate composite technical score (0-100).
    
    Args:
        price_df: DataFrame with OHLCV data (indexed by Date)
        
    Returns:
        dict with comprehensive technical analysis
    """
    if price_df is None or len(price_df) < 50:
        return {
            'score': 0,
            'category': 'INSUFFICIENT_DATA',
            'ma_score': 0,
            'rsi_score': 0,
            'macd_score': 0,
            'volume_score': 0,
            'signals': ['Insufficient price history for technical analysis']
        }
    
    # Get current price
    current_price = price_df['Close'].iloc[-1]
    
    # Calculate Moving Averages
    sma_20 = calculate_sma(price_df['Close'], 20).iloc[-1]
    sma_50 = calculate_sma(price_df['Close'], 50).iloc[-1]
    sma_200 = calculate_sma(price_df['Close'], 200).iloc[-1] if len(price_df) >= 200 else None
    
    # Calculate RSI
    rsi_value = calculate_rsi(price_df['Close'])
    
    # Calculate MACD
    macd_data = calculate_macd(price_df['Close'])
    
    # Analyze Volume
    volume_data = analyze_volume(price_df['Volume'])
    
    # Score each component
    ma_result = score_moving_averages(current_price, sma_20, sma_50, sma_200)
    rsi_result = score_rsi(rsi_value)
    macd_result = score_macd(macd_data)
    volume_result = score_volume(volume_data, ma_result['score'])
    
    # Calculate composite score (0-100)
    total_score = (
        ma_result['score'] +      # 0-30 points
        rsi_result['score'] +      # 0-30 points
        macd_result['score'] +     # 0-20 points
        volume_result['score']     # 0-20 points
    )
    
    # Determine category
    if total_score >= 90:
        category = 'STRONG_BUY'
    elif total_score >= 75:
        category = 'UPTREND'
    elif total_score >= 60:
        category = 'BULLISH'
    elif total_score >= 40:
        category = 'NEUTRAL'
    elif total_score >= 25:
        category = 'WEAK'
    else:
        category = 'DOWNTREND'
    
    # Combine all signals
    all_signals = (
        ma_result['signals'] +
        rsi_result['signals'] +
        macd_result['signals'] +
        volume_result['signals']
    )
    
    return {
        'score': total_score,
        'category': category,
        'ma_score': ma_result['score'],
        'ma_alignment': ma_result['alignment'],
        'rsi_score': rsi_result['score'],
        'rsi_value': rsi_result.get('value'),
        'rsi_status': rsi_result['status'],
        'macd_score': macd_result['score'],
        'macd_status': macd_result['status'],
        'volume_score': volume_result['score'],
        'volume_status': volume_result['status'],
        'signals': all_signals,
        'current_price': current_price,
        'sma_20': sma_20,
        'sma_50': sma_50,
        'sma_200': sma_200
    }


# Test function
if __name__ == "__main__":
    from price_history import fetch_price_history
    
    print("=" * 80)
    print("TECHNICAL INDICATORS MODULE TEST")
    print("=" * 80)
    
    test_tickers = ['TSLL', 'SOFI', 'AAPL']
    
    for ticker in test_tickers:
        print(f"\n{'=' * 80}")
        print(f"🎯 Analyzing: {ticker}")
        print(f"{'=' * 80}")
        
        # Fetch price history
        df = fetch_price_history(ticker, days=90)
        
        if df is not None:
            # Calculate technical score
            analysis = calculate_technical_score(df)
            
            print(f"\n📊 COMPOSITE SCORE: {analysis['score']}/100 - {analysis['category']}")
            print(f"\n📈 Component Scores:")
            print(f"  • Moving Averages: {analysis['ma_score']}/30 ({analysis['ma_alignment']})")
            rsi_val = f"{analysis['rsi_value']:.1f}" if analysis['rsi_value'] else 'N/A'
            print(f"  • RSI: {analysis['rsi_score']}/30 ({analysis['rsi_status']}, value: {rsi_val})")
            print(f"  • MACD: {analysis['macd_score']}/20 ({analysis['macd_status']})")
            print(f"  • Volume: {analysis['volume_score']}/20 ({analysis['volume_status']})")
            
            print(f"\n💡 Key Signals:")
            for signal in analysis['signals']:
                print(f"  • {signal}")
            
            print(f"\n📍 Price Levels:")
            print(f"  Current: ${analysis['current_price']:.2f}")
            sma_20_str = f"${analysis['sma_20']:.2f}" if not pd.isna(analysis['sma_20']) else 'N/A'
            sma_50_str = f"${analysis['sma_50']:.2f}" if not pd.isna(analysis['sma_50']) else 'N/A'
            sma_200_str = f"${analysis['sma_200']:.2f}" if analysis['sma_200'] and not pd.isna(analysis['sma_200']) else 'N/A'
            print(f"  SMA-20: {sma_20_str}")
            print(f"  SMA-50: {sma_50_str}")
            print(f"  SMA-200: {sma_200_str}")
        
        print()
    
    print("=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

"""
Enhanced Trend Analysis Module (Phase 3)
Uses real technical indicators (MA, RSI, MACD, Volume) for comprehensive trend analysis.
Replaces simple 52-week high/low placeholder logic.
"""

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from wishlist_tracker.utils.price_history import fetch_price_history
from wishlist_tracker.utils.technical_indicators import calculate_technical_score


def get_trend_analysis(ticker, current_price=None):
    """
    Enhanced trend analysis using technical indicators.
    
    Args:
        ticker: Stock symbol
        current_price: Current stock price (optional, for display)
        
    Returns:
        dict: {
            'status': 'STRONG_BUY' / 'UPTREND' / 'BULLISH' / 'NEUTRAL' / 'WEAK' / 'DOWNTREND',
            'score': 0-100 composite score,
            'emoji': '🟢' / '🟡' / '🟠' / '🔴',
            'display': 'UPTREND' / 'Neutral' / etc (for backward compatibility),
            'ma_score': 0-30,
            'rsi_score': 0-30,
            'macd_score': 0-20,
            'volume_score': 0-20,
            'details': {technical indicator details},
            'confidence': 'HIGH' / 'MEDIUM' / 'LOW'
        }
    """
    # Fetch price history (uses cache if available)
    try:
        price_df = fetch_price_history(ticker, days=90, use_cache=True)
        
        if price_df is None or len(price_df) < 50:
            # Insufficient data - return neutral
            return {
                'status': 'NEUTRAL',
                'score': 50,
                'emoji': '🟡',
                'display': 'Neutral',
                'ma_score': 0,
                'rsi_score': 0,
                'macd_score': 0,
                'volume_score': 0,
                'details': None,
                'confidence': 'LOW',
                'error': 'Insufficient price history'
            }
        
        # Calculate comprehensive technical score
        analysis = calculate_technical_score(price_df)
        
        # Map category to emoji and display format
        category = analysis['category']
        score = analysis['score']
        
        if category == 'STRONG_BUY':
            emoji = '🟢'
            display = 'Strong Buy'
            confidence = 'HIGH'
        elif category == 'UPTREND':
            emoji = '🟢'
            display = 'Uptrend'
            confidence = 'HIGH'
        elif category == 'BULLISH':
            emoji = '🟡'
            display = 'Bullish'
            confidence = 'MEDIUM'
        elif category == 'NEUTRAL':
            emoji = '🟡'
            display = 'Neutral'
            confidence = 'MEDIUM'
        elif category == 'WEAK':
            emoji = '🟠'
            display = 'Weak'
            confidence = 'LOW'
        else:  # DOWNTREND
            emoji = '🔴'
            display = 'Downtrend'
            confidence = 'LOW'
        
        return {
            'status': category,
            'score': score,
            'emoji': emoji,
            'display': display,
            'ma_score': analysis['ma_score'],
            'rsi_score': analysis['rsi_score'],
            'macd_score': analysis['macd_score'],
            'volume_score': analysis['volume_score'],
            'details': analysis,
            'confidence': confidence
        }
    
    except Exception as e:
        print(f"  ⚠️ Trend analysis error for {ticker}: {e}")
        # Return neutral on error
        return {
            'status': 'NEUTRAL',
            'score': 50,
            'emoji': '🟡',
            'display': 'Neutral',
            'ma_score': 0,
            'rsi_score': 0,
            'macd_score': 0,
            'volume_score': 0,
            'details': None,
            'confidence': 'LOW',
            'error': str(e)
        }


def get_trend_status(current_price, high_52wk, low_52wk):
    """
    LEGACY FUNCTION - Kept for backward compatibility.
    Simple placeholder logic based on 52-week range.
    
    NOTE: New code should use get_trend_analysis() instead!
    
    Args:
        current_price: Current stock price
        high_52wk: 52-week high
        low_52wk: 52-week low
        
    Returns:
        str: "Uptrend" / "Neutral" / "Downtrend"
    """
    if current_price >= high_52wk * 0.95:
        return "Uptrend"
    elif current_price <= low_52wk * 1.05:
        return "Downtrend"
    else:
        return "Neutral"


# OLD FUNCTIONS REMOVED - Use get_trend_analysis() and get_trend_status() instead
# - get_price_history() -> Use fetch_price_history() from price_history.py
# - calculate_moving_average() -> Use calculate_sma() from technical_indicators.py
# - get_trend_signal() -> Use get_trend_analysis()
# - get_trend_score() -> Use analysis['score']
# - is_uptrend() -> Use analysis['status'] in ['UPTREND', 'STRONG_BUY', 'BULLISH']


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("ENHANCED TREND ANALYSIS MODULE TEST (Phase 3)")
    print("=" * 80)
    
    test_tickers = ['TSLL', 'SOFI', 'AAPL', 'SMCI']
    
    for ticker in test_tickers:
        print(f"\n{'=' * 80}")
        print(f"🎯 Analyzing: {ticker}")
        print(f"{'=' * 80}")
        
        # Get enhanced trend analysis
        trend = get_trend_analysis(ticker)
        
        if 'error' in trend:
            print(f"⚠️ Error: {trend['error']}")
        
        print(f"\n{trend['emoji']} TREND ANALYSIS: {trend['display'].upper()}")
        print(f"📊 Composite Score: {trend['score']}/100")
        print(f"🎯 Confidence: {trend['confidence']}")
        print(f"\n📈 Component Breakdown:")
        print(f"  • Moving Averages: {trend['ma_score']}/30")
        print(f"  • RSI Momentum: {trend['rsi_score']}/30")
        print(f"  • MACD Trend: {trend['macd_score']}/20")
        print(f"  • Volume: {trend['volume_score']}/20")
        
        if trend['details']:
            print(f"\n💡 Key Technical Signals:")
            for signal in trend['details']['signals'][:3]:  # Show top 3
                print(f"  • {signal}")
        
        print()
    
    print("=" * 80)
    print("TEST COMPLETE - Phase 3 Enhanced Trend Analysis Working!")
    print("=" * 80)

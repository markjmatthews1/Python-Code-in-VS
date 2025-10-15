#!/usr/bin/env python3
"""
Test Recovery Time Estimation functionality
Tests the EstimateRecoveryTime() function with historical data and implied volatility analysis
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.strategy_engine import estimate_recovery_time, RecoveryTimeEstimator, OptionChainAnalyzer

def test_recovery_time_estimation():
    """Test the recovery time estimation functionality"""
    print("🧪 Recovery Time Estimation Testing Suite")
    print("=" * 60)
    
    # Test scenarios with different recovery distances
    test_scenarios = [
        {
            'ticker': 'SOXL',
            'current_price': 38.50,
            'target_price': 42.50,  # 10.4% recovery needed
            'description': 'SOXL - Moderate recovery needed (10.4%)'
        },
        {
            'ticker': 'NVDA', 
            'current_price': 118.75,
            'target_price': 120.00,  # 1.1% recovery needed
            'description': 'NVDA - Minimal recovery needed (1.1%)'
        },
        {
            'ticker': 'AMD',
            'current_price': 152.30,
            'target_price': 140.00,  # Already recovered (-8.8%)
            'description': 'AMD - Already recovered (above target)'
        },
        {
            'ticker': 'TSLA',
            'current_price': 200.00,
            'target_price': 250.00,  # 25% recovery needed
            'description': 'TSLA - Challenging recovery needed (25%)'
        },
        {
            'ticker': 'QQQ',
            'current_price': 300.00,
            'target_price': 420.00,  # 40% recovery needed
            'description': 'QQQ - Difficult recovery needed (40%)'
        }
    ]
    
    print("🚀 Testing Recovery Time Estimation for Multiple Scenarios...")
    print()
    
    for scenario in test_scenarios:
        print(f"📊 Testing {scenario['description']}")
        print("-" * 50)
        
        # Test with default confidence level (68%)
        result = estimate_recovery_time(
            scenario['ticker'],
            scenario['current_price'], 
            scenario['target_price']
        )
        
        display_recovery_analysis(result)
        print()
    
    # Test component functionality
    print("🔧 Testing Recovery Time Components...")
    print("-" * 50)
    
    analyzer = OptionChainAnalyzer()
    estimator = RecoveryTimeEstimator(analyzer)
    
    # Test volatility calculations
    print("✅ Testing volatility calculations:")
    for ticker in ['SOXL', 'NVDA', 'AAPL', 'SPY']:
        hist_vol = estimator.get_historical_volatility(ticker)
        impl_vol = estimator.get_implied_volatility(ticker, 100.0)  # Arbitrary target
        print(f"   {ticker}: Historical Vol = {hist_vol:.1%}, Implied Vol = {impl_vol:.1%}")
    
    print()
    print("✅ Testing different confidence levels:")
    
    # Test different confidence levels for SOXL
    confidence_levels = [0.50, 0.68, 0.80, 0.90, 0.95]
    ticker = 'SOXL'
    current_price = 38.50
    target_price = 42.50
    
    for confidence in confidence_levels:
        result = estimate_recovery_time(ticker, current_price, target_price, confidence)
        estimates = result['estimates']
        print(f"   {confidence:.0%} confidence: {estimates['most_likely_days']} days "
              f"({estimates.get('most_likely_calendar', 'N/A')})")
    
    print()
    print("🎯 Testing Market Context Analysis...")
    
    # Test different recovery distances
    recovery_scenarios = [
        (35.0, 42.5, "Challenging"),
        (40.0, 42.5, "Moderate"), 
        (42.0, 42.5, "Minimal"),
        (43.0, 42.5, "Already Recovered")
    ]
    
    for current, target, expected in recovery_scenarios:
        result = estimate_recovery_time('SOXL', current, target)
        context = result['market_context']
        print(f"   ${current:.2f} → ${target:.2f}: {context['difficulty_level']} "
              f"({context['recovery_distance_pct']:.1f}% recovery needed)")
    
    print()
    print("📈 Testing Volatility Regime Classification...")
    
    # Test volatility regime analysis
    vol_scenarios = [
        (0.25, 0.35, "Elevated IV"),
        (0.30, 0.25, "Low IV"),
        (0.25, 0.25, "Normal"),
        (0.20, 0.30, "High Fear")
    ]
    
    for hist_vol, impl_vol, expected in vol_scenarios:
        regime = estimator._classify_volatility_regime(hist_vol, impl_vol)
        print(f"   Hist: {hist_vol:.0%}, Impl: {impl_vol:.0%} → {regime['regime']} "
              f"(Ratio: {regime['vol_ratio']:.2f})")
    
    print()
    print("✅ All Recovery Time Estimation tests completed!")

def display_recovery_analysis(result):
    """Display comprehensive recovery time analysis"""
    ticker = result['ticker']
    current = result['current_price']
    target = result['target_price']
    required_return = result['required_return_pct']
    
    print(f"🎯 Recovery Analysis for {ticker}:")
    print(f"   Current Price: ${current:.2f}")
    print(f"   Target Price: ${target:.2f}")
    print(f"   Required Return: {required_return:.1f}%")
    
    # Volatility information
    hist_vol = result['historical_volatility']
    impl_vol = result['implied_volatility']
    avg_vol = result['average_volatility']
    
    print(f"   Historical Volatility: {hist_vol:.1%}")
    print(f"   Implied Volatility: {impl_vol:.1%}")
    print(f"   Average Volatility: {avg_vol:.1%}")
    
    # Time estimates
    estimates = result['estimates']
    print(f"   Breakeven Window: {result['breakeven_window']} days")
    print(f"   Time Estimates:")
    print(f"     Optimistic: {estimates['optimistic_days']} days ({estimates.get('optimistic_calendar', 'N/A')})")
    print(f"     Most Likely: {estimates['most_likely_days']} days ({estimates.get('most_likely_calendar', 'N/A')})")
    print(f"     Pessimistic: {estimates['pessimistic_days']} days ({estimates.get('pessimistic_calendar', 'N/A')})")
    
    # Market context
    context = result['market_context']
    print(f"   Market Context:")
    print(f"     Difficulty Level: {context['difficulty_level']}")
    print(f"     Asset Class: {context['asset_class']}")
    print(f"     Market Sentiment: {context['market_sentiment']}")
    
    # Volatility regime
    vol_regime = result['volatility_regime']
    print(f"   Volatility Regime: {vol_regime['regime']}")
    print(f"   Regime Description: {vol_regime['description']}")
    
    # Recommendation
    print(f"   💡 Recommendation: {result['recommendation']}")

def test_edge_cases():
    """Test edge cases and error handling"""
    print()
    print("🔍 Testing Edge Cases...")
    print("-" * 30)
    
    # Test with extreme scenarios
    edge_cases = [
        ('INVALID', 100.0, 120.0, "Invalid ticker"),
        ('AAPL', 0.01, 200.0, "Extreme recovery needed"),
        ('TSLA', 300.0, 50.0, "Target below current"),
        ('SPY', 400.0, 400.0, "Already at target")
    ]
    
    for ticker, current, target, description in edge_cases:
        try:
            result = estimate_recovery_time(ticker, current, target)
            print(f"✅ {description}: {result['breakeven_window']} days estimated")
        except Exception as e:
            print(f"⚠️ {description}: Error handled - {str(e)[:50]}")
    
    print("✅ Edge case testing completed!")

if __name__ == "__main__":
    test_recovery_time_estimation()
    test_edge_cases()
#!/usr/bin/env python3
"""
Test Call Overlay Strategy Engine
Tests the call overlay evaluation functionality
"""
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.strategy_engine import evaluate_call_overlay, CallOverlayEvaluator, OptionChainAnalyzer

def test_call_overlay_engine():
    """Test the call overlay evaluation engine"""
    try:
        print("🚀 Testing Call Overlay Strategy Engine...")
        
        # Test parameters
        test_cases = [
            ("SOXL", 42.50, 100),
            ("NVDA", 120.00, 50),
            ("AMD", 140.00, 75),
            ("TSLA", 250.00, 25)
        ]
        
        for ticker, cost_basis, qty in test_cases:
            print(f"\n📊 Testing {ticker} - {qty} shares @ ${cost_basis}")
            
            # Test call overlay evaluation
            strategies = evaluate_call_overlay(ticker, cost_basis, qty)
            
            print(f"✅ Found {len(strategies)} call overlay strategies:")
            
            for i, strategy in enumerate(strategies, 1):
                print(f"\n{i}. Strike ${strategy['strike']} Call:")
                print(f"   Expiry: {strategy['expiry']} ({strategy['days_to_expiry']} days)")
                print(f"   Premium: ${strategy['bid']:.2f} (${strategy['premium_income']:.0f} total)")
                print(f"   Premium Yield: {strategy['premium_yield']:.1f}% annualized")
                print(f"   Assignment Probability: {strategy['prob_assignment']:.1%}")
                print(f"   Risk Level: {strategy['risk_level']}")
                print(f"   Score: {strategy['combined_score']:.1f}")
                print(f"   Recommendation: {strategy['recommendation']}")
                
                # Test scenario analysis
                if 'scenario_assigned' in strategy:
                    assigned = strategy['scenario_assigned']
                    print(f"   If Assigned: {assigned['analysis']}")
                
                if 'scenario_expires' in strategy:
                    expires = strategy['scenario_expires']
                    print(f"   If Expires: {expires['analysis']}")
        
        print("\n✅ All Call Overlay tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Call Overlay test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_call_overlay_components():
    """Test individual call overlay components"""
    try:
        print("\n🔧 Testing Call Overlay Components...")
        
        # Test option chain analyzer
        analyzer = OptionChainAnalyzer()
        print("✅ OptionChainAnalyzer initialized")
        
        # Test call evaluator
        call_evaluator = CallOverlayEvaluator(analyzer)
        print("✅ CallOverlayEvaluator initialized")
        
        # Test mock data generation
        current_price = 36.00  # SOXL mock price
        mock_chain = call_evaluator._create_mock_option_chain("SOXL", current_price, 'CALL')
        print(f"✅ Generated {len(mock_chain)} mock call options")
        
        # Test filtering
        viable_calls = []
        for option in mock_chain:
            if call_evaluator._meets_call_filter_criteria(option, current_price, 42.50):
                viable_calls.append(option)
        
        print(f"✅ Filtered to {len(viable_calls)} viable call options")
        
        # Test metrics calculation
        if viable_calls:
            test_option = viable_calls[0]
            metrics = call_evaluator._calculate_call_metrics(
                test_option, "SOXL", current_price, 42.50, 100
            )
            
            if metrics:
                print(f"✅ Calculated metrics for ${test_option['strike']} call:")
                print(f"   Premium Yield: {metrics['premium_yield']:.1f}%")
                print(f"   Combined Score: {metrics['combined_score']:.1f}")
            else:
                print("⚠️ Metrics calculation returned None")
        
        print("✅ All component tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_call_vs_put_comparison():
    """Test comparison between call and put overlay strategies"""
    try:
        print("\n⚖️ Testing Call vs Put Strategy Comparison...")
        
        ticker = "SOXL"
        cost_basis = 42.50
        qty = 100
        
        # Get put strategies
        from utils.strategy_engine import evaluate_put_overlay
        put_strategies = evaluate_put_overlay(ticker, cost_basis, qty)
        
        # Get call strategies
        call_strategies = evaluate_call_overlay(ticker, cost_basis, qty)
        
        print(f"\n📊 Strategy Comparison for {ticker}:")
        print(f"Put Overlays: {len(put_strategies)} strategies found")
        print(f"Covered Calls: {len(call_strategies)} strategies found")
        
        if put_strategies:
            best_put = put_strategies[0]
            print(f"\nBest Put: ${best_put['strike']} strike, Score {best_put['combined_score']:.1f}")
        
        if call_strategies:
            best_call = call_strategies[0]
            print(f"Best Call: ${best_call['strike']} strike, Score {best_call['combined_score']:.1f}")
        
        print("\n💡 Strategy Recommendation:")
        if put_strategies and call_strategies:
            put_score = put_strategies[0]['combined_score']
            call_score = call_strategies[0]['combined_score']
            
            if put_score > call_score:
                print(f"   Prefer PUT overlay (Score: {put_score:.1f} vs {call_score:.1f})")
            else:
                print(f"   Prefer CALL overlay (Score: {call_score:.1f} vs {put_score:.1f})")
        
        print("✅ Comparison test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all call overlay tests"""
    print("🧪 Call Overlay Strategy Testing Suite")
    print("=" * 50)
    
    # Run tests
    tests = [
        test_call_overlay_engine,
        test_call_overlay_components,
        test_call_vs_put_comparison
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All Call Overlay tests PASSED!")
    else:
        print("❌ Some tests FAILED!")

if __name__ == "__main__":
    main()
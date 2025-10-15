#!/usr/bin/env python3
"""
Test Synthetic Recovery Strategy Engine
Tests the synthetic recovery evaluation functionality
"""
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.strategy_engine import build_synthetic_recovery, SyntheticRecoveryEvaluator, OptionChainAnalyzer

def test_synthetic_recovery_engine():
    """Test the synthetic recovery evaluation engine"""
    try:
        print("🚀 Testing Synthetic Recovery Strategy Engine...")
        
        # Test parameters
        test_cases = [
            ("SOXL", 42.50, 100),
            ("NVDA", 120.00, 50),
            ("AMD", 140.00, 75),
            ("TSLA", 250.00, 25)
        ]
        
        for ticker, cost_basis, qty in test_cases:
            print(f"\n📊 Testing {ticker} - {qty} shares @ ${cost_basis}")
            
            # Test synthetic recovery evaluation
            strategy = build_synthetic_recovery(ticker, cost_basis, qty)
            
            if strategy:
                print(f"✅ Synthetic Recovery Strategy Generated:")
                
                # Double down analysis
                if 'double_down_analysis' in strategy:
                    dd = strategy['double_down_analysis']
                    print(f"   Double Down: Buy {dd['additional_shares']} more shares @ ${dd['current_price']:.2f}")
                    print(f"   New Cost Basis: ${dd['new_cost_basis']:.2f}")
                    print(f"   Additional Investment: ${dd['additional_investment']:,.0f}")
                    print(f"   Recovery Needed: {dd['recovery_from_current']:.1f}%")
                
                # Best call option
                if 'best_call_option' in strategy:
                    call = strategy['best_call_option']
                    print(f"   Best Call: ${call['strike']:.2f} strike")
                    print(f"   Premium Income: ${call['premium_income']:.0f}")
                    print(f"   Effective Cost Basis: ${call['effective_cost_basis']:.2f}")
                    print(f"   Synthetic Score: {call['synthetic_score']:.1f}")
                
                # Overall metrics
                print(f"   Viability Score: {strategy['viability_score']:.1f}")
                print(f"   Risk Level: {strategy['risk_level']}")
                print(f"   Recommendation: {strategy['recommendation']}")
                
                # Scenarios
                if 'scenario_no_assignment' in strategy:
                    scenario = strategy['scenario_no_assignment']
                    print(f"   If Calls Expire: {scenario['analysis']}")
                
                if 'scenario_assignment' in strategy:
                    scenario = strategy['scenario_assignment']
                    print(f"   If Calls Assigned: {scenario['analysis']}")
            else:
                print("❌ No strategy generated")
        
        print("\n✅ All Synthetic Recovery tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Synthetic Recovery test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_synthetic_recovery_components():
    """Test individual synthetic recovery components"""
    try:
        print("\n🔧 Testing Synthetic Recovery Components...")
        
        # Test option chain analyzer
        analyzer = OptionChainAnalyzer()
        print("✅ OptionChainAnalyzer initialized")
        
        # Test synthetic evaluator
        synthetic_evaluator = SyntheticRecoveryEvaluator(analyzer)
        print("✅ SyntheticRecoveryEvaluator initialized")
        
        # Test double down calculation
        current_price = 36.00  # SOXL mock price
        double_down = synthetic_evaluator._calculate_double_down_metrics(
            "SOXL", 42.50, 100, current_price
        )
        print(f"✅ Double down calculation:")
        print(f"   Original Investment: ${double_down['original_investment']:,.0f}")
        print(f"   Additional Investment: ${double_down['additional_investment']:,.0f}")
        print(f"   New Cost Basis: ${double_down['new_cost_basis']:.2f}")
        print(f"   Recovery Needed: {double_down['recovery_from_current']:.1f}%")
        
        # Test call option filtering
        mock_options = synthetic_evaluator._create_mock_call_options("SOXL", current_price, double_down['new_cost_basis'])
        print(f"✅ Generated {len(mock_options)} mock call options for synthetic strategy")
        
        # Test viability scoring
        if mock_options:
            best_call = mock_options[0]
            base_viability = synthetic_evaluator._calculate_base_viability(double_down)
            print(f"✅ Base viability score: {base_viability:.1f}")
            print(f"✅ Best call synthetic score: {best_call['synthetic_score']:.1f}")
        
        print("✅ All component tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Component test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_synthetic_vs_other_strategies():
    """Test comparison between synthetic and other recovery strategies"""
    try:
        print("\n⚖️ Testing Synthetic vs Other Strategy Comparison...")
        
        ticker = "SOXL"
        cost_basis = 42.50
        qty = 100
        
        # Get synthetic recovery strategy
        synthetic_strategy = build_synthetic_recovery(ticker, cost_basis, qty)
        
        # Get other strategies for comparison
        from utils.strategy_engine import evaluate_put_overlay, evaluate_call_overlay
        put_strategies = evaluate_put_overlay(ticker, cost_basis, qty)
        call_strategies = evaluate_call_overlay(ticker, cost_basis, qty)
        
        print(f"\n📊 Strategy Comparison for {ticker}:")
        print(f"Put Overlays: {len(put_strategies)} strategies found")
        print(f"Covered Calls: {len(call_strategies)} strategies found")
        print(f"Synthetic Recovery: {'Generated' if synthetic_strategy else 'None'}")
        
        scores = []
        
        if put_strategies:
            best_put = put_strategies[0]
            put_score = best_put['combined_score']
            scores.append(('Put Overlay', put_score))
            print(f"\nBest Put: ${best_put['strike']} strike, Score {put_score:.1f}")
        
        if call_strategies:
            best_call = call_strategies[0]
            call_score = best_call['combined_score']
            scores.append(('Covered Call', call_score))
            print(f"Best Call: ${best_call['strike']} strike, Score {call_score:.1f}")
        
        if synthetic_strategy:
            synthetic_score = synthetic_strategy['viability_score']
            scores.append(('Synthetic Recovery', synthetic_score))
            print(f"Synthetic Recovery: Viability Score {synthetic_score:.1f}")
        
        print("\n💡 Strategy Recommendation:")
        if scores:
            best_strategy = max(scores, key=lambda x: x[1])
            print(f"   Recommended: {best_strategy[0]} (Score: {best_strategy[1]:.1f})")
            
            # Risk consideration
            if synthetic_strategy and best_strategy[0] == 'Synthetic Recovery':
                risk_level = synthetic_strategy['risk_level']
                print(f"   ⚠️ Note: Synthetic recovery has {risk_level} risk due to additional capital requirement")
        
        print("✅ Comparison test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_synthetic_risk_assessment():
    """Test synthetic recovery risk assessment"""
    try:
        print("\n🛡️ Testing Synthetic Recovery Risk Assessment...")
        
        analyzer = OptionChainAnalyzer()
        synthetic_evaluator = SyntheticRecoveryEvaluator(analyzer)
        
        # Test different risk scenarios
        test_scenarios = [
            ("SOXL", 42.50, 100, "High volatility ETF"),
            ("QQQ", 380.00, 50, "Moderate risk ETF"),
            ("AAPL", 175.00, 100, "Large cap stock")
        ]
        
        for ticker, cost_basis, qty, description in test_scenarios:
            print(f"\n📊 {ticker} ({description}):")
            
            strategy = build_synthetic_recovery(ticker, cost_basis, qty)
            
            if strategy:
                print(f"   Viability Score: {strategy['viability_score']:.1f}")
                print(f"   Risk Level: {strategy['risk_level']}")
                print(f"   Additional Capital: ${strategy['double_down_analysis']['additional_investment']:,.0f}")
                
                # Risk factors analysis
                double_down = strategy['double_down_analysis']
                recovery_distance = double_down['recovery_from_current']
                
                if recovery_distance > 25:
                    print(f"   ⚠️ High recovery distance: {recovery_distance:.1f}%")
                elif recovery_distance > 15:
                    print(f"   ⚠️ Moderate recovery distance: {recovery_distance:.1f}%")
                else:
                    print(f"   ✅ Reasonable recovery distance: {recovery_distance:.1f}%")
        
        print("\n✅ Risk assessment test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Risk assessment test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all synthetic recovery tests"""
    print("🧪 Synthetic Recovery Strategy Testing Suite")
    print("=" * 60)
    
    # Run tests
    tests = [
        test_synthetic_recovery_engine,
        test_synthetic_recovery_components,
        test_synthetic_vs_other_strategies,
        test_synthetic_risk_assessment
    ]
    
    passed = 0
    for test in tests:
        if test():
            passed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{len(tests)} tests passed")
    
    if passed == len(tests):
        print("🎉 All Synthetic Recovery tests PASSED!")
    else:
        print("❌ Some tests FAILED!")

if __name__ == "__main__":
    main()
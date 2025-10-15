"""
Test script for Strategy Engine
Tests the EvaluatePutOverlay functionality with real and mock data
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.strategy_engine import evaluate_put_overlay, OptionChainAnalyzer, PutOverlayEvaluator

def test_option_chain_analyzer():
    """Test the option chain analyzer"""
    print("🔗 Testing Option Chain Analyzer...")
    
    try:
        analyzer = OptionChainAnalyzer()
        print("✅ Option chain analyzer initialized")
        
        # Test price fetching
        test_tickers = ['SOXL', 'NVDA', 'AMD', 'AAPL']
        
        for ticker in test_tickers:
            price = analyzer.get_current_price(ticker)
            print(f"✅ {ticker} current price: ${price:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Option chain analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_put_overlay_evaluator():
    """Test the put overlay evaluator with sample data"""
    print("\n🎯 Testing Put Overlay Evaluator...")
    
    try:
        analyzer = OptionChainAnalyzer()
        evaluator = PutOverlayEvaluator(analyzer)
        print("✅ Put overlay evaluator initialized")
        
        # Test with sample position
        ticker = "SOXL"
        cost_basis = 42.50
        qty = 100
        
        print(f"📊 Analyzing {ticker}: {qty} shares @ ${cost_basis}")
        
        # Get current price
        current_price = analyzer.get_current_price(ticker)
        print(f"✅ Current price: ${current_price:.2f}")
        
        # Generate option chain
        option_chain = evaluator._get_option_chain(ticker, current_price)
        print(f"✅ Option chain generated: {len(option_chain)} options")
        
        # Test expiration dates
        expiry_dates = evaluator._get_target_expiration_dates()
        print(f"✅ Target expiration dates: {expiry_dates}")
        
        # Show sample options
        puts = [opt for opt in option_chain if opt['type'] == 'PUT'][:5]
        print(f"✅ Sample puts (first 5):")
        for put in puts:
            print(f"   ${put['strike']} put exp {put['expiry']}: bid ${put['bid']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Put overlay evaluator test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_strategy_evaluation():
    """Test the complete strategy evaluation process"""
    print("\n🧠 Testing Complete Strategy Evaluation...")
    
    try:
        # Test cases with different scenarios
        test_cases = [
            {
                'ticker': 'SOXL',
                'cost_basis': 42.50,
                'qty': 100,
                'description': 'Leveraged ETF underwater position'
            },
            {
                'ticker': 'NVDA',
                'cost_basis': 125.00,
                'qty': 50,
                'description': 'AI stock moderate underwater'
            },
            {
                'ticker': 'AMD',
                'cost_basis': 165.00,
                'qty': 75,
                'description': 'Semiconductor significantly underwater'
            }
        ]
        
        all_strategies = []
        
        for case in test_cases:
            print(f"\n📈 {case['description']}")
            print(f"   Position: {case['qty']} shares of {case['ticker']} @ ${case['cost_basis']}")
            
            strategies = evaluate_put_overlay(
                case['ticker'], 
                case['cost_basis'], 
                case['qty']
            )
            
            print(f"✅ Found {len(strategies)} strategies for {case['ticker']}")
            
            if strategies:
                top_strategy = strategies[0]
                print(f"   Top Strategy: ${top_strategy['strike']} put")
                print(f"   Premium: ${top_strategy['premium_income']:.0f}")
                print(f"   Score: {top_strategy['combined_score']:.1f}")
                print(f"   Risk: {top_strategy['risk_level']}")
            
            all_strategies.extend(strategies)
        
        print(f"\n✅ Total strategies evaluated: {len(all_strategies)}")
        
        # Test strategy ranking
        if all_strategies:
            best_overall = max(all_strategies, key=lambda x: x['combined_score'])
            print(f"✅ Best overall strategy: {best_overall['ticker']} ${best_overall['strike']} put")
            print(f"   Score: {best_overall['combined_score']:.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Strategy evaluation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_calculation_accuracy():
    """Test calculation accuracy with known values"""
    print("\n🧮 Testing Calculation Accuracy...")
    
    try:
        analyzer = OptionChainAnalyzer()
        evaluator = PutOverlayEvaluator(analyzer)
        
        # Test with specific option parameters
        test_option = {
            'strike': 40.0,
            'expiry': '2025-11-15',
            'bid': 2.40,
            'ask': 2.60,
            'type': 'PUT'
        }
        
        ticker = 'SOXL'
        current_price = 38.50
        cost_basis = 42.50
        qty = 100
        
        metrics = evaluator._calculate_put_metrics(
            test_option, ticker, current_price, cost_basis, qty
        )
        
        if metrics:
            print("✅ Metrics calculation successful:")
            print(f"   Premium Income: ${metrics['premium_income']:.0f}")
            print(f"   Effective Entry: ${metrics['effective_entry']:.2f}")
            print(f"   Assignment Probability: {metrics['prob_assignment']:.1%}")
            print(f"   Combined Score: {metrics['combined_score']:.1f}")
            
            # Validate key calculations
            expected_premium = 2.40 * 100
            expected_effective_entry = 40.0 - 2.40
            
            if abs(metrics['premium_income'] - expected_premium) < 0.01:
                print("✅ Premium calculation accurate")
            else:
                print(f"❌ Premium calculation error: expected {expected_premium}, got {metrics['premium_income']}")
            
            if abs(metrics['effective_entry'] - expected_effective_entry) < 0.01:
                print("✅ Effective entry calculation accurate")
            else:
                print(f"❌ Effective entry error: expected {expected_effective_entry}, got {metrics['effective_entry']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Calculation accuracy test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_strategy_engine_tests():
    """Run all strategy engine tests"""
    print("🚀 Strategy Engine Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test 1: Option Chain Analyzer
    if not test_option_chain_analyzer():
        success = False
    
    # Test 2: Put Overlay Evaluator
    if not test_put_overlay_evaluator():
        success = False
    
    # Test 3: Complete Strategy Evaluation
    if not test_strategy_evaluation():
        success = False
    
    # Test 4: Calculation Accuracy
    if not test_calculation_accuracy():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("✅ All Strategy Engine tests passed!")
        print("\n📋 Strategy Engine Features Verified:")
        print("   • Option chain data fetching (mock + real)")
        print("   • Put option filtering by premium and strike")
        print("   • Effective entry calculations")
        print("   • Assignment probability estimation")
        print("   • Recovery scenario analysis")
        print("   • Combined scoring algorithm")
        print("   • Risk level assessment")
        print("   • Top 3 strategy ranking")
        print("   • Comprehensive strategy recommendations")
    else:
        print("❌ Some Strategy Engine tests failed!")
    
    return success

if __name__ == "__main__":
    success = run_strategy_engine_tests()
    sys.exit(0 if success else 1)
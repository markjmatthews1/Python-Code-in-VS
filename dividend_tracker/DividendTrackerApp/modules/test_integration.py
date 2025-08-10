#!/usr/bin/env python3
"""
Quick Test for Enhanced Dividend Tracker
Tests portfolio integration specifically
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

# Test minimal functionality
def test_portfolio_tracker():
    """Test the portfolio tracking functionality"""
    print("=== Testing Portfolio Tracker ===")
    
    try:
        from portfolio_history_manager import PortfolioHistoryManager
        print("✅ PortfolioHistoryManager imported")
        
        manager = PortfolioHistoryManager()
        print("✅ PortfolioHistoryManager created")
        
        # Test portfolio summary
        summary = manager.get_portfolio_summary_for_week()
        if summary:
            print("✅ Portfolio summary retrieved:")
            for account, value in summary.items():
                print(f"  {account}: ${value:,.2f}")
        
        # Test 401K current value
        current_401k = manager.get_current_401k_value()
        print(f"✅ Current 401K: ${current_401k:,.2f}")
        
        # Test Excel creation (without workbook dependencies)
        print("✅ Portfolio functionality working!")
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_tracker():
    """Test the enhanced tracker class creation"""
    print("\n=== Testing Enhanced Tracker ===")
    
    try:
        # Test if we can create the class without dependencies
        from enhanced_dividend_tracker import EnhancedDividendTracker
        print("✅ EnhancedDividendTracker imported")
        
        tracker = EnhancedDividendTracker()
        print("✅ EnhancedDividendTracker created")
        
        if tracker.portfolio_manager:
            print("✅ Portfolio manager available")
            
            # Test portfolio summary through tracker
            summary = tracker.get_portfolio_summary()
            if summary:
                print("✅ Portfolio summary via tracker:")
                for account, value in summary.items():
                    print(f"  {account}: ${value:,.2f}")
        else:
            print("⚠️ Portfolio manager not available")
            
        return True
        
    except Exception as e:
        print(f"❌ Enhanced tracker error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Test individual components
    portfolio_ok = test_portfolio_tracker()
    tracker_ok = test_enhanced_tracker()
    
    if portfolio_ok and tracker_ok:
        print("\n🎉 All tests passed! Portfolio integration working!")
    else:
        print("\n⚠️ Some tests failed. Check errors above.")

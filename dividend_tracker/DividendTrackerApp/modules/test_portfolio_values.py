#!/usr/bin/env python3
"""
Test Portfolio Value Calculation
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from portfolio_value_tracker import PortfolioValueTracker

def test_portfolio_values():
    """Test the corrected portfolio value calculation"""
    print("🧪 Testing Corrected Portfolio Value Calculation")
    print("=" * 60)
    
    try:
        tracker = PortfolioValueTracker()
        values = tracker.get_etrade_portfolio_values()
        
        print("\n📊 Portfolio Values:")
        total = 0
        for account, value in values.items():
            print(f"  {account}: ${value:,.2f}")
            total += value
        
        print(f"\n💰 Total E*TRADE Portfolio: ${total:,.2f}")
        
        # Compare with expected total
        expected_total = 514206.60  # Your stated total
        difference = total - expected_total
        
        print(f"📋 Expected Total: ${expected_total:,.2f}")
        print(f"📊 Actual Total: ${total:,.2f}")
        print(f"📈 Difference: ${difference:,.2f}")
        
        if abs(difference) < 1000:  # Within $1000
            print("✅ Portfolio values are reasonably accurate!")
        else:
            print("⚠️ Significant difference detected - may need API debugging")
        
    except Exception as e:
        print(f"❌ Error testing portfolio values: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_portfolio_values()

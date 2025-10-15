#!/usr/bin/env python3
"""
Test position sizing calculation for various ETF prices
"""

from core.risk_manager import EnhancedRiskManager

def test_position_sizing():
    """Test position sizing for different ETF prices"""
    risk_manager = EnhancedRiskManager(10000)  # $10K account
    
    test_cases = [
        ('XBI', 106.0),   # The problematic case
        ('XLK', 285.0),   # High-priced tech ETF
        ('XLF', 53.0),    # Mid-priced financial ETF
        ('XRT', 45.0),    # Lower-priced retail ETF
        ('XLE', 87.0),    # Energy ETF
    ]
    
    print("🔍 POSITION SIZING TEST FOR $10K ACCOUNT")
    print("=" * 60)
    
    for symbol, price in test_cases:
        pos = risk_manager.calculate_position_size(price)
        
        print(f"\n🎯 {symbol} @ ${price:.2f}")
        print(f"   Shares: {pos['shares']}")
        print(f"   Position Value: ${pos['position_value']:,.2f}")
        print(f"   Risk Amount: ${pos['dollar_risk']:.2f}")
        print(f"   Risk %: {pos['risk_pct']*100:.2f}%")
        print(f"   Stop Loss: ${pos['stop_loss_price']:.2f}")
        print(f"   Target: ${pos['target_price']:.2f}")
        print(f"   Valid: {pos['valid']}")
        
        # Check if position is reasonable for $10K account
        if pos['position_value'] > 2500:  # More than 25% of account
            print(f"   ⚠️  WARNING: Position too large for $10K account!")
        else:
            print(f"   ✅ Position size appropriate")

if __name__ == "__main__":
    test_position_sizing()
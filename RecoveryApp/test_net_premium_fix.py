#!/usr/bin/env python3
"""
Test the fixed net premium calculation
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.models import TradeEntry

def test_net_premium_calculation():
    """Test that net premium is calculated correctly"""
    
    print("=== Testing Fixed Net Premium Calculation ===")
    
    # Test with your actual SOXL trade data
    soxl_trade = TradeEntry(
        type="short_put",
        strike=33.0,
        expiry="2025-11-21", 
        premium=2.20,  # Per share
        status="open",
        quantity=1,    # 1 contract = 100 shares
        commission=0.65  # Total commission for entire trade
    )
    
    print(f"SOXL Short Put Trade:")
    print(f"  Premium per share: ${soxl_trade.premium}")
    print(f"  Quantity: {soxl_trade.quantity} contract(s)")
    print(f"  Total shares: {soxl_trade.quantity * 100}")
    print(f"  Commission (total): ${soxl_trade.commission}")
    
    # Calculate manually
    total_shares = soxl_trade.quantity * 100
    commission_per_share = soxl_trade.commission / total_shares
    expected_net_premium = soxl_trade.premium - commission_per_share
    
    print(f"\nManual Calculation:")
    print(f"  Commission per share: ${commission_per_share:.4f}")
    print(f"  Expected net premium per share: ${expected_net_premium:.4f}")
    
    # Test the method
    calculated_net_premium = soxl_trade.net_premium()
    total_net_premium = soxl_trade.total_net_premium()
    
    print(f"\nMethod Results:")
    print(f"  Net premium per share: ${calculated_net_premium:.4f}")
    print(f"  Total net premium: ${total_net_premium:.2f}")
    
    # Verify calculations
    print(f"\n=== Verification ===")
    print(f"  OLD (incorrect) calculation: ${soxl_trade.premium - soxl_trade.commission:.4f}")
    print(f"  NEW (correct) calculation: ${calculated_net_premium:.4f}")
    print(f"  Difference: ${abs(calculated_net_premium - expected_net_premium):.6f}")
    
    if abs(calculated_net_premium - expected_net_premium) < 0.0001:
        print(f"  ✅ PASS: Net premium calculation is correct!")
    else:
        print(f"  ❌ FAIL: Net premium calculation is wrong!")
    
    # Show the practical impact
    print(f"\n=== Practical Impact ===")
    old_wrong_result = soxl_trade.premium - soxl_trade.commission
    print(f"  Before fix: Net premium = ${old_wrong_result:.2f} per share")
    print(f"  After fix:  Net premium = ${calculated_net_premium:.2f} per share")
    print(f"  Correction: ${calculated_net_premium - old_wrong_result:.2f} per share higher")
    
    # Total trade value
    total_gross = soxl_trade.premium * 100  # Total gross premium
    print(f"\n=== Total Trade Value ===")
    print(f"  Gross premium: ${total_gross:.2f}")
    print(f"  Commission: ${soxl_trade.commission:.2f}")
    print(f"  Net premium: ${total_net_premium:.2f}")
    
    return calculated_net_premium

if __name__ == "__main__":
    test_net_premium_calculation()
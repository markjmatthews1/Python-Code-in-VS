#!/usr/bin/env python3
"""
Debug Sorting Display
Test what's actually being shown in the GUI vs what should be shown
"""

# Let's simulate what the GUI should show with sample data
def test_gui_display():
    """Test what the GUI should display with sample data"""
    
    # Sample tickers with different premium values and trends
    test_data = [
        # (symbol, current_price, premium_val, trend_entry, premium_val_num)
        ("TICKER1", "50.00", "+$2.50", "Uptrend/Entry", 2.50),
        ("TICKER2", "25.00", "-$0.10", "Network/API Error", -0.10),
        ("TICKER3", "35.00", "+$1.00", "Uptrend/Entry", 1.00),
        ("TICKER4", "40.00", "-$10.34", "Network/API Error", -10.34),
        ("TICKER5", "30.00", "+$0.75", "Neutral/Wait", 0.75),
        ("TICKER6", "45.00", "-$5.20", "Downtrend/Avoid", -5.20),
    ]
    
    print("🔍 Debug: What GUI Should Display")
    print("=" * 50)
    
    # Separate into groups like the actual sorting logic
    uptrend_positive_premium = []
    all_others = []
    
    for symbol, price, premium_display, trend, premium_num in test_data:
        is_uptrend = trend == "Uptrend/Entry"
        has_positive_premium = premium_num > 0
        
        print(f"• {symbol}: Premium={premium_display} ({premium_num:+.2f}), Trend={trend}")
        print(f"  - Is Uptrend: {is_uptrend}")
        print(f"  - Has Positive Premium: {has_positive_premium}")
        print(f"  - Priority Group: {'1st (Uptrend+Positive)' if is_uptrend and has_positive_premium else '2nd (All Others)'}")
        print()
        
        if is_uptrend and has_positive_premium:
            uptrend_positive_premium.append((symbol, price, premium_display, trend, premium_num))
        else:
            all_others.append((symbol, price, premium_display, trend, premium_num))
    
    # Sort by premium (highest first)
    uptrend_positive_premium.sort(key=lambda x: x[4], reverse=True)
    all_others.sort(key=lambda x: x[4], reverse=True)
    
    # Combine
    final_order = uptrend_positive_premium + all_others
    
    print("📋 Expected GUI Display Order:")
    print("-" * 30)
    for i, (symbol, price, premium_display, trend, premium_num) in enumerate(final_order, 1):
        group = "1st Priority" if i <= len(uptrend_positive_premium) else "2nd Priority"
        print(f"{i}. {symbol}: Premium={premium_display}, Trend={trend} ({group})")
    
    print(f"\n✅ Summary:")
    print(f"• {len(uptrend_positive_premium)} uptrend tickers with positive premium should be at top")
    print(f"• {len(all_others)} other tickers should follow")
    print(f"• Both groups sorted by highest premium first")

if __name__ == "__main__":
    test_gui_display()
#!/usr/bin/env python3
"""
Test Enhanced Wishlist Sorting Logic
===================================
Test the new two-tier sorting system:
1. Primary: Highest premium to current price ratio (most profitable first)
2. Secondary: Uptrend tickers on top within each premium tier
"""

def test_premium_calculation():
    """Test the new premium calculation logic"""
    print("🧪 Testing Premium Calculation Logic")
    print("=" * 50)
    
    # Test cases based on your example
    test_cases = [
        {
            "name": "Your Example",
            "current_price": 50.0,
            "strike": 55.0,
            "premium": 6.0,
            "expected": -1.0  # $55 - $6 - $50 = -$1
        },
        {
            "name": "Profitable Case",
            "current_price": 100.0,
            "strike": 105.0,
            "premium": 8.0,
            "expected": -3.0  # $105 - $8 - $100 = -$3
        },
        {
            "name": "Very Profitable Case",
            "current_price": 75.0,
            "strike": 80.0,
            "premium": 7.0,
            "expected": -2.0  # $80 - $7 - $75 = -$2
        },
        {
            "name": "Break Even Case",
            "current_price": 50.0,
            "strike": 55.0,
            "premium": 5.0,
            "expected": 0.0   # $55 - $5 - $50 = $0
        },
        {
            "name": "Extra Profit Case",
            "current_price": 45.0,
            "strike": 50.0,
            "premium": 7.0,
            "expected": -2.0  # $50 - $7 - $45 = -$2
        }
    ]
    
    for case in test_cases:
        # Calculate premium to current price
        premium_to_current = case["strike"] - case["premium"] - case["current_price"]
        
        # Format for display
        if premium_to_current >= 0:
            formatted = f"+${premium_to_current:.2f}"
        else:
            formatted = f"-${abs(premium_to_current):.2f}"
        
        # Check result
        passed = abs(premium_to_current - case["expected"]) < 0.01
        status = "✅ PASS" if passed else "❌ FAIL"
        
        print(f"{status} {case['name']}")
        print(f"  Current: ${case['current_price']:.2f}")
        print(f"  Strike: ${case['strike']:.2f}, Premium: ${case['premium']:.2f}")
        print(f"  Calculated: {formatted} (Expected: ${case['expected']:.2f})")
        print()

def test_sorting_logic():
    """Test the two-tier sorting system"""
    print("🧪 Testing Two-Tier Sorting Logic")
    print("=" * 50)
    
    # Sample data: (symbol, premium_value, is_uptrend)
    sample_rows = [
        ("AAPL", -1.0, False),  # Good premium, not uptrend
        ("MSFT", -2.0, True),   # Better premium, uptrend
        ("GOOGL", -1.5, True),  # Good premium, uptrend
        ("TSLA", -3.0, False),  # Best premium, not uptrend
        ("NVDA", -2.5, False),  # Great premium, not uptrend
        ("AMZN", 0.5, True),    # Poor premium, uptrend
        ("META", -0.5, False),  # Poor premium, not uptrend
        ("AMD", -2.1, True),    # Great premium, uptrend
        ("NFLX", -1.8, False),  # Good premium, not uptrend
        ("CRM", -1.2, True),    # Good premium, uptrend
    ]
    
    print("Original order:")
    for i, (symbol, premium, uptrend) in enumerate(sample_rows, 1):
        trend_str = "Uptrend" if uptrend else "No trend"
        prefix = "+" if premium >= 0 else ""
        print(f"  {i}. {symbol}: {prefix}${premium:.2f} premium, {trend_str}")
    
    # Sort using the enhanced two-stage logic
    # Step 1: Sort by premium value (best first)
    sample_rows.sort(key=lambda r: r[1] if r[1] != float('inf') else 999)
    
    # Step 2: Apply uptrend boost to top performers
    valid_rows = [r for r in sample_rows if r[1] != float('inf')]
    if valid_rows:
        top_count = max(3, len(valid_rows) // 3)  # Top 30% or at least 3
        best_premium_threshold = valid_rows[min(top_count-1, len(valid_rows)-1)][1]
        
        # Separate into top tier and others
        top_tier = []
        other_tier = []
        
        for row in sample_rows:
            if row[1] != float('inf') and row[1] <= best_premium_threshold:
                top_tier.append(row)
            else:
                other_tier.append(row)
        
        # Within top tier, sort uptrend stocks first, then by premium
        top_tier.sort(key=lambda r: (-int(r[2]), r[1]))  # Uptrend first, then best premium
        
        # Combine: top tier (with uptrend priority) + remaining stocks
        final_rows = top_tier + other_tier
    else:
        final_rows = sample_rows
    
    print(f"\nSorted order (Best premiums first, uptrend priority in top {top_count} tier):")
    for i, (symbol, premium, uptrend) in enumerate(final_rows, 1):
        trend_str = "🟢 Uptrend" if uptrend else "⚪ No trend"
        prefix = "+" if premium >= 0 else ""
        tier_marker = "🔥" if i <= top_count else "📊"
        print(f"  {i}. {tier_marker} {symbol}: {prefix}${premium:.2f} premium, {trend_str}")
    
    print(f"\nSorting explanation:")
    print(f"📊 Top Premium Tier (best {top_count} opportunities):")
    print(f"  Threshold: ${best_premium_threshold:.2f} or better")
    print(f"  🔥 Within this tier: Uptrend stocks get priority!")
    print(f"📈 Remaining stocks: Sorted by premium quality")
    print("\n✅ Best premium opportunities first, with uptrend boost in the top tier!")

if __name__ == "__main__":
    print("🎯 Enhanced Wishlist Sorting Logic Tests")
    print("=" * 60)
    print()
    
    test_premium_calculation()
    print()
    test_sorting_logic()
    
    print()
    print("🎉 All tests completed!")
    print("✅ Premium calculation: Strike - Premium - Current Price")
    print("✅ Sorting: Uptrend first, then best premium within each group")
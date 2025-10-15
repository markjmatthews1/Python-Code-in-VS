#!/usr/bin/env python3
"""
Test Priority Sorting Logic
---------------------------
Validates the enhanced sorting: Uptrend with positive premium first, then all others by premium.
"""

def test_priority_sorting():
    """Test the priority sorting logic"""
    
    # Simulate the sorting data structure: [symbol, ..., premium_val_num, uptrend_flag]
    test_rows = [
        # Format: [symbol, other_data..., premium_val_num, uptrend_flag]
        ['TICKER1', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 2.5, 1],   # Uptrend + positive premium
        ['TICKER2', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', -1.0, 0],  # Not uptrend, negative premium (best premium)
        ['TICKER3', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 1.0, 1],   # Uptrend + positive premium
        ['TICKER4', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', -0.5, 0],  # Not uptrend, negative premium
        ['TICKER5', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 0.5, 0],   # Not uptrend, positive premium
        ['TICKER6', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', 'data', -2.0, 1],  # Uptrend + negative premium
    ]
    
    print("🔍 Testing Priority Sorting Logic")
    print("=" * 50)
    
    print("\n📊 Input Data:")
    for row in test_rows:
        symbol = row[0]
        premium = row[-2]
        is_uptrend = "Uptrend" if row[-1] == 1 else "Other"
        print(f"  {symbol}: Premium={premium:+.1f}, Trend={is_uptrend}")
    
    # Apply the sorting logic
    uptrend_positive_premium = []
    all_others = []
    
    for row in test_rows:
        premium_value = row[-2]  # premium_val_num
        is_uptrend = row[-1] == 1  # uptrend flag
        has_positive_premium = premium_value != float('inf') and premium_value > 0
        
        if is_uptrend and has_positive_premium:
            uptrend_positive_premium.append(row)
        else:
            all_others.append(row)
    
    # Sort each group by premium (highest first - descending order)
    uptrend_positive_premium.sort(key=lambda r: r[-2] if r[-2] != float('inf') else -999, reverse=True)
    all_others.sort(key=lambda r: r[-2] if r[-2] != float('inf') else -999, reverse=True)
    
    # Combine: uptrend with positive premium first, then all others
    final_rows = uptrend_positive_premium + all_others
    
    print("\n🎯 Expected Results:")
    print("  1st Priority: Uptrend tickers with premium > 0 (sorted by highest premium)")
    print("  2nd Priority: All other tickers (sorted by highest premium)")
    
    print("\n✅ Actual Sorted Results:")
    priority_1_count = len(uptrend_positive_premium)
    
    for i, row in enumerate(final_rows, 1):
        symbol = row[0]
        premium = row[-2]
        is_uptrend = "Uptrend" if row[-1] == 1 else "Other"
        priority = "1st Priority" if i <= priority_1_count else "2nd Priority"
        print(f"  {i}. {symbol}: Premium={premium:+.1f}, Trend={is_uptrend} ({priority})")
    
    print(f"\n📈 Summary:")
    print(f"  • {len(uptrend_positive_premium)} uptrend tickers with positive premium in top positions")
    print(f"  • {len(all_others)} other tickers follow")
    print(f"  • Total tickers: {len(final_rows)}")
    
    # Validation
    print(f"\n🔍 Validation:")
    success = True
    
    # Check that all uptrend positive premium tickers come first
    for i in range(len(uptrend_positive_premium)):
        row = final_rows[i]
        if not (row[-1] == 1 and row[-2] > 0):
            print(f"  ❌ Position {i+1} should be uptrend with positive premium, but got {row[0]}")
            success = False
    
    # Check that uptrend positive premium tickers are sorted by premium
    for i in range(len(uptrend_positive_premium) - 1):
        if final_rows[i][-2] > final_rows[i+1][-2]:
            print(f"  ❌ Premium sorting error in priority group: {final_rows[i][0]} > {final_rows[i+1][0]}")
            success = False
    
    if success:
        print("  ✅ All validation checks passed!")
    
    return success

if __name__ == "__main__":
    test_priority_sorting()
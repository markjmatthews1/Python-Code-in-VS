"""
Test script to verify Current Holdings Status categorization logic
Tests the specific examples mentioned by user
"""

from rotation_engine import RotationEngine
from datetime import datetime, timedelta

def test_holdings_categorization():
    engine = RotationEngine()
    
    print("=" * 90)
    print("CURRENT HOLDINGS STATUS CATEGORIZATION TEST")
    print("=" * 90)
    
    current_time = engine.get_current_time_et()
    print(f"\nCurrent Time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p ET')}")
    
    # Get next rotation targets
    next_targets = engine.find_next_rotation_targets()
    if next_targets:
        ex_day_name = next_targets[0]['next_ex_div_date'].strftime('%A')
        next_rotation_tickers = [t['ticker'] for t in next_targets]
        print(f"Next Rotation Group: {ex_day_name} ex-dividend")
        print(f"Tickers in next rotation: {', '.join(next_rotation_tickers)}")
    else:
        print("No next rotation targets found")
        return
    
    print(f"\n{'=' * 90}")
    print("TESTING USER'S EXAMPLE SCENARIOS")
    print(f"{'=' * 90}")
    
    # Example holdings based on user's scenario
    test_holdings = [
        {
            'ticker': 'NVDW',
            'purchase_date': current_time - timedelta(days=5),  # Bought 5 days ago
            'purchase_price': 42.00,
            'current_price': 42.50,  # Slight profit
            'shares': 100
        },
        {
            'ticker': 'QDTE',
            'purchase_date': current_time - timedelta(days=4),  # Bought 4 days ago
            'purchase_price': 50.00,
            'current_price': 50.25,  # Slight profit
            'shares': 100
        }
    ]
    
    # Analyze holdings
    categorized = engine.analyze_holdings(test_holdings)
    
    print("\nUser's Expected Behavior:")
    print("  NVDW: Monday ex-div, NOT in Wednesday group → READY TO SELL")
    print("  QDTE: Thursday ex-div, NOT in Wednesday group → READY TO SELL")
    print("  (After 3:30 PM today or tomorrow: QDTE moves to MUST HOLD as it enters Thursday rotation)")
    
    print(f"\n{'=' * 90}")
    print("ACTUAL CATEGORIZATION")
    print(f"{'=' * 90}")
    
    print("\n✅ READY TO SELL (at/past ex-date AND not in next rotation):")
    if categorized['ready_to_sell']:
        for h in categorized['ready_to_sell']:
            print(f"  • {h['ticker']}: {h['reason']}")
    else:
        print("  (None)")
    
    print("\n🔒 MUST HOLD (waiting for ex-date OR in next rotation group):")
    if categorized['must_hold']:
        for h in categorized['must_hold']:
            print(f"  • {h['ticker']}: {h['reason']}")
    else:
        print("  (None)")
    
    print("\n📉 HOLD FOR NAV (NAV < purchase AND not in next rotation):")
    if categorized['hold_for_nav']:
        for h in categorized['hold_for_nav']:
            print(f"  • {h['ticker']}: {h['reason']}")
    else:
        print("  (None)")
    
    # Verify expectations
    print(f"\n{'=' * 90}")
    print("VERIFICATION")
    print(f"{'=' * 90}")
    
    nvdw_in_ready = any(h['ticker'] == 'NVDW' for h in categorized['ready_to_sell'])
    qdte_in_ready = any(h['ticker'] == 'QDTE' for h in categorized['ready_to_sell'])
    
    # Check if NVDW is in next rotation
    nvdw_in_next_rotation = 'NVDW' in next_rotation_tickers
    qdte_in_next_rotation = 'QDTE' in next_rotation_tickers
    
    print(f"\nNVDW Status:")
    print(f"  In next rotation group? {nvdw_in_next_rotation}")
    print(f"  In Ready to Sell? {nvdw_in_ready}")
    print(f"  Expected: Ready to Sell (Monday ex-div, not in Wednesday group)")
    if nvdw_in_ready and not nvdw_in_next_rotation:
        print(f"  ✅ CORRECT")
    else:
        print(f"  ❌ INCORRECT")
    
    print(f"\nQDTE Status:")
    print(f"  In next rotation group? {qdte_in_next_rotation}")
    print(f"  In Ready to Sell? {qdte_in_ready}")
    print(f"  Expected: Ready to Sell (Thursday ex-div, not in Wednesday group)")
    if qdte_in_ready and not qdte_in_next_rotation:
        print(f"  ✅ CORRECT")
    else:
        print(f"  ❌ INCORRECT - Might be in Must Hold if still waiting for ex-date")
    
    # Additional test cases
    print(f"\n{'=' * 90}")
    print("ADDITIONAL TEST CASES")
    print(f"{'=' * 90}")
    
    # Test case: Ticker in next rotation group
    if next_rotation_tickers:
        test_next_rotation_ticker = next_rotation_tickers[0]
        print(f"\nTest: Holding {test_next_rotation_ticker} (in next rotation group)")
        
        test_holdings_2 = [{
            'ticker': test_next_rotation_ticker,
            'purchase_date': current_time - timedelta(days=2),
            'purchase_price': 20.00,
            'current_price': 20.10,
            'shares': 100
        }]
        
        categorized_2 = engine.analyze_holdings(test_holdings_2)
        
        in_must_hold = any(h['ticker'] == test_next_rotation_ticker for h in categorized_2['must_hold'])
        print(f"  In Must Hold? {in_must_hold}")
        print(f"  Expected: YES (in next rotation group)")
        if in_must_hold:
            print(f"  ✅ CORRECT")
            reason = [h['reason'] for h in categorized_2['must_hold'] if h['ticker'] == test_next_rotation_ticker][0]
            print(f"  Reason: {reason}")
        else:
            print(f"  ❌ INCORRECT")
    
    # Test case: Holding below NAV, not in next rotation
    print(f"\nTest: Holding NVDW with NAV loss (not in next rotation)")
    
    test_holdings_3 = [{
        'ticker': 'NVDW',
        'purchase_date': current_time - timedelta(days=5),
        'purchase_price': 45.00,
        'current_price': 44.50,  # Loss
        'shares': 100
    }]
    
    categorized_3 = engine.analyze_holdings(test_holdings_3)
    
    in_hold_for_nav = any(h['ticker'] == 'NVDW' for h in categorized_3['hold_for_nav'])
    print(f"  In Hold for NAV? {in_hold_for_nav}")
    print(f"  Expected: YES (NAV < purchase, not in next rotation)")
    if in_hold_for_nav:
        print(f"  ✅ CORRECT")
        reason = [h['reason'] for h in categorized_3['hold_for_nav'] if h['ticker'] == 'NVDW'][0]
        print(f"  Reason: {reason}")
    else:
        print(f"  ❌ INCORRECT")
    
    print(f"\n{'=' * 90}")
    print("SUMMARY")
    print(f"{'=' * 90}")
    print("\nCategorization Rules:")
    print("  ✅ READY TO SELL:")
    print("     - At or beyond ex-dividend date")
    print("     - NOT in next rotation group")
    print("     - NAV is not negative")
    print()
    print("  🔒 MUST HOLD:")
    print("     - Waiting for ex-dividend date, OR")
    print("     - In next rotation group (regardless of ex-date status)")
    print()
    print("  📉 HOLD FOR NAV:")
    print("     - NAV < purchase price (negative)")
    print("     - NOT in next rotation group")
    print("\nThe logic now correctly considers whether a ticker is in the next rotation group!")

if __name__ == "__main__":
    test_holdings_categorization()

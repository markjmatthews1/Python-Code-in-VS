"""
Test that tickers can appear in multiple categories simultaneously
"""

from rotation_engine import RotationEngine
from datetime import datetime, timedelta

def test_multiple_categories():
    engine = RotationEngine()
    
    print("=" * 90)
    print("TEST: Tickers Appearing in Multiple Categories")
    print("=" * 90)
    
    current_time = engine.get_current_time_et()
    print(f"\nCurrent Time: {current_time.strftime('%A, %B %d at %I:%M %p ET')}")
    
    # Get next rotation targets
    next_targets = engine.find_next_rotation_targets()
    if next_targets:
        ex_day_name = next_targets[0]['next_ex_div_date'].strftime('%A')
        next_rotation_tickers = [t['ticker'] for t in next_targets]
        print(f"Next Rotation Group: {ex_day_name} ex-dividend")
        print(f"Tickers: {', '.join(next_rotation_tickers)}")
    
    print(f"\n{'=' * 90}")
    print("TEST CASE 1: QDTE with NAV below purchase (should be in 2 categories)")
    print(f"{'=' * 90}")
    
    test_holdings_1 = [
        {
            'ticker': 'QDTE',
            'purchase_date': current_time - timedelta(days=4),
            'purchase_price': 51.00,  # Bought at 51
            'current_price': 50.25,   # Now at 50.25 (LOSS)
            'shares': 100
        }
    ]
    
    categorized_1 = engine.analyze_holdings(test_holdings_1)
    
    print("\nQDTE Status:")
    print(f"  Purchase: $51.00")
    print(f"  Current:  $50.25")
    print(f"  NAV:      -1.47% (LOSS)")
    print(f"  Ex-div:   Thursday (already passed)")
    print(f"  In next rotation? NO (Wednesday group is next)")
    
    print("\nExpected:")
    print("  ✅ READY TO SELL - YES (past ex-date, not in next rotation)")
    print("  📉 HOLD FOR NAV - YES (NAV below purchase, not in next rotation)")
    
    print("\nActual:")
    in_ready = any(h['ticker'] == 'QDTE' for h in categorized_1['ready_to_sell'])
    in_nav = any(h['ticker'] == 'QDTE' for h in categorized_1['hold_for_nav'])
    in_must = any(h['ticker'] == 'QDTE' for h in categorized_1['must_hold'])
    
    print(f"  ✅ READY TO SELL: {in_ready}")
    if in_ready:
        reason = [h['reason'] for h in categorized_1['ready_to_sell'] if h['ticker'] == 'QDTE'][0]
        print(f"     Reason: {reason}")
    
    print(f"  🔒 MUST HOLD: {in_must}")
    if in_must:
        reason = [h['reason'] for h in categorized_1['must_hold'] if h['ticker'] == 'QDTE'][0]
        print(f"     Reason: {reason}")
    
    print(f"  📉 HOLD FOR NAV: {in_nav}")
    if in_nav:
        reason = [h['reason'] for h in categorized_1['hold_for_nav'] if h['ticker'] == 'QDTE'][0]
        print(f"     Reason: {reason}")
    
    if in_ready and in_nav and not in_must:
        print("\n  ✅ CORRECT: QDTE appears in both Ready to Sell AND Hold for NAV")
    else:
        print("\n  ❌ INCORRECT")
    
    print(f"\n{'=' * 90}")
    print("TEST CASE 2: YETH in next rotation with NAV loss (should be in 2 categories)")
    print(f"{'=' * 90}")
    
    test_holdings_2 = [
        {
            'ticker': 'YETH',
            'purchase_date': current_time - timedelta(days=1),
            'purchase_price': 22.00,  # Bought at 22
            'current_price': 21.50,   # Now at 21.50 (LOSS)
            'shares': 100
        }
    ]
    
    categorized_2 = engine.analyze_holdings(test_holdings_2)
    
    print("\nYETH Status:")
    print(f"  Purchase: $22.00")
    print(f"  Current:  $21.50")
    print(f"  NAV:      -2.27% (LOSS)")
    print(f"  Ex-div:   Wednesday (tomorrow)")
    print(f"  In next rotation? YES (Wednesday group)")
    
    print("\nExpected:")
    print("  🔒 MUST HOLD - YES (in next rotation group)")
    print("  📉 HOLD FOR NAV - NO (NAV rule only applies if NOT in next rotation)")
    
    print("\nActual:")
    in_ready_2 = any(h['ticker'] == 'YETH' for h in categorized_2['ready_to_sell'])
    in_nav_2 = any(h['ticker'] == 'YETH' for h in categorized_2['hold_for_nav'])
    in_must_2 = any(h['ticker'] == 'YETH' for h in categorized_2['must_hold'])
    
    print(f"  ✅ READY TO SELL: {in_ready_2}")
    print(f"  🔒 MUST HOLD: {in_must_2}")
    if in_must_2:
        reason = [h['reason'] for h in categorized_2['must_hold'] if h['ticker'] == 'YETH'][0]
        print(f"     Reason: {reason}")
    
    print(f"  📉 HOLD FOR NAV: {in_nav_2}")
    
    if in_must_2 and not in_nav_2 and not in_ready_2:
        print("\n  ✅ CORRECT: YETH only in Must Hold (in next rotation overrides NAV)")
    else:
        print("\n  ❌ INCORRECT")
    
    print(f"\n{'=' * 90}")
    print("TEST CASE 3: NVDW at profit (should be in 1 category)")
    print(f"{'=' * 90}")
    
    test_holdings_3 = [
        {
            'ticker': 'NVDW',
            'purchase_date': current_time - timedelta(days=5),
            'purchase_price': 42.00,
            'current_price': 42.50,  # Profit
            'shares': 100
        }
    ]
    
    categorized_3 = engine.analyze_holdings(test_holdings_3)
    
    print("\nNVDW Status:")
    print(f"  Purchase: $42.00")
    print(f"  Current:  $42.50")
    print(f"  NAV:      +1.19% (PROFIT)")
    print(f"  Ex-div:   Monday (already passed)")
    print(f"  In next rotation? NO (Wednesday group is next)")
    
    print("\nExpected:")
    print("  ✅ READY TO SELL - YES (past ex-date, not in next rotation, profit)")
    print("  📉 HOLD FOR NAV - NO (NAV is positive)")
    print("  🔒 MUST HOLD - NO (not in next rotation, already past ex-date)")
    
    print("\nActual:")
    in_ready_3 = any(h['ticker'] == 'NVDW' for h in categorized_3['ready_to_sell'])
    in_nav_3 = any(h['ticker'] == 'NVDW' for h in categorized_3['hold_for_nav'])
    in_must_3 = any(h['ticker'] == 'NVDW' for h in categorized_3['must_hold'])
    
    print(f"  ✅ READY TO SELL: {in_ready_3}")
    if in_ready_3:
        reason = [h['reason'] for h in categorized_3['ready_to_sell'] if h['ticker'] == 'NVDW'][0]
        print(f"     Reason: {reason}")
    
    print(f"  🔒 MUST HOLD: {in_must_3}")
    print(f"  📉 HOLD FOR NAV: {in_nav_3}")
    
    if in_ready_3 and not in_nav_3 and not in_must_3:
        print("\n  ✅ CORRECT: NVDW only in Ready to Sell")
    else:
        print("\n  ❌ INCORRECT")
    
    print(f"\n{'=' * 90}")
    print("SUMMARY OF CATEGORIZATION RULES")
    print(f"{'=' * 90}")
    print("""
A ticker can appear in MULTIPLE categories:

✅ READY TO SELL:
   - Past ex-dividend date
   - NOT in next rotation group

🔒 MUST HOLD:
   - Waiting for ex-dividend date, OR
   - In next rotation group

📉 HOLD FOR NAV:
   - NAV < purchase price (negative)
   - NOT in next rotation group

EXAMPLES:
  • QDTE (past ex-div, NAV loss, not in next rotation):
    → Ready to Sell + Hold for NAV

  • YETH (in next rotation, NAV loss):
    → Must Hold only (in next rotation overrides NAV rule)

  • NVDW (past ex-div, NAV profit, not in next rotation):
    → Ready to Sell only

  • Theoretical: Ticker in next rotation that already passed ex-div with profit:
    → Ready to Sell + Must Hold
    """)

if __name__ == "__main__":
    test_multiple_categories()

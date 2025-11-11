"""
Simulate how holdings categorization changes over time
Shows what happens as rotation groups change
"""

from rotation_engine import RotationEngine
from datetime import datetime, timedelta

def simulate_rotation_changes():
    engine = RotationEngine()
    
    print("=" * 90)
    print("HOLDINGS CATEGORIZATION - TIME-BASED SIMULATION")
    print("=" * 90)
    
    current_time = engine.get_current_time_et()
    
    # Sample holdings (as if purchased days ago)
    holdings = [
        {
            'ticker': 'NVDW',  # Monday ex-div
            'purchase_date': current_time - timedelta(days=5),
            'purchase_price': 42.00,
            'current_price': 42.50,
            'shares': 100
        },
        {
            'ticker': 'QDTE',  # Thursday ex-div
            'purchase_date': current_time - timedelta(days=4),
            'purchase_price': 50.00,
            'current_price': 50.25,
            'shares': 100
        },
        {
            'ticker': 'YETH',  # Wednesday ex-div (in next rotation TODAY)
            'purchase_date': current_time - timedelta(days=1),
            'purchase_price': 21.00,
            'current_price': 21.15,
            'shares': 100
        }
    ]
    
    print(f"\nCurrent Time: {current_time.strftime('%A, %B %d at %I:%M %p ET')}")
    print(f"\nSample Holdings:")
    for h in holdings:
        print(f"  • {h['ticker']}: Purchased {(current_time - h['purchase_date']).days} days ago")
    
    # Get current rotation targets
    next_targets = engine.find_next_rotation_targets()
    if next_targets:
        ex_day = next_targets[0]['next_ex_div_date'].strftime('%A')
        next_tickers = [t['ticker'] for t in next_targets]
        print(f"\nNext Rotation Group: {ex_day}")
        print(f"  Tickers: {', '.join(next_tickers)}")
    
    print(f"\n{'=' * 90}")
    print("SCENARIO 1: RIGHT NOW (Tuesday morning, before 3:30 PM)")
    print(f"{'=' * 90}")
    print("Next rotation showing: Wednesday group")
    
    categorized = engine.analyze_holdings(holdings)
    
    print("\n✅ READY TO SELL:")
    if categorized['ready_to_sell']:
        for h in categorized['ready_to_sell']:
            print(f"  • {h['ticker']}: {h['reason']}")
    else:
        print("  (None)")
    
    print("\n🔒 MUST HOLD:")
    if categorized['must_hold']:
        for h in categorized['must_hold']:
            print(f"  • {h['ticker']}: {h['reason']}")
    else:
        print("  (None)")
    
    print("\n📉 HOLD FOR NAV:")
    if categorized['hold_for_nav']:
        for h in categorized['hold_for_nav']:
            print(f"  • {h['ticker']}: {h['reason']}")
    else:
        print("  (None)")
    
    print(f"\n{'=' * 90}")
    print("SCENARIO 2: AFTER 3:30 PM TODAY (or Wednesday morning)")
    print(f"{'=' * 90}")
    print("Next rotation will show: Thursday group (QDTE and others)")
    print("\nExpected changes:")
    print("  • NVDW: Still in READY TO SELL (not in Thursday rotation)")
    print("  • QDTE: Moves to MUST HOLD (now in Thursday rotation group)")
    print("  • YETH: Moves to READY TO SELL (Wednesday ex-div passed)")
    
    print(f"\n{'=' * 90}")
    print("KEY INSIGHTS")
    print(f"{'=' * 90}")
    print("""
The categorization is DYNAMIC based on:
  
1. Whether the ticker is in the NEXT rotation group
   - If YES → MUST HOLD (even if already past ex-date)
   - If NO → READY TO SELL (if past ex-date and NAV OK)

2. Whether the holding has passed through its ex-dividend cycle
   - Checked against last_ex_date in settings
   - Must be held at least 2 days to have passed a cycle

3. Current NAV status
   - If NAV < purchase AND not in next rotation → HOLD FOR NAV
   - Takes priority over other rules

EXAMPLE TIMELINE for QDTE (Thursday ex-dividend):
  
  Tuesday (now):
    - Last ex-div: Thursday 11/7 (passed)
    - Next ex-div: Thursday 11/14 (future) 
    - Next rotation: Wednesday group
    - Status: ✅ READY TO SELL (not in current rotation)
  
  After Tuesday 3:30 PM:
    - Rotation switches to Thursday group
    - Next rotation: Thursday group (includes QDTE)
    - Status: 🔒 MUST HOLD (now in current rotation)
  
  Friday morning:
    - Passed Thursday ex-div
    - Next rotation: Monday group
    - Status: ✅ READY TO SELL (not in current rotation)

This creates a natural rotation cycle where you hold leading up to ex-date,
then sell to free capital once dividend is captured (unless it's needed
again for the next rotation)!
    """)

if __name__ == "__main__":
    simulate_rotation_changes()

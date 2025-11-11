"""
Test script to verify the "next available group" rotation logic
"""

from rotation_engine import RotationEngine
from datetime import datetime

def test_next_group_logic():
    engine = RotationEngine()
    
    print("=" * 80)
    print("TESTING: Next Available Ex-Date Group Logic")
    print("=" * 80)
    
    current_time = engine.get_current_time_et()
    print(f"\nCurrent Time: {current_time.strftime('%A, %B %d, %Y at %I:%M %p ET')}")
    print(f"Current Day: {current_time.strftime('%A')}")
    
    # Get next rotation targets (should only show ONE group)
    targets = engine.find_next_rotation_targets()
    
    print(f"\n{'=' * 80}")
    print(f"NEXT AVAILABLE ROTATION GROUP ({len(targets)} tickers)")
    print(f"{'=' * 80}")
    
    if not targets:
        print("\n⚠️  No upcoming rotation targets found (all deadlines may have passed)")
        return
    
    # Show the group's ex-dividend date
    ex_date = targets[0]['next_ex_div_date']
    print(f"\n📅 Ex-Dividend Date: {ex_date.strftime('%A, %B %d, %Y')}")
    print(f"⏰ Must Purchase By: {targets[0]['buy_deadline'].strftime('%A, %B %d at %I:%M %p ET')}")
    print(f"\n{'Ticker':<8} {'Name':<45} {'Ex-Date':<12} {'Buy Deadline':<25}")
    print("-" * 90)
    
    for target in targets:
        print(f"{target['ticker']:<8} {target['name'][:44]:<45} "
              f"{target['next_ex_div_date'].strftime('%a %m/%d'):<12} "
              f"{target['deadline_description']:<25}")
    
    # Verify all targets have the same ex-dividend date
    print(f"\n{'=' * 80}")
    print("VERIFICATION: All tickers in this group have the same ex-dividend date")
    print(f"{'=' * 80}")
    
    unique_ex_dates = set(t['next_ex_div_date'].date() for t in targets)
    if len(unique_ex_dates) == 1:
        print("✅ PASS: All tickers share the same ex-dividend date")
    else:
        print(f"❌ FAIL: Found {len(unique_ex_dates)} different ex-dividend dates!")
        for date in sorted(unique_ex_dates):
            count = sum(1 for t in targets if t['next_ex_div_date'].date() == date)
            print(f"   - {date.strftime('%A, %B %d')}: {count} tickers")
    
    # Show what comes next (if we had more days)
    print(f"\n{'=' * 80}")
    print("LOGIC EXPLANATION")
    print(f"{'=' * 80}")
    print("\nThe rotation engine now shows ONLY the next available ex-date group.")
    print("Once the deadline passes for this group, it will automatically show the next group.")
    print("\nExample timeline:")
    print("  Monday morning   → Shows Wednesday ex-date group (buy by Tuesday 3:30pm)")
    print("  Tuesday 4:00pm   → Too late for Wednesday, shows Thursday group")
    print("  Wednesday 4:00pm → Too late for Thursday, shows Monday group")
    print("\nThis ensures you always see the most relevant buy recommendations!")

if __name__ == "__main__":
    test_next_group_logic()

"""
Test script for Rotation Engine
Shows how it analyzes your current holdings (NVDW, XOMO, QDTE)
"""

from datetime import datetime
import pytz
from rotation_engine import RotationEngine

# Initialize engine
engine = RotationEngine()

# Get current time
current_time = engine.get_current_time_et()
print(f"=" * 70)
print(f"ROTATION ENGINE TEST - {current_time.strftime('%A, %B %d, %Y at %I:%M %p ET')}")
print(f"=" * 70)
print()

# Test market status
is_open = engine.is_market_open()
print(f"📊 Market Status: {'🟢 OPEN' if is_open else '🔴 CLOSED'}")
print()

# Simulate your current holdings
# You mentioned: NVDW, XOMO, QDTE
eastern = pytz.timezone('America/New_York')

holdings = [
    {
        'ticker': 'NVDW',
        'purchase_date': eastern.localize(datetime(2025, 11, 4, 10, 0)),  # Bought Monday 11/4
        'purchase_price': 42.20,
        'current_price': 42.50,  # Simulated current price
        'shares': 100
    },
    {
        'ticker': 'XOMO',
        'purchase_date': eastern.localize(datetime(2025, 11, 5, 10, 0)),  # Bought Tuesday 11/5
        'purchase_price': 28.90,
        'current_price': 28.75,  # Simulated - at a loss
        'shares': 100
    },
    {
        'ticker': 'QDTE',
        'purchase_date': eastern.localize(datetime(2025, 11, 5, 10, 0)),  # Bought Tuesday 11/5
        'purchase_price': 35.10,
        'current_price': 35.15,  # Simulated - small profit
        'shares': 100
    }
]

print(f"💼 YOUR CURRENT HOLDINGS:")
print(f"-" * 70)
for h in holdings:
    print(f"  {h['ticker']}: {h['shares']} shares @ ${h['purchase_price']} (now ${h['current_price']})")
print()

# Analyze holdings
print(f"🔍 ANALYZING HOLDINGS...")
print(f"=" * 70)
categorized = engine.analyze_holdings(holdings)

print(f"\n✅ READY TO SELL (Dividend received + profitable):")
print(f"-" * 70)
if categorized['ready_to_sell']:
    for h in categorized['ready_to_sell']:
        print(f"  • {h['ticker']}")
        print(f"    Purchase: ${h['purchase_price']} → Current: ${h['current_price']}")
        print(f"    NAV: {h['nav_pct']:+.2f}% ({h['nav_status']})")
        print(f"    Dividend: {h['dividend_status']}")
        print(f"    Days held: {h['days_held']}")
        print(f"    ✓ {h['reason']}")
        print()
else:
    print("  (None)")
print()

print(f"🔒 MUST HOLD (Pre ex-dividend):")
print(f"-" * 70)
if categorized['must_hold']:
    for h in categorized['must_hold']:
        print(f"  • {h['ticker']}")
        print(f"    Purchase: ${h['purchase_price']} → Current: ${h['current_price']}")
        print(f"    NAV: {h['nav_pct']:+.2f}% ({h['nav_status']})")
        print(f"    Dividend: {h['dividend_status']}")
        print(f"    ✗ {h['reason']}")
        print()
else:
    print("  (None)")
print()

print(f"🔴 HOLD FOR NAV (At a loss):")
print(f"-" * 70)
if categorized['hold_for_nav']:
    for h in categorized['hold_for_nav']:
        print(f"  • {h['ticker']}")
        print(f"    Purchase: ${h['purchase_price']} → Current: ${h['current_price']}")
        print(f"    NAV: {h['nav_pct']:+.2f}% ({h['nav_status']})")
        print(f"    Dividend: {h['dividend_status']}")
        print(f"    ✗ {h['reason']}")
        print()
else:
    print("  (None)")
print()

# Find next rotation targets
print(f"🎯 NEXT ROTATION OPPORTUNITIES:")
print(f"=" * 70)
next_targets = engine.find_next_rotation_targets()

if next_targets:
    for i, target in enumerate(next_targets[:5], 1):  # Show top 5
        urgency = "⏰ URGENT!" if target['is_urgent'] else "📅 Upcoming"
        print(f"{i}. {target['ticker']} - {urgency}")
        print(f"   Name: {target['name']}")
        print(f"   Ex-Dividend: {target['next_ex_div_date'].strftime('%A, %B %d, %Y')}")
        print(f"   Buy Deadline: {target['deadline_description']}")
        print(f"   Pays on: {target['pay_day']}")
        print()
else:
    print("  (No upcoming opportunities in next 2 days)")
print()

# Get rotation alert
print(f"🚨 ROTATION ALERT:")
print(f"=" * 70)
alert = engine.get_rotation_alert(holdings)

print(f"Urgency: {alert['urgency'].upper()}")
print(f"Message: {alert['message']}")
print()

if alert['actions']:
    print(f"RECOMMENDED ACTIONS:")
    for action in alert['actions']:
        if action['type'] == 'sell':
            print(f"  📤 SELL {action['ticker']}")
            print(f"     NAV: {action['nav_pct']:+.2f}%")
            print(f"     {action['reason']}")
        elif action['type'] == 'buy':
            print(f"  📥 BUY {action['ticker']}")
            print(f"     Deadline: {action['deadline']}")
            print(f"     Ex-Div: {action['ex_div_date']}")
        print()

print(f"=" * 70)
print(f"✅ Test complete!")

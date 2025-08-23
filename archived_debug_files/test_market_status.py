#!/usr/bin/env python3

def get_market_status_detailed():
    """
    Returns detailed market status including weekends and holidays.
    Returns: (is_open, status_message, explanation)
    """
    from datetime import datetime
    import pytz
    
    # US market holidays (static for 2025)
    us_market_holidays_2025 = set([
        datetime(2025, 1, 1).date(),   # New Year's Day
        datetime(2025, 1, 20).date(),  # Martin Luther King Jr. Day
        datetime(2025, 2, 17).date(),  # Presidents' Day
        datetime(2025, 4, 18).date(),  # Good Friday
        datetime(2025, 5, 26).date(),  # Memorial Day
        datetime(2025, 6, 19).date(),  # Juneteenth
        datetime(2025, 7, 4).date(),   # Independence Day
        datetime(2025, 9, 1).date(),   # Labor Day
        datetime(2025, 11, 27).date(), # Thanksgiving
        datetime(2025, 12, 25).date(), # Christmas
    ])
    
    now = datetime.now(pytz.timezone("US/Eastern"))
    today_date = now.date()
    weekday = now.weekday()  # 0=Monday, 6=Sunday
    
    print(f"🔍 Debug Info:")
    print(f"  Current time (ET): {now}")
    print(f"  Today's date: {today_date}")
    print(f"  Weekday: {weekday} (0=Monday, 6=Sunday)")
    print(f"  Day name: {now.strftime('%A')}")
    
    # Check if today is a weekend
    if weekday >= 5:  # Saturday or Sunday
        day_name = now.strftime('%A')
        return False, f"Market is CLOSED ({day_name})", f"Weekend - Markets closed on {day_name}"
    
    # Check if today is a holiday
    if today_date in us_market_holidays_2025:
        return False, f"Market is CLOSED (Holiday)", f"US Market Holiday - {now.strftime('%B %d, %Y')}"
    
    # Check trading hours (4 AM to 8 PM ET)
    market_open = now.replace(hour=4, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=20, minute=0, second=0, microsecond=0)
    
    if now < market_open:
        return False, f"Market is CLOSED (Pre-market)", f"Market opens at 4:00 AM ET (in {market_open - now})"
    elif now > market_close:
        return False, f"Market is CLOSED (After-hours)", f"Market closed at 8:00 PM ET"
    else:
        # Market is open - determine which session
        regular_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        regular_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        
        if now < regular_open:
            return True, f"Market is OPEN (Pre-market)", f"Pre-market session: 4:00-9:30 AM ET"
        elif now <= regular_close:
            return True, f"Market is OPEN (Regular)", f"Regular session: 9:30 AM-4:00 PM ET"
        else:
            return True, f"Market is OPEN (After-hours)", f"After-hours session: 4:00-8:00 PM ET"

if __name__ == "__main__":
    print("🧪 Testing Market Status Detection")
    print("=" * 50)
    
    is_open, status, explanation = get_market_status_detailed()
    
    print(f"\n📊 Market Status Results:")
    print(f"  Is Open: {is_open}")
    print(f"  Status: {status}")
    print(f"  Explanation: {explanation}")
    
    print(f"\n🔍 Expected for Friday August 23, 2025:")
    print(f"  Should detect: Weekend (Friday is weekday 4, not >= 5)")
    print(f"  Wait... Friday is a weekday! Let me check the date...")
    
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.timezone("US/Eastern"))
    print(f"  Current date check: {now.strftime('%A, %B %d, %Y')}")

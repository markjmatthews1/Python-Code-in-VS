"""
Market Hours Detection Utility
Determines if market is open/closed and provides data quality warnings
"""
from datetime import datetime, time
import pytz


def is_market_open():
    """
    Check if US stock market is currently open
    
    Market hours: Monday-Friday, 9:30 AM - 4:00 PM ET
    Excludes major holidays (simplified - doesn't check all market holidays)
    
    Returns:
        tuple: (is_open: bool, status_message: str, market_state: str)
    """
    # Get current time in Eastern Time
    eastern = pytz.timezone('US/Eastern')
    now_et = datetime.now(eastern)
    
    # Check if weekend
    if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
        next_open = "Monday 9:30 AM ET"
        return False, f"Market Closed (Weekend) - Opens {next_open}", "WEEKEND"
    
    # Market hours: 9:30 AM - 4:00 PM ET
    market_open = time(9, 30)
    market_close = time(16, 0)
    current_time = now_et.time()
    
    # Pre-market: Before 9:30 AM
    if current_time < market_open:
        return False, "Pre-Market - Data may be from previous close", "PRE_MARKET"
    
    # After-hours: After 4:00 PM
    elif current_time > market_close:
        return False, "After-Hours - Data may be stale or have wide spreads", "AFTER_HOURS"
    
    # Market is open
    else:
        return True, "Market Open - Live data", "OPEN"


def get_market_status_display():
    """
    Get formatted market status for GUI display
    
    Returns:
        dict: {
            'is_open': bool,
            'status_text': str,  # For display
            'color': str,        # Suggested color (green/yellow/red)
            'state': str,        # OPEN/PRE_MARKET/AFTER_HOURS/WEEKEND
            'warning': str       # Data quality warning
        }
    """
    is_open, message, state = is_market_open()
    
    # Determine display color
    if is_open:
        color = "green"
        warning = None
    elif state == "PRE_MARKET":
        color = "orange"
        warning = "⚠️ Option prices from yesterday's close - Plan ahead!"
    elif state == "AFTER_HOURS":
        color = "yellow"
        warning = "⚠️ After-hours data may have wider bid-ask spreads"
    else:  # WEEKEND
        color = "red"
        warning = "📅 Weekend - Showing Friday's closing data"
    
    return {
        'is_open': is_open,
        'status_text': message,
        'color': color,
        'state': state,
        'warning': warning
    }


def should_use_planning_mode():
    """
    Determine if app should use relaxed filters for planning
    
    During closed hours, users want to see options even if they're not perfect,
    since they're planning ahead for when market opens.
    
    Returns:
        bool: True if market is closed (use planning mode)
    """
    is_open, _, _ = is_market_open()
    return not is_open


# Example usage and testing
if __name__ == "__main__":
    status = get_market_status_display()
    print(f"Market Status: {status['status_text']}")
    print(f"State: {status['state']}")
    print(f"Color: {status['color']}")
    if status['warning']:
        print(f"Warning: {status['warning']}")
    print(f"\nPlanning Mode: {should_use_planning_mode()}")

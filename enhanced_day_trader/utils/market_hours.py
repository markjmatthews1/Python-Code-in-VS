"""
Market Hours Manager
====================

Handles market hours checking and end-of-day position management.

US Stock Market Hours (Eastern Time):
- Pre-Market: 4:00 AM - 9:30 AM
- Regular Hours: 9:30 AM - 4:00 PM
- After-Hours: 4:00 PM - 8:00 PM

Day Trading Rules:
- Only open new positions during regular hours
- Close all positions by 3:55 PM (5 minutes before market close)
- No trading on weekends
- No trading on market holidays
"""

from datetime import datetime, time
from typing import Tuple
import pytz
import logging

logger = logging.getLogger(__name__)

# Eastern Time Zone (NYSE/NASDAQ)
ET = pytz.timezone('US/Eastern')

# Market Hours (Eastern Time)
MARKET_OPEN = time(9, 30)      # 9:30 AM ET
MARKET_CLOSE = time(16, 0)     # 4:00 PM ET
CLOSE_POSITIONS_TIME = time(15, 55)  # 3:55 PM ET - Close all positions

# US Market Holidays 2025 (will need to update yearly)
MARKET_HOLIDAYS_2025 = [
    datetime(2025, 1, 1),   # New Year's Day
    datetime(2025, 1, 20),  # MLK Jr. Day
    datetime(2025, 2, 17),  # Presidents' Day
    datetime(2025, 4, 18),  # Good Friday
    datetime(2025, 5, 26),  # Memorial Day
    datetime(2025, 6, 19),  # Juneteenth
    datetime(2025, 7, 4),   # Independence Day
    datetime(2025, 9, 1),   # Labor Day
    datetime(2025, 11, 27), # Thanksgiving
    datetime(2025, 12, 25), # Christmas
]


def get_current_time_et() -> datetime:
    """Get current time in Eastern Time"""
    return datetime.now(ET)


def is_market_holiday(dt: datetime = None) -> bool:
    """Check if given date is a market holiday"""
    if dt is None:
        dt = get_current_time_et()
    
    # Check if date matches any holiday
    date_only = dt.date()
    for holiday in MARKET_HOLIDAYS_2025:
        if date_only == holiday.date():
            return True
    
    return False


def is_weekend(dt: datetime = None) -> bool:
    """Check if given date is a weekend"""
    if dt is None:
        dt = get_current_time_et()
    
    # Monday = 0, Sunday = 6
    return dt.weekday() >= 5  # Saturday or Sunday


def is_market_open(dt: datetime = None) -> Tuple[bool, str]:
    """
    Check if market is currently open for regular trading
    
    Returns:
        (is_open: bool, message: str)
    """
    if dt is None:
        dt = get_current_time_et()
    
    # Check weekend
    if is_weekend(dt):
        return False, f"Weekend ({dt.strftime('%A')})"
    
    # Check holiday
    if is_market_holiday(dt):
        return False, "Market Holiday"
    
    # Check time
    current_time = dt.time()
    
    if current_time < MARKET_OPEN:
        return False, f"Pre-Market (opens at {MARKET_OPEN.strftime('%I:%M %p')} ET)"
    
    if current_time >= MARKET_CLOSE:
        return False, f"After-Hours (closed at {MARKET_CLOSE.strftime('%I:%M %p')} ET)"
    
    # Market is open!
    return True, "Market Open"


def should_open_new_trades(dt: datetime = None) -> Tuple[bool, str]:
    """
    Check if we should be opening new trades
    
    Returns:
        (should_open: bool, reason: str)
    """
    if dt is None:
        dt = get_current_time_et()
    
    # First check if market is open
    market_open, market_msg = is_market_open(dt)
    
    if not market_open:
        return False, market_msg
    
    # Market is open - check if we're too close to closing time
    current_time = dt.time()
    
    if current_time >= CLOSE_POSITIONS_TIME:
        return False, f"Too close to market close (stops at {CLOSE_POSITIONS_TIME.strftime('%I:%M %p')} ET)"
    
    # Good to trade!
    return True, "Trading window active"


def should_close_all_positions(dt: datetime = None) -> Tuple[bool, str]:
    """
    Check if we should close all open positions
    
    Closes positions at 3:55 PM ET to ensure all orders execute before market close
    
    Returns:
        (should_close: bool, reason: str)
    """
    if dt is None:
        dt = get_current_time_et()
    
    current_time = dt.time()
    
    # Close all positions at 3:55 PM or later
    if current_time >= CLOSE_POSITIONS_TIME and current_time < MARKET_CLOSE:
        return True, f"End of day - closing all positions at {current_time.strftime('%I:%M %p')} ET"
    
    # Already after market close
    if current_time >= MARKET_CLOSE:
        return True, "Market closed - should have no open positions"
    
    return False, "Normal trading hours"


def get_market_status() -> dict:
    """
    Get comprehensive market status information
    
    Returns:
        dict with market status details
    """
    now = get_current_time_et()
    market_open, market_msg = is_market_open(now)
    can_trade, trade_msg = should_open_new_trades(now)
    must_close, close_msg = should_close_all_positions(now)
    
    return {
        'current_time_et': now,
        'current_time_str': now.strftime('%Y-%m-%d %I:%M:%S %p %Z'),
        'is_weekend': is_weekend(now),
        'is_holiday': is_market_holiday(now),
        'market_open': market_open,
        'market_message': market_msg,
        'can_open_trades': can_trade,
        'trade_message': trade_msg,
        'should_close_all': must_close,
        'close_message': close_msg,
    }


def print_market_status():
    """Print formatted market status"""
    status = get_market_status()
    
    print("\n" + "="*60)
    print("MARKET STATUS")
    print("="*60)
    print(f"Current Time:     {status['current_time_str']}")
    print(f"Weekend:          {'Yes' if status['is_weekend'] else 'No'}")
    print(f"Holiday:          {'Yes' if status['is_holiday'] else 'No'}")
    print(f"Market Open:      {'✅ YES' if status['market_open'] else '❌ NO'} ({status['market_message']})")
    print(f"Can Open Trades:  {'✅ YES' if status['can_open_trades'] else '❌ NO'} ({status['trade_message']})")
    print(f"Close Positions:  {'⚠️ YES' if status['should_close_all'] else '✅ NO'} ({status['close_message']})")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Test the market hours checker
    print_market_status()

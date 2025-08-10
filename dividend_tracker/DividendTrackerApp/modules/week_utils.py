#!/usr/bin/env python3
"""
Week standardization utility
Ensures all weekly updates use consistent weekly dates regardless of when run
"""

from datetime import datetime, timedelta

def get_standard_week_date(run_date=None):
    """
    Convert any date to the standard weekly date (Sunday of that week)
    
    Args:
        run_date: Optional datetime object. If None, uses current date.
        
    Returns:
        String in format 'YYYY-MM-DD' representing the Sunday of that week
    """
    if run_date is None:
        run_date = datetime.now()
    
    # Calculate days since Sunday (0=Monday, 6=Sunday)
    days_since_sunday = (run_date.weekday() + 1) % 7
    
    # Get the Sunday of this week
    sunday_date = run_date - timedelta(days=days_since_sunday)
    
    return sunday_date.strftime('%Y-%m-%d')

def get_display_week_date(run_date=None):
    """
    Get display format for weekly date (MM/DD/YYYY)
    
    Args:
        run_date: Optional datetime object. If None, uses current date.
        
    Returns:
        String in format 'MM/DD/YYYY' representing the Sunday of that week
    """
    if run_date is None:
        run_date = datetime.now()
    
    # Calculate days since Sunday
    days_since_sunday = (run_date.weekday() + 1) % 7
    
    # Get the Sunday of this week
    sunday_date = run_date - timedelta(days=days_since_sunday)
    
    return sunday_date.strftime('%m/%d/%Y')

def test_week_standardization():
    """Test function to show how dates get standardized"""
    test_dates = [
        datetime(2025, 7, 26),  # Saturday
        datetime(2025, 7, 27),  # Sunday
        datetime(2025, 7, 28),  # Monday
        datetime(2025, 7, 29),  # Tuesday
        datetime(2025, 7, 30),  # Wednesday
    ]
    
    print("Week Standardization Test:")
    print("Run Date        -> Standard Week Date")
    print("-" * 40)
    
    for test_date in test_dates:
        standard = get_standard_week_date(test_date)
        display = get_display_week_date(test_date)
        day_name = test_date.strftime('%A')
        print(f"{test_date.strftime('%Y-%m-%d')} ({day_name}) -> {standard} ({display})")

if __name__ == "__main__":
    test_week_standardization()

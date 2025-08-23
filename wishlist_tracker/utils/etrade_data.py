"""
E*TRADE Data Utility for Wishlist Tracker
----------------------------------------
Fetches 52-week high/low and current price for tickers using E*TRADE API.
Wraps the etrade_auth.py logic for use in the wishlist_tracker app.
"""
import os
import sys
import pandas as pd

# Ensure the parent directory is in sys.path for import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Import fetch_etrade_market_data from the main etrade_auth.py
from etrade_auth import fetch_etrade_market_data

def fetch_and_update_watchlist(watchlist):
    """
    Given a list of Instrument objects, fetches 52-week high/low and current price from E*TRADE,
    and updates the Instrument objects in-place.
    Returns a DataFrame of the fetched data.
    """
    tickers = [inst.symbol for inst in watchlist if inst.symbol]
    if not tickers:
        return pd.DataFrame()
    df = fetch_etrade_market_data(tickers)
    # Map results back to Instrument objects
    for inst in watchlist:
        row = df[df['Ticker'] == inst.symbol]
        if not row.empty:
            inst.high_52wk = row.iloc[0].get('week52High', '')
            inst.low_52wk = row.iloc[0].get('week52Low', '')
            inst.current_price = row.iloc[0].get('bid', '')
    return df

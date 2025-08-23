"""
Test script for watchlist_manager module
Verifies load and save functionality for Instrument watchlists.
"""

# Add project root to sys.path for import
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from wishlist_tracker.models.instrument import Instrument
from wishlist_tracker.utils.watchlist_manager import load_watchlist, save_watchlist

# Test data
watchlist = [
    Instrument(symbol='AAPL', name='Apple Inc.', high_52wk=200.0, current_price=175.5, notes=''),
    Instrument(symbol='TSLA', name='Tesla', high_52wk=300.0, current_price=250.0, notes='Earnings soon'),
    Instrument(symbol='SPY', name='S&P 500 ETF', high_52wk=None, current_price=None, notes=None)
]

# Save to temp file
filepath = 'wishlist_tracker/tests/test_watchlist.csv'
save_watchlist(watchlist, filepath)
print('Saved watchlist to', filepath)

# Load back
loaded = load_watchlist(filepath)
print('Loaded watchlist:')
for inst in loaded:
    print(' ', inst)

# Clean up
os.remove(filepath)
print('Test complete.')

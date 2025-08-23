
"""
utils/watchlist_manager.py
-------------------------
Functions to manage the user's watchlist for Wishlist Tracker App.

Watchlist is stored as a CSV file with columns: symbol, name, high_52wk, current_price, notes
No NaN/0.0 values; blank fields for missing data.
"""

import csv
from wishlist_tracker.models.instrument import Instrument

def load_watchlist(filepath):
    """
    Load watchlist from a CSV file.
    Returns a list of Instrument objects.
    Blank fields are treated as None.
    """
    watchlist = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            inst = Instrument(
                symbol=row.get('symbol', '').strip(),
                name=row.get('name', '').strip() or None,
                high_52wk=float(row['high_52wk']) if row.get('high_52wk') not in (None, '', 'NaN') else None,
                current_price=float(row['current_price']) if row.get('current_price') not in (None, '', 'NaN') else None,
                notes=row.get('notes', '').strip() or None
            )
            watchlist.append(inst)
    return watchlist

def save_watchlist(watchlist, filepath):
    """
    Save a list of Instrument objects to a CSV file.
    Blank fields are written as empty strings.
    """
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        fieldnames = ['symbol', 'name', 'high_52wk', 'current_price', 'notes']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for inst in watchlist:
            writer.writerow(inst.to_dict())

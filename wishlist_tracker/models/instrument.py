"""
models/instrument.py
-------------------
Instrument data model for Wishlist Tracker App.

Represents a stock or ETF with relevant fields for analysis and display.
"""

class Instrument:
    """
    Represents a stock or ETF instrument.

    Attributes:
        symbol (str): The ticker symbol (e.g., 'AAPL', 'SPY').
        name (str): The full name of the instrument.
        high_52wk (float or None): The 52-week high price.
        current_price (float or None): The latest price.
        notes (str): Optional notes or flags (e.g., 'Earnings miss').
    """
    def __init__(self, symbol, name=None, high_52wk=None, current_price=None, notes=None):
        self.symbol = symbol
        self.name = name
        self.high_52wk = high_52wk
        self.current_price = current_price
        self.notes = notes

    def to_dict(self):
        """Return a dictionary representation (for saving/display)."""
        return {
            'symbol': self.symbol,
            'name': self.name or '',
            'high_52wk': self.high_52wk if self.high_52wk is not None else '',
            'current_price': self.current_price if self.current_price is not None else '',
            'notes': self.notes or ''
        }

    def __str__(self):
        return f"{self.symbol} ({self.name or ''}) - Price: {self.current_price or ''}, 52wk High: {self.high_52wk or ''}"

    def is_valid(self):
        """Check if the instrument has a valid symbol and price."""
        return bool(self.symbol) and self.current_price not in (None, '', 'NaN', 0.0)

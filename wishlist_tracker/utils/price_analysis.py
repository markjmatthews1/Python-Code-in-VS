# price_analysis.py
# Utility functions for price and premium analysis

def is_excellent_premium(premium, strike, current, high_52wk):
    """Return True if premium > $1, strike > current, strike < 52wk high."""
    return premium > 1 and strike > current and strike < high_52wk

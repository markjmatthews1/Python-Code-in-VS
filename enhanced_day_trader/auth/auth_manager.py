#!/usr/bin/env python3
"""
Enhanced Day Trader Authentication Wrapper
==========================================

Safely imports and manages authentication from parent directory
without conflicts with the original day trading app.

Author: GitHub Copilot
Date: September 26, 2025
"""

import sys
import os
from pathlib import Path
import pandas as pd

# Add parent directory to path for auth imports
parent_dir = Path(__file__).parent.parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

try:
    # Import existing authentication modules
    import Schwab_auth
    import etrade_auth
    import schwab_data
    
    # Import specific functions with error handling
    fetch_batch_quotes = getattr(Schwab_auth, 'fetch_batch_quotes', None)
    fetch_quote = getattr(Schwab_auth, 'fetch_quote', None)
    get_valid_access_token = getattr(Schwab_auth, 'get_valid_access_token', None)
    get_etrade_session = getattr(etrade_auth, 'get_etrade_session', None)
    fetch_etrade_market_data = getattr(etrade_auth, 'fetch_etrade_market_data', None)
    fetch_minute_bars_for_range = getattr(schwab_data, 'fetch_minute_bars_for_range', None)
    fetch_schwab_minute_ohlcv = getattr(schwab_data, 'fetch_schwab_minute_ohlcv', None)
    
    print("✅ Successfully imported authentication modules")
    
except ImportError as e:
    print(f"⚠️ Authentication import warning: {e}")
    print("Ensure parent directory has Schwab_auth.py and etrade_auth.py")
    
    # Create dummy functions for demo mode
    fetch_batch_quotes = lambda symbols: {}
    fetch_quote = lambda symbol: {}
    get_valid_access_token = lambda: "dummy_token"
    get_etrade_session = lambda: None
    fetch_etrade_market_data = lambda symbol: {}
    fetch_minute_bars_for_range = lambda symbol, start, end: pd.DataFrame()
    fetch_schwab_minute_ohlcv = lambda symbol: pd.DataFrame()
    print("Ensure parent directory has Schwab_auth.py and etrade_auth.py")

# Wrapper functions to ensure clean interface
class EnhancedAuthManager:
    """
    Manages authentication for enhanced day trader
    while avoiding conflicts with original system
    """
    
    def __init__(self):
        self.schwab_session = None
        self.etrade_session = None
        
    def get_schwab_quotes(self, tickers):
        """Get Schwab quotes for multiple tickers using existing auth"""
        try:
            if isinstance(tickers, str):
                # Single ticker
                return fetch_quote(tickers)
            else:
                # Multiple tickers - use batch if available, otherwise individual calls
                if fetch_batch_quotes:
                    return fetch_batch_quotes(tickers)
                else:
                    # Fallback to individual calls
                    results = {}
                    for ticker in tickers:
                        quote = fetch_quote(ticker)
                        if quote:
                            results.update(quote)
                    return results
        except Exception as e:
            print(f"Schwab quote error: {e}")
            return {}
    
    def get_etrade_session(self):
        """Get E*Trade session"""
        if self.etrade_session is None:
            try:
                self.etrade_session = get_etrade_session()
            except Exception as e:
                print(f"E*Trade session error: {e}")
        return self.etrade_session
    
    def get_historical_data(self, ticker, days_back=5):
        """Get historical minute data"""
        try:
            return fetch_minute_bars_for_range(ticker, days_back)
        except Exception as e:
            print(f"Historical data error for {ticker}: {e}")
            return None
    
    def get_realtime_data(self, ticker):
        """Get real-time minute data"""
        try:
            return fetch_schwab_minute_ohlcv(ticker)
        except Exception as e:
            print(f"Real-time data error for {ticker}: {e}")
            return None

# Global instance for the enhanced app
enhanced_auth = EnhancedAuthManager()

def test_authentication():
    """Test that authentication is working"""
    print("🧪 Testing Enhanced Day Trader Authentication...")
    
    test_tickers = ['XLK', 'XLF']
    
    # Test Schwab quotes
    try:
        quotes = enhanced_auth.get_schwab_quotes(test_tickers)
        if quotes:
            print(f"✅ Schwab quotes working: {len(quotes)} quotes received")
        else:
            print("⚠️ Schwab quotes returned empty")
    except Exception as e:
        print(f"❌ Schwab quotes failed: {e}")
    
    # Test E*Trade session
    try:
        session = enhanced_auth.get_etrade_session()
        if session:
            print("✅ E*Trade session working")
        else:
            print("⚠️ E*Trade session failed to initialize")
    except Exception as e:
        print(f"❌ E*Trade session failed: {e}")
    
    # Test historical data
    try:
        hist_data = enhanced_auth.get_historical_data('XLK', days_back=1)
        if hist_data is not None and not hist_data.empty:
            print(f"✅ Historical data working: {len(hist_data)} records")
        else:
            print("⚠️ Historical data returned empty")
    except Exception as e:
        print(f"❌ Historical data failed: {e}")

if __name__ == "__main__":
    test_authentication()
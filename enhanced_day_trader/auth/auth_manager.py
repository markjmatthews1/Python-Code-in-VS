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

# Add parent directory to path for auth imports
parent_dir = Path(__file__).parent.parent.absolute()
sys.path.insert(0, str(parent_dir))

try:
    # Import existing authentication modules
    from Schwab_auth import fetch_batch_quotes, get_streamer
    from etrade_auth import get_etrade_session, fetch_etrade_market_data  
    from schwab_data import fetch_minute_bars_for_range, fetch_schwab_minute_ohlcv
    
    print("✅ Successfully imported authentication modules")
    
except ImportError as e:
    print(f"⚠️ Authentication import warning: {e}")
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
        """Get Schwab quotes for multiple tickers"""
        try:
            return fetch_batch_quotes(tickers)
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
    
    test_tickers = ['SPY', 'QQQ']
    
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
        hist_data = enhanced_auth.get_historical_data('SPY', days_back=1)
        if hist_data is not None and not hist_data.empty:
            print(f"✅ Historical data working: {len(hist_data)} records")
        else:
            print("⚠️ Historical data returned empty")
    except Exception as e:
        print(f"❌ Historical data failed: {e}")

if __name__ == "__main__":
    test_authentication()
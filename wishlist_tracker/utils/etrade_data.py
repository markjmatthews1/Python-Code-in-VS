"""
E*TRADE Data Utility for     print(f"🔄 [E*TRADE] Fetching market data for {len(tickers)} tickers...")
    
    try:
        # Add timeout handling for OAuth situations using threading
        import threading
        import queue
        
        def fetch_with_timeout():
            result_queue = queue.Queue()
            
            def target():
                try:
                    result = fetch_etrade_market_data(tickers)
                    result_queue.put(('success', result))
                except Exception as e:
                    result_queue.put(('error', e))
            
            thread = threading.Thread(target=target)
            thread.daemon = True
            thread.start()
            thread.join(timeout=30)  # 30 second timeout
            
            if thread.is_alive():
                # Thread is still running, fetch timed out
                raise TimeoutError("E*Trade fetch timed out - may be hanging after OAuth")
            
            try:
                status, result = result_queue.get_nowait()
                if status == 'error':
                    raise result
                return result
            except queue.Empty:
                raise TimeoutError("E*Trade fetch completed but no result returned")
        
        df = fetch_with_timeout()
        print(f"✅ [E*TRADE] Successfully fetched data for {len(df)} tickers")
        
        # Map results back to Instrument objects
        for inst in watchlist:
            row = df[df['Ticker'] == inst.symbol]
            if not row.empty:
                inst.high_52wk = row.iloc[0].get('week52High', '')
                inst.low_52wk = row.iloc[0].get('week52Low', '')
                inst.current_price = row.iloc[0].get('bid', '')
        
        return dfr
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
    
    Enhanced with OAuth completion detection for automatic continuation.
    """
    tickers = [inst.symbol for inst in watchlist if inst.symbol]
    if not tickers:
        return pd.DataFrame()
    
    print(f"🔄 [E*TRADE] Fetching market data for {len(tickers)} tickers...")
    
    try:
        df = fetch_etrade_market_data(tickers)
        print(f"✅ [E*TRADE] Successfully fetched data for {len(df)} tickers")
        
        # Map results back to Instrument objects
        for inst in watchlist:
            row = df[df['Ticker'] == inst.symbol]
            if not row.empty:
                inst.high_52wk = row.iloc[0].get('week52High', '')
                inst.low_52wk = row.iloc[0].get('week52Low', '')
                inst.current_price = row.iloc[0].get('bid', '')
        
        return df
        
    except Exception as e:
        print(f"⚠️ [E*TRADE] Error fetching market data: {e}")
        # Check if this might be an OAuth issue
        if "401" in str(e) or "unauthorized" in str(e).lower() or "authentication" in str(e).lower():
            print("🔐 [E*TRADE] This appears to be an authentication issue - OAuth popup may be shown")
            print("🔄 [E*TRADE] Please complete OAuth in the popup window - dashboard will auto-refresh")
        raise e  # Re-raise to trigger retry logic in dashboard

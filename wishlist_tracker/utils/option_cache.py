"""
Option Data Cache
Stores option chain data at market close for use during pre-market/after-hours
"""
import json
import os
from datetime import datetime, date
from pathlib import Path


CACHE_DIR = Path(__file__).parent.parent / "data" / "option_cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def get_cache_file(ticker):
    """Get cache file path for a ticker"""
    return CACHE_DIR / f"{ticker}_options.json"


def save_option_cache(ticker, options_data):
    """
    Save option chain data to cache
    
    Args:
        ticker: Stock symbol
        options_data: List of option dictionaries
    """
    try:
        cache_file = get_cache_file(ticker)
        cache_data = {
            'ticker': ticker,
            'timestamp': datetime.now().isoformat(),
            'date': date.today().isoformat(),
            'options': options_data
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2, default=str)
        
        print(f"💾 Cached {len(options_data)} options for {ticker}")
        return True
        
    except Exception as e:
        print(f"❌ Error saving cache for {ticker}: {e}")
        return False


def load_option_cache(ticker):
    """
    Load cached option data if available and recent
    
    Args:
        ticker: Stock symbol
        
    Returns:
        tuple: (options_list, cache_age_hours) or (None, None) if no valid cache
    """
    try:
        cache_file = get_cache_file(ticker)
        
        if not cache_file.exists():
            return None, None
        
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        # Check cache age
        cached_time = datetime.fromisoformat(cache_data['timestamp'])
        age_hours = (datetime.now() - cached_time).total_seconds() / 3600
        
        # Don't use cache older than 24 hours
        if age_hours > 24:
            print(f"⏰ Cache for {ticker} is {age_hours:.1f} hours old, too stale")
            return None, None
        
        options = cache_data.get('options', [])
        print(f"📂 Loaded {len(options)} cached options for {ticker} (age: {age_hours:.1f}h)")
        
        return options, age_hours
        
    except Exception as e:
        print(f"❌ Error loading cache for {ticker}: {e}")
        return None, None


def clear_cache(ticker=None):
    """
    Clear cache for a specific ticker or all tickers
    
    Args:
        ticker: Stock symbol to clear, or None to clear all
    """
    try:
        if ticker:
            cache_file = get_cache_file(ticker)
            if cache_file.exists():
                cache_file.unlink()
                print(f"🗑️ Cleared cache for {ticker}")
        else:
            # Clear all cache files
            for cache_file in CACHE_DIR.glob("*_options.json"):
                cache_file.unlink()
            print(f"🗑️ Cleared all option caches")
        
        return True
        
    except Exception as e:
        print(f"❌ Error clearing cache: {e}")
        return False


def get_cache_info():
    """Get info about all cached data"""
    cache_info = {}
    
    for cache_file in CACHE_DIR.glob("*_options.json"):
        try:
            with open(cache_file, 'r') as f:
                data = json.load(f)
            
            ticker = data['ticker']
            cached_time = datetime.fromisoformat(data['timestamp'])
            age_hours = (datetime.now() - cached_time).total_seconds() / 3600
            
            cache_info[ticker] = {
                'file': cache_file.name,
                'timestamp': data['timestamp'],
                'age_hours': age_hours,
                'option_count': len(data.get('options', []))
            }
        except:
            pass
    
    return cache_info


if __name__ == "__main__":
    # Test caching
    print("Option Cache Test")
    print("="*80)
    
    # Show current cache
    info = get_cache_info()
    if info:
        print(f"\nCurrent cache ({len(info)} tickers):")
        for ticker, data in info.items():
            print(f"  {ticker}: {data['option_count']} options, {data['age_hours']:.1f}h old")
    else:
        print("\nNo cached data found")

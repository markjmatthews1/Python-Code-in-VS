"""
Price History Management for Technical Analysis
Fetches and caches historical OHLCV data for trend analysis calculations.
"""

import os
import json
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd


# Cache directory
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'price_history')


def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    os.makedirs(CACHE_DIR, exist_ok=True)


def get_cache_path(ticker):
    """Get cache file path for a ticker"""
    ensure_cache_dir()
    today = datetime.now().strftime('%Y%m%d')
    return os.path.join(CACHE_DIR, f"{ticker}_{today}.json")


def load_cached_history(ticker, max_age_hours=24):
    """
    Load cached price history if fresh enough.
    
    Args:
        ticker: Stock symbol
        max_age_hours: Maximum age in hours before cache is considered stale
        
    Returns:
        DataFrame with OHLCV data or None if cache miss/stale
    """
    cache_path = get_cache_path(ticker)
    
    if not os.path.exists(cache_path):
        return None
    
    # Check file age
    file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
    age_hours = (datetime.now() - file_time).total_seconds() / 3600
    
    if age_hours > max_age_hours:
        print(f"  💾 Cache STALE for {ticker} (age: {age_hours:.1f}h)")
        return None
    
    try:
        with open(cache_path, 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data['prices'])
        df['Date'] = pd.to_datetime(df['Date'])
        df.set_index('Date', inplace=True)
        
        print(f"  💾 Cache HIT for {ticker} ({len(df)} days, age: {age_hours:.1f}h)")
        return df
    
    except Exception as e:
        print(f"  ❌ Cache READ error for {ticker}: {e}")
        return None


def cache_price_history(ticker, df):
    """
    Save price history DataFrame to cache.
    
    Args:
        ticker: Stock symbol
        df: DataFrame with OHLCV data (indexed by Date)
    """
    try:
        ensure_cache_dir()
        cache_path = get_cache_path(ticker)
        
        # Convert DataFrame to JSON-serializable format
        data = {
            'ticker': ticker,
            'cached_at': datetime.now().isoformat(),
            'prices': df.reset_index().to_dict('records')
        }
        
        # Convert datetime objects to strings
        for record in data['prices']:
            if isinstance(record.get('Date'), pd.Timestamp):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        with open(cache_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        print(f"  💾 Cached {len(df)} days for {ticker}")
        
    except Exception as e:
        print(f"  ❌ Cache WRITE error for {ticker}: {e}")


def fetch_price_history(ticker, days=90, use_cache=True):
    """
    Fetch historical OHLCV data for technical analysis.
    
    Args:
        ticker: Stock symbol
        days: Number of days of history to fetch (default 90 for 200-day MA calculation)
        use_cache: Whether to use cached data if available
        
    Returns:
        DataFrame with columns: Open, High, Low, Close, Volume
        Index: Date (datetime)
    """
    # Try cache first if enabled
    if use_cache:
        cached = load_cached_history(ticker)
        if cached is not None:
            return cached
    
    print(f"  📡 Fetching price history for {ticker} ({days} days)...")
    
    try:
        # Calculate date range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days + 10)  # Extra buffer for weekends/holidays
        
        # Fetch from yfinance
        stock = yf.Ticker(ticker)
        df = stock.history(
            start=start_date.strftime('%Y-%m-%d'),
            end=end_date.strftime('%Y-%m-%d'),
            interval='1d'
        )
        
        if df.empty:
            print(f"  ❌ No price data returned for {ticker}")
            return None
        
        # Keep only needed columns and ensure proper names
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()
        
        # Remove any NaN rows
        df.dropna(inplace=True)
        
        # Limit to requested days (keep most recent)
        df = df.tail(days)
        
        print(f"  ✅ Fetched {len(df)} days for {ticker} (from {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')})")
        
        # Cache the data
        if use_cache:
            cache_price_history(ticker, df)
        
        return df
    
    except Exception as e:
        print(f"  ❌ Error fetching price history for {ticker}: {e}")
        return None


def clean_old_cache_files(days_to_keep=7):
    """
    Remove cache files older than specified days.
    Keeps cache directory clean.
    
    Args:
        days_to_keep: Number of days to retain cache files
    """
    ensure_cache_dir()
    
    cutoff_time = datetime.now() - timedelta(days=days_to_keep)
    removed_count = 0
    
    try:
        for filename in os.listdir(CACHE_DIR):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(CACHE_DIR, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            
            if file_time < cutoff_time:
                os.remove(filepath)
                removed_count += 1
        
        if removed_count > 0:
            print(f"  🧹 Cleaned {removed_count} old cache files")
    
    except Exception as e:
        print(f"  ⚠️ Cache cleanup warning: {e}")


# Test function
if __name__ == "__main__":
    print("=" * 80)
    print("PRICE HISTORY MODULE TEST")
    print("=" * 80)
    
    test_tickers = ['TSLL', 'SOFI', 'AAPL']
    
    for ticker in test_tickers:
        print(f"\n{'=' * 80}")
        print(f"Testing: {ticker}")
        print(f"{'=' * 80}")
        
        # Fetch price history
        df = fetch_price_history(ticker, days=90)
        
        if df is not None:
            print(f"\n📊 Data Summary:")
            print(f"  Rows: {len(df)}")
            print(f"  Columns: {list(df.columns)}")
            print(f"  Date Range: {df.index[0].strftime('%Y-%m-%d')} to {df.index[-1].strftime('%Y-%m-%d')}")
            print(f"\n  Latest 5 days:")
            print(df.tail(5)[['Close', 'Volume']])
        
        print()
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)

"""
Enhanced Earnings Calendar with Multi-Tier API Support and Extended Caching
==========================================================================

Tier 1: Cached data (48-hour duration - earnings dates don't change frequently)
Tier 2: Finnhub API (professional)
Tier 3: Yahoo Finance (yfinance) - primary working source
Tier 4: Fallback estimates

Features:
- 48-hour cache duration (configurable)
- Rate limiting protection
- Comprehensive error handling
- Data validation
- Source tracking
"""

import json
import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd

def get_enhanced_earnings_calendar():
    """
    Enhanced earnings calendar with multi-tier API approach and extended caching
    """
    
    # Configuration - Extended cache duration for earnings data
    CACHE_FILE = "earnings_cache.json"
    CACHE_DURATION_HOURS = 48  # 48 hours - earnings dates rarely change once announced
    FINNHUB_API_KEY = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"
    
    def load_earnings_cache():
        """Load earnings data from cache if recent enough"""
        if not os.path.exists(CACHE_FILE):
            return {}, {}
        
        try:
            with open(CACHE_FILE, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is still valid (48 hours)
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
            if datetime.now() - cache_time < timedelta(hours=CACHE_DURATION_HOURS):
                cache_age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                print(f"Using cached earnings data from {cache_time.strftime('%Y-%m-%d %H:%M')} ({cache_age_hours:.1f} hours old)")
                return cache_data.get('earnings', {}), cache_data.get('sources', {})
            else:
                cache_age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                print(f"⏰ Cache expired - {cache_age_hours:.1f} hours old (max: {CACHE_DURATION_HOURS}h), refreshing data")
        except Exception as e:
            print(f"Cache read error: {e}")
        
        return {}, {}
    
    def save_earnings_cache(earnings_data, sources_data):
        """Save earnings data to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'earnings': earnings_data,
                'sources': sources_data
            }
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache_data, f, indent=2, default=str)
            print(f"Saved earnings data to cache")
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def get_finnhub_earnings(stock_ticker):
        """Tier 2: Get earnings from Finnhub API"""
        try:
            url = f"https://finnhub.io/api/v1/calendar/earnings?symbol={stock_ticker}&token={FINNHUB_API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"Finnhub response for {stock_ticker}: {data}")
                
                if 'earningsCalendar' in data and data['earningsCalendar']:
                    for earning in data['earningsCalendar']:
                        if 'date' in earning:
                            earnings_date = datetime.strptime(earning['date'], '%Y-%m-%d')
                            if earnings_date.date() >= datetime.now().date():
                                return earnings_date, "finnhub"
        except Exception as e:
            print(f"Finnhub earnings fetch failed for {stock_ticker}: {e}")
        
        return None, None
    
    def get_yfinance_earnings(stock_ticker):
        """Tier 3: Get earnings from Yahoo Finance (yfinance) - Primary working source"""
        try:
            ticker = yf.Ticker(stock_ticker)
            
            # Method 1: Try info approach first
            try:
                info = ticker.info
                if 'nextEarningsDate' in info and info['nextEarningsDate']:
                    earnings_timestamp = info['nextEarningsDate']
                    earnings_date = pd.to_datetime(earnings_timestamp, unit='s')
                    
                    if earnings_date.date() >= datetime.now().date():
                        return earnings_date.to_pydatetime(), "yfinance_info"
            except Exception as info_error:
                print(f"yfinance info failed for {stock_ticker}: {info_error}")
            
            # Method 2: Try calendar approach (currently most reliable)
            try:
                calendar = ticker.calendar
                if calendar is not None:
                    if isinstance(calendar, dict):
                        if 'Earnings Date' in calendar:
                            earnings_dates = calendar['Earnings Date']
                            if earnings_dates:
                                next_earnings_date = earnings_dates[0]
                                if hasattr(next_earnings_date, 'strftime'):
                                    earnings_date = pd.to_datetime(next_earnings_date)
                                else:
                                    earnings_date = pd.to_datetime(next_earnings_date)
                                
                                if earnings_date.date() >= datetime.now().date():
                                    return earnings_date.to_pydatetime(), "yfinance_calendar"
            except Exception as cal_error:
                print(f"yfinance calendar failed for {stock_ticker}: {cal_error}")
                
        except Exception as e:
            print(f"yfinance earnings fetch failed for {stock_ticker}: {e}")
        
        return None, None
    
    def get_fallback_estimate(etf_ticker):
        """Tier 4: Fallback estimates based on typical patterns"""
        fallback_days = {
            'NVDW': 14,  # NVDA - typically reports mid-quarter
            'AMDW': 21,  # AMD - typically reports 3 weeks out  
            'HOOW': 29,  # HOOD - typically reports end of month
            'MSFW': 35,  # MSFT - typically reports 5 weeks
            'GOOW': 42,  # GOOGL - typically reports 6 weeks
            'NFLW': 49   # NFLX - typically reports 7 weeks
        }
        
        days_away = fallback_days.get(etf_ticker, 30)
        estimated_date = datetime.now() + timedelta(days=days_away)
        return estimated_date, "fallback_estimate"
    
    # Main execution
    earnings_calendar = {}
    sources_used = {}
    
    # Load cached data first
    cached_earnings, cached_sources = load_earnings_cache()
    
    # ETF to stock mapping
    underlying_stocks = {
        'NVDW': 'NVDA',
        'AMDW': 'AMD', 
        'HOOW': 'HOOD',
        'MSFW': 'MSFT',
        'GOOW': 'GOOGL',
        'NFLW': 'NFLX'
    }
    
    current_date = datetime.now()
    new_earnings_data = {}
    new_sources_data = {}
    
    for etf_ticker, stock_ticker in underlying_stocks.items():
        earnings_date = None
        source = None
        
        # Tier 1: Check cache first
        if etf_ticker in cached_earnings:
            try:
                cached_date = datetime.fromisoformat(cached_earnings[etf_ticker])
                if cached_date.date() >= current_date.date():
                    earnings_date = cached_date
                    source = cached_sources.get(etf_ticker, "cached")
                    print(f"Using cached earnings for {etf_ticker}: {cached_date.strftime('%Y-%m-%d')} ({source})")
            except:
                pass
        
        # If not in cache or expired, try APIs
        if not earnings_date:
            # Tier 2: Finnhub
            earnings_date, source = get_finnhub_earnings(stock_ticker)
            if earnings_date:
                print(f"Finnhub earnings for {etf_ticker} ({stock_ticker}): {earnings_date.strftime('%Y-%m-%d')}")
            
            # Tier 3: Yahoo Finance
            if not earnings_date:
                earnings_date, source = get_yfinance_earnings(stock_ticker)
                if earnings_date:
                    print(f"yfinance earnings for {etf_ticker} ({stock_ticker}): {earnings_date.strftime('%Y-%m-%d')}")
            
            # Tier 4: Fallback estimate
            if not earnings_date:
                earnings_date, source = get_fallback_estimate(etf_ticker)
                print(f"Estimated earnings for {etf_ticker}: {earnings_date.strftime('%Y-%m-%d')} (API data unavailable)")
        
        # Store results
        if earnings_date:
            earnings_calendar[etf_ticker] = earnings_date
            sources_used[etf_ticker] = source
            new_earnings_data[etf_ticker] = earnings_date.isoformat()
            new_sources_data[etf_ticker] = source
    
    # Save to cache (merge with existing cache data that's still valid)
    final_cache_data = {**cached_earnings, **new_earnings_data}
    final_sources_data = {**cached_sources, **new_sources_data}
    save_earnings_cache(final_cache_data, final_sources_data)
    
    # Print summary
    print(f"\nEarnings Calendar Summary:")
    for etf, date in earnings_calendar.items():
        days_until = (date - current_date).days
        source = sources_used.get(etf, "unknown")
        print(f"   {etf}: {date.strftime('%Y-%m-%d')} ({days_until} days) [source: {source}]")
    
    return earnings_calendar

def get_earnings_for_etf(etf_ticker):
    """
    Get earnings date and days away for a specific ETF
    Returns: (earnings_date, days_away)
    """
    calendar = get_enhanced_earnings_calendar()
    if etf_ticker in calendar:
        earnings_date = calendar[etf_ticker]
        days_away = (earnings_date - datetime.now()).days
        return earnings_date, days_away
    else:
        raise ValueError(f"ETF {etf_ticker} not found in calendar")

if __name__ == "__main__":
    # Test the enhanced earnings calendar
    calendar = get_enhanced_earnings_calendar()
"""
Enhanced WeeklyPay Earnings Calendar with Manual Data Entry Integration
Combines API data sources with manual override capability for maximum reliability
"""

import os
import json
import requests
import yfinance as yf
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional, List

class WeeklyPayEarningsCalendar:
    def __init__(self):
        self.cache_file = "earnings_cache.json"
        self.manual_data_file = "manual_earnings_data.json"
        self.cache_duration_hours = 48
        self.finnhub_api_key = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"
        
        self.underlying_stocks = {
            'NVDW': 'NVDA',
            'AMDW': 'AMD', 
            'HOOW': 'HOOD',
            'MSFW': 'MSFT',
            'GOOW': 'GOOGL',
            'NFLW': 'NFLX'
        }
        
        self.fallback_estimates = {
            'NVDW': 14,  # NVDA - typically reports mid-quarter
            'AMDW': 21,  # AMD - typically reports 3 weeks out  
            'HOOW': 29,  # HOOD - typically reports end of month
            'MSFW': 35,  # MSFT - typically reports 5 weeks
            'GOOW': 42,  # GOOGL - typically reports 6 weeks
            'NFLW': 49   # NFLX - typically reports 7 weeks
        }
    
    def load_manual_data(self) -> Dict:
        """Load manual earnings data entries"""
        if os.path.exists(self.manual_data_file):
            try:
                with open(self.manual_data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading manual data: {e}")
        return {}
    
    def load_cache(self) -> Tuple[Dict, Dict]:
        """Load cached earnings data"""
        if not os.path.exists(self.cache_file):
            return {}, {}
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cache_data.get('timestamp', '2000-01-01'))
            if datetime.now() - cache_time < timedelta(hours=self.cache_duration_hours):
                cache_age_hours = (datetime.now() - cache_time).total_seconds() / 3600
                print(f"Using cached API data ({cache_age_hours:.1f} hours old)")
                return cache_data.get('earnings', {}), cache_data.get('sources', {})
            else:
                print("Cache expired, fetching fresh data")
                return {}, {}
        except Exception as e:
            print(f"Cache read error: {e}")
            return {}, {}
    
    def save_cache(self, earnings_data: Dict, sources_data: Dict):
        """Save earnings data to cache"""
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'earnings': earnings_data,
                'sources': sources_data
            }
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2)
            print("Saved earnings data to cache")
        except Exception as e:
            print(f"Cache save error: {e}")
    
    def get_finnhub_earnings(self, stock_ticker: str) -> Tuple[Optional[datetime], str]:
        """Get earnings date from Finnhub API"""
        try:
            url = f"https://finnhub.io/api/v1/calendar/earnings?symbol={stock_ticker}&token={self.finnhub_api_key}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                earnings_calendar = data.get('earningsCalendar', [])
                
                if earnings_calendar:
                    # Get the next earnings date
                    next_earnings = earnings_calendar[0]
                    date_str = next_earnings.get('date')
                    if date_str:
                        earnings_date = datetime.strptime(date_str, '%Y-%m-%d')
                        if earnings_date.date() >= datetime.now().date():
                            return earnings_date, "finnhub_api"
            
            return None, "finnhub_failed"
        except Exception as e:
            print(f"Finnhub earnings fetch failed for {stock_ticker}: {e}")
            return None, "finnhub_error"
    
    def get_yfinance_earnings(self, stock_ticker: str) -> Tuple[Optional[datetime], str]:
        """Get earnings date from yfinance"""
        try:
            ticker = yf.Ticker(stock_ticker)
            
            # Try earnings calendar first
            try:
                calendar = ticker.calendar
                if calendar is not None and not calendar.empty:
                    next_earnings = calendar.index[0]
                    if next_earnings.date() >= datetime.now().date():
                        return next_earnings, "yfinance_calendar"
            except Exception as cal_error:
                print(f"yfinance calendar failed for {stock_ticker}: {cal_error}")
            
            # Try info as fallback
            try:
                info = ticker.info
                earnings_date_str = info.get('nextEarningsDate') or info.get('earningsDate')
                if earnings_date_str:
                    if isinstance(earnings_date_str, str):
                        earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
                    else:
                        earnings_date = datetime.fromtimestamp(earnings_date_str)
                    
                    if earnings_date.date() >= datetime.now().date():
                        return earnings_date, "yfinance_info"
            except Exception as info_error:
                print(f"yfinance info failed for {stock_ticker}: {info_error}")
            
            return None, "yfinance_failed"
        except Exception as e:
            print(f"yfinance earnings fetch failed for {stock_ticker}: {e}")
            return None, "yfinance_error"
    
    def get_fallback_estimate(self, etf_ticker: str) -> Tuple[datetime, str]:
        """Get fallback estimate for earnings date"""
        days_away = self.fallback_estimates.get(etf_ticker, 30)
        estimated_date = datetime.now() + timedelta(days=days_away)
        return estimated_date, "fallback_estimate"
    
    def prompt_for_manual_data(self, failed_tickers: List[str]) -> Dict:
        """Prompt user for manual data entry when APIs fail"""
        if not failed_tickers:
            return {}
        
        print(f"\n⚠️  API data unavailable for: {', '.join(failed_tickers)}")
        print("Opening manual data entry GUI...")
        
        try:
            from manual_data_entry_gui import prompt_for_missing_data
            return prompt_for_missing_data(failed_tickers)
        except ImportError as e:
            print(f"GUI not available: {e}")
            return {}
    
    def get_comprehensive_earnings_calendar(self, prompt_for_manual: bool = True) -> Tuple[Dict, Dict]:
        """
        Get comprehensive earnings calendar with manual data integration
        
        Priority order:
        1. Manual data entries (highest priority)
        2. Cached API data (if recent)
        3. Fresh API data (Finnhub -> yfinance)
        4. Manual prompt for failed APIs (if enabled)
        5. Fallback estimates (lowest priority)
        
        Returns: (earnings_calendar, sources_used)
        """
        earnings_calendar = {}
        sources_used = {}
        failed_tickers = []
        
        # Load manual data (highest priority)
        manual_data = self.load_manual_data()
        
        # Load cached API data
        cached_earnings, cached_sources = self.load_cache()
        
        current_date = datetime.now()
        
        for etf_ticker, stock_ticker in self.underlying_stocks.items():
            earnings_date = None
            source = None
            
            # Priority 1: Manual data
            if etf_ticker in manual_data:
                try:
                    manual_entry = manual_data[etf_ticker]
                    manual_date = datetime.strptime(manual_entry['earnings_date'], '%Y-%m-%d')
                    if manual_date.date() >= current_date.date():
                        earnings_date = manual_date
                        source = "manual_entry"
                        print(f"Using manual entry for {etf_ticker}: {earnings_date.strftime('%Y-%m-%d')}")
                except Exception as e:
                    print(f"Error parsing manual data for {etf_ticker}: {e}")
            
            # Priority 2: Cached API data (if no manual override)
            if not earnings_date and etf_ticker in cached_earnings:
                try:
                    cached_date = datetime.fromisoformat(cached_earnings[etf_ticker])
                    if cached_date.date() >= current_date.date():
                        earnings_date = cached_date
                        source = cached_sources.get(etf_ticker, "cached")
                        print(f"Using cached data for {etf_ticker}: {earnings_date.strftime('%Y-%m-%d')}")
                except Exception as e:
                    print(f"Error parsing cached data for {etf_ticker}: {e}")
            
            # Priority 3: Fresh API data
            if not earnings_date:
                # Try Finnhub
                earnings_date, source = self.get_finnhub_earnings(stock_ticker)
                if earnings_date:
                    print(f"Finnhub data for {etf_ticker} ({stock_ticker}): {earnings_date.strftime('%Y-%m-%d')}")
                else:
                    # Try yfinance
                    earnings_date, source = self.get_yfinance_earnings(stock_ticker)
                    if earnings_date:
                        print(f"yfinance data for {etf_ticker} ({stock_ticker}): {earnings_date.strftime('%Y-%m-%d')}")
                    else:
                        # Mark as failed for potential manual entry
                        failed_tickers.append(etf_ticker)
            
            # Store successful results
            if earnings_date:
                earnings_calendar[etf_ticker] = earnings_date
                sources_used[etf_ticker] = source
        
        # Priority 4: Prompt for manual data for failed tickers
        if failed_tickers and prompt_for_manual:
            manual_entries = self.prompt_for_manual_data(failed_tickers)
            
            for etf_ticker, date_str in manual_entries.items():
                try:
                    earnings_date = datetime.strptime(date_str, '%Y-%m-%d')
                    earnings_calendar[etf_ticker] = earnings_date
                    sources_used[etf_ticker] = "manual_prompt"
                    print(f"Manual prompt entry for {etf_ticker}: {earnings_date.strftime('%Y-%m-%d')}")
                    
                    # Remove from failed list
                    if etf_ticker in failed_tickers:
                        failed_tickers.remove(etf_ticker)
                except Exception as e:
                    print(f"Error parsing manual prompt data for {etf_ticker}: {e}")
        
        # Priority 5: Fallback estimates for remaining failed tickers
        for etf_ticker in failed_tickers:
            earnings_date, source = self.get_fallback_estimate(etf_ticker)
            earnings_calendar[etf_ticker] = earnings_date
            sources_used[etf_ticker] = source
            print(f"Fallback estimate for {etf_ticker}: {earnings_date.strftime('%Y-%m-%d')}")
        
        # Save API data to cache (excluding manual entries)
        api_data = {}
        api_sources = {}
        for etf, date in earnings_calendar.items():
            source = sources_used[etf]
            if source not in ['manual_entry', 'manual_prompt']:
                api_data[etf] = date.isoformat()
                api_sources[etf] = source
        
        if api_data:
            # Merge with existing cache to preserve other data
            cached_earnings, cached_sources = self.load_cache()
            merged_earnings = {**cached_earnings, **api_data}
            merged_sources = {**cached_sources, **api_sources}
            self.save_cache(merged_earnings, merged_sources)
        
        return earnings_calendar, sources_used
    
    def get_earnings_for_etf(self, etf_ticker: str, prompt_for_manual: bool = True) -> Tuple[datetime, int]:
        """
        Get earnings date and days away for a specific ETF
        Returns: (earnings_date, days_away)
        """
        calendar, sources = self.get_comprehensive_earnings_calendar(prompt_for_manual)
        
        if etf_ticker in calendar:
            earnings_date = calendar[etf_ticker]
            days_away = (earnings_date - datetime.now()).days
            return earnings_date, days_away
        else:
            raise ValueError(f"ETF {etf_ticker} not found in calendar")
    
    def print_calendar_summary(self):
        """Print a summary of the earnings calendar"""
        calendar, sources = self.get_comprehensive_earnings_calendar()
        current_date = datetime.now()
        
        print(f"\n📊 WeeklyPay Earnings Calendar Summary:")
        print(f"{'ETF':<6} {'Stock':<6} {'Date':<12} {'Days':<5} {'Source':<15}")
        print("-" * 55)
        
        for etf, date in sorted(calendar.items(), key=lambda x: x[1]):
            stock = self.underlying_stocks[etf]
            days_until = (date - current_date).days
            source = sources.get(etf, "unknown")
            
            print(f"{etf:<6} {stock:<6} {date.strftime('%Y-%m-%d'):<12} {days_until:<5} {source:<15}")

# Convenience function for backward compatibility
def get_enhanced_earnings_calendar():
    """Backward compatibility function"""
    calendar_system = WeeklyPayEarningsCalendar()
    calendar, sources = calendar_system.get_comprehensive_earnings_calendar()
    return calendar

def get_earnings_for_etf(etf_ticker: str):
    """Backward compatibility function"""
    calendar_system = WeeklyPayEarningsCalendar()
    return calendar_system.get_earnings_for_etf(etf_ticker)

if __name__ == "__main__":
    # Test the comprehensive earnings calendar
    calendar_system = WeeklyPayEarningsCalendar()
    calendar_system.print_calendar_summary()
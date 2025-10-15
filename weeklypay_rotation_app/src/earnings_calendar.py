"""
Earnings Calendar Feed for WeeklyPay™ Rotation App
Handles earnings data collection from multiple sources
"""

import requests
import json
import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import yfinance as yf
from pathlib import Path

@dataclass
class EarningsEvent:
    """Earnings event with comprehensive data"""
    symbol: str
    company_name: str
    earnings_date: str
    earnings_time: str = "Unknown"  # BMO (Before Market Open), AMC (After Market Close)
    is_this_week: bool = False
    is_next_week: bool = False
    is_post_earnings: bool = False
    days_until_earnings: int = 0
    quarter: str = "Unknown"
    fiscal_year: str = "Unknown"
    estimated: bool = True  # True if estimated, False if confirmed
    
class EarningsCalendarFeed:
    """Earnings calendar data collection and management"""
    
    def __init__(self, etf_tracker):
        self.etf_tracker = etf_tracker
        self.earnings_events: Dict[str, EarningsEvent] = {}
        self.data_dir = Path("data")
        self.earnings_cache_file = self.data_dir / "earnings_cache.json"
        
        # Get underlying tickers from ETF tracker
        self.underlying_tickers = []
        for etf_symbol in self.etf_tracker.get_etf_list():
            etf_metadata = self.etf_tracker.get_etf_metadata(etf_symbol)
            if etf_metadata:
                self.underlying_tickers.append(etf_metadata.underlying_ticker)
        
        print(f"📅 Earnings Calendar initialized for: {', '.join(self.underlying_tickers)}")
    
    def add_manual_earnings(self, symbol: str, earnings_date: str, 
                          earnings_time: str = "Unknown", estimated: bool = True):
        """Manually add earnings event"""
        try:
            earnings_dt = datetime.datetime.strptime(earnings_date, "%Y-%m-%d")
            today = datetime.datetime.now()
            
            # Calculate week positioning
            week_start = today - datetime.timedelta(days=today.weekday())
            week_end = week_start + datetime.timedelta(days=6)
            next_week_start = week_end + datetime.timedelta(days=1)
            next_week_end = next_week_start + datetime.timedelta(days=6)
            
            is_this_week = week_start <= earnings_dt <= week_end
            is_next_week = next_week_start <= earnings_dt <= next_week_end
            is_post_earnings = earnings_dt < today
            days_until = (earnings_dt - today).days
            
            event = EarningsEvent(
                symbol=symbol,
                company_name=self._get_company_name(symbol),
                earnings_date=earnings_date,
                earnings_time=earnings_time,
                is_this_week=is_this_week,
                is_next_week=is_next_week,
                is_post_earnings=is_post_earnings,
                days_until_earnings=days_until,
                estimated=estimated
            )
            
            self.earnings_events[symbol] = event
            
            status = "THIS WEEK" if is_this_week else "NEXT WEEK" if is_next_week else "POST" if is_post_earnings else f"IN {days_until} DAYS"
            print(f"📅 Added {symbol} earnings: {earnings_date} {earnings_time} ({status})")
            
            return True
            
        except Exception as e:
            print(f"❌ Error adding manual earnings for {symbol}: {e}")
            return False
    
    def fetch_yahoo_earnings(self) -> bool:
        """Fetch earnings data from Yahoo Finance using yfinance"""
        print(f"🔍 Fetching earnings data from Yahoo Finance...")
        
        try:
            for ticker in self.underlying_tickers:
                try:
                    stock = yf.Ticker(ticker)
                    calendar = stock.calendar
                    
                    if calendar is not None and not calendar.empty:
                        # Get the next earnings date
                        earnings_date = calendar.index[0].strftime('%Y-%m-%d')
                        
                        # Try to get earnings time (BMO/AMC)
                        earnings_time = "Unknown"
                        if len(calendar.columns) > 0:
                            # Sometimes earnings time is in the data
                            earnings_time = "AMC"  # Default assumption
                        
                        self.add_manual_earnings(ticker, earnings_date, earnings_time, estimated=True)
                        
                    else:
                        print(f"⚠️  No earnings calendar data for {ticker}")
                        
                except Exception as e:
                    print(f"⚠️  Error fetching {ticker} earnings: {e}")
                    continue
            
            return True
            
        except Exception as e:
            print(f"❌ Error fetching Yahoo Finance earnings: {e}")
            return False
    
    def fetch_finnhub_earnings(self, api_key: str = None) -> bool:
        """Fetch earnings data from Finnhub API (requires free API key)"""
        if not api_key:
            print("⚠️  Finnhub API key required for earnings data")
            return False
        
        print(f"🔍 Fetching earnings data from Finnhub...")
        
        try:
            # Get date range (this week to next month)
            today = datetime.datetime.now()
            start_date = today.strftime('%Y-%m-%d')
            end_date = (today + datetime.timedelta(days=45)).strftime('%Y-%m-%d')
            
            url = f"https://finnhub.io/api/v1/calendar/earnings"
            params = {
                'from': start_date,
                'to': end_date,
                'token': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                earnings_calendar = data.get('earningsCalendar', [])
                
                for event in earnings_calendar:
                    symbol = event.get('symbol', '')
                    if symbol in self.underlying_tickers:
                        earnings_date = event.get('date', '')
                        earnings_time = event.get('when', 'Unknown')  # bmo, amc, etc.
                        
                        # Convert Finnhub time codes
                        time_mapping = {
                            'bmo': 'BMO',
                            'amc': 'AMC',
                            'dmh': 'During Market Hours'
                        }
                        earnings_time = time_mapping.get(earnings_time.lower(), earnings_time)
                        
                        self.add_manual_earnings(symbol, earnings_date, earnings_time, estimated=False)
                
                print(f"✅ Finnhub earnings data loaded")
                return True
            else:
                print(f"❌ Finnhub API error: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error fetching Finnhub earnings: {e}")
            return False
    
    def load_etrade_calendar_paste(self, calendar_text: str) -> bool:
        """Parse earnings data pasted from E*TRADE calendar"""
        print(f"📋 Processing E*TRADE calendar paste...")
        
        try:
            lines = calendar_text.strip().split('\n')
            events_added = 0
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                # Try to parse common E*TRADE formats:
                # "AMD - Oct 8, 2025 AMC"
                # "META Oct 9 BMO"
                # "NVDA 10/15/2025"
                
                parts = line.replace(',', '').split()
                if len(parts) >= 2:
                    symbol = parts[0].upper()
                    
                    if symbol in self.underlying_tickers:
                        # Try to extract date
                        date_str = ""
                        time_str = "Unknown"
                        
                        # Look for date patterns
                        for part in parts[1:]:
                            if '/' in part:  # MM/DD/YYYY or MM/DD/YY
                                date_str = self._normalize_date(part)
                            elif part.upper() in ['BMO', 'AMC']:
                                time_str = part.upper()
                            elif part.lower() in ['before', 'after']:
                                time_str = 'BMO' if part.lower() == 'before' else 'AMC'
                        
                        # Try to parse "Oct 8" format
                        if not date_str and len(parts) >= 3:
                            try:
                                month_day = f"{parts[1]} {parts[2]}"
                                current_year = datetime.datetime.now().year
                                date_obj = datetime.datetime.strptime(f"{month_day} {current_year}", "%b %d %Y")
                                date_str = date_obj.strftime("%Y-%m-%d")
                            except:
                                pass
                        
                        if date_str:
                            self.add_manual_earnings(symbol, date_str, time_str, estimated=True)
                            events_added += 1
            
            print(f"✅ Added {events_added} earnings events from E*TRADE calendar")
            return events_added > 0
            
        except Exception as e:
            print(f"❌ Error parsing E*TRADE calendar: {e}")
            return False
    
    def save_earnings_cache(self):
        """Save earnings data to cache file"""
        try:
            cache_data = {
                'last_updated': datetime.datetime.now().isoformat(),
                'earnings_events': {
                    symbol: {
                        'symbol': event.symbol,
                        'company_name': event.company_name,
                        'earnings_date': event.earnings_date,
                        'earnings_time': event.earnings_time,
                        'estimated': event.estimated,
                        'quarter': event.quarter,
                        'fiscal_year': event.fiscal_year
                    }
                    for symbol, event in self.earnings_events.items()
                }
            }
            
            with open(self.earnings_cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
            
            print(f"💾 Earnings cache saved: {len(self.earnings_events)} events")
            
        except Exception as e:
            print(f"❌ Error saving earnings cache: {e}")
    
    def load_earnings_cache(self) -> bool:
        """Load earnings data from cache file"""
        try:
            if not self.earnings_cache_file.exists():
                print("📝 No earnings cache found - starting fresh")
                return False
            
            with open(self.earnings_cache_file, 'r') as f:
                cache_data = json.load(f)
            
            # Check if cache is recent (within 24 hours)
            last_updated = datetime.datetime.fromisoformat(cache_data['last_updated'])
            if (datetime.datetime.now() - last_updated).hours > 24:
                print("⏰ Earnings cache is stale (>24 hours) - refresh recommended")
            
            # Load events and recalculate time-sensitive fields
            for symbol, event_data in cache_data['earnings_events'].items():
                earnings_date = event_data['earnings_date']
                earnings_time = event_data['earnings_time']
                estimated = event_data.get('estimated', True)
                
                self.add_manual_earnings(symbol, earnings_date, earnings_time, estimated)
            
            print(f"📂 Loaded {len(self.earnings_events)} earnings events from cache")
            return True
            
        except Exception as e:
            print(f"❌ Error loading earnings cache: {e}")
            return False
    
    def get_this_week_earnings(self) -> List[EarningsEvent]:
        """Get earnings events for this week"""
        return [event for event in self.earnings_events.values() if event.is_this_week]
    
    def get_next_week_earnings(self) -> List[EarningsEvent]:
        """Get earnings events for next week"""
        return [event for event in self.earnings_events.values() if event.is_next_week]
    
    def get_post_earnings(self) -> List[EarningsEvent]:
        """Get stocks that are post-earnings (within last 7 days)"""
        return [event for event in self.earnings_events.values() 
                if event.is_post_earnings and event.days_until_earnings >= -7]
    
    def display_earnings_calendar(self):
        """Display formatted earnings calendar"""
        print("\n" + "="*70)
        print("📅 EARNINGS CALENDAR - WEEKLYPAY™ UNDERLYINGS")
        print("="*70)
        
        # This week earnings
        this_week = self.get_this_week_earnings()
        if this_week:
            print(f"\n🟢 THIS WEEK ({len(this_week)} earnings):")
            for event in sorted(this_week, key=lambda x: x.earnings_date):
                print(f"   📈 {event.symbol}: {event.earnings_date} {event.earnings_time}")
                print(f"      {event.company_name}")
        
        # Next week earnings
        next_week = self.get_next_week_earnings()
        if next_week:
            print(f"\n🟡 NEXT WEEK ({len(next_week)} earnings):")
            for event in sorted(next_week, key=lambda x: x.earnings_date):
                print(f"   📊 {event.symbol}: {event.earnings_date} {event.earnings_time}")
        
        # Post-earnings
        post_earnings = self.get_post_earnings()
        if post_earnings:
            print(f"\n🔴 POST-EARNINGS (Last 7 days, {len(post_earnings)} stocks):")
            for event in sorted(post_earnings, key=lambda x: x.earnings_date, reverse=True):
                print(f"   📉 {event.symbol}: {event.earnings_date} ({abs(event.days_until_earnings)} days ago)")
        
        if not (this_week or next_week or post_earnings):
            print(f"\n📝 No recent earnings events found")
            print(f"   Use add_manual_earnings() or fetch data from APIs")
        
        print("\n" + "="*70)
    
    def _get_company_name(self, symbol: str) -> str:
        """Get company name for a symbol"""
        company_names = {
            'NVDA': 'NVIDIA Corporation',
            'AMD': 'Advanced Micro Devices',
            'META': 'Meta Platforms Inc',
            'MSFT': 'Microsoft Corporation',
            'GOOGL': 'Alphabet Inc Class A',
            'NFLX': 'Netflix Inc'
        }
        return company_names.get(symbol, symbol)
    
    def _normalize_date(self, date_str: str) -> str:
        """Normalize date string to YYYY-MM-DD format"""
        try:
            # Handle MM/DD/YYYY or MM/DD/YY
            parts = date_str.split('/')
            if len(parts) == 3:
                month, day, year = parts
                if len(year) == 2:
                    year = f"20{year}"
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        except:
            pass
        return date_str

# Example usage and testing
if __name__ == "__main__":
    from etf_tracker import ETFTracker
    
    # Initialize
    tracker = ETFTracker("../data/etf_list.json")
    earnings_feed = EarningsCalendarFeed(tracker)
    
    # Try loading cache first
    earnings_feed.load_earnings_cache()
    
    # Add some manual earnings for testing
    print(f"\n📝 Adding manual earnings for testing...")
    earnings_feed.add_manual_earnings("AMD", "2025-10-08", "AMC")
    earnings_feed.add_manual_earnings("META", "2025-09-30", "AMC")
    earnings_feed.add_manual_earnings("NFLX", "2025-10-09", "BMO")
    earnings_feed.add_manual_earnings("NVDA", "2025-10-15", "AMC")
    
    # Display calendar
    earnings_feed.display_earnings_calendar()
    
    # Save to cache
    earnings_feed.save_earnings_cache()
    
    # Test E*TRADE calendar paste
    print(f"\n📋 Testing E*TRADE calendar paste...")
    sample_etrade_text = """
    AMD - Oct 8, 2025 AMC
    MSFT Oct 10 BMO
    GOOGL 10/12/2025 AMC
    """
    earnings_feed.load_etrade_calendar_paste(sample_etrade_text)
    
    # Try Yahoo Finance (optional)
    print(f"\n🔍 Attempting Yahoo Finance fetch...")
    earnings_feed.fetch_yahoo_earnings()
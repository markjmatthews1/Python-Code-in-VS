# Earnings Calendar Data Collector for Catalyst Scanner
#
# Fetches upcoming earnings data for portfolio tickers from multiple sources
# with focus on next 7 days for immediate catalyst tracking.
#
# Author: Investment Catalyst Team
# Date: September 29, 2025

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from utils.logger import get_logger, log_api_call, log_data_update
from utils.error_handler import api_error_handler, handle_error, APIError


class EarningsCalendarCollector:
    """
    Earnings calendar data collector for tracking upcoming earnings
    events for portfolio tickers with impact scoring.
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize earnings calendar collector
        
        Args:
            api_key: Optional API key for premium data sources
        """
        self.logger = get_logger()
        self.api_key = api_key
        self.earnings_data = {}
        self.last_update = None
        
        # Configure data sources
        self.data_sources = {
            'alpha_vantage': {
                'enabled': bool(api_key),
                'base_url': 'https://www.alphavantage.co/query',
                'rate_limit': 5  # calls per minute
            },
            'yahoo_finance': {
                'enabled': True,  # Free source
                'base_url': 'https://query1.finance.yahoo.com/v8/finance/chart',
                'rate_limit': 60  # calls per minute
            },
            'fmp': {
                'enabled': False,  # Requires API key
                'base_url': 'https://financialmodelingprep.com/api/v3/earning_calendar',
                'rate_limit': 10
            }
        }
        
        # Earnings impact scoring weights
        self.impact_weights = {
            'market_cap': {
                'large': 1.5,    # $10B+
                'mid': 1.2,      # $2B-$10B
                'small': 1.0,    # <$2B
            },
            'time_of_day': {
                'before_market': 1.3,  # Pre-market earnings
                'after_market': 1.1,   # After-hours earnings
                'during_market': 1.5   # Rare but high impact
            },
            'volatility': {
                'high': 1.4,     # High historical earnings volatility
                'medium': 1.2,   # Medium volatility
                'low': 1.0       # Low volatility
            }
        }
        
        self.logger.info("Earnings calendar collector initialized")
    
    @api_error_handler("Earnings calendar", reraise=False)
    def fetch_earnings_calendar(self, tickers: List[str], days_ahead: int = 30, days_back: int = 2) -> Dict:
        """
        Fetch earnings calendar for specified tickers
        
        Args:
            tickers: List of ticker symbols
            days_ahead: Number of days to look ahead (default 30, increased from 7)
            days_back: Number of days to look back (default 2, catches recent announcements)
            
        Returns:
            Dict: Earnings calendar data with impact scores
        """
        try:
            self.logger.info(f"Fetching earnings calendar for {len(tickers)} tickers, {days_back} days back to {days_ahead} days ahead")
            
            earnings_events = {}
            
            # Calculate date range - NOW INCLUDES RECENT PAST
            today = datetime.now().date()
            start_date = today - timedelta(days=days_back)  # Include recent past (2 days back)
            end_date = today + timedelta(days=days_ahead)   # Extended forward window (30 days)
            
            # Try multiple data sources
            for ticker in tickers:
                ticker_earnings = self._fetch_ticker_earnings(ticker, start_date, end_date)
                if ticker_earnings:
                    earnings_events[ticker] = ticker_earnings
            
            # Score and rank earnings events
            scored_earnings = self._score_earnings_events(earnings_events)
            
            self.earnings_data = scored_earnings
            self.last_update = datetime.now()
            
            event_count = sum(len(events) for events in scored_earnings.values())
            log_data_update("earnings", event_count, f"Earnings calendar updated: {event_count} events")
            
            self.logger.info(f"Successfully fetched {event_count} earnings events")
            return scored_earnings
            
        except Exception as e:
            handle_error(e, "Earnings calendar fetch", "Failed to fetch earnings calendar data")
            return {}
    
    def _fetch_ticker_earnings(self, ticker: str, start_date, end_date) -> List[Dict]:
        """
        Fetch earnings events for a specific ticker
        
        Args:
            ticker: Ticker symbol
            start_date: Start date for search
            end_date: End date for search
            
        Returns:
            List[Dict]: Earnings events for the ticker
        """
        earnings_events = []
        
        # Try Yahoo Finance first (free and reliable)
        yahoo_events = self._fetch_from_yahoo(ticker, start_date, end_date)
        if yahoo_events:
            earnings_events.extend(yahoo_events)
        
        # Try Alpha Vantage if API key available
        if self.api_key and self.data_sources['alpha_vantage']['enabled']:
            av_events = self._fetch_from_alpha_vantage(ticker, start_date, end_date)
            if av_events:
                earnings_events.extend(av_events)
        
        # Deduplicate and merge events
        unique_events = self._deduplicate_earnings_events(earnings_events)
        
        return unique_events
    
    def _fetch_from_yahoo(self, ticker: str, start_date, end_date) -> List[Dict]:
        """Fetch earnings data from Yahoo Finance using yfinance for reliability"""
        try:
            # Use yfinance for more reliable earnings data
            import yfinance as yf
            
            log_api_call("yahoo_finance", f"earnings/{ticker}")
            stock = yf.Ticker(ticker)
            
            # Get earnings calendar
            try:
                calendar = stock.calendar
                if calendar is not None and calendar:
                    # Handle dict format (newer yfinance versions)
                    if isinstance(calendar, dict) and 'Earnings Date' in calendar:
                        earnings_dates = calendar['Earnings Date']
                        # Earnings Date can be a list
                        if isinstance(earnings_dates, list) and len(earnings_dates) > 0:
                            earnings_date = earnings_dates[0]
                        else:
                            earnings_date = earnings_dates
                        
                        # Check if within our date range
                        if start_date <= earnings_date <= end_date:
                            event = {
                                'ticker': ticker,
                                'date': earnings_date.isoformat(),
                                'time': 'after_market',  # Default assumption
                                'estimate': calendar.get('Earnings Average'),
                                'source': 'yfinance',
                                'confirmed': True
                            }
                            self.logger.info(f"Found {ticker} earnings on {earnings_date}")
                            return [event]
                        else:
                            self.logger.debug(f"{ticker} earnings {earnings_date} outside range {start_date} to {end_date}")
                    # Handle DataFrame format (older yfinance versions)
                    elif hasattr(calendar, 'index') and not calendar.empty:
                        # Extract earnings date
                        earnings_date = calendar.index[0].date()  # First (next) earnings date
                        
                        # Check if within our date range
                        if start_date <= earnings_date <= end_date:
                            event = {
                                'ticker': ticker,
                                'date': earnings_date.isoformat(),
                                'time': 'after_market',  # Default assumption
                                'estimate': calendar.loc[calendar.index[0], 'Earnings Average'] if 'Earnings Average' in calendar.columns else None,
                                'source': 'yfinance',
                                'confirmed': True
                            }
                            self.logger.info(f"Found {ticker} earnings on {earnings_date}")
                            return [event]
                        else:
                            self.logger.debug(f"{ticker} earnings {earnings_date} outside range {start_date} to {end_date}")
            except Exception as calendar_error:
                self.logger.debug(f"Calendar extraction failed for {ticker}: {calendar_error}")
            
            # Fallback to original Yahoo Finance API method
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
            params = {
                'modules': 'calendarEvents,earnings',
                'formatted': 'true'
            }
            
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract earnings date from calendar events
                calendar_events = data.get('quoteSummary', {}).get('result', [{}])[0].get('calendarEvents', {})
                earnings = calendar_events.get('earnings', {})
                
                if earnings:
                    earnings_date = earnings.get('earningsDate', [{}])[0].get('raw')
                    
                    if earnings_date:
                        # Convert timestamp to date
                        earnings_datetime = datetime.fromtimestamp(earnings_date)
                        
                        # Check if within our date range
                        if start_date <= earnings_datetime.date() <= end_date:
                            event = {
                                'ticker': ticker,
                                'date': earnings_datetime.date().isoformat(),
                                'time': self._determine_earnings_time(earnings_datetime),
                                'estimate': earnings.get('epsEstimate', {}).get('raw'),
                                'source': 'yahoo_finance_api',
                                'confirmed': True
                            }
                            return [event]
            
            return []
            
        except Exception as e:
            self.logger.warning(f"Yahoo Finance earnings fetch failed for {ticker}: {str(e)}")
            return []
    
    def _fetch_from_alpha_vantage(self, ticker: str, start_date, end_date) -> List[Dict]:
        """Fetch earnings data from Alpha Vantage"""
        try:
            url = self.data_sources['alpha_vantage']['base_url']
            params = {
                'function': 'EARNINGS_CALENDAR',
                'symbol': ticker,
                'apikey': self.api_key
            }
            
            log_api_call("alpha_vantage", f"earnings/{ticker}")
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                # Parse CSV response from Alpha Vantage
                lines = response.text.strip().split('\n')
                if len(lines) > 1:  # Has header + data
                    headers = lines[0].split(',')
                    
                    events = []
                    for line in lines[1:]:
                        values = line.split(',')
                        if len(values) >= len(headers):
                            event_data = dict(zip(headers, values))
                            
                            # Parse date
                            try:
                                event_date = datetime.strptime(event_data.get('reportDate', ''), '%Y-%m-%d').date()
                                
                                if start_date <= event_date <= end_date:
                                    event = {
                                        'ticker': ticker,
                                        'date': event_date.isoformat(),
                                        'time': 'after_market',  # Alpha Vantage default
                                        'estimate': event_data.get('estimate'),
                                        'source': 'alpha_vantage',
                                        'confirmed': True
                                    }
                                    events.append(event)
                            except ValueError:
                                continue
                    
                    return events
            
            return []
            
        except Exception as e:
            self.logger.warning(f"Alpha Vantage earnings fetch failed for {ticker}: {str(e)}")
            return []
    
    def _determine_earnings_time(self, earnings_datetime: datetime) -> str:
        """Determine if earnings are before, during, or after market"""
        hour = earnings_datetime.hour
        
        if hour < 9:  # Before 9 AM
            return 'before_market'
        elif hour >= 16:  # After 4 PM
            return 'after_market'
        else:  # During market hours
            return 'during_market'
    
    def _deduplicate_earnings_events(self, events: List[Dict]) -> List[Dict]:
        """Remove duplicate earnings events from multiple sources"""
        if not events:
            return []
        
        # Use date as the deduplication key
        unique_events = {}
        
        for event in events:
            date_key = event.get('date')
            if date_key:
                # Prefer Alpha Vantage over Yahoo Finance if both exist
                if date_key not in unique_events or event.get('source') == 'alpha_vantage':
                    unique_events[date_key] = event
        
        return list(unique_events.values())
    
    def _score_earnings_events(self, earnings_events: Dict) -> Dict:
        """
        Score earnings events for impact potential
        
        Args:
            earnings_events: Raw earnings events by ticker
            
        Returns:
            Dict: Scored and ranked earnings events
        """
        scored_events = {}
        
        for ticker, events in earnings_events.items():
            ticker_scored_events = []
            
            for event in events:
                # Calculate base impact score
                impact_score = self._calculate_earnings_impact_score(ticker, event)
                
                # Add score to event
                event['impact_score'] = impact_score
                event['impact_level'] = self._get_impact_level(impact_score)
                event['catalyst_priority'] = self._get_catalyst_priority(impact_score)
                
                ticker_scored_events.append(event)
            
            # Sort by impact score (highest first)
            ticker_scored_events.sort(key=lambda x: x['impact_score'], reverse=True)
            scored_events[ticker] = ticker_scored_events
        
        return scored_events
    
    def _calculate_earnings_impact_score(self, ticker: str, event: Dict) -> float:
        """Calculate impact score for an earnings event"""
        base_score = 5.0  # Base score out of 10
        
        # Time of day multiplier
        time_multiplier = self.impact_weights['time_of_day'].get(
            event.get('time', 'after_market'), 1.0
        )
        
        # Days until earnings (closer = higher impact)
        try:
            event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
            days_until = (event_date - datetime.now().date()).days
            
            if days_until == 0:
                days_multiplier = 2.0  # Today
            elif days_until == 1:
                days_multiplier = 1.8  # Tomorrow
            elif days_until <= 3:
                days_multiplier = 1.5  # This week
            else:
                days_multiplier = 1.0  # Next week
        except:
            days_multiplier = 1.0
        
        # Calculate final score
        final_score = base_score * time_multiplier * days_multiplier
        
        # Cap at 10.0
        return min(final_score, 10.0)
    
    def _get_impact_level(self, score: float) -> str:
        """Get impact level based on score"""
        if score >= 8.0:
            return 'HIGH'
        elif score >= 6.0:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _get_catalyst_priority(self, score: float) -> int:
        """Get catalyst priority (1-10) based on score"""
        return max(1, min(10, int(score)))
    
    def get_upcoming_earnings(self, days_ahead: int = 7) -> List[Dict]:
        """
        Get upcoming earnings events sorted by impact
        
        Args:
            days_ahead: Number of days to look ahead
            
        Returns:
            List[Dict]: Sorted earnings events
        """
        all_events = []
        
        for ticker, events in self.earnings_data.items():
            for event in events:
                try:
                    event_date = datetime.strptime(event['date'], '%Y-%m-%d').date()
                    days_until = (event_date - datetime.now().date()).days
                    
                    if 0 <= days_until <= days_ahead:
                        event['days_until'] = days_until
                        all_events.append(event)
                except:
                    continue
        
        # Sort by impact score, then by days until
        all_events.sort(key=lambda x: (-x.get('impact_score', 0), x.get('days_until', 999)))
        
        return all_events
    
    def get_earnings_summary(self) -> Dict:
        """Get summary of earnings calendar data"""
        if not self.earnings_data:
            return {}
        
        total_events = sum(len(events) for events in self.earnings_data.values())
        high_impact = sum(1 for ticker, events in self.earnings_data.items() 
                         for event in events if event.get('impact_level') == 'HIGH')
        
        # Get next earnings event
        upcoming = self.get_upcoming_earnings(days_ahead=7)
        next_earnings = upcoming[0] if upcoming else None
        
        return {
            'total_events': total_events,
            'high_impact_count': high_impact,
            'tickers_with_earnings': len(self.earnings_data),
            'next_earnings': next_earnings,
            'last_update': self.last_update,
            'data_sources_used': [source for source, config in self.data_sources.items() if config['enabled']]
        }
    
    def format_earnings_for_display(self, max_events: int = 10) -> List[Dict]:
        """
        Format earnings data for GUI display
        
        Args:
            max_events: Maximum number of events to return
            
        Returns:
            List[Dict]: Formatted earnings events
        """
        upcoming = self.get_upcoming_earnings()[:max_events]
        
        formatted_events = []
        for event in upcoming:
            try:
                # Format date
                event_date = datetime.strptime(event['date'], '%Y-%m-%d')
                formatted_date = event_date.strftime('%b %d')
                
                # Format time
                time_display = {
                    'before_market': 'Pre-Market',
                    'after_market': 'After Hours',
                    'during_market': 'Market Hours'
                }.get(event.get('time', 'after_market'), 'After Hours')
                
                formatted_event = {
                    'ticker': event['ticker'],
                    'date_display': formatted_date,
                    'time_display': time_display,
                    'days_until': event.get('days_until', 0),
                    'impact_level': event.get('impact_level', 'LOW'),
                    'impact_score': event.get('impact_score', 0),
                    'priority': event.get('catalyst_priority', 1),
                    'estimate': event.get('estimate', 'N/A'),
                    'source': event.get('source', 'unknown')
                }
                
                formatted_events.append(formatted_event)
                
            except Exception as e:
                self.logger.warning(f"Error formatting earnings event: {e}")
                continue
        
        return formatted_events


# Convenience function for quick access
def get_portfolio_earnings_calendar(tickers: List[str], api_key: str = None) -> EarningsCalendarCollector:
    """
    Quick function to get earnings calendar for portfolio
    
    Args:
        tickers: List of ticker symbols
        api_key: Optional API key for premium sources
        
    Returns:
        EarningsCalendarCollector: Collector with earnings data
    """
    collector = EarningsCalendarCollector(api_key)
    collector.fetch_earnings_calendar(tickers)
    return collector


if __name__ == "__main__":
    # Test the earnings calendar collector
    print("Testing Earnings Calendar Collector...")
    
    # Test tickers
    test_tickers = ['AAPL', 'MSFT', 'SMCI', 'MARA']
    
    collector = get_portfolio_earnings_calendar(test_tickers)
    
    summary = collector.get_earnings_summary()
    print(f"Earnings Summary: {summary}")
    
    upcoming = collector.get_upcoming_earnings()
    print(f"Upcoming earnings: {len(upcoming)} events")
    
    for event in upcoming[:3]:  # Show first 3
        print(f"  {event['ticker']}: {event['date']} ({event['impact_level']})")
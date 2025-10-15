"""
Data Collector - Real-time data integration for WeeklyPay™ Rotation App
Coordinates all data sources and feeds the signal engine
"""

import datetime
import json
from typing import Dict, List, Optional
from pathlib import Path

# Import our modules
from earnings_calendar import EarningsCalendarFeed
from etf_tracker import ETFTracker
from signal_engine import RotationRulesEngine
from sector_momentum import SectorMomentumTracker
from weekly_payouts import WeeklyPayoutTracker

class DataCollector:
    """Central data collection and coordination hub"""
    
    def __init__(self, etf_tracker: ETFTracker):
        self.etf_tracker = etf_tracker
        self.earnings_feed = EarningsCalendarFeed(etf_tracker)
        self.sector_momentum = SectorMomentumTracker()
        self.weekly_payouts = WeeklyPayoutTracker(etf_tracker)
        self.signal_engine = None  # Will be set externally
        
        self.data_sources = {
            'earnings': {'last_update': None, 'status': 'Not loaded'},
            'market_data': {'last_update': None, 'status': 'Not loaded'},
            'sector_data': {'last_update': None, 'status': 'Not loaded'},
            'sector_momentum': {'last_update': None, 'status': 'Not loaded'},
            'weekly_payouts': {'last_update': None, 'status': 'Not loaded'},
            'payout_data': {'last_update': None, 'status': 'Not loaded'}
        }
        
        print("🔄 Data Collector initialized")
    
    def set_signal_engine(self, signal_engine: RotationRulesEngine):
        """Set the signal engine reference"""
        self.signal_engine = signal_engine
    
    def collect_all_data(self, sources: List[str] = None) -> Dict:
        """Collect data from all or specified sources"""
        if sources is None:
            sources = ['earnings', 'market_data', 'sector_data', 'sector_momentum', 'weekly_payouts']
        
        print(f"🔄 Starting data collection: {', '.join(sources)}")
        results = {}
        
        for source in sources:
            try:
                if source == 'earnings':
                    results['earnings'] = self._collect_earnings_data()
                elif source == 'market_data':
                    results['market_data'] = self._collect_market_data()
                elif source == 'sector_data':
                    results['sector_data'] = self._collect_sector_data()
                elif source == 'sector_momentum':
                    results['sector_momentum'] = self._collect_sector_momentum()
                elif source == 'payout_data' or source == 'weekly_payouts':
                    results['weekly_payouts'] = self._collect_payout_data()
                
                self.data_sources[source]['last_update'] = datetime.datetime.now().isoformat()
                self.data_sources[source]['status'] = 'Success'
                
            except Exception as e:
                print(f"❌ Error collecting {source}: {e}")
                self.data_sources[source]['status'] = f'Error: {e}'
                results[source] = {'error': str(e)}
        
        # Feed earnings data to signal engine
        if self.signal_engine and 'earnings' in results:
            self._feed_earnings_to_signal_engine()
        
        return results
    
    def _collect_earnings_data(self) -> Dict:
        """Collect earnings calendar data"""
        print("📅 Collecting earnings data...")
        
        # Try loading from cache first
        cache_loaded = self.earnings_feed.load_earnings_cache()
        
        # Try fetching fresh data if cache is old or missing
        if not cache_loaded:
            print("🔍 Cache not available, trying Yahoo Finance...")
            yahoo_success = self.earnings_feed.fetch_yahoo_earnings()
            
            if yahoo_success:
                self.earnings_feed.save_earnings_cache()
        
        # Get earnings summary
        this_week = self.earnings_feed.get_this_week_earnings()
        next_week = self.earnings_feed.get_next_week_earnings()
        post_earnings = self.earnings_feed.get_post_earnings()
        
        return {
            'this_week': len(this_week),
            'next_week': len(next_week),
            'post_earnings': len(post_earnings),
            'events': {
                'this_week': [{'symbol': e.symbol, 'date': e.earnings_date, 'time': e.earnings_time} for e in this_week],
                'next_week': [{'symbol': e.symbol, 'date': e.earnings_date, 'time': e.earnings_time} for e in next_week],
                'post_earnings': [{'symbol': e.symbol, 'date': e.earnings_date, 'days_ago': abs(e.days_until_earnings)} for e in post_earnings]
            }
        }
    
    def _collect_market_data(self) -> Dict:
        """Collect market data for underlying stocks"""
        print("📊 Collecting market data...")
        
        # For now, using sample data - this would integrate with real APIs
        sample_market_data = {
            'NVDA': {'price': 145.50, 'rsi': 65.2, 'volume': 45000000},
            'AMD': {'price': 125.30, 'rsi': 58.7, 'volume': 38000000},
            'META': {'price': 485.20, 'rsi': 72.1, 'volume': 15000000},
            'MSFT': {'price': 378.90, 'rsi': 55.4, 'volume': 25000000},
            'GOOGL': {'price': 162.45, 'rsi': 48.3, 'volume': 18000000},
            'NFLX': {'price': 425.60, 'rsi': 43.8, 'volume': 12000000}
        }
        
        # Update signal engine if available
        if self.signal_engine:
            for symbol, data in sample_market_data.items():
                self.signal_engine.update_market_data(
                    symbol, data['price'], data['rsi'], 
                    volume=data['volume']
                )
        
        return {
            'symbols_updated': len(sample_market_data),
            'data': sample_market_data,
            'note': 'Using sample data - integrate with real API for production'
        }
    
    def _collect_sector_data(self) -> Dict:
        """Collect sector ETF data (SMH, XLC, XLK)"""
        print("🏭 Collecting sector data...")
        
        # Sample sector data - would integrate with real APIs
        sector_data = {
            'SMH': {'price': 195.40, 'rsi': 64.5, 'name': 'VanEck Semiconductor ETF'},
            'XLC': {'price': 67.80, 'rsi': 42.1, 'name': 'Communication Services SPDR'},
            'XLK': {'price': 178.20, 'rsi': 58.9, 'name': 'Technology Select Sector SPDR'}
        }
        
        # Update signal engine if available
        if self.signal_engine:
            for symbol, data in sector_data.items():
                self.signal_engine.update_sector_data(symbol, data['rsi'], data['price'])
        
        return {
            'sectors_updated': len(sector_data),
            'data': sector_data,
            'note': 'Using sample data - integrate with real API for production'
        }
    
    def _collect_sector_momentum(self) -> Dict:
        """Collect comprehensive sector momentum analysis"""
        print("📈 Collecting sector momentum analysis...")
        
        # Try loading cache first
        cache_loaded = self.sector_momentum.load_momentum_cache()
        
        # Update if cache is missing or stale
        if not cache_loaded:
            print("🔄 Cache not available, fetching fresh momentum data...")
            momentum_data = self.sector_momentum.update_all_sectors()
        else:
            momentum_data = self.sector_momentum.momentum_data
        
        # Update signal engine with sector momentum
        if self.signal_engine and momentum_data:
            sector_rsi = self.sector_momentum.get_sector_rsi_values()
            for symbol, rsi in sector_rsi.items():
                # Get price from momentum data
                price = momentum_data[symbol].price if symbol in momentum_data else 0.0
                self.signal_engine.update_sector_data(symbol, rsi, price)
        
        # Prepare summary
        signals = self.sector_momentum.get_sector_signals()
        rsi_values = self.sector_momentum.get_sector_rsi_values()
        
        return {
            'sectors_analyzed': len(momentum_data),
            'signals': signals,
            'rsi_values': rsi_values,
            'momentum_data': {
                symbol: {
                    'signal': momentum.momentum_signal,
                    'rsi': momentum.rsi_14,
                    'price': momentum.price,
                    'sma_crossover': momentum.sma_crossover,
                    'confidence': momentum.confidence
                }
                for symbol, momentum in momentum_data.items()
            },
            'note': 'Real-time sector momentum analysis with RSI and SMA crossovers'
        }
    
    def _collect_payout_data(self) -> Dict:
        """Collect weekly dividend payout data using WeeklyPayoutTracker"""
        print("💰 Collecting weekly dividend payout data...")
        
        # Collect all weekly payout data
        weekly_payouts = self.weekly_payouts.collect_weekly_payouts()
        
        # Update ETF tracker with payout data
        payouts_added = 0
        for symbol, payout in weekly_payouts.items():
            if self.etf_tracker.get_etf_metadata(symbol):
                self.etf_tracker.add_payout_data(
                    symbol, 
                    payout.pay_date, 
                    payout.dividend_amount
                )
                
                # Update NAV price
                current_price = payout.nav_price - 0.27  # Estimate current price
                self.etf_tracker.update_etf_price(symbol, current_price, payout.nav_price)
                payouts_added += 1
        
        # Get summary for return
        summary = self.weekly_payouts.get_weekly_summary()
        
        return {
            'payouts_added': payouts_added,
            'total_payouts': len(weekly_payouts),
            'highest_payout': summary['highest_payouts'][0] if summary['highest_payouts'] else None,
            'average_percentage': summary['average_payout_percentage'],
            'week_of': summary['week_of'],
            'data_sources': summary['data_sources'],
            'data': {
                symbol: {
                    'dividend_amount': payout.dividend_amount,
                    'nav_price': payout.nav_price,
                    'payout_percentage': payout.payout_percentage,
                    'ex_date': payout.ex_date,
                    'pay_date': payout.pay_date,
                    'source': payout.data_source
                }
                for symbol, payout in weekly_payouts.items()
            }
        }
    
    def _feed_earnings_to_signal_engine(self):
        """Feed earnings events to the signal engine"""
        if not self.signal_engine:
            return
        
        # Clear existing earnings in signal engine
        self.signal_engine.earnings_calendar = []
        
        # Add current earnings events
        for symbol, event in self.earnings_feed.earnings_events.items():
            self.signal_engine.add_earnings_event(symbol, event.earnings_date)
    
    def manual_earnings_input(self, etrade_calendar_text: str = None) -> bool:
        """Manual earnings input from E*TRADE calendar paste"""
        if etrade_calendar_text:
            success = self.earnings_feed.load_etrade_calendar_paste(etrade_calendar_text)
            if success:
                self.earnings_feed.save_earnings_cache()
                if self.signal_engine:
                    self._feed_earnings_to_signal_engine()
                return True
        
        # Interactive input
        print("📝 Manual Earnings Input")
        print("Enter earnings events (format: SYMBOL YYYY-MM-DD TIME)")
        print("Example: AMD 2025-10-08 AMC")
        print("Times: BMO (Before Market), AMC (After Market), or leave blank")
        print("Press Enter with empty line to finish:")
        
        events_added = 0
        while True:
            earnings_input = input("  Earnings: ").strip()
            if not earnings_input:
                break
            
            try:
                parts = earnings_input.split()
                if len(parts) >= 2:
                    symbol = parts[0].upper()
                    date = parts[1]
                    time = parts[2] if len(parts) > 2 else "Unknown"
                    
                    if self.earnings_feed.add_manual_earnings(symbol, date, time):
                        events_added += 1
                else:
                    print("  ⚠️  Invalid format. Use: SYMBOL YYYY-MM-DD [TIME]")
            except Exception as e:
                print(f"  ❌ Error: {e}")
        
        if events_added > 0:
            self.earnings_feed.save_earnings_cache()
            if self.signal_engine:
                self._feed_earnings_to_signal_engine()
            print(f"✅ Added {events_added} earnings events")
        
        return events_added > 0
    
    def display_data_status(self):
        """Display current data collection status"""
        print("\n" + "="*60)
        print("📊 DATA COLLECTION STATUS")
        print("="*60)
        
        for source, info in self.data_sources.items():
            status_icon = "✅" if info['status'] == 'Success' else "❌" if 'Error' in info['status'] else "⏳"
            last_update = info['last_update'] or 'Never'
            if last_update != 'Never':
                last_update = datetime.datetime.fromisoformat(last_update).strftime('%H:%M:%S')
            
            print(f"{status_icon} {source.upper():<12} | {info['status']:<20} | Last: {last_update}")
        
        print(f"\n📅 Earnings Summary:")
        this_week = self.earnings_feed.get_this_week_earnings()
        next_week = self.earnings_feed.get_next_week_earnings()
        post_earnings = self.earnings_feed.get_post_earnings()
        
        print(f"   🟢 This Week: {len(this_week)} earnings")
        print(f"   🟡 Next Week: {len(next_week)} earnings")
        print(f"   🔴 Post-Earnings: {len(post_earnings)} stocks")
        
        print("="*60)
    
    def display_sector_momentum_dashboard(self):
        """Display the sector momentum dashboard"""
        self.sector_momentum.display_momentum_dashboard()
    
    def display_weekly_payouts_dashboard(self):
        """Display the weekly payouts dashboard"""
        self.weekly_payouts.display_weekly_dashboard()
    
    def refresh_all_data(self) -> Dict:
        """Refresh all data sources"""
        print("🔄 REFRESHING ALL DATA SOURCES")
        print("="*40)
        
        results = self.collect_all_data()
        
        self.display_data_status()
        
        return results

# Example usage and testing
if __name__ == "__main__":
    # Initialize components
    tracker = ETFTracker("../data/etf_list.json")
    data_collector = DataCollector(tracker)
    signal_engine = RotationRulesEngine(tracker)
    
    # Connect data collector to signal engine
    data_collector.set_signal_engine(signal_engine)
    
    # Refresh all data
    results = data_collector.refresh_all_data()
    
    # Display earnings calendar
    data_collector.earnings_feed.display_earnings_calendar()
    
    # Generate signals with fresh data
    print("\n🧠 Generating signals with fresh data...")
    signals = signal_engine.generate_rotation_signals()
    signal_engine.display_rotation_signals(signals)
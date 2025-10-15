"""
WeeklyPay™ Rotation App - Command Line Interface
Simple CLI for running rotation analysis
"""

import sys
import argparse
import json
import datetime
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.etf_tracker import ETFTracker
from src.signal_engine import RotationRulesEngine
from src.data_collector import DataCollector

class WeeklyPayCLI:
    """Command line interface for WeeklyPay™ Rotation System"""
    
    def __init__(self):
        self.tracker = ETFTracker("data/etf_list.json")
        self.engine = RotationRulesEngine(self.tracker)
        self.data_collector = DataCollector(self.tracker)
        self.data_collector.set_signal_engine(self.engine)
        
    def quick_analysis(self):
        """Run a quick analysis with sample data"""
        print("🚀 Running Quick Analysis with Live Data Integration...")
        
        # Collect fresh data from all sources
        self.data_collector.refresh_all_data()
        
        # Generate signals
        signals = self.engine.generate_rotation_signals()
        self.engine.display_rotation_signals(signals)
        
        return signals
    
    def manual_data_entry(self):
        """Interactive manual data entry"""
        print("📝 Manual Data Entry Mode")
        
        # First, try to collect existing data
        print("🔄 Loading existing data...")
        self.data_collector.collect_all_data(['earnings'])
        
        # Show current earnings calendar
        self.data_collector.earnings_feed.display_earnings_calendar()
        
        # Ask if user wants to add more earnings
        add_earnings = input("\nAdd/update earnings events? (y/n): ").strip().lower() == 'y'
        if add_earnings:
            # Option 1: Paste from E*TRADE
            print("\nOption 1: Paste E*TRADE calendar text")
            print("(Or press Enter to skip and use manual entry)")
            etrade_text = input("Paste E*TRADE calendar: ").strip()
            
            if etrade_text:
                success = self.data_collector.earnings_feed.load_etrade_calendar_paste(etrade_text)
                if success:
                    print("✅ E*TRADE calendar data processed")
            else:
                # Option 2: Manual entry
                self.data_collector.manual_earnings_input()
        
        # Continue with other manual data entry...
        print("\nEnter current market data for each ETF:")
        
        etf_list = self.tracker.get_etf_list()
        
        for etf_symbol in etf_list:
            etf = self.tracker.get_etf_metadata(etf_symbol)
            print(f"\n🎯 {etf_symbol} ({etf.underlying_ticker}):")
            
            try:
                price = float(input(f"  Current price: $"))
                nav = float(input(f"  NAV: $"))
                self.tracker.update_etf_price(etf_symbol, price, nav)
                
                # Optional payout data
                payout_input = input(f"  Recent payout amount (or press Enter to skip): $")
                if payout_input.strip():
                    payout = float(payout_input)
                    payout_date = input(f"  Payout date (YYYY-MM-DD): ")
                    self.tracker.add_payout_data(etf_symbol, payout_date, payout)
                    
            except ValueError:
                print(f"  ⚠️  Skipping {etf_symbol} - invalid input")
        
        # Sector RSI input
        print(f"\n🏭 Sector Data:")
        try:
            smh_rsi = float(input("  SMH (Semiconductor) RSI: "))
            xlc_rsi = float(input("  XLC (Communication) RSI: "))
            xlk_rsi = float(input("  XLK (Technology) RSI: "))
            
            self.engine.update_sector_data("SMH", smh_rsi)
            self.engine.update_sector_data("XLC", xlc_rsi)
            self.engine.update_sector_data("XLK", xlk_rsi)
        except ValueError:
            print("  ⚠️  Using default sector RSI values")
            # Load default sector data
            self.data_collector.collect_all_data(['sector_data'])
        
        # Generate signals
        print(f"\n🧠 Generating Rotation Signals...")
        signals = self.engine.generate_rotation_signals()
        self.engine.display_rotation_signals(signals)
        
        return signals
    
    def data_management(self):
        """Data management interface"""
        print("📊 DATA MANAGEMENT MODE")
        print("="*30)
        
        while True:
            print("\nOptions:")
            print("1. View current data status")
            print("2. Refresh all data sources")
            print("3. Add/update earnings manually")
            print("4. View earnings calendar")
            print("5. Test Yahoo Finance API")
            print("6. Export current data")
            print("7. View sector momentum dashboard")
            print("8. Refresh sector momentum")
            print("9. View weekly payouts dashboard")
            print("10. Refresh weekly payouts")
            print("11. Generate alert format output")
            print("0. Return to main menu")
            
            choice = input("\nSelect option (0-11): ").strip()
            
            if choice == "1":
                self.data_collector.display_data_status()
            
            elif choice == "2":
                print("🔄 Refreshing all data sources...")
                self.data_collector.refresh_all_data()
            
            elif choice == "3":
                self.data_collector.manual_earnings_input()
            
            elif choice == "4":
                self.data_collector.earnings_feed.display_earnings_calendar()
            
            elif choice == "5":
                print("🔍 Testing Yahoo Finance API...")
                success = self.data_collector.earnings_feed.fetch_yahoo_earnings()
                if success:
                    self.data_collector.earnings_feed.save_earnings_cache()
                    print("✅ Yahoo Finance data updated")
                else:
                    print("❌ Yahoo Finance API failed")
            
            elif choice == "6":
                filename = input("Export filename (default: data_export.json): ").strip()
                if not filename:
                    filename = "data_export.json"
                self._export_all_data(filename)
            
            elif choice == "7":
                print("📈 Sector Momentum Dashboard:")
                self.data_collector.display_sector_momentum_dashboard()
            
            elif choice == "8":
                print("🔄 Refreshing sector momentum...")
                self.data_collector.collect_all_data(['sector_momentum'])
                print("✅ Sector momentum refreshed")
            
            elif choice == "9":
                print("💰 Weekly Payouts Dashboard:")
                self.data_collector.display_weekly_payouts_dashboard()
            
            elif choice == "10":
                print("🔄 Refreshing weekly payouts...")
                self.data_collector.collect_all_data(['weekly_payouts'])
                print("✅ Weekly payouts refreshed")
            
            elif choice == "11":
                print("🚨 Generating Alert Format Output:")
                self._generate_alert_format()
            
            elif choice == "0":
                break
            
            else:
                print("❌ Invalid option")
    
    def _export_all_data(self, filename: str):
        """Export all current data to JSON file"""
        try:
            export_data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'earnings_events': {
                    symbol: {
                        'symbol': event.symbol,
                        'earnings_date': event.earnings_date,
                        'earnings_time': event.earnings_time,
                        'is_this_week': event.is_this_week,
                        'is_next_week': event.is_next_week,
                        'is_post_earnings': event.is_post_earnings,
                        'days_until_earnings': event.days_until_earnings
                    }
                    for symbol, event in self.data_collector.earnings_feed.earnings_events.items()
                },
                'etf_data': {
                    symbol: {
                        'symbol': etf.symbol,
                        'name': etf.name,
                        'underlying_ticker': etf.underlying_ticker,
                        'current_price': etf.current_price,
                        'nav': etf.nav,
                        'last_payout_amount': etf.last_payout_amount,
                        'last_payout_date': etf.last_payout_date,
                        'recent_payout_history': etf.recent_payout_history
                    }
                    for symbol, etf in self.tracker.etfs.items()
                },
                'data_collection_status': self.data_collector.data_sources
            }
            
            with open(filename, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"✅ Data exported to '{filename}'")
            
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def export_signals(self, signals, filename="rotation_signals.json"):
        """Export signals to JSON file"""
        with open(filename, "w") as f:
            json.dump(signals, f, indent=2)
        print(f"✅ Signals exported to '{filename}'")
    
    def _load_sample_data(self):
        """Load sample data for testing"""
        # ETF prices
        etf_prices = {
            "NVDW": (45.23, 45.50),
            "AMDW": (32.67, 32.80),
            "HOOW": (67.89, 68.00),
            "MSFW": (89.45, 89.60),
            "GOOW": (156.78, 157.00),
            "NFLW": (78.90, 79.10)
        }
        
        for symbol, (price, nav) in etf_prices.items():
            self.tracker.update_etf_price(symbol, price, nav)
        
        # Sector data
        self.engine.update_sector_data("SMH", 64.5)
        self.engine.update_sector_data("XLC", 42.1)
        self.engine.update_sector_data("XLK", 58.9)
        
        # Earnings
        self.engine.add_earnings_event("AMD", "2025-10-08")
        self.engine.add_earnings_event("META", "2025-09-30")
        self.engine.add_earnings_event("NFLX", "2025-10-09")
        
        # Payouts
        payouts = [
            ("NVDW", "2025-10-01", 0.28),
            ("AMDW", "2025-10-01", 0.15),
            ("HOOW", "2025-10-01", 0.35),
            ("MSFW", "2025-10-01", 0.22),
            ("GOOW", "2025-10-01", 0.42),
            ("NFLW", "2025-10-01", 0.38),
        ]
        
        for symbol, date, amount in payouts:
            self.tracker.add_payout_data(symbol, date, amount)
    
    def _generate_alert_format(self):
        """Generate and display alert format output"""
        print("🚨 GENERATING ALERT FORMAT...")
        print("="*40)
        
        # Collect fresh data
        print("📊 Collecting comprehensive data...")
        self.data_collector.collect_all_data()
        
        # Integrate weekly payouts with signal engine
        self.engine.integrate_weekly_payouts(self.data_collector.weekly_payouts)
        
        # Generate alert format
        alert = self.engine.generate_alert_format(self.data_collector.weekly_payouts)
        
        # Display formatted alert
        print("\n" + "="*50)
        print("🚨 WEEKLYPAY™ ROTATION ALERT")
        print("="*50)
        
        print(f'{{')
        print(f'  "week": "{alert["week"]}",')
        print(f'  "rotate_in": {json.dumps(alert["rotate_in"])},')
        print(f'  "rotate_out": {json.dumps(alert["rotate_out"])},')
        print(f'  "notes": [')
        for i, note in enumerate(alert["notes"]):
            comma = "," if i < len(alert["notes"]) - 1 else ""
            print(f'    "{note}"{comma}')
        print(f'  ]')
        print(f'}}')
        
        # Save to file
        alert_filename = f"weekly_alert_{datetime.datetime.now().strftime('%Y%m%d')}.json"
        with open(alert_filename, 'w') as f:
            json.dump(alert, f, indent=2)
        
        print(f"\n✅ Alert saved to '{alert_filename}'")
        print("="*50)

def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(description="WeeklyPay™ Rotation System")
    parser.add_argument("--mode", choices=["quick", "manual", "data"], default="quick",
                      help="Analysis mode: quick (auto data collection), manual (interactive), data (data management)")
    parser.add_argument("--export", default="rotation_signals.json",
                      help="Export filename for signals")
    
    args = parser.parse_args()
    
    cli = WeeklyPayCLI()
    
    print("🎯 WEEKLYPAY™ ROTATION SYSTEM")
    print("="*40)
    
    if args.mode == "quick":
        signals = cli.quick_analysis()
        cli.export_signals(signals, args.export)
        print(f"\n✅ Analysis complete!")
        print(f"📊 Summary: {len(signals['rotate_in'])} rotate in, {len(signals['rotate_out'])} rotate out")
    elif args.mode == "manual":
        signals = cli.manual_data_entry()
        cli.export_signals(signals, args.export)
        print(f"\n✅ Analysis complete!")
        print(f"📊 Summary: {len(signals['rotate_in'])} rotate in, {len(signals['rotate_out'])} rotate out")
    elif args.mode == "data":
        cli.data_management()
        print(f"\n✅ Data management session complete!")

if __name__ == "__main__":
    main()
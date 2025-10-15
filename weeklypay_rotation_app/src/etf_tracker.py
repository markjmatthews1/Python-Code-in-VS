"""
ETF Tracker Module for WeeklyPay™ Rotation App
Manages the ETF universe and their metadata
"""

import json
import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path

@dataclass
class ETFMetadata:
    """Metadata for a WeeklyPay™ ETF"""
    symbol: str
    name: str
    underlying_ticker: str
    sector: str
    current_price: float = 0.0
    nav: float = 0.0
    recent_payout_history: List[Dict] = None
    last_payout_date: Optional[str] = None
    last_payout_amount: float = 0.0
    
    def __post_init__(self):
        if self.recent_payout_history is None:
            self.recent_payout_history = []

class ETFTracker:
    """Tracks WeeklyPay™ ETFs and their current status"""
    
    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.etfs: Dict[str, ETFMetadata] = {}
        self.load_etf_universe()
    
    def load_etf_universe(self):
        """Load ETF universe from configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Load tracked ETFs
            for etf_data in config.get('tracked_etfs', []):
                etf = ETFMetadata(
                    symbol=etf_data['symbol'],
                    name=etf_data['name'], 
                    underlying_ticker=etf_data['underlying'],
                    sector=etf_data['sector']
                )
                self.etfs[etf.symbol] = etf
                
            print(f"✅ Loaded {len(self.etfs)} WeeklyPay™ ETFs:")
            for symbol in self.etfs.keys():
                print(f"   - {symbol} ({self.etfs[symbol].underlying_ticker})")
                
        except Exception as e:
            print(f"❌ Error loading ETF universe: {e}")
    
    def update_etf_price(self, symbol: str, price: float, nav: float = None):
        """Update current price and NAV for an ETF"""
        if symbol in self.etfs:
            self.etfs[symbol].current_price = price
            if nav:
                self.etfs[symbol].nav = nav
            print(f"📊 Updated {symbol}: ${price:.2f}")
        else:
            print(f"⚠️  ETF {symbol} not found in tracker")
    
    def add_payout_data(self, symbol: str, payout_date: str, amount: float):
        """Add payout data for an ETF"""
        if symbol in self.etfs:
            payout_record = {
                "date": payout_date,
                "amount": amount,
                "percentage": (amount / self.etfs[symbol].nav * 100) if self.etfs[symbol].nav > 0 else 0
            }
            
            self.etfs[symbol].recent_payout_history.append(payout_record)
            self.etfs[symbol].last_payout_date = payout_date
            self.etfs[symbol].last_payout_amount = amount
            
            # Keep only last 10 payouts
            if len(self.etfs[symbol].recent_payout_history) > 10:
                self.etfs[symbol].recent_payout_history = self.etfs[symbol].recent_payout_history[-10:]
            
            print(f"💰 Added payout for {symbol}: ${amount:.4f} ({payout_record['percentage']:.2f}% of NAV)")
        else:
            print(f"⚠️  ETF {symbol} not found in tracker")
    
    def get_etf_list(self) -> List[str]:
        """Get list of tracked ETF symbols"""
        return list(self.etfs.keys())
    
    def get_etf_metadata(self, symbol: str) -> Optional[ETFMetadata]:
        """Get metadata for a specific ETF"""
        return self.etfs.get(symbol)
    
    def get_recent_payout_percentage(self, symbol: str) -> float:
        """Get the most recent payout percentage for an ETF"""
        if symbol in self.etfs and self.etfs[symbol].recent_payout_history:
            return self.etfs[symbol].recent_payout_history[-1]['percentage']
        return 0.0
    
    def display_portfolio_status(self):
        """Display current status of all tracked ETFs"""
        print("\n" + "="*60)
        print("📈 WEEKLYPAY™ ETF PORTFOLIO STATUS")
        print("="*60)
        
        for symbol, etf in self.etfs.items():
            print(f"\n🎯 {symbol} ({etf.underlying_ticker})")
            print(f"   Name: {etf.name}")
            print(f"   Price: ${etf.current_price:.2f}")
            print(f"   NAV: ${etf.nav:.2f}")
            print(f"   Last Payout: ${etf.last_payout_amount:.4f} on {etf.last_payout_date or 'N/A'}")
            
            if etf.recent_payout_history:
                recent_pct = etf.recent_payout_history[-1]['percentage']
                print(f"   Recent Payout %: {recent_pct:.2f}%")
            else:
                print(f"   Recent Payout %: No data")

# Example usage and testing
if __name__ == "__main__":
    # Test the ETF Tracker
    tracker = ETFTracker("../data/etf_list.json")
    
    # Add some sample data for testing
    tracker.update_etf_price("NVDW", 45.23, 45.50)
    tracker.update_etf_price("AMDW", 32.67, 32.80)
    tracker.update_etf_price("HOOW", 67.89, 68.00)
    
    # Add sample payout data
    tracker.add_payout_data("NVDW", "2025-10-01", 0.25)
    tracker.add_payout_data("AMDW", "2025-10-01", 0.18)
    tracker.add_payout_data("HOOW", "2025-10-01", 0.35)
    
    # Display status
    tracker.display_portfolio_status()
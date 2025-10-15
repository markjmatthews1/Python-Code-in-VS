"""
Signal Engine Demo - Test the WeeklyPay™ Rotation System
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.etf_tracker import ETFTracker
from src.signal_engine import RotationRulesEngine
import json

def demo_signal_engine():
    """Demonstrate the Signal Engine with realistic data"""
    
    print("🚀 WEEKLYPAY™ ROTATION SYSTEM DEMO")
    print("="*50)
    
    # Step 1: Initialize the system
    print("\n📋 Step 1: Loading ETF Universe...")
    tracker = ETFTracker("data/etf_list.json")
    engine = RotationRulesEngine(tracker)
    
    # Step 2: Load current market data (simulated real-time data)
    print("\n📊 Step 2: Loading Market Data...")
    
    # ETF prices (simulated current prices)
    etf_prices = {
        "NVDW": (45.23, 45.50),  # (price, nav)
        "AMDW": (32.67, 32.80),
        "HOOW": (67.89, 68.00),
        "MSFW": (89.45, 89.60),
        "GOOW": (156.78, 157.00),
        "NFLW": (78.90, 79.10)
    }
    
    for symbol, (price, nav) in etf_prices.items():
        tracker.update_etf_price(symbol, price, nav)
    
    # Underlying stock data with RSI
    underlying_data = {
        "NVDA": (145.50, 65.2),  # (price, rsi)
        "AMD": (125.30, 58.7),
        "META": (485.20, 72.1),
        "MSFT": (378.90, 55.4),
        "GOOGL": (162.45, 48.3),
        "NFLX": (425.60, 43.8)
    }
    
    for symbol, (price, rsi) in underlying_data.items():
        engine.update_market_data(symbol, price, rsi)
    
    # Step 3: Load sector data
    print("\n🏭 Step 3: Loading Sector Data...")
    engine.update_sector_data("SMH", 64.5, 195.40)  # Semiconductor ETF - bullish
    engine.update_sector_data("XLC", 42.1, 67.80)   # Communication - bearish
    engine.update_sector_data("XLK", 58.9, 178.20)  # Technology - neutral
    
    # Step 4: Load earnings calendar
    print("\n📅 Step 4: Loading Earnings Calendar...")
    earnings_events = [
        ("AMD", "2025-10-08"),    # This week - Tuesday
        ("META", "2025-09-30"),   # Post-earnings (last week)
        ("NFLX", "2025-10-09"),   # This week - Wednesday
        ("GOOGL", "2025-10-15"),  # Next week
    ]
    
    for symbol, date in earnings_events:
        engine.add_earnings_event(symbol, date)
    
    # Step 5: Load recent payout data
    print("\n💰 Step 5: Loading Payout Data...")
    recent_payouts = [
        ("NVDW", "2025-10-01", 0.28),  # 0.61% of NAV - HIGH
        ("AMDW", "2025-10-01", 0.15),  # 0.46% of NAV - LOW
        ("HOOW", "2025-10-01", 0.35),  # 0.51% of NAV - HIGH
        ("MSFW", "2025-10-01", 0.22),  # 0.25% of NAV - LOW
        ("GOOW", "2025-10-01", 0.42),  # 0.27% of NAV - LOW
        ("NFLW", "2025-10-01", 0.38),  # 0.48% of NAV - LOW
    ]
    
    for symbol, date, amount in recent_payouts:
        tracker.add_payout_data(symbol, date, amount)
    
    # Step 6: Display portfolio status
    print("\n" + "="*60)
    tracker.display_portfolio_status()
    
    # Step 7: Generate rotation signals
    print("\n🧠 Step 6: Generating Rotation Signals...")
    signals = engine.generate_rotation_signals()
    
    # Step 8: Display the signals
    engine.display_rotation_signals(signals)
    
    # Step 9: Export signals as JSON for external use
    print("\n💾 Step 7: Exporting Signals...")
    
    with open("rotation_signals_output.json", "w") as f:
        json.dump(signals, f, indent=2)
    
    print("✅ Signals exported to 'rotation_signals_output.json'")
    
    # Step 10: Summary of logic
    print(f"\n🎯 ROTATION LOGIC SUMMARY:")
    print(f"   🟢 ROTATE IN triggers:")
    print(f"      • Earnings this week (AMD, NFLX)")
    print(f"      • Sector RSI > 60 (SMH at 64.5)")
    print(f"      • Payout > 0.5% NAV (NVDW, HOOW)")
    print(f"   🔴 ROTATE OUT triggers:")
    print(f"      • Post-earnings (META)")
    print(f"      • Sector RSI < 40 (XLC at 42.1)")
    print(f"   🟡 HOLD:")
    print(f"      • No strong signals or conflicting signals")
    
    return signals

if __name__ == "__main__":
    signals = demo_signal_engine()
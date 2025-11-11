"""
Debug script to check actual holdings categorization
Run this to see exactly what's happening with your real data
"""

from rotation_engine import RotationEngine
from datetime import datetime, timedelta
import os

def debug_holdings():
    engine = RotationEngine()
    
    print("=" * 90)
    print("DEBUG: Current Holdings Categorization")
    print("=" * 90)
    
    current_time = engine.get_current_time_et()
    print(f"\nCurrent Time: {current_time.strftime('%A, %B %d at %I:%M %p ET')}")
    
    # Get next rotation
    next_targets = engine.find_next_rotation_targets()
    if next_targets:
        ex_day = next_targets[0]['next_ex_div_date'].strftime('%A')
        tickers = [t['ticker'] for t in next_targets]
        print(f"Next Rotation Group: {ex_day} - {', '.join(tickers)}")
    
    # Check if trades file exists
    trades_file = 'weeklypay_trades.csv'
    if not os.path.exists(trades_file):
        print(f"\n❌ {trades_file} not found!")
        print("Creating sample test data...")
        
        # Use sample test data
        sample_holdings = [
            {
                'ticker': 'NVDW',
                'purchase_date': current_time - timedelta(days=5),
                'purchase_price': 42.00,
                'current_price': 42.50,
                'shares': 100
            },
            {
                'ticker': 'QDTE',
                'purchase_date': current_time - timedelta(days=4),
                'purchase_price': 51.00,
                'current_price': 50.25,
                'shares': 100
            }
        ]
        
        print("\nSample Holdings:")
        for h in sample_holdings:
            nav_pct = ((h['current_price'] - h['purchase_price']) / h['purchase_price']) * 100
            print(f"  • {h['ticker']}: ${h['purchase_price']} → ${h['current_price']} (NAV {nav_pct:+.2f}%)")
        
        categorized = engine.analyze_holdings(sample_holdings)
        
    else:
        print(f"\n✅ Found {trades_file}")
        print("Loading actual holdings from file...")
        
        # Load holdings from CSV (simplified version)
        import pandas as pd
        
        try:
            trades_df = pd.read_csv(trades_file)
            print(f"Loaded {len(trades_df)} trades")
            
            # For now, create sample data - you can enhance this to parse the CSV
            sample_holdings = [
                {
                    'ticker': 'NVDW',
                    'purchase_date': current_time - timedelta(days=5),
                    'purchase_price': 42.00,
                    'current_price': 42.50,
                    'shares': 100
                },
                {
                    'ticker': 'QDTE',
                    'purchase_date': current_time - timedelta(days=4),
                    'purchase_price': 51.00,
                    'current_price': 50.25,
                    'shares': 100
                }
            ]
            
            categorized = engine.analyze_holdings(sample_holdings)
            
        except Exception as e:
            print(f"Error loading trades: {e}")
            return
    
    print(f"\n{'=' * 90}")
    print("CATEGORIZATION RESULTS")
    print(f"{'=' * 90}")
    
    print(f"\n✅ READY TO SELL ({len(categorized['ready_to_sell'])} tickers):")
    if categorized['ready_to_sell']:
        for h in categorized['ready_to_sell']:
            print(f"  • {h['ticker']}: {h['reason']}")
            print(f"    NAV: {h['nav_pct']:+.2f}%")
    else:
        print("  (None)")
    
    print(f"\n🔒 MUST HOLD ({len(categorized['must_hold'])} tickers):")
    if categorized['must_hold']:
        for h in categorized['must_hold']:
            print(f"  • {h['ticker']}: {h['reason']}")
            print(f"    NAV: {h['nav_pct']:+.2f}%")
    else:
        print("  (None)")
    
    print(f"\n📉 HOLD FOR NAV ({len(categorized['hold_for_nav'])} tickers):")
    if categorized['hold_for_nav']:
        for h in categorized['hold_for_nav']:
            print(f"  • {h['ticker']}: {h['reason']}")
            print(f"    NAV: {h['nav_pct']:+.2f}%")
    else:
        print("  (None)")
    
    print(f"\n{'=' * 90}")
    print("VERIFICATION")
    print(f"{'=' * 90}")
    
    # Check for QDTE specifically
    qdte_in_ready = any(h['ticker'] == 'QDTE' for h in categorized['ready_to_sell'])
    qdte_in_must = any(h['ticker'] == 'QDTE' for h in categorized['must_hold'])
    qdte_in_nav = any(h['ticker'] == 'QDTE' for h in categorized['hold_for_nav'])
    
    print(f"\nQDTE Status:")
    print(f"  In Ready to Sell? {qdte_in_ready}")
    print(f"  In Must Hold? {qdte_in_must}")
    print(f"  In Hold for NAV? {qdte_in_nav}")
    
    if qdte_in_ready and qdte_in_nav:
        print(f"\n  ✅ CORRECT: QDTE in both Ready to Sell and Hold for NAV")
    else:
        print(f"\n  ❌ ISSUE: QDTE should be in both categories")
        if not qdte_in_ready:
            print(f"     Missing from Ready to Sell")
        if not qdte_in_nav:
            print(f"     Missing from Hold for NAV")
    
    # Show the dashboard display format
    print(f"\n{'=' * 90}")
    print("DASHBOARD DISPLAY FORMAT (as it would appear)")
    print(f"{'=' * 90}")
    
    print("\n✅ Ready to Sell:")
    for h in categorized['ready_to_sell']:
        print(f"  {h['ticker']} {h['nav_pct']:+.2f}%")
    
    print("\n🔒 Must Hold:")
    for h in categorized['must_hold']:
        dividend_status = h.get('dividend_status', 'unknown')
        print(f"  {h['ticker']} {dividend_status}")
    
    print("\n📉 Hold for NAV:")
    for h in categorized['hold_for_nav']:
        print(f"  {h['ticker']} {h['nav_pct']:+.2f}%")
    
    print(f"\n{'=' * 90}")
    print("If QDTE is not showing in both columns in your dashboard,")
    print("the issue may be with your actual holdings data or price data.")
    print("Make sure:")
    print("  1. QDTE purchase price is higher than current price")
    print("  2. QDTE was purchased before last ex-dividend date")
    print("  3. QDTE is not in the current rotation group")
    print(f"{'=' * 90}")

if __name__ == "__main__":
    debug_holdings()

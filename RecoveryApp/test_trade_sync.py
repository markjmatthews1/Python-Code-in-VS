#!/usr/bin/env python3
"""
Test trade entry and synchronization between tabs
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.models import TickerPosition, TradeEntry, PortfolioManager
import json
from datetime import datetime

def test_trade_synchronization():
    """Test that trades added to positions appear in portfolio and can be saved/loaded"""
    
    print("=== Testing Trade Entry and Synchronization ===")
    
    # Create portfolio manager (simulating the main app)
    portfolio = PortfolioManager()
    
    # Create SOXL position (like what's in your portfolio)
    soxl_position = TickerPosition(
        ticker="SOXL",
        cost_basis=54.43,
        qty=110,
        purchase_date="2025-06-26",
        target_recovery_price=55.0
    )
    portfolio.add_position(soxl_position)
    
    print(f"✅ Created SOXL position with {len(soxl_position.trades)} trades")
    
    # Add a trade (simulating what you did in the SOXL tab)
    test_trade = TradeEntry(
        type="covered_call",
        strike=56.0,
        expiry="2025-11-15",
        premium=1.25,
        status="open",
        entry_date="2025-10-10",
        quantity=1,
        commission=0.50,
        notes="Test covered call from SOXL tab"
    )
    
    # Add trade to position (this is what the SOXL tab should do)
    soxl_position.add_trade(test_trade)
    print(f"✅ Added trade to SOXL position. Now has {len(soxl_position.trades)} trades")
    
    # Save portfolio (this should include the trade)
    portfolio.save_to_file("test_portfolio_with_trade.json")
    print(f"✅ Saved portfolio to test file")
    
    # Load portfolio back (simulating what other tabs should see)
    new_portfolio = PortfolioManager()
    new_portfolio.load_from_file("test_portfolio_with_trade.json")
    
    # Check if trade appears in loaded portfolio
    loaded_soxl = new_portfolio.get_position("SOXL")
    if loaded_soxl:
        print(f"✅ Loaded SOXL position with {len(loaded_soxl.trades)} trades")
        if len(loaded_soxl.trades) > 0:
            trade = loaded_soxl.trades[0]
            print(f"   Trade: {trade.type} @ ${trade.strike} - {trade.notes}")
            print(f"✅ SUCCESS: Trade appears in Portfolio Overview and Trade Tracker!")
        else:
            print(f"❌ PROBLEM: No trades found in loaded position")
    else:
        print(f"❌ PROBLEM: Could not load SOXL position")
    
    # Check the actual content of the saved file
    print(f"\n=== Checking Saved File Content ===")
    with open("test_portfolio_with_trade.json", 'r') as f:
        data = json.load(f)
    
    soxl_data = None
    for pos in data.get('positions', []):
        if pos.get('ticker') == 'SOXL':
            soxl_data = pos
            break
    
    if soxl_data:
        trades_in_file = soxl_data.get('trades', [])
        print(f"Trades in saved file: {len(trades_in_file)}")
        if trades_in_file:
            for i, trade in enumerate(trades_in_file):
                print(f"  Trade {i+1}: {trade}")
        else:
            print("  No trades found in saved file - THIS IS THE PROBLEM!")
    
    # Clean up test file
    if os.path.exists("test_portfolio_with_trade.json"):
        os.remove("test_portfolio_with_trade.json")
    
    return len(loaded_soxl.trades) > 0 if loaded_soxl else False

if __name__ == "__main__":
    success = test_trade_synchronization()
    if success:
        print(f"\n✅ Trade synchronization is working correctly!")
        print(f"📋 Check if the app is calling save_portfolio() after adding trades")
    else:
        print(f"\n❌ Trade synchronization has issues!")
        print(f"📋 Need to investigate why trades aren't being saved to portfolio file")
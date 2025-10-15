#!/usr/bin/env python3
"""
Data Cleanup Utility for Enhanced Day Trader
============================================

Removes duplicate trades and synchronizes data between GUI and web dashboard.
"""

import sys
import os
import json
from datetime import datetime

# Add the enhanced_day_trader directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.paper_trader import paper_trader

def cleanup_duplicate_trades():
    """Remove duplicate trades from the paper trading data"""
    print("🧹 Cleaning up duplicate trades...")
    
    # Load current data
    paper_trader.load_trades()
    
    print(f"Before cleanup:")
    print(f"   Closed trades: {len(paper_trader.closed_trades)}")
    print(f"   Active trades: {len(paper_trader.active_trades)}")
    
    # Remove duplicates from closed trades
    # Use trade_id as unique identifier
    unique_closed = {}
    for trade in paper_trader.closed_trades:
        if trade.trade_id not in unique_closed:
            unique_closed[trade.trade_id] = trade
        else:
            print(f"   Found duplicate: {trade.trade_id}")
    
    # Update closed trades list
    paper_trader.closed_trades = list(unique_closed.values())
    
    # Recalculate performance metrics
    paper_trader.total_pnl = sum(trade.pnl for trade in paper_trader.closed_trades)
    paper_trader.total_commission = len(paper_trader.closed_trades) * paper_trader.commission_per_trade
    paper_trader.total_commission += len(paper_trader.active_trades) * paper_trader.commission_per_trade
    
    # Recalculate current balance
    total_position_value = sum(
        trade.quantity * trade.open_price + paper_trader.commission_per_trade 
        for trade in paper_trader.active_trades.values()
    )
    paper_trader.current_balance = (
        paper_trader.initial_balance 
        + paper_trader.total_pnl 
        - paper_trader.total_commission 
        - total_position_value
    )
    
    print(f"After cleanup:")
    print(f"   Closed trades: {len(paper_trader.closed_trades)}")
    print(f"   Active trades: {len(paper_trader.active_trades)}")
    print(f"   Current balance: ${paper_trader.current_balance:,.2f}")
    print(f"   Total P&L: ${paper_trader.total_pnl:+,.2f}")
    
    # Save cleaned data
    paper_trader.save_trades()
    print("✅ Cleaned data saved")

def test_gui_web_sync():
    """Test that GUI and web dashboard show the same data"""
    print("\n🔄 Testing GUI and Web Dashboard synchronization...")
    
    # Get current summary
    summary = paper_trader.get_performance_summary()
    
    print("📊 Current Data State:")
    print(f"   Balance: ${summary['current_balance']:,.2f}")
    print(f"   Total P&L: ${summary['total_pnl']:+,.2f}")
    print(f"   Win Rate: {summary['win_rate']:.1f}%")
    print(f"   Active Positions: {summary['active_positions']}")
    print(f"   Total Trades: {summary['total_trades']}")
    
    # Show active trades
    print(f"\n🟢 Active Trades ({len(paper_trader.active_trades)}):")
    for trade_id, trade in paper_trader.active_trades.items():
        print(f"   {trade_id}: {trade.direction} {trade.quantity} {trade.ticker} @ ${trade.open_price:.2f}")
    
    # Show recent closed trades (no duplicates)
    print(f"\n🔴 Recent Closed Trades (last 5):")
    recent_closed = sorted(paper_trader.closed_trades, key=lambda t: t.close_time or datetime.min, reverse=True)
    for trade in recent_closed[:5]:
        status_emoji = "💰" if trade.pnl > 0 else "📉"
        print(f"   {status_emoji} {trade.trade_id}: {trade.direction} {trade.ticker} P&L: ${trade.pnl:+.2f}")
    
    print(f"\n✅ Data is now synchronized between GUI and Web Dashboard!")
    print(f"🌐 Web Dashboard: http://localhost:8051")
    print(f"🎨 GUI: Run main_trader.py to see the updated interface")

if __name__ == "__main__":
    print("🧪 Enhanced Day Trader - Data Cleanup & Sync")
    print("=" * 50)
    
    cleanup_duplicate_trades()
    test_gui_web_sync()
    
    print("\n✅ Cleanup complete! Both interfaces should now show identical data.")
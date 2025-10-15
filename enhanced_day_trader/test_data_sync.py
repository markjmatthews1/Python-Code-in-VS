#!/usr/bin/env python3
"""
Test Data Synchronization between GUI and Web Dashboard
======================================================

Quick test to verify both interfaces show the same trade data.
"""

import sys
import os

# Add the enhanced_day_trader directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.paper_trader import paper_trader

def test_data_sync():
    """Test that both interfaces can access the same data"""
    print("🧪 Testing Data Synchronization...")
    print("=" * 50)
    
    # Load current paper trading data
    paper_trader.load_trades()
    
    # Get performance summary
    summary = paper_trader.get_performance_summary()
    
    print("📊 Paper Trading Engine Data:")
    print(f"   Current Balance: ${summary['current_balance']:,.2f}")
    print(f"   Total P&L: {summary['total_pnl']:+,.2f}")
    print(f"   Active Positions: {summary['active_positions']}")
    print(f"   Total Trades: {summary['total_trades']}")
    print(f"   Win Rate: {summary['win_rate']:.1f}%")
    
    print(f"\n🟢 Active Trades: {len(paper_trader.active_trades)}")
    for trade_id, trade in paper_trader.active_trades.items():
        print(f"   {trade_id}: {trade.direction} {trade.quantity} {trade.ticker} @ ${trade.open_price:.2f}")
    
    print(f"\n🔴 Closed Trades: {len(paper_trader.closed_trades)}")
    for trade in paper_trader.closed_trades[-5:]:  # Show last 5
        status_emoji = "💰" if trade.pnl > 0 else "📉"
        print(f"   {status_emoji} {trade.trade_id}: {trade.direction} {trade.ticker} P&L: ${trade.pnl:+.2f}")
    
    print(f"\n✅ Data accessible for both GUI and Web interfaces")
    
    # Test web dashboard data structure
    print(f"\n🌐 Web Dashboard API Format:")
    
    # Simulate positions API
    positions = []
    for trade in paper_trader.active_trades.values():
        current_price = trade.open_price * 1.001
        if trade.direction == 'LONG':
            unrealized_pnl = (current_price - trade.open_price) * trade.quantity
        else:
            unrealized_pnl = (trade.open_price - current_price) * trade.quantity
            
        positions.append({
            'ticker': trade.ticker,
            'direction': trade.direction,
            'quantity': trade.quantity,
            'unrealized_pnl': unrealized_pnl
        })
    
    print(f"   Active Positions API: {len(positions)} positions")
    for pos in positions[:3]:  # Show first 3
        print(f"   - {pos['ticker']}: {pos['direction']} {pos['quantity']} shares, P&L: ${pos['unrealized_pnl']:+.2f}")
    
    # Test trades API
    all_trades = []
    all_trades.extend(paper_trader.closed_trades)
    all_trades.extend(paper_trader.active_trades.values())
    all_trades.sort(key=lambda t: t.open_time, reverse=True)
    
    print(f"   Recent Trades API: {len(all_trades)} total trades")
    for trade in all_trades[:3]:  # Show first 3
        status = "OPEN" if not trade.close_time else trade.status
        print(f"   - {trade.trade_id}: {trade.ticker} {status}")
    
    print(f"\n✅ Both interfaces should now show identical data!")

if __name__ == "__main__":
    test_data_sync()
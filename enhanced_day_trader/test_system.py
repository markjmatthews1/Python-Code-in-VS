#!/usr/bin/env python3
"""
Enhanced Day Trader - Test Script
================================

Test the complete paper trading system with sample trades
and colorful display functionality.

Author: GitHub Copilot
Date: October 15, 2025
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add the enhanced_day_trader directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.paper_trader import paper_trader
from ui.trade_display import create_trade_display

def create_sample_trades():
    """Create some sample trades for testing"""
    print("🧪 Creating sample trades for testing...")
    
    # Sample trade signals
    test_signals = [
        {
            'symbol': 'XLK',
            'direction': 'BUY',
            'entry_price': 285.50,
            'stop_loss': 284.36,
            'take_profit': 287.78,
            'signal_strength': 0.65
        },
        {
            'symbol': 'XLF',
            'direction': 'SELL',
            'entry_price': 53.25,
            'stop_loss': 53.46,
            'take_profit': 52.82,
            'signal_strength': 0.58
        },
        {
            'symbol': 'XLV',
            'direction': 'BUY',
            'entry_price': 142.80,
            'stop_loss': 141.37,
            'take_profit': 145.66,
            'signal_strength': 0.72
        },
        {
            'symbol': 'XLE',
            'direction': 'BUY',
            'entry_price': 78.45,
            'stop_loss': 77.61,
            'take_profit': 79.84,
            'signal_strength': 0.55
        }
    ]
    
    # Open the trades
    trade_ids = []
    for signal in test_signals:
        try:
            trade = paper_trader.open_trade(signal)
            if trade:
                trade_ids.append(trade.trade_id)
                print(f"✅ Opened trade {trade.trade_id}: {signal['direction']} {signal['symbol']} @ ${signal['entry_price']}")
            else:
                print(f"❌ Failed to open trade for {signal['symbol']}")
        except Exception as e:
            print(f"❌ Failed to open trade for {signal['symbol']}: {e}")
    
    return trade_ids

def simulate_trade_outcomes(trade_ids):
    """Simulate some trade outcomes for testing"""
    print("\n🎲 Simulating trade outcomes...")
    
    # Close some trades with different outcomes
    if len(trade_ids) >= 2:
        # Close first trade with profit
        try:
            first_trade = paper_trader.active_trades[trade_ids[0]]
            profit_price = first_trade.take_profit * 0.95  # Close near take profit
            paper_trader.close_trade(trade_ids[0], profit_price, 'CLOSED_TAKE_PROFIT')
            print(f"✅ Closed trade {trade_ids[0]} with profit")
        except Exception as e:
            print(f"❌ Error closing profitable trade: {e}")
        
        # Close second trade with loss  
        try:
            if trade_ids[1] in paper_trader.active_trades:
                second_trade = paper_trader.active_trades[trade_ids[1]]
                loss_price = second_trade.stop_loss * 1.01  # Close near stop loss
                paper_trader.close_trade(trade_ids[1], loss_price, 'CLOSED_STOP_LOSS')
                print(f"✅ Closed trade {trade_ids[1]} with loss")
            else:
                print(f"❌ Trade {trade_ids[1]} no longer active")
        except Exception as e:
            print(f"❌ Error closing losing trade: {e}")

def test_performance_summary():
    """Test performance summary functionality"""
    print("\n📊 Testing performance summary...")
    
    summary = paper_trader.get_performance_summary()
    
    print(f"💰 Current Balance: ${summary['current_balance']:,.2f}")
    print(f"📈 Total P&L: {summary['total_pnl']:+,.2f} ({summary['total_return_percent']:+.1f}%)")
    print(f"📅 Today's P&L: {summary['today_pnl']:+,.2f}")
    print(f"🎯 Win Rate: {summary['win_rate']:.1f}% ({summary['winning_trades']}W/{summary['losing_trades']}L)")
    print(f"🟢 Active Positions: {summary['active_positions']}")
    print(f"📋 Total Trades: {summary['total_trades']}")
    
    if summary['total_trades'] > 0:
        print(f"💵 Average Win: ${summary['avg_win']:.2f}")
        print(f"💸 Average Loss: ${summary['avg_loss']:.2f}")
        print(f"🔢 Profit Factor: {summary['profit_factor']:.2f}")

def test_csv_export():
    """Test CSV export functionality"""
    print("\n📄 Testing CSV export...")
    
    try:
        filename = paper_trader.export_to_csv()
        print(f"✅ Trades exported to: {filename}")
    except Exception as e:
        print(f"❌ CSV export failed: {e}")

def main():
    """Main test function"""
    print("🧪 Enhanced Day Trader - Test Suite")
    print("=" * 50)
    
    # Reset paper trader for clean test
    paper_trader.reset_account()
    
    # Test 1: Create sample trades
    trade_ids = create_sample_trades()
    
    # Test 2: Show initial performance
    test_performance_summary()
    
    # Test 3: Simulate some outcomes
    simulate_trade_outcomes(trade_ids)
    
    # Test 4: Show updated performance
    print("\n📊 Performance after trade outcomes:")
    test_performance_summary()
    
    # Test 5: Test CSV export
    test_csv_export()
    
    # Test 6: Save state
    print("\n💾 Saving paper trading state...")
    paper_trader.save_trades()
    print("✅ State saved successfully")
    
    # Test 7: Start colorful display
    print("\n🎨 Starting colorful trade display...")
    print("   (Close the window to continue)")
    
    try:
        display = create_trade_display()
        display.show()
    except Exception as e:
        print(f"❌ Display test failed: {e}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
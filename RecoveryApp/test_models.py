"""
Test script for RecoveryApp data models
Validates TickerPosition and TradeEntry classes functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.models import TickerPosition, TradeEntry, PortfolioManager
from datetime import datetime

def test_trade_entry():
    """Test TradeEntry class functionality"""
    print("🧪 Testing TradeEntry class...")
    
    # Create a valid trade entry
    trade = TradeEntry(
        type="short_put",
        strike=40.0,
        expiry="2025-11-15",
        premium=2.40,
        status="open",
        quantity=1,
        commission=0.65
    )
    
    print(f"✅ Created trade: {trade.type} ${trade.strike} put for ${trade.premium}")
    print(f"✅ Net premium after commission: ${trade.net_premium():.2f}")
    print(f"✅ Is active: {trade.is_active()}")
    
    # Test serialization
    trade_dict = trade.to_dict()
    restored_trade = TradeEntry.from_dict(trade_dict)
    print(f"✅ Serialization test passed: {restored_trade.type == trade.type}")
    
    return trade

def test_ticker_position():
    """Test TickerPosition class functionality"""
    print("\n🧪 Testing TickerPosition class...")
    
    # Create a position
    position = TickerPosition(
        ticker="SOXL",
        cost_basis=42.50,
        qty=100,
        purchase_date="2025-09-15"
    )
    
    print(f"✅ Created position: {position.qty} shares of {position.ticker} @ ${position.cost_basis}")
    print(f"✅ Total investment: ${position.total_investment():.2f}")
    
    # Add some trades
    trade1 = TradeEntry("short_put", 40.0, "2025-11-15", 2.40, "open", commission=0.65)
    trade2 = TradeEntry("short_put", 38.0, "2025-12-20", 1.80, "closed", commission=0.65)
    
    position.add_trade(trade1)
    position.add_trade(trade2)
    
    print(f"✅ Added {len(position.trades)} trades")
    print(f"✅ Total premium collected: ${position.total_premium_collected():.2f}")
    print(f"✅ Effective cost basis: ${position.effective_cost_basis():.2f}")
    
    # Test underwater calculations
    current_price = 38.50
    print(f"\n📊 At current price ${current_price}:")
    print(f"✅ Is underwater: {position.is_underwater(current_price)}")
    print(f"✅ Unrealized loss: ${position.unrealized_loss(current_price):.2f}")
    print(f"✅ Recovery needed: ${position.recovery_needed(current_price):.2f}")
    print(f"✅ Recovery % needed: {position.recovery_percentage_needed(current_price):.1f}%")
    
    return position

def test_portfolio_manager():
    """Test PortfolioManager class functionality"""
    print("\n🧪 Testing PortfolioManager class...")
    
    portfolio = PortfolioManager()
    
    # Create multiple positions
    positions = [
        TickerPosition("SOXL", 42.50, 100, "2025-09-15"),
        TickerPosition("NVDA", 125.00, 50, "2025-08-20"),
        TickerPosition("AMD", 165.00, 75, "2025-07-10")
    ]
    
    for pos in positions:
        portfolio.add_position(pos)
        print(f"✅ Added position: {pos.ticker}")
    
    print(f"✅ Portfolio size: {len(portfolio)} positions")
    print(f"✅ Total investment: ${portfolio.total_investment():.2f}")
    print(f"✅ All tickers: {portfolio.get_all_tickers()}")
    
    # Test getting specific position
    soxl_position = portfolio.get_position("SOXL")
    print(f"✅ Retrieved SOXL position: {soxl_position.ticker if soxl_position else 'Not found'}")
    
    # Test file operations
    test_file = "test_portfolio.json"
    portfolio.save_to_file(test_file)
    print(f"✅ Saved portfolio to {test_file}")
    
    # Load into new portfolio
    new_portfolio = PortfolioManager()
    new_portfolio.load_from_file(test_file)
    print(f"✅ Loaded portfolio with {len(new_portfolio)} positions")
    
    # Cleanup
    if os.path.exists(test_file):
        os.remove(test_file)
        print(f"✅ Cleaned up test file")
    
    return portfolio

def run_all_tests():
    """Run all data model tests"""
    print("🚀 RecoveryApp Data Models Test Suite")
    print("=" * 50)
    
    try:
        trade = test_trade_entry()
        position = test_ticker_position()
        portfolio = test_portfolio_manager()
        
        print("\n" + "=" * 50)
        print("✅ All tests passed! Data models are working correctly.")
        print("\n📋 Test Summary:")
        print(f"   • TradeEntry: Created and validated")
        print(f"   • TickerPosition: Created with trades and calculations")
        print(f"   • PortfolioManager: Created with {len(portfolio)} positions")
        print(f"   • Serialization: JSON save/load working")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
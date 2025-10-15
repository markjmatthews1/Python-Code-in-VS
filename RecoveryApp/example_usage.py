"""
Example usage of RecoveryApp data models
Demonstrates how to create positions, add trades, and track recovery progress
"""
from utils.models import TickerPosition, TradeEntry, PortfolioManager
from datetime import datetime, timedelta

def create_example_portfolio():
    """Create an example portfolio with underwater positions"""
    print("🏗️  Creating Example Recovery Portfolio")
    print("=" * 50)
    
    # Initialize portfolio manager
    portfolio = PortfolioManager()
    
    # Example 1: SOXL position with active recovery trades
    print("\n📈 Example 1: SOXL Recovery Strategy")
    soxl_position = TickerPosition(
        ticker="SOXL",
        cost_basis=42.50,
        qty=100,
        purchase_date="2025-09-15",
        notes="Leveraged semiconductor ETF - high volatility recovery candidate"
    )
    
    # Add recovery trades for SOXL
    soxl_trades = [
        TradeEntry("short_put", 40.0, "2025-11-15", 2.40, "open", commission=0.65),
        TradeEntry("short_put", 38.0, "2025-12-20", 1.80, "open", commission=0.65),
        TradeEntry("covered_call", 45.0, "2025-10-18", 1.20, "expired", commission=0.65)
    ]
    
    for trade in soxl_trades:
        soxl_position.add_trade(trade)
    
    portfolio.add_position(soxl_position)
    
    print(f"   • Position: {soxl_position.qty} shares @ ${soxl_position.cost_basis}")
    print(f"   • Active trades: {len(soxl_position.get_active_trades())}")
    print(f"   • Total premium collected: ${soxl_position.total_premium_collected():.2f}")
    print(f"   • Effective cost basis: ${soxl_position.effective_cost_basis():.2f}")
    
    # Example 2: NVDA position with protective strategies
    print("\n🔧 Example 2: NVDA Protective Recovery")
    nvda_position = TickerPosition(
        ticker="NVDA",
        cost_basis=125.00,
        qty=50,
        purchase_date="2025-08-20",
        target_recovery_price=130.00,
        notes="AI leader - using protective puts and covered calls"
    )
    
    # Add protective trades for NVDA
    nvda_trades = [
        TradeEntry("protective_put", 120.0, "2025-11-15", -3.50, "open", commission=0.65),
        TradeEntry("covered_call", 130.0, "2025-10-18", 2.80, "assigned", commission=0.65),
        TradeEntry("short_put", 115.0, "2025-12-20", 4.20, "open", commission=0.65)
    ]
    
    for trade in nvda_trades:
        nvda_position.add_trade(trade)
    
    portfolio.add_position(nvda_position)
    
    print(f"   • Position: {nvda_position.qty} shares @ ${nvda_position.cost_basis}")
    print(f"   • Target recovery: ${nvda_position.target_recovery_price}")
    print(f"   • Net premium: ${nvda_position.total_premium_collected():.2f}")
    print(f"   • Effective cost basis: ${nvda_position.effective_cost_basis():.2f}")
    
    # Example 3: AMD position with synthetic recovery
    print("\n⚡ Example 3: AMD Synthetic Recovery")
    amd_position = TickerPosition(
        ticker="AMD",
        cost_basis=165.00,
        qty=75,
        purchase_date="2025-07-10",
        notes="Semiconductor - using synthetic strategies for faster recovery"
    )
    
    # Add synthetic recovery trades for AMD
    amd_trades = [
        TradeEntry("synthetic", 160.0, "2025-11-15", 3.80, "open", commission=1.30),
        TradeEntry("short_call", 170.0, "2025-10-18", 2.10, "closed", commission=0.65)
    ]
    
    for trade in amd_trades:
        amd_position.add_trade(trade)
    
    portfolio.add_position(amd_position)
    
    print(f"   • Position: {amd_position.qty} shares @ ${amd_position.cost_basis}")
    print(f"   • Strategy: Synthetic recovery approach")
    print(f"   • Premium impact: ${amd_position.total_premium_collected():.2f}")
    print(f"   • Adjusted basis: ${amd_position.effective_cost_basis():.2f}")
    
    return portfolio

def analyze_portfolio_recovery(portfolio, current_prices):
    """Analyze recovery status for entire portfolio"""
    print("\n\n📊 Portfolio Recovery Analysis")
    print("=" * 50)
    
    total_unrealized_loss = 0
    total_recovery_needed = 0
    
    for position in portfolio:
        current_price = current_prices.get(position.ticker, position.cost_basis * 0.9)  # Default to 10% down
        
        unrealized_loss = position.unrealized_loss(current_price)
        recovery_needed = position.recovery_needed(current_price)
        recovery_pct = position.recovery_percentage_needed(current_price)
        
        total_unrealized_loss += unrealized_loss
        total_recovery_needed += recovery_needed * position.qty
        
        status = "🟢 RECOVERED" if not position.is_underwater(current_price) else "🔴 UNDERWATER"
        
        print(f"\n{position.ticker} {status}")
        print(f"   Current: ${current_price:.2f} | Cost Basis: ${position.cost_basis:.2f}")
        print(f"   Effective Basis: ${position.effective_cost_basis():.2f}")
        print(f"   Unrealized Loss: ${unrealized_loss:.2f}")
        print(f"   Recovery Needed: ${recovery_needed:.2f} ({recovery_pct:.1f}%)")
        print(f"   Active Trades: {len(position.get_active_trades())}")
    
    print(f"\n📈 Portfolio Summary:")
    print(f"   Total Investment: ${portfolio.total_investment():.2f}")
    print(f"   Total Premium Collected: ${portfolio.total_premium_collected():.2f}")
    print(f"   Total Unrealized Loss: ${total_unrealized_loss:.2f}")
    print(f"   Total Recovery Needed: ${total_recovery_needed:.2f}")

def save_and_load_example(portfolio):
    """Demonstrate saving and loading portfolio data"""
    print("\n\n💾 Data Persistence Example")
    print("=" * 50)
    
    filename = "example_recovery_portfolio.json"
    
    # Save portfolio
    portfolio.save_to_file(filename)
    print(f"✅ Portfolio saved to {filename}")
    
    # Load into new portfolio
    new_portfolio = PortfolioManager()
    new_portfolio.load_from_file(filename)
    
    print(f"✅ Portfolio loaded with {len(new_portfolio)} positions")
    print(f"   Tickers: {new_portfolio.get_all_tickers()}")
    
    # Verify data integrity
    original_investment = portfolio.total_investment()
    loaded_investment = new_portfolio.total_investment()
    
    print(f"✅ Data integrity check: ${original_investment:.2f} = ${loaded_investment:.2f}")
    
    import os
    if os.path.exists(filename):
        os.remove(filename)
        print(f"✅ Cleaned up {filename}")

def main():
    """Run the complete example"""
    print("🎯 RecoveryApp Data Models - Complete Example")
    print("This demonstrates how to use the TickerPosition and TradeEntry classes")
    print("to track underwater positions and recovery strategies.\n")
    
    # Create example portfolio
    portfolio = create_example_portfolio()
    
    # Example current prices (simulating market data)
    current_prices = {
        "SOXL": 38.50,  # Down from $42.50 cost basis
        "NVDA": 118.75,  # Down from $125.00 cost basis
        "AMD": 152.30   # Down from $165.00 cost basis
    }
    
    # Analyze recovery status
    analyze_portfolio_recovery(portfolio, current_prices)
    
    # Demonstrate data persistence
    save_and_load_example(portfolio)
    
    print("\n" + "=" * 50)
    print("✅ Example completed successfully!")
    print("The data models are ready for use in the RecoveryApp GUI.")

if __name__ == "__main__":
    main()
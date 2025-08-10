#!/usr/bin/env python3
"""
Quick Portfolio and Dividend Management Script
Easy access to portfolio tracking and 401K updates
Last Updated: July 27, 2025
"""

import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def quick_401k_update():
    """Quick 401K value update"""
    print("=== Quick 401K Update ===")
    
    try:
        from portfolio_history_manager import PortfolioHistoryManager
        
        portfolio = PortfolioHistoryManager()
        current_value = portfolio.get_current_401k_value()
        
        if current_value:
            print(f"Current 401K value: ${current_value:,.2f}")
        else:
            print("No current 401K value found")
        
        new_value_str = input("Enter new 401K value: $")
        new_value = float(new_value_str.replace(',', '').replace('$', ''))
        
        portfolio.update_401k_value(new_value)
        
        # Show updated summary
        summary = portfolio.get_portfolio_summary_for_week()
        if summary:
            print(f"\n📊 Updated Portfolio Summary:")
            total = 0
            for account, value in summary.items():
                if account != 'TOTAL_PORTFOLIO':
                    print(f"  {account}: ${value:,.2f}")
                    total += value
            print(f"  TOTAL: ${total:,.2f}")
            
    except ValueError:
        print("⚠️ Invalid value entered")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_portfolio_summary():
    """Show current portfolio summary"""
    print("=== Portfolio Summary ===")
    
    try:
        from portfolio_history_manager import PortfolioHistoryManager
        
        portfolio = PortfolioHistoryManager()
        summary = portfolio.get_portfolio_summary_for_week()
        
        if summary:
            total = 0
            for account, value in summary.items():
                if account != 'TOTAL_PORTFOLIO':
                    print(f"  {account}: ${value:,.2f}")
                    total += value
            print(f"  TOTAL: ${total:,.2f}")
        else:
            print("No portfolio data found for current week")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def run_full_tracking():
    """Run the full dividend and portfolio tracking"""
    print("=== Full Tracking System ===")
    
    try:
        from enhanced_dividend_tracker import main
        main()
    except Exception as e:
        print(f"❌ Error: {e}")

def main():
    """Main menu"""
    print("=== Portfolio Management ===")
    print("1. Quick 401K Update")
    print("2. Show Portfolio Summary") 
    print("3. Full Dividend & Portfolio Tracking")
    print("4. Exit")
    
    choice = input("Select option (1-4): ").strip()
    
    if choice == "1":
        quick_401k_update()
    elif choice == "2":
        show_portfolio_summary()
    elif choice == "3":
        run_full_tracking()
    elif choice == "4":
        print("Goodbye!")
        return
    else:
        print("Invalid option")
        
    # Ask if user wants to continue
    if input("\nContinue? (y/n): ").lower().startswith('y'):
        main()

if __name__ == "__main__":
    main()

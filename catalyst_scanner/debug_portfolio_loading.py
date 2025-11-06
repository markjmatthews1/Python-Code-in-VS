#!/usr/bin/env python3
"""
Debug Live Dashboard Portfolio Loading
Tests why tickers aren't showing up in the Live Dashboard
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_portfolio_loading():
    """Test portfolio loading for Live Dashboard"""
    
    print("🔍 DEBUGGING LIVE DASHBOARD PORTFOLIO LOADING")
    print("=" * 60)
    
    try:
        # Import the portfolio loader
        from data_collectors.portfolio_loader import PortfolioLoader
        
        print("✅ 1. PortfolioLoader imported successfully")
        
        # Initialize portfolio loader
        portfolio_loader = PortfolioLoader()
        print("✅ 2. PortfolioLoader initialized")
        
        # Get portfolio data
        portfolio_data = portfolio_loader.get_portfolio_data()
        print(f"✅ 3. Portfolio data retrieved: {type(portfolio_data)}")
        print(f"📊 Portfolio data content: {portfolio_data}")
        print(f"📊 Portfolio data length: {len(portfolio_data) if portfolio_data else 0}")
        
        # Try to force load the portfolio
        print("\n🔄 FORCING PORTFOLIO LOAD:")
        portfolio_loader.load_portfolio()
        portfolio_data_after_load = portfolio_loader.get_portfolio_data()
        print(f"📊 After explicit load: {type(portfolio_data_after_load)}")
        print(f"📊 After load length: {len(portfolio_data_after_load) if portfolio_data_after_load else 0}")
        
        if portfolio_data_after_load:
            print(f"📊 Tickers found: {list(portfolio_data_after_load.keys())}")
        
        # Check if there are any stored tickers
        if hasattr(portfolio_loader, 'tickers'):
            print(f"📊 Portfolio loader tickers attribute: {portfolio_loader.tickers}")
        
        if portfolio_data_after_load:
            print(f"📊 Portfolio data type: {type(portfolio_data)}")
            print(f"📊 Has 'items' attribute: {hasattr(portfolio_data, 'items')}")
            
            if hasattr(portfolio_data, 'items'):
                ticker_count = len(portfolio_data)
                print(f"📊 Number of tickers: {ticker_count}")
                print(f"📊 Tickers: {list(portfolio_data.keys())}")
                
                # Test the exact code used in Live Dashboard
                print("\n🧪 TESTING LIVE DASHBOARD LOGIC:")
                print("-" * 40)
                
                for ticker, data in portfolio_data.items():
                    print(f"   {ticker}: {type(data)} - {str(data)[:100]}...")
                    break  # Just show first one
                    
            else:
                print("❌ Portfolio data doesn't have 'items' method")
                print(f"   Actual type: {type(portfolio_data)}")
                print(f"   Actual value: {portfolio_data}")
        else:
            print("❌ No portfolio data returned")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_portfolio_loading()
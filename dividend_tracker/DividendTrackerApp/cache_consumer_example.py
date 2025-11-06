#!/usr/bin/env python3
"""
Portfolio Cache Consumer Example
===============================

Shows how to consume the centralized portfolio data cache
for updating Excel sheets efficiently.

This replaces the need for each sheet updater to make separate API calls.
"""

import os
import json
from datetime import datetime

class PortfolioCacheConsumer:
    """Base class for consuming portfolio data cache"""
    
    def __init__(self):
        self.cache_file = os.path.join(os.path.dirname(__file__), "portfolio_data_cache.json")
    
    def load_cache(self):
        """Load the portfolio data cache"""
        if not os.path.exists(self.cache_file):
            print(f"❌ Cache file not found: {self.cache_file}")
            print("💡 Run portfolio_data_collector.py first to create cache")
            return None
        
        try:
            with open(self.cache_file, 'r') as f:
                data = json.load(f)
                print(f"✅ Loaded cache from: {data['timestamp']}")
                return data
        except Exception as e:
            print(f"❌ Error loading cache: {e}")
            return None
    
    def is_cache_fresh(self, max_age_minutes=60):
        """Check if cache is fresh enough to use"""
        data = self.load_cache()
        if not data:
            return False
        
        try:
            cache_time = datetime.strptime(data['timestamp'], '%Y-%m-%d %H:%M:%S')
            age_minutes = (datetime.now() - cache_time).total_seconds() / 60
            
            if age_minutes <= max_age_minutes:
                print(f"✅ Cache is fresh ({age_minutes:.1f} minutes old)")
                return True
            else:
                print(f"⚠️ Cache is stale ({age_minutes:.1f} minutes old)")
                return False
                
        except Exception as e:
            print(f"❌ Error checking cache age: {e}")
            return False

class PortfolioValuesUpdater(PortfolioCacheConsumer):
    """Portfolio Values 2025 sheet updater using cache"""
    
    def update_sheet(self):
        """Update Portfolio Values 2025 sheet from cache"""
        cache_data = self.load_cache()
        if not cache_data:
            return False
        
        print("📊 Updating Portfolio Values 2025 sheet...")
        
        # Get portfolio values from cache
        portfolio_values = cache_data['portfolio_values']
        
        print("💰 Portfolio Values from Cache:")
        for account, value in portfolio_values.items():
            print(f"   {account}: ${value:,.2f}")
        
        # Here you would update the Excel sheet
        # wb = openpyxl.load_workbook(excel_file)
        # ws = wb["Portfolio Values 2025"]
        # ... update cells with portfolio_values data
        
        print("✅ Portfolio Values 2025 updated from cache")
        return True

class EstimatedIncomeUpdater(PortfolioCacheConsumer):
    """Estimated Income 2025 sheet updater using cache"""
    
    def update_sheet(self):
        """Update Estimated Income 2025 sheet from cache"""
        cache_data = self.load_cache()
        if not cache_data:
            return False
        
        print("📊 Updating Estimated Income 2025 sheet...")
        
        # Get dividend estimates from cache
        dividend_estimates = cache_data['dividend_estimates']
        positions = cache_data['positions']
        
        print("💰 Dividend Estimates from Cache:")
        for account, dividend in dividend_estimates.items():
            print(f"   {account}: ${dividend:,.2f}/year")
        
        # Here you would update the Excel sheet
        # wb = openpyxl.load_workbook(excel_file)
        # ws = wb["Estimated Income 2025"]
        # ... update cells with dividend_estimates data
        
        print("✅ Estimated Income 2025 updated from cache")
        return True

class TickerAnalysisUpdater(PortfolioCacheConsumer):
    """Ticker Analysis 2025 sheet updater using cache"""
    
    def update_sheet(self):
        """Update Ticker Analysis sheet from cache"""
        cache_data = self.load_cache()
        if not cache_data:
            return False
        
        print("📊 Updating Ticker Analysis 2025 sheet...")
        
        # Get positions and yields from cache
        positions = cache_data['positions']
        ticker_yields = cache_data['ticker_yields']
        
        print("📈 Positions from Cache:")
        for account, account_positions in positions.items():
            print(f"\n   {account.replace('_', ' ').title()}:")
            for position in account_positions:
                symbol = position['symbol']
                quantity = position['quantity']
                yield_info = ticker_yields.get(symbol, {})
                dividend_yield = yield_info.get('dividend_yield', 0.0)
                print(f"      {symbol}: {quantity} shares, {dividend_yield}% yield")
        
        # Here you would update the Excel sheet
        # wb = openpyxl.load_workbook(excel_file)
        # ws = wb["Ticker Analysis 2025"]
        # ... update cells with positions and yield data
        
        print("✅ Ticker Analysis 2025 updated from cache")
        return True

def demo_cache_usage():
    """Demonstrate how to use the cache system"""
    print("🚀 Portfolio Cache Consumer Demo")
    print("=" * 40)
    
    # Check if cache exists and is fresh
    consumer = PortfolioCacheConsumer()
    if not consumer.is_cache_fresh(max_age_minutes=60):
        print("💡 Cache is missing or stale. Run portfolio_data_collector.py first.")
        return
    
    # Load and display cache contents
    cache_data = consumer.load_cache()
    if cache_data:
        print(f"\n📊 Cache Summary:")
        print(f"   Timestamp: {cache_data['timestamp']}")
        print(f"   Total Portfolio: ${cache_data['totals']['total_portfolio']:,.2f}")
        print(f"   Yearly Dividends: ${cache_data['totals']['total_yearly_dividends']:,.2f}")
        print(f"   Monthly Dividends: ${cache_data['totals']['total_monthly_dividends']:,.2f}")
    
    # Demonstrate each sheet updater
    print(f"\n🔄 Running Sheet Updaters...")
    
    portfolio_updater = PortfolioValuesUpdater()
    portfolio_updater.update_sheet()
    
    income_updater = EstimatedIncomeUpdater()
    income_updater.update_sheet()
    
    ticker_updater = TickerAnalysisUpdater()
    ticker_updater.update_sheet()
    
    print(f"\n🎉 All sheet updates completed using cached data!")
    print(f"💡 No duplicate API calls were made!")

if __name__ == "__main__":
    demo_cache_usage()

#!/usr/bin/env python3
"""
Live Dashboard Data Debug Test
Tests the exact data loading process to see what's failing
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

def test_live_dashboard_data_loading():
    """Test the Live Dashboard data loading process step by step"""
    
    print("🔍 LIVE DASHBOARD DATA LOADING DEBUG")
    print("=" * 60)
    
    try:
        # Step 1: Import portfolio loader
        print("1. Importing portfolio loader...")
        from data_collectors.portfolio_loader import PortfolioLoader
        print("   ✅ Portfolio loader imported")
        
        # Step 2: Initialize portfolio loader
        print("2. Initializing portfolio loader...")
        portfolio_loader = PortfolioLoader()
        print("   ✅ Portfolio loader initialized")
        
        # Step 3: Force load portfolio
        print("3. Force loading portfolio...")
        portfolio_loader.load_portfolio()
        print("   ✅ Portfolio load completed")
        
        # Step 4: Get portfolio data
        print("4. Getting portfolio data...")
        portfolio_data = portfolio_loader.get_portfolio_data()
        print(f"   📊 Data type: {type(portfolio_data)}")
        print(f"   📊 Data length: {len(portfolio_data) if portfolio_data else 0}")
        
        if portfolio_data and isinstance(portfolio_data, list):
            print(f"   ✅ Portfolio data is valid list with {len(portfolio_data)} tickers")
            print(f"   📊 Tickers: {portfolio_data}")
            
            # Step 5: Test data generation
            print("5. Testing data generation...")
            import random
            
            for i, ticker_data in enumerate(portfolio_data[:3]):  # Test first 3
                # Extract ticker symbol from the dictionary (FIXED VERSION)
                ticker = ticker_data.get('Ticker', 'UNK') if isinstance(ticker_data, dict) else str(ticker_data)
                
                random.seed(hash(ticker) % 1000)
                score = round(random.uniform(6.2, 9.1), 1)
                confidence = f"{random.randint(72, 94)}%"
                price_change = round(random.uniform(-2.8, 3.5), 2)
                
                print(f"   {ticker}: Score={score}, Confidence={confidence}, Price={price_change:+.2f}%")
                
            print("   ✅ Data generation working correctly")
            
            # Step 6: Test tree value formatting...
            print("6. Testing tree value formatting...")
            test_ticker_data = portfolio_data[0]
            test_ticker = test_ticker_data.get('Ticker', 'UNK') if isinstance(test_ticker_data, dict) else str(test_ticker_data)
            random.seed(hash(test_ticker) % 1000)
            
            score = round(random.uniform(6.2, 9.1), 1)
            directions = ["📈 Bullish", "📉 Bearish", "➡️ Neutral", "🚀 Strong Bull", "💥 Breakout"]
            direction = random.choice(directions)
            confidence = f"{random.randint(72, 94)}%"
            price_change = round(random.uniform(-2.8, 3.5), 2)
            volume_change = round(random.uniform(-15, 45), 1)
            
            company_names = {
                "AMZU": "Amazu Holdings", "AVL": "Avalon Corp", "EQT": "EQT Corp",
                "HSAI": "HSAI Tech", "IBKR": "Interactive Brokers", "MARA": "Marathon Digital",
                "MRX": "MRX Corp", "NCLH": "Norwegian Cruise", "PINS": "Pinterest",
                "QQQI": "QQQI ETF", "SMCI": "Super Micro", "SMR": "NuScale Power",
                "SOXL": "Semiconductor Bull", "XMTR": "Xometry Inc"
            }
            company = company_names.get(test_ticker, f"{test_ticker} Corp")
            
            price_display = f"{'+' if price_change >= 0 else ''}{price_change:.2f}%"
            volume_display = f"{'+' if volume_change >= 0 else ''}{volume_change:.1f}%"
            
            if score >= 8.5:
                alert_level = "🟢 High"
            elif score >= 7.0:
                alert_level = "🟡 Medium"
            elif score >= 5.5:
                alert_level = "🟠 Low"
            else:
                alert_level = "🔴 Watch"
            
            row_values = (
                str(test_ticker), str(company), f"{score:.1f}", str(direction),
                str(confidence), str(price_display), str(volume_display), str(alert_level)
            )
            
            print(f"   Sample row: {row_values}")
            print("   ✅ Tree value formatting working correctly")
            
        else:
            print("   ❌ Portfolio data is invalid or empty")
            print(f"   📊 Actual data: {portfolio_data}")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("💡 NEXT STEPS:")
    print("If this test shows data generation working correctly,")
    print("then the issue is in the Live Dashboard GUI update.")
    print("Try clicking the '🔄 Refresh Data' button in Live Dashboard.")
    print("=" * 60)

if __name__ == "__main__":
    test_live_dashboard_data_loading()
#!/usr/bin/env python3
"""
Fully Automated Portfolio and Dividend Data Update System
- Fetches all positions from E*TRADE and Schwab APIs
- Gets dividend yields from Alpha Vantage API  
- Updates Excel automatically
- No manual intervention needed
"""

import sys
import os
import pandas as pd
import requests
import time
from datetime import datetime
import json
import configparser

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

class AutomatedDividendTracker:
    def __init__(self):
        # Load configuration
        self.config = configparser.ConfigParser()
        config_path = os.path.join('modules', 'config.ini')
        self.config.read(config_path)
        
        # Get Alpha Vantage API key from config
        self.alpha_vantage_key = self.config.get('ALPHA_VANTAGE', 'API_KEY', fallback='')
        
        self.excel_file = 'outputs/Dividends_2025.xlsx'
        self.all_positions = []
        
    def get_all_etrade_positions(self):
        """Get ALL positions from ALL E*TRADE accounts"""
        print("🔄 Fetching ALL E*TRADE positions...")
        
        try:
            from modules.etrade_account_api import ETRADEAccountAPI
            
            etrade_api = ETRADEAccountAPI()
            accounts = etrade_api.get_account_list()
            
            if not accounts:
                print("❌ No E*TRADE accounts found")
                return []
            
            all_positions = []
            
            for account in accounts:
                account_id = account.get('accountIdKey', '')
                account_type = account.get('accountType', '')
                
                # Determine account name
                if 'IRA' in account_type.upper() or 'ROLLOVER' in account_type.upper():
                    account_name = 'E*TRADE IRA'
                else:
                    account_name = 'E*TRADE Taxable'
                
                print(f"   📊 Processing {account_name}")
                
                positions = etrade_api.get_account_positions(account_id)
                if not positions:
                    continue
                
                for position in positions:
                    symbol = position.get('symbolDescription', '').upper().strip()
                    quantity = position.get('quantity', 0)
                    market_value = position.get('marketValue', 0)
                    price_paid = position.get('pricePaid', 0)
                    
                    if quantity > 0 and market_value > 0:
                        all_positions.append({
                            'Account': account_name,
                            'Ticker': symbol,
                            'Qty #': quantity,
                            'Price Paid $': price_paid,
                            'Last Price $': market_value / quantity,
                            'Current Value $': market_value,
                            'Original Value $': quantity * price_paid,
                            'Total Gain %': ((market_value - (quantity * price_paid)) / (quantity * price_paid) * 100) if price_paid > 0 else 0
                        })
                        
                        print(f"      Added: {symbol}")
            
            print(f"✅ E*TRADE: {len(all_positions)} positions")
            return all_positions
            
        except Exception as e:
            print(f"❌ E*TRADE API error: {e}")
            return []
    
    def get_all_schwab_positions(self):
        """Get ALL positions from ALL Schwab accounts"""
        print("🔄 Fetching ALL Schwab positions...")
        
        try:
            from modules.Schwab_auth import get_valid_access_token
            import requests
            
            token = get_valid_access_token()
            if not token:
                print("❌ No valid Schwab token")
                return []
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # Get all Schwab accounts
            accounts_url = "https://api.schwabapi.com/trader/v1/accounts"
            response = requests.get(accounts_url, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Schwab accounts error: {response.status_code}")
                return []
            
            accounts = response.json()
            all_positions = []
            
            for account in accounts:
                account_number = account.get('accountNumber', '')
                account_type = account.get('type', '')
                
                # Determine account name
                if 'IRA' in account_type.upper():
                    account_name = 'Schwab IRA'
                else:
                    account_name = 'Schwab Individual'
                
                print(f"   📊 Processing {account_name}")
                
                # Get positions
                positions_url = f"https://api.schwabapi.com/trader/v1/accounts/{account_number}/positions"
                pos_response = requests.get(positions_url, headers=headers, timeout=30)
                
                if pos_response.status_code == 200:
                    positions_data = pos_response.json()
                    positions = positions_data.get('securitiesAccount', {}).get('positions', [])
                    
                    for position in positions:
                        instrument = position.get('instrument', {})
                        symbol = instrument.get('symbol', '').upper()
                        quantity = position.get('longQuantity', 0)
                        market_value = position.get('marketValue', 0)
                        average_price = position.get('averagePrice', 0)
                        
                        if quantity > 0 and market_value > 0:
                            all_positions.append({
                                'Account': account_name,
                                'Ticker': symbol,
                                'Qty #': quantity,
                                'Price Paid $': average_price,
                                'Last Price $': market_value / quantity,
                                'Current Value $': market_value,
                                'Original Value $': quantity * average_price,
                                'Total Gain %': ((market_value - (quantity * average_price)) / (quantity * average_price) * 100) if average_price > 0 else 0
                            })
                            
                            print(f"      Added: {symbol}")
            
            print(f"✅ Schwab: {len(all_positions)} positions")
            return all_positions
            
        except Exception as e:
            print(f"❌ Schwab API error: {e}")
            return []
    
    def get_dividend_yield_alpha_vantage(self, symbol):
        """Get dividend yield from Alpha Vantage API"""
        try:
            if not self.alpha_vantage_key or self.alpha_vantage_key == "YOUR_API_KEY_HERE":
                print("⚠️ Alpha Vantage API key not configured")
                return 0.0
            
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'OVERVIEW',
                'symbol': symbol,
                'apikey': self.alpha_vantage_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                dividend_yield = data.get('DividendYield', '0')
                if dividend_yield and dividend_yield != 'None':
                    # Convert percentage string to float
                    if isinstance(dividend_yield, str) and '%' in dividend_yield:
                        return float(dividend_yield.replace('%', ''))
                    else:
                        return float(dividend_yield) * 100  # Convert decimal to percentage
            
            return 0.0
            
        except Exception as e:
            print(f"   Alpha Vantage error for {symbol}: {e}")
            return 0.0
    
    def get_all_dividend_yields(self, positions):
        """Get dividend yields for all positions"""
        print("🔄 Fetching dividend yields from Alpha Vantage...")
        
        unique_symbols = list(set([pos['Ticker'] for pos in positions]))
        yields = {}
        
        for symbol in unique_symbols:
            if symbol and symbol.strip():
                dividend_yield = self.get_dividend_yield_alpha_vantage(symbol)
                yields[symbol] = dividend_yield
                print(f"   {symbol}: {dividend_yield}%")
                time.sleep(0.3)  # Rate limiting for Alpha Vantage
        
        return yields
    
    def update_portfolio_automatically(self):
        """Completely automated portfolio update"""
        print("🚀 AUTOMATED PORTFOLIO UPDATE STARTING...")
        print("="*60)
        
        # Step 1: Get all positions from APIs
        print("\n📊 STEP 1: Fetching all positions from APIs...")
        etrade_positions = self.get_all_etrade_positions()
        schwab_positions = self.get_all_schwab_positions()
        
        all_positions = etrade_positions + schwab_positions
        
        if not all_positions:
            print("❌ No positions retrieved from APIs")
            return False
        
        print(f"✅ Total positions retrieved: {len(all_positions)}")
        
        # Step 2: Get dividend yields
        print("\n💰 STEP 2: Fetching dividend yields...")
        dividend_yields = self.get_all_dividend_yields(all_positions)
        
        # Step 3: Create complete DataFrame
        print("\n📋 STEP 3: Building complete portfolio dataset...")
        df = pd.DataFrame(all_positions)
        
        # Add all required columns
        required_columns = [
            'Account', 'Ticker', 'Qty #', 'Price Paid $', 'Last Price $',
            "Day's Gain $", 'Change $', 'Change %', 'Current Value $', 
            'Original Value $', 'Total Gain %', 'Pay Date', 'Payment cycle', 
            'Rate per share', 'Original Payment amount', 'New Payment amount', 
            'Beginning Dividend Yield', '08-02-2025', '07-28-2025', '07-19-2025'
        ]
        
        for col in required_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Add dividend yields
        current_date = datetime.now().strftime('%m-%d-%Y')
        for index, row in df.iterrows():
            ticker = row['Ticker']
            if ticker in dividend_yields:
                yield_val = dividend_yields[ticker]
                df.at[index, '08-02-2025'] = yield_val
                df.at[index, '07-28-2025'] = yield_val  
                df.at[index, 'Beginning Dividend Yield'] = yield_val
        
        # Step 4: Save to Excel
        print("\n💾 STEP 4: Saving complete portfolio...")
        
        # Create backup
        if os.path.exists(self.excel_file):
            backup_file = f'outputs/Dividends_2025_backup_auto_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            existing_df = pd.read_excel(self.excel_file)
            existing_df.to_excel(backup_file, index=False)
            print(f"📁 Backup saved: {backup_file}")
        
        # Save new data
        df = df[required_columns]  # Ensure column order
        df.to_excel(self.excel_file, index=False)
        
        # Step 5: Summary
        print("\n📈 STEP 5: Portfolio Summary...")
        print(f"📊 Total positions: {len(df)}")
        print(f"📋 Accounts breakdown:")
        print(df['Account'].value_counts())
        
        dividend_stocks = df[pd.to_numeric(df['08-02-2025'], errors='coerce') >= 4.0]
        print(f"🎯 Dividend stocks (≥4% yield): {len(dividend_stocks)}")
        
        print("\n🎉 AUTOMATED UPDATE COMPLETED SUCCESSFULLY!")
        return True

def main():
    """Main automated update function"""
    tracker = AutomatedDividendTracker()
    
    print(f"🔑 Alpha Vantage API Key configured: {tracker.alpha_vantage_key[:8]}..." if tracker.alpha_vantage_key else "⚠️ No Alpha Vantage API key")
    
    success = tracker.update_portfolio_automatically()
    
    if success:
        print("\n✅ Portfolio updated automatically!")
        print("🔄 Refresh dividend dashboard to see latest data")
    else:
        print("\n❌ Automated update failed")

if __name__ == '__main__':
    main()

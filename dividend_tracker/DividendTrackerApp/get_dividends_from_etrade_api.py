#!/usr/bin/env python3
"""
Get dividend yield data from E*TRADE API for all positions
"""

import sys
import os
import pandas as pd
from datetime import datetime
import json

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def get_dividend_data_from_etrade():
    """Get dividend yield data from E*TRADE API"""
    
    print("🔄 Getting dividend yield data from E*TRADE API...")
    
    try:
        from etrade_account_api import ETRADEAccountAPI
        
        # Initialize E*TRADE API
        etrade_api = ETRADEAccountAPI()
        
        # Get all accounts
        accounts = etrade_api.get_account_list()
        if not accounts:
            print("❌ Failed to get E*TRADE accounts")
            return {}
        
        all_yields = {}
        
        for account in accounts:
            account_id = account.get('accountIdKey', '')
            account_type = account.get('accountType', '')
            
            print(f"\n📊 Processing account: {account_type}")
            
            # Get positions
            positions = etrade_api.get_account_positions(account_id)
            if not positions:
                continue
            
            print(f"   Found {len(positions)} positions")
            
            # Check what data is available in position response
            for i, position in enumerate(positions[:3]):  # Check first 3 positions
                print(f"\n   Position {i+1} sample data:")
                print(f"   Available fields: {list(position.keys())}")
                
                # Look for product info that might contain dividend data
                if 'Product' in position:
                    product = position['Product']
                    print(f"   Product fields: {list(product.keys())}")
                
                if 'Quick' in position:
                    quick = position['Quick']
                    print(f"   Quick fields: {list(quick.keys())}")
                
                # Get symbol for dividend lookup
                symbol = ""
                if 'Product' in position and 'symbol' in position['Product']:
                    symbol = position['Product']['symbol']
                elif 'symbolDescription' in position:
                    symbol = position['symbolDescription']
                
                if symbol:
                    print(f"   Symbol: {symbol}")
                    
                    # Try to get dividend data using E*TRADE market data API
                    dividend_yield = get_dividend_yield_from_etrade_market_api(etrade_api, symbol)
                    if dividend_yield:
                        all_yields[symbol] = dividend_yield
                        print(f"   Dividend Yield: {dividend_yield}%")
                
                if i == 0:  # Show detailed structure for first position
                    print(f"   Full position data: {json.dumps(position, indent=2)[:500]}...")
        
        return all_yields
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return {}

def get_dividend_yield_from_etrade_market_api(api, symbol):
    """Try to get dividend yield from E*TRADE market data API"""
    try:
        # E*TRADE has a quotes API that might include dividend data
        url = f"{api.base_url}/v1/market/productlookup.json"
        params = {
            'company': symbol,
            'type': 'eq'  # equity
        }
        
        response = api.session.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            # Parse response for dividend yield if available
            # This would need to be customized based on actual API response structure
            print(f"   Market data response keys: {list(data.keys()) if data else 'No data'}")
            
        return None  # For now, return None until we see the actual API structure
        
    except Exception as e:
        print(f"   Error getting market data for {symbol}: {e}")
        return None

def update_yields_from_etrade_api():
    """Update Excel with dividend yields from E*TRADE API"""
    
    print("🚀 Updating dividend yields from E*TRADE API...")
    print("="*60)
    
    # Get dividend data from API
    dividend_yields = get_dividend_data_from_etrade()
    
    if not dividend_yields:
        print("⚠️ No dividend yield data retrieved from API")
        return False
    
    try:
        # Read current portfolio data
        excel_file = 'outputs/Dividends_2025.xlsx'
        df = pd.read_excel(excel_file)
        
        # Create backup
        backup_file = f'outputs/Dividends_2025_backup_api_yields_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        df.to_excel(backup_file, index=False)
        print(f"📁 Backup saved: {backup_file}")
        
        # Update yields from API data
        updated_count = 0
        for index, row in df.iterrows():
            ticker = str(row['Ticker']).upper().strip()
            
            if ticker in dividend_yields:
                yield_val = dividend_yields[ticker]
                df.at[index, '08-02-2025'] = yield_val
                df.at[index, '07-28-2025'] = yield_val
                df.at[index, 'Beginning Dividend Yield'] = yield_val
                print(f"   ✅ Updated {ticker}: {yield_val}%")
                updated_count += 1
        
        # Save updated data
        df.to_excel(excel_file, index=False)
        print(f"\n✅ Updated {updated_count} positions with API dividend data")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating Excel: {e}")
        return False

if __name__ == '__main__':
    success = update_yields_from_etrade_api()
    if success:
        print("\n🎉 Successfully updated dividend yields from E*TRADE API!")
    else:
        print("\n❌ Failed to get dividend yields from API")

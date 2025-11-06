#!/usr/bin/env python3
"""
Debug E*TRADE Portfolio API Response
===================================
Test if the portfolio endpoint gives us total account values
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.etrade_account_api import ETRADEAccountAPI
import json

def debug_portfolio_api():
    print("🔍 DEBUGGING E*TRADE PORTFOLIO API")
    print("=" * 40)
    
    try:
        # Initialize API
        api = ETRADEAccountAPI()
        
        # Get accounts
        print("📋 Getting account list...")
        accounts = api.get_account_list()
        
        if not accounts:
            print("❌ No accounts found!")
            return
        
        print(f"✅ Found {len(accounts)} accounts")
        
        for account in accounts:
            account_id_key = account.get('accountIdKey')
            account_name = account.get('accountName', 'Unknown')
            account_type = account.get('accountType', 'Unknown')
            
            print(f"\n🏦 Account: {account_name} ({account_type})")
            print(f"   ID: {account_id_key}")
            
            # Get positions for this account
            print(f"   🔍 Getting portfolio...")
            positions = api.get_account_positions(account_id_key)
            
            if positions:
                print(f"   ✅ Found {len(positions)} positions")
                
                # Calculate total value from positions
                total_value = 0
                for position in positions:
                    # Check different possible value fields
                    market_value = 0
                    position_value = position.get('marketValue', 0)
                    if position_value:
                        market_value = float(position_value)
                        total_value += market_value
                    
                    symbol = position.get('Product', {}).get('symbol', 'Unknown')
                    quantity = position.get('Qty', 0)
                    print(f"      {symbol}: {quantity} shares @ ${market_value:,.2f}")
                
                print(f"   💰 CALCULATED TOTAL VALUE: ${total_value:,.2f}")
                
            else:
                print(f"   ❌ No positions found")
                
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_portfolio_api()
    input("\nPress Enter to close...")

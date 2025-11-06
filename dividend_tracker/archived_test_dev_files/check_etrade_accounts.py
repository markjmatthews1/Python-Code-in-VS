#!/usr/bin/env python3
"""
Check E*TRADE accounts and their positions
"""

import sys
import os

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def check_etrade_accounts():
    """Check all E*TRADE accounts and their positions"""
    
    print("🔍 Checking all E*TRADE accounts...")
    
    try:
        from etrade_account_api import ETRADEAccountAPI
        
        # Initialize E*TRADE API
        etrade_api = ETRADEAccountAPI()
        
        # Get all accounts
        accounts = etrade_api.get_account_list()
        if not accounts:
            print("❌ Failed to get E*TRADE accounts")
            return
        
        print(f"📊 Found {len(accounts)} E*TRADE accounts:")
        
        for i, account in enumerate(accounts, 1):
            account_id = account.get('accountIdKey', '')
            account_type = account.get('accountType', '')
            account_desc = account.get('accountDesc', '')
            
            print(f"\n{i}. Account ID: {account_id}")
            print(f"   Type: {account_type}")
            print(f"   Description: {account_desc}")
            
            # Try to get positions for each account
            try:
                positions = etrade_api.get_account_positions(account_id)
                if positions:
                    print(f"   📊 Positions: {len(positions)}")
                    for pos in positions[:3]:  # Show first 3 positions
                        symbol = pos.get('symbolDescription', 'Unknown')
                        quantity = pos.get('quantity', 0)
                        value = pos.get('marketValue', 0)
                        print(f"      {symbol}: {quantity} shares, ${value:.2f}")
                    if len(positions) > 3:
                        print(f"      ... and {len(positions)-3} more positions")
                else:
                    print(f"   📊 No positions found")
            except Exception as e:
                print(f"   ❌ Error getting positions: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    check_etrade_accounts()

#!/usr/bin/env python3
"""
Debug E*TRADE Balance API Response
=================================
Test what the balance API actually returns
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.etrade_account_api import ETRADEAccountAPI
import json

def debug_balance_api():
    print("🔍 DEBUGGING E*TRADE BALANCE API")
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
            
            # Get balance for this account
            print(f"   🔍 Getting balance...")
            balance_response = api.get_account_balance(account_id_key)
            
            if balance_response:
                print(f"   ✅ Balance Response Keys: {list(balance_response.keys())}")
                print(f"   📊 Full Response:")
                print(json.dumps(balance_response, indent=4, default=str))
                
                # Look for common balance fields
                possible_fields = [
                    'netAccountValue', 'accountValue', 'totalAccountValue', 
                    'totalValue', 'cashBalance', 'accountBalance'
                ]
                
                print(f"   🎯 Checking for balance fields:")
                for field in possible_fields:
                    if field in balance_response:
                        value = balance_response[field]
                        print(f"      ✅ {field}: {value}")
                    else:
                        print(f"      ❌ {field}: Not found")
            else:
                print(f"   ❌ No balance response received")
                
    except Exception as e:
        print(f"❌ Debug failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_balance_api()
    input("\nPress Enter to close...")

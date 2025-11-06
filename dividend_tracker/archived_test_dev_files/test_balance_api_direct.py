#!/usr/bin/env python3
"""
Test Correct E*TRADE Balance API
===============================
Test the balance API with the correct path that should work
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.etrade_auth import get_etrade_session
import requests

def test_balance_api_directly():
    print("🔍 TESTING E*TRADE BALANCE API DIRECTLY")
    print("=" * 45)
    
    try:
        # Get session
        print("🔑 Getting E*TRADE session...")
        session, base_url = get_etrade_session()
        
        # Get accounts first
        print("📋 Getting account list...")
        accounts_response = session.get(f"{base_url}/v1/accounts/list.json")
        if accounts_response.status_code != 200:
            print(f"❌ Account list failed: {accounts_response.status_code}")
            return
            
        accounts_data = accounts_response.json()
        accounts = accounts_data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
        
        print(f"✅ Found {len(accounts)} accounts")
        
        for account in accounts:
            account_id_key = account.get('accountIdKey')
            account_name = account.get('accountName', 'Unknown')
            account_type = account.get('accountType', 'Unknown')
            
            print(f"\n🏦 Testing: {account_name} ({account_type})")
            print(f"   ID: {account_id_key}")
            
            # Test balance API
            balance_url = f"{base_url}/v1/accounts/{account_id_key}/balance.json"
            print(f"   🔍 Calling: {balance_url}")
            
            balance_response = session.get(balance_url)
            print(f"   📊 Status Code: {balance_response.status_code}")
            
            if balance_response.status_code == 200:
                balance_data = balance_response.json()
                print(f"   ✅ Response Keys: {list(balance_data.keys())}")
                
                balance_response_data = balance_data.get('BalanceResponse', {})
                print(f"   📊 BalanceResponse Keys: {list(balance_response_data.keys())}")
                
                if 'Computed' in balance_response_data:
                    computed = balance_response_data['Computed']
                    print(f"   🧮 Computed Keys: {list(computed.keys())}")
                    
                    if 'RealTimeValues' in computed:
                        real_time = computed['RealTimeValues']
                        print(f"   ⏰ RealTimeValues Keys: {list(real_time.keys())}")
                        
                        total_value = real_time.get('totalAccountValue', 0)
                        print(f"   💰 TOTAL ACCOUNT VALUE: ${total_value:,.2f}")
                    else:
                        print(f"   ⚠️ No RealTimeValues found")
                else:
                    print(f"   ⚠️ No Computed section found")
                    
            else:
                print(f"   ❌ Balance API Error: {balance_response.status_code}")
                print(f"   📄 Response: {balance_response.text[:200]}...")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_balance_api_directly()
    input("\nPress Enter to close...")

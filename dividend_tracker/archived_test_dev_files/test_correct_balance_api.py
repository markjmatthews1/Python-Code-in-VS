#!/usr/bin/env python3
"""
Test Correct E*TRADE Balance API with Parameters
===============================================
Test the balance API with the correct parameters from Aristo
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.etrade_auth import get_etrade_session
import requests

def test_correct_balance_api():
    print("🔍 TESTING CORRECT E*TRADE BALANCE API")
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
            
            # Test balance API with CORRECT parameters from Aristo
            balance_url = f"{base_url}/v1/accounts/{account_id_key}/balance"
            params = {
                'instType': 'BROKERAGE',
                'realTimeNAV': 'true'
            }
            
            print(f"   🔍 Calling: {balance_url}")
            print(f"   📊 Parameters: {params}")
            
            balance_response = session.get(balance_url, params=params)
            print(f"   📊 Status Code: {balance_response.status_code}")
            
            if balance_response.status_code == 200:
                print(f"   ✅ SUCCESS! Response received")
                print(f"   📄 Raw Response: {balance_response.text[:500]}...")
                
                try:
                    balance_data = balance_response.json()
                    print(f"   ✅ JSON Response Keys: {list(balance_data.keys())}")
                    
                    balance_response_data = balance_data.get('BalanceResponse', {})
                    print(f"   📊 BalanceResponse Keys: {list(balance_response_data.keys())}")
                    
                    if 'Computed' in balance_response_data:
                        computed = balance_response_data['Computed']
                        print(f"   🧮 Computed Keys: {list(computed.keys())}")
                        
                        if 'RealTimeValues' in computed:
                            real_time = computed['RealTimeValues']
                            print(f"   ⏰ RealTimeValues Keys: {list(real_time.keys())}")
                            
                            total_value = real_time.get('totalAccountValue', 0)
                            print(f"   💰 TOTAL ACCOUNT VALUE: ${float(total_value):,.2f}")
                        else:
                            print(f"   ⚠️ No RealTimeValues found")
                    else:
                        print(f"   ⚠️ No Computed section found")
                        
                except Exception as json_error:
                    print(f"   ⚠️ JSON parsing error: {json_error}")
                    print(f"   📄 Response content type: {balance_response.headers.get('content-type', 'unknown')}")
                    print(f"   📄 Response length: {len(balance_response.text)}")
                    
            else:
                print(f"   ❌ Balance API Error: {balance_response.status_code}")
                print(f"   📄 Response: {balance_response.text[:300]}...")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_correct_balance_api()
    input("\nPress Enter to close...")

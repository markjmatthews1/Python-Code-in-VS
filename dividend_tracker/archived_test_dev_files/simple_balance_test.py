#!/usr/bin/env python3
"""
Simple Direct E*TRADE Balance Test
=================================
Direct test to see exactly what's happening with the balance API
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from modules.etrade_auth import get_etrade_session
import requests
import json

def simple_balance_test():
    print("🔍 SIMPLE E*TRADE BALANCE TEST")
    print("=" * 35)
    
    try:
        # Get session
        session, base_url = get_etrade_session()
        print(f"✅ Session obtained: {base_url}")
        
        # Get one account
        accounts_response = session.get(f"{base_url}/v1/accounts/list.json")
        print(f"📋 Account list status: {accounts_response.status_code}")
        
        if accounts_response.status_code != 200:
            print(f"❌ Failed to get accounts")
            return
            
        accounts_data = accounts_response.json()
        accounts = accounts_data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
        
        if not accounts:
            print("❌ No accounts found")
            return
            
        # Test first account only
        account = accounts[0]
        account_id_key = account.get('accountIdKey')
        account_type = account.get('accountType', 'Unknown')
        
        print(f"\n🏦 Testing Account: {account_type}")
        print(f"   ID: {account_id_key}")
        
        # Test balance API with timeout
        balance_url = f"{base_url}/v1/accounts/{account_id_key}/balance"
        params = {
            'instType': 'BROKERAGE',
            'realTimeNAV': 'true'
        }
        
        print(f"   🔍 Calling: {balance_url}")
        print(f"   📊 Params: {params}")
        
        try:
            # Add timeout to prevent hanging
            response = session.get(balance_url, params=params, timeout=10)
            print(f"   📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"   ✅ Success! Response length: {len(response.text)}")
                
                if response.text.strip():
                    try:
                        data = response.json()
                        print(f"   📊 JSON keys: {list(data.keys())}")
                        
                        # Save full response for inspection
                        with open('balance_response.json', 'w') as f:
                            json.dump(data, f, indent=2)
                        print(f"   💾 Full response saved to balance_response.json")
                        
                    except Exception as json_err:
                        print(f"   ❌ JSON error: {json_err}")
                        print(f"   📄 Raw response: {response.text[:200]}...")
                else:
                    print(f"   ⚠️ Empty response")
            else:
                print(f"   ❌ Error: {response.status_code}")
                print(f"   📄 Response: {response.text[:200]}...")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ Request timed out after 10 seconds")
        except Exception as req_err:
            print(f"   ❌ Request error: {req_err}")
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    simple_balance_test()
    print("\n✅ Test complete!")
    input("Press Enter to close...")

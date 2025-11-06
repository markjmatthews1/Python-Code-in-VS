#!/usr/bin/env python3
"""
Correct E*TRADE Balance API Implementation
=========================================
Using the proper OAuth1 approach from the provided snippet
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

import requests
from requests_oauthlib import OAuth1
import json
import configparser

def get_etrade_balance_correct():
    print("🔍 TESTING CORRECT E*TRADE BALANCE API")
    print("=" * 45)
    
    try:
        # Load credentials from config
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), 'modules', 'config.ini')
        config.read(config_path)
        
        consumer_key = config["ETRADE_API"]["CONSUMER_KEY"]
        consumer_secret = config["ETRADE_API"]["CONSUMER_SECRET"]
        
        # Load current tokens
        auth_file_path = "C:/Users/mjmat/Python Code in VS/auth_data.json"
        with open(auth_file_path, "r") as file:
            auth_data = json.load(file)
            
        access_token = auth_data["oauth_token"]
        access_token_secret = auth_data["oauth_token_secret"]
        
        print(f"✅ Loaded credentials and tokens")
        
        # Get account list first to get account IDs
        print("📋 Getting account list...")
        
        # OAuth1 setup for account list
        auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
        accounts_url = 'https://api.etrade.com/v1/accounts/list.json'
        
        accounts_response = requests.get(accounts_url, auth=auth)
        print(f"   Account list status: {accounts_response.status_code}")
        
        if accounts_response.status_code != 200:
            print(f"❌ Failed to get accounts: {accounts_response.text}")
            return
            
        accounts_data = accounts_response.json()
        accounts = accounts_data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
        print(f"✅ Found {len(accounts)} accounts")
        
        # Test balance for each account
        for account in accounts:
            account_id_key = account.get('accountIdKey')
            account_type = account.get('accountType', 'Unknown')
            
            print(f"\n🏦 Testing: {account_type}")
            print(f"   Account ID: {account_id_key}")
            
            # E*TRADE balance endpoint with OAuth1 (from your snippet)
            balance_url = f'https://api.etrade.com/v1/accounts/{account_id_key}/balance?instType=BROKERAGE&realTimeNAV=true'
            
            print(f"   🔍 URL: {balance_url}")
            
            # Make the request with OAuth1
            response = requests.get(balance_url, auth=auth)
            
            print(f"   📊 Status: {response.status_code}")
            
            # Check and print result
            if response.status_code == 200:
                balance_data = response.json()
                print("   ✅ SUCCESS! Account Balance Info:")
                
                # Save response for analysis
                with open(f'balance_response_{account_type}.json', 'w') as f:
                    json.dump(balance_data, f, indent=2)
                print(f"   💾 Response saved to balance_response_{account_type}.json")
                
                # Look for account value in the response
                if 'BalanceResponse' in balance_data:
                    balance_resp = balance_data['BalanceResponse']
                    print(f"   📊 BalanceResponse keys: {list(balance_resp.keys())}")
                    
                    # Check for Computed section
                    if 'Computed' in balance_resp:
                        computed = balance_resp['Computed']
                        print(f"   🧮 Computed keys: {list(computed.keys())}")
                        
                        # Check for RealTimeValues
                        if 'RealTimeValues' in computed:
                            real_time = computed['RealTimeValues']
                            print(f"   ⏰ RealTimeValues keys: {list(real_time.keys())}")
                            
                            if 'totalAccountValue' in real_time:
                                total_value = real_time['totalAccountValue']
                                print(f"   💰 TOTAL ACCOUNT VALUE: ${float(total_value):,.2f}")
                            else:
                                print(f"   ⚠️ No totalAccountValue in RealTimeValues")
                        else:
                            print(f"   ⚠️ No RealTimeValues in Computed")
                    else:
                        print(f"   ⚠️ No Computed in BalanceResponse")
                else:
                    print(f"   ⚠️ No BalanceResponse in data")
                    print(f"   📊 Top level keys: {list(balance_data.keys())}")
                    
            else:
                print(f"   ❌ Error {response.status_code}: {response.text}")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    get_etrade_balance_correct()
    input("\nPress Enter to close...")

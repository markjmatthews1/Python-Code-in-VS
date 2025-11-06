#!/usr/bin/env python3
"""
Fixed E*TRADE Account API with Correct Balance Endpoint
======================================================
"""

import os
import json
from datetime import datetime
from modules.etrade_auth import get_etrade_session

class FixedETRADEAccountAPI:
    """Fixed E*TRADE Account API with correct balance endpoint"""
    
    def __init__(self):
        self.session = None
        self.base_url = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize E*TRADE session"""
        try:
            self.session, self.base_url = get_etrade_session()
            print("✅ E*TRADE API session initialized")
        except Exception as e:
            print(f"❌ Failed to initialize E*TRADE session: {e}")
            raise
    
    def get_account_list(self):
        """Get list of accounts"""
        try:
            url = f"{self.base_url}/v1/accounts/list.json"
            response = self.session.get(url)
            
            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                self.session, self.base_url = get_etrade_session(force_new=True)
                response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Error getting account list: {response.status_code}")
                return None
                
            data = response.json()
            accounts = data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
            print(f"📊 Found {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            print(f"❌ Error getting account list: {e}")
            return None
    
    def get_account_balance(self, account_id_key):
        """Get account balance using CORRECT endpoint with required parameters"""
        try:
            # Use the CORRECT endpoint from Aristo with required parameters
            url = f"{self.base_url}/v1/accounts/{account_id_key}/balance"
            params = {
                'instType': 'BROKERAGE',
                'realTimeNAV': 'true'
            }
            
            print(f"📊 Getting balance for account: {account_id_key}")
            print(f"   URL: {url}")
            print(f"   Params: {params}")
            
            response = self.session.get(url, params=params)
            print(f"   Status: {response.status_code}")
            
            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                self.session, self.base_url = get_etrade_session(force_new=True)
                response = self.session.get(url, params=params)
                print(f"   Retry Status: {response.status_code}")
            
            if response.status_code != 200:
                print(f"❌ Error getting account balance: {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                return 0.0
            
            # Check if response is empty or invalid JSON
            if not response.text.strip():
                print("⚠️ Empty response from balance API")
                return 0.0
            
            try:
                data = response.json()
                print(f"✅ JSON Response received, keys: {list(data.keys())}")
            except Exception as json_err:
                print(f"⚠️ JSON parsing error: {json_err}")
                print(f"   Raw response: {response.text[:300]}...")
                return 0.0
                
            balance_response = data.get('BalanceResponse', {})
            if not balance_response:
                print("⚠️ No BalanceResponse in data")
                return 0.0
            
            # Try to get totalAccountValue from the standard path
            computed = balance_response.get('Computed', {})
            if computed:
                real_time_values = computed.get('RealTimeValues', {})
                if real_time_values:
                    total_account_value = real_time_values.get('totalAccountValue', 0)
                    if total_account_value:
                        account_value = float(total_account_value)
                        print(f"💰 Account Balance: ${account_value:,.2f}")
                        return account_value
            
            # If standard path doesn't work, look for other balance fields
            print("⚠️ Standard path not found, checking all balance fields...")
            print(f"   BalanceResponse keys: {list(balance_response.keys())}")
            
            # Look for any field that might contain account value
            for key, value in balance_response.items():
                if isinstance(value, (int, float)) and value > 1000:  # Reasonable account balance
                    print(f"   Found possible balance in {key}: ${float(value):,.2f}")
                    return float(value)
                elif isinstance(value, dict):
                    for subkey, subvalue in value.items():
                        if isinstance(subvalue, (int, float)) and subvalue > 1000:
                            print(f"   Found possible balance in {key}.{subkey}: ${float(subvalue):,.2f}")
                            return float(subvalue)
            
            print("⚠️ No account balance value found")
            return 0.0
            
        except Exception as e:
            print(f"❌ Error getting account balance: {e}")
            import traceback
            traceback.print_exc()
            return 0.0

# Test the fixed API
if __name__ == "__main__":
    print("🧪 TESTING FIXED E*TRADE BALANCE API")
    print("=" * 40)
    
    try:
        api = FixedETRADEAccountAPI()
        
        accounts = api.get_account_list()
        if not accounts:
            print("❌ No accounts found")
            exit(1)
        
        for account in accounts[:2]:  # Test first 2 accounts
            account_id_key = account.get('accountIdKey')
            account_name = account.get('accountName', 'Unknown')
            account_type = account.get('accountType', 'Unknown')
            
            print(f"\n🏦 Account: {account_name} ({account_type})")
            balance = api.get_account_balance(account_id_key)
            
            if balance > 0:
                print(f"✅ SUCCESS: ${balance:,.2f}")
            else:
                print(f"❌ Failed to get balance")
                
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
    
    input("\nPress Enter to close...")

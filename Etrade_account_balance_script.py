#!/usr/bin/env python3
"""
Enhanced E*TRADE Account Balance Script
=====================================
Gets account balance using shared authentication system with proper 401 error handling.
This script serves as a reference implementation that works with the E*TRADE API.

Features:
- Uses shared authentication from auth_data.json and config.ini
- Automatic 401 error handling with re-authentication
- Support for single account or all accounts
- Proper error handling and timeouts
- Fallback authentication methods
- Detailed balance information display

Usage:
    python Etrade_account_balance_script.py

Dependencies:
    - config.ini with ETRADE_API section (CONSUMER_KEY, CONSUMER_SECRET)
    - auth_data.json with current OAuth tokens
    - modules/etrade_auth.py (optional but recommended)

API Endpoint:
    GET https://api.etrade.com/v1/accounts/{accountIdKey}/balance?instType=BROKERAGE&realTimeNAV=true

Response Path:
    BalanceResponse.Computed.RealTimeValues.totalAccountValue

Created: September 2025
Last Updated: September 2025
Purpose: Reference implementation for working E*TRADE balance API calls
"""

import requests
from requests_oauthlib import OAuth1
import json
import configparser
import sys
import os

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from etrade_auth import EtradeAuth
except ImportError:
    print("Warning: Could not import EtradeAuth module, using fallback method")
    EtradeAuth = None

def load_credentials():
    """Load E*TRADE credentials from config.ini"""
    try:
        config = configparser.ConfigParser()
        config.read('config.ini')
        return (
            config['ETRADE_API']['CONSUMER_KEY'],
            config['ETRADE_API']['CONSUMER_SECRET']
        )
    except Exception as e:
        print(f"Error loading config: {e}")
        return None, None

def load_tokens():
    """Load OAuth tokens from shared auth_data.json"""
    try:
        with open('auth_data.json', 'r') as f:
            auth_data = json.load(f)
        return (
            auth_data['oauth_token'],
            auth_data['oauth_token_secret']
        )
    except Exception as e:
        print(f"Error loading tokens: {e}")
        return None, None

def get_account_balance(account_id_key, force_new_auth=False):
    """
    Get account balance using shared authentication system
    
    Args:
        account_id_key: The E*TRADE account ID key
        force_new_auth: Force new authentication if True
    
    Returns:
        dict: Balance data or None if failed
    """
    
    # Try using EtradeAuth module first
    if EtradeAuth and not force_new_auth:
        try:
            etrade_auth = EtradeAuth()
            auth = etrade_auth.get_oauth_session()
            if auth is None:
                print("EtradeAuth failed, falling back to direct method")
            else:
                print("✅ Using EtradeAuth module")
        except Exception as e:
            print(f"EtradeAuth error: {e}, falling back to direct method")
            auth = None
    else:
        auth = None
    
    # Fallback to direct credential loading
    if auth is None:
        consumer_key, consumer_secret = load_credentials()
        if not consumer_key or not consumer_secret:
            print("❌ Failed to load credentials")
            return None
            
        access_token, access_token_secret = load_tokens()
        if not access_token or not access_token_secret:
            print("❌ Failed to load tokens")
            return None
            
        auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
        print("✅ Using direct OAuth1 authentication")

    # Headers
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }

    # Endpoint
    url = f'https://api.etrade.com/v1/accounts/{account_id_key}/balance?instType=BROKERAGE&realTimeNAV=true'

    try:
        # Make request
        print(f"🔄 Making request to: {url}")
        response = requests.get(url, auth=auth, headers=headers, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        
        # Handle 401 - Unauthorized
        if response.status_code == 401:
            print("🔄 401 Unauthorized - Attempting re-authentication...")
            
            if EtradeAuth and not force_new_auth:
                try:
                    etrade_auth = EtradeAuth()
                    print("Forcing new authentication...")
                    auth = etrade_auth.get_oauth_session(force_new=True)
                    if auth:
                        print("✅ Re-authentication successful, retrying request")
                        response = requests.get(url, auth=auth, headers=headers, timeout=10)
                        print(f"Retry Status Code: {response.status_code}")
                except Exception as e:
                    print(f"Re-authentication failed: {e}")
                    return None
            else:
                print("❌ 401 error and no re-authentication available")
                print("Raw Response Text:")
                print(response.text)
                return None
        
        if response.status_code == 200:
            print("✅ Request successful!")
            return response.json()
        else:
            print(f"❌ Request failed with status {response.status_code}")
            print("Raw Response Text:")
            print(response.text)
            return None
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
        return None
    except Exception as e:
        print(f"❌ Request error: {e}")
        return None

def parse_balance_response(data):
    """Parse balance response and display formatted results"""
    try:
        balance = data['BalanceResponse']['Computed']
        realtime = balance.get('RealTimeValues', {})

        print("\n✅ Parsed Account Balance:")
        print("=" * 50)
        print(f"Cash Available for Withdrawal: ${balance.get('cashAvailableForWithdrawal', 'N/A')}")
        print(f"Total Account Value: ${realtime.get('totalAccountValue', 'N/A')}")
        print(f"Margin Buying Power: ${balance.get('marginBuyingPower', 'N/A')}")
        
        # Additional balance details
        if 'netMv' in balance:
            print(f"Net Market Value: ${balance.get('netMv', 'N/A')}")
        if 'totalLongValue' in balance:
            print(f"Total Long Value: ${balance.get('totalLongValue', 'N/A')}")
        if 'cashBalance' in balance:
            print(f"Cash Balance: ${balance.get('cashBalance', 'N/A')}")
            
        return realtime.get('totalAccountValue')
        
    except Exception as e:
        print("\n❌ Failed to parse JSON response.")
        print("Error:", str(e))
        print("Raw response:")
        print(json.dumps(data, indent=2))
        return None

def get_all_account_balances():
    """Get balances for all E*TRADE accounts"""
    
    # Try using EtradeAuth module first
    if EtradeAuth:
        try:
            etrade_auth = EtradeAuth()
            auth = etrade_auth.get_oauth_session()
            if auth is None:
                print("EtradeAuth failed, falling back to direct method")
        except Exception as e:
            print(f"EtradeAuth error: {e}, falling back to direct method")
            auth = None
    else:
        auth = None
    
    # Fallback to direct credential loading
    if auth is None:
        consumer_key, consumer_secret = load_credentials()
        if not consumer_key or not consumer_secret:
            print("❌ Failed to load credentials")
            return None
            
        access_token, access_token_secret = load_tokens()
        if not access_token or not access_token_secret:
            print("❌ Failed to load tokens")
            return None
            
        auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
    
    # First get account list
    try:
        url = 'https://api.etrade.com/v1/accounts/list.json'
        response = requests.get(url, auth=auth, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
            
            print("🔄 Getting balances for all accounts:")
            print("=" * 50)
            
            total_portfolio_value = 0
            
            for account in accounts:
                account_id = account.get('accountIdKey', 'Unknown')
                account_type = account.get('accountType', 'Unknown')
                account_name = account.get('accountName', 'Unknown')
                
                print(f"\n📊 {account_type} ({account_name})")
                print(f"   Account ID: {account_id}")
                
                # Get balance for this account
                balance_data = get_account_balance(account_id)
                if balance_data:
                    try:
                        balance = balance_data['BalanceResponse']['Computed']
                        realtime = balance.get('RealTimeValues', {})
                        account_value = realtime.get('totalAccountValue', 0)
                        
                        print(f"   💰 Total Value: ${account_value:,.2f}")
                        total_portfolio_value += float(account_value) if account_value else 0
                        
                    except Exception as e:
                        print(f"   ❌ Error parsing balance: {e}")
                else:
                    print(f"   ❌ Could not get balance")
            
            print(f"\n🎯 TOTAL PORTFOLIO VALUE: ${total_portfolio_value:,.2f}")
            return total_portfolio_value
            
        else:
            print(f"❌ Failed to get account list: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting account list: {e}")
        return None

def main():
    """Main execution function"""
    print("Enhanced E*TRADE Account Balance Script")
    print("=" * 50)
    
    choice = input("Get balance for:\n1. Single IRA account\n2. All accounts\nChoice (1 or 2): ").strip()
    
    if choice == "2":
        get_all_account_balances()
    else:
        # E*TRADE IRA Account ID (from previous debugging)
        ACCOUNT_ID_KEY = 'fOTHyxD-9tctDlNfYkhFzA'  # Rollover IRA
        
        print(f"Getting balance for account: {ACCOUNT_ID_KEY}")
        
        # Get account balance
        data = get_account_balance(ACCOUNT_ID_KEY)
        
        if data:
            # Parse and display results
            total_value = parse_balance_response(data)
            
            if total_value:
                print(f"\n🎯 Key Result: Total Account Value = ${total_value}")
        else:
            print("\n❌ Failed to get account balance")
            print("\nTroubleshooting:")
            print("1. Check that auth_data.json contains valid tokens")
            print("2. Verify config.ini has correct consumer key/secret")
            print("3. Ensure account ID is correct")
            print("4. Check E*TRADE API status")

if __name__ == "__main__":
    main()
    try:
        input("\nPress Enter to continue...")
    except (EOFError, KeyboardInterrupt):
        print("\nExiting...")

"""
Enhancement Summary:
===================
1. ✅ Integrated with shared authentication system (auth_data.json, config.ini)
2. ✅ Added proper 401 error handling with automatic re-authentication
3. ✅ Supports both EtradeAuth module and fallback direct OAuth1
4. ✅ Added timeout handling to prevent hanging
5. ✅ Enhanced error reporting and troubleshooting guidance
6. ✅ Added support for getting all account balances
7. ✅ Improved response parsing with additional balance details
8. ✅ Added comprehensive documentation and usage instructions
9. ✅ Graceful handling of input/output scenarios
10. ✅ Maintains compatibility with original working functionality

This script now serves as a reliable reference implementation for E*TRADE balance API
integration that can be easily reused or referenced in future development.
"""
#!/usr/bin/env python3
"""
Get E*TRADE Account IDs
======================
"""

import requests
from requests_oauthlib import OAuth1
import json
import configparser

def get_account_ids():
    try:
        # Load config
        config = configparser.ConfigParser()
        config.read('config.ini')
        consumer_key = config['ETRADE_API']['CONSUMER_KEY']
        consumer_secret = config['ETRADE_API']['CONSUMER_SECRET']
        
        # Load tokens
        with open('auth_data.json', 'r') as f:
            auth_data = json.load(f)
        access_token = auth_data['oauth_token']
        access_token_secret = auth_data['oauth_token_secret']
        
        # OAuth1 setup
        auth = OAuth1(consumer_key, consumer_secret, access_token, access_token_secret)
        
        # Get account list
        url = 'https://api.etrade.com/v1/accounts/list.json'
        response = requests.get(url, auth=auth, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            accounts = data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
            
            print("E*TRADE Account IDs:")
            print("=" * 50)
            
            for account in accounts:
                account_id = account.get('accountIdKey', 'Unknown')
                account_type = account.get('accountType', 'Unknown')
                account_name = account.get('accountName', 'Unknown')
                
                print(f"{account_type}: {account_id}")
                
                if 'IRA' in account_type.upper():
                    print(f"   ⭐ E*TRADE IRA ID: {account_id}")
                    
        else:
            print(f"Error: {response.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_account_ids()
    input("Press Enter...")

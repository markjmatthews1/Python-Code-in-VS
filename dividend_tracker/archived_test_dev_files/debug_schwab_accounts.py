#!/usr/bin/env python3
"""
Debug Schwab Account Structure
"""
import sys
import os
import json
import requests
import importlib.util

def debug_schwab_accounts():
    """Debug Schwab account structure to find account IDs"""
    try:
        # Get main directory path (go up two levels)
        main_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        
        # Import Schwab_auth from main directory
        main_schwab_auth_path = os.path.join(main_dir, "Schwab_auth.py")
        spec = importlib.util.spec_from_file_location("main_schwab_auth", main_schwab_auth_path)
        main_schwab_auth = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(main_schwab_auth)
        
        # Set the token file path
        main_schwab_auth.TOKEN_FILE = os.path.join(main_dir, "tokens.json")
        
        # Load tokens
        tokens = main_schwab_auth.load_tokens()
        if not tokens:
            print("❌ No tokens available")
            return
        
        print("✅ Tokens loaded successfully")
        
        # Make API call
        accounts_url = "https://api.schwabapi.com/trader/v1/accounts"
        headers = {
            'Authorization': f'Bearer {tokens["access_token"]}',
            'Accept': 'application/json'
        }
        
        response = requests.get(accounts_url, headers=headers)
        
        if response.status_code != 200:
            print(f"❌ API failed: {response.status_code}")
            print(f"Response: {response.text}")
            return
        
        accounts = response.json()
        print(f"✅ Found {len(accounts)} accounts")
        
        for i, account_wrapper in enumerate(accounts):
            account = account_wrapper.get('securitiesAccount', {})
            print(f"\n📊 Account {i+1}:")
            print(f"   Available fields: {list(account.keys())}")
            
            # Look for different ID fields
            for key in account.keys():
                if 'id' in key.lower() or 'number' in key.lower():
                    print(f"   {key}: {account[key]}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_schwab_accounts()

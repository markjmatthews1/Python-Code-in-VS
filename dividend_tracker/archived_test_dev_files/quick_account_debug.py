#!/usr/bin/env python3
import sys
import os

# Add path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from etrade_account_api import ETRADEAccountAPI
    
    api = ETRADEAccountAPI()
    accounts = api.get_account_list()
    
    print(f"Found {len(accounts)} accounts:")
    
    for i, acc in enumerate(accounts):
        account_id = acc.get('accountIdKey', 'N/A')
        account_type = acc.get('accountType', 'N/A')
        account_desc = acc.get('accountDesc', 'N/A')
        
        print(f"{i+1}. ID: {account_id}")
        print(f"   Type: {account_type}")
        print(f"   Desc: {account_desc}")
        print(f"   IRA account? {'YES' if 'IRA' in account_desc.upper() else 'NO'}")
        print()
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

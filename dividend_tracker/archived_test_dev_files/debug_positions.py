#!/usr/bin/env python3
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from etrade_account_api import ETRADEAccountAPI

print("Debugging position data structure...")

api = ETRADEAccountAPI()
accounts = api.get_account_list()

# Find IRA account
ira_account = None
for acc in accounts:
    if 'IRA' in acc.get('accountType', '').upper():
        ira_account = acc
        break

if ira_account:
    print(f"Using account: {ira_account.get('accountDesc')} - {ira_account.get('accountIdKey')}")
    
    positions = api.get_account_positions(ira_account['accountIdKey'])
    print(f"Found {len(positions)} positions")
    
    if positions:
        print("\nFirst 3 positions structure:")
        for i, pos in enumerate(positions[:3]):
            print(f"Position {i+1}:")
            for key, value in pos.items():
                if key == 'symbol' or 'symbol' in key.lower():
                    print(f"  {key}: {value}")
            print()
else:
    print("No IRA account found")

"""
Debug E*TRADE API Position Data Structure
Author: Mark
Date: July 26, 2025
Purpose: Investigate actual position data structure to fix portfolio value calculation
"""

from etrade_account_api import ETRADEAccountAPI
import json

def debug_position_data():
    """Debug the actual structure of position data from E*TRADE API"""
    
    try:
        api = ETRADEAccountAPI()
        accounts = api.get_account_list()
        
        if not accounts:
            print("❌ No accounts found")
            return
        
        for account in accounts:
            account_id_key = account.get('accountIdKey')
            account_name = account.get('accountName', '')
            account_type = account.get('accountType', '')
            
            print(f"\n📊 Account: {account_name} ({account_type})")
            print(f"    Account ID Key: {account_id_key}")
            
            # Get positions
            positions = api.get_account_positions(account_id_key)
            
            if not positions:
                print("    ❌ No positions found")
                continue
            
            print(f"    📈 Found {len(positions)} positions")
            
            # Show first position structure in detail
            if positions:
                first_position = positions[0]
                print("\n🔍 First Position Data Structure:")
                print(json.dumps(first_position, indent=2, default=str))
                
                # Show all available keys
                print(f"\n📋 Available Position Keys: {list(first_position.keys())}")
                
                # Try to find value-related fields
                value_fields = []
                for key, value in first_position.items():
                    if any(word in key.lower() for word in ['value', 'price', 'market', 'total', 'worth']):
                        value_fields.append((key, value))
                
                if value_fields:
                    print(f"\n💰 Value-related fields:")
                    for key, value in value_fields:
                        print(f"    {key}: {value}")
                else:
                    print("    ⚠️ No obvious value fields found")
                
                # Check if there's a Quote or similar nested object
                if 'Quote' in first_position:
                    quote = first_position['Quote']
                    print(f"\n💹 Quote Data: {quote}")
                
                break  # Only show first account for debugging
    
    except Exception as e:
        print(f"❌ Error debugging position data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_position_data()

#!/usr/bin/env python3
"""
Debug Cache Data Structure for Positions
"""

import json
import os

def debug_cache_positions():
    """Debug the structure of positions data in cache"""
    
    cache_file = "portfolio_data_cache.json"
    
    if not os.path.exists(cache_file):
        print("❌ Cache file not found")
        return
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        print("🔍 Cache Data Structure")
        print("=" * 40)
        print(f"Top-level keys: {list(cache_data.keys())}")
        
        if 'positions' in cache_data:
            positions = cache_data['positions']
            print(f"\nPositions type: {type(positions)}")
            print(f"Positions content:")
            
            if isinstance(positions, dict):
                for account, account_data in positions.items():
                    print(f"  {account}: {type(account_data)}")
                    if isinstance(account_data, (list, dict)):
                        if isinstance(account_data, list):
                            print(f"    List length: {len(account_data)}")
                            if account_data:
                                print(f"    First item: {account_data[0]}")
                        else:
                            print(f"    Dict keys: {list(account_data.keys())[:5]}...")  # Show first 5
            elif isinstance(positions, list):
                print(f"  List length: {len(positions)}")
                if positions:
                    print(f"  First item: {positions[0]}")
        else:
            print("\n❌ No 'positions' key in cache data")
    
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_cache_positions()
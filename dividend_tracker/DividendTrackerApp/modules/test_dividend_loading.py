#!/usr/bin/env python3
"""Test dividend loading with Schwab integration"""

from estimated_income_tracker import load_estimate_files

def test_dividend_loading():
    print("🔄 Testing dividend loading with API integration...")
    
    try:
        data = load_estimate_files(use_api=True)
        
        print(f"\n📊 Found {len(data)} account types:")
        for account_type, df in data.items():
            print(f"  {account_type}: {len(df)} positions")
            if len(df) > 0:
                print(f"    Sample symbols: {list(df['Symbol'].head(3))}")
        
        return data
        
    except Exception as e:
        print(f"❌ Error testing dividend loading: {e}")
        return None

if __name__ == "__main__":
    test_dividend_loading()

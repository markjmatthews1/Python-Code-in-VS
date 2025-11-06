#!/usr/bin/env python3
"""
Inspect the actual data file to see account names
"""

import pandas as pd
import os

def inspect_data_file():
    """Inspect the dividend_stocks.xlsx file"""
    
    data_file = os.path.join("data", "dividend_stocks.xlsx")
    
    if not os.path.exists(data_file):
        print(f"❌ {data_file} not found")
        return
    
    print(f"🔍 Inspecting {data_file}")
    print("=" * 50)
    
    try:
        df = pd.read_excel(data_file)
        print(f"📊 Found {len(df)} rows")
        print(f"📝 Columns: {list(df.columns)}")
        print()
        
        # Check account column values
        if 'Account' in df.columns:
            account_values = df['Account'].dropna().unique()
            print(f"🏦 Unique Account values:")
            for acc in account_values:
                count = len(df[df['Account'] == acc])
                print(f"  • {acc}: {count} positions")
        
        print(f"\n📋 First 5 rows:")
        print(df.head().to_string())
        
        # Look for duplicate tickers
        if 'Ticker' in df.columns:
            ticker_counts = df['Ticker'].value_counts()
            duplicates = ticker_counts[ticker_counts > 1]
            
            if len(duplicates) > 0:
                print(f"\n🔄 Duplicate tickers:")
                for ticker, count in duplicates.items():
                    print(f"  • {ticker}: {count} entries")
                    # Show which accounts have this ticker
                    ticker_accounts = df[df['Ticker'] == ticker]['Account'].tolist()
                    print(f"    Accounts: {ticker_accounts}")
            else:
                print(f"\n✅ No duplicate tickers found")
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")

if __name__ == "__main__":
    inspect_data_file()

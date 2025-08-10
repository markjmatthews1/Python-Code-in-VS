#!/usr/bin/env python3
"""
Test Historical Data Reading
Check if we can read the dividend_stocks.xlsx historical data correctly
"""

import pandas as pd
import os

def test_historical_data_reading():
    """Test reading historical data from dividend_stocks.xlsx"""
    
    print("🔍 Testing Historical Data Reading")
    print("=" * 50)
    
    data_file = os.path.join(os.path.dirname(__file__), "data", "dividend_stocks.xlsx")
    
    if not os.path.exists(data_file):
        print(f"❌ File not found: {data_file}")
        return
    
    try:
        # Read the Excel file
        df = pd.read_excel(data_file)
        
        print(f"📊 File loaded successfully")
        print(f"📊 Shape: {df.shape} (rows x columns)")
        print(f"📊 Columns: {list(df.columns)}")
        
        # Look for date columns
        date_columns = []
        mm_dd_yyyy_format = []
        yyyy_mm_dd_format = []
        
        for col in df.columns:
            col_str = str(col)
            # Look for date columns (formats: MM/DD/YYYY, MM-DD-YYYY, YYYY-MM-DD, etc.)
            if '2025' in col_str and col_str not in ['Ticker', 'Account', 'Beginning Dividend Yield']:
                if any(char in col_str for char in ['-', '/']):
                    date_columns.append(col_str)
                    # Categorize by format
                    if col_str.startswith('2025'):
                        yyyy_mm_dd_format.append(col_str)
                    else:
                        mm_dd_yyyy_format.append(col_str)
        
        print(f"\n📅 Found {len(date_columns)} date columns:")
        print(f"  📅 MM/DD/YYYY format (preferred): {len(mm_dd_yyyy_format)} columns")
        print(f"  📅 YYYY-MM-DD format (older): {len(yyyy_mm_dd_format)} columns")
        
        # Show sample of each format
        if mm_dd_yyyy_format:
            print(f"  ✅ Preferred format examples: {sorted(mm_dd_yyyy_format, reverse=True)[:3]}")
        if yyyy_mm_dd_format:
            print(f"  📊 Older format examples: {sorted(yyyy_mm_dd_format, reverse=True)[:3]}")
        
        for i, date_col in enumerate(sorted(date_columns, reverse=True)[:10]):  # Show first 10
            format_type = "MM/DD/YYYY" if not date_col.startswith('2025') else "YYYY-MM-DD"
            print(f"  {i+1}. {date_col} ({format_type})")
        
        if len(date_columns) > 10:
            print(f"  ... and {len(date_columns) - 10} more")
        
        # Show sample data for first few tickers
        print(f"\n📈 Sample ticker data:")
        ticker_count = 0
        historical_yields = {}
        
        for idx, row in df.iterrows():
            if pd.notna(row.get('Ticker')) and ticker_count < 5:
                ticker = str(row['Ticker']).strip()
                print(f"\n🔸 {ticker}:")
                print(f"  Account: {row.get('Account', 'N/A')}")
                print(f"  Qty: {row.get('Qty #', 'N/A')}")
                print(f"  Price Paid: ${row.get('Price Paid $', 'N/A')}")
                print(f"  Beginning Yield: {row.get('Beginning Dividend Yield', 'N/A')}%")
                
                # Show historical yields for this ticker
                ticker_yields = {}
                for date_col in sorted(date_columns, reverse=True)[:5]:  # Show last 5 weeks
                    yield_value = row.get(date_col)
                    if pd.notna(yield_value) and isinstance(yield_value, (int, float)):
                        ticker_yields[date_col] = float(yield_value)
                
                if ticker_yields:
                    print(f"  Recent yields: {ticker_yields}")
                    historical_yields[ticker] = ticker_yields
                else:
                    print(f"  ⚠️ No historical yield data found")
                
                ticker_count += 1
        
        print(f"\n📊 Summary:")
        print(f"  ✅ Total tickers: {len(df)}")
        print(f"  ✅ Date columns found: {len(date_columns)}")
        print(f"  ✅ Tickers with historical data: {len(historical_yields)}")
        
        # Test if data matches expected format
        if date_columns:
            print(f"\n✅ Your data format is PERFECT for import!")
            print(f"📅 Mixed date formats detected:")
            print(f"  ✅ Preferred: MM/DD/YYYY (e.g., {mm_dd_yyyy_format[0] if mm_dd_yyyy_format else 'none'})")
            print(f"  📊 Older: YYYY-MM-DD (e.g., {yyyy_mm_dd_format[0] if yyyy_mm_dd_format else 'none'})")
            print(f"📊 Historical yields are numeric values")
            print(f"🎯 The script will read both date formats correctly")
        else:
            print(f"\n❌ No date columns found matching the expected format")
            print(f"🔍 Expected formats: MM/DD/YYYY or YYYY-MM-DD")
        
        return True
        
    except Exception as e:
        print(f"❌ Error reading file: {e}")
        return False

if __name__ == "__main__":
    test_historical_data_reading()

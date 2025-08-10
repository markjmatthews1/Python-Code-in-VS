#!/usr/bin/env python3
"""
Simple Excel Column Inspector
Check exactly what's in the dividend_stocks.xlsx file
"""

import pandas as pd
import os

def inspect_excel_structure():
    """Inspect the exact structure of the Excel file"""
    
    data_file = os.path.join(os.path.dirname(__file__), "data", "dividend_stocks.xlsx")
    
    if not os.path.exists(data_file):
        print(f"❌ File not found: {data_file}")
        return
    
    try:
        df = pd.read_excel(data_file)
        
        print(f"📊 Excel file structure:")
        print(f"   Shape: {df.shape}")
        print(f"   Columns: {len(df.columns)}")
        
        # Show all column names
        print(f"\n📋 All column names:")
        for i, col in enumerate(df.columns):
            print(f"   {i:2d}. '{col}'")
        
        # Show first few rows of data
        print(f"\n📈 First 3 rows of data:")
        for idx in range(min(3, len(df))):
            print(f"\n🔸 Row {idx}:")
            for col in df.columns:
                value = df.iloc[idx][col]
                if pd.notna(value) and str(value).strip():
                    print(f"      {col}: '{value}'")
        
        # Look for potential account columns
        print(f"\n🔍 Looking for account-related data...")
        account_keywords = ['etrade', 'schwab', 'individual', 'ira', 'taxable']
        
        for col in df.columns:
            for idx in range(len(df)):
                value = str(df.iloc[idx][col]).lower().strip()
                if any(keyword in value for keyword in account_keywords):
                    print(f"   Found '{df.iloc[idx][col]}' in column '{col}' row {idx}")
                    break
    
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    inspect_excel_structure()

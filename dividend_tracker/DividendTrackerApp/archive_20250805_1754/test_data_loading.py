#!/usr/bin/env python3
"""
Quick test script to check if data loading is working correctly
"""

import os
import pandas as pd
from datetime import datetime

def test_data_loading():
    print("🔍 Testing Data Loading...")
    print("=" * 50)
    
    # Check Excel files exist
    base_path = os.path.join(os.path.dirname(__file__), '..', '..')
    
    etrade_files = {
        'IRA': os.path.join(base_path, 'Etrade_Rollover_IRA_data.xlsx'),
        'Taxable': os.path.join(base_path, 'Etrade_Individual_Brokerage_data.xlsx')
    }
    
    print("📂 Checking E*TRADE Excel files:")
    for account_type, file_path in etrade_files.items():
        if os.path.exists(file_path):
            print(f"   ✅ {account_type}: {os.path.basename(file_path)} - EXISTS")
            
            # Try to read it
            try:
                wb_data = pd.read_excel(file_path, sheet_name=None)
                print(f"      📊 Sheets found: {list(wb_data.keys())}")
                
                for sheet_name, df in wb_data.items():
                    if not df.empty:
                        print(f"         • {sheet_name}: {len(df)} rows, {len(df.columns)} columns")
                        if len(df.columns) > 0:
                            print(f"           Columns: {list(df.columns)[:3]}...")
                    
            except Exception as e:
                print(f"      ❌ Error reading: {e}")
        else:
            print(f"   ❌ {account_type}: {file_path} - NOT FOUND")
    
    print("\n📂 Checking Schwab Excel file:")
    dividends_file = os.path.join('outputs', 'Dividends_2025.xlsx')
    if os.path.exists(dividends_file):
        print(f"   ✅ Dividends_2025.xlsx - EXISTS in outputs directory")
        
        try:
            wb_data = pd.read_excel(dividends_file, sheet_name=None)
            print(f"      📊 Sheets found: {list(wb_data.keys())}")
            
            for sheet_name, df in wb_data.items():
                if not df.empty:
                    print(f"         • {sheet_name}: {len(df)} rows, {len(df.columns)} columns")
                    if 'schwab' in sheet_name.lower() or 'individual' in sheet_name.lower():
                        print(f"           🎯 Potential Schwab data in: {sheet_name}")
                        if len(df.columns) > 0:
                            print(f"           Columns: {list(df.columns)}")
                        
        except Exception as e:
            print(f"      ❌ Error reading: {e}")
    else:
        print(f"   ❌ Dividends_2025.xlsx - NOT FOUND in outputs directory")
    
    print("\n🏁 Test complete!")

if __name__ == "__main__":
    test_data_loading()

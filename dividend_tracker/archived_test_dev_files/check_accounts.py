#!/usr/bin/env python3
"""
Check account column data specifically
"""

import pandas as pd
import os

def check_account_data():
    """Check the exact account data in column 34"""
    
    data_file = os.path.join(os.path.dirname(__file__), "data", "dividend_stocks.xlsx")
    df = pd.read_excel(data_file)
    
    print(f"🔍 Account data in 'Unnamed: 34' column:")
    for idx, row in df.iterrows():
        ticker = row.get('Ticker', 'N/A')
        account_value = row.get('Unnamed: 34', 'N/A')
        print(f"   Row {idx}: {ticker} = '{account_value}' (type: {type(account_value)})")
        
        if idx >= 5:  # Just show first few rows
            print("   ...")
            break

if __name__ == "__main__":
    check_account_data()

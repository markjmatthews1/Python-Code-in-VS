#!/usr/bin/env python3
"""
Test the improved data integrity monitoring with weekend awareness
"""

import pandas as pd
from datetime import datetime, date
import sys
import os

# Add current directory to path to import modules
sys.path.append(os.getcwd())

# Import the updated data integrity monitor
from data_integrity_monitor import check_data_integrity

def test_weekend_data_integrity():
    print("🧪 Testing Weekend-Aware Data Integrity Check")
    print("=" * 60)
    
    # Load the actual historical data file
    try:
        df = pd.read_csv("historical_data.csv")
        print(f"✅ Loaded historical data: {len(df)} rows")
        
        # Show date range in the data
        if 'Datetime' in df.columns:
            df_temp = df.copy()
            df_temp['Datetime'] = pd.to_datetime(df_temp['Datetime'], format='mixed')
            df_temp['Date'] = df_temp['Datetime'].dt.date
            
            date_range = f"{df_temp['Date'].min()} to {df_temp['Date'].max()}"
            tickers = sorted(df_temp['Ticker'].unique())
            print(f"📅 Date range: {date_range}")
            print(f"📊 Tickers: {len(tickers)} unique tickers")
            print(f"🎯 Sample tickers: {tickers[:5]}")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    # Test with a subset of tickers (the top 5 from the app)
    test_tickers = ['ETHU', 'TQQQ', 'LABU', 'JNUG', 'NVDL']
    
    print(f"\n🔍 Testing data integrity for: {test_tickers}")
    print("-" * 60)
    
    # Run the improved data integrity check
    is_valid, errors, details = check_data_integrity(df, test_tickers)
    
    print(f"\n📊 RESULTS:")
    print(f"   Valid: {is_valid}")
    print(f"   Errors: {errors}")
    
    print(f"\n📋 DETAILED ANALYSIS:")
    for detail in details:
        print(f"   {detail}")
    
    print(f"\n🎯 EXPECTED BEHAVIOR:")
    print(f"   - Should recognize today is Saturday (weekend)")
    print(f"   - Should NOT expect Saturday data")
    print(f"   - Should accept Friday's data as current")
    print(f"   - Should show high coverage % for weekend")
    print(f"   - Should use lenient coverage threshold (60% vs 80%)")

if __name__ == "__main__":
    test_weekend_data_integrity()

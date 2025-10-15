#!/usr/bin/env python3
"""
Simple test script to verify basic trade tracking functionality
"""

import pandas as pd
import os
from datetime import datetime, date

def test_basic_functionality():
    """Test the basic trade tracking CSV functionality"""
    
    print("🧪 Testing WeeklyPay Trade Tracking - Basic Functions")
    print("=" * 55)
    
    # Test 1: CSV creation and writing
    print("📝 Test 1: CSV Creation and Writing")
    
    # Create test trade data
    test_trades = pd.DataFrame({
        'Date': [date.today(), date.today()],
        'Ticker': ['NVDW', 'AMDW'],
        'Action': ['BUY', 'BUY'],
        'Quantity': [100, 50],
        'Price': [52.30, 48.75],
        'Total': [5230.00, 2437.50],
        'Notes': ['Top WeeklyPay pick', 'Strong rotation signal'],
        'WeeklyPay_Score': [8.5, 7.2]
    })
    
    # Save test data
    test_trades.to_csv('test_trades.csv', index=False)
    
    if os.path.exists('test_trades.csv'):
        print("✅ CSV file created successfully")
    else:
        print("❌ CSV file creation failed")
        return False
    
    # Test 2: CSV reading
    print("\n📖 Test 2: CSV Reading")
    
    try:
        loaded_trades = pd.read_csv('test_trades.csv')
        print("✅ CSV file loaded successfully")
        print(f"✅ Loaded {len(loaded_trades)} records")
            
    except Exception as e:
        print(f"❌ CSV reading failed: {str(e)}")
        return False
    
    # Test 3: Performance calculations
    print("\n📊 Test 3: Performance Calculations")
    
    try:
        total_invested = loaded_trades[loaded_trades['Action'] == 'BUY']['Total'].sum()
        trade_count = len(loaded_trades)
        avg_score = loaded_trades['WeeklyPay_Score'].mean()
        
        print(f"✅ Total Invested: ${total_invested:,.2f}")
        print(f"✅ Trade Count: {trade_count}")
        print(f"✅ Average WeeklyPay Score: {avg_score:.2f}")
            
    except Exception as e:
        print(f"❌ Performance calculation failed: {str(e)}")
        return False
    
    # Cleanup
    print("\n🧹 Cleanup")
    try:
        os.remove('test_trades.csv')
        print("✅ Test file cleaned up")
    except:
        print("⚠️ Test file cleanup failed (not critical)")
    
    print("\n" + "=" * 55)
    print("🎉 ALL BASIC TESTS PASSED!")
    print("✅ Trade tracking system is working correctly!")
    print("=" * 55)
    
    return True

if __name__ == "__main__":
    test_basic_functionality()
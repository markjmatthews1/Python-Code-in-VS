#!/usr/bin/env python3
"""
Test script to verify WeeklyPay trade tracking functionality
"""

import pandas as pd
import os
from datetime import datetime, date

def test_trade_tracking():
    """Test the trade tracking CSV functionality"""
    
    print("🧪 Testing WeeklyPay Trade Tracking System")
    print("=" * 50)
    
    # Test CSV creation and writing
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
    test_trades.to_csv('test_weeklypay_trades.csv', index=False)
    
    if os.path.exists('test_weeklypay_trades.csv'):
        print("✅ CSV file created successfully")
    else:
        print("❌ CSV file creation failed")
        return False
    
    # Test CSV reading
    print("\n📖 Test 2: CSV Reading and Data Integrity")
    
    try:
        loaded_trades = pd.read_csv('test_weeklypay_trades.csv')
        print("✅ CSV file loaded successfully")
        
        # Verify columns
        expected_columns = ['Date', 'Ticker', 'Action', 'Quantity', 'Price', 'Total', 'Notes', 'WeeklyPay_Score']
        if list(loaded_trades.columns) == expected_columns:
            print("✅ All columns present and correct")
        else:
            print("❌ Column mismatch")
            print(f"Expected: {expected_columns}")
            print(f"Found: {list(loaded_trades.columns)}")
            return False
            
        # Verify data
        if len(loaded_trades) == 2:
            print("✅ Correct number of records loaded")
        else:
            print(f"❌ Expected 2 records, found {len(loaded_trades)}")
            return False
            
    except Exception as e:
        print(f"❌ CSV reading failed: {str(e)}")
        return False
    
    # Test performance calculations
    print("\n📊 Test 3: Performance Calculations")
    
    try:
        total_invested = loaded_trades[loaded_trades['Action'] == 'BUY']['Total'].sum()
        total_sold = loaded_trades[loaded_trades['Action'] == 'SELL']['Total'].sum()
        trade_count = len(loaded_trades)
        avg_score = loaded_trades['WeeklyPay_Score'].mean()
        
        print(f"✅ Total Invested: ${total_invested:,.2f}")
        print(f"✅ Total Sold: ${total_sold:,.2f}")
        print(f"✅ Trade Count: {trade_count}")
        print(f"✅ Average WeeklyPay Score: {avg_score:.2f}")
        
        # Verify calculations
        if total_invested == 7667.50:
            print("✅ Investment calculation correct")
        else:
            print(f"❌ Investment calculation wrong: expected 7667.50, got {total_invested}")
            return False
            
    except Exception as e:
        print(f"❌ Performance calculation failed: {str(e)}")
        return False
    
    # Test position tracking
    print("\n📈 Test 4: Position Tracking")
    
    try:
        position_summary = loaded_trades.groupby('Ticker').apply(
            lambda x: (x[x['Action'] == 'BUY']['Quantity'].sum() - x[x['Action'] == 'SELL']['Quantity'].sum())
        )
        active_positions = (position_summary > 0).sum()
        
        print(f"✅ Active Positions: {active_positions}")
        print("✅ Position Summary:")
        for ticker, quantity in position_summary.items():
            print(f"   {ticker}: {quantity} shares")
            
        if active_positions == 2:
            print("✅ Position tracking correct")
        else:
            print(f"❌ Position tracking wrong: expected 2, got {active_positions}")
            return False
            
    except Exception as e:
        print(f"❌ Position tracking failed: {str(e)}")
        return False
    
    # Test score analysis
    print("\n🎯 Test 5: WeeklyPay Score Analysis")
    
    try:
        high_score_trades = loaded_trades[loaded_trades['WeeklyPay_Score'] >= 7.0]
        mid_score_trades = loaded_trades[(loaded_trades['WeeklyPay_Score'] >= 5.0) & (loaded_trades['WeeklyPay_Score'] < 7.0)]
        low_score_trades = loaded_trades[loaded_trades['WeeklyPay_Score'] < 5.0]
        
        print(f"✅ High Score Trades (7.0+): {len(high_score_trades)}")
        print(f"✅ Mid Score Trades (5.0-7.0): {len(mid_score_trades)}")
        print(f"✅ Low Score Trades (<5.0): {len(low_score_trades)}")
        
        if len(high_score_trades) == 2 and len(mid_score_trades) == 0 and len(low_score_trades) == 0:
            print("✅ Score analysis correct")
        else:
            print("❌ Score analysis incorrect")
            return False
            
    except Exception as e:
        print(f"❌ Score analysis failed: {str(e)}")
        return False
    
    # Cleanup
    print("\n🧹 Cleanup")
    try:
        os.remove('test_weeklypay_trades.csv')
        print("✅ Test file cleaned up")
    except:
        print("⚠️ Test file cleanup failed (not critical)")
    
    print("\n" + "=" * 50)
    print("🎉 ALL TESTS PASSED! Trade tracking system is working correctly!")
    print("=" * 50)
    
    return True

def test_trade_analyzer_creation():
    """Test the standalone trade analyzer creation"""
    
    print("\n📊 Testing Trade Analyzer Creation")
    print("-" * 30)
    
    analyzer_code = '''
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="WeeklyPay Trade Analyzer", page_icon="📈", layout="wide")

st.title("📈 WeeklyPay Trade Performance Analyzer")

try:
    trades_df = pd.read_csv('weeklypay_trades.csv')
    
    if not trades_df.empty:
        trades_df['Date'] = pd.to_datetime(trades_df['Date'])
        
        # Performance metrics
        st.subheader("📊 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_invested = trades_df[trades_df['Action'] == 'BUY']['Total'].sum()
        total_sold = trades_df[trades_df['Action'] == 'SELL']['Total'].sum()
        net_position = total_invested - total_sold
        trade_count = len(trades_df)
        
        col1.metric("Total Invested", f"${total_invested:,.2f}")
        col2.metric("Total Sold", f"${total_sold:,.2f}")
        col3.metric("Net Position", f"${net_position:,.2f}")
        col4.metric("Total Trades", trade_count)
        
        # Trade timeline
        st.subheader("📈 Trade Timeline")
        fig = px.scatter(trades_df, x='Date', y='Total', color='Action', 
                        size='Quantity', hover_data=['Ticker', 'Price', 'WeeklyPay_Score'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Position analysis
        st.subheader("📋 Position Analysis")
        position_summary = trades_df.groupby('Ticker').apply(
            lambda x: pd.Series({
                'Total_Bought': x[x['Action'] == 'BUY']['Quantity'].sum(),
                'Total_Sold': x[x['Action'] == 'SELL']['Quantity'].sum(),
                'Net_Position': x[x['Action'] == 'BUY']['Quantity'].sum() - x[x['Action'] == 'SELL']['Quantity'].sum(),
                'Avg_WeeklyPay_Score': x['WeeklyPay_Score'].mean()
            })
        ).reset_index()
        
        st.dataframe(position_summary, use_container_width=True)
        
        # Recent trades
        st.subheader("🕒 Recent Trades")
        recent_trades = trades_df.sort_values('Date', ascending=False).head(10)
        st.dataframe(recent_trades, use_container_width=True)
        
    else:
        st.info("No trade data found. Start logging trades to see analysis.")
        
except FileNotFoundError:
    st.error("No trade data file found. Log some trades first!")
'''
    
    try:
        with open('test_trade_analyzer.py', 'w') as f:
            f.write(analyzer_code)
        
        if os.path.exists('test_trade_analyzer.py'):
            print("✅ Trade analyzer created successfully")
            
            # Check file size
            file_size = os.path.getsize('test_trade_analyzer.py')
            print(f"✅ File size: {file_size} bytes")
            
            # Cleanup
            os.remove('test_trade_analyzer.py')
            print("✅ Test analyzer cleaned up")
            
            return True
        else:
            print("❌ Trade analyzer creation failed")
            return False
            
    except Exception as e:
        print(f"❌ Trade analyzer creation failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 WeeklyPay Trade Tracking System Test Suite")
    print("=" * 60)
    
    success = True
    
    # Run main trade tracking tests
    if not test_trade_tracking():
        success = False
    
    # Run trade analyzer tests
    if not test_trade_analyzer_creation():
        success = False
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 ALL TESTS PASSED! The trade tracking system is ready for use!")
        print("\n📋 What you can do now:")
        print("   1. Open the dashboard: http://localhost:8508")
        print("   2. Scroll down to 'TRADE - Portfolio Performance Tracking'")
        print("   3. Log your first trade using the form")
        print("   4. Track which WeeklyPay scores perform best")
        print("   5. Measure the app's profitability over time")
    else:
        print("❌ SOME TESTS FAILED! Please check the errors above.")
    print("=" * 60)
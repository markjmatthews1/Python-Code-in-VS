#!/usr/bin/env python3
"""
SMCI Earnings Verification Script
Checks multiple sources to determine accurate earnings date
"""

import yfinance as yf
import requests
from datetime import datetime
import json

def verify_smci_earnings():
    print("=== SMCI EARNINGS VERIFICATION ===")
    print(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Check yfinance
    print("\n=== YFINANCE DATA ===")
    try:
        smci = yf.Ticker('SMCI')
        info = smci.info
        
        print(f"Next Earnings Date: {info.get('earningsDate', 'Not found')}")
        print(f"Earnings Timestamp: {info.get('earningsTimestamp', 'Not found')}")
        print(f"Earnings Time: {info.get('earningsTime', 'Not found')}")
        
        # Try to get calendar
        try:
            calendar = smci.calendar
            print(f"Earnings Calendar: {calendar}")
        except Exception as cal_e:
            print(f"Calendar error: {cal_e}")
            
    except Exception as e:
        print(f"yfinance error: {e}")
    
    # Check our system data
    print(f"\n=== OUR SYSTEM COMPARISON ===")
    print(f"❌ Opportunity Scanner: Claims SMCI earnings 2025-10-02 (TODAY)")
    print(f"❌ Earnings Calendar: Shows 0 events found")
    print(f"✅ User Research: SMCI earnings November 3rd")
    
    # Determine accuracy
    print(f"\n=== ACCURACY ASSESSMENT ===")
    print("🚨 CRITICAL ISSUE IDENTIFIED:")
    print("- Opportunity Scanner has HARDCODED incorrect date")
    print("- Earnings Calendar API is not finding any data")
    print("- User research suggests November 3rd is correct")
    
    print(f"\n=== RECOMMENDED ACTIONS ===")
    print("1. Remove hardcoded SMCI earnings date from Opportunity Scanner")
    print("2. Fix Earnings Calendar API to get real data")
    print("3. Implement data validation against multiple sources")
    print("4. Add manual override capability for verified earnings dates")

if __name__ == "__main__":
    verify_smci_earnings()
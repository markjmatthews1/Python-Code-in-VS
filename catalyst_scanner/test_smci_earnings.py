#!/usr/bin/env python3
"""
Quick test to check SMCI earnings data from Catalyst Scanner
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collectors.earnings_calendar import EarningsCalendarCollector
from datetime import datetime
import json

def test_smci_earnings():
    print("=== SMCI EARNINGS TEST ===")
    print(f"Current Date: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Current Time: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Create collector and get SMCI earnings data
        collector = EarningsCalendarCollector()
        earnings_data = collector.fetch_earnings_calendar(['SMCI'], days_ahead=45)  # Extended to 45 days
        
        print("\n=== RAW EARNINGS DATA ===")
        print(json.dumps(earnings_data, indent=2, default=str))
        
        # Check SMCI specific data
        if 'SMCI' in earnings_data:
            smci_data = earnings_data['SMCI']
            print(f"\n=== SMCI SPECIFIC DATA ===")
            print(f"Earnings Date: {smci_data.get('earnings_date', 'Not found')}")
            print(f"Time: {smci_data.get('earnings_time', 'Not found')}")
            print(f"Days Until: {smci_data.get('days_until', 'Not calculated')}")
            print(f"Source: {smci_data.get('source', 'Unknown')}")
            
            # Manual days calculation
            earnings_date = smci_data.get('earnings_date')
            if earnings_date:
                try:
                    if isinstance(earnings_date, str):
                        earnings_dt = datetime.strptime(earnings_date, '%Y-%m-%d')
                    else:
                        earnings_dt = earnings_date
                    
                    today = datetime.now()
                    days_until = (earnings_dt - today).days
                    print(f"\n=== MANUAL CALCULATION ===")
                    print(f"Today: {today.strftime('%Y-%m-%d')}")
                    print(f"Earnings: {earnings_dt.strftime('%Y-%m-%d')}")
                    print(f"Days until SMCI earnings: {days_until}")
                    
                    if days_until == 1:
                        print("✅ CONFIRMED: SMCI earnings in 1 day")
                    elif days_until == 0:
                        print("⚠️  SMCI earnings are TODAY")
                    elif days_until < 0:
                        print(f"❌ SMCI earnings were {abs(days_until)} days ago")
                    else:
                        print(f"📅 SMCI earnings in {days_until} days")
                        
                except Exception as e:
                    print(f"Error in date calculation: {e}")
        else:
            print("❌ No SMCI data found in earnings results")
            
    except Exception as e:
        print(f"Error collecting earnings data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_smci_earnings()
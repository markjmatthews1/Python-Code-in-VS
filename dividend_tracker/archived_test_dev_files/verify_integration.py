#!/usr/bin/env python3
"""
Quick Integration Verification
=============================
Verify that the Etrade menu integration is working properly
"""

import os
import sys

def verify_integration():
    print("🔧 VERIFYING ETRADE MENU INTEGRATION")
    print("=" * 40)
    
    # Check if files exist
    base_dir = r"c:\Users\mjmat\Python Code in VS"
    dividend_tracker_dir = os.path.join(base_dir, "dividend_tracker", "DividendTrackerApp")
    
    files_to_check = [
        (os.path.join(base_dir, "Etrade_menu.py"), "Main Menu"),
        (os.path.join(dividend_tracker_dir, "proper_excel_updater.py"), "Working Updater"),
        (os.path.join(dividend_tracker_dir, "portfolio_data_collector.py"), "API Collector"),
        (os.path.join(dividend_tracker_dir, "outputs", "Dividends_2025.xlsx"), "Excel File")
    ]
    
    all_good = True
    
    for file_path, description in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {description}: {os.path.basename(file_path)}")
        else:
            print(f"❌ {description}: MISSING - {file_path}")
            all_good = False
    
    print("\n📋 INTEGRATION STATUS:")
    if all_good:
        print("✅ All components are in place!")
        print("🎯 The 'Complete System Update (WORKING - Append Only)' button")
        print("   should now run the proper_excel_updater.py script")
        print("   that preserves historical data and adds new columns.")
        print("\n🔄 To test: Run Etrade_menu.py and click the button")
    else:
        print("❌ Some components are missing!")
        print("⚠️  The integration may not work properly")
        
    print("\n" + "=" * 40)

if __name__ == "__main__":
    verify_integration()

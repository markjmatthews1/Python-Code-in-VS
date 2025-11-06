#!/usr/bin/env python3
"""
Test Complete System Update with Historical Yield Integration
"""

import os
import sys

# Add the DividendTrackerApp to path
dividend_tracker_path = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp"
sys.path.insert(0, dividend_tracker_path)

from proper_excel_updater import ProperExcelUpdater

def test_complete_system_update():
    """Test the complete system update process"""
    print("🚀 TESTING COMPLETE SYSTEM UPDATE WITH HISTORICAL YIELD")
    print("=" * 60)
    
    try:
        updater = ProperExcelUpdater()
        
        # Check if cache file exists
        if not os.path.exists(updater.cache_file):
            print(f"❌ Cache file missing: {updater.cache_file}")
            return False
            
        print(f"✅ Cache file found: portfolio_data_cache.json")
        
        # Check if Excel file exists
        if not os.path.exists(updater.excel_file):
            print(f"❌ Excel file missing: {updater.excel_file}")
            return False
            
        print(f"✅ Excel file found: Dividends_2025.xlsx")
        
        # Test just the historical yield update first
        print("\n📊 Testing historical yield update...")
        success = updater.update_historical_yield_sheet()
        
        if success:
            print("✅ Historical yield sheet test PASSED")
        else:
            print("❌ Historical yield sheet test FAILED")
            
        return success
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_complete_system_update()
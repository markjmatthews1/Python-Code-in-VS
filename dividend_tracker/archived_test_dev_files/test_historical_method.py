#!/usr/bin/env python3

# Test script to simulate the exact call that proper_excel_updater makes
import os
import sys

# Add the current directory to path
sys.path.insert(0, os.getcwd())

def test_historical_yield_method():
    """Test the update_historical_yield_sheet method directly"""
    print("TESTING HISTORICAL YIELD METHOD")
    print("=" * 40)
    
    try:
        # Import the proper excel updater
        from proper_excel_updater import ProperExcelUpdater
        
        # Create an instance
        updater = ProperExcelUpdater()
        
        # Call the historical yield update method
        print("Calling update_historical_yield_sheet()...")
        result = updater.update_historical_yield_sheet()
        
        print(f"Method returned: {result}")
        
        if result:
            print("SUCCESS: Historical yield sheet update method worked!")
        else:
            print("ERROR: Historical yield sheet update method failed")
            
        return result
        
    except Exception as e:
        print(f"ERROR: Exception during method call: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_historical_yield_method()
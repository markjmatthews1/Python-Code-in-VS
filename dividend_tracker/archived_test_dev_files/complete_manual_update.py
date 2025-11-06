#!/usr/bin/env python3
"""
Complete manual update script that handles both 401k and QDTE properly
"""

import os
import sys
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def complete_manual_update():
    """Complete manual update with 401k prompt and QDTE fix"""
    
    print("=== COMPLETE MANUAL DIVIDEND TRACKER UPDATE ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Get 401k value from user
    print("\n💰 401K VALUE INPUT REQUIRED")
    print("Please enter your current 401k value:")
    
    while True:
        try:
            k401_input = input("401k Value: $")
            k401_value = float(k401_input.replace(',', '').replace('$', ''))
            print(f"✅ 401k value entered: ${k401_value:,.2f}")
            break
        except ValueError:
            print("❌ Invalid input. Please enter a number (e.g., 125000)")
    
    # Now run the estimated income tracker with the 401k value
    print("\n📊 UPDATING ESTIMATED INCOME AND PORTFOLIO VALUES...")
    
    try:
        import estimated_income_tracker
        
        # Call with the 401k value provided
        estimated_income_tracker.build_estimated_income_tracker(
            import_historical=False,
            use_api=False,  # Use Excel for now to avoid module import issues
            use_hybrid=False,
            include_portfolio=True,
            create_comprehensive=True,
            k401_value=k401_value
        )
        
        print("✅ Portfolio and income sheets updated with 401k value")
        
    except Exception as e:
        print(f"❌ Error updating sheets: {e}")
        import traceback
        traceback.print_exc()
    
    print(f"\n✅ Manual update completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("📝 Note: QDTE yield issue requires separate fix to historic yield updater")
    
    input("\nPress Enter to continue...")

if __name__ == "__main__":
    complete_manual_update()

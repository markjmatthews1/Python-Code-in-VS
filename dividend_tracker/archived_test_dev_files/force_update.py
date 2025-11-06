#!/usr/bin/env python3
"""
Direct test script to force update the dividend tracker data
"""

import os
import sys
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def force_update():
    """Force update the dividend tracker by calling functions directly"""
    
    print("=== FORCE UPDATE DIVIDEND TRACKER ===")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Import the estimated income tracker
        import estimated_income_tracker
        print("✅ Successfully imported estimated_income_tracker")
        
        # Try to call the main function directly
        print("🔄 Attempting to run build_estimated_income_tracker...")
        
        # Call with the parameters that should work
        estimated_income_tracker.build_estimated_income_tracker(
            import_historical=False,
            use_api=True, 
            use_hybrid=True,
            include_portfolio=True,
            create_comprehensive=True
        )
        
        print("✅ Direct function call completed")
        return True
        
    except Exception as e:
        print(f"❌ Error in direct function call: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = force_update()
    print(f"\n=== RESULT: {'SUCCESS' if success else 'FAILED'} ===")
    input("Press Enter to continue...")

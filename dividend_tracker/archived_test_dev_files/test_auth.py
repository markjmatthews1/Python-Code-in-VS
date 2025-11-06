#!/usr/bin/env python3
"""
Simple test to check E*TRADE authentication
"""

import os
import sys
import traceback

# Add the modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_etrade_auth():
    """Test E*TRADE authentication directly"""
    
    print("Testing E*TRADE authentication...")
    
    try:
        from etrade_auth import get_etrade_session
        print("Successfully imported etrade_auth")
        
        # Try to get a session
        print("Attempting to get E*TRADE session...")
        session, base_url = get_etrade_session()
        
        if session and base_url:
            print(f"SUCCESS: Got E*TRADE session")
            print(f"Base URL: {base_url}")
            return True
        else:
            print("FAILED: Could not get E*TRADE session")
            return False
            
    except Exception as e:
        print(f"ERROR: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_etrade_auth()
    print(f"\nAuthentication test result: {'PASSED' if success else 'FAILED'}")

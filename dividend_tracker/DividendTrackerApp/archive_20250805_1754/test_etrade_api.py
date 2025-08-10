"""
Test script for E*TRADE API integration
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

def test_api_connection():
    """Test the E*TRADE API connection"""
    print("🔄 Testing E*TRADE API connection...")
    
    try:
        from modules.etrade_account_api import test_etrade_connection
        result = test_etrade_connection()
        
        if result:
            print("✅ E*TRADE API test successful!")
            return True
        else:
            print("❌ E*TRADE API test failed")
            return False
            
    except Exception as e:
        print(f"❌ Error testing E*TRADE API: {e}")
        return False

if __name__ == "__main__":
    test_api_connection()

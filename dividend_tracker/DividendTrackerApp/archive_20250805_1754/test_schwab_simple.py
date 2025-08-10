#!/usr/bin/env python3
"""
Simple test to check if Schwab API is working
"""

import sys
import os

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

print("🧪 Testing Schwab API access...")

try:
    from schwab_api_integrated import SchwabAPI
    print("✅ Schwab API module imported successfully")
    
    # Try to initialize API
    api = SchwabAPI()
    print("✅ Schwab API initialized")
    
    # Test basic connection
    print("🔄 Testing connection...")
    result = api.test_connection()
    
    if result:
        print("✅ Schwab API connection successful!")
        
        # Try to get account numbers
        accounts = api.get_account_numbers()
        print(f"📊 Found {len(accounts)} Schwab accounts: {accounts}")
        
    else:
        print("❌ Schwab API connection failed")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("🏁 Test complete")

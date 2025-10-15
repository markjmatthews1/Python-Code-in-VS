#!/usr/bin/env python3
"""
Schwab API Test for Enhanced Day Trader v2.0
===========================================

Quick test to verify Schwab API authentication and data access.
"""

import sys
import os

# Add main directory to path
main_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, main_dir)

# Change to main directory for token access
original_cwd = os.getcwd()
os.chdir(main_dir)

try:
    from Schwab_auth import get_valid_access_token, fetch_quote
    print("✅ Successfully imported Schwab authentication")
    
    # Test token access
    token = get_valid_access_token()
    if token:
        print("✅ Valid access token obtained")
        
        # Test a quote
        quote_data = fetch_quote("XLK")
        if quote_data:
            print(f"✅ Successfully fetched XLK quote: ${quote_data.get('price', 'N/A')}")
        else:
            print("⚠️ Quote fetch returned no data")
    else:
        print("❌ No valid access token available")
        
except Exception as e:
    print(f"❌ Error testing Schwab API: {e}")

# Change back to original directory
os.chdir(original_cwd)

print("\n🔗 Schwab API test complete")
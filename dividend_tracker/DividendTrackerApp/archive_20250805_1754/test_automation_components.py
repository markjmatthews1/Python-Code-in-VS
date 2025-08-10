#!/usr/bin/env python3
"""
Quick Test of Automated System Components
"""

import sys
import os

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

print("TESTING AUTOMATED SYSTEM COMPONENTS...")
print("="*60)

# Test 1: Check Alpha Vantage config
print("1. Testing Alpha Vantage configuration...")
try:
    from alpha_vantage_config import ALPHA_VANTAGE_API_KEY
    if ALPHA_VANTAGE_API_KEY != "K83KWPBFXRE10DAD":
        print(f"[OK] Alpha Vantage API key configured: {ALPHA_VANTAGE_API_KEY[:8]}...")
    else:
        print("[WARNING] Alpha Vantage API key needs to be set in alpha_vantage_config.py")
        print("   Go to: https://www.alphavantage.co/support/#api-key")
except ImportError:
    print("[WARNING] Alpha Vantage config file missing")

# Test 2: E*TRADE API module
print("\n2. Testing E*TRADE API module...")
try:
    from modules.etrade_account_api import ETRADEAccountAPI
    print("[OK] E*TRADE API module imported successfully")
except ImportError as e:
    print(f"[ERROR] E*TRADE API import error: {e}")

# Test 3: Schwab auth module
print("\n3. Testing Schwab authentication module...")
try:
    from modules.Schwab_auth import get_valid_access_token
    print("[OK] Schwab auth module imported successfully")
except ImportError as e:
    print(f"[ERROR] Schwab auth import error: {e}")

# Test 4: Required packages
print("\n4. Testing required packages...")
required_packages = ['pandas', 'requests', 'openpyxl']
for package in required_packages:
    try:
        __import__(package)
        print(f"[OK] {package} available")
    except ImportError:
        print(f"[ERROR] {package} missing - install with: pip install {package}")

# Test 5: File structure
print("\n5. Testing file structure...")
required_files = [
    'automated_portfolio_update.py',
    'dividend_focused_dashboard.py',
    'alpha_vantage_config.py',
    'modules/etrade_account_api.py',
    'modules/Schwab_auth.py'
]

for file in required_files:
    if os.path.exists(file):
        print(f"[OK] {file}")
    else:
        print(f"[ERROR] {file} missing")

print("\nCOMPONENT TEST COMPLETE!")
print("\nSETUP INSTRUCTIONS:")
print("   1. Get Alpha Vantage API key: https://www.alphavantage.co/support/#api-key")
print("   2. Update alpha_vantage_config.py with your API key")
print("   3. Run: python automated_portfolio_update.py")
print("   4. Run: python dividend_focused_dashboard.py")

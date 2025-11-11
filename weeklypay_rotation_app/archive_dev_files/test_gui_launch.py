"""
Test script to diagnose WeeklyPay GUI launch issues
"""

import sys
import traceback

print("=" * 80)
print("WeeklyPay GUI Launch Diagnostic Test")
print("=" * 80)

# Test 1: Check tkinter availability
print("\n1. Testing tkinter availability...")
try:
    import tkinter as tk
    from tkinter import ttk, scrolledtext
    print("   ✅ tkinter is available")
except ImportError as e:
    print(f"   ❌ tkinter import failed: {e}")
    sys.exit(1)

# Test 2: Check required modules
print("\n2. Testing required module imports...")
try:
    import pandas as pd
    import random
    from datetime import datetime, timedelta
    print("   ✅ pandas, random, datetime available")
except ImportError as e:
    print(f"   ❌ Module import failed: {e}")
    sys.exit(1)

# Test 3: Try importing simple_dashboard
print("\n3. Testing simple_dashboard module...")
try:
    import simple_dashboard
    print("   ✅ simple_dashboard imported successfully")
except Exception as e:
    print(f"   ❌ simple_dashboard import failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 4: Check if generate_etf_data exists and works
print("\n4. Testing generate_etf_data function...")
try:
    df = simple_dashboard.generate_etf_data()
    print(f"   ✅ generate_etf_data() returned {len(df)} rows")
    print(f"   Tickers: {df['Ticker'].tolist()}")
except Exception as e:
    print(f"   ❌ generate_etf_data() failed: {e}")
    traceback.print_exc()
    sys.exit(1)

# Test 5: Try creating GUI window
print("\n5. Testing GUI window creation...")
try:
    print("   Calling create_tkinter_gui_window()...")
    root = simple_dashboard.create_tkinter_gui_window()
    if root:
        print("   ✅ GUI window created successfully!")
        print("   Window title:", root.title())
        print("   Window geometry:", root.geometry())
        print("\n   Destroying test window...")
        root.destroy()
        print("   ✅ Test complete - GUI should work!")
    else:
        print("   ❌ create_tkinter_gui_window() returned None")
except Exception as e:
    print(f"   ❌ GUI creation failed: {e}")
    traceback.print_exc()
    sys.exit(1)

print("\n" + "=" * 80)
print("✅ ALL TESTS PASSED - GUI should launch successfully!")
print("=" * 80)

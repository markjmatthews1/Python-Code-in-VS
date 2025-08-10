#!/usr/bin/env python3
"""Simple test to verify TradeTracker can start"""

try:
    import sys
    import os
    
    # Import the TradeTracker class without running the main window
    print("Testing TradeTracker import...")
    from TradeTracker import TradeTrackerApp
    print("✓ TradeTracker imported successfully")
    
    # Test if we can create an instance (without showing the window)
    print("Testing TradeTracker instantiation...")
    import tkinter as tk
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    app = TradeTrackerApp(root)
    print("✓ TradeTracker instance created successfully")
    
    # Test if the new methods exist
    if hasattr(app, 'get_stock_price_from_etrade'):
        print("✓ get_stock_price_from_etrade method exists")
    else:
        print("✗ get_stock_price_from_etrade method missing")
        
    if hasattr(app, 'get_option_price_from_etrade'):
        print("✓ get_option_price_from_etrade method exists")
    else:
        print("✗ get_option_price_from_etrade method missing")
    
    print("TradeTracker test completed successfully")
    root.destroy()
    
except Exception as e:
    print(f"✗ TradeTracker test failed: {e}")
    import traceback
    traceback.print_exc()

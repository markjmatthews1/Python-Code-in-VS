#!/usr/bin/env python3
"""Debug the P/L fix function directly"""

import sys
import tkinter as tk
from tkinter import messagebox

try:
    print("Testing Fix P/L function directly...")
    
    # Import TradeTracker
    exec(open('TradeTracker.py').read())
    
    # Create a minimal tkinter root (hidden)
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create TradeTracker instance
    app = TradeTrackerApp(root)
    
    print("TradeTracker instance created successfully")
    print("Running fix_missing_current_pl()...")
    
    # Run the fix function directly
    app.fix_missing_current_pl()
    
    print("Fix P/L function completed")
    
    root.destroy()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

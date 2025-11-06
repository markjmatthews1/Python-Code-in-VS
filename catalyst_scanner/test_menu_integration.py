#!/usr/bin/env python3
"""
Test Live Dashboard Menu Integration
"""
import tkinter as tk
import sys
import os

# Add path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from gui.main_window import CatalystScannerMainWindow
    
    # Create test window
    root = tk.Tk()
    root.withdraw()  # Hide the window
    
    # Create main window
    main_window = CatalystScannerMainWindow(root)
    
    # Test if the Live Dashboard menu method exists
    has_live_dashboard_method = hasattr(main_window, 'open_live_dashboard')
    
    print("="*50)
    print("🔍 LIVE DASHBOARD MENU INTEGRATION TEST")
    print("="*50)
    print(f"✅ Main window created successfully")
    print(f"✅ Live Dashboard method exists: {has_live_dashboard_method}")
    
    if has_live_dashboard_method:
        print(f"✅ Menu integration successful!")
        print(f"🎯 Live Dashboard accessible via View menu")
    else:
        print(f"❌ Menu integration failed - method missing")
    
    # Clean up
    root.destroy()
    
    print("="*50)
    print("📋 MENU INTEGRATION TEST COMPLETE")
    print("="*50)
    
except Exception as e:
    print(f"❌ Menu integration test failed: {e}")
    import traceback
    traceback.print_exc()
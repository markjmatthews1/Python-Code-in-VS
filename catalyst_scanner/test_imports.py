"""
Simple test to identify import issues causing the crash
"""

import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

print("🔍 TESTING CATALYST SCANNER IMPORTS")
print(f"Current directory: {current_dir}")
print(f"Python path: {sys.path[:3]}...")

try:
    print("\n1. Testing basic imports...")
    import tkinter as tk
    print("✅ tkinter import successful")
    
    print("\n2. Testing utils imports...")
    from utils.auto_refresh_manager import AutoRefreshManager
    print("✅ AutoRefreshManager import successful")
    
    from alerts.alert_system import AlertSystem
    print("✅ AlertSystem import successful")
    
    print("\n3. Testing GUI imports...")
    from gui.main_window import CatalystScannerMainWindow
    print("✅ CatalystScannerMainWindow import successful")
    
    print("\n4. Testing logger imports...")
    try:
        from utils.logger import initialize_logging, get_logger
        print("✅ Logger imports successful")
    except ImportError as e:
        print(f"⚠️ Logger import issue: {e}")
    
    print("\n5. Testing error handler imports...")
    try:
        from utils.error_handler import CatalystErrorHandler, get_error_handler
        print("✅ Error handler imports successful")
    except ImportError as e:
        print(f"⚠️ Error handler import issue: {e}")
    
    print("\n6. Testing basic GUI creation...")
    root = tk.Tk()
    root.title("Test Window")
    
    # Test main window creation
    main_window = CatalystScannerMainWindow(root)
    print("✅ Main window creation successful")
    
    # Clean up
    root.destroy()
    
    print("\n🎯 ALL TESTS PASSED - Application should work!")
    
except Exception as e:
    print(f"\n❌ ERROR FOUND: {e}")
    print(f"Error type: {type(e).__name__}")
    import traceback
    print(f"Traceback:\n{traceback.format_exc()}")

print("\n✅ Import test complete!")
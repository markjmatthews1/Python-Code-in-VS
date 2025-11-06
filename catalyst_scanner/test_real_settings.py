#!/usr/bin/env python3
"""
Test Settings with Real Objects
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import tkinter as tk
import logging
from utils.auto_refresh_manager import AutoRefreshManager
from alerts.alert_system import AlertSystem
from gui.settings_dialog import show_settings_dialog

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s | %(levelname)s | %(name)s | %(message)s')

def test_real_settings():
    """Test with actual AutoRefreshManager and AlertSystem objects"""
    print("Testing with REAL AutoRefreshManager and AlertSystem objects")
    print("="*70)
    
    root = tk.Tk()
    root.title("Real Settings Test")
    root.geometry("500x400")
    root.configure(bg="#2b2b2b")
    
    # Create REAL objects like the main app does
    try:
        print("Creating AutoRefreshManager...")
        auto_refresh_manager = AutoRefreshManager()
        print("✓ AutoRefreshManager created successfully")
        
        print("Creating AlertSystem...")
        alert_system = AlertSystem()
        print("✓ AlertSystem created successfully")
        
        # Mock main window for header alignment
        class MockMainWindow:
            def get_header_offset(self, header):
                return 0  # Simple mock
            
            def _adjust_header_in_settings(self, header, pixels, display_label):
                display_label.config(text=f"{pixels:+d} px")
            
            def _reset_header_in_settings(self, header, display_label):
                display_label.config(text="+0 px")
            
            def _reset_all_headers_in_settings(self):
                pass
        
        main_window = MockMainWindow()
        
        def open_settings():
            print("\n" + "="*50)
            print("OPENING SETTINGS DIALOG WITH REAL OBJECTS")
            print("="*50)
            try:
                dialog = show_settings_dialog(root, auto_refresh_manager, alert_system, main_window)
                print("✓ Settings dialog opened successfully!")
                print("\nNow test:")
                print("1. Change settings in any tab")
                print("2. Click Save & Apply")
                print("3. Close and reopen settings")
                print("4. Check if settings persisted")
                print("5. Check if header alignment buttons are visible")
            except Exception as e:
                print(f"✗ ERROR: {e}")
                import traceback
                traceback.print_exc()
        
        # Test button
        tk.Label(root, text="Real Settings Test", font=("Arial", 16, "bold"), 
                fg="white", bg="#2b2b2b").pack(pady=20)
        
        tk.Label(root, text="This test uses the actual AutoRefreshManager and AlertSystem\nobjects like the main application does.", 
                font=("Arial", 12), fg="lightgray", bg="#2b2b2b", justify="center").pack(pady=10)
        
        tk.Button(root, text="Open Settings Dialog", command=open_settings,
                 font=("Arial", 14, "bold"), bg="#4CAF50", fg="white",
                 padx=30, pady=15).pack(pady=20)
        
        # Show current settings
        status_frame = tk.Frame(root, bg="#333333", relief="sunken", bd=2)
        status_frame.pack(fill="x", padx=20, pady=20)
        
        tk.Label(status_frame, text="Current Settings Status:", 
                font=("Arial", 12, "bold"), fg="white", bg="#333333").pack(pady=5)
        
        refresh_status = tk.Label(status_frame, 
                                 text=f"Auto Refresh Enabled: {auto_refresh_manager.get_setting('auto_refresh_enabled', 'Not Set')}", 
                                 font=("Arial", 10), fg="lightblue", bg="#333333")
        refresh_status.pack()
        
        alert_status = tk.Label(status_frame, 
                               text=f"Visual Alerts: {alert_system.get_setting('visual_alerts_enabled', 'Not Set')}", 
                               font=("Arial", 10), fg="lightgreen", bg="#333333")
        alert_status.pack(pady=(0, 5))
        
        print("Setup complete! Click the button to test.")
        root.mainloop()
        
    except Exception as e:
        print(f"✗ ERROR creating objects: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_settings()
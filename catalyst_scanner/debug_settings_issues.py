#!/usr/bin/env python3
"""
Debug Settings Dialog Issues
"""
import sys
import os
import logging

# Add the catalyst_scanner directory to the Python path
sys.path.insert(0, os.path.abspath('.'))

import tkinter as tk
from gui.settings_dialog import show_settings_dialog

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
)

def debug_settings_issues():
    """Debug the specific issues with settings"""
    print("="*70)
    print("DEBUGGING SETTINGS DIALOG ISSUES")
    print("="*70)
    
    root = tk.Tk()
    root.title("Settings Debug Test")
    root.geometry("400x300")
    
    # Mock systems that will help us debug
    class DebugAutoRefreshManager:
        def __init__(self):
            self.settings = {}
            print(f"DEBUG: AutoRefreshManager initialized with settings: {self.settings}")
        
        def get_setting(self, key, default=None):
            value = self.settings.get(key, default)
            print(f"DEBUG: get_setting({key}) -> {value}")
            return value
        
        def update_setting(self, key, value):
            print(f"DEBUG: update_setting({key}, {value})")
            self.settings[key] = value
            print(f"DEBUG: Settings now: {self.settings}")
            return True
        
        def get_status(self):
            return {'running': False, 'last_refresh': 'Never', 'next_refresh': 'Unknown'}
        
        def is_running(self):
            return False
        
        def start_auto_refresh(self):
            print("DEBUG: start_auto_refresh called")
        
        def stop_auto_refresh(self):
            print("DEBUG: stop_auto_refresh called")
    
    class DebugAlertSystem:
        def __init__(self):
            self.settings = {}
            print(f"DEBUG: AlertSystem initialized with settings: {self.settings}")
        
        def get_setting(self, key, default=None):
            value = self.settings.get(key, default)
            print(f"DEBUG: get_setting({key}) -> {value}")
            return value
        
        def update_setting(self, key, value):
            print(f"DEBUG: update_setting({key}, {value})")
            self.settings[key] = value
            print(f"DEBUG: Alert settings now: {self.settings}")
            return True
    
    class DebugMainWindow:
        def get_header_offset(self, header):
            offsets = {"Ticker": 0, "Price": -10, "Change %": -20, "RSI": 0, "Signal": 5, "Momentum": -5}
            offset = offsets.get(header, 0)
            print(f"DEBUG: get_header_offset({header}) -> {offset}")
            return offset
        
        def _adjust_header_in_settings(self, header, pixels, display_label):
            print(f"DEBUG: _adjust_header_in_settings({header}, {pixels})")
            new_offset = self.get_header_offset(header) + pixels
            display_label.config(text=f"{new_offset:+d} px")
            print(f"DEBUG: Updated display to show {new_offset:+d} px")
        
        def _reset_header_in_settings(self, header, display_label):
            print(f"DEBUG: _reset_header_in_settings({header})")
            display_label.config(text="+0 px")
        
        def _reset_all_headers_in_settings(self):
            print("DEBUG: _reset_all_headers_in_settings()")
    
    # Create debug instances
    auto_refresh_manager = DebugAutoRefreshManager()
    alert_system = DebugAlertSystem()
    main_window = DebugMainWindow()
    
    def test_settings():
        print("\n" + "="*50)
        print("OPENING SETTINGS DIALOG")
        print("="*50)
        
        try:
            dialog = show_settings_dialog(root, auto_refresh_manager, alert_system, main_window)
            print("Settings dialog created successfully!")
            print("Check the dialog for:")
            print("1. Settings persistence - change values and save")
            print("2. Header alignment buttons - should be visible")
            print("3. Debug output in console")
        except Exception as e:
            print(f"ERROR creating settings dialog: {e}")
            import traceback
            traceback.print_exc()
    
    # Create UI
    tk.Label(root, text="Settings Dialog Debug Test", font=("Arial", 14, "bold")).pack(pady=20)
    tk.Button(root, text="Open Settings Dialog", command=test_settings, 
              bg="#4CAF50", fg="white", font=("Arial", 12), padx=20, pady=10).pack(pady=20)
    
    print("Ready to test! Click the button to open settings.")
    root.mainloop()

if __name__ == "__main__":
    debug_settings_issues()
#!/usr/bin/env python3
"""
Test the complete settings dialog with all tabs
"""
import tkinter as tk
from gui.settings_dialog import SettingsDialog
import json

# Mock main window class for testing
class MockMainWindow:
    def __init__(self):
        self.config = {
            "auto_refresh": {
                "enabled": True,
                "interval_hours": 2.0
            },
            "alerts": {
                "visual_enabled": True,
                "audio_enabled": True,
                "sms_enabled": False
            }
        }
    
    def get_header_offset(self, header_name):
        """Mock method to get header offsets"""
        # Return some test values
        offsets = {
            "Ticker": -10,
            "Price": 5,
            "Change %": 0,
            "RSI": 15,
            "Signal": -5,
            "Momentum": 20
        }
        return offsets.get(header_name, 0)
    
    def _adjust_header_in_settings(self, header_name, pixels, display_label):
        """Mock method for header adjustment"""
        print(f"Adjusting {header_name} by {pixels} pixels")
        # Update the display
        current_offset = self.get_header_offset(header_name) + pixels
        display_label.config(text=f"{current_offset:+d} px")
    
    def _reset_header_in_settings(self, header_name, display_label):
        """Mock method for header reset"""
        print(f"Resetting {header_name}")
        display_label.config(text="+0 px")
    
    def _reset_all_headers_in_settings(self):
        """Mock method for resetting all headers"""
        print("Resetting all headers")

def test_settings_dialog():
    """Test the complete settings dialog"""
    root = tk.Tk()
    root.title("Settings Dialog Test")
    
    # Create mock main window
    main_window = MockMainWindow()
    
    def open_settings():
        dialog = SettingsDialog(root, main_window)
        print("Settings dialog opened successfully!")
    
    # Create test button
    test_btn = tk.Button(
        root,
        text="Open Settings Dialog",
        command=open_settings,
        font=("Arial", 12),
        bg="#4CAF50",
        fg="white",
        padx=20,
        pady=10
    )
    test_btn.pack(pady=50)
    
    # Instructions
    instructions = tk.Label(
        root,
        text="Click the button to test the enhanced settings dialog\nwith all 4 tabs: Auto Refresh, Visual & Audio Alerts, SMS Alerts, Header Alignment",
        font=("Arial", 10),
        justify="center"
    )
    instructions.pack(pady=20)
    
    root.geometry("500x200")
    root.mainloop()

if __name__ == "__main__":
    test_settings_dialog()
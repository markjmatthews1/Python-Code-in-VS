#!/usr/bin/env python3
"""
Test Settings Dialog with Debugging
"""
import tkinter as tk
import logging
from gui.settings_dialog import show_settings_dialog

# Configure logging to see debug output
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s | %(levelname)-8s | %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

# Mock systems for testing
class MockAutoRefreshManager:
    def __init__(self):
        self.settings = {
            'auto_refresh_enabled': True,
            'refresh_interval_minutes': 120,
            'market_hours_only': True,
            'weekend_refresh': False
        }
    
    def get_setting(self, key, default=None):
        print(f"DEBUG: Getting setting {key} = {self.settings.get(key, default)}")
        return self.settings.get(key, default)
    
    def update_setting(self, key, value):
        print(f"DEBUG: Updating setting {key} = {value}")
        self.settings[key] = value
        return True
    
    def get_status(self):
        return {
            'running': True,
            'last_refresh': '2025-09-30 13:00:00',
            'next_refresh': '2025-09-30 15:00:00'
        }
    
    def is_running(self):
        return True
    
    def start_auto_refresh(self):
        print("DEBUG: Starting auto refresh")
    
    def stop_auto_refresh(self):
        print("DEBUG: Stopping auto refresh")

class MockAlertSystem:
    def __init__(self):
        self.settings = {
            'visual_alerts_enabled': True,
            'audio_alerts_enabled': True,
            'sms_alerts_enabled': False,
            'popup_duration_seconds': 10,
            'cooldown_minutes': 30,
            'alert_on_rsi_extreme': True,
            'rsi_extreme_threshold': 25,
            'alert_on_signal_change': True,
            'alert_on_momentum_change': True,
            'alert_on_opportunity_score_change': True,
            'opportunity_score_threshold': 7.0,
            'sms_phone_number': ''
        }
    
    def get_setting(self, key, default=None):
        print(f"DEBUG: Getting alert setting {key} = {self.settings.get(key, default)}")
        return self.settings.get(key, default)
    
    def update_setting(self, key, value):
        print(f"DEBUG: Updating alert setting {key} = {value}")
        self.settings[key] = value
        return True

class MockMainWindow:
    def get_header_offset(self, header):
        offsets = {
            "Ticker": 0,
            "Price": -26,
            "Change %": -70,
            "RSI": -92,
            "Signal": -100,
            "Momentum": -75
        }
        print(f"DEBUG: Getting header offset for {header} = {offsets.get(header, 0)}")
        return offsets.get(header, 0)
    
    def _adjust_header_in_settings(self, header, pixels, display_label):
        print(f"DEBUG: Adjusting header {header} by {pixels}px")
        current_offset = self.get_header_offset(header) + pixels
        display_label.config(text=f"{current_offset:+d} px")
    
    def _reset_header_in_settings(self, header, display_label):
        print(f"DEBUG: Resetting header {header}")
        display_label.config(text="+0 px")
    
    def _reset_all_headers_in_settings(self):
        print("DEBUG: Resetting all headers")

def test_enhanced_settings():
    """Test the enhanced settings dialog with debugging"""
    root = tk.Tk()
    root.title("Enhanced Settings Dialog Test")
    root.geometry("600x400")
    root.configure(bg='#2b2b2b')
    
    # Create mock systems
    auto_refresh_manager = MockAutoRefreshManager()
    alert_system = MockAlertSystem()
    main_window = MockMainWindow()
    
    def open_settings():
        print("="*60)
        print("OPENING SETTINGS DIALOG")
        print("="*60)
        dialog = show_settings_dialog(root, auto_refresh_manager, alert_system, main_window)
        print("Settings dialog opened successfully!")
    
    # Create test interface
    title = tk.Label(root, text="Enhanced Settings Dialog Test", 
                    font=("Arial", 16, "bold"), fg="white", bg="#2b2b2b")
    title.pack(pady=20)
    
    instruction = tk.Label(root, 
                          text="Click below to test the enhanced settings dialog\nwith all 4 tabs and improved functionality", 
                          font=("Arial", 12), fg="lightgray", bg="#2b2b2b", justify="center")
    instruction.pack(pady=10)
    
    test_btn = tk.Button(root, text="🔧 Open Enhanced Settings Dialog", 
                        command=open_settings,
                        font=("Arial", 14, "bold"),
                        bg="#4CAF50", fg="white",
                        padx=30, pady=15,
                        relief="raised", bd=3)
    test_btn.pack(pady=30)
    
    features = tk.Label(root, 
                       text="Features to test:\n" +
                            "✅ Auto Refresh settings persistence\n" +
                            "✅ Visual & Audio Alert configurations\n" +
                            "✅ SMS Alert settings\n" +
                            "✅ Header Alignment with live controls\n" +
                            "✅ Settings save/load functionality", 
                       font=("Arial", 10), fg="lightblue", bg="#2b2b2b", justify="left")
    features.pack(pady=20)
    
    root.mainloop()

if __name__ == "__main__":
    test_enhanced_settings()
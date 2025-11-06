#!/usr/bin/env python3
"""
Comprehensive Settings Test - Focus on Persistence and Header Buttons
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

import tkinter as tk
import logging
from utils.auto_refresh_manager import AutoRefreshManager
from alerts.alert_system import AlertSystem
from gui.settings_dialog import show_settings_dialog

# Enable detailed logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s | %(name)s | %(message)s')

def comprehensive_settings_test():
    """Test to specifically verify settings persistence and header alignment buttons"""
    print("🧪 COMPREHENSIVE SETTINGS TEST")
    print("Testing: Settings Persistence + Header Alignment Buttons")
    print("="*60)
    
    root = tk.Tk()
    root.title("Settings Test - Focus on Issues")
    root.geometry("600x500")
    root.configure(bg="#1a1a2e")
    
    # Create real objects
    auto_refresh_manager = AutoRefreshManager()
    alert_system = AlertSystem()
    
    # Mock main window with better debugging
    class TestMainWindow:
        def __init__(self):
            self.header_offsets = {"Ticker": 0, "Price": -26, "Change %": -70, "RSI": -92, "Signal": -100, "Momentum": -75}
        
        def get_header_offset(self, header):
            offset = self.header_offsets.get(header, 0)
            print(f"🔍 get_header_offset('{header}') -> {offset}")
            return offset
        
        def _adjust_header_in_settings(self, header, pixels, display_label):
            old_offset = self.header_offsets.get(header, 0)
            new_offset = old_offset + pixels
            self.header_offsets[header] = new_offset
            display_label.config(text=f"{new_offset:+d} px")
            print(f"⚡ Adjusted {header}: {old_offset} -> {new_offset} (moved {pixels}px)")
        
        def _reset_header_in_settings(self, header, display_label):
            self.header_offsets[header] = 0
            display_label.config(text="+0 px")
            print(f"🔄 Reset {header} to 0")
        
        def _reset_all_headers_in_settings(self):
            for header in self.header_offsets:
                self.header_offsets[header] = 0
            print("🔄 Reset ALL headers to 0")
    
    main_window = TestMainWindow()
    
    # Test variables to track state
    test_results = {
        "settings_opened": 0,
        "settings_saved": 0,
        "header_buttons_visible": False
    }
    
    def open_settings_test():
        test_results["settings_opened"] += 1
        attempt = test_results["settings_opened"]
        
        print(f"\n🚀 OPENING SETTINGS - ATTEMPT #{attempt}")
        print("-" * 40)
        
        try:
            # Show current settings before opening
            print("📊 Current Settings Before Opening:")
            print(f"   Auto Refresh: {auto_refresh_manager.get_setting('auto_refresh_enabled', 'DEFAULT')}")
            print(f"   Visual Alerts: {alert_system.get_setting('visual_alerts_enabled', 'DEFAULT')}")
            print(f"   SMS Enabled: {alert_system.get_setting('sms_alerts_enabled', 'DEFAULT')}")
            
            dialog = show_settings_dialog(root, auto_refresh_manager, alert_system, main_window)
            
            print("✅ Settings dialog opened successfully!")
            print("\n🔍 TEST CHECKLIST:")
            print("   1. ✅ Can you see all 4 tabs?")
            print("   2. ❓ Go to 'Header Alignment' tab - do you see adjustment buttons?")
            print("   3. ❓ Change some settings in any tab")
            print("   4. ❓ Click 'Save & Apply'")
            print("   5. ❓ Close dialog and reopen - are settings still there?")
            
        except Exception as e:
            print(f"❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    def check_persistence():
        print(f"\n🔍 CHECKING PERSISTENCE - After {test_results['settings_opened']} Opens")
        print("-" * 40)
        print("📊 Current Settings After Operations:")
        print(f"   Auto Refresh: {auto_refresh_manager.get_setting('auto_refresh_enabled', 'NOT_SET')}")
        print(f"   Visual Alerts: {alert_system.get_setting('visual_alerts_enabled', 'NOT_SET')}")
        print(f"   SMS Enabled: {alert_system.get_setting('sms_alerts_enabled', 'NOT_SET')}")
        print(f"   Phone Number: '{alert_system.get_setting('sms_phone_number', 'NOT_SET')}'")
        
        print(f"\n📐 Header Offsets:")
        for header, offset in main_window.header_offsets.items():
            print(f"   {header}: {offset:+d}px")
    
    # Create UI
    title = tk.Label(root, text="🧪 Settings Persistence & Button Test", 
                    font=("Arial", 16, "bold"), fg="#00ff41", bg="#1a1a2e")
    title.pack(pady=20)
    
    subtitle = tk.Label(root, text="Test settings persistence and header alignment button visibility", 
                       font=("Arial", 12), fg="#cccccc", bg="#1a1a2e")
    subtitle.pack(pady=5)
    
    # Buttons frame
    buttons_frame = tk.Frame(root, bg="#1a1a2e")
    buttons_frame.pack(pady=30)
    
    open_btn = tk.Button(buttons_frame, text="🔧 Open Settings Dialog", 
                        command=open_settings_test,
                        font=("Arial", 14, "bold"), bg="#0f4c75", fg="white",
                        padx=20, pady=10, relief="raised", bd=3)
    open_btn.pack(side="left", padx=10)
    
    check_btn = tk.Button(buttons_frame, text="🔍 Check Persistence", 
                         command=check_persistence,
                         font=("Arial", 14, "bold"), bg="#ff6b6b", fg="white",
                         padx=20, pady=10, relief="raised", bd=3)
    check_btn.pack(side="left", padx=10)
    
    # Issues frame
    issues_frame = tk.LabelFrame(root, text="🐛 Issues to Verify Fixed", 
                                bg="#16213e", fg="#ffaa00", font=("Arial", 12, "bold"))
    issues_frame.pack(fill="x", padx=20, pady=20)
    
    issue1 = tk.Label(issues_frame, text="1. Settings don't stay after closing dialog", 
                     font=("Arial", 11), fg="#ff4444", bg="#16213e")
    issue1.pack(anchor="w", padx=10, pady=2)
    
    issue2 = tk.Label(issues_frame, text="2. Header alignment tab only shows descriptions, no buttons", 
                     font=("Arial", 11), fg="#ff4444", bg="#16213e")
    issue2.pack(anchor="w", padx=10, pady=2)
    
    # Instructions
    instructions = tk.Label(root, 
                           text="Instructions:\n" +
                                "1. Click 'Open Settings Dialog'\n" +
                                "2. Go to Header Alignment tab - verify buttons are visible\n" +
                                "3. Change some settings in other tabs\n" +
                                "4. Click 'Save & Apply' and close dialog\n" +
                                "5. Click 'Check Persistence' to verify settings saved\n" +
                                "6. Reopen settings to verify they persisted",
                           font=("Arial", 10), fg="#00aaff", bg="#1a1a2e", justify="left")
    instructions.pack(pady=20)
    
    print("Ready! Use the buttons to test settings persistence and header alignment buttons.")
    root.mainloop()

if __name__ == "__main__":
    comprehensive_settings_test()
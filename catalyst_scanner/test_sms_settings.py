"""
Test SMS Settings Tab
Quick test to check SMS settings visibility and functionality
"""

import sys
import os

# Add the project directory to the path
project_dir = r'c:\Users\mjmat\Python Code in VS\catalyst_scanner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import tkinter as tk
from gui.settings_dialog import SettingsDialog

def test_sms_settings():
    """Test the SMS settings tab specifically"""
    root = tk.Tk()
    root.title("SMS Settings Test")
    root.geometry("800x600")
    root.configure(bg='#2b2b2b')
    
    try:
        # Create settings dialog
        dialog = SettingsDialog(root)
        
        # Select the SMS tab
        # The notebook should have tabs: Refresh, Alerts, SMS Alerts, Header Alignment
        try:
            dialog.notebook.select(2)  # SMS Alerts tab (0=Refresh, 1=Alerts, 2=SMS Alerts)
            print("SMS tab selected successfully")
        except Exception as e:
            print(f"Error selecting SMS tab: {e}")
            # Try to find and select SMS tab by name
            for i in range(dialog.notebook.index("end")):
                tab_text = dialog.notebook.tab(i, "text")
                print(f"Tab {i}: {tab_text}")
                if "SMS" in tab_text:
                    dialog.notebook.select(i)
                    print(f"Selected SMS tab at index {i}")
                    break
        
        # Check if radio button variables are working
        print(f"SMS Provider variable: {dialog.alert_vars.get('sms_provider', 'NOT FOUND')}")
        print(f"Phone Number variable: {dialog.alert_vars.get('phone_number', 'NOT FOUND')}")
        
        # Set some test values
        if 'sms_provider' in dialog.alert_vars:
            dialog.alert_vars['sms_provider'].set('mock')
            print("Set SMS provider to mock")
        
        if 'phone_number' in dialog.alert_vars:
            dialog.alert_vars['phone_number'].set('+1234567890')
            print("Set phone number to test value")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating settings dialog: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_settings()
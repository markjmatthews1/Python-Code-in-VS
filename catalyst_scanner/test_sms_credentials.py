"""
Test Complete SMS Settings with Credentials
Test the enhanced SMS settings with Twilio/AWS credential configuration
"""

import sys
import os

# Add the project directory to the path
project_dir = r'c:\Users\mjmat\Python Code in VS\catalyst_scanner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import tkinter as tk
from gui.settings_dialog import SettingsDialog
from alerts.alert_system import AlertSystem

def test_sms_credentials():
    """Test SMS settings with credential configuration"""
    
    print("Testing SMS Settings with Credential Configuration")
    print("=" * 60)
    
    # Create main window
    root = tk.Tk()
    root.title("SMS Credentials Test")
    root.geometry("900x700")
    root.configure(bg='#2b2b2b')
    
    try:
        # Create alert system for realistic testing
        alert_system = AlertSystem()
        print("Alert system created successfully")
        
        # Create settings dialog with alert system
        dialog = SettingsDialog(root, alert_system=alert_system)
        print("Settings dialog created successfully")
        
        # Navigate to SMS tab
        try:
            # Find SMS tab (usually index 2: Refresh=0, Alerts=1, SMS=2)
            for i in range(dialog.notebook.index("end")):
                tab_text = dialog.notebook.tab(i, "text")
                print(f"Tab {i}: {tab_text}")
                if "SMS" in tab_text:
                    dialog.notebook.select(i)
                    print(f"Selected SMS tab at index {i}")
                    break
        except Exception as e:
            print(f"Error selecting SMS tab: {e}")
        
        # Check SMS variables
        print("\nSMS Variables Status:")
        print(f"SMS Provider: {dialog.alert_vars.get('sms_provider', 'NOT FOUND')}")
        print(f"Phone Number: {dialog.alert_vars.get('phone_number', 'NOT FOUND')}")
        print(f"Twilio SID: {dialog.alert_vars.get('twilio_account_sid', 'NOT FOUND')}")
        print(f"Twilio Token: {dialog.alert_vars.get('twilio_auth_token', 'NOT FOUND')}")
        print(f"AWS Access Key: {dialog.alert_vars.get('aws_access_key', 'NOT FOUND')}")
        
        # Set some test values to verify functionality
        if 'sms_provider' in dialog.alert_vars:
            dialog.alert_vars['sms_provider'].set('mock')
            print("\nSet SMS provider to mock")
        
        if 'phone_number' in dialog.alert_vars:
            dialog.alert_vars['phone_number'].set('+1234567890')
            print("Set phone number to test value")
        
        # Test credential fields
        if 'twilio_account_sid' in dialog.alert_vars:
            dialog.alert_vars['twilio_account_sid'].set('ACtest123')
            print("Set test Twilio Account SID")
        
        if 'aws_access_key' in dialog.alert_vars:
            dialog.alert_vars['aws_access_key'].set('AKIATEST123')
            print("Set test AWS Access Key")
        
        print("\nSMS Settings with Credentials Ready!")
        print("Features available:")
        print("• Radio buttons for provider selection (Mock/Twilio/AWS)")
        print("• Phone number input field")
        print("• Twilio credential configuration tab")
        print("• AWS SNS credential configuration tab")
        print("• Test SMS and Status check buttons")
        print("• Automatic credential saving/loading")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error in SMS credentials test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_sms_credentials()
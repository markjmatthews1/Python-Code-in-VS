#!/usr/bin/env python3
"""
Twilio Credential Verification Tool
===================================
This tool helps verify your Twilio credentials are correct and working.
"""

import json
import os
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

def test_twilio_credentials():
    """Test Twilio credentials step by step"""
    print("Twilio Credential Verification Tool")
    print("=" * 50)
    
    # Get credentials from alert system settings
    settings_file = "config/alert_settings.json"
    
    if not os.path.exists(settings_file):
        print("❌ No alert settings file found. Please configure SMS in settings first.")
        return False
    
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
    except Exception as e:
        print(f"❌ Error reading settings file: {e}")
        return False
    
    # Extract Twilio credentials
    account_sid = settings.get('twilio_account_sid', '')
    auth_token = settings.get('twilio_auth_token', '')
    from_number = settings.get('twilio_phone_number', '')
    
    print(f"\n1. Checking saved credentials...")
    print(f"   Account SID: {account_sid[:8]}... (length: {len(account_sid)})")
    print(f"   Auth Token: {'*' * min(8, len(auth_token))}... (length: {len(auth_token)})")
    print(f"   From Number: {from_number}")
    
    # Validate credential format
    if not account_sid or not auth_token:
        print("❌ Missing Account SID or Auth Token")
        return False
    
    if not account_sid.startswith('AC'):
        print("❌ Account SID should start with 'AC'")
        print(f"   Your Account SID starts with: '{account_sid[:2]}'")
        return False
    
    if len(account_sid) != 34:
        print(f"❌ Account SID should be 34 characters long, yours is {len(account_sid)}")
        return False
    
    if len(auth_token) != 32:
        print(f"❌ Auth Token should be 32 characters long, yours is {len(auth_token)}")
        return False
    
    print("✅ Credential format looks correct")
    
    # Test connection to Twilio
    print(f"\n2. Testing connection to Twilio...")
    try:
        client = Client(account_sid, auth_token)
        
        # Try to fetch account info
        print("   Attempting to fetch account information...")
        account = client.api.accounts(account_sid).fetch()
        
        print(f"✅ Successfully connected to Twilio!")
        print(f"   Account Name: {account.friendly_name}")
        print(f"   Account Status: {account.status}")
        
        # Test phone number validation
        if from_number:
            print(f"\n3. Validating phone number: {from_number}")
            try:
                # Get list of owned phone numbers
                phone_numbers = client.incoming_phone_numbers.list()
                
                if phone_numbers:
                    print(f"   Found {len(phone_numbers)} phone number(s) in your account:")
                    for pn in phone_numbers:
                        print(f"   - {pn.phone_number} ({pn.friendly_name})")
                        
                    # Check if our from_number is in the list
                    owned_numbers = [pn.phone_number for pn in phone_numbers]
                    if from_number in owned_numbers:
                        print(f"✅ Phone number {from_number} is verified and owned by your account")
                    else:
                        print(f"❌ Phone number {from_number} is not found in your account")
                        print(f"   Please use one of the numbers listed above")
                        return False
                else:
                    print("❌ No phone numbers found in your Twilio account")
                    print("   You need to purchase a phone number from Twilio console first")
                    return False
                    
            except Exception as e:
                print(f"⚠️  Could not verify phone number: {e}")
        
        return True
        
    except TwilioRestException as e:
        print(f"❌ Twilio API Error: {e}")
        if e.code == 20003:
            print("   This means authentication failed - check your Account SID and Auth Token")
            print("   Please verify these in your Twilio Console:")
            print("   https://console.twilio.com/")
        return False
        
    except Exception as e:
        print(f"❌ Connection Error: {e}")
        return False

def provide_setup_help():
    """Provide step-by-step setup help"""
    print("\n" + "=" * 60)
    print("TWILIO SETUP HELP")
    print("=" * 60)
    print("""
To fix authentication issues, please verify:

1. 📱 LOGIN TO TWILIO CONSOLE
   Go to: https://console.twilio.com/
   Log in with your Twilio account

2. 🔑 GET YOUR CREDENTIALS
   On the dashboard, find:
   - Account SID (starts with 'AC', 34 characters)
   - Auth Token (32 characters, click 'show' to reveal)

3. 📞 GET YOUR PHONE NUMBER
   Go to: Phone Numbers > Manage > Active numbers
   Copy the phone number (format: +1234567890)

4. ✏️  UPDATE SETTINGS
   In the SMS settings tab:
   - Paste Account SID exactly as shown
   - Paste Auth Token exactly as shown  
   - Paste phone number in +1234567890 format
   - Click Save Settings

5. 🧪 TEST AGAIN
   Click "Test SMS" to send a test message

Common Issues:
- ❌ Copied extra spaces or characters
- ❌ Used Account SID instead of Auth Token (or vice versa)
- ❌ Phone number not in correct +1234567890 format
- ❌ Using phone number you don't own in Twilio
""")

if __name__ == "__main__":
    success = test_twilio_credentials()
    
    if not success:
        provide_setup_help()
    else:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"Your Twilio credentials are correctly configured.")
        print(f"SMS functionality should work properly now!")
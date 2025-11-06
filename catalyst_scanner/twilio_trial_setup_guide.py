#!/usr/bin/env python3
"""
Twilio Trial Mode Setup Guide
============================
This guide helps you set up SMS with Twilio trial account.
"""

def print_trial_setup_guide():
    """Print comprehensive trial setup guide"""
    print("🚀 TWILIO TRIAL ACCOUNT SETUP")
    print("=" * 60)
    print("""
OPTION 1: Use Trial Mode (Recommended for Testing)
==================================================

1. 📱 SIGN UP FOR TRIAL:
   - Go to: https://www.twilio.com/try-twilio
   - Sign up with email and phone number
   - Verify your phone number (this becomes your verified number)

2. 🔑 GET TRIAL CREDENTIALS:
   - After signup, go to Console: https://console.twilio.com/
   - Copy your Trial Account SID (starts with 'AC', 34 characters)
   - Copy your Trial Auth Token (32 characters)

3. 📞 USE TRIAL PHONE NUMBER:
   - Twilio provides a trial number automatically
   - OR use the phone number you verified during signup
   - Trial mode can only send to verified numbers

4. ✅ TRIAL LIMITATIONS (But Perfect for Testing):
   - Can only send SMS to verified phone numbers
   - Messages prefixed with "Sent from your Twilio trial account"
   - Limited to a few messages per day
   - Perfect for testing our SMS alerts!

OPTION 2: Bypass Verification Issues
===================================

If you're stuck on verification, try:

1. 🌐 WEBSITE URL WORKAROUNDS:
   - Use: https://github.com/yourusername
   - Use: https://linkedin.com/in/yourprofile  
   - Use: https://example.com (temporary)
   - Use: https://localhost (for development)

2. 📝 BUSINESS INFO:
   - Company: "Personal Project" or "Individual Developer"
   - Use Case: "Personal notification system"
   - Description: "Python application for portfolio alerts"

3. 🏠 ADDRESS:
   - Use your home address
   - Select "Individual/Personal" for business type

OPTION 3: Alternative SMS Providers
==================================

If Twilio verification remains problematic:

1. 📱 TEXTBELT (Simpler Setup):
   - Website: https://textbelt.com/
   - Pay-per-message, no monthly fees
   - No complex verification process

2. 📧 EMAIL ALERTS (Immediate Alternative):
   - We can set up email notifications instead
   - Much easier to configure
   - Works with Gmail, Outlook, etc.

NEXT STEPS:
==========
1. Try Option 1 (Trial Account) - easiest path
2. Let me know which option you prefer
3. I'll help you configure the credentials
""")

def print_trial_credentials_format():
    """Show what trial credentials look like"""
    print("\n" + "=" * 60)
    print("TRIAL CREDENTIALS FORMAT")
    print("=" * 60)
    print("""
Your Twilio trial credentials should look like:

Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (34 chars, starts with AC)
Auth Token:  xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx  (32 chars, random letters/numbers)
Phone Number: +1234567890                       (Your verified number)

Example (not real):
Account SID: AC1234567890abcdef1234567890abcdef
Auth Token:  abcdef1234567890abcdef1234567890
Phone Number: +15551234567

IMPORTANT: 
- Trial accounts can only send to YOUR verified phone number
- Messages will have "trial account" prefix
- Perfect for testing our alerts system!
""")

if __name__ == "__main__":
    print_trial_setup_guide()
    print_trial_credentials_format()
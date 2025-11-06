#!/usr/bin/env python3
"""
Schwab Token Renewal Script
Triggers the authentication popup and renewal process for fresh Schwab tokens
"""

import sys
import os
import time
from datetime import datetime
import json

# Add the main directory to path so we can import Schwab_auth
sys.path.append('c:\\Users\\mjmat\\Python Code in VS')

try:
    from Schwab_auth import (
        load_tokens, 
        refresh_access_token, 
        schwab_auth_popup_and_sound, 
        AUTH_URL,
        ensure_fresh_token,
        debug_token_status
    )
except ImportError as e:
    print(f"❌ Error importing Schwab_auth: {e}")
    print("Make sure Schwab_auth.py is in the correct location")
    sys.exit(1)

def check_token_status():
    """Check current token status and validity"""
    print("🔍 Checking current token status...")
    
    try:
        tokens = load_tokens()
        if not tokens:
            print("❌ No tokens found")
            return False, "No tokens exist"
            
        current_time = time.time()
        expires_at = tokens.get('expires_at', 0)
        
        if expires_at > current_time:
            time_left = expires_at - current_time
            expires_datetime = datetime.fromtimestamp(expires_at)
            print(f"✅ Token is valid until: {expires_datetime}")
            print(f"   Time remaining: {time_left/60:.1f} minutes")
            
            if time_left < 300:  # Less than 5 minutes
                return False, "Token expires soon (less than 5 minutes)"
            else:
                return True, "Token is valid"
        else:
            print("❌ Token has expired")
            return False, "Token has expired"
            
    except Exception as e:
        print(f"❌ Error checking token: {e}")
        return False, f"Error: {e}"

def request_fresh_tokens():
    """Request fresh Schwab tokens"""
    print("🚀 Requesting Fresh Schwab Tokens")
    print("="*50)
    
    # First check current status
    is_valid, status_msg = check_token_status()
    print(f"Current status: {status_msg}")
    
    if is_valid:
        print("\n🤔 Current tokens are still valid.")
        response = input("Do you want to refresh anyway? (y/N): ").lower().strip()
        if response != 'y':
            print("✅ Keeping existing tokens")
            return True
    
    print("\n🔄 Initiating token refresh process...")
    
    try:
        # Try to refresh existing tokens first
        print("📱 Attempting to refresh with existing refresh token...")
        new_tokens = refresh_access_token()
        
        if new_tokens:
            print("✅ Successfully refreshed tokens!")
            check_token_status()  # Show new status
            return True
        else:
            print("⚠️ Refresh failed, need full re-authentication")
            
    except Exception as e:
        print(f"⚠️ Refresh attempt failed: {e}")
    
    # If refresh failed, trigger full authentication
    print("\n🌐 Triggering Schwab authentication popup...")
    print("📋 Instructions:")
    print("1. A popup window will appear")
    print("2. Click 'Open Schwab OAuth URL' to open your browser")
    print("3. Log in to your Schwab account")
    print("4. The browser will redirect back to complete authentication")
    print("5. The popup should close automatically when complete")
    
    try:
        # This will open the popup and start the authentication process
        schwab_auth_popup_and_sound(AUTH_URL)
        
        print("\n⏳ Authentication popup has been triggered...")
        print("💡 Complete the authentication process in the popup window")
        
        # Wait a moment and check if tokens were created
        time.sleep(2)
        
        # Check for completion over the next few minutes
        max_wait = 300  # 5 minutes
        check_interval = 5  # 5 seconds
        waited = 0
        
        while waited < max_wait:
            if os.path.exists("auth_complete.txt") or os.path.exists("tokens.json"):
                time.sleep(1)  # Give it a moment
                is_valid, status = check_token_status()
                if is_valid:
                    print("\n✅ Authentication completed successfully!")
                    # Clean up signal file
                    try:
                        if os.path.exists("auth_complete.txt"):
                            os.remove("auth_complete.txt")
                    except:
                        pass
                    return True
            
            time.sleep(check_interval)
            waited += check_interval
            if waited % 30 == 0:  # Print update every 30 seconds
                print(f"⏳ Still waiting for authentication... ({waited}s elapsed)")
        
        print("⏰ Authentication timeout reached")
        print("💡 If you completed the authentication, tokens may still be valid")
        
        # Final check
        is_valid, status = check_token_status()
        return is_valid
        
    except Exception as e:
        print(f"❌ Error during authentication process: {e}")
        return False

def update_estimated_income_with_fresh_data():
    """Update the Estimated Income sheet with fresh Schwab data"""
    print("\n📊 Updating Estimated Income 2025 with fresh data...")
    
    try:
        # Import our dividend tracker modules
        sys.path.append('c:\\Users\\mjmat\\Python Code in VS\\dividend_tracker\\DividendTrackerApp\\modules')
        
        # This would be where we'd call your existing functions to get fresh account data
        # For now, we'll just note that this is where it would happen
        print("📈 Fresh token available - you can now run:")
        print("   • Portfolio data collection scripts")
        print("   • Dividend estimate calculations")
        print("   • Account balance updates")
        
        return True
        
    except Exception as e:
        print(f"❌ Error updating data: {e}")
        return False

if __name__ == "__main__":
    print("🔐 Schwab Token Renewal Process")
    print("="*40)
    
    # Check if we can import the auth module
    try:
        debug_token_status()
    except:
        print("📋 No existing tokens to debug")
    
    # Request fresh tokens
    success = request_fresh_tokens()
    
    if success:
        print("\n✅ SUCCESS! Fresh Schwab tokens are now available")
        print("🔄 You can now run scripts that require Schwab API access")
        
        # Optionally update data
        response = input("\nWould you like to update portfolio data now? (y/N): ").lower().strip()
        if response == 'y':
            update_estimated_income_with_fresh_data()
            
    else:
        print("\n❌ FAILED to obtain fresh tokens")
        print("💡 You may need to:")
        print("   • Check your internet connection")
        print("   • Verify your Schwab login credentials")
        print("   • Try running this script again")
    
    input("\nPress Enter to exit...")

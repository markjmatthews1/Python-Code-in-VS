#!/usr/bin/env python3
"""Test script for Schwab authentication improvements"""

import os
import time
import json

def test_schwab_auth():
    print("🧪 Testing Schwab Authentication System")
    print("=" * 50)
    
    # Check for existing tokens
    if os.path.exists("tokens.json"):
        print("📋 Current token status:")
        try:
            with open("tokens.json", "r") as f:
                tokens = json.load(f)
            
            if "token_dictionary" in tokens:
                token_dict = tokens["token_dictionary"]
                
                # Check expiration
                if "expires_at" in token_dict:
                    expires_at = token_dict["expires_at"]
                    current_time = time.time()
                    time_remaining = expires_at - current_time
                    
                    print(f"✅ Tokens exist")
                    print(f"🕒 Expires in: {time_remaining/60:.1f} minutes")
                    
                    if time_remaining > 120:  # More than 2 minutes
                        print("✅ Tokens are fresh - no authentication needed")
                        return True
                    else:
                        print("⚠️ Tokens expire soon - may need refresh")
                else:
                    print("⚠️ No expiration info in tokens")
            else:
                print("❌ Invalid token format")
        except Exception as e:
            print(f"❌ Error reading tokens: {e}")
    else:
        print("❌ No token file found")
    
    print("\n🔄 Starting authentication test...")
    print("📝 Instructions:")
    print("1. A popup window will appear")
    print("2. Click 'Open Schwab OAuth URL'")
    print("3. Log into Schwab in your browser")
    print("4. The popup should close automatically")
    print("5. Check that tokens are saved")
    
    # Import and run the auth
    try:
        from Schwab_auth import main
        main()
        
        # Check results
        time.sleep(3)
        if os.path.exists("tokens.json"):
            print("✅ Authentication test completed - tokens saved!")
            return True
        else:
            print("❌ Authentication test failed - no tokens saved")
            return False
            
    except Exception as e:
        print(f"❌ Authentication test error: {e}")
        return False

if __name__ == "__main__":
    test_schwab_auth()

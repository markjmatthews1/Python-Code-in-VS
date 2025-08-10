#!/usr/bin/env python3
"""
Test the improved Schwab authentication system
"""

import sys
import os

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

print("🔐 Testing Improved Schwab Authentication...")
print("="*60)

try:
    from Schwab_auth import main, load_tokens, get_valid_access_token
    
    # Check existing tokens first
    existing_tokens = load_tokens()
    if existing_tokens and "access_token" in existing_tokens:
        print("✅ Existing tokens found. Testing validity...")
        try:
            token = get_valid_access_token()
            if token:
                print("✅ Existing tokens are valid! No new authentication needed.")
                print(f"🎯 Ready to proceed with Schwab API calls.")
                print("\n🚀 Now proceeding with data update...")
            else:
                print("⚠️ Existing tokens are invalid. Starting fresh authentication...")
                result = main()
                if result:
                    print("✅ Fresh authentication successful!")
                else:
                    print("❌ Authentication failed")
        except Exception as e:
            print(f"⚠️ Token validation error: {e}")
            print("🔄 Starting fresh authentication...")
            result = main()
            if result:
                print("✅ Fresh authentication successful!")
            else:
                print("❌ Authentication failed")
    else:
        print("🆕 No existing tokens. Starting authentication...")
        result = main()
        if result:
            print("✅ Authentication successful!")
        else:
            print("❌ Authentication failed")

except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Authentication test complete!")

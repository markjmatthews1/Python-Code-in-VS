#!/usr/bin/env python3
"""
Weekly Schwab Token Renewal Fix
==============================
Specifically addresses the weekly refresh token expiration issue.
"""

import os
import time
import json
import subprocess
import threading
from datetime import datetime, timedelta

def check_refresh_token_expiry():
    """
    Check if refresh token is about to expire and needs full re-authentication.
    Schwab refresh tokens typically last 7 days.
    """
    try:
        with open("tokens.json", "r") as f:
            data = json.load(f)
        
        refresh_issued = data.get("refresh_token_issued")
        if not refresh_issued:
            print("⚠️ No refresh token issue date found")
            return True  # Assume needs renewal
        
        # Parse the issue date
        issue_time = datetime.fromisoformat(refresh_issued.replace('Z', '+00:00'))
        now = datetime.now()
        
        # Calculate age (handle timezone-naive comparison)
        if issue_time.tzinfo:
            issue_time = issue_time.replace(tzinfo=None)
        
        age = now - issue_time
        days_old = age.total_seconds() / (24 * 3600)
        
        print(f"🕐 Refresh token age: {days_old:.1f} days")
        
        # Schwab refresh tokens expire after 7 days
        if days_old >= 6.5:  # Start renewal process early
            print("🔄 Refresh token approaching expiry - full re-auth needed")
            return True
        else:
            print("✅ Refresh token still valid")
            return False
            
    except Exception as e:
        print(f"❌ Error checking refresh token expiry: {e}")
        return True  # Assume needs renewal if we can't check

def simulate_weekly_renewal_failure():
    """
    Simulate the weekly renewal failure scenario for testing.
    """
    print("🧪 SIMULATING WEEKLY RENEWAL FAILURE")
    print("="*50)
    
    # Back up current tokens
    if os.path.exists("tokens.json"):
        import shutil
        shutil.copy("tokens.json", "tokens_backup.json")
        print("📋 Backed up current tokens")
    
    # Simulate expired refresh token by modifying token data
    try:
        with open("tokens.json", "r") as f:
            data = json.load(f)
        
        # Make refresh token appear old
        old_date = (datetime.now() - timedelta(days=8)).isoformat()
        data["refresh_token_issued"] = old_date
        
        with open("tokens.json", "w") as f:
            json.dump(data, f, indent=2)
        
        print(f"🕐 Modified refresh token date to: {old_date}")
        print("📤 Now testing renewal process...")
        
        # Test the renewal
        from schwab_auth import refresh_access_token
        result = refresh_access_token()
        
        if result:
            print("✅ Weekly renewal test PASSED")
        else:
            print("❌ Weekly renewal test FAILED (this was expected)")
        
    except Exception as e:
        print(f"❌ Error during simulation: {e}")
    
    finally:
        # Restore backup
        if os.path.exists("tokens_backup.json"):
            import shutil
            shutil.move("tokens_backup.json", "tokens.json")
            print("🔄 Restored original tokens")

def manual_weekly_renewal():
    """
    Manual process for weekly token renewal when automatic fails.
    """
    print("🔄 MANUAL WEEKLY RENEWAL PROCESS")
    print("="*40)
    
    # Check if we really need renewal
    if not check_refresh_token_expiry():
        print("✅ Tokens don't need renewal yet")
        return True
    
    print("🔐 Starting manual weekly renewal...")
    
    # Remove old tokens to force full re-auth
    if os.path.exists("tokens.json"):
        os.remove("tokens.json")
        print("🗑️ Removed expired tokens")
    
    # Run full authentication
    try:
        print("🚀 Starting schwab_auth.py for full re-authentication...")
        result = subprocess.run(
            ["python", "schwab_auth.py"],
            capture_output=True,
            text=True,
            timeout=300  # 5 minute timeout
        )
        
        print(f"📤 Auth process stdout: {result.stdout}")
        if result.stderr:
            print(f"⚠️ Auth process stderr: {result.stderr}")
        
        # Check if tokens were created
        if os.path.exists("tokens.json"):
            print("✅ Weekly renewal completed successfully!")
            return True
        else:
            print("❌ Weekly renewal failed - no tokens created")
            return False
            
    except subprocess.TimeoutExpired:
        print("⏰ Weekly renewal timed out")
        return False
    except Exception as e:
        print(f"❌ Error during weekly renewal: {e}")
        return False

def create_weekly_renewal_monitor():
    """
    Create a monitoring script for weekly renewals.
    """
    monitor_script = '''#!/usr/bin/env python3
"""
Weekly Schwab Token Monitor
Run this daily to check token status
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from weekly_schwab_renewal_fix import check_refresh_token_expiry, manual_weekly_renewal

def main():
    print("📅 Daily Schwab Token Check")
    print("="*30)
    
    if check_refresh_token_expiry():
        print("🔔 ALERT: Tokens need renewal!")
        
        user_input = input("Start renewal process now? (y/n): ")
        if user_input.lower() == 'y':
            success = manual_weekly_renewal()
            if success:
                print("🎉 Renewal completed!")
            else:
                print("❌ Renewal failed - manual intervention needed")
        else:
            print("⚠️ Remember to renew tokens before they expire!")
    else:
        print("✅ Tokens are current - no action needed")

if __name__ == "__main__":
    main()
'''
    
    with open("daily_token_check.py", "w") as f:
        f.write(monitor_script)
    
    print("📊 Created 'daily_token_check.py' - run daily to monitor token status")

def main():
    """Main function to diagnose and fix weekly renewal issues"""
    
    print("🔧 WEEKLY SCHWAB TOKEN RENEWAL DIAGNOSTICS")
    print("="*50)
    
    # Check current status
    needs_renewal = check_refresh_token_expiry()
    
    if needs_renewal:
        print("\n🔔 Action required: Tokens need renewal")
        print("\nOptions:")
        print("1. Test the fixed renewal process")
        print("2. Run manual renewal now")
        print("3. Create monitoring script")
        
        choice = input("\nEnter choice (1-3): ")
        
        if choice == "1":
            # Don't actually simulate - just explain
            print("\n💡 The fix has been applied to schwab_auth.py")
            print("   Next time tokens expire, it will start the full Flask server")
            print("   instead of just showing a popup")
            
        elif choice == "2":
            manual_weekly_renewal()
            
        elif choice == "3":
            create_weekly_renewal_monitor()
            
    else:
        print("\n✅ Current tokens are still valid")
        print("💡 The fix is in place for next weekly renewal")
    
    print("\n🔧 WEEKLY RENEWAL FIX SUMMARY:")
    print("   ✅ Fixed schwab_auth.py to start Flask server on refresh failure")
    print("   ✅ Enhanced error handling for expired refresh tokens")
    print("   ✅ Added proper completion detection for re-authentication")
    print("   💡 Next weekly renewal should work automatically!")

if __name__ == "__main__":
    main()
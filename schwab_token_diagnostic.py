"""
Schwab Token Diagnostic - Check current token status and refresh if needed
"""
import json
import time
from datetime import datetime
import requests

def diagnose_schwab_tokens():
    print("🔍 SCHWAB TOKEN DIAGNOSTIC")
    print("=" * 50)
    
    # Check if tokens.json exists
    try:
        with open("tokens.json", "r") as f:
            token_data = json.load(f)
        print("✅ tokens.json file found")
    except FileNotFoundError:
        print("❌ tokens.json file not found!")
        print("   Need to run Schwab authentication script")
        return False
    
    # Extract token information
    token_dict = token_data.get("token_dictionary", {})
    access_token = token_dict.get("access_token")
    refresh_token = token_dict.get("refresh_token")
    expires_at = token_dict.get("expires_at")
    expires_in = token_dict.get("expires_in", 1800)  # Default 30 minutes
    
    # Show token info
    print(f"📋 TOKEN INFORMATION:")
    print(f"   Access token: {access_token[:20]}...{access_token[-10:] if access_token else 'None'}")
    print(f"   Refresh token: {refresh_token[:20]}...{refresh_token[-10:] if refresh_token else 'None'}")
    print(f"   Expires at: {expires_at}")
    print(f"   Expires in: {expires_in} seconds")
    
    # Check token timestamps
    issued_time = token_data.get("access_token_issued")
    print(f"   Issued: {issued_time}")
    
    # Calculate actual expiration
    if issued_time:
        try:
            issued_dt = datetime.fromisoformat(issued_time.replace('Z', '+00:00'))
            issued_timestamp = issued_dt.timestamp()
            calculated_expires_at = issued_timestamp + expires_in
            
            print(f"📅 TIMESTAMP ANALYSIS:")
            print(f"   Issued timestamp: {issued_timestamp}")
            print(f"   Calculated expires at: {calculated_expires_at}")
            print(f"   Stored expires at: {expires_at}")
            print(f"   Current timestamp: {time.time()}")
            
            # Check if expired
            current_time = time.time()
            if current_time > calculated_expires_at:
                print("🚨 TOKEN EXPIRED!")
                print(f"   Expired {(current_time - calculated_expires_at)/60:.1f} minutes ago")
                expired = True
            else:
                remaining = (calculated_expires_at - current_time) / 60
                print(f"✅ Token valid for {remaining:.1f} more minutes")
                expired = False
                
        except Exception as e:
            print(f"❌ Error parsing timestamps: {e}")
            expired = True
    else:
        print("❌ No issued time found - assuming expired")
        expired = True
    
    # Test token with a simple API call
    if access_token:
        print(f"\n🧪 TESTING TOKEN WITH API CALL:")
        try:
            headers = {"Authorization": f"Bearer {access_token}"}
            # Test with a simple endpoint
            test_url = "https://api.schwab.com/marketdata/v1/markets"
            response = requests.get(test_url, headers=headers, timeout=10)
            
            print(f"   API Response: {response.status_code}")
            if response.status_code == 200:
                print("✅ Token works! API call successful")
                return True
            elif response.status_code == 401:
                print("🚨 401 Unauthorized - Token is invalid/expired")
                expired = True
            else:
                print(f"⚠️ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ API test failed: {e}")
    
    if expired:
        print(f"\n🔧 RECOMMENDED ACTIONS:")
        print("   1. Run token refresh script")
        print("   2. If refresh fails, run full re-authentication")
        print("   3. Check Schwab credentials and redirect URI")
        print("   4. Verify ngrok tunnel is running if needed")
        return False
    
    return True

def refresh_schwab_token():
    """Attempt to refresh the Schwab token"""
    print("\n🔄 ATTEMPTING TOKEN REFRESH...")
    
    try:
        with open("tokens.json", "r") as f:
            token_data = json.load(f)
    except:
        print("❌ Cannot load tokens.json for refresh")
        return False
    
    token_dict = token_data.get("token_dictionary", {})
    refresh_token = token_dict.get("refresh_token")
    
    if not refresh_token:
        print("❌ No refresh token available")
        return False
    
    # Schwab token refresh endpoint
    refresh_url = "https://api.schwab.com/v1/oauth/token"
    refresh_data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token
    }
    
    # Add client credentials (you'll need to provide these)
    CLIENT_ID = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"  # Replace with actual
    CLIENT_SECRET = "your_client_secret"  # Replace with actual
    
    import base64
    credentials = base64.b64encode(f"{CLIENT_ID}:{CLIENT_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {credentials}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    try:
        response = requests.post(refresh_url, data=refresh_data, headers=headers, timeout=10)
        print(f"   Refresh response: {response.status_code}")
        
        if response.status_code == 200:
            new_tokens = response.json()
            print("✅ Token refresh successful!")
            
            # Update tokens.json
            token_data["token_dictionary"].update(new_tokens)
            token_data["access_token_issued"] = datetime.now().isoformat()
            token_data["refresh_token_issued"] = datetime.now().isoformat()
            
            # Fix expires_at calculation
            expires_in = new_tokens.get("expires_in", 1800)
            token_data["token_dictionary"]["expires_at"] = time.time() + expires_in
            
            with open("tokens.json", "w") as f:
                json.dump(token_data, f, indent=2)
            
            print("✅ tokens.json updated with new tokens")
            return True
        else:
            print(f"❌ Refresh failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Refresh error: {e}")
        return False

if __name__ == "__main__":
    is_valid = diagnose_schwab_tokens()
    
    if not is_valid:
        print("\n" + "="*50)
        print("🔧 ATTEMPTING AUTOMATIC TOKEN REFRESH...")
        refresh_success = refresh_schwab_token()
        
        if refresh_success:
            print("\n" + "="*50)
            print("🧪 RE-TESTING AFTER REFRESH...")
            diagnose_schwab_tokens()
        else:
            print("\n" + "="*50)
            print("🚨 MANUAL INTERVENTION REQUIRED")
            print("   Need to run full Schwab authentication flow")
            print("   Check Schwab_auth.py or Aristo_simple_Schwab_auth.py")

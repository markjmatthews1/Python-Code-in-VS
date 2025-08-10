"""
Simple Schwab Auth Test - Check current status and fix tokens
"""
import json
import time
import requests
import base64
from datetime import datetime

def test_schwab_current_status():
    print("🔍 SCHWAB AUTHENTICATION STATUS CHECK")
    print("=" * 50)
    
    # Load current tokens
    try:
        with open("tokens.json", "r") as f:
            token_data = json.load(f)
        print("✅ tokens.json found")
    except FileNotFoundError:
        print("❌ tokens.json not found!")
        print("   Run: python Schwab_auth.py")
        return
    
    # Extract token info
    token_dict = token_data.get("token_dictionary", {})
    access_token = token_dict.get("access_token")
    refresh_token = token_dict.get("refresh_token")
    expires_at = token_dict.get("expires_at")
    
    print(f"📋 CURRENT TOKEN STATUS:")
    print(f"   Access token exists: {'✅' if access_token else '❌'}")
    print(f"   Refresh token exists: {'✅' if refresh_token else '❌'}")
    print(f"   Expires at: {expires_at}")
    
    # Check if expired
    if expires_at:
        now = time.time()
        if now > expires_at:
            print(f"🚨 TOKEN EXPIRED {(now - expires_at)/60:.1f} minutes ago")
        else:
            print(f"✅ Token valid for {(expires_at - now)/60:.1f} more minutes")
    
    # Test with API call
    if access_token:
        print(f"\n🧪 TESTING API CALL...")
        headers = {"Authorization": f"Bearer {access_token}"}
        test_url = "https://api.schwabapi.com/marketdata/v1/quotes?symbols=AAPL"
        
        try:
            response = requests.get(test_url, headers=headers, timeout=10)
            print(f"   Response code: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ API CALL SUCCESSFUL!")
                data = response.json()
                print(f"   AAPL data received: {len(data)} keys")
                return True
            elif response.status_code == 401:
                print("🚨 401 UNAUTHORIZED - Token invalid")
                print(f"   Response: {response.text}")
                return False
            else:
                print(f"⚠️ Unexpected response: {response.status_code}")
                print(f"   Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ API call failed: {e}")
            return False
    
    return False

def attempt_token_refresh():
    print(f"\n🔄 ATTEMPTING TOKEN REFRESH...")
    
    try:
        with open("tokens.json", "r") as f:
            token_data = json.load(f)
    except:
        print("❌ Cannot load tokens.json")
        return False
    
    token_dict = token_data.get("token_dictionary", {})
    refresh_token = token_dict.get("refresh_token")
    
    if not refresh_token:
        print("❌ No refresh token available")
        return False
    
    # Schwab credentials from the auth file
    APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
    APP_SECRET = "h9YybKHnDVoDM1Jw"
    TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
    
    auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": APP_KEY
    }
    
    try:
        response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=10)
        print(f"   Refresh response: {response.status_code}")
        
        if response.status_code == 200:
            new_tokens = response.json()
            print("✅ TOKEN REFRESH SUCCESSFUL!")
            
            # Update tokens.json
            token_data["token_dictionary"].update(new_tokens)
            token_data["access_token_issued"] = datetime.now().isoformat()
            token_data["refresh_token_issued"] = datetime.now().isoformat()
            
            # Fix expires_at calculation
            expires_in = new_tokens.get("expires_in", 1800)
            token_data["token_dictionary"]["expires_at"] = time.time() + expires_in
            
            with open("tokens.json", "w") as f:
                json.dump(token_data, f, indent=2)
            
            print("✅ tokens.json updated")
            return True
        else:
            print(f"❌ Refresh failed: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Refresh error: {e}")
        return False

if __name__ == "__main__":
    # Test current status
    is_working = test_schwab_current_status()
    
    if not is_working:
        print("\n" + "="*50)
        print("🔧 ATTEMPTING TOKEN REFRESH...")
        refresh_success = attempt_token_refresh()
        
        if refresh_success:
            print("\n" + "="*50)
            print("🧪 RE-TESTING AFTER REFRESH...")
            test_schwab_current_status()
        else:
            print("\n" + "="*50)
            print("🚨 MANUAL RE-AUTHENTICATION REQUIRED")
            print("   Run: python Schwab_auth.py")
            print("   This will open a browser for OAuth login")
            print("   Make sure SSL certificates are in place")
    else:
        print("\n✅ SCHWAB AUTHENTICATION IS WORKING CORRECTLY!")
        print("   The data issue must be elsewhere in the pipeline")

#!/usr/bin/env python3
"""
Quick Schwab Token Refresh
==========================
Uses the working Schwab balance script logic to refresh tokens and then test positions.
"""
import sys
import os
import json
import requests
import base64
from datetime import datetime

# Add main directory to path
main_dir = r"c:\Users\mjmat\Python Code in VS"
sys.path.append(main_dir)

try:
    from Schwab_auth import APP_KEY, APP_SECRET, TOKEN_URL
    TOKEN_FILE = os.path.join(main_dir, "tokens.json")
    print("✅ Using Schwab_auth module")
except ImportError:
    # Fallback credentials
    APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
    APP_SECRET = "h9YybKHnDVoDM1Jw" 
    TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
    TOKEN_FILE = os.path.join(main_dir, "tokens.json")
    print("⚠️ Using fallback Schwab credentials")

def load_tokens():
    """Load tokens from main directory"""
    try:
        if not os.path.exists(TOKEN_FILE):
            print(f"❌ Token file not found: {TOKEN_FILE}")
            return None
            
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
        
        token_dict = data.get('token_dictionary', {})
        access_token = token_dict.get('access_token')
        refresh_token = token_dict.get('refresh_token')
        expires_at = token_dict.get('expires_at', 0)
        
        if not access_token:
            print("❌ No access token found in token file")
            return None
            
        print(f"✅ Tokens loaded from: {TOKEN_FILE}")
        print(f"🕐 Token expires at: {datetime.fromtimestamp(expires_at)}")
        
        return {
            'access_token': access_token,
            'refresh_token': refresh_token,
            'expires_at': expires_at
        }
        
    except Exception as e:
        print(f"❌ Error loading tokens: {e}")
        return None

def is_token_expired(tokens):
    """Check if access token is expired"""
    try:
        expires_at = tokens.get('expires_at', 0)
        current_time = datetime.now().timestamp()
        
        # Consider expired if within 5 minutes of expiration
        buffer_time = 300  # 5 minutes
        
        is_expired = current_time >= (expires_at - buffer_time)
        
        if is_expired:
            print("⏰ Access token is expired or will expire soon")
        else:
            remaining = expires_at - current_time
            print(f"✅ Access token valid for {remaining/60:.1f} more minutes")
            
        return is_expired
        
    except Exception as e:
        print(f"⚠️ Error checking token expiration: {e}")
        return True  # Assume expired on error

def refresh_access_token(tokens):
    """Refresh the access token using OAuth2 refresh token"""
    try:
        print("🔄 Refreshing access token...")
        
        # Prepare refresh request
        auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
        
        headers = {
            'Authorization': f'Basic {auth_header}',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': tokens['refresh_token']
        }
        
        response = requests.post(TOKEN_URL, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            token_data = response.json()
            
            # Update tokens
            new_expires_at = datetime.now().timestamp() + token_data.get('expires_in', 1800)
            
            updated_tokens = {
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', tokens['refresh_token']),
                'expires_at': new_expires_at
            }
            
            # Save updated tokens
            save_tokens(updated_tokens, token_data)
            
            print("✅ Access token refreshed successfully")
            return updated_tokens
            
        else:
            print(f"❌ Token refresh failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error refreshing token: {e}")
        return None

def save_tokens(tokens, full_token_data):
    """Save updated tokens to tokens.json"""
    try:
        # Load existing token file to preserve structure
        with open(TOKEN_FILE, 'r') as f:
            existing_data = json.load(f)
        
        # Update with new token data
        existing_data['token_dictionary'].update({
            'access_token': tokens['access_token'],
            'refresh_token': tokens['refresh_token'],
            'expires_at': tokens['expires_at'],
            'expires_in': full_token_data.get('expires_in', 1800)
        })
        
        # Update timestamps
        existing_data['access_token_issued'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
        
        # Save back to file
        with open(TOKEN_FILE, 'w') as f:
            json.dump(existing_data, f, indent=2)
            
        print("💾 Updated tokens saved successfully")
        
    except Exception as e:
        print(f"❌ Error saving tokens: {e}")

def test_schwab_positions():
    """Test Schwab positions after token refresh"""
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
        from portfolio_data_collector import PortfolioDataCollector
        
        collector = PortfolioDataCollector()
        result = collector.get_schwab_positions_by_account()
        
        ira_count = len(result.get('schwab_ira', []))
        individual_count = len(result.get('schwab_individual', []))
        
        print(f"🎯 SCHWAB POSITIONS TEST RESULTS:")
        print(f"   IRA positions: {ira_count}")
        print(f"   Individual positions: {individual_count}")
        print(f"   Total: {ira_count + individual_count}")
        
        return ira_count + individual_count > 0
        
    except Exception as e:
        print(f"❌ Error testing Schwab positions: {e}")
        return False

def main():
    """Main execution function"""
    print("🔄 SCHWAB TOKEN REFRESH & POSITION TEST")
    print("=" * 50)
    
    # Load tokens
    tokens = load_tokens()
    if not tokens:
        print("❌ Cannot proceed without tokens")
        return False
        
    # Check if token needs refresh
    if is_token_expired(tokens):
        tokens = refresh_access_token(tokens)
        if not tokens:
            print("❌ Cannot proceed without valid access token")
            return False
    
    # Test Schwab positions
    print("\n📊 Testing Schwab positions...")
    success = test_schwab_positions()
    
    if success:
        print("✅ Schwab positions working!")
        return True
    else:
        print("❌ Schwab positions still not working")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 SCHWAB TOKEN REFRESH SUCCESSFUL!")
    else:
        print("\n❌ SCHWAB TOKEN REFRESH FAILED!")
    
    input("Press Enter to continue...")

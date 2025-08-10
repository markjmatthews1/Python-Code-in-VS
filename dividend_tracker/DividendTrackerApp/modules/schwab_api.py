"""
Schwab API Integration Module
Author: Mark
Created: July 26, 2025
Purpose: Integrate with Charles Schwab API for automated portfolio tracking
Location: C:\Python_Projects\DividendTrackerApp\modules\schwab_api.py
"""

import os
import json
import requests
from datetime import datetime, timedelta
import configparser

class SchwabAPI:
    """Charles Schwab API integration for portfolio tracking"""
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.config.read(self.config_path)
        
        # Schwab API endpoints
        self.base_url = "https://api.schwabapi.com"
        self.auth_url = "https://api.schwabapi.com/oauth/authorize"
        self.token_url = "https://api.schwabapi.com/oauth/token"
        
        # API credentials (to be added to config.ini)
        self.client_id = self.config.get('SCHWAB_API', 'CLIENT_ID', fallback=None)
        self.client_secret = self.config.get('SCHWAB_API', 'CLIENT_SECRET', fallback=None)
        self.redirect_uri = self.config.get('SCHWAB_API', 'REDIRECT_URI', fallback='https://localhost:8080/callback')
        
        self.session = None
        self.access_token = None
        self.refresh_token = None
        
        # Token storage
        self.token_file = os.path.join(os.path.dirname(__file__), '..', 'schwab_tokens.json')
    
    def setup_config(self):
        """Setup Schwab API configuration in config.ini"""
        if not self.config.has_section('SCHWAB_API'):
            self.config.add_section('SCHWAB_API')
        
        # Add placeholder values
        if not self.client_id:
            self.config.set('SCHWAB_API', 'CLIENT_ID', 'your_schwab_client_id_here')
        if not self.client_secret:
            self.config.set('SCHWAB_API', 'CLIENT_SECRET', 'your_schwab_client_secret_here')
        if not self.config.has_option('SCHWAB_API', 'REDIRECT_URI'):
            self.config.set('SCHWAB_API', 'REDIRECT_URI', 'https://localhost:8080/callback')
        
        # Write back to config file
        with open(self.config_path, 'w') as f:
            self.config.write(f)
        
        print("📝 Schwab API configuration added to config.ini")
        print("Please update with your actual Schwab API credentials")
    
    def load_tokens(self):
        """Load stored access tokens"""
        try:
            if os.path.exists(self.token_file):
                with open(self.token_file, 'r') as f:
                    token_data = json.load(f)
                    self.access_token = token_data.get('access_token')
                    self.refresh_token = token_data.get('refresh_token')
                    
                    # Check if token is still valid
                    expires_at = token_data.get('expires_at')
                    if expires_at and datetime.now() < datetime.fromtimestamp(expires_at):
                        print("✅ Using stored Schwab access token")
                        return True
                    else:
                        print("⚠️ Schwab token expired, need to refresh")
                        return self.refresh_access_token()
            return False
        except Exception as e:
            print(f"❌ Error loading Schwab tokens: {e}")
            return False
    
    def save_tokens(self, access_token, refresh_token, expires_in=3600):
        """Save access tokens to file"""
        try:
            token_data = {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': (datetime.now() + timedelta(seconds=expires_in)).timestamp(),
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.token_file, 'w') as f:
                json.dump(token_data, f, indent=2)
            
            self.access_token = access_token
            self.refresh_token = refresh_token
            print("💾 Schwab tokens saved successfully")
            
        except Exception as e:
            print(f"❌ Error saving Schwab tokens: {e}")
    
    def authenticate(self):
        """Start OAuth authentication flow"""
        if not self.client_id or self.client_id == 'your_schwab_client_id_here':
            print("❌ Schwab API credentials not configured")
            print("Please update config.ini with your Schwab API credentials")
            print("Get them from: https://developer.schwab.com/")
            return False
        
        # Try to load existing tokens first
        if self.load_tokens():
            return True
        
        # Start OAuth flow
        auth_params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'readonly'
        }
        
        auth_url = f"{self.auth_url}?" + "&".join([f"{k}={v}" for k, v in auth_params.items()])
        
        print("🔐 Schwab OAuth Authentication Required")
        print(f"Please visit: {auth_url}")
        print("After authorization, paste the authorization code here:")
        
        auth_code = input("Authorization code: ").strip()
        
        return self.exchange_code_for_token(auth_code)
    
    def exchange_code_for_token(self, auth_code):
        """Exchange authorization code for access token"""
        try:
            token_data = {
                'grant_type': 'authorization_code',
                'code': auth_code,
                'redirect_uri': self.redirect_uri,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.token_url, data=token_data)
            
            if response.status_code == 200:
                token_response = response.json()
                self.save_tokens(
                    token_response['access_token'],
                    token_response.get('refresh_token'),
                    token_response.get('expires_in', 3600)
                )
                return True
            else:
                print(f"❌ Token exchange failed: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error exchanging authorization code: {e}")
            return False
    
    def refresh_access_token(self):
        """Refresh the access token using refresh token"""
        if not self.refresh_token:
            print("❌ No refresh token available")
            return False
        
        try:
            refresh_data = {
                'grant_type': 'refresh_token',
                'refresh_token': self.refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret
            }
            
            response = requests.post(self.token_url, data=refresh_data)
            
            if response.status_code == 200:
                token_response = response.json()
                self.save_tokens(
                    token_response['access_token'],
                    token_response.get('refresh_token', self.refresh_token),
                    token_response.get('expires_in', 3600)
                )
                return True
            else:
                print(f"❌ Token refresh failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error refreshing token: {e}")
            return False
    
    def get_session(self):
        """Get authenticated session"""
        if not self.access_token:
            if not self.authenticate():
                return None
        
        if not self.session:
            self.session = requests.Session()
            self.session.headers.update({
                'Authorization': f'Bearer {self.access_token}',
                'Content-Type': 'application/json'
            })
        
        return self.session
    
    def get_accounts(self):
        """Get list of Schwab accounts"""
        session = self.get_session()
        if not session:
            return []
        
        try:
            response = session.get(f"{self.base_url}/trader/v1/accounts")
            
            if response.status_code == 200:
                accounts = response.json()
                print(f"📊 Found {len(accounts)} Schwab accounts")
                return accounts
            else:
                print(f"❌ Error getting accounts: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching Schwab accounts: {e}")
            return []
    
    def get_account_positions(self, account_hash):
        """Get positions for a specific account"""
        session = self.get_session()
        if not session:
            return []
        
        try:
            response = session.get(f"{self.base_url}/trader/v1/accounts/{account_hash}/positions")
            
            if response.status_code == 200:
                positions = response.json()
                return positions.get('positions', [])
            else:
                print(f"❌ Error getting positions: {response.status_code} - {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error fetching positions: {e}")
            return []
    
    def get_portfolio_values(self):
        """Get current portfolio values from all Schwab accounts"""
        accounts = self.get_accounts()
        if not accounts:
            return {}
        
        portfolio_values = {}
        
        for account in accounts:
            account_hash = account.get('hashValue', '')
            account_type = account.get('type', '')
            
            # Get account balance
            session = self.get_session()
            try:
                balance_response = session.get(f"{self.base_url}/trader/v1/accounts/{account_hash}")
                
                if balance_response.status_code == 200:
                    account_data = balance_response.json()
                    balance_info = account_data.get('currentBalances', {})
                    market_value = balance_info.get('liquidationValue', 0)
                    
                    # Map account types to our naming convention
                    if 'IRA' in account_type.upper():
                        portfolio_values['Schwab IRA'] = float(market_value)
                    else:
                        portfolio_values['Schwab Individual'] = float(market_value)
                    
                    print(f"📊 Schwab {account_type}: ${market_value:,.2f}")
                
            except Exception as e:
                print(f"❌ Error getting account balance for {account_type}: {e}")
        
        return portfolio_values

def test_schwab_api():
    """Test Schwab API integration"""
    print("🧪 Testing Schwab API Integration")
    print("=" * 50)
    
    api = SchwabAPI()
    
    # Setup configuration if needed
    if not api.client_id:
        api.setup_config()
        print("⚠️ Please configure Schwab API credentials in config.ini")
        return
    
    # Test authentication
    if api.authenticate():
        print("✅ Schwab authentication successful")
        
        # Test getting portfolio values
        portfolio_values = api.get_portfolio_values()
        
        if portfolio_values:
            print("\n💰 Schwab Portfolio Values:")
            total = 0
            for account, value in portfolio_values.items():
                print(f"  {account}: ${value:,.2f}")
                total += value
            print(f"  Total Schwab: ${total:,.2f}")
        else:
            print("❌ No portfolio values retrieved")
    else:
        print("❌ Schwab authentication failed")

if __name__ == "__main__":
    test_schwab_api()

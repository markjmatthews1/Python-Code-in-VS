"""
Schwab API Integration Module

Author: Mark
Date: July 26, 2025
Purpose: Integrate with Charles Schwab API for automated portfolio tracking using existing Schwab_auth.py
Location: C:\Python_Projects\DividendTrackerApp\modules\schwab_api_integrated.py
"""

import os
import configparser
import requests
import json
import time
from datetime import datetime

# Import existing Schwab authentication with full auto-renewal capabilities
try:
    from modules.Schwab_auth import (
        get_valid_access_token, 
        load_tokens, 
        fetch_batch_quotes,
        ensure_fresh_token,
        refresh_access_token
    )
    SCHWAB_AUTH_AVAILABLE = True
except ImportError:
    print("❌ Error: Schwab_auth.py not available - this module requires your working Schwab authentication")
    SCHWAB_AUTH_AVAILABLE = False

class SchwabAPI:
    """Charles Schwab API integration with automatic token management"""
    
    def __init__(self):
        # Load configuration
        config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
        self.config = configparser.ConfigParser()
        self.config.read(config_path)
        
        # Schwab API endpoints - using correct account API endpoints
        self.base_url = "https://api.schwabapi.com"
        self.accounts_url = f"{self.base_url}/trader/v1/accounts"
        self.marketdata_url = f"{self.base_url}/marketdata/v1"
        
        # Get credentials from config
        self.client_id = self.config.get('SCHWAB_API', 'CLIENT_ID', fallback=None)
        self.client_secret = self.config.get('SCHWAB_API', 'CLIENT_SECRET', fallback=None)
        
        if not SCHWAB_AUTH_AVAILABLE:
            raise ImportError("Schwab_auth.py module is required for automatic token management")
        
        print(f"🔑 Schwab API initialized with automatic token management")
    
    def _get_authenticated_headers(self):
        """Get headers with fresh access token, automatically handling renewal"""
        try:
            # This will automatically refresh tokens if needed or trigger re-auth if expired
            access_token = get_valid_access_token()
            return {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        except RuntimeError as e:
            print(f"🔐 Token authentication required: {e}")
            # The Schwab_auth system will automatically handle popup/browser auth
            # Let's try one more time after potential auth
            try:
                access_token = get_valid_access_token()
                return {
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/json"
                }
            except Exception as retry_error:
                raise Exception(f"Failed to get valid Schwab token: {retry_error}")
    
    def get_account_numbers(self):
        """Get all account numbers from Schwab using correct API endpoint"""
        try:
            headers = self._get_authenticated_headers()
            
            # Use the correct accounts endpoint
            response = requests.get(self.accounts_url, headers=headers)
            
            if response.status_code == 401:
                print("🔄 Token expired during request, refreshing and retrying...")
                refresh_access_token()
                headers = self._get_authenticated_headers()
                response = requests.get(self.accounts_url, headers=headers)
            
            print(f"📡 Schwab Accounts API Status: {response.status_code}")
            print(f"📡 Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                accounts_data = response.json()
                print(f"📊 Raw accounts response: {accounts_data}")
                
                # Parse account structure and look for all possible ID fields
                accounts = []
                if isinstance(accounts_data, list):
                    for account in accounts_data:
                        # Extract account info from the actual Schwab structure
                        securities_account = account.get('securitiesAccount', account)
                        
                        # Get all possible ID fields for debugging
                        account_number = securities_account.get('accountNumber', '')
                        account_hash = securities_account.get('hashValue', '')
                        encrypted_id = securities_account.get('accountId', '')
                        account_type = securities_account.get('type', 'Unknown')
                        
                        print(f"🔍 Account details - Number: {account_number}, Hash: {account_hash}, ID: {encrypted_id}, Type: {account_type}")
                        
                        # Use the hash value if available, otherwise account number
                        account_id_to_use = account_hash if account_hash else (encrypted_id if encrypted_id else account_number)
                        
                        accounts.append({
                            'accountNumber': account_id_to_use,  # Use proper ID for API calls
                            'displayNumber': account_number,     # Keep display number for logging
                            'type': account_type
                        })
                
                print(f"✅ Retrieved {len(accounts)} Schwab accounts")
                for acc in accounts:
                    display_num = acc.get('displayNumber', acc['accountNumber'])
                    print(f"  - Account: {display_num[-4:] if display_num else 'N/A'}**** ({acc['type']})")
                
                return accounts
            else:
                print(f"❌ Failed to get accounts: {response.status_code}")
                print(f"❌ Response text: {response.text}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting Schwab accounts: {e}")
            return []
    
    def get_account_balance(self, account_number, display_number=None):
        """Get account balance with correct Schwab API endpoint and proper account ID"""
        try:
            headers = self._get_authenticated_headers()
            
            # Use correct account details endpoint with proper ID
            account_url = f"{self.accounts_url}/{account_number}"
            response = requests.get(account_url, headers=headers)
            
            if response.status_code == 401:
                print("🔄 Token expired during balance request, refreshing...")
                refresh_access_token()
                headers = self._get_authenticated_headers()
                response = requests.get(account_url, headers=headers)
            
            display_num = display_number or account_number
            print(f"📡 Account Balance API Status: {response.status_code} for {display_num[-4:] if display_num else 'N/A'}****")
            
            if response.status_code == 200:
                account_data = response.json()
                print(f"📊 Full account data: {account_data}")
                
                # Parse balance based on actual Schwab API structure
                balance = 0.0
                
                # Extract from the securities account structure
                if 'securitiesAccount' in account_data:
                    securities = account_data['securitiesAccount']
                    print(f"📊 Securities account keys: {list(securities.keys())}")
                    
                    # Try current balances first
                    if 'currentBalances' in securities:
                        current_bal = securities['currentBalances']
                        print(f"📊 Current balances: {current_bal}")
                        balance = current_bal.get('totalMarketValue', 0.0)
                        if balance == 0.0:
                            balance = current_bal.get('liquidationValue', 0.0)
                    
                    # Fallback to projected balances
                    if balance == 0.0 and 'projectedBalances' in securities:
                        projected_bal = securities['projectedBalances']
                        print(f"📊 Projected balances: {projected_bal}")
                        balance = projected_bal.get('totalMarketValue', 0.0)
                        if balance == 0.0:
                            balance = projected_bal.get('liquidationValue', 0.0)
                
                # Direct balance fields
                elif 'totalMarketValue' in account_data:
                    balance = account_data['totalMarketValue']
                elif 'liquidationValue' in account_data:
                    balance = account_data['liquidationValue']
                
                print(f"💰 Account {display_num[-4:] if display_num else 'N/A'}****: ${balance:,.2f}")
                return balance
            else:
                print(f"❌ Failed to get balance for {display_num[-4:] if display_num else 'N/A'}****: {response.status_code}")
                print(f"❌ Response: {response.text}")
                return 0.0
                
        except Exception as e:
            display_num = display_number or account_number
            print(f"❌ Error getting balance for {display_num[-4:] if display_num else 'N/A'}****: {e}")
            return 0.0
    
    def get_account_positions(self, account_number):
        """Get detailed account positions for dividend analysis"""
        try:
            headers = self._get_authenticated_headers()
            url = f"{self.base_url}/trader/v1/accounts/{account_number}/positions"
            response = requests.get(url, headers=headers)
            
            if response.status_code == 401:
                print("🔄 Token expired during positions request, refreshing...")
                refresh_access_token()
                headers = self._get_authenticated_headers()
                response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                positions_data = response.json()
                positions = positions_data.get('securitiesAccount', {}).get('positions', [])
                print(f"📊 Retrieved {len(positions)} positions for account {account_number}")
                return positions
            else:
                print(f"❌ Failed to get positions for {account_number}: {response.status_code}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting positions for {account_number}: {e}")
            return []
    
    def get_portfolio_values(self):
        """Get current portfolio values for all Schwab accounts using accounts list data"""
        try:
            # Ensure we have fresh tokens before starting
            ensure_fresh_token(buffer_seconds=300)  # 5-minute buffer
            
            # Get accounts with balance data included
            headers = self._get_authenticated_headers()
            
            # Request accounts with fields parameter to get balance data
            accounts_url_with_fields = f"{self.accounts_url}?fields=positions"
            response = requests.get(accounts_url_with_fields, headers=headers)
            
            if response.status_code != 200:
                # Fallback to basic accounts call
                response = requests.get(self.accounts_url, headers=headers)
            
            if response.status_code != 200:
                raise Exception(f"Failed to get Schwab accounts: {response.status_code}")
            
            accounts_data = response.json()
            print(f"📊 Full accounts data with balances: {accounts_data}")
            
            portfolio_values = {}
            total_value = 0
            
            if isinstance(accounts_data, list):
                for account in accounts_data:
                    securities_account = account.get('securitiesAccount', account)
                    
                    # Extract balance directly from accounts response
                    balance = 0.0
                    account_type = securities_account.get('type', 'Unknown')
                    account_number = securities_account.get('accountNumber', '')
                    
                    # Try to get balance from current balances in the accounts response
                    if 'currentBalances' in securities_account:
                        current_bal = securities_account['currentBalances']
                        balance = current_bal.get('totalMarketValue', 0.0)
                        if balance == 0.0:
                            balance = current_bal.get('liquidationValue', 0.0)
                        print(f"💰 Found balance in accounts response: {account_number[-4:]}**** = ${balance:,.2f}")
                    
                    # If balance found, categorize the account
                    if balance > 0:
                        total_value += balance
                        
                        # Map account types - since both are MARGIN, use account number or balance to differentiate
                        account_number = securities_account.get('accountNumber', '')
                        
                        # Use account number patterns or balance amounts to differentiate
                        if 'IRA' in account_type.upper():
                            portfolio_values['Schwab IRA'] = balance
                        elif balance > 10000:  # Assume larger balance is IRA account
                            portfolio_values['Schwab IRA'] = balance
                            print(f"✅ Mapped {account_number[-4:]}**** ({account_type}) to Schwab IRA = ${balance:,.2f}")
                        else:  # Smaller balance is Individual account
                            portfolio_values['Schwab Individual'] = balance
                            print(f"✅ Mapped {account_number[-4:]}**** ({account_type}) to Schwab Individual = ${balance:,.2f}")
                        
                        # Remove the generic mapping that was causing duplication
                        # print(f"✅ Mapped {account_number[-4:]}**** ({account_type}) = ${balance:,.2f}")
            
            if not portfolio_values:
                print("⚠️ No balance data found in accounts response, using fallback approach")
                # NO MORE HARDCODED VALUES - Return zeros if API fails
                portfolio_values = {
                    'Schwab IRA': 0.00,        # No hardcoded values - API integration required
                    'Schwab Individual': 0.00  # No hardcoded values - API integration required
                }
                total_value = sum(portfolio_values.values())
            
            print(f"📊 Schwab Portfolio Total: ${total_value:,.2f}")
            print(f"📊 Account Breakdown: {portfolio_values}")
            return portfolio_values
            
        except Exception as e:
            print(f"❌ Error getting Schwab portfolio values: {e}")
            raise
    
    def get_account_values(self):
        """Get account values formatted for portfolio tracking sheet"""
        try:
            portfolio_values = self.get_portfolio_values()
            return portfolio_values
        except Exception as e:
            print(f"❌ Error getting Schwab account values: {e}")
            return {}
    
    def get_dividend_estimates(self):
        """Get dividend estimates from all Schwab accounts using accounts API with positions"""
        try:
            ensure_fresh_token(buffer_seconds=300)
            headers = self._get_authenticated_headers()
            
            # Get accounts with positions included
            accounts_url_with_positions = f"{self.accounts_url}?fields=positions"
            response = requests.get(accounts_url_with_positions, headers=headers)
            
            if response.status_code == 401:
                print("🔄 Token expired during accounts request, refreshing...")
                refresh_access_token()
                headers = self._get_authenticated_headers()
                response = requests.get(accounts_url_with_positions, headers=headers)
            
            if response.status_code != 200:
                print(f"❌ Failed to get Schwab accounts with positions: {response.status_code}")
                return {}
            
            accounts_data = response.json()
            all_estimates = {}
            
            if isinstance(accounts_data, list):
                for account in accounts_data:
                    securities_account = account.get('securitiesAccount', account)
                    account_type = securities_account.get('type', 'Unknown')
                    account_number = securities_account.get('accountNumber', '')
                    
                    print(f"🔄 Processing dividend estimates for {account_type} account {account_number[-4:]}****...")
                    
                    # Get positions from the account data
                    positions = securities_account.get('positions', [])
                    dividend_estimates = []
                    
                    for position in positions:
                        instrument = position.get('instrument', {})
                        symbol = instrument.get('symbol', '')
                        quantity = position.get('longQuantity', 0) + position.get('shortQuantity', 0)
                        market_value = position.get('marketValue', 0)
                        
                        if quantity > 0 and symbol:
                            # Create dividend estimate entry
                            dividend_estimates.append({
                                'Symbol': symbol,
                                'Quantity': quantity,
                                'Account_Type': account_type,
                                'Account_Number': account_number[-4:],  # Last 4 digits for privacy
                                'Position_Value': market_value
                            })
                    
                    if dividend_estimates:
                        # Map account types using the same logic as portfolio values
                        if 'IRA' in account_type.upper():
                            account_key = 'Schwab_IRA'
                        else:
                            # Use balance to differentiate between accounts since both are MARGIN type
                            current_balances = securities_account.get('currentBalances', {})
                            balance = current_balances.get('liquidationValue', 0.0)  # Use liquidationValue instead of totalMarketValue
                            print(f"🔍 Account {account_number[-4:]}**** balance: ${balance:,.2f}")
                            if balance > 10000:  # Larger balance is IRA
                                account_key = 'Schwab_IRA'
                                print(f"  ✅ Mapped to Schwab_IRA (balance > 10k)")
                            else:  # Smaller balance is Individual
                                account_key = 'Schwab_Individual'
                                print(f"  ✅ Mapped to Schwab_Individual (balance <= 10k)")
                        
                        # Add to existing estimates for this account key or create new
                        if account_key in all_estimates:
                            all_estimates[account_key].extend(dividend_estimates)
                            print(f"✅ Added {len(dividend_estimates)} more positions to existing {account_key}")
                        else:
                            all_estimates[account_key] = dividend_estimates
                            print(f"✅ Found {len(dividend_estimates)} positions in {account_key}")
            
            return all_estimates
            
        except Exception as e:
            print(f"❌ Error getting Schwab dividend estimates: {e}")
            return {}
    
    def test_connection(self):
        """Test Schwab API connection with automatic token management"""
        try:
            print("🧪 Testing Schwab API connection...")
            
            # Test with quote fetch first (simpler)
            quote = fetch_batch_quotes(["AAPL"])
            if quote:
                print("✅ Schwab quote API working")
                
                # Test account access
                accounts = self.get_account_numbers()
                if accounts:
                    print("✅ Schwab account API working")
                    print(f"📊 Found {len(accounts)} accounts")
                    return True
                else:
                    print("⚠️ Quote API works but account API failed")
                    return False
            else:
                print("❌ Schwab API connection failed")
                return False
                
        except Exception as e:
            print(f"❌ Schwab API test failed: {e}")
            return False

# Test function for direct execution
if __name__ == "__main__":
    try:
        api = SchwabAPI()
        print("🧪 Testing Schwab API with automatic token management...")
        
        if api.test_connection():
            print("\n💰 Getting portfolio values...")
            portfolio = api.get_portfolio_values()
            print(f"Portfolio: {portfolio}")
            
            print("\n📊 Getting dividend estimates...")
            estimates = api.get_dividend_estimates()
            for account, positions in estimates.items():
                print(f"{account}: {len(positions)} positions")
        else:
            print("❌ API test failed")
    except Exception as e:
        print(f"❌ Error: {e}")

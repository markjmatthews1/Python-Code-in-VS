r"""
Module: etrade_account_api.py
Author: Mark
Created: July 26, 2025
Purpose: Collect dividend estimate data directly from E*TRADE API
Location: C:\Python_Projects\DividendTrackerApp\modules\etrade_account_api.py
"""

import os
import json
import pandas as pd
from datetime import datetime, timedelta
import requests
from requests_oauthlib import OAuth1Session
from modules.etrade_auth import get_etrade_session

class ETRADEAccountAPI:
    """Class to handle E*TRADE account API calls for dividend data"""
    
    def __init__(self):
        self.session = None
        self.base_url = None
        self._initialize_session()
    
    def _initialize_session(self):
        """Initialize the E*TRADE OAuth session"""
        try:
            self.session, self.base_url = get_etrade_session()
            print("✅ E*TRADE API session initialized")
        except Exception as e:
            print(f"❌ Failed to initialize E*TRADE session: {e}")
            raise
    
    def get_account_list(self):
        """Get list of all accounts"""
        try:
            url = f"{self.base_url}/v1/accounts/list.json"
            response = self.session.get(url)
            
            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                self.session, self.base_url = get_etrade_session(force_new=True)
                response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Error getting accounts: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            accounts = data.get('AccountListResponse', {}).get('Accounts', {}).get('Account', [])
            
            print(f"📊 Found {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            print(f"❌ Error getting account list: {e}")
            return None
    
    def get_account_positions(self, account_id_key):
        """Get all positions for a specific account"""
        try:
            url = f"{self.base_url}/v1/accounts/{account_id_key}/portfolio.json"
            response = self.session.get(url)
            
            if response.status_code == 401:
                print("🔄 Token expired, refreshing...")
                self.session, self.base_url = get_etrade_session(force_new=True)
                response = self.session.get(url)
            
            if response.status_code != 200:
                print(f"❌ Error getting positions: {response.status_code} - {response.text}")
                return None
                
            data = response.json()
            positions = data.get('PortfolioResponse', {}).get('AccountPortfolio', [])
            
            if positions and len(positions) > 0:
                portfolio = positions[0].get('Position', [])
                print(f"📊 Found {len(portfolio)} positions in account {account_id_key}")
                return portfolio
            else:
                print(f"📊 No positions found in account {account_id_key}")
                return []
                
        except Exception as e:
            print(f"❌ Error getting account positions: {e}")
            return None
    
    def get_dividend_estimates(self):
        """
        Get dividend estimates from all accounts
        Returns data in the same format as the Excel file processing
        """
        print("🔄 Fetching dividend estimates from E*TRADE API...")
        
        # Get all accounts
        accounts = self.get_account_list()
        if not accounts:
            print("❌ Could not retrieve account list")
            return {}
        
        account_data = {}
        
        for account in accounts:
            account_id_key = account.get('accountIdKey')
            account_name = account.get('accountName', '')
            account_type = account.get('accountType', '')
            
            print(f"🔄 Processing account: {account_name} ({account_type})")
            
            # Map account names to our internal format
            print(f"  🏦 Account details: {account_name} | Type: {account_type} | ID: {account_id_key}")
            
            if 'IRA' in account_name.upper() or 'IRA' in account_type.upper():
                internal_account_type = 'ETRADE_IRA'
                print(f"  ✅ Mapped to: ETRADE_IRA")
            elif 'INDIVIDUAL' in account_type.upper() or 'MARGIN' in account_type.upper():
                internal_account_type = 'ETRADE_Taxable'
                print(f"  ✅ Mapped to: ETRADE_Taxable")
            else:
                internal_account_type = f'ETRADE_{account_type}'
                print(f"  ⚠️ Unknown account type, mapped to: {internal_account_type}")
            
            # Get positions for this account
            positions = self.get_account_positions(account_id_key)
            if not positions:
                continue
            
            # Process positions to estimate dividends
            dividend_estimates = []
            
            for position in positions:
                product = position.get('Product', {})
                symbol = product.get('symbol', '')
                quantity = float(position.get('quantity', 0))
                
                if quantity <= 0:
                    continue
                
                # Get more position details
                position_type = product.get('securityType', 'EQ')
                
                # For now, we'll create placeholder entries with actual position data
                # In a real implementation, we'd need additional API calls for dividend data
                print(f"  📊 Found position: {symbol} - {quantity} shares ({position_type})")
                
                dividend_estimates.append({
                    'Symbol': symbol,
                    'Quantity #': quantity,
                    'Payable Date': None,  # Would need research API or external data
                    'Est. Income $': 0,    # Would need dividend rate data
                    'Status': 'API_PLACEHOLDER',
                    'Frequency': 'Unknown',
                    'Income Type': 'Dividend',
                    'Rate': 0,
                    'account_type': internal_account_type,
                    'Position_Type': position_type
                })
            
            if dividend_estimates:
                df = pd.DataFrame(dividend_estimates)
                account_data[internal_account_type] = df
                print(f"✅ Processed {len(dividend_estimates)} positions from {account_name}")
        
        return account_data
    
    def fetch_dividend_calendar(self, symbol, num_months=12):
        """
        Fetch dividend calendar data for a specific symbol
        This would require additional E*TRADE API endpoints
        """
        # Note: E*TRADE's API may not have direct dividend calendar access
        # This is a placeholder for future implementation
        print(f"🔄 Fetching dividend calendar for {symbol} (placeholder)")
        return None

def test_etrade_connection():
    """Test function to verify E*TRADE API connectivity"""
    try:
        api = ETRADEAccountAPI()
        accounts = api.get_account_list()
        
        if accounts:
            print("✅ E*TRADE API connection successful!")
            for account in accounts:
                print(f"  - {account.get('accountName')} ({account.get('accountType')})")
            return True
        else:
            print("❌ No accounts found")
            return False
            
    except Exception as e:
        print(f"❌ E*TRADE API connection failed: {e}")
        return False

if __name__ == "__main__":
    # Test the API connection
    test_etrade_connection()

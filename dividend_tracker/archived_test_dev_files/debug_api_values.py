#!/usr/bin/env python3
"""
Portfolio API Values Debugger
=============================

Debug and fix the API connections to get REAL portfolio values
from E*TRADE and Schwab APIs.
"""

import os
import sys
import traceback

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from etrade_auth import get_etrade_session
except ImportError as e:
    print(f"❌ E*TRADE import error: {e}")

class PortfolioAPIDebugger:
    """Debug API connections to get real portfolio values"""
    
    def __init__(self):
        self.session = None
        self.base_url = None
        
    def test_etrade_connection(self):
        """Test E*TRADE connection and get real portfolio values"""
        try:
            print("🔍 TESTING E*TRADE API CONNECTION")
            print("=" * 50)
            
            # Get E*TRADE session
            print(">> Initializing E*TRADE session...")
            self.session, self.base_url = get_etrade_session()
            
            if not self.session or not self.base_url:
                print("❌ E*TRADE session failed")
                return {}
                
            print("✅ E*TRADE session established")
            print(f"   Base URL: {self.base_url}")
            
            # Import accounts module
            from pyetrade.accounts import ETradeAccounts
            accounts_api = ETradeAccounts(self.session, self.base_url)
            
            # Get account list
            print("\n📊 Getting account list...")
            account_list = accounts_api.get_account_list()
            
            print("Raw account list structure:")
            print(f"   Keys: {list(account_list.keys())}")
            
            if 'AccountListResponse' in account_list:
                accounts = account_list['AccountListResponse']['Accounts']['Account']
                print(f"   Found {len(accounts)} accounts")
                
                portfolio_values = {}
                
                for i, account_group in enumerate(accounts):
                    print(f"\n📋 Account {i+1}:")
                    account_id = account_group['accountId']
                    account_desc = account_group.get('accountDesc', 'Unknown')
                    
                    print(f"   ID: {account_id}")
                    print(f"   Description: {account_desc}")
                    
                    # Get detailed account balance
                    print(f"   >> Getting balance details...")
                    try:
                        balance_response = accounts_api.get_account_balance(account_id)
                        
                        if balance_response and 'BalanceResponse' in balance_response:
                            balance = balance_response['BalanceResponse']
                            
                            print(f"   Balance response keys: {list(balance.keys())}")
                            
                            # Look for account value fields
                            possible_value_fields = ['accountBalance', 'totalAccountValue', 'netAccountValue']
                            account_value = 0
                            
                            for field in possible_value_fields:
                                if field in balance:
                                    account_value = float(balance[field])
                                    print(f"   {field}: ${account_value:,.2f}")
                                    break
                            
                            # Map to sheet names
                            if 'IRA' in account_desc.upper():
                                portfolio_values['E*TRADE IRA'] = account_value
                                print(f"   ✅ Mapped to E*TRADE IRA: ${account_value:,.2f}")
                            elif any(word in account_desc.upper() for word in ['INDIVIDUAL', 'TAXABLE', 'MARGIN']):
                                portfolio_values['E*TRADE Taxable'] = account_value
                                print(f"   ✅ Mapped to E*TRADE Taxable: ${account_value:,.2f}")
                                
                        else:
                            print(f"   ❌ No balance response for account {account_id}")
                            
                    except Exception as e:
                        print(f"   ❌ Error getting balance for {account_id}: {e}")
                
                return portfolio_values
                
            else:
                print("❌ Unexpected account list structure")
                return {}
                
        except Exception as e:
            print(f"❌ E*TRADE API error: {e}")
            traceback.print_exc()
            return {}
    
    def test_schwab_connection(self):
        """Test Schwab API connection"""
        try:
            print("\n🔍 TESTING SCHWAB API CONNECTION")  
            print("=" * 50)
            
            # Try to import Schwab module
            try:
                from schwab_api_integrated import SchwabAPI
                print("✅ Schwab module imported successfully")
                
                schwab_api = SchwabAPI()
                print("✅ SchwabAPI instance created")
                
                # Get account values
                print(">> Getting Schwab account values...")
                schwab_values = schwab_api.get_account_values()
                
                if schwab_values:
                    print("✅ Schwab values retrieved:")
                    for account, value in schwab_values.items():
                        print(f"   {account}: ${value:,.2f}")
                    return schwab_values
                else:
                    print("❌ No Schwab values returned")
                    return {}
                    
            except ImportError as e:
                print(f"❌ Schwab module import failed: {e}")
                print(">> Using placeholder values")
                return {
                    'Schwab IRA': 0.00,
                    'Schwab Individual': 0.00
                }
                
        except Exception as e:
            print(f"❌ Schwab API error: {e}")
            return {}
    
    def run_api_debug(self):
        """Run comprehensive API debugging"""
        
        print("🔍 PORTFOLIO API VALUES DEBUGGER")
        print("=" * 55)
        print("Testing API connections to get REAL portfolio values")
        print("=" * 55)
        
        # Test E*TRADE
        etrade_values = self.test_etrade_connection()
        
        # Test Schwab  
        schwab_values = self.test_schwab_connection()
        
        # Summary
        print(f"\n📊 API DEBUG RESULTS")
        print("=" * 30)
        
        print(f"E*TRADE Results:")
        if etrade_values:
            for account, value in etrade_values.items():
                print(f"   ✅ {account}: ${value:,.2f}")
        else:
            print(f"   ❌ No E*TRADE values retrieved")
            
        print(f"\nSchwab Results:")
        if schwab_values:
            for account, value in schwab_values.items():
                print(f"   ✅ {account}: ${value:,.2f}")
        else:
            print(f"   ❌ No Schwab values retrieved")
        
        # Calculate total if we have values
        if etrade_values or schwab_values:
            all_values = {**etrade_values, **schwab_values}
            total = sum(all_values.values())
            print(f"\nTotal Portfolio (excluding 401K): ${total:,.2f}")
            return all_values
        else:
            print(f"\n❌ No API values retrieved - need to fix API connections")
            return {}

if __name__ == "__main__":
    debugger = PortfolioAPIDebugger()
    values = debugger.run_api_debug()
    
    input("\nPress Enter to close...")

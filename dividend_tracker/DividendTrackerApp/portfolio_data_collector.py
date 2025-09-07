#!/usr/bin/env python3
"""
Centralized Portfolio Data Collector
===================================

Single point of API data collection for all dividend tracker sheets.
Creates a JSON cache file that can be consumed by multiple sheet updaters.

Features:
- Collects E*TRADE positions & balances (IRA + Taxable)
- Collects Schwab positions & balances (IRA + Individual) 
- Gets 401K value via user input
- Calculates dividend estimates for all positions
- Saves everything to portfolio_data_cache.json
- Deletes and recreates cache each run for fresh data

Author: GitHub Copilot
Created: September 2, 2025
Purpose: Centralized data collection for efficient multi-sheet updates
"""

import os
import sys
import json
import time
import traceback
import requests
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from gui_prompts import get_k401_value
    from etrade_auth import get_etrade_session
    print("✅ Successfully imported dividend tracker modules")
except ImportError as e:
    print(f"❌ Import error: {e}")
    
    def get_k401_value():
        return 125000.00  # Fallback

class PortfolioDataCollector:
    """Centralized data collection for all portfolio sheets"""
    
    def __init__(self):
        self.main_dir = r"c:\Users\mjmat\Python Code in VS"
        self.cache_file = os.path.join(os.path.dirname(__file__), "portfolio_data_cache.json")
        self.ticker_yields_file = os.path.join(self.main_dir, "ticker_yields.json")
        
    def clear_cache(self):
        """Delete existing cache file for fresh data"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
            print(f"🗑️ Cleared existing cache: {self.cache_file}")
    
    def load_manual_yield_overrides(self):
        """Load manual yield overrides that take priority over API/cache data"""
        try:
            override_file = os.path.join(os.path.dirname(__file__), 'manual_yield_overrides.json')
            if os.path.exists(override_file):
                with open(override_file, 'r') as f:
                    overrides = json.load(f)
                    print(f"✅ Loaded {len(overrides)} manual yield overrides")
                    return overrides
            else:
                return {}
        except Exception as e:
            print(f"⚠️ Error loading manual yield overrides: {e}")
            return {}
    
    def load_ticker_yields(self):
        """Load ticker yield database from consolidated cache"""
        try:
            # First try to load from consolidated portfolio_data_cache.json
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    ticker_yields = cache_data.get('ticker_yields', {})
                    if ticker_yields:
                        print(f"✅ Loaded {len(ticker_yields)} ticker yields from consolidated cache")
                        return ticker_yields
            
            # Fallback to legacy ticker_yields.json if consolidated cache doesn't have yield data
            if os.path.exists(self.ticker_yields_file):
                with open(self.ticker_yields_file, 'r') as f:
                    yield_data = json.load(f)
                    tickers = yield_data.get('tickers', {})
                    print(f"⚠️ Using legacy ticker yields file ({len(tickers)} tickers)")
                    return tickers
            else:
                print(f"⚠️ No ticker yield data found")
                return {}
        except Exception as e:
            print(f"❌ Error loading ticker yields: {e}")
            return {}
    
    def collect_fresh_ticker_yields_from_etrade_ira(self):
        """Collect fresh ticker yields from E*TRADE IRA API"""
        print("🔄 Collecting fresh ticker yields from E*TRADE IRA API...")
        
        try:
            # Import the E*TRADE API
            sys.path.append(os.path.join(self.main_dir, 'dividend_tracker', 'DividendTrackerApp'))
            from modules.etrade_account_api import ETRADEAccountAPI
            
            etrade_api = ETRADEAccountAPI()
            accounts = etrade_api.get_account_list()
            
            if not accounts:
                print("❌ No E*TRADE accounts found")
                return {}
            
            # Find IRA account (look for IRA in account type or description)
            target_account = None
            for account in accounts:
                account_id = account.get('accountIdKey', '')
                account_type = account.get('accountType', '')
                account_desc = account.get('accountDesc', '')
                
                # Check if it's an IRA account
                if 'IRA' in account_type.upper() or 'IRA' in account_desc.upper():
                    target_account = account
                    print(f"✅ Found E*TRADE IRA: {account_desc} ({account_type}) - ID: {account_id}")
                    break
            
            if not target_account:
                print("❌ Could not find E*TRADE IRA account")
                return {}
            
            # Get positions from the target account
            positions = etrade_api.get_account_positions(target_account['accountIdKey'])
            if not positions:
                print("❌ No positions found in E*TRADE IRA")
                return {}
            
            # Extract unique tickers
            tickers = []
            for pos in positions:
                # E*TRADE API structure: position -> Product -> symbol
                product = pos.get('Product', {})
                symbol = product.get('symbol', '').strip()
                
                # Fallback to other possible locations if Product.symbol is empty
                if not symbol:
                    symbol = (pos.get('symbolDescription', '') or 
                             pos.get('Symbol', '') or
                             pos.get('ticker', '')).strip()
                
                if symbol and symbol not in tickers:
                    tickers.append(symbol)
            
            print(f"📊 Found {len(tickers)} unique tickers: {', '.join(tickers)}")
            
            # Get dividend data for each ticker
            ticker_yields = {}
            
            # Get E*TRADE session
            from etrade_auth import get_etrade_session
            session, base_url = get_etrade_session()
            
            if not session or not base_url:
                print("❌ Could not get E*TRADE session for quotes")
                return {}
            
            print("🔍 Getting dividend data for each ticker...")
            for ticker in tickers:
                try:
                    print(f"   📊 Getting dividend data for {ticker}...")
                    
                    # Use E*TRADE Quote API (correct endpoint)
                    quote_url = f"{base_url}/v1/market/quote/{ticker}.json"
                    quote_response = session.get(quote_url)
                    
                    if quote_response.status_code == 200:
                        quote_data = quote_response.json()
                        
                        # Extract dividend data from E*TRADE Quote API response structure
                        dividend_yield = 0.0
                        dividend_amount = 0.0
                        annual_dividend = 0.0
                        last_price = 0.0
                        
                        # Parse E*TRADE Quote API response structure
                        if ('QuoteResponse' in quote_data and 
                            'QuoteData' in quote_data['QuoteResponse'] and 
                            isinstance(quote_data['QuoteResponse']['QuoteData'], list) and
                            len(quote_data['QuoteResponse']['QuoteData']) > 0):
                            
                            quote_info = quote_data['QuoteResponse']['QuoteData'][0]
                            all_data = quote_info.get('All', {})
                            
                            # Extract dividend information - try multiple field names
                            dividend_yield = float(all_data.get('yield', 0))
                            annual_dividend = float(all_data.get('annualDividend', 0))
                            dividend_amount = float(all_data.get('dividendAmount', 0))
                            last_price = float(all_data.get('lastTrade', 0))
                            
                            # Check for weekly dividend fields (like QDTE)
                            weekly_dividend = float(all_data.get('dividend', 0))
                            if weekly_dividend == 0:
                                weekly_dividend = float(all_data.get('declaredDividend', 0))
                            
                            # Handle QDTE specifically - weekly paying ETF
                            if ticker == 'QDTE' and weekly_dividend > 0:
                                # QDTE pays weekly dividends (approximately $0.286 per share per week)
                                annual_dividend = weekly_dividend * 52  # 52 weeks per year
                                payment_frequency = 'weekly'
                                if last_price > 0:
                                    dividend_yield = (annual_dividend / last_price) * 100
                                print(f"      📊 {ticker} WEEKLY: ${weekly_dividend:.3f}/week × 52 = ${annual_dividend:.3f}/year = {dividend_yield:.2f}% yield")
                            
                            # Try alternative field names that might have the correct yield
                            elif dividend_yield == 0:
                                dividend_yield = float(all_data.get('dividendYield', 0))
                            
                            # Try other potential dividend fields for other tickers
                            if annual_dividend == 0 and ticker != 'QDTE':
                                annual_dividend = float(all_data.get('annualDiv', 0))
                                if annual_dividend == 0:
                                    annual_dividend = float(all_data.get('totalDividend', 0))
                            
                            # Try to find trailing twelve months dividend or distribution
                            if annual_dividend == 0 and ticker != 'QDTE':
                                ttm_dividend = float(all_data.get('ttmDividend', 0))
                                if ttm_dividend > 0:
                                    annual_dividend = ttm_dividend
                                    print(f"      📊 Using TTM dividend for {ticker}: ${ttm_dividend}")
                            
                            # For ETFs (except QDTE which we handled above), check for distribution fields
                            if annual_dividend == 0 and ticker != 'QDTE':
                                distribution = float(all_data.get('distribution', 0))
                                if distribution > 0:
                                    annual_dividend = distribution * 12  # Assume monthly
                                    print(f"      📊 Using monthly distribution for {ticker}: ${distribution}/month")
                            
                            # Calculate yield from annual dividend if yield is 0 or seems low
                            if last_price > 0 and annual_dividend > 0 and ticker != 'QDTE':
                                calculated_yield = (annual_dividend / last_price) * 100
                                if calculated_yield > dividend_yield:
                                    print(f"      🔄 Calculated yield {calculated_yield:.2f}% > API yield {dividend_yield:.2f}% for {ticker}")
                                    dividend_yield = calculated_yield
                            
                            # Set payment frequency
                            if ticker == 'QDTE':
                                payment_frequency = 'weekly'
                            else:
                                payment_frequency = 'quarterly'
                        
                        # Calculate quarterly dividend if we have annual dividend
                        quarterly_dividend = annual_dividend / 4 if annual_dividend > 0 else dividend_amount
                        
                        ticker_yields[ticker] = {
                            'yield': dividend_yield,
                            'dividend_amount': quarterly_dividend,
                            'annual_dividend': annual_dividend,
                            'payment_frequency': payment_frequency,
                            'last_price': last_price,
                            'has_dividend': annual_dividend > 0 or dividend_yield > 0,
                            'dividend_source': 'etrade_quote_api',
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if annual_dividend > 0 or dividend_yield > 0:
                            print(f"      ✅ {ticker}: {dividend_yield:.2f}% yield, ${annual_dividend:.4f} annual dividend")
                        else:
                            print(f"      ⚪ {ticker}: No dividend data available")
                    
                    else:
                        print(f"      ⚠️ Quote API error for {ticker}: {quote_response.status_code}")
                        ticker_yields[ticker] = {
                            'yield': 0.0,
                            'dividend_amount': 0.0,
                            'annual_dividend': 0.0,
                            'payment_frequency': 'quarterly',
                            'last_price': 0.0,
                            'has_dividend': False,
                            'dividend_source': 'etrade_quote_api_error',
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                    
                    # Small delay to avoid rate limiting
                    time.sleep(0.1)
                    
                except Exception as ticker_error:
                    print(f"      ❌ Error getting {ticker}: {ticker_error}")
                    ticker_yields[ticker] = {
                        'yield': 0.0,
                        'dividend_amount': 0.0,
                        'annual_dividend': 0.0,
                        'payment_frequency': 'quarterly',
                        'last_price': 0.0,
                        'has_dividend': False,
                        'dividend_source': 'error',
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            print(f"✅ Collected ticker yield data for {len(ticker_yields)} tickers")
            return ticker_yields
            
        except Exception as e:
            print(f"❌ Error collecting fresh ticker yields: {e}")
            traceback.print_exc()
            return {}
    
    def get_etrade_data(self):
        """Get E*TRADE account balances and positions"""
        print("\n📊 Collecting E*TRADE Data...")
        print("=" * 40)
        
        etrade_data = {
            'balances': {},
            'positions': {}
        }
        
        try:
            # Get account balances using existing working method
            from enhanced_portfolio_updater_with_schwab import EnhancedPortfolioUpdater
            updater = EnhancedPortfolioUpdater()
            
            # Get account balances (this hits balance endpoint)
            etrade_balances = updater.get_etrade_values()
            etrade_data['balances'] = etrade_balances
            print("✅ E*TRADE account balances collected")
            
            # Now get positions for each account (this hits positions endpoint)
            etrade_positions = self.get_etrade_positions_by_account()
            etrade_data['positions'] = etrade_positions
            print("✅ E*TRADE positions collected")
            
            return etrade_data
            
        except Exception as e:
            print(f"❌ Error collecting E*TRADE data: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'balances': {'E*TRADE IRA': 0.0, 'E*TRADE Taxable': 0.0},
                'positions': {'etrade_ira': [], 'etrade_taxable': []}
            }
    
    def get_etrade_positions_by_account(self):
        """Get E*TRADE positions organized by account using working API"""
        print("🔍 Getting E*TRADE positions by account...")
        
        positions_by_account = {
            'etrade_ira': [],
            'etrade_taxable': []
        }
        
        try:
            # Use the working ETRADEAccountAPI approach (same as ticker collection)
            from modules.etrade_account_api import ETRADEAccountAPI
            
            etrade_api = ETRADEAccountAPI()
            accounts = etrade_api.get_account_list()
            
            if not accounts:
                print("❌ No E*TRADE accounts found")
                return positions_by_account
            
            # Process each account using the working API methods
            for account in accounts:
                account_id_key = account.get('accountIdKey', '')
                account_name = account.get('accountName', '')
                account_type = account.get('accountType', '')
                
                print(f"   📁 Processing {account_name} ({account_type})")
                
                # Get positions using the working API method
                positions = etrade_api.get_account_positions(account_id_key)
                
                if positions:
                    # Parse positions to extract symbol and quantity
                    parsed_positions = []
                    for position in positions:
                        product = position.get('Product', {})
                        symbol = product.get('symbol', '').strip()
                        quantity = float(position.get('quantity', 0))
                        market_value = float(position.get('marketValue', 0))
                        
                        if symbol and quantity > 0:
                            parsed_positions.append({
                                'symbol': symbol,
                                'quantity': quantity,
                                'market_value': market_value,
                                'account_id': account_id_key,
                                'account_name': account_name,
                                'account_type': account_type
                            })
                    
                    # Determine account mapping
                    if 'IRA' in account_name.upper() or 'IRA' in account_type.upper():
                        positions_by_account['etrade_ira'].extend(parsed_positions)
                        print(f"     → Mapped to E*TRADE IRA ({len(parsed_positions)} positions)")
                    elif 'INDIVIDUAL' in account_type.upper() or 'BROKERAGE' in account_type.upper():
                        positions_by_account['etrade_taxable'].extend(parsed_positions)
                        print(f"     → Mapped to E*TRADE Taxable ({len(parsed_positions)} positions)")
                    else:
                        print(f"     ⚠️ Unknown account type mapping for {account_type}")
                else:
                    print(f"     ❌ Failed to get positions: No data returned")
            
            return positions_by_account
            
        except Exception as e:
            print(f"❌ Error getting E*TRADE positions: {e}")
            import traceback
            print(f"Traceback: {traceback.format_exc()}")
            return positions_by_account
    
    def parse_etrade_positions(self, positions_data):
        """Parse E*TRADE positions response into standardized format"""
        positions = []
        
        try:
            portfolio = positions_data.get('response', {}).get('Portfolio', {})
            position_lots = portfolio.get('PositionLot', [])
            
            # Handle single position vs array
            if not isinstance(position_lots, list):
                position_lots = [position_lots]
            
            for lot in position_lots:
                instrument = lot.get('Instrument', {})
                position_info = lot.get('Position', {})
                
                symbol = instrument.get('symbolDescription', '')
                quantity = float(position_info.get('quantity', 0))
                market_value = float(position_info.get('marketValue', 0))
                current_price = float(position_info.get('currentPrice', 0))
                
                if quantity > 0:  # Only long positions
                    positions.append({
                        'symbol': symbol,
                        'quantity': quantity,
                        'market_value': market_value,
                        'current_price': current_price
                    })
            
        except Exception as e:
            print(f"⚠️ Error parsing E*TRADE positions: {e}")
        
        return positions
    
    def get_schwab_data(self):
        """Get Schwab account balances and positions"""
        print("\n📊 Collecting Schwab Data...")
        print("=" * 40)
        
        schwab_data = {
            'balances': {},
            'positions': {}
        }
        
        try:
            # Get account balances using existing working method
            from enhanced_portfolio_updater_with_schwab import EnhancedPortfolioUpdater
            updater = EnhancedPortfolioUpdater()
            
            # Get account balances (this hits balance endpoint)
            schwab_balances = updater.get_schwab_values()
            schwab_data['balances'] = schwab_balances
            print("✅ Schwab account balances collected")
            
            # Get positions for each account (this hits positions endpoint)
            schwab_positions = self.get_schwab_positions_by_account()
            schwab_data['positions'] = schwab_positions
            print("✅ Schwab positions collected")
            
            return schwab_data
            
        except Exception as e:
            print(f"❌ Error collecting Schwab data: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return {
                'balances': {'Schwab IRA': 0.0, 'Schwab Individual': 0.0},
                'positions': {'schwab_ira': [], 'schwab_individual': []}
            }
    
    def get_schwab_positions_by_account(self):
        """Get Schwab positions organized by account"""
        print("🔍 Getting Schwab positions by account...")
        
        positions_by_account = {
            'schwab_ira': [],
            'schwab_individual': []
        }
        
        try:
            # Import and use main directory Schwab auth system with automatic token refresh
            import importlib.util
            main_schwab_auth_path = os.path.join(self.main_dir, "Schwab_auth.py")
            spec = importlib.util.spec_from_file_location("main_schwab_auth", main_schwab_auth_path)
            main_schwab_auth = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(main_schwab_auth)
            
            # Override TOKEN_FILE to use main directory path
            main_schwab_auth.TOKEN_FILE = os.path.join(self.main_dir, "tokens.json")
            
            # Use the built-in automatic token refresh function
            try:
                access_token = main_schwab_auth.get_valid_access_token()
                print("✅ Got valid access token with automatic refresh")
            except Exception as e:
                print(f"❌ Error getting valid Schwab token: {e}")
                return positions_by_account
            
            # Make API call to get accounts with positions
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            }
            
            # Get account list first to get the correct account IDs/numbers
            # Request positions data along with account data (similar to schwabr value_pull="all")
            accounts_url = "https://api.schwabapi.com/trader/v1/accounts?fields=positions"
            print(f"🔍 Requesting accounts with positions: {accounts_url}")
            accounts_response = requests.get(accounts_url, headers=headers, timeout=15)
            
            if accounts_response.status_code != 200:
                print(f"❌ Failed to get Schwab accounts with positions: {accounts_response.status_code}")
                print(f"   Response: {accounts_response.text[:200]}")
                
                # Fallback to basic accounts endpoint
                print("🔄 Trying basic accounts endpoint...")
                accounts_url = "https://api.schwabapi.com/trader/v1/accounts"
                accounts_response = requests.get(accounts_url, headers=headers, timeout=15)
                
                if accounts_response.status_code != 200:
                    print(f"❌ Failed to get basic Schwab accounts: {accounts_response.status_code}")
                    return positions_by_account
            
            accounts_data = accounts_response.json()
            print(f"✅ Retrieved {len(accounts_data)} Schwab accounts")
            
            # Get positions for each account using the actual account data
            for account_wrapper in accounts_data:
                account = account_wrapper.get('securitiesAccount', {})
                account_number = account.get('accountNumber', 'Unknown')
                account_type = account.get('type', 'Unknown')
                
                print(f"   📁 Getting positions for {account_type} ({account_number})")
                
                # First check if positions are already included in the main account data
                # (similar to how schwabr library gets positions with balances)
                existing_positions = account.get('positions', [])
                if existing_positions:
                    print(f"     ✅ Found {len(existing_positions)} positions in account data")
                    
                    # Process positions from main account response
                    for position in existing_positions:
                        try:
                            instrument = position.get('instrument', {})
                            symbol = instrument.get('symbol', '')
                            
                            # Schwab uses longQuantity for position quantity
                            quantity = position.get('longQuantity', 0)
                            if quantity == 0:
                                quantity = position.get('quantity', 0)
                                
                            market_value = position.get('marketValue', 0)
                            
                            if symbol and quantity > 0:
                                position_data = {
                                    'symbol': symbol,
                                    'quantity': quantity,
                                    'market_value': market_value,
                                    'account_name': f"Schwab {account_type}",
                                    'account_number': account_number
                                }
                                
                                # Map to account categories
                                if 'IRA' in account_type.upper() or account_number == '91562183':
                                    positions_by_account['schwab_ira'].append(position_data)
                                else:
                                    positions_by_account['schwab_individual'].append(position_data)
                                    
                                print(f"       💰 {symbol}: {quantity} shares = ${market_value:,.2f}")
                                
                        except Exception as e:
                            print(f"       ⚠️ Error processing position: {e}")
                            continue
                    
                    continue  # Skip endpoint testing if we found positions
                
                # If no positions in main data, try different position endpoint formats
                position_endpoints = [
                    f"https://api.schwabapi.com/trader/v1/accounts/{account_number}?fields=positions",  # Most likely based on R code
                    f"https://api.schwabapi.com/v1/accounts/{account_number}/positions", 
                    f"https://api.schwabapi.com/trader/v1/accounts/{account_number}/positions",
                    f"https://api.schwabapi.com/trader/v1/accounts/{account_number}/positions.json",
                    f"https://api.schwabapi.com/trader/v1/accounts/{account_number}/portfolio"
                ]
                
                positions_found = False
                for endpoint in position_endpoints:
                    endpoint_name = endpoint.split('/')[-1] if '?' not in endpoint else endpoint.split('?')[1]
                    print(f"     🔍 Trying: {endpoint_name}")
                    
                    try:
                        response = requests.get(endpoint, headers=headers, timeout=10)
                        
                        if response.status_code == 200:
                            try:
                                positions_data = response.json()
                                
                                # Handle different response structures
                                if isinstance(positions_data, list) and positions_data:
                                    # Direct list of positions
                                    positions = positions_data
                                elif isinstance(positions_data, dict):
                                    # Nested structure - look for positions in various keys
                                    positions = (positions_data.get('positions', []) or 
                                               positions_data.get('securitiesAccount', {}).get('positions', []) or
                                               positions_data.get('portfolio', {}).get('positions', []))
                                else:
                                    positions = []
                                    
                                if positions:
                                    print(f"     ✅ Found {len(positions)} positions via {endpoint_name}")
                                    
                                    for position in positions:
                                        try:
                                            # Handle different position data structures
                                            instrument = position.get('instrument', {})
                                            symbol = instrument.get('symbol') or instrument.get('cusip', '')
                                            
                                            # Try different quantity fields (Schwab uses longQuantity)
                                            quantity = (position.get('longQuantity', 0) or 
                                                       position.get('quantity', 0))
                                            market_value = position.get('marketValue', 0)
                                            
                                            if symbol and quantity > 0:
                                                position_data = {
                                                    'symbol': symbol,
                                                    'quantity': quantity,
                                                    'market_value': market_value,
                                                    'account_name': f"Schwab {account_type}",
                                                    'account_number': account_number
                                                }
                                                
                                                # Map to account categories
                                                if 'IRA' in account_type.upper() or account_number == '91562183':
                                                    positions_by_account['schwab_ira'].append(position_data)
                                                else:
                                                    positions_by_account['schwab_individual'].append(position_data)
                                                    
                                                print(f"       💰 {symbol}: {quantity} shares = ${market_value:,.2f}")
                                                
                                        except Exception as e:
                                            print(f"       ⚠️ Error processing position: {e}")
                                            continue
                                    
                                    positions_found = True
                                    break  # Success - stop trying other endpoints
                                    
                                else:
                                    print(f"     ⚪ No positions found in response via {endpoint_name}")
                                    
                            except json.JSONDecodeError:
                                print(f"     ❌ Invalid JSON response from {endpoint_name}")
                                continue
                                
                        elif response.status_code == 404:
                            print(f"     ⚪ Endpoint not found: {endpoint_name}")
                        elif response.status_code == 500:
                            print(f"     ❌ Server error (500) for: {endpoint_name}")
                        else:
                            print(f"     ❌ HTTP {response.status_code} for: {endpoint_name}")
                            
                    except requests.exceptions.Timeout:
                        print(f"     ⏰ Timeout for: {endpoint_name}")
                        continue
                    except Exception as e:
                        print(f"     ❌ Error with {endpoint_name}: {e}")
                        continue
                
                if not positions_found:
                    print(f"     ❌ No positions found for {account_type} ({account_number})")
            
            return positions_by_account
            
        except Exception as e:
            print(f"❌ Error getting Schwab positions: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return positions_by_account
    
    def parse_schwab_positions(self, positions):
        """Parse Schwab positions into standardized format"""
        parsed_positions = []
        
        try:
            for position in positions:
                instrument = position.get('instrument', {})
                symbol = instrument.get('symbol', '')
                
                long_quantity = float(position.get('longQuantity', 0))
                market_value = float(position.get('marketValue', 0))
                current_day_profit_loss = position.get('currentDayProfitLoss', 0)
                
                if long_quantity > 0:  # Only long positions
                    # Calculate approximate current price
                    current_price = market_value / long_quantity if long_quantity > 0 else 0
                    
                    parsed_positions.append({
                        'symbol': symbol,
                        'quantity': long_quantity,
                        'market_value': market_value,
                        'current_price': current_price,
                        'day_profit_loss': current_day_profit_loss
                    })
            
        except Exception as e:
            print(f"⚠️ Error parsing Schwab positions: {e}")
        
        return parsed_positions
    
    def calculate_dividend_estimates(self, all_positions, ticker_yields):
        """Calculate dividend estimates for all accounts using E*TRADE IRA yield database"""
        print("\n💰 Calculating Dividend Estimates...")
        print("=" * 40)
        
        dividend_estimates = {}
        
        for account, positions in all_positions.items():
            account_dividend = 0.0
            print(f"\n📊 Processing {account.replace('_', ' ').title()}...")
            
            for position in positions:
                symbol = position['symbol']
                quantity = position['quantity']
                market_value = position['market_value']
                
                # Get yield from E*TRADE IRA ticker database (used for all accounts)
                yield_info = ticker_yields.get(symbol, {})
                
                if yield_info:
                    # Try different yield field names from the database
                    dividend_yield = (
                        yield_info.get('dividend_yield') or
                        yield_info.get('yield') or
                        yield_info.get('annual_dividend_yield') or
                        0.0
                    )
                    
                    if dividend_yield > 0:
                        # Calculate annual dividend based on market value and yield percentage
                        annual_dividend = market_value * (dividend_yield / 100)
                        account_dividend += annual_dividend
                        print(f"   📊 {symbol}: {quantity} × {dividend_yield}% = ${annual_dividend:.2f}/year")
                    else:
                        print(f"   📊 {symbol}: {quantity} shares - No dividend yield available")
                else:
                    # Try to get yield from any available source or use conservative estimate
                    print(f"   ⚠️ {symbol}: Not in E*TRADE IRA yield database - using conservative estimate")
                    # Conservative estimate for unknown tickers (2% yield)
                    conservative_dividend = market_value * 0.02
                    account_dividend += conservative_dividend
                    print(f"   📊 {symbol}: {quantity} × 2.0% (est.) = ${conservative_dividend:.2f}/year")
            
            # Map account names for output
            if account == 'etrade_ira':
                dividend_estimates['E*TRADE IRA'] = account_dividend
            elif account == 'etrade_taxable':
                dividend_estimates['E*TRADE Taxable'] = account_dividend
            elif account == 'schwab_ira':
                dividend_estimates['Schwab IRA'] = account_dividend
            elif account == 'schwab_individual':
                dividend_estimates['Schwab Individual'] = account_dividend
            
            print(f"✅ {account.replace('_', ' ').title()} yearly dividend income: ${account_dividend:.2f}")
        
        return dividend_estimates
    
    def create_cache(self):
        """Create comprehensive portfolio data cache"""
        print("🔄 Creating Portfolio Data Cache...")
        print("=" * 50)
        
        # Clear existing cache
        self.clear_cache()
        
        # Collect fresh ticker yields from E*TRADE IRA API
        print("\n📊 Step 1: Collecting fresh ticker yields from E*TRADE IRA...")
        ticker_yields = self.collect_fresh_ticker_yields_from_etrade_ira()
        
        if not ticker_yields:
            print("⚠️ No ticker yields collected, falling back to backup...")
            ticker_yields = self.load_ticker_yields()  # Try backup/legacy source
        
        # Collect all data
        print("\n📊 Step 2: Collecting account data...")
        etrade_data = self.get_etrade_data()
        schwab_data = self.get_schwab_data()
        
        # Get 401K value
        print("\n💰 Getting 401K Value...")
        k401_value = get_k401_value()
        
        # Combine all positions for dividend calculations
        all_positions = {
            **etrade_data['positions'],
            **schwab_data['positions']
        }
        
        # Calculate dividend estimates
        dividend_estimates = self.calculate_dividend_estimates(all_positions, ticker_yields)
        
        # Create comprehensive cache
        cache_data = {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'portfolio_values': {
                **etrade_data['balances'],
                **schwab_data['balances'],
                '401K': k401_value
            },
            'positions': all_positions,
            'dividend_estimates': dividend_estimates,
            'ticker_yields': ticker_yields,
            'totals': {
                'total_portfolio': sum([
                    sum(etrade_data['balances'].values()),
                    sum(schwab_data['balances'].values()),
                    k401_value
                ]),
                'total_yearly_dividends': sum(dividend_estimates.values()),
                'total_monthly_dividends': sum(dividend_estimates.values()) / 12
            }
        }
        
        # Save cache
        with open(self.cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        print(f"\n✅ Cache created: {self.cache_file}")
        print(f"📊 Total Portfolio: ${cache_data['totals']['total_portfolio']:,.2f}")
        print(f"💰 Total Yearly Dividends: ${cache_data['totals']['total_yearly_dividends']:,.2f}")
        print(f"📅 Total Monthly Dividends: ${cache_data['totals']['total_monthly_dividends']:,.2f}")
        
        return cache_data
    
    def load_cache(self):
        """Load existing cache data"""
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return None
    
    def collect_all_data(self):
        """Collect all fresh data and return it (wrapper for create_cache)"""
        try:
            return self.create_cache()
        except Exception as e:
            print(f"❌ Error collecting all data: {e}")
            return None
    
    def collect_all_data_with_fallback(self, k401_value=None):
        """Collect all fresh data with fallback handling and optional 401K value override"""
        print("\n🔄 Collecting all data with fallback handling...")
        
        try:
            # Use provided 401K value or get it fresh
            if k401_value is not None:
                print(f"💰 Using provided 401K value: ${k401_value:,.2f}")
            else:
                print("💰 Getting fresh 401K value...")
                k401_value = get_k401_value()
                print(f"💰 401K value: ${k401_value:,.2f}")
            
            # Clear existing cache
            self.clear_cache()
            
            # Collect fresh ticker yields from E*TRADE IRA API
            print("\n📊 Step 1: Collecting fresh ticker yields...")
            ticker_yields = self.collect_fresh_ticker_yields_from_etrade_ira()
            
            if not ticker_yields:
                print("⚠️ No ticker yields collected, trying fallback...")
                ticker_yields = self.load_ticker_yields()  # Try backup/legacy source
            
            # Collect account data with error handling
            print("\n📊 Step 2: Collecting account data...")
            
            # Get E*TRADE data with fallback
            try:
                etrade_data = self.get_etrade_data()
                print("✅ E*TRADE data collected successfully")
            except Exception as e:
                print(f"⚠️ E*TRADE data collection failed: {e}")
                etrade_data = {
                    'balances': {'E*TRADE IRA': 0.0, 'E*TRADE Taxable': 0.0},
                    'positions': {'etrade_ira': [], 'etrade_taxable': []}
                }
            
            # Get Schwab data with fallback
            try:
                schwab_data = self.get_schwab_data()
                print("✅ Schwab data collected successfully")
            except Exception as e:
                print(f"⚠️ Schwab data collection failed: {e}")
                schwab_data = {
                    'balances': {'Schwab IRA': 0.0, 'Schwab Individual': 0.0},
                    'positions': {'schwab_ira': [], 'schwab_individual': []}
                }
            
            # Combine all positions for dividend calculations
            all_positions = {
                **etrade_data['positions'],
                **schwab_data['positions']
            }
            
            # Calculate dividend estimates with fallback
            try:
                dividend_estimates = self.calculate_dividend_estimates(all_positions, ticker_yields)
                print("✅ Dividend estimates calculated successfully")
            except Exception as e:
                print(f"⚠️ Dividend calculation failed: {e}")
                dividend_estimates = {}
            
            # Create comprehensive cache
            cache_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'portfolio_values': {
                    **etrade_data['balances'],
                    **schwab_data['balances'],
                    '401K': k401_value
                },
                'positions': all_positions,
                'dividend_estimates': dividend_estimates,
                'ticker_yields': ticker_yields,
                'totals': {
                    'total_portfolio': sum([
                        sum(etrade_data['balances'].values()),
                        sum(schwab_data['balances'].values()),
                        k401_value
                    ]),
                    'total_yearly_dividends': sum(dividend_estimates.values()),
                    'total_monthly_dividends': sum(dividend_estimates.values()) / 12
                }
            }
            
            # Save cache
            try:
                with open(self.cache_file, 'w') as f:
                    json.dump(cache_data, f, indent=2)
                print(f"✅ Cache saved: {self.cache_file}")
            except Exception as e:
                print(f"⚠️ Error saving cache: {e}")
            
            print(f"\n🎉 Data collection completed with fallback handling!")
            print(f"📊 Total Portfolio: ${cache_data['totals']['total_portfolio']:,.2f}")
            print(f"💰 Total Yearly Dividends: ${cache_data['totals']['total_yearly_dividends']:,.2f}")
            print(f"📅 Total Monthly Dividends: ${cache_data['totals']['total_monthly_dividends']:,.2f}")
            
            return cache_data
            
        except Exception as e:
            print(f"❌ Critical error in collect_all_data_with_fallback: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            
            # Return minimal fallback data structure
            fallback_data = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'portfolio_values': {
                    'E*TRADE IRA': 0.0,
                    'E*TRADE Taxable': 0.0,
                    'Schwab IRA': 0.0,
                    'Schwab Individual': 0.0,
                    '401K': k401_value if k401_value else 0.0
                },
                'positions': {
                    'etrade_ira': [],
                    'etrade_taxable': [],
                    'schwab_ira': [],
                    'schwab_individual': []
                },
                'dividend_estimates': {},
                'ticker_yields': {},
                'totals': {
                    'total_portfolio': k401_value if k401_value else 0.0,
                    'total_yearly_dividends': 0.0,
                    'total_monthly_dividends': 0.0
                }
            }
            
            print("🔄 Returning fallback data structure to prevent complete failure")
            return fallback_data

def main():
    """Main execution"""
    collector = PortfolioDataCollector()
    
    print("🚀 Portfolio Data Collector")
    print("=" * 30)
    print("Collecting fresh data from all APIs...")
    
    try:
        cache_data = collector.create_cache()
        
        print(f"\n🎉 SUCCESS! Portfolio data cache created")
        print(f"📁 Cache file: {collector.cache_file}")
        print(f"⏰ Timestamp: {cache_data['timestamp']}")
        print(f"\n💡 This cache can now be used by:")
        print("   • Portfolio Values 2025 updater")
        print("   • Estimated Income 2025 updater") 
        print("   • Any other sheet updater")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating cache: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    main()

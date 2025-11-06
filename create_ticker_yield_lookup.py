"""
Create Ticker Yield Lookup from E*TRADE IRA Account
Gets dividend tickers from E*TRADE IRA (ending in 7660) and their current yields
Creates ticker_yields.json file for use across all accounts
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etrade_auth import get_etrade_session
import json
import time
from datetime import datetime

def get_etrade_ira_dividend_tickers():
    """Get tickers from E*TRADE IRA account ending in 7660"""
    print("🔄 Getting dividend tickers from E*TRADE IRA account...")
    
    try:
        # Import the E*TRADE API
        sys.path.append(r'c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp')
        from modules.etrade_account_api import ETRADEAccountAPI
        
        etrade_api = ETRADEAccountAPI()
        accounts = etrade_api.get_account_list()
        
        if not accounts:
            print("❌ No E*TRADE accounts found")
            return []
        
        # Find IRA account ending in 7660
        target_account = None
        for account in accounts:
            account_id = account.get('accountIdKey', '')
            account_type = account.get('accountType', '')
            account_desc = account.get('accountDesc', '')
            
            if account_id.endswith('7660'):
                target_account = account
                print(f"✅ Found target IRA account: {account_desc} ({account_id})")
                break
        
        if not target_account:
            print("❌ Could not find E*TRADE IRA account ending in 7660")
            return []
        
        # Get positions from the target account
        positions = etrade_api.get_account_positions(target_account['accountIdKey'])
        if not positions:
            print("❌ No positions found in IRA account")
            return []
        
        print(f"📊 Found {len(positions)} positions in IRA account")
        
        # Extract ticker symbols
        tickers = []
        for position in positions:
            symbol = position.get('symbolDescription', '').upper().strip()
            quantity = position.get('quantity', 0)
            market_value = position.get('marketValue', 0)
            
            if symbol and quantity > 0 and market_value > 0:
                tickers.append(symbol)
                print(f"   📈 {symbol}: {quantity} shares, ${market_value:,.2f}")
        
        print(f"✅ Extracted {len(tickers)} ticker symbols from IRA account")
        return tickers
        
    except Exception as e:
        print(f"❌ Error getting IRA tickers: {e}")
        return []

def get_dividend_yields_from_quotes(tickers):
    """Get dividend yields for tickers using E*TRADE Quote API"""
    print("🔄 Getting dividend yields from E*TRADE Quote API...")
    
    try:
        session, base_url = get_etrade_session()
        ticker_yields = {}
        
        for ticker in tickers:
            print(f"   🔍 Getting yield for {ticker}...")
            
            try:
                # Get quote from E*TRADE Quote API
                quote_url = f"{base_url}/v1/market/quote/{ticker}.json"
                quote_response = session.get(quote_url)
                
                if quote_response.status_code == 200:
                    quote_data = quote_response.json()
                    
                    # Navigate the response structure
                    if 'QuoteResponse' in quote_data and 'QuoteData' in quote_data['QuoteResponse']:
                        quote_list = quote_data['QuoteResponse']['QuoteData']
                        if not isinstance(quote_list, list):
                            quote_list = [quote_list]
                        
                        # Get the first quote
                        quote = quote_list[0]
                        
                        # Extract dividend data
                        dividend_yield = None
                        dividend_amount = None
                        last_trade = None
                        
                        if 'All' in quote:
                            all_data = quote['All']
                            dividend_yield = all_data.get('yield', 0)
                            dividend_amount = all_data.get('annualDividend', 0)
                            last_trade = all_data.get('lastTrade', 0)
                            
                            # Also check alternative field names
                            if not dividend_yield:
                                dividend_yield = all_data.get('dividendYield', 0)
                            if not dividend_amount:
                                dividend_amount = all_data.get('dividendAmount', 0)
                        
                        # Convert to numbers and validate
                        dividend_yield = float(dividend_yield) if dividend_yield else 0.0
                        dividend_amount = float(dividend_amount) if dividend_amount else 0.0
                        last_trade = float(last_trade) if last_trade else 0.0
                        
                        # Store ticker data
                        ticker_yields[ticker] = {
                            'yield': dividend_yield,
                            'annual_dividend': dividend_amount,
                            'last_price': last_trade,
                            'has_dividend': dividend_yield > 0 or dividend_amount > 0,
                            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        }
                        
                        if dividend_yield > 0 or dividend_amount > 0:
                            print(f"      💰 {ticker}: {dividend_yield:.2f}% yield, ${dividend_amount:.4f} annual dividend")
                        else:
                            print(f"      ⚪ {ticker}: No dividend data found")
                            
                else:
                    print(f"      ⚠️ Quote API error for {ticker}: {quote_response.status_code}")
                    ticker_yields[ticker] = {
                        'yield': 0.0,
                        'annual_dividend': 0.0,
                        'last_price': 0.0,
                        'has_dividend': False,
                        'error': f"API error {quote_response.status_code}",
                        'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
            
            except Exception as ticker_error:
                print(f"      ❌ Error getting {ticker}: {ticker_error}")
                ticker_yields[ticker] = {
                    'yield': 0.0,
                    'annual_dividend': 0.0,
                    'last_price': 0.0,
                    'has_dividend': False,
                    'error': str(ticker_error),
                    'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            
            # Pause between API calls to avoid rate limits
            time.sleep(0.3)
        
        return ticker_yields
        
    except Exception as e:
        print(f"❌ Error getting dividend yields: {e}")
        return {}

def save_ticker_yields(ticker_yields, filename='ticker_yields.json'):
    """Save ticker yields to JSON file for reuse"""
    print(f"💾 Saving ticker yields to {filename}...")
    
    try:
        # Add metadata
        output_data = {
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'source': 'E*TRADE IRA account ending in 7660',
            'total_tickers': len(ticker_yields),
            'dividend_tickers': sum(1 for t in ticker_yields.values() if t['has_dividend']),
            'tickers': ticker_yields
        }
        
        with open(filename, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f"✅ Saved {len(ticker_yields)} tickers to {filename}")
        
        # Print summary
        dividend_count = sum(1 for t in ticker_yields.values() if t['has_dividend'])
        print(f"📊 Summary: {dividend_count} dividend-paying stocks out of {len(ticker_yields)} total")
        
        return True
        
    except Exception as e:
        print(f"❌ Error saving ticker yields: {e}")
        return False

def main():
    """Main function to create ticker yield lookup file"""
    print("🚀 CREATING TICKER YIELD LOOKUP FROM E*TRADE IRA")
    print("=" * 55)
    
    # Step 1: Get tickers from E*TRADE IRA account
    tickers = get_etrade_ira_dividend_tickers()
    if not tickers:
        print("❌ Failed to get tickers from E*TRADE IRA account")
        return
    
    print(f"\n📋 Found {len(tickers)} tickers: {', '.join(tickers)}")
    
    # Step 2: Get dividend yields from Quote API
    ticker_yields = get_dividend_yields_from_quotes(tickers)
    if not ticker_yields:
        print("❌ Failed to get dividend yields from Quote API")
        return
    
    # Step 3: Save to JSON file
    if save_ticker_yields(ticker_yields):
        print("\n✅ Ticker yield lookup file created successfully!")
        print("🎯 You can now use this file to calculate dividend estimates for all accounts")
    else:
        print("\n❌ Failed to save ticker yield lookup file")

if __name__ == "__main__":
    main()

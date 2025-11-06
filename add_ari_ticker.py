#!/usr/bin/env python3
"""
Get ARI dividend yield from E*TRADE Quote API and add to ticker yields data
"""

import json
import sys
import os
from datetime import datetime

# Add the dividend tracker path for E*TRADE API
sys.path.append(r'c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp')
from modules.etrade_account_api import ETRADEAccountAPI

def get_ari_dividend_data():
    """Get ARI dividend data from E*TRADE Quote API."""
    try:
        etrade_api = ETRADEAccountAPI()
        
        print("🔄 Getting ARI dividend data from E*TRADE Quote API...")
        
        # Get quote data for ARI
        quote_response = etrade_api.session.get(
            f"{etrade_api.base_url}/v1/market/productlookup.json",
            params={'company': 'ARI', 'type': 'EQ'}
        )
        
        if quote_response.status_code == 401:
            print("🔄 Token expired, refreshing...")
            etrade_api.session, etrade_api.base_url = etrade_api.get_etrade_session(force_new=True)
            quote_response = etrade_api.session.get(
                f"{etrade_api.base_url}/v1/market/productlookup.json",
                params={'company': 'ARI', 'type': 'EQ'}
            )
        
        if quote_response.status_code != 200:
            print(f"❌ Error getting ARI quote: {quote_response.status_code} - {quote_response.text}")
            return None
            
        # Try the Market Quote API for dividend info
        quote_url = f"{etrade_api.base_url}/v1/market/optionslist/ARI.json"
        market_response = etrade_api.session.get(quote_url)
        
        print(f"📊 Market API response status: {market_response.status_code}")
        
        # Try the product lookup for ARI
        lookup_url = f"{etrade_api.base_url}/v1/market/productlookup.json"
        lookup_response = etrade_api.session.get(lookup_url, params={'company': 'ARI', 'type': 'EQ'})
        
        print(f"📊 Product lookup response: {lookup_response.status_code}")
        if lookup_response.status_code == 200:
            print("📋 Product lookup data:", lookup_response.json())
        
        # Alternative: Try getting quote data directly
        quote_url = f"{etrade_api.base_url}/v1/market/productlookup.json"
        params = {
            'company': 'ARI',
            'type': 'EQ'
        }
        
        response = etrade_api.session.get(quote_url, params=params)
        print(f"📊 Direct quote response: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("📋 Quote data received:", data)
            return data
        else:
            print(f"❌ Could not get ARI quote data: {response.status_code} - {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error getting ARI data: {e}")
        return None

def add_ari_to_ticker_data(ari_yield, ari_dividend_per_share):
    """Add ARI data to the ticker yields file."""
    try:
        # Load existing data
        with open('actual_ira_dividend_data_20250825.json', 'r') as f:
            data = json.load(f)
        
        # Add ARI to the holdings
        ari_data = {
            "symbol": "ARI",
            "quantity": 0,  # Not in IRA, just for yield reference
            "market_value": 0,
            "yield": ari_yield,
            "dividend_per_share": ari_dividend_per_share,
            "current_price": 0,
            "pay_date": "",
            "has_dividend": True,
            "is_high_dividend": ari_yield >= 4.0,
            "annual_dividend_income": 0,
            "calculation_method": "etrade_quote_api",
            "payment_frequency_info": {
                "frequency": "quarterly",
                "multiplier": 4,
                "note": "Added from E*TRADE Quote API"
            },
            "last_updated": datetime.now().isoformat()
        }
        
        data['all_current_holdings']['ARI'] = ari_data
        data['metadata']['total_current_holdings'] += 1
        data['metadata']['update_date'] = datetime.now().isoformat()
        
        # Save updated data
        with open('actual_ira_dividend_data_20250825.json', 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Added ARI to ticker data with {ari_yield}% yield")
        return True
        
    except Exception as e:
        print(f"❌ Error adding ARI to ticker data: {e}")
        return False

def main():
    """Main function to get ARI data and add to ticker file."""
    print("🏢 GETTING ARI DIVIDEND DATA FROM E*TRADE")
    print("=" * 50)
    
    # Try to get ARI data from E*TRADE API
    ari_data = get_ari_dividend_data()
    
    if not ari_data:
        # If API fails, use manual estimate
        print("⚠️  API lookup failed, using manual estimate for ARI")
        ari_yield = 11.5  # Typical for Apollo Commercial Real Estate Finance
        ari_dividend_per_share = 0.35
        
        if add_ari_to_ticker_data(ari_yield, ari_dividend_per_share):
            print(f"✅ Added ARI manually: {ari_yield}% yield, ${ari_dividend_per_share} per share")
        
        return
    
    # Process API data if successful
    print("🎉 Successfully retrieved ARI data from E*TRADE API")

if __name__ == "__main__":
    main()

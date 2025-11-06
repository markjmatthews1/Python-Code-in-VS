#!/usr/bin/env python3
"""
Quick test to check QDTE yield data specifically
"""

import os
import sys

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_qdte_yield():
    """Test QDTE yield retrieval specifically"""
    
    print("Testing QDTE yield data retrieval...")
    
    try:
        from etrade_auth import get_etrade_session
        import requests
        
        # Get E*TRADE session
        session, base_url = get_etrade_session()
        
        if not session or not base_url:
            print("❌ Failed to get E*TRADE session")
            return
            
        # Test QDTE specifically
        symbol = "QDTE"
        quote_url = f"{base_url}/v1/market/quote/{symbol}.json"
        
        print(f"🔍 Testing quote for {symbol}...")
        print(f"URL: {quote_url}")
        
        response = session.get(quote_url)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            quote_data = response.json()
            print(f"Raw response: {quote_data}")
            
            # Check for yield data
            if 'QuoteResponse' in quote_data:
                quote_response = quote_data['QuoteResponse']
                if 'QuoteData' in quote_response:
                    for quote in quote_response['QuoteData']:
                        if 'All' in quote:
                            all_data = quote['All']
                            yield_value = all_data.get('yield', 'Not found')
                            dividend_yield = all_data.get('dividendYield', 'Not found')
                            print(f"Yield: {yield_value}")
                            print(f"Dividend Yield: {dividend_yield}")
                            print(f"All available fields: {list(all_data.keys())}")
        else:
            print(f"❌ HTTP Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error testing QDTE: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_qdte_yield()

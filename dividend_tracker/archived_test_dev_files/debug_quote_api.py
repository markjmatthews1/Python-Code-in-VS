#!/usr/bin/env python3
"""
Debug Quote API Issue
====================
"""

import sys
import os

# Add modules directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from etrade_auth import get_etrade_session
except ImportError as e:
    print(f"❌ ERROR: Could not import E*TRADE auth: {e}")
    sys.exit(1)

def test_single_quote():
    """Test a single quote to debug the API issue"""
    
    print("🔍 DEBUG: Testing Single Quote API Call")
    print("=" * 50)
    
    # Get session
    session, base_url = get_etrade_session()
    
    if not session:
        print("❌ Could not get E*TRADE session")
        return
    
    print(f"✅ Session established")
    print(f"🌐 Base URL: {base_url}")
    
    # Test with a simple ticker
    symbol = "AAPL"
    quote_url = f"{base_url}/v1/market/quote/{symbol}.json"
    print(f"📞 Testing API call: {quote_url}")
    
    try:
        response = session.get(quote_url)
        print(f"📊 Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ JSON Response received")
            print(f"📋 Top-level keys: {list(data.keys())}")
            
            if 'QuoteResponse' in data:
                print(f"📊 QuoteResponse keys: {list(data['QuoteResponse'].keys())}")
                if 'QuoteData' in data['QuoteResponse']:
                    quote_data = data['QuoteResponse']['QuoteData'][0]
                    print(f"📈 QuoteData keys: {list(quote_data.keys())[:10]}...")  # First 10 keys
                    
                    # Look for yield-related fields
                    yield_fields = [k for k in quote_data.keys() if 'yield' in k.lower() or 'dividend' in k.lower()]
                    print(f"💰 Yield-related fields: {yield_fields}")
                    
                    for field in yield_fields:
                        print(f"   {field}: {quote_data[field]}")
                        
        else:
            print(f"❌ Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_single_quote()

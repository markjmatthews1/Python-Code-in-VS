#!/usr/bin/env python3
"""
Quick test to verify yield data is working correctly
"""

import json
import os

def test_yield_data():
    cache_file = os.path.join(os.path.dirname(__file__), "portfolio_data_cache.json")
    
    try:
        with open(cache_file, 'r') as f:
            cache_data = json.load(f)
        
        ticker_yields = cache_data.get('ticker_yields', {})
        
        print("🧪 YIELD DATA TEST")
        print("="*30)
        
        sample_tickers = ['ABR', 'QDTE', 'PINS', 'PDI', 'AGNC']
        
        for ticker in sample_tickers:
            if ticker in ticker_yields:
                yield_data = ticker_yields[ticker]
                dividend_yield = yield_data.get('yield', 0)
                print(f"{ticker}: {dividend_yield:.2f}%")
            else:
                print(f"{ticker}: NOT FOUND")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_yield_data()
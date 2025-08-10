#!/usr/bin/env python3
"""
Test script for Alpha Vantage dividend API integration
"""

import sys
sys.path.append(r'c:\Python_Projects\DividendTrackerApp\modules')

def test_alpha_vantage():
    """Test Alpha Vantage dividend data retrieval"""
    try:
        from alpha_vantage_dividends import AlphaVantageDividends
        
        print("Testing Alpha Vantage dividend API...")
        
        # Initialize client
        av_client = AlphaVantageDividends()
        
        if not av_client.api_key or av_client.api_key == 'your_alpha_vantage_api_key_here':
            print("\n*** SETUP REQUIRED ***")
            print("Please add your Alpha Vantage API key to config.ini")
            print("1. Get a free API key at: https://www.alphavantage.co/support/#api-key")
            print("2. Edit modules/config.ini")
            print("3. Replace 'your_alpha_vantage_api_key_here' with your actual API key")
            return
        
        # Test with dividend-paying stocks
        test_symbols = ['ABR', 'O', 'T']  # Arbor Realty, Realty Income, AT&T
        
        for symbol in test_symbols:
            print(f"\n--- Testing {symbol} ---")
            result = av_client.get_dividend_data(symbol)
            
            if result:
                for key, value in result.items():
                    print(f"  {key}: {value}")
            else:
                print("  No data returned")
        
        print("\n--- Testing Portfolio Integration ---")
        # Test portfolio-style data
        test_positions = [
            {'symbol': 'ABR', 'quantity': 100},
            {'symbol': 'O', 'quantity': 50}
        ]
        
        portfolio_df = av_client.get_portfolio_dividends(test_positions)
        
        if not portfolio_df.empty:
            print("Portfolio dividend estimates:")
            print(portfolio_df.to_string())
        else:
            print("No portfolio data returned")
            
    except Exception as e:
        print(f"Error during test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alpha_vantage()

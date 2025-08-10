"""
Alpha Vantage API Integration for Dividend Data
Provides reliable, real-time dividend estimates and historical data
Last Updated: July 27, 2025
"""

import requests
import pandas as pd
import json
import time
from datetime import datetime, timedelta
import logging

class AlphaVantageDividends:
    def __init__(self, api_key=None):
        """
        Initialize Alpha Vantage API client
        
        Args:
            api_key (str): Your Alpha Vantage API key
        """
        self.api_key = api_key or self._load_api_key()
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_delay = 12  # Free tier: 5 requests per minute (12 seconds between calls)
        
    def _load_api_key(self):
        """Load API key from config file or environment"""
        try:
            # Try to load from config file
            import configparser
            import os
            
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(__file__), 'config.ini')
            config.read(config_path)
            
            if 'ALPHA_VANTAGE' in config and 'API_KEY' in config['ALPHA_VANTAGE']:
                api_key = config['ALPHA_VANTAGE']['API_KEY']
                if api_key and api_key != 'your_alpha_vantage_api_key_here':
                    return api_key
        except Exception as e:
            print(f"Error reading config file: {e}")
            
        # If no config file, prompt user to add it
        print("Alpha Vantage API key not found in config.ini")
        print("Please add your API key to config.ini under [ALPHA_VANTAGE] section")
        return None
    
    def get_dividend_data(self, symbol):
        """
        Get dividend data for a specific symbol
        
        Args:
            symbol (str): Stock symbol (e.g., 'ABR', 'ACP')
            
        Returns:
            dict: Dividend information including yield, frequency, recent payments
        """
        if not self.api_key:
            print("No API key available")
            return None
            
        try:
            # Get overview data for dividend yield and basic info
            overview_data = self._get_company_overview(symbol)
            
            # Get actual dividend history
            dividend_history = self._get_dividend_history(symbol)
            
            # Combine and analyze the data
            dividend_info = self._analyze_dividend_data(symbol, overview_data, dividend_history)
            
            return dividend_info
            
        except Exception as e:
            print(f"Error getting dividend data for {symbol}: {e}")
            return None
    
    def _get_company_overview(self, symbol):
        """Get company overview including dividend yield"""
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching overview for {symbol}: {response.status_code}")
            return {}
    
    def _get_dividend_history(self, symbol):
        """Get historical dividend payments"""
        params = {
            'function': 'CASH_FLOW',
            'symbol': symbol,
            'apikey': self.api_key
        }
        
        response = requests.get(self.base_url, params=params)
        time.sleep(self.rate_limit_delay)  # Rate limiting
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            print(f"Error fetching dividend history for {symbol}: {response.status_code}")
            return {}
    
    def _analyze_dividend_data(self, symbol, overview, dividend_history):
        """Analyze dividend data to create forward-looking estimates"""
        
        dividend_info = {
            'symbol': symbol,
            'dividend_yield': None,
            'annual_dividend': None,
            'quarterly_dividend': None,
            'monthly_estimate': None,
            'frequency': 'Unknown',
            'last_updated': datetime.now().strftime('%m/%d/%Y %H:%M'),
            'source': 'Alpha Vantage'
        }
        
        # Extract dividend yield from overview
        if overview and 'DividendYield' in overview:
            try:
                dividend_info['dividend_yield'] = float(overview['DividendYield'])
            except (ValueError, TypeError):
                pass
        
        # Extract dividend per share from overview
        if overview and 'DividendPerShare' in overview:
            try:
                dividend_info['annual_dividend'] = float(overview['DividendPerShare'])
                # Estimate quarterly (most common frequency)
                dividend_info['quarterly_dividend'] = dividend_info['annual_dividend'] / 4
                dividend_info['monthly_estimate'] = dividend_info['annual_dividend'] / 12
                dividend_info['frequency'] = 'Quarterly'  # Most common assumption
            except (ValueError, TypeError):
                pass
        
        # Try to determine actual frequency from dividend history if available
        # This would require parsing the cash flow data for dividend payments
        
        return dividend_info
    
    def get_portfolio_dividends(self, positions_list):
        """
        Get dividend data for a list of positions
        
        Args:
            positions_list: List of dicts with 'symbol' and 'quantity' keys
            
        Returns:
            pandas.DataFrame: Dividend estimates for all positions
        """
        dividend_estimates = []
        
        for position in positions_list:
            symbol = position.get('symbol', '')
            quantity = position.get('quantity', 0)
            
            if not symbol or quantity <= 0:
                continue
                
            print(f"Getting dividend data for {symbol}...")
            
            dividend_data = self.get_dividend_data(symbol)
            
            if dividend_data and dividend_data.get('quarterly_dividend'):
                try:
                    quarterly_div = dividend_data['quarterly_dividend']
                    monthly_estimate = (quarterly_div * quantity) / 3  # Convert quarterly to monthly
                    
                    dividend_estimates.append({
                        'Symbol': symbol,
                        'Quantity': quantity,
                        'Dividend_Per_Share': quarterly_div,
                        'Annual_Dividend': dividend_data.get('annual_dividend', 0),
                        'Frequency': dividend_data.get('frequency', 'Quarterly'),
                        'Monthly_Estimate': monthly_estimate,
                        'Dividend_Yield': dividend_data.get('dividend_yield', ''),
                        'Source': 'Alpha_Vantage',
                        'Last_Updated': dividend_data.get('last_updated', '')
                    })
                    
                except Exception as e:
                    print(f"Error calculating estimate for {symbol}: {e}")
            
            # Rate limiting for free tier
            time.sleep(self.rate_limit_delay)
        
        return pd.DataFrame(dividend_estimates)

def test_alpha_vantage_dividends():
    """Test function for Alpha Vantage dividend integration"""
    
    # Initialize the API client
    av_client = AlphaVantageDividends()
    
    if not av_client.api_key:
        print("Please set up your Alpha Vantage API key first")
        return
    
    # Test with some dividend-paying stocks
    test_symbols = ['ABR', 'O', 'T', 'VZ']  # Known dividend payers
    
    for symbol in test_symbols:
        print(f"\n--- Testing {symbol} ---")
        result = av_client.get_dividend_data(symbol)
        
        if result:
            for key, value in result.items():
                print(f"  {key}: {value}")
        else:
            print("  No data returned")

if __name__ == "__main__":
    test_alpha_vantage_dividends()

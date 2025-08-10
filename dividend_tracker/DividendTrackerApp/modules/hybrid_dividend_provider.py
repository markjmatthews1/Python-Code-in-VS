"""
Alpha Vantage Dividend Data Provider
Uses Alpha Vantage API for reliable, real-time dividend estimates
Last Updated: July 27, 2025
"""

import sys
import pandas as pd
from datetime import datetime
import logging

# Add modules to path
sys.path.append(r'C:\Python_Projects\DividendTrackerApp\modules')

try:
    from alpha_vantage_dividends import AlphaVantageDividends
except ImportError:
    print("Alpha Vantage module not found")
    AlphaVantageDividends = None

class DividendDataProvider:
    def __init__(self):
        """Initialize the dividend data provider using Alpha Vantage API"""
        self.av_client = AlphaVantageDividends() if AlphaVantageDividends else None
        
        # High-priority dividend stocks where we want the most accurate data
        self.dividend_stocks = {
            'ABR', 'ACP', 'O', 'REFI', 'NLY', 'AGNC', 'CIM', 'TWO',
            'T', 'VZ', 'KO', 'PEP', 'JNJ', 'PG', 'MCD', 'WMT',
            'SCHD', 'VYM', 'DVY', 'HDV', 'DGRO', 'VIG', 'SPHD'
        }
        
    def get_dividend_estimates(self, positions_list):
        """
        Get dividend estimates for a list of positions using Alpha Vantage API
        
        Args:
            positions_list: List of dicts with 'symbol' and 'quantity' keys
            
        Returns:
            pandas.DataFrame: Dividend estimates with monthly projections
        """
        
        if not self.av_client:
            print("Alpha Vantage client not available")
            return pd.DataFrame()
            
        dividend_estimates = []
        
        print("Getting dividend estimates from Alpha Vantage...")
        
        for position in positions_list:
            symbol = position.get('symbol', '').upper()
            quantity = position.get('quantity', 0)
            account_type = position.get('account_type', 'Unknown')
            
            if not symbol or quantity <= 0:
                continue
                
            print(f"  Fetching dividend data for {symbol}...")
            
            try:
                dividend_data = self.av_client.get_dividend_data(symbol)
                
                if dividend_data:
                    quarterly_div = dividend_data.get('quarterly_dividend', 0)
                    annual_div = dividend_data.get('annual_dividend', 0)
                    dividend_yield = dividend_data.get('dividend_yield', 0)
                    
                    # Calculate monthly estimate
                    if quarterly_div > 0:
                        monthly_estimate = (quarterly_div * quantity) / 3
                    elif annual_div > 0:
                        monthly_estimate = (annual_div * quantity) / 12
                    else:
                        monthly_estimate = 0
                    
                    dividend_estimates.append({
                        'Symbol': symbol,
                        'Quantity': quantity,
                        'Account_Type': account_type,
                        'Dividend_Per_Share': quarterly_div if quarterly_div > 0 else annual_div / 4,
                        'Annual_Dividend': annual_div,
                        'Frequency': dividend_data.get('frequency', 'Quarterly'),
                        'Monthly_Estimate': monthly_estimate,
                        'Dividend_Yield': f"{dividend_yield:.1%}" if dividend_yield else 'N/A',
                        'Source': 'Alpha_Vantage',
                        'Data_Quality': 'High'
                    })
                else:
                    print(f"    No dividend data found for {symbol}")
                    
            except Exception as e:
                print(f"    Error getting data for {symbol}: {e}")
                
        # Convert to DataFrame
        df = pd.DataFrame(dividend_estimates)
        
        if not df.empty:
            # Add metadata
            df['Last_Updated'] = datetime.now().strftime('%m/%d/%Y %H:%M')
            
            # Sort by monthly estimate (highest first)
            df = df.sort_values('Monthly_Estimate', ascending=False).reset_index(drop=True)
        
        return df
    
    def get_portfolio_summary(self, positions_list):
        """
        Get a summary of dividend estimates for the entire portfolio
        
        Returns:
            dict: Summary statistics
        """
        
        df = self.get_dividend_estimates(positions_list)
        
        if df.empty:
            return {
                'total_monthly': 0,
                'total_annual': 0,
                'stock_count': 0,
                'avg_yield': 0
            }
        
        total_monthly = df['Monthly_Estimate'].sum()
        total_annual = total_monthly * 12
        stock_count = len(df)
        
        # Calculate weighted average yield
        yields = []
        for _, row in df.iterrows():
            try:
                yield_str = row['Dividend_Yield'].replace('%', '')
                if yield_str != 'N/A':
                    yields.append(float(yield_str))
            except:
                pass
        
        avg_yield = sum(yields) / len(yields) if yields else 0
        
        return {
            'total_monthly': total_monthly,
            'total_annual': total_annual,
            'stock_count': stock_count,
            'avg_yield': avg_yield,
            'top_performers': df.head(5)[['Symbol', 'Monthly_Estimate', 'Dividend_Yield']].to_dict('records')
        }

def test_dividend_provider():
    """Test the dividend data provider"""
    
    provider = DividendDataProvider()
    
    # Test positions - focus on known dividend stocks
    test_positions = [
        {'symbol': 'ABR', 'quantity': 100, 'account_type': 'IRA'},
        {'symbol': 'O', 'quantity': 50, 'account_type': 'Taxable'},
        {'symbol': 'ACP', 'quantity': 200, 'account_type': 'IRA'},
        {'symbol': 'T', 'quantity': 25, 'account_type': 'Taxable'},
        {'symbol': 'VZ', 'quantity': 30, 'account_type': 'IRA'}
    ]
    
    print("Testing Alpha Vantage dividend provider...")
    
    # Get detailed estimates
    result_df = provider.get_dividend_estimates(test_positions)
    
    if not result_df.empty:
        print("\nDividend Estimates:")
        print(result_df.to_string())
        
        # Get portfolio summary
        summary = provider.get_portfolio_summary(test_positions)
        
        print(f"\n--- Portfolio Summary ---")
        print(f"Total Monthly Dividend: ${summary['total_monthly']:.2f}")
        print(f"Total Annual Dividend: ${summary['total_annual']:.2f}")
        print(f"Number of Dividend Stocks: {summary['stock_count']}")
        print(f"Average Dividend Yield: {summary['avg_yield']:.1f}%")
        
        print("\nTop Dividend Contributors:")
        for stock in summary['top_performers']:
            print(f"  {stock['Symbol']}: ${stock['Monthly_Estimate']:.2f}/month ({stock['Dividend_Yield']})")
            
    else:
        print("No dividend estimates returned")

if __name__ == "__main__":
    test_dividend_provider()

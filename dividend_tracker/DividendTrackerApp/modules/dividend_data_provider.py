"""
Production Dividend Data Provider
Uses Alpha Vantage API for reliable dividend estimates in production dividend tracker
Last Updated: July 27, 2025
"""

import sys
import pandas as pd
from datetime import datetime
import os

# Add modules to path
sys.path.append(os.path.dirname(__file__))

try:
    from alpha_vantage_dividends import AlphaVantageDividends
except ImportError:
    print("Alpha Vantage module not found")
    AlphaVantageDividends = None

def get_dividend_estimates_for_positions(positions_list, account_filter=None):
    """
    Main function to get dividend estimates for portfolio positions
    
    Args:
        positions_list: List of dicts with 'symbol', 'quantity', and optionally 'account_type'
        account_filter: Optional filter for specific account types ('IRA', 'Taxable', etc.)
        
    Returns:
        pandas.DataFrame: Dividend estimates with monthly projections
    """
    
    # Initialize Alpha Vantage client
    av_client = AlphaVantageDividends() if AlphaVantageDividends else None
    
    if not av_client:
        print("Alpha Vantage client not available")
        return pd.DataFrame()
    
    # Filter positions if account filter is specified
    if account_filter:
        positions_list = [p for p in positions_list if p.get('account_type', '').upper() == account_filter.upper()]
    
    dividend_estimates = []
    
    print(f"Getting dividend estimates for {len(positions_list)} positions...")
    
    for i, position in enumerate(positions_list, 1):
        symbol = position.get('symbol', '').upper()
        quantity = position.get('quantity', 0)
        account_type = position.get('account_type', 'Unknown')
        
        if not symbol or quantity <= 0:
            continue
            
        print(f"  ({i}/{len(positions_list)}) {symbol}...")
        
        try:
            dividend_data = av_client.get_dividend_data(symbol)
            
            if dividend_data:
                quarterly_div = dividend_data.get('quarterly_dividend', 0)
                annual_div = dividend_data.get('annual_dividend', 0)
                dividend_yield = dividend_data.get('dividend_yield', 0)
                
                # Calculate monthly estimate
                if quarterly_div > 0:
                    monthly_estimate = (quarterly_div * quantity) / 3
                    per_share_estimate = quarterly_div
                elif annual_div > 0:
                    monthly_estimate = (annual_div * quantity) / 12
                    per_share_estimate = annual_div / 4  # Assume quarterly
                else:
                    monthly_estimate = 0
                    per_share_estimate = 0
                
                dividend_estimates.append({
                    'Symbol': symbol,
                    'Quantity': quantity,
                    'Account_Type': account_type,
                    'Dividend_Per_Share': per_share_estimate,
                    'Annual_Dividend': annual_div,
                    'Frequency': dividend_data.get('frequency', 'Quarterly'),
                    'Monthly_Estimate': monthly_estimate,
                    'Dividend_Yield': f"{dividend_yield:.1%}" if dividend_yield else 'N/A',
                    'Last_Updated': datetime.now().strftime('%m/%d/%Y %H:%M'),
                    'Source': 'Alpha_Vantage'
                })
            else:
                # Add entry for stocks with no dividend data
                dividend_estimates.append({
                    'Symbol': symbol,
                    'Quantity': quantity,
                    'Account_Type': account_type,
                    'Dividend_Per_Share': 0,
                    'Annual_Dividend': 0,
                    'Frequency': 'None',
                    'Monthly_Estimate': 0,
                    'Dividend_Yield': 'N/A',
                    'Last_Updated': datetime.now().strftime('%m/%d/%Y %H:%M'),
                    'Source': 'Alpha_Vantage'
                })
                
        except Exception as e:
            print(f"    Error getting data for {symbol}: {e}")
            
    # Convert to DataFrame
    df = pd.DataFrame(dividend_estimates)
    
    if not df.empty:
        # Sort by monthly estimate (highest first)
        df = df.sort_values('Monthly_Estimate', ascending=False).reset_index(drop=True)
    
    return df

def get_dividend_summary(positions_list, account_filter=None):
    """
    Get summary statistics for dividend estimates
    
    Returns:
        dict: Summary with totals and key metrics
    """
    
    df = get_dividend_estimates_for_positions(positions_list, account_filter)
    
    if df.empty:
        return {
            'total_monthly': 0,
            'total_annual': 0,
            'dividend_paying_stocks': 0,
            'total_stocks': 0,
            'avg_yield': 0
        }
    
    # Filter out non-dividend paying stocks for yield calculation
    dividend_stocks = df[df['Monthly_Estimate'] > 0]
    
    total_monthly = df['Monthly_Estimate'].sum()
    total_annual = total_monthly * 12
    dividend_paying_count = len(dividend_stocks)
    total_stock_count = len(df)
    
    # Calculate average yield for dividend-paying stocks only
    yields = []
    for _, row in dividend_stocks.iterrows():
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
        'dividend_paying_stocks': dividend_paying_count,
        'total_stocks': total_stock_count,
        'avg_yield': avg_yield,
        'top_dividend_stocks': dividend_stocks.head(5)[['Symbol', 'Monthly_Estimate', 'Dividend_Yield']].to_dict('records') if not dividend_stocks.empty else []
    }

def save_dividend_estimates_to_excel(positions_list, filename=None):
    """
    Save dividend estimates to Excel file
    
    Args:
        positions_list: List of position dictionaries
        filename: Optional filename (default: auto-generated with timestamp)
        
    Returns:
        str: Path to saved file
    """
    
    df = get_dividend_estimates_for_positions(positions_list)
    
    if df.empty:
        print("No dividend data to save")
        return None
    
    if not filename:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M')
        filename = f"dividend_estimates_{timestamp}.xlsx"
    
    # Add summary sheet
    summary = get_dividend_summary(positions_list)
    
    try:
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Main data sheet
            df.to_excel(writer, sheet_name='Dividend_Estimates', index=False)
            
            # Summary sheet
            summary_df = pd.DataFrame([
                ['Total Monthly Dividend', f"${summary['total_monthly']:.2f}"],
                ['Total Annual Dividend', f"${summary['total_annual']:.2f}"],
                ['Dividend Paying Stocks', summary['dividend_paying_stocks']],
                ['Total Stocks', summary['total_stocks']],
                ['Average Dividend Yield', f"{summary['avg_yield']:.1f}%"],
                ['Generated', datetime.now().strftime('%m/%d/%Y %H:%M')]
            ], columns=['Metric', 'Value'])
            
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
        
        print(f"Dividend estimates saved to: {filename}")
        return filename
        
    except Exception as e:
        print(f"Error saving to Excel: {e}")
        return None

# Example usage and testing
if __name__ == "__main__":
    # Test with sample positions
    test_positions = [
        {'symbol': 'ABR', 'quantity': 100, 'account_type': 'IRA'},
        {'symbol': 'O', 'quantity': 50, 'account_type': 'Taxable'},
        {'symbol': 'T', 'quantity': 25, 'account_type': 'IRA'},
        {'symbol': 'AAPL', 'quantity': 10, 'account_type': 'Taxable'}  # Low dividend
    ]
    
    print("=== Testing Dividend Data Provider ===")
    
    # Get estimates
    estimates_df = get_dividend_estimates_for_positions(test_positions)
    
    if not estimates_df.empty:
        print("\nDividend Estimates:")
        print(estimates_df.to_string())
        
        # Get summary
        summary = get_dividend_summary(test_positions)
        
        print(f"\n=== Portfolio Summary ===")
        print(f"Total Monthly Dividend: ${summary['total_monthly']:.2f}")
        print(f"Total Annual Dividend: ${summary['total_annual']:.2f}")
        print(f"Dividend Paying Stocks: {summary['dividend_paying_stocks']}/{summary['total_stocks']}")
        print(f"Average Dividend Yield: {summary['avg_yield']:.1f}%")
        
        if summary['top_dividend_stocks']:
            print(f"\nTop Dividend Contributors:")
            for stock in summary['top_dividend_stocks']:
                print(f"  {stock['Symbol']}: ${stock['Monthly_Estimate']:.2f}/month ({stock['Dividend_Yield']})")
                
    else:
        print("No dividend estimates returned")

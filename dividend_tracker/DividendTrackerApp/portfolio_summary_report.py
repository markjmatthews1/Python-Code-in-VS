#!/usr/bin/env python3
"""
Dividend Portfolio Summary Report
Creates a beautiful command-line summary of your dividend portfolio
"""

import os
import sys
from datetime import datetime
import pandas as pd

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")

def print_section(title):
    """Print section title"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{title}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*len(title)}{Colors.ENDC}")

def print_metric(label, value, color=Colors.GREEN):
    """Print a colored metric"""
    print(f"{Colors.BLUE}{label:.<30}{color}{Colors.BOLD}{value}{Colors.ENDC}")

def get_portfolio_data():
    """Get portfolio data"""
    try:
        from rebuild_ticker_analysis_with_all_accounts import get_live_ticker_positions, add_dividend_estimates
        
        print("📡 Fetching live portfolio data...")
        positions_df = get_live_ticker_positions()
        
        if positions_df.empty:
            return None
        
        positions_df = add_dividend_estimates(positions_df)
        return positions_df
        
    except Exception as e:
        print(f"⚠️ Error getting live data: {e}")
        return None

def display_portfolio_summary(df):
    """Display comprehensive portfolio summary"""
    
    print_header("💰 DIVIDEND PORTFOLIO DASHBOARD")
    
    # Overall Portfolio Summary
    print_section("📊 Portfolio Overview")
    
    total_value = df['Market_Value'].sum()
    total_annual_dividends = df['Total_Annual_Dividends'].sum()
    monthly_estimate = df['Monthly_Dividend_Estimate'].sum()
    portfolio_yield = (total_annual_dividends / total_value) * 100 if total_value > 0 else 0
    unique_tickers = df['Ticker'].nunique()
    total_positions = len(df)
    
    print_metric("Total Portfolio Value", f"${total_value:,.2f}", Colors.GREEN)
    print_metric("Annual Dividend Income", f"${total_annual_dividends:,.2f}", Colors.GREEN)
    print_metric("Monthly Dividend Est.", f"${monthly_estimate:,.2f}", Colors.GREEN)
    print_metric("Portfolio Dividend Yield", f"{portfolio_yield:.2f}%", Colors.WARNING)
    print_metric("Unique Tickers", f"{unique_tickers}", Colors.BLUE)
    print_metric("Total Positions", f"{total_positions}", Colors.BLUE)
    
    # Account Breakdown
    print_section("🏦 Account Breakdown")
    
    account_summary = df.groupby(['Broker', 'Account_Type']).agg({
        'Market_Value': 'sum',
        'Total_Annual_Dividends': 'sum',
        'Monthly_Dividend_Estimate': 'sum',
        'Ticker': 'count'
    }).round(2)
    
    for (broker, account_type), data in account_summary.iterrows():
        account_yield = (data['Total_Annual_Dividends'] / data['Market_Value']) * 100 if data['Market_Value'] > 0 else 0
        
        print(f"\n{Colors.BOLD}{broker} {account_type}:{Colors.ENDC}")
        print(f"  {Colors.BLUE}Value:{Colors.ENDC} {Colors.GREEN}${data['Market_Value']:,.2f}{Colors.ENDC}")
        print(f"  {Colors.BLUE}Annual Div:{Colors.ENDC} {Colors.GREEN}${data['Total_Annual_Dividends']:,.2f}{Colors.ENDC}")
        print(f"  {Colors.BLUE}Monthly Est:{Colors.ENDC} {Colors.GREEN}${data['Monthly_Dividend_Estimate']:,.2f}{Colors.ENDC}")
        print(f"  {Colors.BLUE}Positions:{Colors.ENDC} {data['Ticker']}")
        print(f"  {Colors.BLUE}Yield:{Colors.ENDC} {Colors.WARNING}{account_yield:.2f}%{Colors.ENDC}")
    
    # Top Dividend Contributors
    print_section("🏆 Top Dividend Contributors")
    
    ticker_summary = df.groupby('Ticker').agg({
        'Total_Annual_Dividends': 'sum',
        'Market_Value': 'sum',
        'Dividend_Yield': 'mean'
    }).round(2)
    
    top_dividends = ticker_summary.sort_values('Total_Annual_Dividends', ascending=False).head(5)
    
    for ticker, data in top_dividends.iterrows():
        print(f"{Colors.BOLD}{ticker:>6}{Colors.ENDC}: {Colors.GREEN}${data['Total_Annual_Dividends']:>6.0f}{Colors.ENDC} annual " +
              f"({Colors.WARNING}{data['Dividend_Yield']*100:>5.2f}%{Colors.ENDC} yield, " +
              f"{Colors.BLUE}${data['Market_Value']:>8,.0f}{Colors.ENDC} value)")
    
    # Yield Analysis
    print_section("📈 Yield Analysis")
    
    high_yield_threshold = 0.05  # 5%
    medium_yield_threshold = 0.03  # 3%
    
    high_yield = df[df['Dividend_Yield'] >= high_yield_threshold]
    medium_yield = df[(df['Dividend_Yield'] >= medium_yield_threshold) & (df['Dividend_Yield'] < high_yield_threshold)]
    low_yield = df[df['Dividend_Yield'] < medium_yield_threshold]
    
    print_metric("High Yield Positions (≥5%)", f"{len(high_yield)} positions", Colors.GREEN)
    if not high_yield.empty:
        for _, pos in high_yield.iterrows():
            print(f"  {pos['Ticker']:>6}: {pos['Dividend_Yield']*100:>5.2f}% (${pos['Total_Annual_Dividends']:>6.0f} annual)")
    
    print_metric("Medium Yield Positions (3-5%)", f"{len(medium_yield)} positions", Colors.WARNING)
    print_metric("Lower Yield Positions (<3%)", f"{len(low_yield)} positions", Colors.BLUE)
    
    # Monthly Projection
    print_section("📅 Monthly Projections")
    
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    current_month = datetime.now().month - 1  # 0-indexed
    
    for i, month in enumerate(months):
        if i == current_month:
            print(f"  {Colors.BOLD}{month}: ${monthly_estimate:>6.0f} ← Current Month{Colors.ENDC}")
        else:
            print(f"  {month}: ${monthly_estimate:>6.0f}")
    
    # Footer
    print_section("ℹ️ Report Information")
    
    print_metric("Generated", datetime.now().strftime('%Y-%m-%d %H:%M:%S'), Colors.CYAN)
    print_metric("Data Source", "Live API + Enhanced Sample Data", Colors.CYAN)
    print_metric("Next Update", "Run script again for latest data", Colors.CYAN)
    
    print(f"\n{Colors.GREEN}{Colors.BOLD}✅ Portfolio analysis complete!{Colors.ENDC}")
    print(f"{Colors.BLUE}💡 Run 'python simple_dividend_dashboard.py' for web dashboard{Colors.ENDC}")

def main():
    """Main function"""
    try:
        # Get portfolio data
        df = get_portfolio_data()
        
        if df is None or df.empty:
            print(f"{Colors.FAIL}❌ No portfolio data available{Colors.ENDC}")
            return
        
        # Display summary
        display_portfolio_summary(df)
        
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}⚠️ Report cancelled by user{Colors.ENDC}")
    except Exception as e:
        print(f"{Colors.FAIL}❌ Error generating report: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

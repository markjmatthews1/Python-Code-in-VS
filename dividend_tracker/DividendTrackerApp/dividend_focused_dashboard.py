#!/usr/bin/env python3
"""
Update dashboard with proper 4% dividend threshold filtering
Only tracks and calculates yields for stocks with ≥4% dividend yield
"""

from flask import Flask, render_template_string
import pandas as pd
import os
import sys
from datetime import datetime

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def get_filtered_dividend_data():
    """Get portfolio data with 4% dividend threshold filtering from Dividends_2025.xlsx"""
    print("🎯 Loading portfolio data from Dividends_2025.xlsx with 4% dividend threshold...")
    
    try:
        # Read the updated Excel file with all account data
        excel_path = os.path.join(os.path.dirname(__file__), 'outputs', 'Dividends_2025.xlsx')
        
        if not os.path.exists(excel_path):
            print(f"❌ Excel file not found: {excel_path}")
            return pd.DataFrame()
        
        df = pd.read_excel(excel_path)
        print(f"📊 Loaded {len(df)} positions from Excel file")
        print(f"📋 Columns: {list(df.columns)}")
        
        # Check what accounts we have
        if 'Account' in df.columns:
            accounts = df['Account'].unique()
            print(f"🏦 Found accounts: {accounts}")
        
        # Filter for dividend stocks (≥4% yield)
        # Use the most recent date column for current yield data
        yield_column = None
        
        # Find the most recent date column (should be the first date column)
        date_columns = [col for col in df.columns if '-2025' in str(col)]
        if date_columns:
            # Sort to get the most recent date (assuming format MM-DD-2025 or YYYY-MM-DD)
            date_columns.sort(reverse=True)
            yield_column = date_columns[0]  # Most recent date
            print(f"📈 Using current yield from most recent date: {yield_column}")
        else:
            # Fallback to other possible yield columns
            possible_yield_columns = ['Beginning Dividend Yield', 'Yield', 'Dividend_Yield', 'Current_Yield', 'yield', 'dividend_yield']
            for col in possible_yield_columns:
                if col in df.columns:
                    yield_column = col
                    print(f"📈 Using fallback yield column: {yield_column}")
                    break
        
        if yield_column:
            print(f"📈 Using yield column: {yield_column}")
            
            # Convert yield to numeric and filter for ≥4%
            df[yield_column] = pd.to_numeric(df[yield_column], errors='coerce')
            dividend_stocks = df[df[yield_column] >= 4.0].copy()
            
            print(f"🎯 Found {len(dividend_stocks)} dividend stocks with ≥4% yield")
            
            # Standardize column names to match your Excel structure
            if 'Ticker' in dividend_stocks.columns:
                dividend_stocks['ticker'] = dividend_stocks['Ticker']
            elif 'Symbol' in dividend_stocks.columns:
                dividend_stocks['ticker'] = dividend_stocks['Symbol']
            
            if 'Qty #' in dividend_stocks.columns:
                dividend_stocks['shares'] = dividend_stocks['Qty #']
            elif 'Shares' in dividend_stocks.columns:
                dividend_stocks['shares'] = dividend_stocks['Shares']
            elif 'Quantity' in dividend_stocks.columns:
                dividend_stocks['shares'] = dividend_stocks['Quantity']
            
            if 'Current Value $' in dividend_stocks.columns:
                dividend_stocks['value'] = dividend_stocks['Current Value $']
            elif 'Market_Value' in dividend_stocks.columns:
                dividend_stocks['value'] = dividend_stocks['Market_Value']
            elif 'Value' in dividend_stocks.columns:
                dividend_stocks['value'] = dividend_stocks['Value']
            
            if 'Account' in dividend_stocks.columns:
                # Map account names to more descriptive names
                account_mapping = {
                    'E*TRADE IRA': 'E*TRADE IRA',  # Keep as is
                    'E*TRADE Taxable': 'E*TRADE Taxable',  # Keep as is
                    'Etrade': 'E*TRADE IRA',  # Legacy mapping
                    'Schwab individual': 'Schwab Individual',
                    'Schwab': 'Schwab IRA',
                    'Schwab IRA': 'Schwab IRA',
                    'Schwab Individual': 'Schwab Individual'
                }
                
                dividend_stocks['account'] = dividend_stocks['Account'].map(account_mapping).fillna(dividend_stocks['Account'])
            else:
                dividend_stocks['account'] = 'Unknown Account'
            
            dividend_stocks['yield'] = dividend_stocks[yield_column]
            
            # Calculate dividend income
            dividend_stocks['monthly_dividend'] = (dividend_stocks['value'] * dividend_stocks['yield'] / 100) / 12
            dividend_stocks['annual_dividend'] = dividend_stocks['value'] * dividend_stocks['yield'] / 100
            
            return dividend_stocks[['ticker', 'shares', 'value', 'yield', 'account', 'monthly_dividend', 'annual_dividend']]
            
        else:
            print("⚠️ No yield column found in Excel file")
            print(f"Available columns: {list(df.columns)}")
            return df
            
    except Exception as e:
        print(f"❌ Error loading Excel data: {e}")
        return pd.DataFrame()

def create_dividend_focused_dashboard():
    """Create dashboard focused only on dividend stocks (≥4% yield)"""
    
    HTML_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dividend Portfolio Dashboard (≥4% Yield Only)</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 10px; text-align: center; }
            .card { background: white; margin: 20px 0; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
            .metric { display: inline-block; margin: 0 20px; text-align: center; }
            .metric-value { font-size: 2em; font-weight: bold; color: #27ae60; }
            .metric-label { color: #7f8c8d; }
            .accounts { display: flex; gap: 20px; }
            .account { flex: 1; background: #ecf0f1; padding: 15px; border-radius: 8px; }
            .positions { margin-top: 20px; }
            .position { background: #f8f9fa; margin: 5px 0; padding: 10px; border-radius: 5px; border-left: 4px solid #e74c3c; }
            .dividend-stock { border-left-color: #27ae60; }
            .refresh { text-align: center; color: #7f8c8d; }
            .filter-note { background: #fff3cd; border: 1px solid #ffeaa7; padding: 10px; border-radius: 5px; margin: 10px 0; }
        </style>
        <meta http-equiv="refresh" content="30">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>💎 DIVIDEND PORTFOLIO DASHBOARD</h1>
                <p>Tracking dividend stocks with ≥4% yield only</p>
            </div>
            
            <div class="filter-note">
                <strong>📊 Filtering Rules:</strong> Only dividend stocks with ≥4% yield are included. 
                Investment/growth stocks (&lt;4% yield) are excluded from dividend calculations.
            </div>
            
            <div class="card">
                <div class="metric">
                    <div class="metric-value">${{ "{:,.2f}".format(total_dividend_value) }}</div>
                    <div class="metric-label">Total Dividend Stock Value</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${{ "{:,.2f}".format(monthly_dividends) }}</div>
                    <div class="metric-label">Monthly Dividends</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ dividend_positions }}</div>
                    <div class="metric-label">Dividend Positions</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ "{:.2f}".format(avg_yield) }}%</div>
                    <div class="metric-label">Average Dividend Yield</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Dividend Account Breakdown</h2>
                <div class="accounts">
                    {% for account in accounts %}
                    <div class="account">
                        <h3>{{ account.name }}</h3>
                        <div><strong>${{ "{:,.2f}".format(account.value) }}</strong></div>
                        <div>{{ account.positions }} dividend positions</div>
                        <div><strong>{{ "{:.2f}".format(account.yield) }}% yield</strong></div>
                        <div>${{ "{:,.0f}".format(account.monthly_div) }}/month</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="card">
                <h2>💎 Dividend Holdings (≥4% Yield)</h2>
                <div class="positions">
                    {% for pos in dividend_positions_list %}
                    <div class="position dividend-stock">
                        <strong>{{ pos.ticker }}</strong> ({{ pos.account }}): {{ pos.shares }} shares @ {{ "{:.1f}".format(pos.yield) }}% yield
                        = <strong>${{ "{:,.0f}".format(pos.value) }}</strong> → <strong>${{ "{:.0f}".format(pos.monthly_div) }}/month</strong>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="refresh">
                <p>Last updated: {{ timestamp }}</p>
                <p>🎯 Showing dividend stocks only (≥4% yield threshold)</p>
                <p>Page refreshes automatically every 30 seconds</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    app = Flask(__name__)
    
    @app.route('/')
    def dividend_dashboard():
        try:
            # Get filtered dividend data
            df = get_filtered_dividend_data()
            
            if not df.empty:
                # Calculate key metrics
                total_dividend_value = df['value'].sum()
                monthly_dividends = df['monthly_dividend'].sum()
                dividend_positions = len(df)
                avg_yield = (df['annual_dividend'].sum() / total_dividend_value * 100) if total_dividend_value > 0 else 0
                
                # Account breakdown (dividend stocks only)
                account_breakdown = df.groupby('account').agg({
                    'value': 'sum',
                    'monthly_dividend': 'sum',
                    'annual_dividend': 'sum',
                    'ticker': 'count'
                }).round(2)
                
                accounts = []
                for account_name, data in account_breakdown.iterrows():
                    yield_pct = (data['annual_dividend'] / data['value'] * 100) if data['value'] > 0 else 0
                    accounts.append({
                        'name': account_name,
                        'value': data['value'],
                        'positions': data['ticker'],
                        'yield': yield_pct,
                        'monthly_div': data['monthly_dividend']
                    })
                
                # Top dividend positions
                top_positions = df.nlargest(10, 'value')
                positions = []
                for _, row in top_positions.iterrows():
                    positions.append({
                        'ticker': row['ticker'],
                        'account': row['account'],
                        'shares': row['shares'],
                        'value': row['value'],
                        'yield': row['yield'],
                        'monthly_div': row['monthly_dividend']
                    })
                
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                return render_template_string(HTML_TEMPLATE,
                    total_dividend_value=total_dividend_value,
                    monthly_dividends=monthly_dividends,
                    dividend_positions=dividend_positions,
                    avg_yield=avg_yield,
                    accounts=accounts,
                    dividend_positions_list=positions,
                    timestamp=timestamp
                )
            else:
                return "<h1>No dividend data available (≥4% yield)</h1>"
                
        except Exception as e:
            return f"<h1>Error loading dividend data: {e}</h1>"
    
    return app

if __name__ == '__main__':
    print("🚀 Starting Dividend-Focused Dashboard (≥4% yield only)...")
    print("📊 Loading dividend stocks with 4% minimum yield threshold...")
    print("🌐 Dashboard available at: http://127.0.0.1:8052")
    print("💡 Press Ctrl+C to stop")
    
    app = create_dividend_focused_dashboard()
    app.run(debug=True, host='127.0.0.1', port=8052, use_reloader=False)

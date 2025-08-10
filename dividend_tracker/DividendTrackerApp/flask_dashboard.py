#!/usr/bin/env python3
"""
Simple Flask-based Portfolio Dashboard
Creates a basic web dashboard showing your real portfolio data
"""

try:
    from flask import Flask, render_template_string
    import sys
    import os
    
    # Add modules path
    sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))
    
    # Import our data function
    from rebuild_ticker_analysis_with_all_accounts import get_live_ticker_positions, add_dividend_estimates
    
    app = Flask(__name__)
    
    HTML_TEMPLATE = '''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Real Portfolio Dashboard</title>
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
            .position { background: #f8f9fa; margin: 5px 0; padding: 10px; border-radius: 5px; border-left: 4px solid #3498db; }
            .refresh { text-align: center; color: #7f8c8d; }
        </style>
        <meta http-equiv="refresh" content="30">
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🎉 YOUR REAL PORTFOLIO DASHBOARD</h1>
                <p>Live data from your E*TRADE accounts</p>
            </div>
            
            <div class="card">
                <div class="metric">
                    <div class="metric-value">${{ "{:,.2f}".format(total_value) }}</div>
                    <div class="metric-label">Total Portfolio Value</div>
                </div>
                <div class="metric">
                    <div class="metric-value">${{ "{:,.2f}".format(monthly_dividends) }}</div>
                    <div class="metric-label">Monthly Dividends</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ unique_tickers }}</div>
                    <div class="metric-label">Unique Tickers</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ total_positions }}</div>
                    <div class="metric-label">Total Positions</div>
                </div>
            </div>
            
            <div class="card">
                <h2>📊 Account Breakdown</h2>
                <div class="accounts">
                    {% for account in accounts %}
                    <div class="account">
                        <h3>{{ account.name }}</h3>
                        <div><strong>${{ "{:,.2f}".format(account.value) }}</strong></div>
                        <div>{{ account.positions }} positions</div>
                        <div>{{ "{:.2f}".format(account.yield) }}% yield</div>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="card">
                <h2>🏆 Top Holdings</h2>
                <div class="positions">
                    {% for pos in top_positions %}
                    <div class="position">
                        <strong>{{ pos.ticker }}</strong>: {{ pos.shares }} shares @ ${{ "{:.2f}".format(pos.price) }} 
                        = <strong>${{ "{:,.2f}".format(pos.value) }}</strong>
                    </div>
                    {% endfor %}
                </div>
            </div>
            
            <div class="refresh">
                <p>Last updated: {{ timestamp }}</p>
                <p>Page refreshes automatically every 30 seconds</p>
            </div>
        </div>
    </body>
    </html>
    '''
    
    @app.route('/')
    def dashboard():
        try:
            # Get real portfolio data
            df = get_live_ticker_positions()
            if not df.empty:
                df = add_dividend_estimates(df)
                
                # Calculate metrics
                total_value = df['Market_Value'].sum()
                monthly_dividends = df['Monthly_Dividend_Estimate'].sum()
                unique_tickers = df['Ticker'].nunique()
                total_positions = len(df)
                
                # Account breakdown
                account_breakdown = df.groupby(['Broker', 'Account_Type']).agg({
                    'Market_Value': 'sum',
                    'Total_Annual_Dividends': 'sum',
                    'Ticker': 'count'
                }).round(2)
                
                accounts = []
                for (broker, account_type), data in account_breakdown.iterrows():
                    accounts.append({
                        'name': f"{broker} {account_type}",
                        'value': data['Market_Value'],
                        'positions': data['Ticker'],
                        'yield': (data['Total_Annual_Dividends'] / data['Market_Value'] * 100) if data['Market_Value'] > 0 else 0
                    })
                
                # Top positions
                top_positions = df.nlargest(10, 'Market_Value')
                positions = []
                for _, row in top_positions.iterrows():
                    positions.append({
                        'ticker': row['Ticker'],
                        'shares': row['Shares'],
                        'price': row['Price'],
                        'value': row['Market_Value']
                    })
                
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                return render_template_string(HTML_TEMPLATE,
                    total_value=total_value,
                    monthly_dividends=monthly_dividends,
                    unique_tickers=unique_tickers,
                    total_positions=total_positions,
                    accounts=accounts,
                    top_positions=positions,
                    timestamp=timestamp
                )
            else:
                return "<h1>No portfolio data available</h1>"
                
        except Exception as e:
            return f"<h1>Error loading portfolio data: {e}</h1>"
    
    if __name__ == '__main__':
        print("🚀 Starting Real Portfolio Dashboard...")
        print("📊 Loading your actual E*TRADE data...")
        print("🌐 Dashboard available at: http://127.0.0.1:8051")
        print("💡 Press Ctrl+C to stop")
        
        app.run(debug=True, host='127.0.0.1', port=8051, use_reloader=False)

except ImportError as e:
    print(f"❌ Module import error: {e}")
    print("Installing Flask...")
    import subprocess
    import sys
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'flask'])
    print("✅ Flask installed. Please run the script again.")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

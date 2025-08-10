#!/usr/bin/env python3
"""
Simple Dividend Dashboard - Real-time Portfolio Visualization
Creates a beautiful dashboard showing portfolio status across all accounts
"""

import dash
from dash import dcc, html, Input, Output
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime
import os
import sys

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import our ticker analysis module
try:
    from rebuild_ticker_analysis_with_all_accounts import get_live_ticker_positions, add_dividend_estimates
    DATA_MODULE_AVAILABLE = True
except ImportError:
    DATA_MODULE_AVAILABLE = False
    print("⚠️ Data module not available, using mock data")

# Dash app configuration
app = dash.Dash(__name__)
app.title = "Dividend Portfolio Dashboard"

# Color scheme
COLORS = {
    'etrade': '#00a651',       # E*TRADE green
    'schwab': '#003366',       # Schwab navy
    'success': '#28a745',      # Green
    'primary': '#007bff',      # Blue
    'warning': '#ffc107',      # Yellow
    'danger': '#dc3545',       # Red
    'light': '#f8f9fa',        # Light gray
    'dark': '#343a40'          # Dark gray
}

def get_sample_data():
    """Create sample data for testing"""
    return pd.DataFrame([
        {'Ticker': 'AAPL', 'Broker': 'E*TRADE', 'Account_Type': 'IRA', 'Market_Value': 15000, 'Dividend_Yield': 0.0044, 'Total_Annual_Dividends': 66},
        {'Ticker': 'MSFT', 'Broker': 'E*TRADE', 'Account_Type': 'IRA', 'Market_Value': 22500, 'Dividend_Yield': 0.0072, 'Total_Annual_Dividends': 162},
        {'Ticker': 'JNJ', 'Broker': 'E*TRADE', 'Account_Type': 'IRA', 'Market_Value': 8000, 'Dividend_Yield': 0.0290, 'Total_Annual_Dividends': 232},
        {'Ticker': 'KO', 'Broker': 'E*TRADE', 'Account_Type': 'Taxable', 'Market_Value': 11000, 'Dividend_Yield': 0.0310, 'Total_Annual_Dividends': 341},
        {'Ticker': 'PG', 'Broker': 'E*TRADE', 'Account_Type': 'Taxable', 'Market_Value': 11200, 'Dividend_Yield': 0.0240, 'Total_Annual_Dividends': 269},
        {'Ticker': 'T', 'Broker': 'Schwab', 'Account_Type': 'IRA', 'Market_Value': 5400, 'Dividend_Yield': 0.0680, 'Total_Annual_Dividends': 367},
        {'Ticker': 'VZ', 'Broker': 'Schwab', 'Account_Type': 'IRA', 'Market_Value': 6000, 'Dividend_Yield': 0.0620, 'Total_Annual_Dividends': 372},
        {'Ticker': 'IBM', 'Broker': 'Schwab', 'Account_Type': 'IRA', 'Market_Value': 5000, 'Dividend_Yield': 0.0490, 'Total_Annual_Dividends': 245},
        {'Ticker': 'XOM', 'Broker': 'Schwab', 'Account_Type': 'Individual', 'Market_Value': 8500, 'Dividend_Yield': 0.0550, 'Total_Annual_Dividends': 468},
        {'Ticker': 'CVX', 'Broker': 'Schwab', 'Account_Type': 'Individual', 'Market_Value': 7500, 'Dividend_Yield': 0.0620, 'Total_Annual_Dividends': 465}
    ])

def get_dashboard_data():
    """Get data for dashboard"""
    if DATA_MODULE_AVAILABLE:
        try:
            positions_df = get_live_ticker_positions()
            if not positions_df.empty:
                positions_df = add_dividend_estimates(positions_df)
                return positions_df, None
        except Exception as e:
            print(f"Error getting real data: {e}")
    
    # Fall back to sample data
    df = get_sample_data()
    df['Monthly_Dividend_Estimate'] = df['Total_Annual_Dividends'] / 12
    return df, None

def create_summary_cards(df):
    """Create summary metric cards"""
    total_value = df['Market_Value'].sum()
    total_annual_dividends = df['Total_Annual_Dividends'].sum()
    monthly_estimate = df['Monthly_Dividend_Estimate'].sum()
    portfolio_yield = (total_annual_dividends / total_value) * 100 if total_value > 0 else 0
    
    return html.Div([
        html.Div([
            html.H2(f"${total_value:,.0f}", style={'color': COLORS['primary'], 'margin': '0'}),
            html.P("Total Portfolio Value", style={'margin': '5px 0'})
        ], className='summary-card'),
        
        html.Div([
            html.H2(f"${monthly_estimate:.0f}", style={'color': COLORS['success'], 'margin': '0'}),
            html.P("Monthly Dividend Est.", style={'margin': '5px 0'})
        ], className='summary-card'),
        
        html.Div([
            html.H2(f"{portfolio_yield:.2f}%", style={'color': COLORS['warning'], 'margin': '0'}),
            html.P("Portfolio Yield", style={'margin': '5px 0'})
        ], className='summary-card'),
        
        html.Div([
            html.H2(f"{df['Ticker'].nunique()}", style={'color': COLORS['danger'], 'margin': '0'}),
            html.P("Unique Tickers", style={'margin': '5px 0'})
        ], className='summary-card'),
    ], style={'display': 'flex', 'justify-content': 'space-around', 'margin': '20px 0'})

def create_account_pie_chart(df):
    """Create pie chart of account breakdown"""
    account_summary = df.groupby(['Broker', 'Account_Type']).agg({
        'Market_Value': 'sum'
    }).reset_index()
    
    account_summary['Label'] = account_summary['Broker'] + ' ' + account_summary['Account_Type']
    
    fig = go.Figure(data=[go.Pie(
        labels=account_summary['Label'],
        values=account_summary['Market_Value'],
        hole=0.4,
        textinfo='label+percent'
    )])
    
    fig.update_layout(
        title='Portfolio Value by Account',
        height=400
    )
    
    return fig

def create_dividend_bar_chart(df):
    """Create bar chart of dividend income by ticker"""
    ticker_summary = df.groupby('Ticker').agg({
        'Total_Annual_Dividends': 'sum',
        'Dividend_Yield': 'mean'
    }).reset_index()
    
    ticker_summary = ticker_summary.sort_values('Total_Annual_Dividends', ascending=True)
    
    fig = go.Figure(data=[go.Bar(
        y=ticker_summary['Ticker'],
        x=ticker_summary['Total_Annual_Dividends'],
        orientation='h',
        marker_color=COLORS['success']
    )])
    
    fig.update_layout(
        title='Annual Dividend Income by Ticker',
        height=400,
        xaxis_title='Annual Dividend ($)',
        yaxis_title='Ticker'
    )
    
    return fig

# App layout
app.layout = html.Div([
    # Header
    html.Div([
        html.H1("💰 Dividend Portfolio Dashboard", style={'color': 'white', 'text-align': 'center', 'margin': '0'})
    ], style={
        'background': f'linear-gradient(90deg, {COLORS["etrade"]}, {COLORS["schwab"]})',
        'padding': '20px',
        'margin-bottom': '20px'
    }),
    
    # Auto-refresh
    dcc.Interval(
        id='interval-component',
        interval=60*1000,  # Update every minute
        n_intervals=0
    ),
    
    # Content
    html.Div(id='dashboard-content'),
    
    # Footer
    html.Div([
        html.P(id='last-update', style={'text-align': 'center', 'color': COLORS['dark']})
    ], style={'margin-top': '20px'})
    
], style={'font-family': 'Arial, sans-serif'})

# CSS styles
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        <title>Dividend Dashboard</title>
        <style>
            .summary-card {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin: 10px;
                min-width: 200px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

@app.callback(
    [Output('dashboard-content', 'children'),
     Output('last-update', 'children')],
    [Input('interval-component', 'n_intervals')]
)
def update_dashboard(n):
    """Update dashboard content"""
    df, error = get_dashboard_data()
    
    if error:
        return html.Div(f"Error: {error}", style={'color': COLORS['danger']}), f"Error at {datetime.now().strftime('%H:%M:%S')}"
    
    content = html.Div([
        create_summary_cards(df),
        
        html.Div([
            html.Div([
                dcc.Graph(figure=create_account_pie_chart(df))
            ], style={'width': '50%', 'display': 'inline-block'}),
            
            html.Div([
                dcc.Graph(figure=create_dividend_bar_chart(df))
            ], style={'width': '50%', 'display': 'inline-block'})
        ])
    ])
    
    last_update = f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    return content, last_update

if __name__ == '__main__':
    print("🚀 Starting Dividend Portfolio Dashboard...")
    print("📊 Dashboard available at: http://127.0.0.1:8051")
    print("💡 Press Ctrl+C to stop")
    
    app.run_server(debug=True, host='127.0.0.1', port=8051)

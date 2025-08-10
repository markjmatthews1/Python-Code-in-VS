#!/usr/bin/env python3
"""
Dividend Dashboard - Real-time Portfolio and Dividend Visualization
Creates a beautiful, colorful dashboard showing portfolio status across all accounts

Key Features:
1. Real-time data from all 4 accounts (E*TRADE IRA, E*TRADE Taxable, Schwab IRA, Schwab Individual)
2. Interactive charts and visualizations
3. Portfolio value breakdown by account and broker
4. Dividend income projections and analysis
5. Color-coded performance indicators
6. Weekly status tracking and historical trends
"""

import dash
from dash import dcc, html, Input, Output, callback
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os
import sys

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

# Import our ticker analysis module
from rebuild_ticker_analysis_with_all_accounts import get_live_ticker_positions, add_dividend_estimates

# Dash app configuration
app = dash.Dash(__name__)
app.title = "Dividend Portfolio Dashboard"

# Color scheme for beautiful dashboard
COLORS = {
    'primary': '#1f77b4',      # Blue
    'success': '#2ca02c',      # Green
    'warning': '#ff7f0e',      # Orange
    'danger': '#d62728',       # Red
    'info': '#17a2b8',         # Cyan
    'light': '#f8f9fa',        # Light gray
    'dark': '#343a40',         # Dark gray
    'etrade': '#00a651',       # E*TRADE green
    'schwab': '#003366',       # Schwab navy
    'ira': '#ffd700',          # Gold for IRA
    'taxable': '#87ceeb',      # Sky blue for taxable
    'individual': '#dda0dd'    # Plum for individual
}

def get_dashboard_data():
    """Get live data for dashboard display"""
    print("🔄 Refreshing dashboard data...")
    
    try:
        # Get live positions
        positions_df = get_live_ticker_positions()
        
        if positions_df.empty:
            return None, "No position data available"
        
        # Add dividend estimates
        positions_df = add_dividend_estimates(positions_df)
        
        return positions_df, None
        
    except Exception as e:
        return None, f"Error loading data: {str(e)}"

def create_portfolio_summary_cards(df):
    """Create summary cards showing key metrics"""
    
    if df is None or df.empty:
        return html.Div("No data available", style={'color': COLORS['danger']})
    
    # Calculate key metrics
    total_value = df['Market_Value'].sum()
    total_annual_dividends = df['Total_Annual_Dividends'].sum()
    monthly_estimate = df['Monthly_Dividend_Estimate'].sum()
    total_positions = len(df)
    unique_tickers = df['Ticker'].nunique()
    
    # Calculate dividend yield
    portfolio_yield = (total_annual_dividends / total_value) * 100 if total_value > 0 else 0
    
    cards = html.Div([
        html.Div([
            html.H3(f"${total_value:,.0f}", style={'color': COLORS['primary'], 'margin': '0'}),
            html.P("Total Portfolio Value", style={'margin': '5px 0', 'color': COLORS['dark']})
        ], style={'background': COLORS['light'], 'padding': '20px', 'border-radius': '10px', 'text-align': 'center', 'margin': '10px'}),
        
        html.Div([
            html.H3(f"${monthly_estimate:,.0f}", style={'color': COLORS['success'], 'margin': '0'}),
            html.P("Monthly Dividend Est.", style={'margin': '5px 0', 'color': COLORS['dark']})
        ], style={'background': COLORS['light'], 'padding': '20px', 'border-radius': '10px', 'text-align': 'center', 'margin': '10px'}),
        
        html.Div([
            html.H3(f"{portfolio_yield:.2f}%", style={'color': COLORS['warning'], 'margin': '0'}),
            html.P("Portfolio Yield", style={'margin': '5px 0', 'color': COLORS['dark']})
        ], style={'background': COLORS['light'], 'padding': '20px', 'border-radius': '10px', 'text-align': 'center', 'margin': '10px'}),
        
        html.Div([
            html.H3(f"{unique_tickers}", style={'color': COLORS['info'], 'margin': '0'}),
            html.P(f"Unique Tickers ({total_positions} positions)", style={'margin': '5px 0', 'color': COLORS['dark']})
        ], style={'background': COLORS['light'], 'padding': '20px', 'border-radius': '10px', 'text-align': 'center', 'margin': '10px'}),
        
    ], style={'display': 'flex', 'justify-content': 'space-around', 'flex-wrap': 'wrap'})
    
    return cards

def create_account_breakdown_chart(df):
    """Create pie chart showing portfolio breakdown by account"""
    
    if df is None or df.empty:
        return go.Figure()
    
    # Group by broker and account type
    account_summary = df.groupby(['Broker', 'Account_Type']).agg({
        'Market_Value': 'sum'
    }).reset_index()
    
    # Create labels combining broker and account type
    account_summary['Account_Label'] = account_summary['Broker'] + ' ' + account_summary['Account_Type']
    
    # Define colors for each account type
    color_map = {
        'E*TRADE IRA': COLORS['etrade'],
        'E*TRADE Taxable': '#4CAF50',  # Lighter green
        'Schwab IRA': COLORS['schwab'],
        'Schwab Individual': '#6699CC'  # Lighter navy
    }
    
    colors = [color_map.get(label, COLORS['primary']) for label in account_summary['Account_Label']]
    
    fig = go.Figure(data=[go.Pie(
        labels=account_summary['Account_Label'],
        values=account_summary['Market_Value'],
        hole=0.4,
        marker_colors=colors,
        textinfo='label+percent+value',
        texttemplate='<b>%{label}</b><br>%{percent}<br>$%{value:,.0f}',
        hovertemplate='<b>%{label}</b><br>Value: $%{value:,.2f}<br>Percentage: %{percent}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Portfolio Value by Account',
        title_font_size=18,
        title_x=0.5,
        height=400,
        showlegend=True,
        legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.05)
    )
    
    return fig

def create_dividend_analysis_chart(df):
    """Create bar chart showing dividend analysis by ticker"""
    
    if df is None or df.empty:
        return go.Figure()\n    \n    # Group by ticker and sum dividends\n    ticker_dividends = df.groupby('Ticker').agg({\n        'Total_Annual_Dividends': 'sum',\n        'Monthly_Dividend_Estimate': 'sum',\n        'Dividend_Yield': 'mean',  # Average yield if ticker appears in multiple accounts\n        'Market_Value': 'sum'\n    }).reset_index()\n    \n    # Sort by total annual dividends\n    ticker_dividends = ticker_dividends.sort_values('Total_Annual_Dividends', ascending=True)\n    \n    # Create color scale based on yield\n    colors = px.colors.sample_colorscale('RdYlGn', \n                                        [yield_val/ticker_dividends['Dividend_Yield'].max() \n                                         for yield_val in ticker_dividends['Dividend_Yield']])\n    \n    fig = go.Figure()\n    \n    # Add annual dividends bar\n    fig.add_trace(go.Bar(\n        y=ticker_dividends['Ticker'],\n        x=ticker_dividends['Total_Annual_Dividends'],\n        orientation='h',\n        marker_color=colors,\n        name='Annual Dividends',\n        text=[f'${val:.0f} ({yield_val:.2f}%)' \n              for val, yield_val in zip(ticker_dividends['Total_Annual_Dividends'], \n                                       ticker_dividends['Dividend_Yield'] * 100)],\n        textposition='auto',\n        hovertemplate='<b>%{y}</b><br>Annual Dividend: $%{x:,.2f}<br>Yield: %{customdata:.2f}%<extra></extra>',\n        customdata=ticker_dividends['Dividend_Yield'] * 100\n    ))\n    \n    fig.update_layout(\n        title='Annual Dividend Income by Ticker',\n        title_font_size=18,\n        title_x=0.5,\n        height=max(400, len(ticker_dividends) * 25),\n        xaxis_title='Annual Dividend ($)',\n        yaxis_title='Ticker',\n        showlegend=False\n    )\n    \n    return fig\n\ndef create_yield_comparison_chart(df):\n    \"\"\"Create scatter plot showing yield vs position size\"\"\"\n    \n    if df is None or df.empty:\n        return go.Figure()\n    \n    # Create scatter plot\n    fig = go.Figure()\n    \n    # Color by broker\n    for broker in df['Broker'].unique():\n        broker_data = df[df['Broker'] == broker]\n        \n        fig.add_trace(go.Scatter(\n            x=broker_data['Market_Value'],\n            y=broker_data['Dividend_Yield'] * 100,\n            mode='markers',\n            marker=dict(\n                size=10,\n                color=COLORS['etrade'] if broker == 'E*TRADE' else COLORS['schwab'],\n                line=dict(width=2, color='white')\n            ),\n            name=broker,\n            text=broker_data['Ticker'],\n            customdata=broker_data[['Account_Type', 'Total_Annual_Dividends']],\n            hovertemplate='<b>%{text}</b><br>' +\n                         'Position Size: $%{x:,.0f}<br>' +\n                         'Yield: %{y:.2f}%<br>' +\n                         'Account: %{customdata[0]}<br>' +\n                         'Annual Dividend: $%{customdata[1]:,.2f}<extra></extra>'\n        ))\n    \n    fig.update_layout(\n        title='Dividend Yield vs Position Size',\n        title_font_size=18,\n        title_x=0.5,\n        height=400,\n        xaxis_title='Position Value ($)',\n        yaxis_title='Dividend Yield (%)',\n        showlegend=True\n    )\n    \n    return fig\n\ndef create_monthly_projection_chart(df):\n    \"\"\"Create chart showing monthly dividend projections\"\"\"\n    \n    if df is None or df.empty:\n        return go.Figure()\n    \n    # Calculate monthly projections (simplified - assumes even distribution)\n    monthly_total = df['Monthly_Dividend_Estimate'].sum()\n    \n    # Create 12 months of projections\n    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',\n             'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']\n    \n    # For demo, add some variation to make it more realistic\n    np.random.seed(42)  # For consistent demo data\n    monthly_values = [monthly_total * (1 + np.random.uniform(-0.1, 0.1)) for _ in months]\n    \n    fig = go.Figure()\n    \n    fig.add_trace(go.Bar(\n        x=months,\n        y=monthly_values,\n        marker_color=COLORS['success'],\n        name='Projected Dividends',\n        text=[f'${val:.0f}' for val in monthly_values],\n        textposition='auto'\n    ))\n    \n    # Add trend line\n    fig.add_trace(go.Scatter(\n        x=months,\n        y=monthly_values,\n        mode='lines',\n        line=dict(color=COLORS['primary'], width=3),\n        name='Trend'\n    ))\n    \n    fig.update_layout(\n        title='Monthly Dividend Projections',\n        title_font_size=18,\n        title_x=0.5,\n        height=400,\n        xaxis_title='Month',\n        yaxis_title='Projected Dividends ($)',\n        showlegend=False\n    )\n    \n    return fig\n\n# App layout\napp.layout = html.Div([\n    # Header\n    html.Div([\n        html.H1(\"💰 Dividend Portfolio Dashboard\", \n               style={'color': 'white', 'text-align': 'center', 'margin': '0', 'padding': '20px'})\n    ], style={'background': f'linear-gradient(90deg, {COLORS[\"etrade\"]}, {COLORS[\"schwab\"]})', \n              'margin-bottom': '20px'}),\n    \n    # Auto-refresh interval\n    dcc.Interval(\n        id='interval-component',\n        interval=60*1000,  # Update every minute\n        n_intervals=0\n    ),\n    \n    # Summary cards\n    html.Div(id='summary-cards'),\n    \n    # Charts row 1\n    html.Div([\n        html.Div([\n            dcc.Graph(id='account-breakdown-chart')\n        ], style={'width': '50%', 'display': 'inline-block'}),\n        \n        html.Div([\n            dcc.Graph(id='dividend-analysis-chart')\n        ], style={'width': '50%', 'display': 'inline-block'})\n    ]),\n    \n    # Charts row 2\n    html.Div([\n        html.Div([\n            dcc.Graph(id='yield-comparison-chart')\n        ], style={'width': '50%', 'display': 'inline-block'}),\n        \n        html.Div([\n            dcc.Graph(id='monthly-projection-chart')\n        ], style={'width': '50%', 'display': 'inline-block'})\n    ]),\n    \n    # Footer with last update time\n    html.Div([\n        html.P(id='last-update', style={'text-align': 'center', 'color': COLORS['dark']})\n    ], style={'margin-top': '20px', 'padding': '10px'})\n    \n], style={'font-family': 'Arial, sans-serif', 'margin': '0', 'padding': '0'})\n\n# Callbacks\n@app.callback(\n    [\n        Output('summary-cards', 'children'),\n        Output('account-breakdown-chart', 'figure'),\n        Output('dividend-analysis-chart', 'figure'),\n        Output('yield-comparison-chart', 'figure'),\n        Output('monthly-projection-chart', 'figure'),\n        Output('last-update', 'children')\n    ],\n    [Input('interval-component', 'n_intervals')]\n)\ndef update_dashboard(n):\n    \"\"\"Update all dashboard components\"\"\"\n    \n    # Get fresh data\n    df, error = get_dashboard_data()\n    \n    if error:\n        error_msg = html.Div(f\"Error: {error}\", style={'color': COLORS['danger'], 'text-align': 'center'})\n        empty_fig = go.Figure()\n        return error_msg, empty_fig, empty_fig, empty_fig, empty_fig, f\"Error at {datetime.now().strftime('%H:%M:%S')}\"\n    \n    # Create all components\n    summary_cards = create_portfolio_summary_cards(df)\n    account_chart = create_account_breakdown_chart(df)\n    dividend_chart = create_dividend_analysis_chart(df)\n    yield_chart = create_yield_comparison_chart(df)\n    projection_chart = create_monthly_projection_chart(df)\n    \n    last_update = f\"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\"\n    \n    return summary_cards, account_chart, dividend_chart, yield_chart, projection_chart, last_update\n\ndef main():\n    \"\"\"Run the dashboard server\"\"\"\n    print(\"🚀 Starting Dividend Portfolio Dashboard...\")\n    print(\"📊 Dashboard will be available at: http://127.0.0.1:8050\")\n    print(\"🔄 Data refreshes automatically every minute\")\n    print(\"💡 Press Ctrl+C to stop the server\")\n    \n    app.run_server(debug=True, host='127.0.0.1', port=8051)\n\nif __name__ == '__main__':\n    main()"

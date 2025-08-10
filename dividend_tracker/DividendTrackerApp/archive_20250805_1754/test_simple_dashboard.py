#!/usr/bin/env python3
"""Simple test dashboard to debug issues"""

print("🔍 Testing dashboard components...")

try:
    print("1. Testing basic imports...")
    import dash
    from dash import dcc, html
    import pandas as pd
    print("   ✅ Basic imports successful")
    
    print("2. Testing Dash app creation...")
    app = dash.Dash(__name__)
    print("   ✅ Dash app created")
    
    print("3. Testing simple layout...")
    app.layout = html.Div([
        html.H1("🎉 REAL PORTFOLIO TEST"),
        html.H2("Portfolio Value: $269,229.93"),
        html.P("Monthly Dividends: $538.26"),
        html.P("This is your REAL data from E*TRADE files!")
    ])
    print("   ✅ Layout created")
    
    print("4. Starting server...")
    print("🌐 Dashboard should be available at: http://127.0.0.1:8051")
    print("📱 Press Ctrl+C to stop")
    
    app.run_server(debug=True, host='127.0.0.1', port=8051, use_reloader=False)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

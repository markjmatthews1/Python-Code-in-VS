#!/usr/bin/env python3
"""
Minimal Dashboard Test
"""

print("Starting minimal dashboard test...")

try:
    import dash
    print("✅ Dash imported")
    
    from dash import dcc, html
    print("✅ Dash components imported")
    
    import plotly.graph_objs as go
    print("✅ Plotly imported")
    
    # Create minimal app
    app = dash.Dash(__name__)
    
    app.layout = html.Div([
        html.H1("🎯 Test Dashboard"),
        html.P("If you can see this, the dashboard is working!"),
        dcc.Graph(
            figure=go.Figure(
                data=[go.Bar(x=['A', 'B', 'C'], y=[1, 2, 3])],
                layout=go.Layout(title="Test Chart")
            )
        )
    ])
    
    print("✅ App layout created")
    print("🚀 Starting server at http://127.0.0.1:8051")
    print("💡 Press Ctrl+C to stop")
    
    app.run_server(debug=False, host='127.0.0.1', port=8051)
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

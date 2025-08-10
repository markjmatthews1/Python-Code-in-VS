def start_dashboard(realtime_ds, tickers):
    #from dash import Dash, dcc, html
    """Starts the Dash dashboard."""
    if manual_run:
        print("🚀 Manually starting dashboard...")
    app.run_server(debug=True)

    """Starts the Dash dashboard with real-time stock data."""
    print("🚀 Starting Dash dashboard Function is Running!...")

    app = dash.Dash(__name__)

    df = pd.DataFrame.from_dict(realtime_ds, orient="index").reset_index()
    df.rename(columns={"index": "Ticker"}, inplace=True)

    # Define Layout
    app.layout = html.Div([
        html.H1("Top 5 Stocks & ETFs Dashboard"),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=[{'label': t, 'value': t} for t in df["Ticker"].unique()],
            value=list(df["Ticker"].unique()[:5]),
            multi=True
        ),
        html.Div([
            dcc.Graph(id='live-graph', style={'width': '48%', 'display': 'inline-block'}),
            dcc.Graph(id='volume-histogram', style={'width': '48%', 'display': 'inline-block'})
        ], style={'display': 'flex', 'justify-content': 'center'}),
        dcc.Interval(id='interval-component', interval=300000, n_intervals=0)
    ])

    @app.callback(
        [Output('live-graph', 'figure'),
         Output('volume-histogram', 'figure')],
        [Input('interval-component', 'n_intervals'),
         Input('ticker-dropdown', 'value')]
    )
    def update_graph(n, tickers):
        """Updates price and volume visuals with real-time data."""
        filtered_df = df[df["Ticker"].isin(tickers)]
        price_figure = go.Figure()
        for ticker in tickers:
            ticker_df = filtered_df[filtered_df["Ticker"] == ticker]
            price_figure.add_trace(go.Scatter(
                x=ticker_df["Datetime"],
                y=ticker_df["lastTrade"],
                mode='lines+markers',
                name=ticker
            ))
        price_figure.update_layout(title="Live Price Movement", xaxis_title="Time", yaxis_title="Price")

        volume_figure = go.Figure()
        for ticker in tickers:
            ticker_df = filtered_df[filtered_df["Ticker"] == ticker]
            volume_figure.add_trace(go.Bar(
                x=ticker_df["Datetime"],
                y=ticker_df["totalVolume"],
                name=ticker
            ))
        volume_figure.update_layout(title="Hourly Volume Trends", xaxis_title="Time", yaxis_title="Volume")

        return price_figure, volume_figure

    app.run_server(debug=True)
    if __name__ == "__main__":
        start_dashboard()
        #run_realtime_data()
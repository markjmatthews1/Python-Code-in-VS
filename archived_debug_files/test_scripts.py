import soundfile as sf
import sounddevice as sd
data, samplerate = sf.read("C:/Users/mjmat/Pythons_Code_Files/adx_alert.mp3")
sd.play(data, samplerate)
sd.wait()

exit() # stop the app at this point

if __name__ == "__main__":
    # Test a ticker you know is in your mapping and in a whale's 13F
    test_ticker = "AAPL"  # Or any S&P 500 ticker in your cusip_ticker_map.csv
    from edgar_whale import get_whale_13f_holdings
    print(f"Testing SEC EDGAR 13F holdings for whales and ticker: {test_ticker}")
    whales = [
        ("BlackRock", "0001364742"),
        ("Vanguard", "0000102909"),
        ("Berkshire Hathaway", "0001067983")
    ]
    for whale_name, whale_cik in whales:
        holdings = get_whale_13f_holdings(whale_cik)
        matches = [h for h in holdings if h.get("ticker", "").lower() == test_ticker.lower()]
        print(f"{whale_name}: {len(matches)} holdings for {test_ticker}")
        for h in matches:
            print(h)


exit() # stop the app at this point

# Dashboard script that has edit trade fix but is broke

def start_dashboard(historical_data, filtered_df, tickers, dashboard_ranks):
    import dash
    from dash import dcc, html, Input, Output, State
    import plotly.graph_objs as go
    from plotly.subplots import make_subplots
    import pandas as pd
    import numpy as np
    import os
    from datetime import datetime
    from ai_module import get_trade_recommendations

    # Helper to always load latest AI recommendations for the table
    def load_latest_ai_recommendations():
        try:
            ai_df = get_trade_recommendations(tickers, return_df=True)
            print("AI table data:", ai_df)
            return ai_df.head(5)
        except Exception as e:
            print("Error loading AI recommendations:", e)
            return pd.DataFrame(columns=["ticker", "probability", "entry", "target", "stop", "recommendation"])

    market_data_columns = ["Ticker", "week52High", "week52Low", "week52HiDate", "week52LowDate"]
    if os.path.exists("market_data.csv") and os.path.getsize("market_data.csv") > 0:
        try:
            market_data_df = pd.read_csv("market_data.csv", parse_dates=["week52HiDate", "week52LowDate"])
        except Exception as e:
            print(f"⚠️ Error reading market_data.csv: {e}")
            market_data_df = pd.DataFrame(columns=market_data_columns)
    else:
        print("⚠️ market_data.csv missing or empty, using empty DataFrame.")
        market_data_df = pd.DataFrame(columns=market_data_columns)

    def get_52w_label(ticker):
        row = market_data_df[market_data_df["Ticker"] == ticker]
        if not row.empty:
            hi = row["week52High"].iloc[0]
            lo = row["week52Low"].iloc[0]
            hi_date = row["week52HiDate"].iloc[0]
            lo_date = row["week52LowDate"].iloc[0]
            hi_date = pd.to_datetime(hi_date).strftime("%Y-%m-%d") if pd.notnull(hi_date) else ""
            lo_date = pd.to_datetime(lo_date).strftime("%Y-%m-%d") if pd.notnull(lo_date) else ""
            return f"{ticker} (H:{hi} {hi_date}, L:{lo} {lo_date})"
        return ticker

    dropdown_options = [{"label": get_52w_label(t), "value": t} for t in tickers]
    trade_ticker_options = [{"label": t, "value": t} for t in tickers]
    default_ticker = tickers[0] if tickers else ""

    today_str = datetime.now().strftime("%Y-%m-%d")
    default_open_dt = f"{today_str} 09:15"
    default_close_dt = f"{today_str} 15:45"

    settings = load_settings()
    interval = settings.get("dashboard_interval", 1)

    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.Div(id='ai-recommendations-table-container'),
        html.Div(id='dummy-div', style={'display': 'none'}),  
        html.H1("Top 5 Stocks & ETFs Dashboard"),
        html.Div([
            html.H4(f"Dashboard interval: {interval} minute(s)", style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Button(
            "Open Settings",
            id="open-settings-btn",
            n_clicks=0,
            style={
                'backgroundColor': '#3572b0',
                'color': 'white',
                'fontWeight': 'bold',
                'border': 'none',
                'padding': '8px 16px',
                'borderRadius': '5px',
                'display': 'inline-block',
                'verticalAlign': 'middle'
            }
        )
    ], style={'marginBottom': '10px', 'display': 'flex', 'alignItems': 'center'}),
        html.H3(
            "Composite Rank (1-5, 5=best): " +
            ", ".join([f"{t}: {dashboard_ranks.get(t, '')}" for t in tickers])
        ),
        dcc.Dropdown(
            id='ticker-dropdown',
            options=dropdown_options,
            value=tickers,
            multi=True
        ),
        html.Div([
            html.Div([
                html.Label("Price Height:"),
                dcc.Input(id='price-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='price-tick-count', type='number', value=30, min=2, max=100, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Label("Volume Height:"),
                dcc.Input(id='volume-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='volume-tick-count', type='number', value=30, min=2, max=100, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Label("ADX Height:"),
                dcc.Input(id='adx-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='adx-tick-count', type='number', value=100, min=2, max=100, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Label("PMO Height:"),
                dcc.Input(id='pmo-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='pmo-tick-count', type='number', value=60, min=2, max=100, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block'}),
        ], style={'marginBottom': '15px'}),
        html.Div([
            html.Div([dcc.Graph(id='price-graph')], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([dcc.Graph(id='volume-histogram')], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([dcc.Graph(id='adx-graph')], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'width': '100%', 'display': 'flex'}),
        html.Div([
            html.Div([dcc.Graph(id='pmo-graph')], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                html.H4("Latest News"),
                html.Button("Refresh News", id="refresh-news-btn", n_clicks=0, style={'margin-bottom': '10px'}),
                html.Div(id='news-table-container', style={'width': '100%'})
            ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            html.Div([
                html.H4("Whale Activity"),
                html.Div(id='whale-table-container', style={'width': '100%'})
            ], style={'width': '33%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'width': '100%', 'display': 'flex'}),
        html.Hr(),
        html.H4("Trade Log"),
        html.Div([
            html.Div([
                html.Label("Type:"),
                dcc.Dropdown(
                    id='trade-type',
                    options=[
                        {'label': 'Paper', 'value': 'Paper'},
                        {'label': 'Real', 'value': 'Real'}
                    ],
                    value='Real',
                    clearable=False,
                    style={'width': '90px', 'marginRight': '5px'}
                ),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Ticker:"),
                dcc.Dropdown(
                    id='trade-ticker',
                    options=trade_ticker_options,
                    value=default_ticker,
                    clearable=False,
                    style={'width': '90px', 'marginRight': '5px'}
                ),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Qty:"),
                dcc.Input(id='trade-qty', type='number', placeholder='Qty', style={'width': '60px', 'marginRight': '5px'}),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Open Datetime:"),
                dcc.Input(id='trade-open-datetime', type='text', value=default_open_dt, style={'width': '120px', 'marginRight': '5px'}),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Open Price:"),
                dcc.Input(id='trade-open-price', type='number', placeholder='Open Price', style={'width': '80px', 'marginRight': '5px'}),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Close Datetime:"),
                dcc.Input(id='trade-close-datetime', type='text', value=default_close_dt, style={'width': '120px', 'marginRight': '5px'}),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Close Price:"),
                dcc.Input(id='trade-close-price', type='number', placeholder='Close Price', style={'width': '80px', 'marginRight': '5px'}),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Div([
                html.Label("Notes:"),
                dcc.Input(id='trade-notes', type='text', placeholder='Notes', style={'width': '120px', 'marginRight': '5px'}),
            ], style={'display': 'inline-block', 'verticalAlign': 'top', 'marginRight': '10px'}),
            html.Button("Log Trade", id="log-trade-btn", n_clicks=0, style={'marginLeft': '10px', 'height': '40px', 'backgroundColor': '#4CAF50', 'color': 'white', 'fontWeight': 'bold'}),
        ], style={'marginBottom': '10px', 'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'center'}),
        dcc.Store(id='trade-log-store'),
        dcc.Store(id='interval-store', data=interval),
        html.Div(id='trade-log-table'),
        dcc.Interval(
            id='interval-component',
            interval=interval * 60 * 1000,  # initial value, will be updated by callback
            n_intervals=0
        ),
    ])
    @app.callback(
        Output('dummy-div', 'children'),  # <-- use dummy-div, not ai-recommendations-table-container
        Input('open-settings-btn', 'n_clicks'),
        prevent_initial_call=True
    )
    def open_settings_gui(n_clicks):
        if n_clicks:
            print("Launching settings GUI...")
            subprocess.Popen([sys.executable, "day_settings_gui.py"])
        return dash.no_update
    
    @app.callback(
        Output('ai-recommendations-table-container', 'children'),
        Input('interval-component', 'n_intervals')
    )
    def update_ai_table(n):
        latest_ai = load_latest_ai_recommendations()
        return make_ai_recommendations_table(latest_ai)

    @app.callback(
        [
            Output('price-graph', 'figure'),
            Output('volume-histogram', 'figure'),
            Output('adx-graph', 'figure'),
            Output('pmo-graph', 'figure'),
            Output('news-table-container', 'children'),
            Output('whale-table-container', 'children')
        ],
        [
            Input('interval-component', 'n_intervals'),
            Input('ticker-dropdown', 'value'),
            Input('refresh-news-btn', 'n_clicks'),
            Input('price-chart-height', 'value'),
            Input('price-tick-count', 'value'),
            Input('volume-chart-height', 'value'),
            Input('volume-tick-count', 'value'),
            Input('adx-chart-height', 'value'),
            Input('adx-tick-count', 'value'),
            Input('pmo-chart-height', 'value'),
            Input('pmo-tick-count', 'value')
        ]
    )
    def update_dash(n, selected_tickers, n_clicks,
                    price_chart_height, price_tick_count,
                    volume_chart_height, volume_tick_count,
                    adx_chart_height, adx_tick_count,
                    pmo_chart_height, pmo_tick_count):
       
        # Ensure selected_tickers is a list of non-empty, unique strings
        if isinstance(selected_tickers, str):
            selected_tickers = [selected_tickers]
        if not selected_tickers:
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No tickers selected."), html.Div("No whale data.")

                # Load data
        try:
            df = pd.read_csv("historical_data.csv", parse_dates=["Datetime"])
            # Aggregate bars for dashboard display based on settings
            settings = load_settings()  # Make sure this is imported at the top
            interval = settings.get("dashboard_interval", 1)
            if interval > 1:
                df = aggregate_bars(df, interval_minutes=interval)
            def calculate_tick_volume(df):
                """
                Given a DataFrame with columns ['Datetime', 'Ticker', 'Volume', ...] where 'Volume' is cumulative,
                compute tick-by-tick (per-row) volume for each ticker.
                Adds a new column 'TickVolume' to the DataFrame.
                """
                df["Datetime"] = pd.to_datetime(df["Datetime"])
                df = df.sort_values(["Datetime", "Ticker"])
                # Calculate tick volume as the difference in cumulative volume for each ticker
                df['TickVolume'] = df.groupby('Ticker')['Volume'].diff().fillna(df['Volume'])
                # Ensure no negative values (can happen if cumulative resets intraday)
                df['TickVolume'] = df['TickVolume'].clip(lower=0)
                return df
        except Exception as e:
            print("Error loading historical_data.csv:", e)
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No data file found."), html.Div("No whale data.")

        if "Ticker" not in df.columns:
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No Ticker column in data."), html.Div("No whale data.")

        # Only keep tickers that actually have at least one valid OHLCV row
        valid_ticker_rows = []
        for t in selected_tickers:
            if not t or not isinstance(t, str):
                continue
            tdf = df[df["Ticker"] == t]
            if not tdf[["Open", "High", "Low", "Close", "Volume"]].dropna().empty:
                valid_ticker_rows.append(t)
        subplot_titles = [f"{t} Price ({i+1})" for i, t in enumerate(valid_ticker_rows)]
        num_tickers = len(valid_ticker_rows)
        if num_tickers == 0:
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No tickers with data."), html.Div("No whale data.")

        df = df[df["Ticker"].isin(valid_ticker_rows)].copy()

        # Helper to get last N rows and assign Tick 1..N for each ticker
        def get_last_n_with_tick(df, ticker, n):
            tdf = df[df["Ticker"] == ticker].sort_values("Datetime").tail(n).copy()
            tdf["Tick"] = range(1, len(tdf) + 1)
            return tdf

        # Build DataFrames for each chart type
        # Limit to at most 5 tickers for charting
        #if len(valid_ticker_rows) > 5:
            #valid_ticker_rows = valid_ticker_rows[:5]

        price_plot_df = pd.concat([get_last_n_with_tick(df, t, price_tick_count) for t in valid_ticker_rows], ignore_index=True)
        volume_plot_df = pd.concat([get_last_n_with_tick(df, t, volume_tick_count) for t in valid_ticker_rows], ignore_index=True)
        adx_plot_df = pd.concat([get_last_n_with_tick(df, t, adx_tick_count) for t in valid_ticker_rows], ignore_index=True)
        pmo_plot_df = pd.concat([get_last_n_with_tick(df, t, pmo_tick_count) for t in valid_ticker_rows], ignore_index=True)

        # Calculate technicals on the correct DataFrames
        adx_df = calculate_adx_multi(adx_plot_df, valid_ticker_rows)
        filtered_adx_df = pd.merge(
            adx_plot_df,
            adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]],
            on=["Datetime", "Ticker"],
            how="left"
        )
        pmo_df = calculate_pmo_multi(pmo_plot_df, valid_ticker_rows)
        filtered_pmo_df = pd.merge(
            pmo_plot_df,
            pmo_df[["Datetime", "Ticker", "PMO", "PMO_signal"]],
            on=["Datetime", "Ticker"],
            how="left"
        )

        # --- Price (candlestick) charts with buy/sell signals ---
        def detect_candle_signals(tdf):
            """
            Adds buy/sell signals to a ticker DataFrame.
            Returns a list of dicts: {"Tick": ..., "Price": ..., "Signal": "Buy"/"Sell"}
            """
            signals = []
            tdf = tdf.reset_index(drop=True)
            for i in range(1, len(tdf)):
                o1, c1 = tdf.loc[i-1, "Open"], tdf.loc[i-1, "Close"]
                o2, c2 = tdf.loc[i, "Open"], tdf.loc[i, "Close"]
                h2, l2 = tdf.loc[i, "High"], tdf.loc[i, "Low"]
                tick = tdf.loc[i, "Tick"]

                # Bullish Engulfing
                if (c2 > o2 and c1 < o1 and o2 < c1 and c2 > o1):
                    signals.append({"Tick": tick, "Price": l2, "Signal": "Buy"})
                # Bearish Engulfing
                if (c2 < o2 and c1 > o1 and o2 > c1 and c2 < o1):
                    signals.append({"Tick": tick, "Price": h2, "Signal": "Sell"})
                # Hammer (bullish reversal)
                body = abs(c2 - o2)
                lower_shadow = min(o2, c2) - l2
                upper_shadow = h2 - max(o2, c2)
                if body < upper_shadow and lower_shadow > 2 * body:
                    signals.append({"Tick": tick, "Price": l2, "Signal": "Buy"})
                # Inverted Hammer (bearish reversal)
                if body < lower_shadow and upper_shadow > 2 * body:
                    signals.append({"Tick": tick, "Price": h2, "Signal": "Sell"})
            return signals

        price_fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.08,
            subplot_titles=subplot_titles,
            row_heights=[1]*num_tickers
        )
        for i, ticker in enumerate(valid_ticker_rows, start=1):
            ticker_df = price_plot_df[price_plot_df["Ticker"] == ticker].copy()
            ticker_df = ticker_df.sort_values("Tick")
            price_fig.add_trace(
                go.Candlestick(
                    x=ticker_df["Tick"],
                    open=ticker_df["Open"],
                    high=ticker_df["High"],
                    low=ticker_df["Low"],
                    close=ticker_df["Close"],
                    increasing_line_color="green",
                    decreasing_line_color="red",
                    name=f"{ticker} Price"
                ),
                row=i, col=1
            )
            # --- Add buy/sell markers ---
            signals = detect_candle_signals(ticker_df)
            for sig in signals:
                color = "green" if sig["Signal"] == "Buy" else "red"
                marker_symbol = "arrow-up" if sig["Signal"] == "Buy" else "arrow-down"
                price_fig.add_trace(
                    go.Scatter(
                        x=[sig["Tick"]],
                        y=[sig["Price"]],
                        mode="markers+text",
                        marker=dict(symbol=marker_symbol, color=color, size=16),
                        text=[sig["Signal"]],
                        textposition="top center" if sig["Signal"] == "Buy" else "bottom center",
                        name=f"{ticker} {sig['Signal']}",
                        showlegend=False
                    ),
                    row=i, col=1
                )
            price_fig.update_xaxes(nticks=price_tick_count, row=i, col=1)
        price_fig.update_layout(
            height=price_chart_height * num_tickers,
            title="Price (Candlestick)",
            showlegend=False
        )

                        # --- Volume histogram ---
        def calculate_tick_volume(df):
            df["Datetime"] = pd.to_datetime(df["Datetime"])
            df = df.sort_values(["Datetime", "Ticker"])
            df['TickVolume'] = df.groupby('Ticker')['Volume'].diff().fillna(df['Volume'])
            df['TickVolume'] = df['TickVolume'].clip(lower=0)
            return df

        volume_plot_df = calculate_tick_volume(volume_plot_df)

        volume_fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.08,
            subplot_titles=[f"{ticker} Volume" for ticker in valid_ticker_rows],
            row_heights=[1]*num_tickers
        )
        for i, ticker in enumerate(valid_ticker_rows, start=1):
            vol_df = volume_plot_df[volume_plot_df["Ticker"] == ticker].copy()
            if not vol_df.empty:
                vol_df = vol_df.sort_values("Tick")
                vol_df["PrevClose"] = vol_df["Close"].shift(1)
                vol_df["BarColor"] = np.where(vol_df["Close"] >= vol_df["PrevClose"], "green", "red")
                # Remove the first bar (which may be a large outlier)
                vol_df = vol_df.iloc[1:].copy() if len(vol_df) > 1 else vol_df
                # Optionally, clip y-axis to 99th percentile to avoid outliers
                y_max = vol_df["TickVolume"].quantile(0.99) * 1.1 if not vol_df["TickVolume"].empty else None
                volume_fig.add_trace(go.Bar(
                    x=vol_df["Tick"],
                    y=vol_df["TickVolume"],
                    marker_color=vol_df["BarColor"],
                    name=f"{ticker} Volume"
                ), row=i, col=1)
                if y_max and y_max > 0:
                    volume_fig.update_yaxes(range=[0, y_max], row=i, col=1)
                volume_fig.update_xaxes(nticks=volume_tick_count, row=i, col=1)
        volume_fig.update_layout(
            title="Volume",
            height=volume_chart_height * num_tickers,
            showlegend=False,
            barmode='group'
        )

        # --- ADX chart ---
        adx_fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.08,
            subplot_titles=[f"{ticker} ADX/DMS" for ticker in valid_ticker_rows],
            row_heights=[1]*num_tickers
        )
        for i, ticker in enumerate(valid_ticker_rows, start=1):
            adx_sub = filtered_adx_df[filtered_adx_df["Ticker"] == ticker]
            if not adx_sub.empty and "ADX" in adx_sub.columns and "+DI" in adx_sub.columns and "-DI" in adx_sub.columns:
                adx_fig.add_trace(go.Scatter(
                    x=adx_sub["Tick"],
                    y=adx_sub["ADX"],
                    mode="lines",
                    name=f"{ticker} ADX",
                    line=dict(color="blue")
                ), row=i, col=1)
                adx_fig.add_trace(go.Scatter(
                    x=adx_sub["Tick"],
                    y=adx_sub["+DI"],
                    mode="lines",
                    name=f"{ticker} +DI",
                    line=dict(color="green")
                ), row=i, col=1)
                adx_fig.add_trace(go.Scatter(
                    x=adx_sub["Tick"],
                    y=adx_sub["-DI"],
                    mode="lines",
                    name=f"{ticker} -DI",
                    line=dict(color="red")
                ), row=i, col=1)
                adx_fig.update_xaxes(nticks=adx_tick_count, row=i, col=1)
        adx_fig.update_layout(
            title="ADX / DMS",
            height=adx_chart_height * num_tickers,
            showlegend=False
        )

        # --- PMO chart ---
        pmo_fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.08,
            subplot_titles=[f"{ticker} PMO" for ticker in valid_ticker_rows],
            row_heights=[1]*num_tickers
        )
        for i, ticker in enumerate(valid_ticker_rows, start=1):
            pmo_sub = filtered_pmo_df[filtered_pmo_df["Ticker"] == ticker]
            if not pmo_sub.empty and "PMO" in pmo_sub.columns and "PMO_signal" in pmo_sub.columns:
                pmo_fig.add_trace(go.Scatter(
                    x=pmo_sub["Tick"],
                    y=pmo_sub["PMO"],
                    mode="lines",
                    name=f"{ticker} PMO",
                    line=dict(color="green")
                ), row=i, col=1)
                pmo_fig.add_trace(go.Scatter(
                    x=pmo_sub["Tick"],
                    y=pmo_sub["PMO_signal"],
                    mode="lines",
                    name=f"{ticker} PMO Signal",
                    line=dict(color="red", dash="dot")
                ), row=i, col=1)
                pmo_fig.update_xaxes(nticks=pmo_tick_count, row=i, col=1)
        pmo_fig.update_layout(
            title="PMO & PMO Signal",
            height=pmo_chart_height * num_tickers,
            showlegend=False
        )

        # --- NEWS TABLE FEATURE ---
        # Always get the latest AI recommendations for the top 5 tickers
        if not top5_ai.empty:
            try:
                ai_df = get_trade_recommendations(valid_ticker_rows, return_df=True)
                top5_ai = ai_df.head(5)
            except Exception as e:
                print("Error loading AI recommendations in update_dash:", e)
                top5_ai = pd.DataFrame(columns=["ticker", "probability", "entry", "target", "stop", "recommendation"])

            news_rows = []
            news_cache = load_news_cache()
            for ticker in top5_ai["ticker"].tolist():
                # Only use cached news; do NOT call the API here
                if ticker in news_cache:
                    _, news_list = news_cache[ticker]
                else:
                    news_list = []
                for article in news_list:
                    if isinstance(article, dict):
                        news_rows.append({
                            "Ticker": ticker,  # This will always show the ETF symbol
                            "Title": article.get("title", ""),
                            "Sentiment": article.get("sentiment", "Neutral"),
                            "URL": article.get("url", f"https://www.bing.com/news/search?q={ticker}")
                        })

            if news_rows:
                news_df = pd.DataFrame(news_rows)
                table_header = [
                    html.Thead(html.Tr([
                        html.Th("Ticker"),
                        html.Th("Title"),
                        html.Th("Sentiment"),
                        html.Th("Link")
                    ]))
                ]
                table_body = [
                    html.Tbody([
                        html.Tr([
                            html.Td(row["Ticker"]),
                            html.Td(row["Title"]),
                            html.Td(row["Sentiment"]),
                            html.Td(html.A("Read", href=row["URL"], target="_blank"))
                        ]) for _, row in news_df.iterrows()
                    ])
                ]
                news_table = html.Table(table_header + table_body, style={'width': '100%', 'fontSize': '12px'})
            else:
                news_table = html.Div("No news found.", style={'fontSize': '12px'})

                # --- WHALE TABLE FEATURE ---
        whale_rows = []
        if not top5_ai.empty:
            for ticker in top5_ai["ticker"].tolist():
                # Fetch whale data for both ETF and parent if mapped
                symbols_to_search = [ticker]
                if ticker in ETF_UNDERLYING_MAP:
                    underlying = ETF_UNDERLYING_MAP[ticker]
                    if underlying not in symbols_to_search:
                        symbols_to_search.append(underlying)
                for symbol in symbols_to_search:
                    whale_data = fetch_whale_data(symbol)
                    for entry in whale_data.get("insider", []):
                        whale_rows.append({
                            "Ticker": symbol,
                            "Type": "Insider",
                            "Entity": entry.get("name", ""),
                            "Shares": entry.get("share", ""),
                            "Change": entry.get("transactionType", ""),
                            "Date": entry.get("transactionDate", "")
                        })
                    for entry in whale_data.get("institutional", []):
                        whale_rows.append({
                            "Ticker": symbol,
                            "Type": "Institutional",
                            "Entity": entry.get("entityProperName", ""),
                            "Shares": entry.get("shares", ""),
                            "Change": entry.get("change", ""),
                            "Date": entry.get("reportDate", "")
                        })
                    for entry in whale_data.get("government", []):
                        whale_rows.append({
                            "Ticker": symbol,
                            "Type": "Government",
                            "Entity": entry.get("entityProperName", ""),
                            "Shares": entry.get("shares", ""),
                            "Change": entry.get("change", ""),
                            "Date": entry.get("reportDate", "")
                        })
            if whale_rows:
                whale_df = pd.DataFrame(whale_rows)
                whale_header = [
                    html.Thead(html.Tr([
                        html.Th("Ticker"),
                        html.Th("Type"),
                        html.Th("Entity"),
                        html.Th("Shares"),
                        html.Th("Change"),
                        html.Th("Date")
                    ]))
                ]
                whale_body = [
                    html.Tbody([
                        html.Tr([
                            html.Td(row["Ticker"]),
                            html.Td(row["Type"]),
                            html.Td(row["Entity"]),
                            html.Td(row["Shares"]),
                            html.Td(row["Change"]),
                            html.Td(row["Date"])
                        ]) for _, row in whale_df.iterrows()
                    ])
                ]
                whale_table = html.Table(whale_header + whale_body, style={'width': '100%', 'fontSize': '12px'})
            else:
                whale_table = html.Div("No whale data found.", style={'fontSize': '12px'})

            return price_fig, volume_fig, adx_fig, pmo_fig, news_table, whale_table

                                       # --- TRADE LOG FEATURE ---

    @app.callback(
        [
            Output('trade-log-table', 'children'),
            Output('trade-log-store', 'data'),
            Output('trade-type', 'value'),
            Output('trade-ticker', 'value'),
            Output('trade-qty', 'value'),
            Output('trade-open-datetime', 'value'),
            Output('trade-open-price', 'value'),
            Output('trade-close-datetime', 'value'),
            Output('trade-close-price', 'value'),
            Output('trade-notes', 'value')
        ],
        [Input('log-trade-btn', 'n_clicks')],
        [
            State('trade-type', 'value'),
            State('trade-ticker', 'value'),
            State('trade-qty', 'value'),
            State('trade-open-datetime', 'value'),
            State('trade-open-price', 'value'),
            State('trade-close-datetime', 'value'),
            State('trade-close-price', 'value'),
            State('trade-notes', 'value'),
            State('trade-log-store', 'data'),
            State('trade-log-table', 'selected_rows')
        ]
    )
    def log_trade(n_clicks, trade_type, ticker, qty, open_dt, open_price, close_dt, close_price, notes, store_data, selected_rows):
        print("log_trade called:", n_clicks, trade_type, ticker, qty, open_dt, open_price, close_dt, close_price, notes, store_data, selected_rows)
        TRADE_LOG_FILE = "trade_log.xlsx"
        TRADE_LOG_COLUMNS = [
            "Type", "Ticker", "Trade QTY", "Open Datetime", "Open Price",
            "Close Datetime", "Close Price", "Profit/Loss", "Profit/Loss %", "Notes"
        ]
        if store_data is not None:
            trade_log_df = pd.DataFrame(store_data)
        elif os.path.exists(TRADE_LOG_FILE):
            trade_log_df = pd.read_excel(TRADE_LOG_FILE)
        else:
            trade_log_df = pd.DataFrame(columns=TRADE_LOG_COLUMNS)

        if n_clicks:
            try:
                open_price = float(open_price)
            except Exception:
                open_price = 0.0
            try:
                close_price = float(close_price)
            except Exception:
                close_price = 0.0
            try:
                qty = int(qty)
            except Exception:
                qty = 0

            pl = (close_price - open_price) * qty if close_price and open_price and qty else ""
            pl_pct = ((close_price - open_price) / open_price * 100) if close_price and open_price else ""

            new_row = {
                "Type": trade_type,
                "Ticker": ticker,
                "Trade QTY": qty,
                "Open Datetime": open_dt,
                "Open Price": open_price,
                "Close Datetime": close_dt,
                "Close Price": close_price,
                "Profit/Loss": round(pl, 2) if pl != "" else "",
                "Profit/Loss %": round(pl_pct, 2) if pl_pct != "" else "",
                "Notes": notes
            }

            if selected_rows and len(selected_rows) > 0:
                idx = selected_rows[0]
                for col in TRADE_LOG_COLUMNS:
                    trade_log_df.at[idx, col] = new_row[col]
            else:
                trade_log_df = pd.concat([trade_log_df, pd.DataFrame([new_row])], ignore_index=True)

            for col in TRADE_LOG_COLUMNS:
                if col not in trade_log_df.columns:
                    trade_log_df[col] = ""
            trade_log_df = trade_log_df[TRADE_LOG_COLUMNS]
            try:
                trade_log_df.to_excel(TRADE_LOG_FILE, index=False)
            except Exception as e:
                print("Excel save error:", e)

            today_str = datetime.now().strftime("%Y-%m-%d")
            trade_type = "Paper"
            ticker = ""
            qty = 0
            open_dt = f"{today_str} 09:15"
            open_price = 0
            close_dt = f"{today_str} 15:45"
            close_price = 0
            notes = ""

        # Build DataTable for display and editing
        if trade_log_df.empty:
            table = html.Div("No trades logged yet.")
        else:
            table = dash_table.DataTable(
                id='trade-log-table', 
                columns=[{"name": col, "id": col} for col in TRADE_LOG_COLUMNS],
                data=trade_log_df.to_dict('records'),
                row_selectable='single',
                selected_rows=[],
                style_table={'width': '100%', 'fontSize': '13px', 'marginTop': '10px'},
                style_cell={'textAlign': 'left'},
            )

        return (
            table,
            trade_log_df.to_dict('records'),
            trade_type,
            ticker,
            qty,
            open_dt,
            open_price,
            close_dt,
            close_price,
            notes
        )
    @app.callback(
        Output('interval-component', 'interval'),
        [Input('interval-store', 'data'),
        Input('open-settings-btn', 'n_clicks'),
        Input('interval-component', 'n_intervals')]
    )
    def update_interval(interval_data, n_clicks, n_intervals):
        # Always read the latest interval from settings
        settings = load_settings()
        interval = settings.get("dashboard_interval", 1)
        return interval * 60 * 1000

    @app.callback(
        Output('interval-store', 'data'),
        [Input('open-settings-btn', 'n_clicks'),
        Input('interval-component', 'n_intervals')]
)
    def refresh_interval_store(n_clicks, n_intervals):
        settings = load_settings()
        interval = settings.get("dashboard_interval", 1)
        return interval
    
    @app.callback(
        [
            Output('trade-type', 'value'),
            Output('trade-ticker', 'value'),
            Output('trade-qty', 'value'),
            Output('trade-open-datetime', 'value'),
            Output('trade-open-price', 'value'),
            Output('trade-close-datetime', 'value'),
            Output('trade-close-price', 'value'),
            Output('trade-notes', 'value'),
        ],
        [Input('trade-log-table', 'selected_rows')],
        [State('trade-log-store', 'data')]
    )
    
    def populate_trade_fields(selected_rows, store_data):
        if not selected_rows or store_data is None:
            raise dash.exceptions.PreventUpdate
        row = store_data[selected_rows[0]]
        return (
            row.get("Type", ""),
            row.get("Ticker", ""),
            row.get("Trade QTY", 0),
            row.get("Open Datetime", ""),
            row.get("Open Price", 0),
            row.get("Close Datetime", ""),
            row.get("Close Price", 0),
            row.get("Notes", ""),
        )
    
# Dashboard call back for editing the trade log


    def populate_trade_fields(selected_rows, store_data):
        logging.debug(f"populate_trade_fields called with 1770 selected_rows={selected_rows}, store_data={store_data}")
        if not selected_rows or not store_data:
            # No row selected, return dash.no_update for all fields
            logging.debug("Trade log is empty. 1773")
            return [dash.no_update] * 8
        idx = selected_rows[0]
        row = store_data[idx]
        return (
            row.get("Type", "Paper"),
            row.get("Ticker", ""),
            row.get("Trade QTY", 0),
            row.get("Open Datetime", ""),
            row.get("Open Price", 0),
            row.get("Close Datetime", ""),
            row.get("Close Price", 0),
            row.get("Notes", ""),
        )
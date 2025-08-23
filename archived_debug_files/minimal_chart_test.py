#!/usr/bin/env python3

"""
Minimal test to reproduce the exact chart creation issue
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

print("🧪 MINIMAL CHART TEST STARTING...")

# Test 1: Basic imports
try:
    print("✅ Plotly imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    exit(1)

# Test 2: Load data exactly like dashboard
try:
    print("📊 Loading historical_data.csv...")
    df = pd.read_csv("historical_data.csv")
    print(f"✅ Loaded {len(df)} rows")
    
    # Filter exactly like dashboard
    selected_tickers = ['ETHU', 'TQQQ', 'LABU', 'JNUG', 'NVDL']
    df_filtered = df[df['Ticker'].isin(selected_tickers)].copy()
    print(f"📊 Filtered to {len(df_filtered)} rows for {len(selected_tickers)} tickers")
    
    # Parse datetime exactly like dashboard
    df_filtered['Datetime'] = pd.to_datetime(df_filtered['Datetime'], format='%Y-%m-%d %H:%M', errors='coerce')
    print(f"✅ Datetime parsed")
    
except Exception as e:
    print(f"❌ Data loading failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 3: Create make_subplots exactly like dashboard
try:
    valid_tickers = ['ETHU', 'TQQQ', 'LABU', 'JNUG', 'NVDL']
    num_tickers = len(valid_tickers)
    
    print(f"🎨 Creating make_subplots with {num_tickers} rows...")
    
    subplot_titles = [f"{t} Price ({i+1})" for i, t in enumerate(valid_tickers)]
    
    price_fig = make_subplots(
        rows=num_tickers, cols=1,
        shared_xaxes=False,
        vertical_spacing=0.08,
        subplot_titles=subplot_titles,
        row_heights=[1]*num_tickers
    )
    
    print("✅ make_subplots created successfully!")
    
except Exception as e:
    print(f"❌ make_subplots failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Test 4: Add candlestick traces exactly like dashboard  
try:
    chart_success = False
    
    for i, ticker in enumerate(valid_tickers, start=1):
        print(f"📊 Processing {ticker} (row {i})...")
        
        ticker_df = df_filtered[df_filtered["Ticker"] == ticker].copy()
        ticker_df = ticker_df.sort_values("Datetime")
        
        print(f"  📊 {ticker}: {len(ticker_df)} rows")
        
        if ticker_df.empty:
            print(f"  ❌ {ticker}: No data")
            continue
        
        # Check for required columns
        required_cols = ["Open", "High", "Low", "Close", "Datetime"]
        missing = [col for col in required_cols if col not in ticker_df.columns]
        if missing:
            print(f"  ❌ {ticker}: Missing columns: {missing}")
            continue
        
        # Check for NaN values
        ohlc_data = ticker_df[["Open", "High", "Low", "Close"]]
        if ohlc_data.isna().any().any():
            print(f"  ⚠️ {ticker}: Has NaN values in OHLC data")
            # Remove NaN rows
            ticker_df = ticker_df.dropna(subset=["Open", "High", "Low", "Close"])
            print(f"  📊 {ticker}: After cleaning: {len(ticker_df)} rows")
        
        if len(ticker_df) == 0:
            print(f"  ❌ {ticker}: No valid data after cleaning")
            continue
            
        try:
            print(f"  🕯️ Adding candlestick for {ticker}...")
            
            price_fig.add_trace(
                go.Candlestick(
                    x=ticker_df["Datetime"],
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
            
            chart_success = True
            print(f"  ✅ {ticker}: Candlestick added successfully!")
            
        except Exception as candlestick_error:
            print(f"  ❌ {ticker}: Candlestick failed: {candlestick_error}")
            import traceback
            traceback.print_exc()
            continue
    
    if chart_success:
        print(f"🎉 SUCCESS: {len(price_fig.data)} traces added to chart!")
        
        # Update layout
        price_fig.update_layout(
            height=400 * num_tickers,
            title="Minimal Chart Test - Success!",
            showlegend=False
        )
        
        # Save for testing
        price_fig.write_html("minimal_chart_test.html")
        print("💾 Saved as 'minimal_chart_test.html'")
        
    else:
        print("❌ FAILED: No charts were successfully created")
        
except Exception as e:
    print(f"❌ Chart creation failed: {e}")
    import traceback
    traceback.print_exc()

print("🧪 MINIMAL CHART TEST COMPLETED")

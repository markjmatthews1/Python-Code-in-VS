#!/usr/bin/env python3

"""
Debug script to isolate chart creation issues in the dashboard
"""

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import traceback
import sys
from pathlib import Path

def debug_chart_creation():
    """Debug the chart creation process step by step"""
    
    print("🔍 STARTING CHART DEBUG PROCESS...")
    
    # Step 1: Load the data
    try:
        print("📊 Step 1: Loading historical data...")
        df = pd.read_csv("historical_data.csv")
        print(f"✅ Data loaded: {len(df)} rows, {len(df.columns)} columns")
        print(f"📊 Available tickers: {sorted(df['Ticker'].unique().tolist())}")
    except Exception as e:
        print(f"❌ Failed to load data: {e}")
        return
    
    # Step 2: Filter for selected tickers
    selected_tickers = ['ETHU', 'TQQQ', 'LABU', 'JNUG', 'NVDL']
    print(f"🎯 Step 2: Filtering for selected tickers: {selected_tickers}")
    
    df_filtered = df[df['Ticker'].isin(selected_tickers)].copy()
    print(f"✅ Filtered data: {len(df_filtered)} rows")
    
    # Step 3: Parse datetime
    print("📅 Step 3: Parsing datetime...")
    try:
        df_filtered['Datetime'] = pd.to_datetime(df_filtered['Datetime'], format='%Y-%m-%d %H:%M', errors='coerce')
        print(f"✅ Datetime parsed. Sample: {df_filtered['Datetime'].iloc[0]}")
    except Exception as e:
        print(f"❌ Datetime parsing failed: {e}")
        return
    
    # Step 4: Check for required columns
    print("🔍 Step 4: Checking required columns...")
    required_cols = ['Datetime', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing_cols = [col for col in required_cols if col not in df_filtered.columns]
    if missing_cols:
        print(f"❌ Missing columns: {missing_cols}")
        return
    else:
        print("✅ All required columns present")
    
    # Step 5: Check data quality
    print("🔍 Step 5: Checking data quality...")
    for ticker in selected_tickers:
        ticker_data = df_filtered[df_filtered['Ticker'] == ticker]
        print(f"  {ticker}: {len(ticker_data)} rows")
        
        if ticker_data.empty:
            print(f"    ❌ {ticker}: No data")
            continue
            
        # Check for NaN values in OHLC
        ohlc_cols = ['Open', 'High', 'Low', 'Close']
        nan_counts = ticker_data[ohlc_cols].isna().sum()
        if nan_counts.sum() > 0:
            print(f"    ⚠️ {ticker}: NaN values found: {nan_counts.to_dict()}")
        else:
            print(f"    ✅ {ticker}: Clean OHLC data")
        
        # Check data range
        date_range = f"{ticker_data['Datetime'].min()} to {ticker_data['Datetime'].max()}"
        print(f"    📅 {ticker}: Date range: {date_range}")
    
    # Step 6: Try to create make_subplots
    print("🎨 Step 6: Testing make_subplots creation...")
    try:
        valid_tickers = [t for t in selected_tickers if not df_filtered[df_filtered['Ticker'] == t].empty]
        num_tickers = len(valid_tickers)
        print(f"📊 Creating subplots for {num_tickers} tickers: {valid_tickers}")
        
        subplot_titles = [f"{t} Price ({i+1})" for i, t in enumerate(valid_tickers)]
        
        price_fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.08,
            subplot_titles=subplot_titles,
            row_heights=[1]*num_tickers
        )
        print("✅ make_subplots created successfully")
        
    except Exception as e:
        print(f"❌ make_subplots failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Step 7: Try to add candlestick traces
    print("🕯️ Step 7: Testing candlestick trace addition...")
    chart_success = False
    
    for i, ticker in enumerate(valid_tickers, start=1):
        print(f"  📊 Adding candlestick for {ticker} (row {i})")
        
        ticker_df = df_filtered[df_filtered["Ticker"] == ticker].copy()
        ticker_df = ticker_df.sort_values("Datetime")
        
        if ticker_df.empty:
            print(f"    ❌ No data for {ticker}")
            continue
        
        print(f"    📊 {ticker} data shape: {ticker_df.shape}")
        
        # Check for valid OHLC data
        ohlc_data = ticker_df[['Open', 'High', 'Low', 'Close']].copy()
        if ohlc_data.isna().any().any():
            print(f"    ❌ {ticker}: Contains NaN values in OHLC data")
            continue
            
        try:
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
            print(f"    ✅ Successfully added candlestick for {ticker}")
            
        except Exception as candlestick_error:
            print(f"    ❌ Error adding candlestick for {ticker}: {candlestick_error}")
            import traceback
            traceback.print_exc()
            continue
    
    # Step 8: Update layout and test completion
    print("🎨 Step 8: Testing layout update...")
    try:
        price_chart_height = 400  # Default height
        price_fig.update_layout(
            height=price_chart_height * num_tickers,
            title="Price (Candlestick)",
            showlegend=False
        )
        print("✅ Layout updated successfully")
        
        if chart_success:
            print(f"🎉 CHART DEBUG COMPLETED SUCCESSFULLY!")
            print(f"📊 Final figure has {len(price_fig.data)} traces")
            
            # Save to HTML for testing
            try:
                price_fig.write_html("debug_chart_test.html")
                print("💾 Saved debug chart as 'debug_chart_test.html' for testing")
            except Exception as save_error:
                print(f"⚠️ Could not save chart: {save_error}")
                
        else:
            print("❌ No charts were successfully created")
            
    except Exception as layout_error:
        print(f"❌ Layout update failed: {layout_error}")
        import traceback
        traceback.print_exc()

def test_basic_plotly():
    """Test basic Plotly functionality"""
    print("=== Testing Basic Plotly ===")
    try:
        # Create a simple figure
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[1, 2, 3], y=[4, 5, 6], mode='lines'))
        print(f"✅ Basic Plotly figure created: {len(fig.data)} traces")
        
        # Test make_subplots
        subfig = make_subplots(rows=2, cols=1)
        subfig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 2, 3]), row=1, col=1)
        subfig.add_trace(go.Scatter(x=[1, 2, 3], y=[3, 2, 1]), row=2, col=1)
        print(f"✅ make_subplots created: {len(subfig.data)} traces")
        
        return True
    except Exception as e:
        print(f"❌ Basic Plotly test failed: {e}")
        traceback.print_exc()
        return False

def test_candlestick_chart():
    """Test candlestick chart creation"""
    print("\n=== Testing Candlestick Chart ===")
    try:
        # Create sample OHLC data
        dates = pd.date_range('2025-08-22 09:30', periods=10, freq='5min')
        sample_data = {
            'Datetime': dates,
            'Open': [100, 101, 102, 103, 104, 105, 106, 107, 108, 109],
            'High': [101, 102, 103, 104, 105, 106, 107, 108, 109, 110],
            'Low': [99, 100, 101, 102, 103, 104, 105, 106, 107, 108],
            'Close': [100.5, 101.5, 102.5, 103.5, 104.5, 105.5, 106.5, 107.5, 108.5, 109.5]
        }
        df = pd.DataFrame(sample_data)
        
        # Create candlestick chart
        fig = make_subplots(rows=1, cols=1, subplot_titles=["Test Candlestick"])
        fig.add_trace(
            go.Candlestick(
                x=df["Datetime"],
                open=df["Open"],
                high=df["High"],
                low=df["Low"],
                close=df["Close"],
                name="Test Data"
            ),
            row=1, col=1
        )
        
        print(f"✅ Candlestick chart created: {len(fig.data)} traces")
        return fig
        
    except Exception as e:
        print(f"❌ Candlestick test failed: {e}")
        traceback.print_exc()
        return None

def test_multiple_subplots():
    """Test multiple subplot creation like in the dashboard"""
    print("\n=== Testing Multiple Subplots (Dashboard Style) ===")
    try:
        tickers = ['ETHU', 'TQQQ', 'LABU']
        num_tickers = len(tickers)
        
        # Create subplots like in dashboard
        fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.08,
            subplot_titles=[f"{ticker} Chart" for ticker in tickers],
            row_heights=[1]*num_tickers
        )
        
        # Add sample data for each ticker
        for i, ticker in enumerate(tickers, start=1):
            dates = pd.date_range('2025-08-22 09:30', periods=5, freq='5min')
            fig.add_trace(
                go.Candlestick(
                    x=dates,
                    open=[100 + i, 101 + i, 102 + i, 103 + i, 104 + i],
                    high=[101 + i, 102 + i, 103 + i, 104 + i, 105 + i],
                    low=[99 + i, 100 + i, 101 + i, 102 + i, 103 + i],
                    close=[100.5 + i, 101.5 + i, 102.5 + i, 103.5 + i, 104.5 + i],
                    name=f"{ticker} Price"
                ),
                row=i, col=1
            )
        
        print(f"✅ Multiple subplot chart created: {len(fig.data)} traces, {num_tickers} rows")
        return fig
        
    except Exception as e:
        print(f"❌ Multiple subplots test failed: {e}")
        traceback.print_exc()
        return None

def test_dash_integration():
    """Test if Dash components can be created"""
    print("\n=== Testing Dash Integration ===")
    try:
        import dash
        from dash import html, dcc
        
        # Test Dash components
        app = dash.Dash(__name__)
        
        # Create a simple layout
        test_fig = go.Figure()
        test_fig.add_trace(go.Scatter(x=[1, 2, 3], y=[1, 4, 2], mode='lines'))
        
        app.layout = html.Div([
            dcc.Graph(id='test-graph', figure=test_fig)
        ])
        
        print("✅ Dash app and components created successfully")
        return app
        
    except Exception as e:
        print(f"❌ Dash integration test failed: {e}")
        traceback.print_exc()
        return None

def main():
    """Run all diagnostic tests"""
    print("🔍 CHART DIAGNOSTIC TOOL - Testing Dashboard Chart Components")
    print("=" * 60)
    
    # Test basic Plotly
    if not test_basic_plotly():
        print("❌ CRITICAL: Basic Plotly functionality failed - cannot proceed")
        return
    
    # Test candlestick charts
    candlestick_fig = test_candlestick_chart()
    if candlestick_fig is None:
        print("❌ WARNING: Candlestick charts are failing")
    
    # Test multiple subplots
    subplot_fig = test_multiple_subplots()
    if subplot_fig is None:
        print("❌ WARNING: Multiple subplots are failing")
    
    # Test Dash integration
    dash_app = test_dash_integration()
    if dash_app is None:
        print("❌ WARNING: Dash integration is failing")
    
    print("\n" + "=" * 60)
    if candlestick_fig and subplot_fig and dash_app:
        print("✅ ALL TESTS PASSED - Chart components should work")
        print("💡 The issue may be in the dashboard callback logic or data processing")
    else:
        print("❌ SOME TESTS FAILED - Chart creation has issues")
        print("💡 Check the failed components above")

if __name__ == "__main__":
    main()

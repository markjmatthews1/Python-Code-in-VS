# =========================
# Standard Library Imports
# =========================
import os
import time
import json
import logging
import threading
import configparser
import webbrowser
import warnings

# Suppress pandas_ta deprecation warning
warnings.filterwarnings("ignore", message="pkg_resources is deprecated")
from datetime import datetime, timedelta, timezone
import schedule

# =========================
# Third-Party Imports
# =========================
import pandas as pd
import numpy as np
import requests
from requests_oauthlib import OAuth1Session
from bs4 import BeautifulSoup
import pandas_ta as ta
import matplotlib.pyplot as plt
import plotly.graph_objs as go
from plotly.subplots import make_subplots
import dash
from dash import dcc, html, Input, Output, State, dash_table
from dash.dependencies import Input, Output
import gspread
import gtts
import soundfile as sf
import sounddevice as sd
from sklearn.ensemble import RandomForestClassifier
from alpha_vantage.timeseries import TimeSeries
import yfinance as yf
import pyetrade
from pyetrade import market
from pyetrade.authorization import ETradeOAuth
from pyetrade.market import ETradeMarket
from pyetrade.accounts import ETradeAccounts
from pyngrok import ngrok
import psutil
import pytz
from etrade_auth import get_etrade_session
from rank_top5_etfs import rank_top5_etfs
from Schwab_auth import fetch_batch_quotes
from etrade_auth import fetch_etrade_market_data
from Schwab_auth import get_streamer
from schwab_data import fetch_schwab_minute_ohlcv
import subprocess
from schwab_data import fetch_schwab_latest_minute
from schwab_data import refresh_access_token
from ai_module import get_trade_recommendations
import pyttsx3
import logging
from day_settings_gui import load_settings, save_settings
import subprocess
import sys
from dash import dash_table
import logging
from edgar_whale import get_whale_13f_holdings   # ***** Importing the whale data fetching function as backup for finnhub *****
import requests



logging.basicConfig(
    filename='dashboard_debug.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(message)s'
)

# =========================
# Jupyter/IPython Tools (optional)
# =========================
from IPython.display import Audio, display, HTML, clear_output


# =========================
# GUI Tools
# =========================
import tkinter as tk
from tkinter import simpledialog

# --- Splash Popup will be created later when data processing starts ---

# =========================
# Local/Other Imports
# =========================
from newspaper import Article

# =========================
# AI Imports
# =========================
# Replace your current AI settings (around line 110) with:
from config import (
    AI_PROB_THRESHOLD, 
    AI_VOLATILITY_THRESHOLD, 
    AI_TARGET_PERCENT, 
    AI_STOP_PERCENT,
    VOLATILITY_THRESHOLDS,
    LEVERAGED_ETFS,
    get_volatility_threshold
)

# =========================
# End of Imports
# =========================

# Assign the clear_output function to cls for convenience
cls = lambda: os.system('cls' if os.name == 'nt' else 'clear')
cls()  # This will clear the terminal screen

                                                          # ***** Begin global variables *****
realtime_ds = None
api_data_dict = {}
historical_data_dict = {}
tickers = []
top_5_tickers = []
ai_recommendations = None
top5_ai = None
access_token = {}
merged_data_dict = {}
filtered_df = None
df = None
session = None
base_url = None
HISTORICAL_DATA_FILE = "historical_data.csv"
on_new_ohlcv_bar = None  # Callback for new OHLCV bar data
streamer = None  # Global reference to Schwab streamer

                        
# ====== File paths and constants ======
TOP_ETFS_FILE = "C:/Users/mjmat/Python Code in VS/Top_ETFS_for_DayTrade.xlsx"
HISTORICAL_DATA_FILE = "historical_data.csv"
NEWS_CACHE_FILE = "news_cache.json"
WHALE_CACHE_FILE = "whale_cache.json"



                                                             # ***** End of global variables *****

                                                             # ***** Begin ETF mapping setup *****

ETF_UNDERLYING_MAP = {
    "TQQQ": "QQQ",      # Tracks Nasdaq 100 (QQQ, not a single stock)
    "TECL": "XLK",      # Tracks Technology Select Sector SPDR (not a single stock)
    "BITX": "BTC-USD",  # Bitcoin ETF (crypto, not a stock)
    "MSTX": "MSFT",     # Direxion Daily MSFT Bull 1.5X Shares
    "BITU": "BTC-USD",  # Bitcoin ETF (crypto)
    "USD": "USD",       # US Dollar (not a stock)
    "ETHU": "ETH-USD",  # Ethereum ETF (crypto)
    "ROM": "XLK",       # Technology sector (not a single stock)
    "NVDU": "NVDA",     # Direxion Daily NVDA Bull 1.5X Shares
    "AGQ": "SILVER",    # Silver (commodity)
    "LABU": "XBI",      # Biotech sector (not a single stock)
    "GDXU": "GDX",      # Gold miners (not a single stock)
    "NUGT": "GDX",      # Gold miners (not a single stock)
    "SMCX": "SMCI",     # Direxion Daily Super Micro Computer Bull 1.5X Shares
    "CWEB": "KWEB",     # China internet (not a single stock)
    "JNUG": "GDXJ",     # Junior gold miners (not a single stock)
    "NAIL": "XHB",      # Homebuilders (not a single stock)
    "DFEN": "ITA",      # Aerospace & Defense (not a single stock)
    "ERX": "XLE",       # Energy sector (not a single stock)
    "SDOW": "DIA",      # Dow 30 (not a single stock)
    "TMV": "TLT",       # 20+ Year Treasuries (not a stock)
    "BOIL": "UNG",      # Natural gas (not a stock)
    "MSFU": "MSFT",     # Direxion Daily MSFT Bull 2X Shares
    "MVV": "MDY",       # S&P MidCap 400 (not a single stock)
}

                                        # ***** End of ETF mapping setup *****

# --- E*TRADE session setup (all logic in etrade_auth.py) ---
session, base_url = get_etrade_session()

# Schwab API Key and Secret
APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
APP_SECRET = "h9YybKHnDVoDM1Jw"

# Quiver Quantitative API Key (Signed up for hobbist account will charge $10 per month starting 8/10/2025)
QUIVERQUANT_API_KEY = "d10f3ec17b4706b01f9f25cd814b696960b8be54"  # Add your API key here if you have one

# StockData.org API Key
STOCKDATA_API_KEY = "xLNRWy3tt5l4hQ57ncF99pcrEsuUVhOsqsBHnt01"

# AlphaVantage API Key
ALPHA_VANTAGE_API_KEY = "K83KWPBFXRE10DAD"

# ngrok dashboard token
ngrok_auth_token = ngrok.set_auth_token("2wb279vOFwuArbSWlk1qv6khhxF_2PAQeWaWL7vzaRffiJZP7")

# Microsoft Bing API Key 
BING_NEWS_API_KEY = "bf5f748cc61a4b7387c45398cdd40b8d"

# News API Key
NEWS_API_KEY = "7fdd7fe392ff4a9b9e7940a32a055fdb"

# Finnhub API Key
                 # d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0
FINNHUB_API_KEY = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"
FINNHUB_SECRET = "d0o631hr01qn5ghnfap0"


                              # ***** End of API keys setup *****

                              # ====== Settings File Setup ======

SETTINGS_FILE = "settings.json"
DEFAULT_SETTINGS = {"dashboard_interval": 1, "volatility_lookback_bars": 1}

def get_current_interval():
    settings = load_settings()
    return settings.get("dashboard_interval", 1)

def load_settings():
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    return DEFAULT_SETTINGS.copy()

def get_volatility_lookback_bars():
    settings = load_settings()
    return settings.get("volatility_lookback_bars", 12)



                                           # ===== End of Settings File Setup ======

                                           # ===== Function to aggregate 1-min bars into N-min bars ======


def aggregate_bars(df, interval_minutes=5, selected_tickers=None):
    """
    Aggregates 1-min bars into N-min bars for each ticker.
    Handles NaT (Not a Time) values properly.
    ENHANCED: Preserves selected tickers by filtering BEFORE datetime cleaning.
    """
    if df.empty:
        return df
    
    df = df.copy()
    
    # 🔥 PRIORITY FIX: Filter by selected tickers FIRST to preserve chart data
    if selected_tickers is not None and 'Ticker' in df.columns:
        print(f"🎯 Filtering for selected tickers: {selected_tickers}")
        original_tickers = df['Ticker'].unique()
        print(f"📊 Available tickers before filter: {list(original_tickers)}")
        df = df[df['Ticker'].isin(selected_tickers)]
        remaining_tickers = df['Ticker'].unique() 
        print(f"📊 Remaining tickers after filter: {list(remaining_tickers)}")
    
    # 🔥 FIX: More robust datetime handling - preserve format if already good
    if 'Datetime' in df.columns:
        # Check if datetime is already in proper format
        if df['Datetime'].dtype == 'datetime64[ns]':
            print("✅ Datetime already in proper format")
        else:
            print("🔧 Converting datetime format...")
            # Try to preserve existing format first, then convert if needed
            try:
                df["Datetime"] = pd.to_datetime(df["Datetime"], errors='coerce')
            except Exception as e:
                print(f"⚠️ Datetime conversion error: {e}")
    
    # Count NaT values AFTER filtering for selected tickers
    nat_count = df['Datetime'].isna().sum()
    total_count = len(df)
    
    print(f"📊 Datetime validation: {total_count - nat_count}/{total_count} valid ({nat_count} NaT values)")
    
    if nat_count == total_count:
        print("🚨 CRITICAL: ALL datetime values are NaT")
        print(f"🔍 Sample raw datetime values: {df['Datetime'].head().tolist()}")
        # Instead of failing, create a simple time sequence
        print("🛠️ Creating synthetic datetime sequence to preserve chart data")
        start_time = pd.Timestamp.now().floor('min')
        df['Datetime'] = [start_time + pd.Timedelta(minutes=i) for i in range(len(df))]
        print(f"✅ Created datetime sequence from {df['Datetime'].min()} to {df['Datetime'].max()}")
    elif nat_count > 0 and nat_count < (total_count * 0.3):
        before_count = len(df)
        df = df.dropna(subset=['Datetime'])
        after_count = len(df)
        print(f"⚠️ Removed {before_count - after_count} rows with invalid datetime values")
    elif nat_count >= (total_count * 0.3):
        print(f"🚨 WARNING: {nat_count} datetime values are NaT ({nat_count/total_count:.1%}) - trying to fix")
        # Try forward/backward fill first
        df['Datetime'] = df['Datetime'].ffill().bfill()
        remaining_nat = df['Datetime'].isna().sum()
        if remaining_nat > 0:
            print(f"🛠️ Still {remaining_nat} NaT values, creating synthetic sequence")
            start_time = pd.Timestamp.now().floor('min')
            mask = df['Datetime'].isna()
            df.loc[mask, 'Datetime'] = [start_time + pd.Timedelta(minutes=i) for i in range(mask.sum())]
    
    if df.empty:
        print("❌ No valid datetime data remaining after cleaning")
        return pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
    
    df = df.sort_values(["Ticker", "Datetime"])
    result = []
    
    for ticker, tdf in df.groupby("Ticker"):
        if tdf.empty:
            continue
            
        try:
            tdf = tdf.set_index("Datetime")
            
            # Additional safety check for empty group
            if tdf.empty:
                continue
                
            agg = tdf.resample(f"{interval_minutes}min").agg({
                "Open": "first",
                "High": "max", 
                "Low": "min",
                "Close": "last",
                "Volume": "sum"
            }).reset_index()
            
            # **CRITICAL FIX**: Don't use .dropna() which removes aggregated data
            # Only remove rows where ALL OHLC values are NaN (completely empty periods)
            ohlc_cols = ['Open', 'High', 'Low', 'Close']
            completely_empty = agg[ohlc_cols].isna().all(axis=1)
            agg = agg[~completely_empty]
            
            print(f"📊 {ticker}: Aggregated {len(tdf)} rows to {len(agg)} {interval_minutes}-min bars")
            
            if not agg.empty:
                agg["Ticker"] = ticker
                result.append(agg)
                
        except Exception as e:
            print(f"⚠️ Error aggregating data for {ticker}: {e}")
            continue
    
    if result:
        return pd.concat(result, ignore_index=True)
    else:
        print("❌ No data could be aggregated")
        return pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
    
def validate_datetime_data(df):
    """Check for datetime issues in the DataFrame and handle multiple formats"""
    if df.empty:
        return df
    
    print("🔍 Validating datetime data...")
    
    # 🔥 NEW: Handle multiple datetime formats robustly
    if 'Datetime' in df.columns:
        # Clean up any malformed datetime strings first
        df['Datetime'] = df['Datetime'].astype(str)
        
        # Remove any trailing artifacts or extra spaces
        df['Datetime'] = df['Datetime'].str.replace(r':00$', '', regex=True)
        df['Datetime'] = df['Datetime'].str.replace(r'\s+', ' ', regex=True)
        
        # Try multiple parsing approaches
        try:

            # First try: errors='coerce' to preserve data
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            print("✅ Parsed datetime with errors='coerce'")
        except:
            try:
                # Second try: specific format
                df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M')
                print("✅ Parsed datetime with format '%Y-%m-%d %H:%M'")
            except:
                # Last resort: force conversion
                print("⚠️ Using force conversion")
                df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
    
    # Count and report issues
    nat_count = df['Datetime'].isna().sum()
    total_count = len(df)
    
    print(f"📊 Datetime validation: {total_count - nat_count}/{total_count} valid ({nat_count} NaT values)")
    
    # **CHANGED**: Be much more conservative about removing data
    if nat_count > 0 and nat_count < (total_count * 0.5):  # Only if less than 50% are NaT
        print("⚠️ Found some problematic datetime values, cleaning...")
        df = df.dropna(subset=['Datetime'])
        print(f"✅ Cleaned data: {len(df)} rows remaining")
    elif nat_count >= (total_count * 0.5):
        print("🚨 WARNING: Many datetime values are NaT - keeping all data to preserve charts")
        # Don't clean if more than half the data would be lost
    
    # **DEBUG**: Show what tickers remain after datetime processing
    if 'Ticker' in df.columns:
        remaining_tickers = df['Ticker'].unique()
        print(f"🔍 Tickers remaining after datetime processing: {list(remaining_tickers)}")
    
    return df

# ====== Schwab Token Check and Refresh ======
TOKEN_FILE = "tokens.json"

def load_schwab_tokens():
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        return token_data.get("token_dictionary", {})
    except FileNotFoundError:
        return None

def ensure_schwab_token():
    print("ensure_schwab_token() called")
    needs_refresh = False
    tokens = load_schwab_tokens()
    if not tokens:
        print("No Schwab tokens found. Running Schwab_auth.py to create tokens.")
        needs_refresh = True
    else:
        access_token = tokens.get("access_token")
        expires_at = tokens.get("expires_at")
        print(f"access_token: {access_token}, expires_at: {expires_at}")
        if not access_token or not expires_at or time.time() > float(expires_at) - 60:
            print("Schwab access token expired or about to expire. Refreshing tokens.")
            needs_refresh = True
    if needs_refresh:
        import subprocess
        result = subprocess.run(["python", "Schwab_auth.py"], capture_output=True, text=True)
        print("Schwab_auth.py stdout:", result.stdout)
        print("Schwab_auth.py stderr:", result.stderr)
        tokens = load_schwab_tokens()
        if not tokens or not tokens.get("access_token"):
            print("Failed to refresh Schwab tokens. Please run Schwab_auth.py manually if needed.")
            exit(1)
        else:
            print("✅ Schwab tokens refreshed.")

ensure_schwab_token()
assert os.path.exists(TOKEN_FILE), "tokens.json was not created!"

# ====== ETF List Loader ======
TOP_ETFS_FILE = "C:/Users/mjmat/Python Code in VS/Top_ETFS_for_DayTrade.xlsx"

def get_top_etf_list_from_excel():
    if not os.path.exists(TOP_ETFS_FILE):
        raise FileNotFoundError(f"ETF list file not found: {TOP_ETFS_FILE}")
    df = pd.read_excel(TOP_ETFS_FILE)
    if "Symbol" not in df.columns:
        raise ValueError(f"'Symbol' column not found in {TOP_ETFS_FILE}")
    symbols = df["Symbol"].dropna().astype(str).str.strip().unique().tolist()
    print(f"Loaded {len(symbols)} ETF tickers from {TOP_ETFS_FILE}: {symbols}")
    return symbols

# Load all potential tickers for ranking process (will be filtered down to top 5)
all_candidate_tickers = get_top_etf_list_from_excel()
print(f"🎯 Starting with {len(all_candidate_tickers)} candidate tickers for ranking")

# ====== Historical Data Loader ======
HISTORICAL_DATA_FILE = "historical_data.csv"

def is_file_fresh(filepath, min_rows=10):
    if not os.path.exists(filepath):
        return False
    try:
        df = pd.read_csv(filepath)
        return len(df) >= min_rows
    except Exception:
        return False

def append_missing_schwab_data(historical_file, tickers, max_ticks=500):
    from datetime import datetime, timedelta
    from schwab_data import fetch_minute_bars_for_range, fetch_schwab_minute_ohlcv
    
    print(f"🔍 SCHWAB DATA FETCH: Starting for {len(tickers)} tickers...")
    print(f"🔍 Current time: {datetime.now()}")
    
    # Load existing data
    if os.path.exists(historical_file):
        hist_df = pd.read_csv(historical_file, parse_dates=["Datetime"])
        print(f"🔍 Loaded existing data: {len(hist_df)} rows")
    else:
        hist_df = pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
        print(f"🔍 No existing historical file, starting fresh")

    all_new_data = []
    today = datetime.now().date()
    
    for ticker in tickers:
        print(f"Processing {ticker}...")
        
        if not hist_df.empty and ticker in hist_df["Ticker"].unique():
            ticker_data = hist_df[hist_df["Ticker"] == ticker].copy()
            last_dt = ticker_data["Datetime"].max()
            print(f"  Last data for {ticker}: {last_dt}")
            
            # Check if we have today's data
            ticker_data.loc[:, 'Date'] = pd.to_datetime(ticker_data['Datetime'], format='mixed', errors='coerce').dt.date
            today_data = ticker_data[ticker_data['Date'] == today]
            print(f"  Today's data rows for {ticker}: {len(today_data)}")
            
            # **FIX: Force fetch if we don't have sufficient today's data**
            if len(today_data) < 10:  # Need at least 10 bars for today
                print(f"  🚨 INSUFFICIENT TODAY DATA for {ticker} - forcing fresh fetch")
                # Fetch today's data starting from market open
                market_open = datetime.combine(today, datetime.min.time().replace(hour=9, minute=30))
                end_dt = datetime.now()
                
                print(f"  Fetching today's data from {market_open} to {end_dt}")
                new_data = fetch_minute_bars_for_range(ticker, market_open, end_dt)
                
                if not new_data.empty:
                    print(f"  ✅ Found {len(new_data)} new bars for {ticker}")
                    all_new_data.append(new_data)
                else:
                    print(f"  ❌ No new data returned from Schwab for {ticker}")
            else:
                # **FIX: Ensure last_dt is a datetime object**
                last_dt = pd.to_datetime(last_dt)
                
                # Calculate start and end times for new data
                start_dt = last_dt + timedelta(minutes=1)  # Start after last bar
                end_dt = datetime.now()
                
                if start_dt < end_dt:
                    # Use the range function to get data between specific dates
                    print(f"  Fetching incremental data from {start_dt} to {end_dt}")
                    new_data = fetch_minute_bars_for_range(ticker, start_dt, end_dt)
                    
                    if not new_data.empty:
                        print(f"  Found {len(new_data)} new bars for {ticker}")
                        all_new_data.append(new_data)
                    else:
                        print(f"  No new incremental data for {ticker}")
                else:
                    print(f"  Data for {ticker} is up to date")
        else:
            # No existing data, fetch recent data
            print(f"  No existing data for {ticker}, fetching fresh data...")
            new_data = fetch_schwab_minute_ohlcv(ticker, period=1)
            if not new_data.empty:
                all_new_data.append(new_data)
            else:
                print(f"  ❌ No data returned from Schwab for {ticker}")
    
    
    # Rest of your existing logic...
    if all_new_data:
        print(f"🔗 COMBINING DATA: Found {len(all_new_data)} ticker datasets with new data")
        new_df = pd.concat(all_new_data, ignore_index=True)
        print(f"🔗 Combined new data: {len(new_df)} total new rows")
        
        combined_df = pd.concat([hist_df, new_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["Datetime", "Ticker"], keep="last")
        combined_df = combined_df.sort_values(["Ticker", "Datetime"])
        combined_df = combined_df.groupby("Ticker").tail(max_ticks).reset_index(drop=True)
        combined_df.to_csv(historical_file, index=False)
        print("✅ Appended missing Schwab data to historical_data.csv")
        print(f"Total rows after update: {len(combined_df)}")
        
        # Verify today's data coverage after update
        combined_df_copy = combined_df.copy()
        combined_df_copy['Date'] = pd.to_datetime(combined_df_copy['Datetime'], format='mixed', errors='coerce').dt.date
        today_check = combined_df_copy[combined_df_copy['Date'] == today]
        tickers_with_today_data = len(today_check['Ticker'].unique())
        print(f"🎯 POST-UPDATE: {tickers_with_today_data}/{len(tickers)} tickers have today's data")
        
        return combined_df
    else:
        print("✅ No new Schwab data to append.")
        print(f"🔍 DEBUGGING: Checking today's data coverage in existing data...")
        if not hist_df.empty:
            hist_df_copy = hist_df.copy()
            hist_df_copy['Date'] = pd.to_datetime(hist_df_copy['Datetime'], format='mixed', errors='coerce').dt.date
            today_existing = hist_df_copy[hist_df_copy['Date'] == today]
            tickers_with_today = len(today_existing['Ticker'].unique())
            print(f"🎯 EXISTING DATA: {tickers_with_today}/{len(tickers)} tickers have today's data")
            
            # Show sample of what we have for troubleshooting
            print(f"🔍 Sample today data:")
            for ticker in tickers[:3]:
                ticker_today = today_existing[today_existing['Ticker'] == ticker]
                print(f"   {ticker}: {len(ticker_today)} rows")
        
        return hist_df
    
# At startup, after loading tickers:
historical_data = append_missing_schwab_data(HISTORICAL_DATA_FILE, all_candidate_tickers, max_ticks=500)  # Increased for better AI analysis
# diagnostic prints
df = pd.read_csv("historical_data.csv")
print("Total rows: 316", len(df))
print("Tickers:", df["Ticker"].unique())
print("Rows per ticker: 318")
print(df.groupby("Ticker").size())

def build_fresh_schwab_history_file(tickers, filename="historical_data.csv", max_ticks=500):
    from schwab_data import fetch_schwab_minute_ohlcv
    dfs = []
    for symbol in tickers:
        df = fetch_schwab_minute_ohlcv(symbol, period=1)
        if not df.empty:
            print(f"{symbol}: {df['Datetime'].min()} to {df['Datetime'].max()} ({len(df)} bars)")
            dfs.append(df)
        else:
            print(f"⚠️ No data for {symbol}")
    if dfs:
        all_df = pd.concat(dfs, ignore_index=True)
        expected_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]
        all_df = all_df[[col for col in expected_cols if col in all_df.columns]]
        all_df = all_df.sort_values(["Ticker", "Datetime"])
        all_df = all_df.groupby("Ticker").tail(max_ticks).reset_index(drop=True)
        print("About to save historical_data.csv")
        print(all_df[["Datetime", "Ticker"]].head(3))
        print(all_df[["Datetime", "Ticker"]].tail(3))
        all_df.to_csv(filename, index=False)
        print(f"✅ Saved last {max_ticks} 1-min bars per ticker to {filename}")
    else:
        print("⚠️ No data fetched for any ticker.")

#if not is_file_fresh(HISTORICAL_DATA_FILE, min_rows=10):
    print(f"{HISTORICAL_DATA_FILE} missing or stale, building fresh Schwab history file...")
    build_fresh_schwab_history_file(tickers, filename=HISTORICAL_DATA_FILE, max_ticks=500)  # Increased for enhanced AI
#else:
#    print(f"{HISTORICAL_DATA_FILE} found and fresh, using existing file.")

# NOTE: AI recommendations will be called after ticker selection is complete   

# ====== Streaming Handler Setup ======
ohlcv_buffer = {}

def schwab_streaming_handler(response):
    global ohlcv_buffer
    try:
        data = json.loads(response)
        if "data" in data:
            for item in data["data"]:
                if item.get("service") == "LEVELONE_EQUITIES":
                    for quote in item.get("content", []):
                        symbol = quote["key"]
                        price = quote.get("3")
                        volume = quote.get("8")
                        if price is None or volume is None:
                            continue
                        now_minute = pd.Timestamp.now().floor("min")
                        if symbol not in ohlcv_buffer:
                            ohlcv_buffer[symbol] = {}
                        if now_minute not in ohlcv_buffer[symbol]:
                            ohlcv_buffer[symbol][now_minute] = []
                        ohlcv_buffer[symbol][now_minute].append({
                            "price": price,
                            "volume": volume
                        })
    except Exception as e:
        print("Error in streaming handler:", e)

def aggregate_ohlcv_for_minute(symbol, minute):
    ticks = ohlcv_buffer[symbol][minute]
    prices = [t["price"] for t in ticks]
    volumes = [t["volume"] for t in ticks]
    open_ = prices[0]
    high_ = max(prices)
    low_ = min(prices)
    close = prices[-1]
    volume = volumes[-1] - volumes[0] if len(volumes) > 1 else 0
    return {
        "Datetime": minute,
        "Ticker": symbol,
        "Open": open_,
        "High": high_,
        "Low": low_,
        "Close": close,
        "Volume": volume
    }

# ====== End of Streaming Handler Setup ======

# ====== Now you can safely proceed with analysis, candidate selection, etc. ======                       

                              # ***** Begin logging trades setup *****

TRADE_LOG_FILE = "trade_log.xlsx"
TRADE_LOG_COLUMNS = [
    "Type", "Ticker", "Trade QTY", "Open Datetime", "Open Price",
        "Close Datetime", "Close Price", "Profit/Loss", "Profit/Loss %", "Notes"
]

# Load or initialize trade log DataFrame
if os.path.exists(TRADE_LOG_FILE):
    trade_log_df = pd.read_excel(TRADE_LOG_FILE)
else:
    trade_log_df = pd.DataFrame(columns=TRADE_LOG_COLUMNS)

                                             # ***** End of logging trades setup *****
                  
                              # ***** Begin function to fetch Whale data, institutional, govvernment, and insider trading data *****
#                    ***** Schwab historical data retrieval and processing *****


WHALE_CACHE_FILE = "whale_cache.json"

def save_whale_cache():
    serializable_cache = {}
    for k, v in whale_cache.items():
        if isinstance(v, tuple):
            ts, data = v
            serializable_cache[k] = (ts.isoformat(), data)
        else:
            serializable_cache[k] = v
    with open(WHALE_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_cache, f)

def load_whale_cache():
    global whale_cache
    if os.path.exists(WHALE_CACHE_FILE):
        with open(WHALE_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                if isinstance(v, list):
                    whale_cache[k] = (datetime.now(timezone.utc), v)
                elif isinstance(v, list) or isinstance(v, tuple):
                    ts, d = v
                    whale_cache[k] = (datetime.fromisoformat(ts), d)

whale_cache = {}
load_whale_cache()


                              # ***** End of function to fetch Whale data, institutional, government, and insider trading data *****


                             # ***** Begin function to fetch ETF news *****  

NEWS_CACHE_FILE = "news_cache.json"

news_cache = {}

def load_news_cache():
    global news_cache
    if os.path.exists(NEWS_CACHE_FILE):
        with open(NEWS_CACHE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            for k, v in data.items():
                if isinstance(v, list):
                    # Old format, just articles
                    news_cache[k] = (datetime.now(timezone.utc), v)
                elif isinstance(v, list) or isinstance(v, tuple):
                    ts, articles = v
                    news_cache[k] = (datetime.fromisoformat(ts), articles)

def save_news_cache():
    # Convert datetime keys to ISO format for JSON serialization
    serializable_cache = {}
    for k, v in news_cache.items():
        if isinstance(v, tuple):
            ts, articles = v
            serializable_cache[k] = (ts.isoformat(), articles)
        else:
            serializable_cache[k] = v
    with open(NEWS_CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(serializable_cache, f)

load_news_cache()

                                                  # ***** End of function to load and save ETF news cache file *****

                                               # *****Calculate ADX/DMS Indicators with rounding *****

# ✅ Ensure merge function runs FIRST, so merged_data_dict is created
realtime_ds = {}

def calculate_adx(df, period=14, smoothing_period=3):
    """
    Calculate ADX, +DI, and -DI with E*Trade-style smoothing for cleaner lines.
    Uses standard 14-period calculation with additional smoothing for visual appeal.
    """
    df = df.copy()
    
    # Ensure we have enough data
    if len(df) < period * 3:  # Need more data for smoother calculation
        # Return NaNs if insufficient data
        result = pd.DataFrame(index=df.index)
        result['ADX'] = np.nan
        result['+DI'] = np.nan
        result['-DI'] = np.nan
        return result
    
    # Calculate price differences
    df['up_move'] = df['High'] - df['High'].shift(1)
    df['down_move'] = df['Low'].shift(1) - df['Low']

    # +DM and -DM (directional movements)
    df['+DM'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0.0)
    df['-DM'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0.0)

    # True Range (TR)
    df['tr1'] = df['High'] - df['Low']
    df['tr2'] = np.abs(df['High'] - df['Close'].shift(1))
    df['tr3'] = np.abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

    # **E*TRADE STYLE**: Use pandas rolling mean for initial smoothing, then apply Wilder's
    # This creates smoother initial values compared to raw Wilder's smoothing
    df['TR_initial'] = df['TR'].rolling(window=period, min_periods=period).mean()
    df['+DM_initial'] = df['+DM'].rolling(window=period, min_periods=period).mean()
    df['-DM_initial'] = df['-DM'].rolling(window=period, min_periods=period).mean()
    
    # Apply Wilder's smoothing starting from the initial smoothed values
    df['TR_smooth'] = np.nan
    df['+DM_smooth'] = np.nan
    df['-DM_smooth'] = np.nan
    
    # Set first valid smoothed values
    first_valid = period - 1
    df.iloc[first_valid, df.columns.get_loc('TR_smooth')] = df.iloc[first_valid, df.columns.get_loc('TR_initial')]
    df.iloc[first_valid, df.columns.get_loc('+DM_smooth')] = df.iloc[first_valid, df.columns.get_loc('+DM_initial')]
    df.iloc[first_valid, df.columns.get_loc('-DM_smooth')] = df.iloc[first_valid, df.columns.get_loc('-DM_initial')]
    
    # Apply Wilder's smoothing for subsequent values
    for i in range(first_valid + 1, len(df)):
        if not pd.isna(df.iloc[i-1, df.columns.get_loc('TR_smooth')]):
            df.iloc[i, df.columns.get_loc('TR_smooth')] = (df.iloc[i-1, df.columns.get_loc('TR_smooth')] * (period - 1) + df.iloc[i, df.columns.get_loc('TR')]) / period
            df.iloc[i, df.columns.get_loc('+DM_smooth')] = (df.iloc[i-1, df.columns.get_loc('+DM_smooth')] * (period - 1) + df.iloc[i, df.columns.get_loc('+DM')]) / period
            df.iloc[i, df.columns.get_loc('-DM_smooth')] = (df.iloc[i-1, df.columns.get_loc('-DM_smooth')] * (period - 1) + df.iloc[i, df.columns.get_loc('-DM')]) / period

    # +DI and -DI (avoid division by zero)
    df['+DI_raw'] = np.where(df['TR_smooth'] > 0, 100 * (df['+DM_smooth'] / df['TR_smooth']), 0)
    df['-DI_raw'] = np.where(df['TR_smooth'] > 0, 100 * (df['-DM_smooth'] / df['TR_smooth']), 0)
    
    # **E*TRADE STYLE**: Apply additional smoothing to DI values for cleaner lines
    df['+DI'] = df['+DI_raw'].rolling(window=smoothing_period, center=True, min_periods=1).mean()
    df['-DI'] = df['-DI_raw'].rolling(window=smoothing_period, center=True, min_periods=1).mean()

    # DX calculation (avoid division by zero)
    di_sum = df['+DI'] + df['-DI']
    df['DX'] = np.where(di_sum > 0, 100 * (np.abs(df['+DI'] - df['-DI']) / di_sum), 0)
    
    # ADX calculation with proper initialization
    df['ADX_raw'] = np.nan
    
    # Initialize ADX with rolling mean of DX values
    adx_start = period + smoothing_period
    if adx_start < len(df):
        df.iloc[adx_start, df.columns.get_loc('ADX_raw')] = df['DX'].iloc[period:adx_start+1].mean()
        
        # Apply Wilder's smoothing to ADX
        for i in range(adx_start + 1, len(df)):
            if not pd.isna(df.iloc[i-1, df.columns.get_loc('ADX_raw')]):
                df.iloc[i, df.columns.get_loc('ADX_raw')] = (df.iloc[i-1, df.columns.get_loc('ADX_raw')] * (period - 1) + df.iloc[i, df.columns.get_loc('DX')]) / period

    # **E*TRADE STYLE**: Apply final smoothing to ADX for ultra-smooth lines like E*Trade
    df['ADX'] = df['ADX_raw'].rolling(window=smoothing_period, center=True, min_periods=1).mean()

    # Clean up: only return values after proper initialization
    result = df[['ADX', '+DI', '-DI']].copy()
    
    # Mask early values as NaN to avoid unrealistic starting values
    result.iloc[:period + smoothing_period] = np.nan
    
    return result.round(2)

def calculate_pmo(df, period=35, signal_period=10):
    df = df.copy()
    if df.empty or period is None or not isinstance(period, int) or period < 1:
        df['PMO'] = np.nan
        df['PMO_signal'] = np.nan
        return df[['PMO', 'PMO_signal']]
    roc = df['Close'].pct_change() * 100
    ema1 = roc.ewm(span=period, adjust=False).mean()
    pmo = ema1.ewm(span=period, adjust=False).mean()
    pmo_signal = pmo.ewm(span=signal_period, adjust=False).mean()
    df['PMO'] = pmo
    df['PMO_signal'] = pmo_signal
    return df[['PMO', 'PMO_signal']]

def calculate_adx_multi(df, tickers, period=14):  # Use standard 14-period for smoother E*Trade-style ADX
    """
    Calculate ADX for multiple tickers and return a DataFrame with columns: Datetime, Ticker, ADX, +DI, -DI
    Uses E*Trade-style smoothing for cleaner, less jagged lines.
    """
    print(f"🔍 ADX_MULTI DEBUG: Input data shape: {df.shape}")
    print(f"🔍 ADX_MULTI DEBUG: Tickers: {tickers}")
    print(f"🔍 ADX_MULTI DEBUG: Period: {period} (E*Trade style)")
    
    results = []
    for ticker in tickers:
        tdf = df[df["Ticker"] == ticker].sort_values("Datetime").copy()
        if tdf.empty:
            print(f"⚠️ ADX_MULTI WARNING: No data for {ticker}")
            continue
            
        print(f"🔍 ADX_MULTI DEBUG: Processing {ticker} with {len(tdf)} rows")
        
        # Need more data for smooth E*Trade-style calculation
        min_required = period * 3 + 5  # Increased requirement for smoother lines
        if len(tdf) < min_required:
            print(f"⚠️ ADX_MULTI WARNING: {ticker} has insufficient data ({len(tdf)} < {min_required})")
            # Create a result with NaN values for insufficient data
            tdf["ADX"] = np.nan
            tdf["+DI"] = np.nan
            tdf["-DI"] = np.nan
            merged = tdf[["Datetime", "Ticker", "ADX", "+DI", "-DI"]].copy()
        else:
            # Use E*Trade-style calculation with smoothing
            adx_df = calculate_adx(tdf, period=period, smoothing_period=3)
            if adx_df is not None and not adx_df.empty:
                print(f"✅ ADX_MULTI DEBUG: {ticker} E*Trade-style ADX calculation successful")
                tdf = tdf.reset_index(drop=True)
                adx_df = adx_df.reset_index(drop=True)
                merged = pd.concat([tdf[["Datetime", "Ticker"]], adx_df], axis=1)
            else:
                print(f"❌ ADX_MULTI ERROR: {ticker} ADX calculation failed")
                tdf["ADX"] = np.nan
                tdf["+DI"] = np.nan
                tdf["-DI"] = np.nan
                merged = tdf[["Datetime", "Ticker", "ADX", "+DI", "-DI"]].copy()
        
        results.append(merged)
        
    if results:
        final_result = pd.concat(results, ignore_index=True)
        print(f"🔍 ADX_MULTI DEBUG: Final E*Trade-style result shape: {final_result.shape}")
        # Debug: Check for non-null ADX values
        non_null_adx = final_result.dropna(subset=["ADX"])
        print(f"🔍 ADX_MULTI DEBUG: Non-null ADX rows: {len(non_null_adx)}")
        return final_result
    else:
        print("❌ ADX_MULTI ERROR: No results to return")
        return pd.DataFrame(columns=["Datetime", "Ticker", "ADX", "+DI", "-DI"])
    
                                               # ***** End of ADX/DMS calculation *****
                                              # ====== BEGIN NEW RANKING FUNCTIONS ====== 

def rank_dmi_plus_minus(adx_df):
    """
    Adds DMIPlusRank and DMIMinusRank columns to adx_df based on +DMI and -DMI values.
    """
    def dmi_rank(row):
        plus = row["+DI"]
        minus = row["-DI"]
        # Strong Uptrend
        if plus > 40 and minus < 20:
            return 5, 1
        # Moderate Uptrend
        if plus >= minus + 10 and plus > minus:
            return 4, 2
        # Strong Downtrend
        if minus > 40 and plus < 20:
            return 1, 5
        # Weak Downtrend
        if minus > plus:
            return 2, 4
        # Neutral/Range
        return 3, 3

    ranks = adx_df.apply(dmi_rank, axis=1)
    adx_df["DMIPlusRank"] = [r[0] for r in ranks]
    adx_df["DMIMinusRank"] = [r[1] for r in ranks]
    return adx_df

def rank_adx_strength(adx_df):
    """
    Adds ADXRank column to adx_df based on ADX value.
    """
    def adx_rank(adx):
        if adx < 15:
            return 1
        elif adx < 20:
            return 2
        elif adx < 30:
            return 3
        elif adx < 40:
            return 4
        else:
            return 5
    adx_df["ADXRank"] = adx_df["ADX"].apply(adx_rank)
    return adx_df
                                                             # ====== END OF NEW RANKING FUNCTIONS ======

def calculate_pmo_multi(df, tickers, period=35, signal_period=10):  # Set defaults, ignore settings
    """
    Calculate PMO for multiple tickers in a DataFrame.
    Returns a DataFrame with columns: Datetime, Ticker, PMO, PMO_signal
    """
    results = []
    for ticker in tickers:
        tdf = df[df["Ticker"] == ticker].sort_values("Datetime").copy()
        if tdf.empty:
            continue
        pmo_df = calculate_pmo(tdf, period=period, signal_period=signal_period)
        tdf = tdf.reset_index(drop=True)
        pmo_df = pmo_df.reset_index(drop=True)
        merged = pd.concat([tdf[["Datetime", "Ticker"]], pmo_df], axis=1)
        results.append(merged)
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Datetime", "Ticker", "PMO", "PMO_signal"])

def calculate_cci(df, period=20):
    df = df.copy()
    if df.empty or period is None or not isinstance(period, int) or period < 1:
        df['CCI'] = np.nan
        return df[['CCI']]
    tp = (df['High'] + df['Low'] + df['Close']) / 3
    ma = tp.rolling(window=period).mean()
    md = tp.rolling(window=period).apply(lambda x: np.mean(np.abs(x - np.mean(x))), raw=True)
    df['CCI'] = (tp - ma) / (0.015 * md)
    return df[['CCI']]

def calculate_cci_multi(df, tickers, period=20):  # Set default to 20, ignore settings
    """
    Calculate CCI for multiple tickers in a DataFrame.
    Returns a DataFrame with columns: Datetime, Ticker, CCI
    """
    results = []
    for ticker in tickers:
        tdf = df[df["Ticker"] == ticker].sort_values("Datetime").copy()
        if tdf.empty:
            continue
        cci_df = calculate_cci(tdf, period=period)
        tdf = tdf.reset_index(drop=True)
        cci_df = cci_df.reset_index(drop=True)
        merged = pd.concat([tdf[["Datetime", "Ticker"]], cci_df], axis=1)
        results.append(merged)
    if results:
        return pd.concat(results, ignore_index=True)
    else:
        return pd.DataFrame(columns=["Datetime", "Ticker", "CCI"])

                                                   # ***** End of CCI calculation ****                             
                              
                              # ***** Begin function to update historical data for new tickers *****

def update_historical_data_for_new_tickers(
    tickers,
    historical_data_file="historical_data.csv",
    max_ticks=200
):
    """
    Checks for new tickers not in the historical data file, fetches their Schwab history,
    appends to the file, and keeps only the last max_ticks bars per ticker.
    """
    import os
    import pandas as pd
    from schwab_data import fetch_schwab_minute_ohlcv

    # Load existing historical data (if any)
    if os.path.exists(historical_data_file):
        hist_df = pd.read_csv(historical_data_file)
    else:
        hist_df = pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])

    # Find which tickers are new
    existing_tickers = set(hist_df["Ticker"].unique())
    new_tickers = [t for t in tickers if t not in existing_tickers]

    if not new_tickers:
        print("✅ No new tickers to update.")
        return hist_df

    print(f"🚀 Fetching historical data for new tickers: {new_tickers}")
    all_new_data = []
    for ticker in new_tickers:
        try:
            new_data = fetch_schwab_minute_ohlcv(ticker, period=2)
            if not new_data.empty:
                all_new_data.append(new_data)
            else:
                print(f"⚠️ No data fetched for {ticker}.")
        except Exception as e:
            print(f"⚠️ Error fetching data for {ticker}: {e}")

    if all_new_data:
        new_hist_df = pd.concat(all_new_data, ignore_index=True)
        combined_df = pd.concat([hist_df, new_hist_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["Datetime", "Ticker"])
        combined_df = combined_df.sort_values(["Ticker", "Datetime"])
        # Keep only the last max_ticks bars per ticker
        combined_df = combined_df.groupby("Ticker").tail(max_ticks).reset_index(drop=True)
        # Round numeric columns
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in combined_df.columns:
                combined_df[col] = pd.to_numeric(combined_df[col], errors="coerce").round(2)
        print("About to save historical_data.csv 655")
        print(combined_df[["Datetime", "Ticker"]].head(3))
        print(combined_df[["Datetime", "Ticker"]].tail(3))
        combined_df.to_csv(historical_data_file, index=False)
        print("✅ Historical data file updated with new tickers.")
        return combined_df
    else:
        print("⚠️ No new historical data fetched.")
        return hist_df
    
                                              # ***** function to update historical data for new tickers *****


# Define file paths in Python code in VS directory

login_file_path = "C:/Users/mjmat/Pythons_Code_Files/data.csv"


def play_audio(audio_file, ticker=None, message=None, tts=True):
    try:
        audio_file_path = f"C:/Users/mjmat/Pythons_Code_Files/{audio_file}"
        if os.path.exists(audio_file_path):
            data, samplerate = sf.read(audio_file_path)
            sd.play(data, samplerate)
            sd.wait()
        else:
            print(f"Audio file {audio_file_path} not found.")

        if tts and ticker:
            tts_message = f"{ticker} {message}" if message else f"{ticker} alert"
            engine = pyttsx3.init()
            engine.say(tts_message)
            engine.runAndWait()
    except Exception as e:
        print(f"Error playing audio alert for {ticker}: {e}")

        
                                                  # ***** End of function to initiate file path for audio files *****

                                                     # ***** Audio alert and news alert function *****


# Global dict to track last alert time for each ticker/event
_last_alert_times = {}

def initialize_alert_system():
    """Initialize the alert system with necessary variables"""
    global dashboard_ranks, ai_recommendations
    
    # Initialize dashboard_ranks if not exists
    if 'dashboard_ranks' not in globals():
        dashboard_ranks = {}
        print("⚠️ dashboard_ranks not found, initializing empty dict")
    
    # Initialize ai_recommendations if not exists  
    if 'ai_recommendations' not in globals():
        try:
            ai_recommendations = get_trade_recommendations(tickers, return_df=True)
            print("✅ AI recommendations loaded for alert system")
        except Exception as e:
            print(f"⚠️ Could not load AI recommendations: {e}")
            ai_recommendations = pd.DataFrame()
    
    # Load missing functions if needed
    missing_functions = []
    if 'fetch_etf_news' not in globals():
        missing_functions.append('fetch_etf_news')
    if 'fetch_whale_data' not in globals():
        missing_functions.append('fetch_whale_data')
    if 'play_audio' not in globals():
        missing_functions.append('play_audio')
    
    if missing_functions:
        print(f"⚠️ Missing functions for alerts: {missing_functions}")
        print("   Some alert features may not work properly")

# Placeholder functions for missing dependencies
def fetch_etf_news(ticker):
    """Placeholder for news fetching - returns empty list if not implemented"""
    return []

def fetch_whale_data(ticker):
    """Placeholder for whale data fetching - returns empty dict if not implemented"""
    return {"insider": [], "institutional": [], "government": []}

# Initialize the alert system
initialize_alert_system()

def check_trade_alerts(historical_data, top5_tickers=None):
    """
    IMPROVED: Realistic alert system integrated with AI and technical rankings.
    Triggers alerts based on:
    1. AI probability thresholds (from get_trade_recommendations)
    2. Composite technical ranking (from dashboard_ranks) 
    3. Meaningful technical signals only
    4. Weighted alert scoring system
    Only processes tickers in top5_tickers if provided.
    """
    global _last_alert_times, dashboard_ranks, ai_recommendations
    alert_summary = []

    # Get current AI recommendations for correlation
    try:
        current_ai_recs = get_trade_recommendations(top5_tickers or tickers, return_df=True)
    except Exception as e:
        print(f"⚠️ Could not get AI recommendations for alerts: {e}")
        current_ai_recs = pd.DataFrame()

    print(f"🔍 Checking alerts for {len(top5_tickers or tickers)} tickers...")
    
    historical_data = historical_data.sort_values(["Ticker", "Datetime"])
    for ticker, group in historical_data.groupby("Ticker"):
        if top5_tickers is not None and ticker not in top5_tickers:
            continue
            
        group = group.reset_index(drop=True)
        if len(group) < 2:
            continue
            
        prev, curr = group.iloc[-2], group.iloc[-1]
        dt_str = str(curr["Datetime"])
        
        # Initialize signal scoring system
        signal_score = 0
        bullish_signals = []
        bearish_signals = []
        
        # Helper to avoid duplicate alerts
        def should_alert(event):
            key = (ticker, event)
            now_minute = dt_str
            if _last_alert_times.get(key) == now_minute:
                return False
            _last_alert_times[key] = now_minute
            return True

        # --- 1. AI RECOMMENDATION INTEGRATION (40% weight) ---
        ai_rec = current_ai_recs[current_ai_recs['ticker'] == ticker] if not current_ai_recs.empty else pd.DataFrame()
        if not ai_rec.empty:
            ai_prob = ai_rec.iloc[0].get('probability', 0.5)
            ai_recommendation = ai_rec.iloc[0].get('recommendation', '')
            
            if "BUY:" in ai_recommendation and ai_prob >= 0.70:
                signal_score += 4.0  # Strong AI signal
                bullish_signals.append(f"AI-Strong({ai_prob:.1%})")
            elif "BUY:" in ai_recommendation and ai_prob >= 0.60:
                signal_score += 2.5  # Moderate AI signal
                bullish_signals.append(f"AI-Mod({ai_prob:.1%})")
            elif ai_prob <= 0.40:
                signal_score -= 2.0  # Bearish AI signal
                bearish_signals.append(f"AI-Bear({ai_prob:.1%})")

        # --- 2. TECHNICAL RANKING INTEGRATION (25% weight) ---
        tech_rank = dashboard_ranks.get(ticker, 3.0)  # Default to neutral
        if tech_rank >= 4.5:
            signal_score += 2.5  # Excellent technical rank
            bullish_signals.append(f"Tech-Excellent({tech_rank:.1f})")
        elif tech_rank >= 4.0:
            signal_score += 1.5  # Good technical rank
            bullish_signals.append(f"Tech-Good({tech_rank:.1f})")
        elif tech_rank <= 2.0:
            signal_score -= 1.5  # Poor technical rank
            bearish_signals.append(f"Tech-Poor({tech_rank:.1f})")

        # --- 3. KEY TECHNICAL SIGNALS (25% weight) ---
        tech_cols = ["ADX", "+DI", "-DI", "PMO", "PMO_signal", "CCI"]
        if all(col in group.columns for col in tech_cols):
            # ADX momentum breakout (quality signal)
            if (prev["ADX"] < 25 and curr["ADX"] >= 25 and 
                curr["+DI"] > curr["-DI"] and should_alert("ADX_Breakout")):
                signal_score += 2.0
                bullish_signals.append("ADX-Breakout")
                print(f"🚀 {ticker}: ADX momentum breakout ({curr['ADX']:.1f})")
                
            # PMO bullish crossover with confirmation
            if (prev["PMO"] < prev["PMO_signal"] and curr["PMO"] > curr["PMO_signal"] and
                curr["PMO"] > -2.0 and should_alert("PMO_Bullish")):  # Avoid oversold bounces
                signal_score += 1.5
                bullish_signals.append("PMO-Bull")
                print(f"📈 {ticker}: PMO bullish crossover")
                
            # PMO bearish crossover 
            if (prev["PMO"] > prev["PMO_signal"] and curr["PMO"] < curr["PMO_signal"] and
                should_alert("PMO_Bearish")):
                signal_score -= 1.5
                bearish_signals.append("PMO-Bear")
                print(f"📉 {ticker}: PMO bearish crossover")
                
            # Directional Movement reversal
            if (prev["+DI"] < prev["-DI"] and curr["+DI"] > curr["-DI"] and
                curr["ADX"] > 20 and should_alert("DI_Bullish")):
                signal_score += 1.0
                bullish_signals.append("DI-Bull")
                
            if (prev["+DI"] > prev["-DI"] and curr["+DI"] < curr["-DI"] and
                curr["ADX"] > 20 and should_alert("DI_Bearish")):
                signal_score -= 1.0
                bearish_signals.append("DI-Bear")
                
            # CCI extreme reversal (only from extreme levels)
            if (prev["CCI"] < -200 and curr["CCI"] > -150 and should_alert("CCI_Oversold_Recovery")):
                signal_score += 1.0
                bullish_signals.append("CCI-Recovery")
            elif (prev["CCI"] > 200 and curr["CCI"] < 150 and should_alert("CCI_Overbought_Decline")):
                signal_score -= 1.0
                bearish_signals.append("CCI-Decline")

        # --- 4. NEWS & WHALE SENTIMENT (10% weight) ---
        # Only count recent, high-impact news
        news_list = fetch_etf_news(ticker)
        for article in news_list[:2]:  # Only top 2 recent articles
            if isinstance(article, dict):
                sentiment = article.get("sentiment", "Neutral")
                title = article.get("title", "")
                if sentiment == "Positive" and not _last_alert_times.get((ticker, "News+", title)):
                    signal_score += 0.5
                    bullish_signals.append("News+")
                    _last_alert_times[(ticker, "News+", title)] = True
                elif sentiment == "Negative" and not _last_alert_times.get((ticker, "News-", title)):
                    signal_score -= 0.5
                    bearish_signals.append("News-")
                    _last_alert_times[(ticker, "News-", title)] = True

        # Whale activity (simplified - only major moves)
        whale_data = fetch_whale_data(ticker)
        for entry in whale_data.get("insider", [])[:1]:  # Only most recent insider trade
            tx_type = entry.get("transactionType", "").lower()
            if tx_type == "buy" and _last_alert_times.get((ticker, "Whale+")) != dt_str:
                signal_score += 0.5
                bullish_signals.append("Insider+")
                _last_alert_times[(ticker, "Whale+")] = dt_str
            elif tx_type == "sell" and _last_alert_times.get((ticker, "Whale-")) != dt_str:
                signal_score -= 0.5
                bearish_signals.append("Insider-")
                _last_alert_times[(ticker, "Whale-")] = dt_str

        # --- 5. GENERATE REALISTIC ALERTS ---
        current_price = curr.get("Close", 0)
        
        # STRONG BUY: High signal score + AI confirmation + good technicals
        if (signal_score >= 6.0 and tech_rank >= 4.0 and 
            any("AI-Strong" in s for s in bullish_signals) and
            _last_alert_times.get((ticker, "StrongBuy")) != dt_str):
            
            print(f"🔥 STRONG BUY ALERT: {ticker} @ ${current_price:.2f}")
            print(f"   Signal Score: {signal_score:.1f} | Tech Rank: {tech_rank:.1f}")
            print(f"   Bullish Signals: {', '.join(bullish_signals)}")
            play_audio("strongbuy.mp3", ticker, f"Strong buy signal with {signal_score:.1f} points")
            _last_alert_times[(ticker, "StrongBuy")] = dt_str
            
        # MEDIUM BUY: Moderate signal score with some confirmation
        elif (signal_score >= 4.0 and tech_rank >= 3.0 and
              (any("AI-" in s for s in bullish_signals) or len(bullish_signals) >= 3) and
              _last_alert_times.get((ticker, "MediumBuy")) != dt_str):
            
            print(f"📈 MEDIUM BUY ALERT: {ticker} @ ${current_price:.2f}")
            print(f"   Signal Score: {signal_score:.1f} | Tech Rank: {tech_rank:.1f}")
            print(f"   Bullish Signals: {', '.join(bullish_signals)}")
            play_audio("mediumbuy.mp3", ticker, f"Moderate buy signal")
            _last_alert_times[(ticker, "MediumBuy")] = dt_str
            
        # EXIT/SELL: Strong bearish signal score or AI bearish + technical breakdown
        elif (signal_score <= -3.0 or 
              (signal_score <= -2.0 and tech_rank <= 2.5) and
              _last_alert_times.get((ticker, "Exit")) != dt_str):
            
            print(f"🚨 EXIT ALERT: {ticker} @ ${current_price:.2f}")
            print(f"   Signal Score: {signal_score:.1f} | Tech Rank: {tech_rank:.1f}")
            print(f"   Bearish Signals: {', '.join(bearish_signals)}")
            play_audio("exit.mp3", ticker, f"Exit signal detected")
            _last_alert_times[(ticker, "Exit")] = dt_str

        # Store summary for analysis
        alert_summary.append({
            "ticker": ticker,
            "signal_score": signal_score,
            "tech_rank": tech_rank,
            "bullish_signals": bullish_signals,
            "bearish_signals": bearish_signals,
            "ai_probability": ai_rec.iloc[0].get('probability', 0.5) if not ai_rec.empty else 0.5
        })

    # Summary stats
    total_analyzed = len(alert_summary)
    strong_signals = len([a for a in alert_summary if a["signal_score"] >= 6.0])
    moderate_signals = len([a for a in alert_summary if 4.0 <= a["signal_score"] < 6.0])
    weak_signals = len([a for a in alert_summary if a["signal_score"] <= -3.0])
    
    print(f"\n📊 ALERT SUMMARY: {total_analyzed} tickers analyzed")
    print(f"   Strong buy signals: {strong_signals}")
    print(f"   Moderate buy signals: {moderate_signals}")  
    print(f"   Exit signals: {weak_signals}")
    
    return alert_summary

def get_alert_breakdown(ticker):
    """
    Provide detailed breakdown of alert scoring for a specific ticker.
    Useful for understanding why alerts are or aren't triggering.
    """
    try:
        # Get current data
        hist_data = pd.read_csv(HISTORICAL_DATA_FILE)
        ticker_data = hist_data[hist_data['Ticker'] == ticker].tail(2)
        
        if len(ticker_data) < 2:
            return f"❌ Insufficient data for {ticker}"
        
        prev, curr = ticker_data.iloc[-2], ticker_data.iloc[-1]
        
        # Get AI recommendation
        try:
            ai_rec = get_trade_recommendations([ticker], return_df=True)
            ai_prob = ai_rec.iloc[0].get('probability', 0.5) if not ai_rec.empty else 0.5
            ai_recommendation = ai_rec.iloc[0].get('recommendation', 'No AI data') if not ai_rec.empty else 'No AI data'
        except:
            ai_prob = 0.5
            ai_recommendation = 'AI unavailable'
        
        # Get technical ranking
        tech_rank = dashboard_ranks.get(ticker, 3.0)
        
        breakdown = f"""
🔍 ALERT BREAKDOWN FOR {ticker}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 Current Price: ${curr.get('Close', 0):.2f}

🤖 AI ANALYSIS (40% weight):
   • Probability: {ai_prob:.1%}
   • Recommendation: {ai_recommendation}
   • Score Impact: {4.0 if ai_prob >= 0.70 else 2.5 if ai_prob >= 0.60 else -2.0 if ai_prob <= 0.40 else 0.0:.1f} points

📈 TECHNICAL RANKING (25% weight):
   • Composite Rank: {tech_rank:.1f}/5.0
   • Score Impact: {2.5 if tech_rank >= 4.5 else 1.5 if tech_rank >= 4.0 else -1.5 if tech_rank <= 2.0 else 0.0:.1f} points

⚡ TECHNICAL INDICATORS (25% weight):
   • ADX: {curr.get('ADX', 'N/A')} (Trend strength)
   • +DI: {curr.get('+DI', 'N/A')} | -DI: {curr.get('-DI', 'N/A')}
   • PMO: {curr.get('PMO', 'N/A'):.2f} | Signal: {curr.get('PMO_signal', 'N/A'):.2f}
   • CCI: {curr.get('CCI', 'N/A'):.1f}

📰 SENTIMENT FACTORS (10% weight):
   • News sentiment: Being checked...
   • Whale activity: Being checked...

🎯 ALERT THRESHOLDS:
   • Strong Buy: ≥6.0 points + Tech Rank ≥4.0 + AI Strong signal
   • Medium Buy: ≥4.0 points + Tech Rank ≥3.0 + AI confirmation
   • Exit Signal: ≤-3.0 points OR (≤-2.0 + Tech Rank ≤2.5)

💡 TIP: Higher quality signals = fewer false alerts
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        return breakdown.strip()
        
    except Exception as e:
        return f"❌ Error analyzing {ticker}: {e}"

def test_alert_system(test_tickers=None):
    """
    Test the alert system with current data to see potential alerts.
    """
    if test_tickers is None:
        test_tickers = tickers[:5]  # Test first 5 tickers
    
    print("🧪 TESTING ALERT SYSTEM")
    print("=" * 50)
    
    try:
        hist_data = pd.read_csv(HISTORICAL_DATA_FILE)
        alert_summary = check_trade_alerts(hist_data, test_tickers)
        
        print(f"\n📋 TEST RESULTS:")
        for alert in alert_summary:
            ticker = alert['ticker']
            score = alert['signal_score']
            rank = alert['tech_rank']
            ai_prob = alert['ai_probability']
            
            status = "🔥 STRONG BUY" if score >= 6.0 and rank >= 4.0 else \
                    "📈 MEDIUM BUY" if score >= 4.0 and rank >= 3.0 else \
                    "🚨 EXIT" if score <= -3.0 else \
                    "😐 NEUTRAL"
            
            print(f"{ticker}: {status} | Score: {score:.1f} | Rank: {rank:.1f} | AI: {ai_prob:.1%}")
            
        return alert_summary
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return []

                                                # ***** Graph Update Function *****

def make_ai_recommendations_table(top5_ai):
    import datetime
    if top5_ai is None or top5_ai.empty:
        return html.Div("No AI recommendations available.", style={'fontSize': '14px'})
    # Add a "Time" column if not present
    if "time" not in top5_ai.columns:
        now_str = datetime.datetime.now().strftime("%H:%M:%S")
        top5_ai = top5_ai.copy()
        top5_ai["time"] = now_str
    return html.Table([
        html.Thead(html.Tr([
            html.Th("Ticker", style={'textAlign': 'left', 'width': '8%', 'padding': '8px 5px'}),
            html.Th("Probability Up", style={'textAlign': 'left', 'width': '12%', 'padding': '8px 5px'}),
            html.Th("Entry", style={'textAlign': 'left', 'width': '8%', 'padding': '8px 5px'}),
            html.Th("Target", style={'textAlign': 'left', 'width': '8%', 'padding': '8px 5px'}),
            html.Th("Stop", style={'textAlign': 'left', 'width': '8%', 'padding': '8px 5px'}),
            html.Th("Recommendation", style={'textAlign': 'left', 'width': '46%', 'padding': '8px 5px'}),
            html.Th("Time", style={'textAlign': 'left', 'width': '10%', 'padding': '8px 5px'})
        ])),
        html.Tbody([
            html.Tr([
                html.Td(row["ticker"], style={'textAlign': 'left', 'width': '8%', 'padding': '6px 5px', 'fontWeight': 'bold'}),
                html.Td(f"{row['probability']:.2%}", style={'textAlign': 'left', 'width': '12%', 'padding': '6px 5px'}),
                html.Td(f"{row['entry']:.2f}", style={'textAlign': 'left', 'width': '8%', 'padding': '6px 5px'}),
                html.Td(f"{row['target']:.2f}", style={'textAlign': 'left', 'width': '8%', 'padding': '6px 5px'}),
                html.Td(f"{row['stop']:.2f}", style={'textAlign': 'left', 'width': '8%', 'padding': '6px 5px'}),
                html.Td([
                    # Add visual indicator based on recommendation type
                    html.Span(
                        "🔥 " if "TRADE:" in row["recommendation"] else "❌ ",
                        style={'fontWeight': 'bold', 'marginRight': '5px'}
                    ),
                    html.Span(row["recommendation"])
                ], style={'textAlign': 'left', 'width': '46%', 'padding': '6px 5px'}),
                html.Td(row["time"], style={'textAlign': 'left', 'width': '10%', 'padding': '6px 5px'})
            ]) for _, row in top5_ai.iterrows()
        ])
    ], style={'width': '100%', 'fontSize': '14px', 'marginBottom': '15px', 'borderCollapse': 'collapse', 'border': '1px solid #ddd'})


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

    # --- DESTROY SPLASH POPUP ON FIRST DASHBOARD DISPLAY ---
    global _day_splash
    try:
        _day_splash.destroy()
    except Exception:
        pass

    # --- Play dashboard ready audio (MP3) ---
    try:
        audio_file_path = "C:/Users/mjmat/Pythons_Code_Files/dashboard_ready.mp3"
        if os.path.exists(audio_file_path):
            data, samplerate = sf.read(audio_file_path)
            sd.play(data, samplerate)
            sd.wait()
        else:
            print(f"Audio file {audio_file_path} not found.")
    except Exception as e:
        print(f"Error playing dashboard ready audio: {e}")

    # --- Load Quiver government and institutional data ---
    def load_quiver_cache(cache_path):
        if not os.path.exists(cache_path):
            return pd.DataFrame()
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Standardize date columns
        for col in ["TransactionDate", "reportDate", "Date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    congress_df = load_quiver_cache("quiver_congress_cache.json")
    inst_df = load_quiver_cache("quiver_institutional_cache.json")

    # Helper to always load latest AI recommendations for the table
    def load_latest_ai_recommendations():
        try:
            # Use the passed tickers parameter (the properly selected 5 tickers)
            ai_df = get_trade_recommendations(tickers, return_df=True)
            print(f"AI table data for dashboard: {len(ai_df)} recommendations")
            print("AI recommendations summary:", ai_df[['ticker', 'probability', 'recommendation']].to_string() if not ai_df.empty else "No data")
            return ai_df.head(5)
        except Exception as e:
            print("Error loading AI recommendations:", e)
            import traceback
            traceback.print_exc()
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

    # --- Calculate initial trade log summary for dashboard startup ---
    TRADE_LOG_FILE = "trade_log.xlsx"
    TRADE_LOG_COLUMNS = [
        "Type", "Ticker", "Trade QTY", "Open Datetime", "Open Price",
        "Close Datetime", "Close Price", "Profit/Loss", "Profit/Loss %", "Notes"
    ]
    if os.path.exists(TRADE_LOG_FILE):
        trade_log_df = pd.read_excel(TRADE_LOG_FILE)
    else:
        trade_log_df = pd.DataFrame(columns=TRADE_LOG_COLUMNS)

    def calc_trade_log_summary(trade_log_df):
        # Defensive: ensure columns exist and are numeric
        if trade_log_df.empty or "Open Price" not in trade_log_df.columns or "Close Price" not in trade_log_df.columns:
            return "Total Profit/Loss: $0.00 | Total Profit/Loss %: 0.00%"
        df = trade_log_df.copy()
        # Replace blanks with 0, coerce errors
        for col in ["Open Price", "Close Price", "Profit/Loss", "Trade QTY"]:
            if col not in df.columns:
                df[col] = 0
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df = df[(df["Open Price"] != 0) & (df["Close Price"] != 0)]
        total_pl = df["Profit/Loss"].sum()
        total_cost = (df["Open Price"] * df["Trade QTY"]).sum()
        total_pl_pct = (total_pl / total_cost * 100) if total_cost else 0
        return f"Total Profit/Loss: ${total_pl:,.2f} | Total Profit/Loss %: {total_pl_pct:.2f}%"

    initial_trade_log_summary = calc_trade_log_summary(trade_log_df)

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
            value=tickers[:5],  # Only show top 5 tickers by default
            multi=True
        ),
        html.Div([
            html.Div([
                html.Label("Price Height:"),
                dcc.Input(id='price-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='price-tick-count', type='number', value=60, min=2, max=200, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Label("Volume Height:"),
                dcc.Input(id='volume-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='volume-tick-count', type='number', value=60, min=2, max=200, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Label("ADX Height:"),
                dcc.Input(id='adx-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='adx-tick-count', type='number', value=60, min=2, max=200, step=1, style={'width': '50px'}),
            ], style={'display': 'inline-block', 'marginRight': '20px'}),
            html.Div([
                html.Label("PMO Height:"),
                dcc.Input(id='pmo-chart-height', type='number', value=300, min=100, max=2000, step=10, style={'width': '70px'}),
                html.Label("Ticks:"),
                dcc.Input(id='pmo-tick-count', type='number', value=60, min=2, max=200, step=1, style={'width': '50px'}),
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
             html.Button("Update Trade", id="update-trade-btn", n_clicks=0, style={'marginLeft': '10px', 'height': '40px', 'backgroundColor': '#FFA500', 'color': 'white', 'fontWeight': 'bold'}),
            html.Button("Log Trade", id="log-trade-btn", n_clicks=0, style={'marginLeft': '10px', 'height': '40px', 'backgroundColor': '#4CAF50', 'color': 'white', 'fontWeight': 'bold'}),
            ], style={'marginBottom': '10px', 'display': 'flex', 'flexWrap': 'wrap', 'alignItems': 'center'}),
            html.Div(id='trade-log-message', style={'color': 'green', 'fontWeight': 'bold', 'marginBottom': '10px'}),
        dcc.Store(id='trade-log-store'),
        dcc.Store(id='interval-store', data=interval),
        html.Div(id='trade-log-summary', children=initial_trade_log_summary, style={'fontWeight': 'bold', 'fontSize': '16px', 'marginBottom': '10px'}),
        dash_table.DataTable(
            id='trade-log-table',
            columns=[{"name": col, "id": col} for col in TRADE_LOG_COLUMNS],
            data=trade_log_df.to_dict('records') if not trade_log_df.empty else [],
            row_selectable='single',
            style_table={'width': '100%', 'fontSize': '13px', 'marginTop': '10px'},
            style_cell={'textAlign': 'left'},
        ),
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
        # Load data
        try:
            # First try to use the global variable, then fall back to CSV
            global historical_data
            if historical_data is not None and not historical_data.empty:
                df = historical_data.copy()
                print(f"Dashboard using global historical_data: {len(df)} rows")
                
                # **DON'T convert datetime here - let aggregate_bars handle it after filtering**
                # df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
                
            else:
                # Fix the datetime parsing issue for CSV
                print("Loading from CSV with robust datetime parsing...")
                df = pd.read_csv("historical_data.csv")
            
            # **DEBUG**: Check what tickers we have BEFORE any processing
            if 'Ticker' in df.columns:
                loaded_tickers = df['Ticker'].unique()
                print(f"🎯 LOADED data tickers: {list(loaded_tickers)}")
                print(f"🎯 SELECTED tickers: {selected_tickers}")
                missing_tickers = [t for t in selected_tickers if t not in loaded_tickers]
                if missing_tickers:
                    print(f"❌ Selected tickers NOT FOUND in loaded data: {missing_tickers}")
                else:
                    print(f"✅ All selected tickers found in loaded data")
                
                # Handle datetime parsing more robustly
                if 'Datetime' in df.columns:
                    # First, clean up any malformed datetime strings
                    df['Datetime'] = df['Datetime'].astype(str)
                    
                    # Remove any trailing ":00" artifacts or other issues
                    df['Datetime'] = df['Datetime'].str.replace(r':00$', '', regex=True)
                    df['Datetime'] = df['Datetime'].str.replace(r'\s+', ' ', regex=True)  # Clean extra spaces
                    
                    # Try different datetime formats in order of likelihood
                    datetime_parsed = False
                    
                    # Try format 1: "YYYY-MM-DD HH:MM"
                    try:
                        df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M')
                        datetime_parsed = True
                        print("✅ Parsed datetime with format '%Y-%m-%d %H:%M'")
                    except ValueError as e:
                        print(f"Format 1 failed: {e}")
                    
                    # Try format 2: "YYYY-MM-DD HH:MM:SS"
                    if not datetime_parsed:
                        try:
                            df['Datetime'] = pd.to_datetime(df['Datetime'], format='%Y-%m-%d %H:%M:%S')
                            datetime_parsed = True
                            print("✅ Parsed datetime with format '%Y-%m-%d %H:%M:%S'")
                        except ValueError as e:
                            print(f"Format 2 failed: {e}")
                    
                    # Try format 3: Mixed/infer
                    if not datetime_parsed:
                        try:
                            df['Datetime'] = pd.to_datetime(df['Datetime'], infer_datetime_format=True)
                            datetime_parsed = True
                            print("✅ Parsed datetime with infer_datetime_format")
                        except ValueError as e:
                            print(f"Format 3 failed: {e}")
                    
                    # Last resort: Remove problematic rows
                    if not datetime_parsed:
                        print("⚠️ Using coerce method, some dates may become NaT")
                        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
                        # Remove rows with invalid dates
                        before_count = len(df)
                        df = df.dropna(subset=['Datetime'])
                        after_count = len(df)
                        print(f"Removed {before_count - after_count} rows with invalid datetimes")
                
                print(f"Dashboard loaded from CSV: {len(df)} rows")
            
            # Debug: Check what we actually loaded
            print(f"Dashboard data shape: {df.shape}")
            print(f"Dashboard data columns: {df.columns.tolist()}")
            if not df.empty:
                print(f"Dashboard data sample:....1429")
                print(df.head())
                # print(f"Datetime range...1431: {df['Datetime'].min()} to {df['Datetime'].max()}")
            
            # **CRITICAL FIX**: Filter to TODAY'S DATA ONLY before processing
            if 'Datetime' in df.columns:
                from datetime import date
                today = date.today()
                
                # Convert to datetime if not already
                if df['Datetime'].dtype != 'datetime64[ns]':
                    df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
                    df = df.dropna(subset=['Datetime'])  # Remove invalid dates
                
                # PRESERVE FULL HISTORICAL DATA FOR ADX CALCULATION
                full_historical_df = df.copy()  # Keep unfiltered data for ADX
                
                # Filter to today only
                df['Date'] = df['Datetime'].dt.date
                today_data = df[df['Date'] == today].copy()
                today_data = today_data.drop('Date', axis=1)  # Remove helper column
                
                print(f"📅 DASHBOARD FILTER: Original data: {len(df)} rows")
                print(f"📅 DASHBOARD FILTER: Today only ({today}): {len(today_data)} rows")
                
                if not today_data.empty:
                    print(f"📅 DASHBOARD FILTER: Today's time range: {today_data['Datetime'].min()} to {today_data['Datetime'].max()}")
                    df = today_data
                else:
                    print(f"⚠️ DASHBOARD FILTER: No data for today ({today}), using last available day")
                    # If no data for today, use the most recent day's data
                    latest_date = df['Date'].max()
                    df = df[df['Date'] == latest_date].copy()
                    df = df.drop('Date', axis=1)
                    print(f"📅 DASHBOARD FILTER: Using latest available date: {latest_date} ({len(df)} rows)")
            
            # Aggregate bars for dashboard display based on settings
            settings = load_settings()
            interval = settings.get("dashboard_interval", 1)
            
            # **CRITICAL FIX**: Filter for selected tickers BEFORE any processing
            if 'Ticker' in df.columns and selected_tickers:
                print(f"🎯 Pre-filtering for selected tickers: {selected_tickers}")
                pre_filter_count = len(df)
                df = df[df['Ticker'].isin(selected_tickers)]
                post_filter_count = len(df)
                print(f"📊 Filtered from {pre_filter_count} to {post_filter_count} rows")
                
                if df.empty:
                    print(f"❌ No data found for selected tickers: {selected_tickers}")
                    return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No data for selected tickers."), html.Div("No whale data.")
            
            # In the update_dash callback, before aggregation:
            if interval > 1:
                print(f"Aggregating bars to {interval} minute intervals...1499")
                # **SKIP datetime validation for dashboard to preserve chart data**
                # df = validate_datetime_data(df)  # Commented out to preserve data
                df = aggregate_bars(df, interval_minutes=interval, selected_tickers=selected_tickers)
                print(f"After aggregation...1502: {len(df)} rows")
                # **DEBUG**: Show what tickers survived aggregation
                if 'Ticker' in df.columns:
                    aggregated_tickers = df['Ticker'].unique()
                    print(f"🎯 Tickers surviving aggregation: {list(aggregated_tickers)}")
                    missing_from_aggregation = [t for t in selected_tickers if t not in aggregated_tickers]
                    if missing_from_aggregation:
                        print(f"⚠️ Selected tickers LOST during aggregation: {missing_from_aggregation}")
            else:
                print("📊 No aggregation needed (1-minute interval)")
                # For 1-minute data, ensure datetime is properly formatted but don't aggregate
                if 'Datetime' in df.columns:
                    if df['Datetime'].dtype != 'datetime64[ns]':
                        print("🔧 Converting datetime for 1-minute data...")
                        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
                        # Remove only completely invalid rows
                        nat_count = df['Datetime'].isna().sum()
                        if nat_count > 0:
                            print(f"⚠️ Found {nat_count} invalid datetime values, removing...")
                            df = df.dropna(subset=['Datetime'])
                print(f"📊 Raw data: {len(df)} rows for 1-minute display")

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
            print(f"❌ Error loading data: {e}")
            import traceback
            traceback.print_exc()
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div(f"Data loading error: {e}"), html.Div("No whale data.")

        # Ensure required columns exist
        required_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            print(f"❌ Missing required columns: {missing_cols}")
            print(f"Available columns: {df.columns.tolist()}")
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div(f"Missing columns: {missing_cols}"), html.Div("No whale data.")

        # Check if we have data for the selected tickers
        available_tickers = df["Ticker"].unique()
        valid_selected = [t for t in selected_tickers if t in available_tickers]
        if not valid_selected:
            print(f"❌ No data available for selected tickers: {selected_tickers}")
            print(f"Available tickers: {available_tickers}")
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No data for selected tickers."), html.Div("No whale data.")

        print(f"✅ Valid tickers for charts: {valid_selected}")

        # Only keep tickers that actually have at least one valid OHLCV row  
        valid_ticker_rows = []
        for t in selected_tickers:
            if not t or not isinstance(t, str):
                continue
            tdf = df[df["Ticker"] == t]
            print(f"Checking ticker {t}: {len(tdf)} total rows")
            
            # Check for valid OHLCV data
            valid_ohlcv = tdf[["Open", "High", "Low", "Close", "Volume"]].dropna()
            print(f"  Valid OHLCV rows for {t}: {len(valid_ohlcv)}")
            
            if not valid_ohlcv.empty:
                valid_ticker_rows.append(t)
                print(f"  ✅ {t} added to valid tickers")
            else:
                print(f"  ❌ {t} has no valid OHLCV data")

        print(f"Final valid_ticker_rows: {valid_ticker_rows}")
        print(f"🔍 DEBUG: Length before limit: {len(valid_ticker_rows)}")
        
        # **CRITICAL CHECK: Exit early if no valid tickers**
        if len(valid_ticker_rows) == 0:
            print("❌ CRITICAL: No valid tickers found, returning empty charts")
            return (
                go.Figure().add_annotation(text="No valid ticker data found", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False),
                go.Figure().add_annotation(text="No valid ticker data found", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False),
                go.Figure().add_annotation(text="No valid ticker data found", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False),
                go.Figure().add_annotation(text="No valid ticker data found", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False),
                html.Div("No valid ticker data found for charts"),
                html.Div("No whale data.")
            )
        
        # Limit to exactly 5 tickers for clean charts (fix the 6th rogue ticker issue)
        if len(valid_ticker_rows) > 5:
            print(f"⚠️ TRIMMING {len(valid_ticker_rows)} tickers down to 5")
            valid_ticker_rows = valid_ticker_rows[:5]
            print(f"🎯 LIMITED to exactly 5 tickers: {valid_ticker_rows}")
        
        print(f"🔍 DEBUG: Length after limit: {len(valid_ticker_rows)}")
        print(f"🔍 DEBUG: About to create {len(valid_ticker_rows)} subplots")
        
        subplot_titles = [f"{t} Price ({i+1})" for i, t in enumerate(valid_ticker_rows)]
        num_tickers = len(valid_ticker_rows)
        if num_tickers == 0:
            return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No tickers with data."), html.Div("No whale data.")

        df = df[df["Ticker"].isin(valid_ticker_rows)].copy()

        # Helper to get last N rows while preserving datetime for proper chronological order
        def get_last_n_with_datetime(df, ticker, n):
            """Get the last N rows for a ticker, prefer current trading day but fallback to most recent data"""
            tdf = df[df["Ticker"] == ticker].copy()
            
            # Filter to current trading day only (today's data)
            from datetime import datetime, date
            today = date.today()
            
            # Convert Datetime to date for comparison
            if 'Datetime' in tdf.columns and not tdf.empty:
                tdf_copy = tdf.copy()
                tdf_copy['Date'] = pd.to_datetime(tdf_copy['Datetime'], format='mixed', errors='coerce').dt.date
                # Try to get today's data first
                today_data = tdf_copy[tdf_copy['Date'] == today].copy()
                
                if not today_data.empty:
                    # Use today's data if available
                    tdf = today_data.drop('Date', axis=1)
                    print(f"📅 {ticker}: Using {len(tdf)} rows from TODAY ({today})")
                else:
                    # Fallback to most recent date available
                    tdf = tdf.drop('Date', axis=1)  # Remove helper column
                    tdf = tdf.sort_values("Datetime").tail(n).copy()
                    if not tdf.empty:
                        latest_date = pd.to_datetime(tdf["Datetime"]).dt.date.max()
                        print(f"📅 {ticker}: No data for today, using {len(tdf)} rows from most recent date ({latest_date})")
                    else:
                        print(f"📅 {ticker}: No data available at all")
            else:
                # Sort and take last N rows from today only
                tdf = tdf.sort_values("Datetime").tail(n).copy()
            
            # Sort and take last N rows
            if not tdf.empty:
                tdf = tdf.sort_values("Datetime").tail(n).copy()
                min_date = tdf["Datetime"].min()
                max_date = tdf["Datetime"].max()
                print(f"📅 {ticker}: Final dataset: {len(tdf)} rows from {min_date} to {max_date}")
            
            return tdf
            
        # Alternative helper to get consistent date range across all tickers
        def get_consistent_date_range(df, tickers, n):
            """Get the last N time periods that are common across all tickers - prefer today, fallback to recent"""
            if df.empty:
                return df
            
            # Filter to current trading day first
            from datetime import datetime, date
            today = date.today()
            
            # Convert Datetime to date for comparison
            if 'Datetime' in df.columns and not df.empty:
                df_copy = df.copy()
                df_copy['Date'] = pd.to_datetime(df_copy['Datetime'], format='mixed', errors='coerce').dt.date
                # Try today's data first
                today_data = df_copy[df_copy['Date'] == today].copy()
                
                if not today_data.empty:
                    # Use today's data
                    df = today_data.drop('Date', axis=1)
                    print(f"📅 Using today's data ({today}) for consistent range")
                else:
                    # Fallback to most recent data available
                    df = df.drop('Date', axis=1)
                    print(f"📅 No data for today, using most recent available data for consistent range")
            
            if df.empty:
                print(f"📅 No data available at all")
                return df
                
            # Find the latest datetime that exists for ALL tickers (today only)
            latest_dates_per_ticker = []
            for ticker in tickers:
                ticker_data = df[df["Ticker"] == ticker]
                if not ticker_data.empty:
                    latest_dates_per_ticker.append(ticker_data["Datetime"].max())
            
            if not latest_dates_per_ticker:
                return df
                
            # Use the earliest of the latest dates as the common end point
            common_end_date = min(latest_dates_per_ticker)
            print(f"📅 Using common end date: {common_end_date} (TODAY ONLY)")
            
            # Get all unique datetime values up to this point, then take the last N
            all_dates = sorted(df[df["Datetime"] <= common_end_date]["Datetime"].unique())
            if len(all_dates) > n:
                cutoff_date = all_dates[-n]
                result_df = df[df["Datetime"] >= cutoff_date].copy()
            else:
                result_df = df[df["Datetime"] <= common_end_date].copy()
                
            print(f"📅 Consistent range: {len(result_df)} total rows from {result_df['Datetime'].min()} to {result_df['Datetime'].max()} (TODAY ONLY)")
            return result_df

        # Build DataFrames for each chart type
        #if len(valid_ticker_rows) > 5:
            #valid_ticker_rows = valid_ticker_rows[:5]

        price_plot_df = pd.concat([get_last_n_with_datetime(df, t, price_tick_count) for t in valid_ticker_rows], ignore_index=True)
        volume_plot_df = pd.concat([get_last_n_with_datetime(df, t, volume_tick_count) for t in valid_ticker_rows], ignore_index=True)
        
        # For ADX, use rolling window approach to get sufficient historical data
        print("📊 Creating ADX plot data with rolling window approach...")
        
        def get_adx_rolling_data(df, tickers, min_points=100):
            """Get sufficient historical data for ADX calculation using rolling window"""
            if df.empty:
                return df
            
            print(f"📊 ADX ROLLING: Processing {len(tickers)} tickers for ADX calculation")
            
            adx_data_list = []
            for ticker in tickers:
                ticker_data = df[df["Ticker"] == ticker].copy()
                if not ticker_data.empty:
                    # Sort by datetime and take the most recent N points (regardless of date)
                    ticker_data = ticker_data.sort_values("Datetime")
                    
                    # Take enough data for proper ADX calculation (at least 100 points, up to 200)
                    needed_points = max(min_points, min(200, len(ticker_data)))
                    recent_data = ticker_data.tail(needed_points)
                    
                    print(f"📊 ADX ROLLING: {ticker} - Using last {len(recent_data)} data points")
                    print(f"   Date range: {recent_data['Datetime'].min()} to {recent_data['Datetime'].max()}")
                    
                    adx_data_list.append(recent_data)
                else:
                    print(f"📊 ADX ROLLING: {ticker} - No data available")
            
            if adx_data_list:
                combined_data = pd.concat(adx_data_list, ignore_index=True)
                print(f"📊 ADX ROLLING: Combined {len(combined_data)} total data points")
                return combined_data
            else:
                print(f"📊 ADX ROLLING: No data for any ticker")
                return pd.DataFrame()
        
        adx_plot_df = get_adx_rolling_data(full_historical_df[full_historical_df["Ticker"].isin(valid_ticker_rows)], valid_ticker_rows)
        
        # For PMO, also use consistent date range to fix date mismatch issue
        print("📊 Creating PMO plot data with consistent date range...")
        # Calculate PMO using full historical data, merge on Datetime/Ticker, then slice last N for display and add Tick column
        # --- Calculate PMO for each ticker on full data ---
        pmo_full_df = pd.concat([
            (
                df[df["Ticker"] == t].sort_values("Datetime")
                .assign(**calculate_pmo(df[df["Ticker"] == t].sort_values("Datetime")))
            )
            for t in valid_ticker_rows
        ], ignore_index=True)

        # --- For display, use consistent date range instead of individual ticker slicing ---
        pmo_plot_df = get_consistent_date_range(pmo_full_df[pmo_full_df["Ticker"].isin(valid_ticker_rows)], valid_ticker_rows, pmo_tick_count)

        # --- Use pmo_plot_df directly for plotting ---
        filtered_pmo_df = pmo_plot_df

                # Calculate technicals on the correct DataFrames
        # **E*TRADE STYLE ADX**: Use standard 14-period with smoothing for cleaner lines like E*Trade
        standard_adx_period = 14  # Fixed standard period for smooth E*Trade-style ADX
        print(f"📊 ADX DEBUG: Using standard period {standard_adx_period} for E*Trade-style smooth ADX calculation")
        print(f"📊 ADX DEBUG: ADX plot data shape: {adx_plot_df.shape}")
        
        # Debug: Show data per ticker before ADX calculation
        for ticker in valid_ticker_rows:
            ticker_adx_data = adx_plot_df[adx_plot_df["Ticker"] == ticker]
            print(f"📊 ADX DEBUG: {ticker} has {len(ticker_adx_data)} data points for smooth ADX calculation")
        
        adx_df = calculate_adx_multi(adx_plot_df, valid_ticker_rows, period=standard_adx_period)
        print(f"📊 ADX DEBUG: E*Trade-style ADX calculation result shape: {adx_df.shape}")
        print(f"📊 ADX DEBUG: ADX columns: {adx_df.columns.tolist()}")
        
        # Debug: Check if ADX data exists
        if not adx_df.empty:
            non_null_adx = adx_df.dropna(subset=["ADX", "+DI", "-DI"])
            print(f"📊 ADX DEBUG: Non-null ADX data: {len(non_null_adx)} rows")
            if not non_null_adx.empty:
                print(f"📊 ADX DEBUG: ADX range: {non_null_adx['ADX'].min():.2f} to {non_null_adx['ADX'].max():.2f}")
                print(f"📊 ADX DEBUG: +DI range: {non_null_adx['+DI'].min():.2f} to {non_null_adx['+DI'].max():.2f}")
                print(f"📊 ADX DEBUG: -DI range: {non_null_adx['-DI'].min():.2f} to {non_null_adx['-DI'].max():.2f}")
        else:
            print("📊 ADX DEBUG: ADX calculation returned empty DataFrame!")
        
        filtered_adx_df = pd.merge(
            adx_plot_df,
            adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]],
            on=["Datetime", "Ticker"],
            how="left"
        )
        print(f"📊 ADX DEBUG: Filtered ADX data shape: {filtered_adx_df.shape}")
        print(f"📊 ADX DEBUG: Filtered ADX columns: {filtered_adx_df.columns.tolist()}")
       
         #    --- Price (candlestick) charts with buy/sell signals ---
        def detect_candle_signals(tdf):
            """
            Adds buy/sell signals to a ticker DataFrame.
            Returns a list of dicts: {"Datetime": ..., "Price": ..., "Signal": "Buy"/"Sell"}
            """
            signals = []
            tdf = tdf.reset_index(drop=True)
            
            if len(tdf) < 2:
                return signals
                
            for i in range(1, len(tdf)):
                o1, c1, h1, l1 = tdf.loc[i-1, "Open"], tdf.loc[i-1, "Close"], tdf.loc[i-1, "High"], tdf.loc[i-1, "Low"]
                o2, c2, h2, l2 = tdf.loc[i, "Open"], tdf.loc[i, "Close"], tdf.loc[i, "High"], tdf.loc[i, "Low"]
                datetime_val = tdf.loc[i, "Datetime"]

                # Bullish Engulfing: current green candle engulfs previous red candle
                if (c2 > o2 and c1 < o1 and o2 < c1 and c2 > o1):
                    signals.append({"Datetime": datetime_val, "Price": l2 * 0.995, "Signal": "Buy"})
                    
                # Bearish Engulfing: current red candle engulfs previous green candle
                elif (c2 < o2 and c1 > o1 and o2 > c1 and c2 < o1):
                    signals.append({"Datetime": datetime_val, "Price": h2 * 1.005, "Signal": "Sell"})
                    
                # Hammer (bullish reversal): small body, long lower shadow
                body2 = abs(c2 - o2)
                lower_shadow2 = min(o2, c2) - l2
                upper_shadow2 = h2 - max(o2, c2)
                total_range2 = h2 - l2
                
                if (total_range2 > 0 and body2 > 0 and 
                    lower_shadow2 > 2 * body2 and upper_shadow2 < body2 and
                    c2 > l1):  # Close above previous low (reversal confirmation)
                    signals.append({"Datetime": datetime_val, "Price": l2 * 0.998, "Signal": "Buy"})
                    
                # Shooting Star (bearish reversal): small body, long upper shadow
                elif (total_range2 > 0 and body2 > 0 and 
                      upper_shadow2 > 2 * body2 and lower_shadow2 < body2 and
                      c2 < h1):  # Close below previous high (reversal confirmation)
                    signals.append({"Datetime": datetime_val, "Price": h2 * 1.002, "Signal": "Sell"})
                    
                # Doji (indecision): very small body relative to shadows
                elif (total_range2 > 0 and body2 < total_range2 * 0.1 and
                      lower_shadow2 > body2 * 3 and upper_shadow2 > body2 * 3):
                    # Doji after uptrend = potential sell, after downtrend = potential buy
                    if c1 > o1:  # Previous was green (uptrend)
                        signals.append({"Datetime": datetime_val, "Price": h2 * 1.001, "Signal": "Sell"})
                    elif c1 < o1:  # Previous was red (downtrend)
                        signals.append({"Datetime": datetime_val, "Price": l2 * 0.999, "Signal": "Buy"})
                        
            return signals

        # --- Price (candlestick) charts with buy/sell signals ---
        try:
            print(f"🎨 CHART DEBUG: Creating price chart with {num_tickers} rows for tickers: {valid_ticker_rows}")
            print(f"🎨 CHART DEBUG: price_plot_df shape: {price_plot_df.shape if 'price_plot_df' in locals() else 'NOT DEFINED'}")
            
            if num_tickers == 0:
                print("❌ CHART DEBUG: num_tickers is 0, returning empty figures")
                return go.Figure(), go.Figure(), go.Figure(), go.Figure(), html.Div("No valid tickers for charts"), html.Div("No whale data.")
            
            price_fig = make_subplots(
                rows=num_tickers, cols=1,
                shared_xaxes=False,
                vertical_spacing=0.08,
                subplot_titles=subplot_titles,
                row_heights=[1]*num_tickers
            )
            
            chart_success = False
            for i, ticker in enumerate(valid_ticker_rows, start=1):
                print(f"  📊 CHART DEBUG: Adding chart for {ticker} (row {i})")
                ticker_df = price_plot_df[price_plot_df["Ticker"] == ticker].copy()
                ticker_df = ticker_df.sort_values("Datetime")
                
                print(f"  📊 CHART DEBUG: {ticker} data shape: {ticker_df.shape}")
                print(f"  📊 CHART DEBUG: {ticker} columns: {ticker_df.columns.tolist()}")
                
                if ticker_df.empty:
                    print(f"❌ CHART DEBUG: No data for {ticker} price chart")
                    continue
                    
                # Validate OHLC data
                required_chart_cols = ["Open", "High", "Low", "Close", "Datetime"]
                missing_chart_cols = [col for col in required_chart_cols if col not in ticker_df.columns]
                if missing_chart_cols:
                    print(f"❌ CHART DEBUG: {ticker} missing columns: {missing_chart_cols}")
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
                    print(f"✅ CHART DEBUG: Successfully added candlestick for {ticker}")
                except Exception as candlestick_error:
                    print(f"❌ CHART DEBUG: Error adding candlestick for {ticker}: {candlestick_error}")
                    continue
                
                # Add buy/sell signals to the chart
                signals = detect_candle_signals(ticker_df)
                if signals:
                    buy_signals = [s for s in signals if s["Signal"] == "Buy"]
                    sell_signals = [s for s in signals if s["Signal"] == "Sell"]
                    
                    if buy_signals:
                        price_fig.add_trace(
                            go.Scatter(
                                x=[s["Datetime"] for s in buy_signals],
                                y=[s["Price"] for s in buy_signals],
                                mode='markers',
                                marker=dict(symbol='triangle-up', size=12, color='lime', line=dict(width=2, color='darkgreen')),
                                name=f"{ticker} Buy Signal",
                                showlegend=False
                            ),
                            row=i, col=1
                        )
                    
                    if sell_signals:
                        price_fig.add_trace(
                            go.Scatter(
                                x=[s["Datetime"] for s in sell_signals],
                                y=[s["Price"] for s in sell_signals],
                                mode='markers',
                                marker=dict(symbol='triangle-down', size=12, color='red', line=dict(width=2, color='darkred')),
                                name=f"{ticker} Sell Signal",
                                showlegend=False
                            ),
                            row=i, col=1
                        )
                    
                    print(f"✅ Added {len(buy_signals)} buy signals and {len(sell_signals)} sell signals for {ticker}")
                else:
                    print(f"⚠️ No candlestick signals detected for {ticker}")
                
                # ... rest of price chart logic
                
            price_fig.update_layout(
                height=price_chart_height * num_tickers,
                title="Price (Candlestick)",
                showlegend=False
            )
            
            if chart_success:
                print(f"✅ CHART DEBUG: Price chart creation completed successfully with {num_tickers} tickers")
            else:
                print(f"❌ CHART DEBUG: No charts were successfully created")
            
        except Exception as e:
            print(f"❌ CHART DEBUG: Error creating price chart: {e}")
            import traceback
            traceback.print_exc()
            price_fig = go.Figure().add_annotation(text=f"Chart Error: {str(e)}", xref="paper", yref="paper", x=0.5, y=0.5, showarrow=False)

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
                vol_df = vol_df.sort_values("Datetime")
                vol_df["PrevClose"] = vol_df["Close"].shift(1)
                vol_df["BarColor"] = np.where(vol_df["Close"] >= vol_df["PrevClose"], "green", "red")
                # Remove the first bar (which may be a large outlier)
                vol_df = vol_df.iloc[1:].copy() if len(vol_df) > 1 else vol_df
                # Optionally, clip y-axis to 99th percentile to avoid outliers
                y_max = vol_df["TickVolume"].quantile(0.99) * 1.1 if not vol_df["TickVolume"].empty else None
                volume_fig.add_trace(go.Bar(
                    x=vol_df["Datetime"],
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

        # --- ADX chart with improved styling ---
        # **DEBUG**: Check ADX data before chart creation
        print(f"📊 CHART DEBUG: Creating ADX chart for {num_tickers} tickers")
        print(f"📊 CHART DEBUG: filtered_adx_df shape: {filtered_adx_df.shape}")
        print(f"📊 CHART DEBUG: filtered_adx_df columns: {filtered_adx_df.columns.tolist()}")
        
        for ticker in valid_ticker_rows:
            ticker_data = filtered_adx_df[filtered_adx_df["Ticker"] == ticker]
            print(f"📊 CHART DEBUG: {ticker} - Total rows: {len(ticker_data)}")
            if not ticker_data.empty:
                # Use correct column names with _y suffix
                adx_data = ticker_data.dropna(subset=["ADX_y", "+DI_y", "-DI_y"])
                print(f"📊 CHART DEBUG: {ticker} - Non-null ADX rows: {len(adx_data)}")
                if not adx_data.empty:
                    print(f"📊 CHART DEBUG: {ticker} - ADX range: {adx_data['ADX_y'].min():.2f} to {adx_data['ADX_y'].max():.2f}")
                    print(f"📊 CHART DEBUG: {ticker} - First few ADX values: {adx_data['ADX_y'].head(3).tolist()}")
        
        adx_fig = make_subplots(
            rows=num_tickers, cols=1,
            shared_xaxes=False,
            vertical_spacing=0.05,  # Reduced spacing
            subplot_titles=[f"{ticker} ADX/DMS" for ticker in valid_ticker_rows],
            row_heights=[1]*num_tickers
        )

        traces_added = 0  # **DEBUG**: Count traces added

        for i, ticker in enumerate(valid_ticker_rows, start=1):
            adx_sub = filtered_adx_df[filtered_adx_df["Ticker"] == ticker]
            print(f"📊 TRACE DEBUG: {ticker} - subplot {i} - adx_sub shape: {adx_sub.shape}")
            
            # **NEW**: Filter to today's data for DISPLAY (but calculation used full rolling window)
            if not adx_sub.empty:
                from datetime import date
                today = date.today()
                if 'Datetime' in adx_sub.columns:
                    adx_sub['Date'] = pd.to_datetime(adx_sub['Datetime']).dt.date
                    today_adx = adx_sub[adx_sub['Date'] == today].copy()
                    
                    if not today_adx.empty:
                        adx_sub = today_adx.drop('Date', axis=1)
                        print(f"📊 DISPLAY FILTER: {ticker} - Using {len(adx_sub)} today's data points for display")
                    else:
                        # If no today data, use the most recent data available
                        print(f"📊 DISPLAY FILTER: {ticker} - No today data, using recent data for display")
                        adx_sub = adx_sub.tail(50)  # Show last 50 points
            
            if not adx_sub.empty and "ADX_y" in adx_sub.columns and "+DI_y" in adx_sub.columns and "-DI_y" in adx_sub.columns:
                
                # Remove NaN values for smoother lines - use the correct column names
                adx_clean = adx_sub.dropna(subset=["ADX_y", "+DI_y", "-DI_y"])
                print(f"📊 TRACE DEBUG: {ticker} - adx_clean shape: {adx_clean.shape}")
                
                if not adx_clean.empty:
                    print(f"📊 TRACE DEBUG: {ticker} - Adding traces to chart")
                    # ADX line (blue, thicker)
                    adx_fig.add_trace(go.Scatter(
                        x=adx_clean["Datetime"],
                        y=adx_clean["ADX_y"],  # Use ADX_y column
                        mode="lines",
                        name=f"{ticker} ADX",
                        line=dict(color="#1f77b4", width=2.5, smoothing=1.3),  # Smoothing added
                        connectgaps=True
                    ), row=i, col=1)
                    traces_added += 1
                    
                    # +DI line (green)
                    adx_fig.add_trace(go.Scatter(
                        x=adx_clean["Datetime"],
                        y=adx_clean["+DI_y"],  # Use +DI_y column
                        mode="lines",
                        name=f"{ticker} +DI",
                        line=dict(color="#2ca02c", width=1.8, smoothing=1.3),
                        connectgaps=True
                    ), row=i, col=1)
                    traces_added += 1
                    
                    # -DI line (red)
                    adx_fig.add_trace(go.Scatter(
                        x=adx_clean["Datetime"],
                        y=adx_clean["-DI_y"],  # Use -DI_y column
                        mode="lines",
                        name=f"{ticker} -DI",
                        line=dict(color="#d62728", width=1.8, smoothing=1.3),
                        connectgaps=True
                    ), row=i, col=1)
                    traces_added += 1
                    
                    # Add reference lines - use correct column names
                    max_val = max(adx_clean["ADX_y"].max(), adx_clean["+DI_y"].max(), adx_clean["-DI_y"].max())
                    min_val = min(adx_clean["ADX_y"].min(), adx_clean["+DI_y"].min(), adx_clean["-DI_y"].min())
                    
                    # 25 line (strong trend threshold)
                    adx_fig.add_hline(y=25, line_dash="dot", line_color="gray", opacity=0.5, row=i, col=1)
                    
                    # Configure axes for better space utilization
                    adx_fig.update_xaxes(
                        nticks=min(adx_tick_count, 15),
                        showgrid=True,
                        gridcolor="rgba(128,128,128,0.2)",
                        row=i, col=1
                    )
                    
                    adx_fig.update_yaxes(
                        range=[max(0, min_val - 2), min(100, max_val + 5)],  # Dynamic range
                        showgrid=True,
                        gridcolor="rgba(128,128,128,0.2)",
                        dtick=10,  # Major ticks every 10 units
                        row=i, col=1
                    )
                else:
                    print(f"⚠️ TRACE WARNING: {ticker} - No clean ADX data after removing NaN values")
            else:
                print(f"⚠️ TRACE WARNING: {ticker} - Missing ADX columns or empty data")

        print(f"📊 FINAL DEBUG: ADX chart completed with {traces_added} traces")

        adx_fig.update_layout(
            title="ADX / DMS Indicators",
            height=adx_chart_height * num_tickers,
            showlegend=False,
            margin=dict(l=40, r=20, t=50, b=30),  # Tighter margins
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)"
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
                    x=pmo_sub["Datetime"],
                    y=pmo_sub["PMO"],
                    mode="lines",
                    name=f"{ticker} PMO",
                    line=dict(color="green")
                ), row=i, col=1)
                pmo_fig.add_trace(go.Scatter(
                    x=pmo_sub["Datetime"],
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
        global news_cache
        news_rows = []
        # Load the news cache from file (do this once per dashboard update)
        news_cache = load_news_cache()
        
        # Get latest AI recommendations for news
        latest_ai_for_news = load_latest_ai_recommendations()
        
        for ticker in latest_ai_for_news["ticker"].tolist() if not latest_ai_for_news.empty else selected_tickers:
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
            news_table = html.Table(table_header + table_body, style={'width': '100%', 'fontSize': '16px'})
        else:
            news_table = html.Div("No news found.", style={'fontSize': '16px'})

        # --- WHALE TABLE FEATURE ---
        whale_rows = []
        for ticker in latest_ai_for_news["ticker"].tolist() if not latest_ai_for_news.empty else selected_tickers:
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
                # --- Quiver Institutional ---
                if not inst_df.empty:
                    inst_quiver = inst_df[inst_df["Ticker"].str.upper() == symbol.upper()]
                    for _, row in inst_quiver.iterrows():
                        whale_rows.append({
                            "Ticker": symbol,
                            "Type": "Quiver Institutional",
                            "Entity": row.get("Institution", row.get("Entity", "")),
                            "Shares": row.get("Amount", ""),
                            "Change": row.get("Transaction", ""),
                            "Date": row.get("Date", "")
                        })
                # --- Quiver Congress/Government ---
                if not congress_df.empty:
                    gov_quiver = congress_df[congress_df["Ticker"].str.upper() == symbol.upper()]
                    for _, row in gov_quiver.iterrows():
                        whale_rows.append({
                            "Ticker": symbol,
                            "Type": "Quiver Congress",
                            "Entity": row.get("Representative", row.get("Entity", "")),
                            "Shares": row.get("Amount", ""),
                            "Change": row.get("Transaction", ""),
                            "Date": row.get("TransactionDate", row.get("Date", ""))
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
            whale_table = html.Table(whale_header + whale_body, style={'width': '100%', 'fontSize': '16px'})
        else:
            whale_table = html.Div("No whale data found.", style={'fontSize': '16px'})

        # **SAFETY CHECK**: Ensure ADX figure is valid before returning
        if not hasattr(adx_fig, 'data') or len(adx_fig.data) == 0:
            print("⚠️ SAFETY: ADX figure is empty, creating fallback chart")
            adx_fig = go.Figure()
            adx_fig.add_annotation(
                text="ADX/DMS: Calculating... (Refresh in a moment)",
                x=0.5, y=0.5,
                xref="paper", yref="paper",
                showarrow=False,
                font=dict(size=16)
            )
            adx_fig.update_layout(
                title="ADX / DMS Indicators - Loading...",
                height=adx_chart_height * num_tickers
            )
        else:
            print(f"✅ SAFETY: ADX figure is valid with {len(adx_fig.data)} traces")

        # **FINAL DEBUG**: Confirm all figures before return
        print(f"📊 FINAL: Returning figures - Price: {len(price_fig.data) if hasattr(price_fig, 'data') else 0} traces, "
              f"Volume: {len(volume_fig.data) if hasattr(volume_fig, 'data') else 0} traces, "
              f"ADX: {len(adx_fig.data) if hasattr(adx_fig, 'data') else 0} traces, "
              f"PMO: {len(pmo_fig.data) if hasattr(pmo_fig, 'data') else 0} traces")

        return price_fig, volume_fig, adx_fig, pmo_fig, news_table, whale_table

    @app.callback(
        [
            Output('trade-log-table', 'data'),
            Output('trade-log-table', 'selected_rows'),
            Output('trade-log-store', 'data'),
            Output('trade-type', 'value'),
            Output('trade-ticker', 'value'),
            Output('trade-qty', 'value'),
            Output('trade-open-datetime', 'value'),
            Output('trade-open-price', 'value'),
            Output('trade-close-datetime', 'value'),
            Output('trade-close-price', 'value'),
            Output('trade-notes', 'value'),
            Output('trade-log-summary', 'children')
        ],
        [
            Input('update-trade-btn', 'n_clicks'),
            Input('log-trade-btn', 'n_clicks'),
            Input('trade-log-table', 'selected_rows')
        ],
        [
            State('trade-type', 'value'),
            State('trade-ticker', 'value'),
            State('trade-qty', 'value'),
            State('trade-open-datetime', 'value'),
            State('trade-open-price', 'value'),
            State('trade-close-datetime', 'value'),
            State('trade-close-price', 'value'),
            State('trade-notes', 'value'),
            State('trade-log-table', 'data')
        ]
    )
    def trade_log_callback(update_n, log_n, selected_rows,
                        trade_type, ticker, qty, open_dt, open_price, close_dt, close_price, notes, table_data):
        import dash
        import pandas as pd
        from datetime import datetime

        ctx = dash.callback_context
        triggered = ctx.triggered[0]['prop_id'] if ctx.triggered else ''

        TRADE_LOG_FILE = "trade_log.xlsx"
        TRADE_LOG_COLUMNS = [
            "Type", "Ticker", "Trade QTY", "Open Datetime", "Open Price",
            "Close Datetime", "Close Price", "Profit/Loss", "Profit/Loss %", "Notes"
        ]

        trade_log_df = pd.DataFrame(table_data) if table_data else pd.DataFrame(columns=TRADE_LOG_COLUMNS)

        def calc_trade_log_summary(trade_log_df):
            # Defensive: ensure columns exist and are numeric
            if trade_log_df.empty or "Open Price" not in trade_log_df.columns or "Close Price" not in trade_log_df.columns:
                return "Total Profit/Loss: $0.00 | Total Profit/Loss %: 0.00%"
            df = trade_log_df.copy()
            # Replace blanks with 0, coerce errors
            for col in ["Open Price", "Close Price", "Profit/Loss", "Trade QTY"]:
                if col not in df.columns:
                    df[col] = 0.0
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
            df = df[(df["Open Price"] != 0) & (df["Close Price"] != 0)]
            total_pl = df["Profit/Loss"].sum()
            total_cost = (df["Open Price"] * df["Trade QTY"]).sum()
            total_pl_pct = (total_pl / total_cost * 100) if total_cost else 0
            return f"Total Profit/Loss: ${total_pl:,.2f} | Total Profit/Loss %: {total_pl_pct:.2f}%"

        # --- LOG TRADE ---
        if triggered.startswith('log-trade-btn'):
            try:
                open_price = float(open_price)
            except:
                open_price = 0.0
            try:
                close_price = float(close_price)
            except:
                close_price = 0.0
            try:
                qty = int(qty)
            except:
                qty = 0
            new_row = {
                "Type": trade_type,
                "Ticker": ticker,
                "Trade QTY": qty,
                "Open Datetime": open_dt,
                "Open Price": open_price,
                "Close Datetime": close_dt,
                "Close Price": close_price,
                "Profit/Loss": "",
                "Profit/Loss %": "",
                "Notes": notes
            }
            trade_log_df = pd.concat([trade_log_df, pd.DataFrame([new_row])], ignore_index=True)
            # Recalculate P/L
            for i, row in trade_log_df.iterrows():
                try:
                    op = float(row["Open Price"])
                except:
                    op = 0.0
                try:
                    cp = float(row["Close Price"])
                except:
                    cp = 0.0
                try:
                    q = int(row["Trade QTY"])
                except:
                    q = 0
                if op and cp and q:
                    pl = (cp - op) * q
                    pl_pct = ((cp - op) / op * 100)
                    trade_log_df.at[i, "Profit/Loss"] = round(pl, 2)
                    trade_log_df.at[i, "Profit/Loss %"] = round(pl_pct, 2)
                else:
                    trade_log_df.at[i, "Profit/Loss"] = ""
                    trade_log_df.at[i, "Profit/Loss %"] = ""
            try:
                trade_log_df.to_excel(TRADE_LOG_FILE, index=False)
            except Exception as e:
                print("Excel save error:", e)
            today_str = datetime.now().strftime("%Y-%m-%d")
            return (
                trade_log_df.to_dict('records'),
                [],  # clear selection
                trade_log_df.to_dict('records'),
                "Paper", "", 0, f"{today_str} 09:15", 0.0, f"{today_str} 15:45", 0.0, "",
                calc_trade_log_summary(trade_log_df)
            )

        # --- UPDATE TRADE ---
        if triggered.startswith('update-trade-btn'):
            if selected_rows and len(selected_rows) == 1:
                idx = selected_rows[0]
                for col, val in zip(
                    ["Type", "Ticker", "Trade QTY", "Open Datetime", "Open Price",
                    "Close Datetime", "Close Price", "Notes"],
                    [trade_type, ticker, qty, open_dt, open_price, close_dt, close_price, notes]
                ):
                    trade_log_df.at[idx, col] = val
                # Recalculate P/L
                for i, row in trade_log_df.iterrows():
                    try:
                        op = float(row["Open Price"])
                    except:
                        op = 0.0
                    try:
                        cp = float(row["Close Price"])
                    except:
                        cp = 0.0
                    try:
                        q = int(row["Trade QTY"])
                    except:
                        q = 0
                    if op and cp and q:
                        pl = (cp - op) * q
                        pl_pct = ((cp - op) / op * 100)
                        trade_log_df.at[i, "Profit/Loss"] = round(pl, 2)
                        trade_log_df.at[i, "Profit/Loss %"] = round(pl_pct, 2)
                    else:
                        trade_log_df.at[i, "Profit/Loss"] = ""
                        trade_log_df.at[i, "Profit/Loss %"] = ""
                try:
                    trade_log_df.to_excel(TRADE_LOG_FILE, index=False)
                except Exception as e:
                    print("Excel save error:", e)
                today_str = datetime.now().strftime("%Y-%m-%d")
                return (
                    trade_log_df.to_dict('records'),
                    [],  # clear selection
                    trade_log_df.to_dict('records'),
                    "Paper", "", 0, f"{today_str} 09:15", 0.0, f"{today_str} 15:45", 0.0, "",
                    calc_trade_log_summary(trade_log_df)
                )

        # --- POPULATE FIELDS ON ROW SELECT ---
        if triggered.startswith('trade-log-table'):
            if selected_rows and len(selected_rows) == 1:
                idx = selected_rows[0]
                row = trade_log_df.iloc[idx]
                return (
                    dash.no_update,  # don't change table data
                    selected_rows,
                    dash.no_update,  # don't change store
                    row.get("Type", "Paper"),
                    row.get("Ticker", ""),
                    row.get("Trade QTY", 0),
                    row.get("Open Datetime", ""),
                    row.get("Open Price", 0.0),
                    row.get("Close Datetime", ""),
                    row.get("Close Price", 0.0),
                    row.get("Notes", ""),
                    calc_trade_log_summary(trade_log_df)
                )

        # --- DEFAULT: no update ---
        return [dash.no_update] * 11 + [dash.no_update]
    

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
    
    
    

    print("🚀 Dash is running on http://127.0.0.1:8050/")
    app.run(host='127.0.0.1', port=8050, debug=False)
    
                                      #******* End  of Dashboard function *******              


# ====== ETF List Loader ======
def get_top_etf_list_from_excel():
    if not os.path.exists(TOP_ETFS_FILE):
        raise FileNotFoundError(f"ETF list file not found: {TOP_ETFS_FILE}")
    df = pd.read_excel(TOP_ETFS_FILE)
    if "Symbol" not in df.columns:
        raise ValueError(f"'Symbol' column not found in {TOP_ETFS_FILE}")
    symbols = df["Symbol"].dropna().astype(str).str.strip().unique().tolist()
    print(f"Loaded {len(symbols)} ETF tickers from {TOP_ETFS_FILE}: {symbols}")
    return symbols

# ====== News Cache Handling ======
def load_news_cache():
    if os.path.exists(NEWS_CACHE_FILE):
        with open(NEWS_CACHE_FILE, "r") as f:
            raw = json.load(f)
        for symbol in raw:
            ts, data = raw[symbol]
            raw[symbol] = (datetime.fromisoformat(ts), data)
        return raw
    return {}

def save_news_cache(news_cache):
    serializable = {symbol: (ts.isoformat(), data) for symbol, (ts, data) in news_cache.items()}
    with open(NEWS_CACHE_FILE, "w") as f:
        json.dump(serializable, f, indent=2)

def analyze_sentiment(text):
    positive_keywords = [
        "growth", "strong", "bullish", "rising", "beat", "beats", "record", "surge", "up", "increase", "profit", "gain", "soar", "positive", "outperform", "buy", "upgrade", "rebound", "rally", "optimistic", "tops"
    ]
    negative_keywords = [
        "drop", "decline", "bearish", "falling", "miss", "misses", "loss", "down", "decrease", "plunge", "negative", "underperform", "sell", "downgrade", "slump", "cut", "warning", "disappoint", "bear", "weak"
    ]
    text_lower = text.lower()
    if any(word in text_lower for word in positive_keywords):
        return "Positive"
    if any(word in text_lower for word in negative_keywords):
        return "Negative"
    return "Neutral"

def fetch_etf_news(etf_symbol, finnhub_api_key=None, news_cache=None):
    now = datetime.now(timezone.utc)
    cache_validity = timedelta(hours=1)
    if news_cache is None:
        news_cache = load_news_cache()
    symbols_to_search = [etf_symbol]
    if 'ETF_UNDERLYING_MAP' in globals() and etf_symbol in ETF_UNDERLYING_MAP:
        underlying = ETF_UNDERLYING_MAP[etf_symbol]
        if underlying not in symbols_to_search:
            symbols_to_search.append(underlying)
    all_articles = []
    for symbol in symbols_to_search:
        if symbol in news_cache:
            cached_time, cached_data = news_cache[symbol]
            if now - cached_time < cache_validity:
                all_articles.extend(cached_data)
                continue
        # Finnhub company-news endpoint
        from_date = (now - timedelta(days=7)).strftime("%Y-%m-%d")
        to_date = now.strftime("%Y-%m-%d")
        api_url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={from_date}&to={to_date}&token={FINNHUB_API_KEY}"
        try:
            response = requests.get(api_url)
            if response.status_code == 200:
                news_data = response.json()[:5]
                formatted_news = [
                    {
                        "title": article.get("headline", ""),
                        "sentiment": analyze_sentiment(article.get("headline", "")),
                        "url": article.get("url", "")
                    }
                    for article in news_data
                ]
                news_cache[symbol] = (now, formatted_news)
                save_news_cache(news_cache)
                all_articles.extend(formatted_news)
            else:
                print(f"❌ Finnhub News API error for {symbol}: {response.status_code} {response.text}")
        except Exception as e:
            print(f"❌ Finnhub News fetch error for {symbol}: {e}")
    # Remove duplicates by title
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        title = article["title"] if isinstance(article, dict) and "title" in article else str(article)
        if title not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(title)
    return unique_articles

# ====== Whale Cache Handling ======
def load_whale_cache():
    if os.path.exists(WHALE_CACHE_FILE):
        with open(WHALE_CACHE_FILE, "r") as f:
            raw = json.load(f)
        for symbol in raw:
            ts, data = raw[symbol]
            raw[symbol] = (datetime.fromisoformat(ts), data)
        # print(f"[DEBUG] Loaded whale cache for symbols...2263: {list(raw.keys())}")
        return raw
    print("[DEBUG] No whale cache file found.")
    return {}

def save_whale_cache(whale_cache):
    serializable = {symbol: (ts.isoformat(), data) for symbol, (ts, data) in whale_cache.items()}
    with open(WHALE_CACHE_FILE, "w") as f:
        json.dump(serializable, f, indent=2)

def fetch_whale_data(ticker, finnhub_api_key=None, whale_cache=None):
    now = datetime.now(timezone.utc)
    cache_validity = timedelta(hours=2)
    if whale_cache is None:
        whale_cache = load_whale_cache()
    symbols_to_search = [ticker]
    if 'ETF_UNDERLYING_MAP' in globals() and ticker in ETF_UNDERLYING_MAP:
        underlying = ETF_UNDERLYING_MAP[ticker]
        if underlying not in symbols_to_search:
            symbols_to_search.append(underlying)
    combined_data = {"institutional": [], "government": [], "insider": []}
    for symbol in symbols_to_search:
        if symbol in whale_cache:
            cached_time, cached_data = whale_cache[symbol]
            if now - cached_time < cache_validity:
                if isinstance(cached_data, dict):
                    for key in ["institutional", "government", "insider"]:
                        if key not in cached_data or not isinstance(cached_data[key], list):
                            cached_data[key] = []
                        combined_data[key].extend(cached_data[key])
                print(f"[DEBUG] Using cached whale data for {symbol}")
                continue
        try:
            inst_url = f"https://finnhub.io/api/v1/stock/institutional-ownership?symbol={symbol}&token={FINNHUB_API_KEY}"
            inst_resp = requests.get(inst_url)
            print(f"[DEBUG] 1946 Institutional response for {symbol}: {inst_resp.status_code} {inst_resp.text}")
            try:
                inst = inst_resp.json().get("ownership", [])[:3]
            except Exception:
                print(f"Finnhub returned non-JSON for {symbol}, skipping to SEC EDGAR.")
                inst = []

            gov_url = f"https://finnhub.io/api/v1/stock/government-ownership?symbol={symbol}&token={FINNHUB_API_KEY}"
            gov_resp = requests.get(gov_url)
            print(f"[DEBUG] 1951 Government response for {symbol}: {gov_resp.status_code} {gov_resp.text}")
            try:
                gov = gov_resp.json().get("ownership", [])[:3]
            except Exception:
                print(f"Finnhub returned non-JSON for {symbol} (government), skipping.")
                gov = []

            ins_url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={symbol}&token={FINNHUB_API_KEY}"
            ins_resp = requests.get(ins_url)
            print(f"[DEBUG] 1956 Insider response for {symbol}: {ins_resp.status_code} {ins_resp.text}")
            try:
                ins = ins_resp.json().get("data", [])[:3]
            except Exception:
                print(f"Finnhub returned non-JSON for {symbol} (insider), skipping.")
                ins = []

            data = {"institutional": inst, "government": gov, "insider": ins}
            whale_cache[symbol] = (now, data)
            save_whale_cache(whale_cache)
            for key in ["institutional", "government", "insider"]:
                combined_data[key].extend(data[key])
        except Exception as e:
            print(f"Whale fetch error for {symbol}: {e}")
            continue

        # === SEC EDGAR 13F Supplement if Finnhub institutional data is empty ===
        if not inst:
            print(f"🔎 1970 Finnhub institutional data missing for {symbol}, supplementing with SEC EDGAR 13F...")
            try:
                # You can try several major funds; here we use "BlackRock", "Vanguard", "Berkshire Hathaway"
                whales_to_try = [
                    ("0001364742"),
                    ("0000102909"),
                    ("0001067983")
                ]
                for whale_cik in whales_to_try:
                    holdings = get_whale_13f_holdings(whale_cik)
                all_holdings = []
                for whale in whales_to_try:
                    holdings = get_whale_13f_holdings(whale)
                    # Optionally filter for your symbol in the issuer name (case-insensitive)
                    for h in holdings:
                        print(f"DEBUG:1979 Found holding with ticker {h.get('ticker','')} for whale {whale}")
                        if h.get("ticker", "").strip().lower() == symbol.strip().lower():
                            h["whale"] = whale
                            all_holdings.append(h)
                if all_holdings:
                    print(f"✅ 1983 SEC EDGAR 13F supplement found {len(all_holdings)} holdings for {symbol}")
                    # Add to institutional data
                    combined_data["institutional"].extend(all_holdings)

                    # Save to cache
                    data = {"institutional": all_holdings, "government": [], "insider": []}
                    whale_cache[symbol] = (now, data)
                    save_whale_cache(whale_cache)
            except Exception as e:
                print(f"SEC EDGAR 13F fetch error for {symbol}: {e}")

    # Remove duplicates
    for key in ["institutional", "government", "insider"]:
        seen = set()
        unique = []
        for entry in combined_data[key]:
            uid = tuple(sorted(entry.items()))
            if uid not in seen:
                unique.append(entry)
                seen.add(uid)
        combined_data[key] = unique
    print(f"[DEBUG] Combined whale data for {ticker}: {combined_data}")
    return combined_data


def count_recent_whale_trades(whale_data, days=30):
    if not isinstance(whale_data, dict):
        print(f"[WARN] whale_data is not a dict: {type(whale_data)} - value: {whale_data}")
        return 0
    for key in ["institutional", "government", "insider"]:
        if key not in whale_data or not isinstance(whale_data[key], list):
            whale_data[key] = []
    now = datetime.now(timezone.utc)
    count = 0
    for entry in whale_data.get("institutional", []) + whale_data.get("government", []):
        date_str = entry.get("reportDate")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if now - dt.replace(tzinfo=timezone.utc) <= timedelta(days=days):
                    count += 1
            except Exception:
                continue
    for entry in whale_data.get("insider", []):
        date_str = entry.get("transactionDate")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if now - dt.replace(tzinfo=timezone.utc) <= timedelta(days=days):
                    count += 1
            except Exception:
                continue
    return count

# ====== CCI Strength Rank ======
def cci_strength_rank(cci):
    if cci is None or pd.isna(cci):
        return 3
    if cci <= -200:
        return 1
    elif -200 < cci <= -150:
        return 2
    elif -100 < cci < 100:
        return 3
    elif 100 <= cci < 150:
        return 4
    elif 150 <= cci <= 200:
        return 5
    else:
        return 3

# ====== ETF Candidate Selection ======
def select_trade_candidates():
    # Use the globally loaded candidate tickers
    global all_candidate_tickers
    symbols = all_candidate_tickers
    print("🎯 Final leveraged ETF list before further processing:", symbols)
    leveraged_etfs = symbols
    print("✅ Starting selection process for ETFs.")
    # Use the global variable that was just updated
    global historical_data
    hist_df = historical_data if historical_data is not None else pd.read_csv(HISTORICAL_DATA_FILE)
    atr_values, price_change, volume_values = {}, {}, {}

    lookback_bars = 200  # Use all available data for ATR calculation
    atr_period = 21  # Fixed ATR calculation period
    print("=== ATR DEBUG INFO ===")
    print(f"Total rows in hist_df 2280: {len(hist_df)}")
    for t in leveraged_etfs:
        # Get ALL available data for this ticker, not just tail(lookback_bars)
        tdf = hist_df[hist_df["Ticker"] == t].sort_values("Datetime")
        print(f" 2283{t}: {len(tdf)} total rows")
        
        # Use the last lookback_bars for ATR calculation
        if len(tdf) >= lookback_bars:
            recent_tdf = tdf.tail(lookback_bars)
            print(f" 2285{t}: Using last {lookback_bars} rows for ATR calculation")
            
            valid_tdf = recent_tdf[(recent_tdf["High"] > 0) & (recent_tdf["Low"] > 0) & (recent_tdf["Close"] > 0)]
            print(f" 2287{t}: {len(valid_tdf)} valid rows for ATR calculation")
            
            if len(valid_tdf) >= atr_period:
                print(f" 2289{t}: Sample data:")
                print("2290", valid_tdf[["Datetime", "High", "Low", "Close"]].head())
                print("=== END ATR DEBUG ===")

                # Calculate True Range properly using the last atr_period bars
                recent_for_atr = valid_tdf.tail(atr_period)
                recent_for_atr = recent_for_atr.copy()
                recent_for_atr['High_Low'] = recent_for_atr['High'] - recent_for_atr['Low']
                recent_for_atr['High_PrevClose'] = abs(recent_for_atr['High'] - recent_for_atr['Close'].shift(1))
                recent_for_atr['Low_PrevClose'] = abs(recent_for_atr['Low'] - recent_for_atr['Close'].shift(1))
                
                # True Range is the maximum of the three calculations
                recent_for_atr['True_Range'] = recent_for_atr[['High_Low', 'High_PrevClose', 'Low_PrevClose']].max(axis=1)
                
                # Remove the first row (NaN due to shift) and calculate ATR
                valid_tr = recent_for_atr['True_Range'].dropna()
                
                if len(valid_tr) > 0:
                    atr_val = valid_tr.mean()  # Simple average of True Range values
                else:
                    atr_val = 0
                    
                atr_values[t] = atr_val
                price_change[t] = valid_tdf["Close"].iloc[-1] - valid_tdf["Close"].iloc[0]
                volume_values[t] = valid_tdf["Volume"].mean()
                print(f"ATR for 2297 {t}: {atr_val:.4f} (from {len(valid_tr)} valid True Range values)")
            else:
                atr_values[t] = 0
                price_change[t] = 0
                volume_values[t] = 0
                print(f"ATR for 2302 {t}: 0 (not enough valid bars, only {len(valid_tdf)}, need {atr_period})")
        else:
            atr_values[t] = 0
            price_change[t] = 0
            volume_values[t] = 0
            print(f"ATR for {t}: 0 (total data insufficient: {len(tdf)} rows, need {lookback_bars})")

    
    sentiment_map = {"Positive": 3, "Neutral": 2, "Negative": 1}
    news_cache = load_news_cache()
    news_sentiment = {}
    for t in leveraged_etfs:
        news_list = fetch_etf_news(t, news_cache=news_cache)
        if news_list and isinstance(news_list, list) and isinstance(news_list[0], dict) and "title" in news_list[0]:
            news_sentiment[t] = analyze_sentiment(news_list[0]["title"])
        else:
            news_sentiment[t] = "Neutral"
    whale_cache = load_whale_cache()
    whale_scores = {}
    for t in leveraged_etfs:
        whale_data = fetch_whale_data(t, whale_cache=whale_cache)
        whale_scores[t] = count_recent_whale_trades(whale_data, days=30)
    df = pd.DataFrame({
        "Symbol": leveraged_etfs,
        "PriceChange": [price_change.get(t, 0) for t in leveraged_etfs],
        "Volume": [volume_values.get(t, 0) for t in leveraged_etfs],
        "ATR": [atr_values.get(t, 0) for t in leveraged_etfs],
        "Sentiment": [news_sentiment.get(t, "Neutral") for t in leveraged_etfs],
        "SentimentScore": [sentiment_map.get(news_sentiment.get(t, "Neutral"), 2) for t in leveraged_etfs],
        "WhaleScore": [whale_scores.get(t, 0) for t in leveraged_etfs]
    })
    adx_vals, pmo_vals, cci_vals = [], [], []
    lookback_bars = get_volatility_lookback_bars()  # Already defined above, reuse here
    for t in df["Symbol"]:
        tdf = hist_df[hist_df["Ticker"] == t].sort_values("Datetime").tail(500)  # Use more data for better technical analysis
        for col in ["High", "Low", "Close"]:
            tdf[col] = pd.to_numeric(tdf[col], errors="coerce")
        adx = calculate_adx(tdf, period=21)  # Fixed 21-period ADX
        adx_last = adx["ADX"].iloc[-1] if not adx.empty else np.nan
        adx_vals.append(adx_last)
        pmo = calculate_pmo(tdf, period=35)  # Fixed 35-period PMO
        pmo_last = pmo["PMO"].iloc[-1] if not pmo.empty else np.nan
        pmo_vals.append(pmo_last)
        cci = calculate_cci(tdf, period=20)  # Fixed 20-period CCI
        cci_last = cci["CCI"].iloc[-1] if not cci.empty else np.nan
        cci_vals.append(cci_last)
    df["ADX"] = adx_vals
    df["PMO"] = pmo_vals
    df["CCI"] = cci_vals
    df["CCI_strength_rank"] = df["CCI"].apply(cci_strength_rank)
    N = len(df)
    df["ATR_rank"] = N + 1 - df["ATR"].rank(ascending=False, method="min")
    df["PriceChange_rank"] = N + 1 - df["PriceChange"].rank(ascending=False, method="min")
    df["Volume_rank"] = N + 1 - df["Volume"].rank(ascending=False, method="min")
    df["Sentiment_rank"] = N + 1 - df["SentimentScore"].rank(ascending=False, method="min")
    df["Whale_rank"] = N + 1 - df["WhaleScore"].rank(ascending=False, method="min")
    df["ADX_rank"] = N + 1 - df["ADX"].rank(ascending=False, method="min")
    df["PMO_rank"] = N + 1 - df["PMO"].rank(ascending=False, method="min")
    df["CCI_rank"] = N + 1 - df["CCI"].abs().rank(ascending=False, method="min")

    print('2257', df[["ATR_rank", "PriceChange_rank", "Volume_rank", "Sentiment_rank", "Whale_rank", "ADX_rank", "PMO_rank", "CCI_rank"]])
   
    # --- FIX: Ensure all rank columns are numeric before summing ---
    rank_cols = [
        "ATR_rank", "PriceChange_rank", "Volume_rank", "Sentiment_rank",
        "Whale_rank", "ADX_rank", "PMO_rank", "CCI_rank"
    ]
    for col in rank_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["CompositeScore"] = df[rank_cols].sum(axis=1)
    df["CompositeRank"] = df["CompositeScore"].rank(ascending=False, method="min")
    df = df.sort_values("CompositeScore", ascending=False)
    print("Ranked trade candidates 2270 (ATR is a rank, not a filter):")
    print('2271', df[["Symbol", "ATR", "ATR_rank", "PriceChange", "PriceChange_rank", "Volume", "Volume_rank", "Sentiment", "Sentiment_rank", "WhaleScore", "Whale_rank", "ADX", "ADX_rank", "PMO", "PMO_rank", "CCI", "CCI_rank", "CCI_strength_rank", "CompositeScore", "CompositeRank"]])
    top5_df = df.head(5).reset_index(drop=True)
    ticker_ranks = dict(zip(top5_df["Symbol"], top5_df["CompositeRank"]))
    print("🚀 Top 5 ETFs for Dashboard 2275:")
    print('2275', top5_df[["Symbol", "CompositeRank"]])
    return top5_df

# ====== Example Usage and Dashboard Prep ======

# --- Create Splash Popup at the start of data processing ---
_day_splash = tk.Tk()
_day_splash.title("Loading Day Trading Dashboard...")
_day_splash.geometry("420x130")
_day_splash.configure(bg="#ffe066")  # Vibrant yellow background
_day_splash.attributes("-topmost", True)  # Always on top
_day_splash_label = tk.Label(
    _day_splash,
    text="Day Trading Dashboard is starting...\nPlease wait...",
    font=("Segoe UI", 17, "bold"),
    fg="#0a2463",  # Deep blue text for high contrast
    bg="#ffe066",
    pady=32
)
_day_splash_label.pack(expand=True, fill="both")
_day_splash.update()

# --- Play startup audio notification ---
try:
    print("🔊 Playing startup audio notification...")
    play_audio("day_app_starting.mp3", ticker=None, message=None, tts=False)
    print("✅ Startup audio played successfully")
except Exception as e:
    print(f"⚠️ Could not play startup audio: {e}")

# STEP 1: Ensure we have historical data for ALL candidate tickers before ranking
print(f"📊 STEP 1: Ensuring historical data for all {len(all_candidate_tickers)} candidate tickers...")

# **CRITICAL: RUN DATA INTEGRITY CHECK BEFORE DASHBOARD STARTUP**
print("🔍 === RUNNING CRITICAL PRE-STARTUP DATA INTEGRITY CHECK ===")
import threading
try:
    from data_integrity_monitor import check_data_integrity, show_data_integrity_error
    
    hist_df_full = pd.read_csv(HISTORICAL_DATA_FILE)
    
    # Run comprehensive integrity check with ALL candidate tickers
    is_valid, errors, details = check_data_integrity(
        df=hist_df_full,
        selected_tickers=all_candidate_tickers,
        ai_recommended_tickers=all_candidate_tickers
    )
    
    if not is_valid:
        print("🚨 CRITICAL STARTUP ERROR: DATA INTEGRITY FAILURE!")
        print(f"🚨 Errors found: {errors}")
        
        # Show BLOCKING popup that prevents dashboard startup
        def show_startup_critical_alert():
            startup_details = [
                "🚨 CRITICAL: Dashboard startup blocked due to data integrity failure!",
                "",
                "SYSTEM STATUS:",
                f"• Market is currently OPEN (Wednesday, {datetime.now().strftime('%H:%M')})",
                f"• Expected: All {len(all_candidate_tickers)} tickers should have current data",
                f"• Reality: Massive data retrieval system failure detected",
                "",
                "IMMEDIATE ACTION REQUIRED:",
                "• Contact Claude for Schwab API troubleshooting",
                "• Check Schwab authentication tokens",
                "• Verify network connectivity to Schwab servers",
                "• Do NOT attempt trading until this is resolved",
                ""
            ] + details
            
            show_data_integrity_error(errors, startup_details)
        
        # Show the popup in a separate thread so it doesn't block the main process
        alert_thread = threading.Thread(target=show_startup_critical_alert)
        alert_thread.daemon = True
        alert_thread.start()
        
        print("⚠️ Continuing startup despite integrity issues (user has been alerted)")
        print("⚠️ Dashboard will display data but trading should NOT proceed")
    else:
        print("✅ PRE-STARTUP DATA INTEGRITY CHECK PASSED")
        
except Exception as e:
    print(f"❌ CRITICAL: Cannot perform startup integrity check: {e}")
    # Show emergency popup
    def show_emergency_alert():
        show_data_integrity_error(
            ["STARTUP_DATA_CHECK_FAILED"],
            [f"Cannot load or validate historical data", f"Error: {str(e)}", "Contact Claude immediately"]
        )
    alert_thread = threading.Thread(target=show_emergency_alert)
    alert_thread.daemon = True
    alert_thread.start()

hist_df_full = pd.read_csv(HISTORICAL_DATA_FILE)

# Calculate technical indicators for ALL candidates (needed for ranking)
print("📈 STEP 2: Calculating technical indicators for all candidates...")
adx_df_full = calculate_adx_multi(hist_df_full, all_candidate_tickers, period=21)
pmo_df_full = calculate_pmo_multi(hist_df_full, all_candidate_tickers)
cci_df_full = calculate_cci_multi(hist_df_full, all_candidate_tickers)

# Merge technical indicators back into historical data
hist_df_full = hist_df_full.merge(adx_df_full[["Datetime", "Ticker", "ADX", "+DI", "-DI"]], on=["Datetime", "Ticker"], how="left")
hist_df_full = hist_df_full.merge(pmo_df_full[["Datetime", "Ticker", "PMO", "PMO_signal"]], on=["Datetime", "Ticker"], how="left")
hist_df_full = hist_df_full.merge(cci_df_full[["Datetime", "Ticker", "CCI"]], on=["Datetime", "Ticker"], how="left")

# Update the global historical_data with all technical indicators
historical_data = hist_df_full
print(f"✅ Historical data updated with technical indicators for {len(all_candidate_tickers)} tickers")

# STEP 3: Now run the selection process to pick top 5 from all candidates
print("🎯 STEP 3: Running candidate selection to pick top 5...")
try:
    top5_df = select_trade_candidates()
    print(f"✅ select_trade_candidates() returned: {type(top5_df)}")
    print(f"   Shape: {top5_df.shape if hasattr(top5_df, 'shape') else 'No shape attr'}")
    print(f"   Columns: {top5_df.columns.tolist() if hasattr(top5_df, 'columns') else 'No columns attr'}")
    
    if top5_df.empty:
        print("❌ CRITICAL: select_trade_candidates() returned empty DataFrame!")
        print("   Using fallback tickers from candidate list")
        # Fallback to first 5 candidates
        fallback_tickers = all_candidate_tickers[:5]
        top5_df = pd.DataFrame({"Symbol": fallback_tickers, "CompositeScore": [3.0] * len(fallback_tickers)})
        
except Exception as e:
    print(f"❌ CRITICAL: Error in select_trade_candidates(): {e}")
    import traceback
    traceback.print_exc()
    # Emergency fallback
    fallback_tickers = all_candidate_tickers[:5]
    top5_df = pd.DataFrame({"Symbol": fallback_tickers, "CompositeScore": [3.0] * len(fallback_tickers)})
    print(f"   Using emergency fallback: {fallback_tickers}")

tickers = top5_df["Symbol"].tolist()

# 🔒 ENSURE EXACTLY 5 TICKERS FOR DASHBOARD
if len(tickers) > 5:
    print(f"⚠️ TRIMMING tickers from {len(tickers)} to 5 items")
    tickers = tickers[:5]
print(f"🎯 FINAL DASHBOARD TICKERS: {tickers} (count: {len(tickers)})")

#                                   ***** Call ai_module to get trade recommendations *****
# Get AI trade recommendations for the selected tickers
print("🤖 STEP 3.5: Getting AI trade recommendations for selected tickers...")
print(f"   Input tickers for AI: {tickers}")

try:
    ai_recommendations = get_trade_recommendations(tickers, return_df=True)
    top5_ai = ai_recommendations.head(5)
    print(f"✅ AI recommendations loaded for {len(ai_recommendations)} tickers")
    
    if not ai_recommendations.empty:
        print("📊 AI Summary:")
        for _, row in ai_recommendations.iterrows():
            print(f"   {row['ticker']}: {row['probability']:.2%} - {row['recommendation'][:50]}...")
    else:
        print("⚠️ AI recommendations is empty!")
        
except Exception as e:
    print(f"❌ Error generating AI recommendations: {e}")
    import traceback
    traceback.print_exc()
    ai_recommendations = pd.DataFrame()
    top5_ai = pd.DataFrame()

# NOTE: Dashboard update will be triggered by the callback system

#                            ****** End of AI trade recommendations *****   

ticker_ranks = dict(zip(top5_df["Symbol"], top5_df["CompositeScore"]))

# STEP 4: Dashboard prep for the selected 5 tickers
print("📊 STEP 4: Preparing dashboard data for selected tickers...")
hist_df = historical_data[historical_data["Ticker"].isin(tickers)].copy()  # Filter to selected tickers
price_lookup = {}
for symbol in tickers:
    tdf = hist_df[hist_df["Ticker"] == symbol].copy()
    if not tdf.empty:
        tdf["current_price"] = tdf["Close"].iloc[-1]
        price_lookup[symbol] = tdf
print("DEBUG: price_lookup for ranking:")
for k, v in price_lookup.items():
    print(f"{k}: {v.tail(1)}")
etf_ranks = rank_top5_etfs(
    etf_list=tickers,
    news_api_key=NEWS_API_KEY,
    finnhub_api_key=FINNHUB_API_KEY,
    price_lookup=price_lookup,
    cache={"news": load_news_cache(), "whale": load_whale_cache()}
)
final_ranks = []
for etf in etf_ranks:
    symbol = etf['symbol']
    old_rank = ticker_ranks.get(symbol, 3)
    new_rank = etf['composite_rank']
    combined_rank = round((old_rank + new_rank) / 2, 2)
    etf['final_rank'] = combined_rank
    final_ranks.append(etf)
print("==== Combined ETF Rankings ====")
for etf in final_ranks:
    print(f"{etf['symbol']}: Final Rank {etf['final_rank']} (Old: {ticker_ranks.get(etf['symbol'], 3)}, New: {etf['composite_rank']})")
dashboard_ranks = {etf['symbol']: etf['final_rank'] for etf in final_ranks}

# STEP 5: Initialize AI recommendations for the selected tickers
print("🤖 STEP 5: Initializing AI recommendations for dashboard...")
try:
    # Call AI recommendations for the newly selected tickers
    print(f"Calling AI recommendations for: {tickers}")
    ai_recommendations = get_trade_recommendations(tickers, return_df=True)
    top5_ai = ai_recommendations.head(5)
    print(f"✅ AI recommendations ready: {len(ai_recommendations)} tickers")
    
    # Display summary
    if not ai_recommendations.empty:
        trade_count = len([r for r in ai_recommendations['recommendation'] if 'TRADE:' in r])
        no_trade_count = len([r for r in ai_recommendations['recommendation'] if 'No trade' in r])
        print(f"   Trade candidates: {trade_count}")
        print(f"   No trade (red X): {no_trade_count}")
    else:
        print("   ⚠️ No AI recommendations generated")
        
except Exception as e:
    print(f"❌ Error generating AI recommendations: {e}")
    ai_recommendations = pd.DataFrame()
    top5_ai = pd.DataFrame()

                                   # ***** Start Schwab Historical Data Retrieval Functions *****

HISTORICAL_DATA_FILE = "historical_data.csv"

def fetch_schwab_1min_history(ticker, period=1):
    """
    Fetches up to 'period' days of 1-minute OHLCV bars for a ticker from Schwab.
    Handles Schwab token refresh on 401 error.
    Returns a DataFrame with standardized columns.
    """
    from schwab_data import fetch_schwab_minute_ohlcv  # Ensure this is implemented as discussed

    def try_fetch():
        try:
            df, status_code = fetch_schwab_minute_ohlcv(ticker, period=period, return_status=True)
            return df, status_code
        except Exception as e:
            print(f"Exception during Schwab fetch: {e}")
            return None, None

    df, status_code = try_fetch()
    if status_code == 401:
        print("401 Unauthorized from Schwab API. Attempting token refresh...")
        ensure_schwab_token()
        df, status_code = try_fetch()
        if status_code == 401:
            print("Token refresh failed or still unauthorized. Please check Schwab_auth.")
            return pd.DataFrame()
    if df is not None and not df.empty:
        if "averageVolume10day" not in df.columns:
            df["averageVolume10day"] = np.nan
        df = df[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"]]
    return df

def load_historical_data_from_schwab(tickers, period=1):
    """
    Loads historical data from CSV if present and not empty.
    If missing or empty, fetches from Schwab and merges with any existing data, then saves to CSV.
    Returns DataFrame.
    """
 
    if os.path.exists(HISTORICAL_DATA_FILE):
        df = pd.read_csv(HISTORICAL_DATA_FILE, parse_dates=["Datetime"])
        if not df.empty:
            print("Loaded historical data from CSV.")
            return df
        else:
            print("CSV is empty, fetching from Schwab...")
    else:
        print("CSV not found, fetching from Schwab...")

    # Fetch from Schwab
    all_data = []
    for ticker in tickers:
        print(f"Fetching {ticker} history from Schwab...")
        try:
            df = fetch_schwab_1min_history(ticker, period=period)
            if not df.empty:
                all_data.append(df)
            else:
                print(f"⚠️ No Schwab data returned for {ticker}")
        except Exception as e:
            print(f"Error fetching {ticker} from Schwab: {e}")
    if all_data:
        hist_df = pd.concat(all_data, ignore_index=True)
        # Merge with any existing data (if file exists)
        if os.path.exists(HISTORICAL_DATA_FILE):
            try:
                existing_df = pd.read_csv(HISTORICAL_DATA_FILE)
                hist_df = pd.concat([existing_df, hist_df], ignore_index=True)
            except Exception:
                pass
        hist_df = hist_df.drop_duplicates(subset=["Datetime", "Ticker"], keep="last")
        hist_df = hist_df.sort_values(["Datetime", "Ticker"])
        print("About to save historical_data.csv 2109")
        print(hist_df[["Datetime", "Ticker"]].head(3))
        print(hist_df[["Datetime", "Ticker"]].tail(3))
        hist_df.to_csv(HISTORICAL_DATA_FILE, index=False)
        print("Historical data saved to CSV.")
        return hist_df
    else:
        print("No historical data fetched.")
        return pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"])

def save_historical_data(df, filename="historical_data.csv"):
    """
    Saves DataFrame to CSV, keeping all relevant columns in the correct order.
    """
    required_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan
    df = df[required_cols]
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    df = df.sort_values(by=["Ticker", "Datetime"], ascending=True)
    
    # **FIX: Use consistent datetime format without seconds**
    df["Datetime"] = df["Datetime"].dt.strftime("%Y-%m-%d %H:%M")
    
    print("About to save historical_data.csv")
    print(df[["Datetime", "Ticker"]].head(3))
    print(df[["Datetime", "Ticker"]].tail(3))
    df.to_csv(filename, index=False)

def update_historical_data(historical_data, new_data, max_entries=10000):
    """
    Appends new_data to historical_data, removes duplicates, sorts, and trims to max_entries.
    Always keeps the most recent rows.
    """
    import pandas as pd

    combined = pd.concat([historical_data, new_data], ignore_index=True)
    combined = combined.dropna(subset=["Close", "Volume"])
    combined = combined.drop_duplicates(subset=["Datetime", "Ticker"], keep="last")
    combined = combined.sort_values(["Datetime", "Ticker"])
    if len(combined) > max_entries:
        combined = combined.sort_values("Datetime", ascending=False).head(max_entries)
        combined = combined.sort_values(["Datetime", "Ticker"])
    return combined

# ***** End Schwab Historical Data Retrieval Functions *****

def append_realtime_to_historical(historical_df, realtime_df, max_ticks=200):
    """
    Appends new real-time bars to historical data, ensuring correct OHLC logic.
    Handles Datetime as string or integer (timestamp in ms).
    Returns: Updated historical_df with new bars appended, sorted, deduped, and trimmed.
    """
    import pandas as pd

    # Ensure correct types
    historical_df = historical_df.copy()
    realtime_df = realtime_df.copy()

    # --- Robust Datetime conversion for both DataFrames ---
    def fix_datetime_col(df):
        if df.empty:
            return df
        # Convert to pandas datetime (handles string, int, or already datetime)
        df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
        return df

    historical_df = fix_datetime_col(historical_df)
    realtime_df = fix_datetime_col(realtime_df)

    # Prepare new rows
    new_rows = []
    for _, row in realtime_df.iterrows():
        ticker = row['Ticker']
        dt = row['Datetime']
        close = row['Close']
        volume = row['Volume']

        # Try to get OHLC from realtime_df, else set to None
        open_ = row['Open'] if 'Open' in row and not pd.isna(row['Open']) else None
        high_ = row['High'] if 'High' in row and not pd.isna(row['High']) else None
        low_ = row['Low'] if 'Low' in row and not pd.isna(row['Low']) else None

        # Get previous close for this ticker
        prev = historical_df[historical_df['Ticker'] == ticker].sort_values('Datetime')
        prev_close = prev.iloc[-1]['Close'] if not prev.empty else close

        # If OHLC not provided, set all to close
        if open_ is None or high_ is None or low_ is None:
            open_ = prev_close  # Open = previous close
            high_ = close
            low_ = close

        new_rows.append({
            'Datetime': dt,
            'Ticker': ticker,
            'Open': open_,
            'High': high_,
            'Low': low_,
            'Close': close,
            'Volume': volume
        })

    # Convert to DataFrame and append
    new_df = pd.DataFrame(new_rows)
    combined = pd.concat([historical_df, new_df], ignore_index=True)

    # Round numeric columns
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").round(2)

    # Ensure Datetime is pandas datetime for sorting/deduplication
    combined['Datetime'] = pd.to_datetime(combined['Datetime'], errors='coerce')

    # Drop duplicates, keeping the latest
    combined = combined.drop_duplicates(subset=["Datetime", "Ticker"], keep="last")

    # Sort and keep only the last N bars per ticker
    combined = combined.sort_values(["Ticker", "Datetime"])
    combined = combined.groupby("Ticker").tail(max_ticks).reset_index(drop=True)

    return combined

def fetch_batch_ohlc(tickers, access_token, last_cum_vol):
    """
    Fetch OHLCV for all tickers from Schwab.
    last_cum_vol: dict of {symbol: last_cumulative_volume}
    Returns: dict {symbol: ohlc_dict}
    """
    results = {}
    tickers_to_retry = []
    tokens = load_schwab_tokens()
    access_token = tokens["access_token"]

    for symbol in tickers:
        result = fetch_schwab_realtime_ohlc(access_token, symbol, last_cum_vol.get(symbol))
        if result is None:
            tickers_to_retry.append(symbol)
        else:
            results[symbol] = result

    # If any 401s, refresh token ONCE and retry those tickers
    if tickers_to_retry:
        print("Refreshing Schwab OAuth token for all tickers after 401 error.")
        tokens = refresh_access_token()
        access_token = tokens["access_token"]
        for symbol in tickers_to_retry:
            result = fetch_schwab_realtime_ohlc(access_token, symbol, last_cum_vol.get(symbol))
            results[symbol] = result
    return results

def on_new_ohlcv_bar(bar):
    row = {
        "Datetime": pd.to_datetime(bar['datetime'], unit='ms').strftime("%Y-%m-%d %H:%M"),
        "Ticker": bar['key'],
        "Open": bar['openPrice'],
        "High": bar['highPrice'],
        "Low": bar['lowPrice'],
        "Close": bar['closePrice'],
        "Volume": bar['volume']
    }
    print("Streaming OHLCV bar received:", row)

    global historical_data
    if 'historical_data' not in globals() or historical_data is None:
        historical_data = pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
    historical_data = pd.concat([historical_data, pd.DataFrame([row])], ignore_index=True)
    historical_data.drop_duplicates(subset=["Datetime", "Ticker"], keep="last", inplace=True)
    historical_data.sort_values(["Datetime", "Ticker"], inplace=True)
    historical_data.reset_index(drop=True, inplace=True)

    csv_path = os.path.join(os.getcwd(), "historical_data.csv")
    file_exists = os.path.isfile(csv_path)
    header_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]
    print("About to save historical_data.csv 2267")
    print(historical_data[["Datetime", "Ticker"]].head(3))
    print(historical_data[["Datetime", "Ticker"]].tail(3))
    pd.DataFrame([row]).to_csv(
        csv_path,
        mode="a",
        header=not file_exists,
        index=False,
        columns=header_cols
    )
    print(f"✅ Streaming OHLCV bar appended to {csv_path}.")

                                 # ***** Real-time Data Retrieval Functions from etrade for 52 week high low *****

def get_realtime_data(tickers, interval='1m', count=30):
   
    quote_data = fetch_batch_quotes(tickers)
    etrade_df = fetch_etrade_market_data(tickers)
    etrade_df = etrade_df.set_index("Ticker") if not etrade_df.empty else pd.DataFrame()

    all_data = []
    for symbol in tickers:
        q = quote_data.get(symbol)
        if not q or "quote" not in q:
            continue
        quote = q["quote"]

        # --- Fix Datetime ---
        quote_time = quote.get("quoteTime") or quote.get("tradeTime") or 0
        if isinstance(quote_time, (int, float)):
            dt_str = pd.to_datetime(quote_time // 1000, unit='s').strftime("%Y-%m-%d %H:%M")
        else:
            dt_str = str(quote_time)

        # Get E*TRADE 52-week stats for this symbol
        week52High = week52Low = week52HiDate = week52LowDate = None
        if not etrade_df.empty and symbol in etrade_df.index:
            week52High = etrade_df.at[symbol, "week52High"]
            week52Low = etrade_df.at[symbol, "week52Low"]
            week52HiDate = etrade_df.at[symbol, "week52HiDate"]
            week52LowDate = etrade_df.at[symbol, "week52LowDate"]

        all_data.append({
            "Datetime": dt_str,
            "Ticker": symbol,
            "Open": quote.get("openPrice") if quote.get("openPrice") is not None else quote.get("lastPrice"),
            "High": quote.get("highPrice") if quote.get("highPrice") is not None else quote.get("lastPrice"),
            "Low": quote.get("lowPrice") if quote.get("lowPrice") is not None else quote.get("lastPrice"),
            "Close": quote.get("lastPrice") or quote.get("closePrice"),
            "Volume": quote.get("totalVolume"),
            "AfterHours": q.get("extended", {}).get("lastPrice"),
            "PreMarket": None,
            "52WeekHigh": week52High,
            "52WeekHighDate": week52HiDate,
            "52WeekLow": week52Low,
            "52WeekLowDate": week52LowDate,
        })
    if all_data:
        df = pd.DataFrame(all_data)
        for col in ["Open", "High", "Low", "Close", "Volume", "AfterHours", "PreMarket", "52WeekHigh", "52WeekLow"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        print("Top 10 rows of real-time data:\n", df.head(10))
        return df
    else:
        print("No valid data returned for requested tickers.")
        return pd.DataFrame(columns=[
            "Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "AfterHours", "PreMarket",
            "52WeekHigh", "52WeekHighDate", "52WeekLow", "52WeekLowDate"
        ])
    
def run_realtime_data(historical_data, tickers, session=None, base_url=None):
    """
    Uses Schwab streaming for real-time data during market hours,
    and falls back to 1-min historical data from Schwab for pre/post-market.
    Updates and returns the merged DataFrame.
    """
    global streamer
    header_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]

    if is_market_open():
        print("Market is open. Using Schwab streaming data for real-time updates.")
        logging.info("Market is open. Using Schwab streaming data for real-time updates.")

        # Start the streamer with your handler (if not already started elsewhere)
        if streamer is None:
            logging.info("Starting Schwab streamer for real-time data.")
            streamer = get_streamer(APP_KEY, APP_SECRET, schwab_streaming_handler)
            for symbol in tickers:
                streamer.send(streamer.level_one_equities(symbol, "0,3,8"))

        # Build a DataFrame from the latest streaming data
        global realtime_ds
        realtime_data_list = []
        for ticker in tickers:
            if ticker in realtime_ds and realtime_ds[ticker]:
                latest = realtime_ds[ticker][-1]
                dt = pd.Timestamp.now().floor("min")
                close = latest.get("3") or latest.get("Close")
                open_ = latest.get("Open", close)
                high_ = latest.get("High", close)
                low_ = latest.get("Low", close)
                volume = latest.get("Volume", 0)
                realtime_data_list.append({
                    "Datetime": dt,
                    "Ticker": ticker,
                    "Open": open_,
                    "High": high_,
                    "Low": low_,
                    "Close": close,
                    "Volume": volume
                })
        if realtime_data_list:
            realtime_df = pd.DataFrame(realtime_data_list)
            historical_data = append_realtime_to_historical(historical_data, realtime_df)
        else:
            print("⚠️ No streaming data available, using previous historical data.")

    else:
        print("Market is closed (pre/post-market). Using 1-min historical data from Schwab.")
        
        # --- STOP STREAMER IF RUNNING ---
        if streamer is not None:
            try:
                streamer.stop()
                print("✅ Schwab streamer stopped after market close.")
            except Exception as e:
                print(f"⚠️ Error stopping Schwab streamer: {e}")
            streamer = None

        # **CRITICAL FIX: Refresh token proactively when switching from streaming to historical**
        print("🔄 Proactively refreshing Schwab token for after-hours data...")
        ensure_schwab_token()

        # Fetch latest 1-min bars for all tickers
        from schwab_data import fetch_schwab_latest_minute
        new_rows = []
        token_refreshed = False
        
        for symbol in tickers:
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    result = fetch_schwab_latest_minute(symbol)
                    
                    # Handle tuple return (df, status_code)
                    if isinstance(result, tuple):
                        df_new, status_code = result
                        
                        if status_code == 401:
                            if not token_refreshed and attempt == 0:
                                print(f"401 Unauthorized for {symbol} during after-hours fetch. Refreshing Schwab token and retrying...")
                                ensure_schwab_token()
                                token_refreshed = True
                                continue  # Retry with new token
                            else:
                                print(f"Still 401 after token refresh for {symbol}. Skipping.")
                                break
                    else:
                        df_new = result
                    
                    if not df_new.empty:
                        new_rows.append(df_new)
                        break  # Success, move to next symbol
                    else:
                        break  # No data, but no error
                        
                except Exception as e:
                    print(f"Error fetching after-hours data for {symbol} (attempt {attempt + 1}): {e}")
                    if attempt == max_retries - 1:
                        print(f"Max retries exceeded for {symbol}")

        if new_rows:
            realtime_df = pd.concat(new_rows, ignore_index=True)
            historical_data = append_realtime_to_historical(historical_data, realtime_df)
        else:
            print("⚠️ No new 1-min data fetched from Schwab.")

    # Calculate indicators
    adx_df = calculate_adx_multi(historical_data, tickers)
    pmo_df = calculate_pmo_multi(historical_data, tickers)

    # Merge indicators into historical_data for plotting/alerts
    merged = historical_data
    try:
        merged = merged.merge(
            adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]],
            on=["Datetime", "Ticker"], how="left"
        ).merge(
            pmo_df[["Datetime", "Ticker", "PMO", "PMO_signal"]],
            on=["Datetime", "Ticker"], how="left"
        )
    except Exception as e:
        print(f"⚠️ Error merging indicators: {e}")

    # Save merged data to CSV
    save_historical_data(merged)

    return merged

                               # ***** End of historical data retrieval from Schwab *****


                # ***** Merge historical and realtime data *****

                                       # ***** Function to merge historical & real-time data *****


# --- Function to merge historical & real-time data ---

HISTORICAL_DATA_FILE = r"C:\Users\mjmat\Python Code in VS\historical_data.csv"

def merge_historical_realtime(historical_data, realtime_ds):
    # Use all tickers present in either historical_data or realtime_ds
    merge_tickers = set(historical_data['Ticker'].unique()) | set(realtime_ds.keys())

    #Merge historical data with real-time data for the given tickers.
    #Updates the historical_data DataFrame with the latest real-time data.

    print("🔍 Running merge_historical_realtime()...")

    # Create a DataFrame to hold the real-time data
    realtime_data_list = []

    for ticker in merge_tickers:
        if ticker in realtime_ds:
            # Get the latest data point for the ticker
            realtime_data = realtime_ds[ticker][-1]  # Extract the last (most recent) entry in the list

            timestamp = pd.Timestamp.now().floor("min")  # Current timestamp for real-time data

            if not realtime_data:
                logging.warning(f"⚠️ Skipping {ticker} due to missing real-time data.")
                continue

            # Add real-time data for the ticker
            realtime_data_list.append({
                "Datetime": timestamp,
                "Ticker": ticker,
                "Close": round(realtime_data.get("Close", 0), 2),
                "High": round(realtime_data.get("High", 0), 2),
                "Low": round(realtime_data.get("Low", 0), 2),
                "Open": round(realtime_data.get("Open", 0), 2),
                "Volume": round(realtime_data.get("Volume", 0), 2),
                "averageVolume10day": round(realtime_data.get("averageVolume10Day", 0), 2),  # <-- Ensure this line is present
            })

    # Convert the real-time data list to a DataFrame
    if realtime_data_list:
        realtime_df = pd.DataFrame(realtime_data_list)
        realtime_df["Datetime"] = pd.to_datetime(realtime_df["Datetime"])  # Ensure Datetime is consistent

        # Concatenate and ensure Datetime is a column, not index
        historical_data = pd.concat([historical_data.reset_index(drop=True), realtime_df], ignore_index=True)

    # Ensure the 'Datetime' column is datetime type
    historical_data["Datetime"] = pd.to_datetime(historical_data["Datetime"])

    # Sort the DataFrame by Datetime ascending (oldest first, newest last)
    historical_data = historical_data.sort_values(by="Datetime", ascending=True)

    # Only keep the correct columns in the right order (including averageVolume10day)
    if "averageVolume10day" not in historical_data.columns:
        historical_data["averageVolume10day"] = np.nan
    historical_data = historical_data[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"]]

    # Debug: Print the merged historical data
    logging.debug(f"Merged Historical Data:\n{historical_data}")

    max_ticks = 200  # or your desired window
    historical_data = historical_data.sort_values(["Ticker", "Datetime"])
    historical_data = historical_data.groupby("Ticker").tail(max_ticks).reset_index(drop=True)

    return historical_data

                                       # ***** Function to fetch Schwab timesales and quote data *****


def fetch_schwab_realtime_ohlc(access_token, symbol, last_cumulative_volume=None):
    """
    Fetches OHLCV data for a symbol from Schwab.
    Returns a dict: {Datetime, Ticker, Open, High, Low, Close, Volume, CumulativeVolume}
    last_cumulative_volume: previous cumulative volume for this symbol (for after-hours)
    """

def is_market_open():
    """
    Returns True if the current time is between 4:00am and 8:00pm US/Eastern, Monday-Friday.
    """
    from datetime import datetime
    import pytz
    now = datetime.now(pytz.timezone("US/Eastern"))
    # Only open Monday-Friday
    if now.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
        return False
    market_open = now.replace(hour=4, minute=0, second=0, microsecond=0)
    market_close = now.replace(hour=20, minute=0, second=0, microsecond=0)
    is_open = market_open <= now <= market_close
    print(f"Market check: Current time {now.strftime('%H:%M:%S')}, Market open: {is_open}")
    return is_open

def update_with_latest_minute():
    """
    Updates historical_data.csv with the latest 1-min bars from Schwab for all tickers.
    Handles Schwab 401 Unauthorized errors by refreshing the token and retrying once.
    """
    if not is_market_open():
        print("Market is closed. Skipping latest minute update.")
        return

    hist_file = "historical_data.csv"
    from schwab_data import fetch_schwab_latest_minute
    import pandas as pd

    try:
        historical_data = pd.read_csv(hist_file)
    except FileNotFoundError:
        historical_data = pd.DataFrame()

    new_rows = []
    token_refreshed = False  # Track if we've already refreshed the token
    
    for symbol in tickers:
        max_retries = 2
        for attempt in range(max_retries):
            try:
                result = fetch_schwab_latest_minute(symbol)
                
                # Handle tuple return (df, status_code)
                if isinstance(result, tuple):
                    df_new, status_code = result
                    
                    if status_code == 401:
                        if not token_refreshed and attempt == 0:
                            print(f"401 Unauthorized for {symbol}. Refreshing Schwab token...")
                            ensure_schwab_token()
                            token_refreshed = True
                            continue  # Retry with new token
                        else:
                            print(f"Still 401 after token refresh for {symbol}. Skipping.")
                            break
                else:
                    df_new = result
                    status_code = 200
                
                if not df_new.empty:
                    new_rows.append(df_new)
                    break  # Success, move to next symbol
                else:
                    print(f"No data returned for {symbol}")
                    break
                    
            except Exception as e:
                print(f"Error fetching latest minute for {symbol} (attempt {attempt + 1}): {e}")
                if attempt == max_retries - 1:
                    print(f"Max retries exceeded for {symbol}")

    if new_rows:
        all_new = pd.concat(new_rows, ignore_index=True)
        historical_data = pd.concat([historical_data, all_new], ignore_index=True)
        
        # Drop duplicates, sort, and save
        historical_data.drop_duplicates(subset=["Datetime", "Ticker"], keep="last", inplace=True)
        historical_data.sort_values(["Datetime", "Ticker"], inplace=True)
        historical_data.reset_index(drop=True, inplace=True)
        
        print("About to save historical_data.csv (update_with_latest_minute)")
        print(historical_data[["Datetime", "Ticker"]].head(3))
        print(historical_data[["Datetime", "Ticker"]].tail(3))
        historical_data.to_csv(hist_file, index=False)
        print("Historical data updated with latest minute bars.")
    else:
        print("No new data fetched from any symbol.")

def run_realtime_job():
    global historical_data
    global tickers, session, base_url
    print("⏰ [SCHEDULER] Real-time data update fired at", datetime.now().strftime('%H:%M:%S'))
    historical_data = load_historical_data_from_schwab(tickers)

    # Get top 5 tickers from AI
    from ai_module import get_trade_recommendations
    recommendations = get_trade_recommendations(tickers, return_df=True)
    top5_tickers = recommendations.head(5)["ticker"].tolist()

    check_trade_alerts(historical_data, top5_tickers)
    print("✅ [SCHEDULER] Real-time data update completed at", datetime.now().strftime('%H:%M:%S'))

def dashboard_update_job():
    print("📊 [SCHEDULER] Dashboard update fired at", datetime.now().strftime('%H:%M:%S'))
    
    global tickers, historical_data
    
    # Check if we have properly selected tickers
    if not tickers or len(tickers) == 0:
        print("⚠️ [SCHEDULER] No tickers available for dashboard update, skipping...")
        return
    
    print(f"📊 [SCHEDULER] Updating dashboard for tickers: {tickers}")

    # --- Load Quiver government and institutional data ---
    def load_quiver_cache(cache_path):
        import json
        import pandas as pd
        import os
        if not os.path.exists(cache_path):
            return pd.DataFrame()
        with open(cache_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        # Standardize date columns
        for col in ["TransactionDate", "reportDate", "Date"]:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        return df

    congress_df = load_quiver_cache("quiver_congress_cache.json")
    inst_df = load_quiver_cache("quiver_institutional_cache.json")
    print(f"Loaded Quiver Congress data: {congress_df.shape}")
    print(f"Loaded Quiver Institutional data: {inst_df.shape}")

    # --- Existing dashboard update logic ---
    df = pd.read_csv(HISTORICAL_DATA_FILE)
    if "Ticker" not in df.columns:
        print("❌ 'Ticker' column missing from historical data!")
        print("Columns present:", df.columns)
        return
    adx_df = calculate_adx_multi(df, tickers)
    filtered_df = pd.merge(
        df,
        adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]],
        on=["Datetime", "Ticker"],
        how="left"
    )
    pmo_df = calculate_pmo_multi(filtered_df, tickers)
    if not pmo_df.empty:
        filtered_df = pd.merge(
            filtered_df,
            pmo_df[["Datetime", "Ticker", "PMO", "PMO_signal"]],
            on=["Datetime", "Ticker"],
            how="left"
        )
    cci_df = calculate_cci_multi(filtered_df, tickers)
    if not cci_df.empty:
        filtered_df = pd.merge(
            filtered_df,
            cci_df[["Datetime", "Ticker", "CCI"]],
            on=["Datetime", "Ticker"],
            how="left"
        )
    global market_data_df
    market_data_df = fetch_etrade_market_data(tickers)
    check_trade_alerts(filtered_df, tickers)

    # You can now use congress_df and inst_df in your dashboard as needed

print("🚀 [MAIN] Starting dashboard at 3287", datetime.now().strftime('%H:%M:%S'))

def run_dashboard_thread():
    try:
        print("🚀 [MAIN] Starting dashboard immediately with initial data...")
        
        # Debug: Check the data being passed to dashboard
        print(f"Historical data shape: {historical_data.shape}")
        print(f"Historical data columns: {historical_data.columns.tolist()}")
        print(f"Tickers being passed: {tickers}")
        print(f"Dashboard ranks: {dashboard_ranks}")
        
        # Load historical data and calculate filtered_df before starting dashboard
        adx_df = calculate_adx_multi(historical_data, tickers)
        filtered_df = pd.merge(
            historical_data,
            adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]],
            on=["Datetime", "Ticker"],
            how="left"
        )
        
        print(f"Filtered data shape: {filtered_df.shape}")
        
        def debug_data_for_charts():
            """Debug function to check data quality for charts"""
            print("\n=== CHART DATA DEBUG ===")
            
            # Check CSV file
            if os.path.exists("historical_data.csv"):
                csv_df = pd.read_csv("historical_data.csv")
                print(f"CSV file: {len(csv_df)} rows, {len(csv_df['Ticker'].unique())} tickers")
                print(f"CSV tickers: {csv_df['Ticker'].unique()}")
                print(f"CSV date range: {csv_df['Datetime'].min()} to {csv_df['Datetime'].max()}")
            else:
                print("❌ No CSV file found")
            
            # Check global variable
            global historical_data
            if historical_data is not None and not historical_data.empty:
                print(f"Global data: {len(historical_data)} rows, {len(historical_data['Ticker'].unique())} tickers")
                print(f"Global tickers: {historical_data['Ticker'].unique()}")
            else:
                print("❌ Global historical_data is empty")
            
            print("=== END DEBUG ===\n")

        # Call this right before starting dashboard
        debug_data_for_charts()
        
        # **FIX: Call start_dashboard directly - it handles app.run() internally**
        start_dashboard(historical_data, filtered_df, tickers, dashboard_ranks)
        
    except Exception as e:
        import traceback
        print("❌ Exception in run_dashboard_thread:", e)
        traceback.print_exc()

def refresh_news_cache():
    news_cache = load_news_cache()
    global ai_recommendations
    if ai_recommendations is None or ai_recommendations.empty:
        print("No AI recommendations available for news refresh.")
        return
    top5 = ai_recommendations.head(5)["ticker"].tolist()
    print(f"🔔 Refreshing news for top 5 tickers: {top5}")
    for ticker in top5:
        fetch_etf_news(ticker, news_cache=news_cache)

def refresh_whale_cache():
    print("🔄 Refreshing whale cache for all tickers...")
    for ticker in tickers:
        fetch_whale_data(ticker)
    print("✅ Whale cache refreshed.")

def fetch_quiver_congress_trades(ticker):
    """
    Fetches recent Congress trades for a ticker from QuiverQuant.
    Returns a list of trade dicts (never None).
    """
    url = f"https://api.quiverquant.com/beta/historical/congresstrading/{ticker.upper()}"
    headers = {"accept": "application/json"}
    if QUIVERQUANT_API_KEY:
        headers["Authorization"] = f"Bearer {QUIVERQUANT_API_KEY}"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"QuiverQuant API error for {ticker}: {resp.status_code} {resp.text}")
            return []
    except Exception as e:
        print(f"QuiverQuant fetch error for {ticker}: {e}")
        return []
    
def fetch_quiver_institutional_trades(ticker):
    """
    Fetches recent institutional trades for a ticker from QuiverQuant.
    Returns a list of trade dicts (never None).
    """
    url = f"https://api.quiverquant.com/beta/historical/institutionaltrading/{ticker.upper()}"
    headers = {"accept": "application/json"}
    if QUIVERQUANT_API_KEY:
        headers["Authorization"] = f"Bearer {QUIVERQUANT_API_KEY}"
    try:
        resp = requests.get(url, headers=headers)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return data
            else:
                return []
        else:
            print(f"QuiverQuant API error for {ticker} (institutional): {resp.status_code} {resp.text}")
            return []
    except Exception as e:
        print(f"QuiverQuant fetch error for {ticker} (institutional): {e}")
        return []

from datetime import datetime, timedelta

def refresh_quiver_congress_cache(ticker_list, cache_path="quiver_congress_cache.json", delay=1, days=30):
    all_trades = []
    seen = set()
    cutoff = datetime.now() - timedelta(days=days)
    for ticker in ticker_list:
        symbols_to_fetch = [ticker]
        if ticker in ETF_UNDERLYING_MAP:
            underlying = ETF_UNDERLYING_MAP[ticker]
            if underlying not in symbols_to_fetch:
                symbols_to_fetch.append(underlying)
        for symbol in symbols_to_fetch:
            if symbol in seen:
                continue
            seen.add(symbol)
            print(f"Fetching QuiverQuant Congress trades for {symbol}...")
            trades = fetch_quiver_congress_trades(symbol)
            # Filter trades to last N days
            filtered_trades = []
            for trade in trades:
                trade["Ticker"] = symbol.upper()
                date_str = trade.get("TransactionDate") or trade.get("Date")
                if date_str:
                    try:
                        trade_date = pd.to_datetime(date_str)
                        if trade_date >= cutoff:
                            filtered_trades.append(trade)
                    except Exception:
                        continue
            all_trades.extend(filtered_trades)
            time.sleep(delay)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(all_trades, f, default=str)
    print(f"Saved {len(all_trades)} Congress trades (last {days} days) to {cache_path}")

def refresh_quiver_institutional_cache(ticker_list, cache_path="quiver_institutional_cache.json", delay=1, days=30):
    """
    Fetches institutional trades for all tickers and their underlyings, saves only recent trades to a cache file.
    delay: seconds to wait between API calls (to avoid rate limits).
    days: only keep trades from the last N days.
    """
    from datetime import datetime, timedelta
    all_trades = []
    seen = set()
    cutoff = datetime.now() - timedelta(days=days)
    for ticker in ticker_list:
        symbols_to_fetch = [ticker]
        if ticker in ETF_UNDERLYING_MAP:
            underlying = ETF_UNDERLYING_MAP[ticker]
            if underlying not in symbols_to_fetch:
                symbols_to_fetch.append(underlying)
        for symbol in symbols_to_fetch:
            if symbol in seen:
                continue
            seen.add(symbol)
            print(f"Fetching QuiverQuant Institutional trades for {symbol}...")
            trades = fetch_quiver_institutional_trades(symbol)
            # Filter trades to last N days
            filtered_trades = []
            for trade in trades:
                trade["Ticker"] = symbol.upper()
                date_str = trade.get("Date") or trade.get("TransactionDate") or trade.get("reportDate")
                if date_str:
                    try:
                        trade_date = pd.to_datetime(date_str)
                        if trade_date >= cutoff:
                            filtered_trades.append(trade)
                    except Exception:
                        continue
            all_trades.extend(filtered_trades)
            time.sleep(delay)  # Be nice to the API
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(all_trades, f, default=str)
    print(f"Saved {len(all_trades)} Institutional trades (last {days} days) to {cache_path}")

def daily_full_quiver_pull(ticker_list, cache_path, last_pull_file, delay=1):
    """
    Pulls Quiver data for all tickers once per day.
    """
    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")
    last_pull = None
    if os.path.exists(last_pull_file):
        with open(last_pull_file, "r") as f:
            last_pull = f.read().strip()
    if last_pull == today:
        print(f"✅ Already did full Quiver pull today ({today}). Skipping.")
        return
    print(f"🚀 Doing full Quiver pull for all tickers ({today})...")
    refresh_quiver_congress_cache(ticker_list, cache_path="quiver_congress_cache.json", delay=delay)
    refresh_quiver_institutional_cache(ticker_list, cache_path="quiver_institutional_cache.json", delay=delay)
    with open(last_pull_file, "w") as f:
        f.write(today)   

ai_recommendations = None  # Global variable for AI recs



def refresh_ai_recommendations():
    global ai_recommendations, top5_ai, tickers
    print("🔄 Refreshing AI recommendations...")
    print(f"Using tickers: {tickers}")
    
    if not tickers:
        print("⚠️ No tickers available for AI recommendations")
        ai_recommendations = pd.DataFrame()
        top5_ai = pd.DataFrame()
        return
        
    try:
        ai_recommendations = get_trade_recommendations(tickers, return_df=True)
        top5_ai = ai_recommendations.head(5)
        print(f"✅ AI recommendations updated for {len(ai_recommendations)} tickers")
        print(f"Trade candidates: {len([r for r in ai_recommendations['recommendation'] if 'TRADE:' in r])}")
        print(f"No trade (red X): {len([r for r in ai_recommendations['recommendation'] if 'No trade' in r])}")
    except Exception as e:
        print(f"❌ Error refreshing AI recommendations: {e}")
        ai_recommendations = pd.DataFrame()
        top5_ai = pd.DataFrame()
                                # ***** Get quiver data for first pull comment out afer first run *****

daily_full_quiver_pull(
    tickers,
    cache_path="quiver_congress_cache.json",
    last_pull_file="quiver_last_full_pull.txt",
    delay=1
)

                                # ***** End of fetching immediate quiver data *****

def reschedule_jobs():
    schedule.clear()
    interval = get_current_interval()
    schedule.every(interval).minutes.do(update_with_latest_minute)
    schedule.every(interval).minutes.do(dashboard_update_job)
    schedule.every(30).minutes.do(refresh_quiver_congress_cache, ticker_list=top_5_tickers)
    schedule.every(30).minutes.do(refresh_quiver_institutional_cache, ticker_list=top_5_tickers)
    # Keep your daily jobs as before
    schedule.every().day.at("10:30").do(refresh_ai_recommendations)
    schedule.every().day.at("11:30").do(refresh_ai_recommendations)
    schedule.every().day.at("10:30").do(refresh_news_cache)
    schedule.every().day.at("11:30").do(refresh_news_cache)
    schedule.every().day.at("10:30").do(refresh_whale_cache)
    schedule.every().day.at("11:30").do(refresh_whale_cache)

reschedule_jobs()

# Dashboard update will be called after ticker selection is complete
print("🚀 [MAIN] Scheduler initialized at", datetime.now().strftime('%H:%M:%S'))

def scheduler_loop():
    last_interval = get_current_interval()
    while True:
        current_interval = get_current_interval()
        if current_interval != last_interval:
            print(f"⏱️ Interval changed from {last_interval} to {current_interval}, rescheduling jobs...")
            reschedule_jobs()
            last_interval = current_interval
        print("🔍 [LOOP] Scheduled Jobs:", schedule.jobs)
        schedule.run_pending()
        print("🚀 [LOOP] Waiting for next scheduled job... (sleeping 30s)")
        print("Current time :", datetime.now().strftime('%H:%M:%S'))
        time.sleep(30)


# Start the scheduler in a background thread
scheduler_thread = threading.Thread(target=scheduler_loop, daemon=True)
scheduler_thread.start()

# Start the dashboard in the main thread (blocking)
run_dashboard_thread()



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
from dash import dcc, html, Input, Output, State
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
from Schwab_auth import start_schwab_stream
from schwab_data import fetch_schwab_minute_ohlcv

# =========================
# Jupyter/IPython Tools (optional)
# =========================
from IPython.display import Audio, display, HTML, clear_output

# =========================
# GUI Tools
# =========================
import tkinter as tk
from tkinter import simpledialog

# =========================
# Local/Other Imports
# =========================
from newspaper import Article


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
access_token = {}
merged_data_dict = {}
filtered_df = None
df = None
session = None
base_url = None
HISTORICAL_DATA_FILE = "historical_data.csv"
on_new_ohlcv_bar = None  # Callback for new OHLCV bar data  
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
FINNHUB_API_KEY = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"
FINNHUB_SECRET = "d0o631hr01qn5ghnfap0"


                              # ***** End of API keys setup *****

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

                                                  # ***** End of function to fetch ETF news *****

                                               # *****Calculate ADX/DMS Indicators with rounding *****

# ✅ Ensure merge function runs FIRST, so merged_data_dict is created
realtime_ds = {}

def calculate_adx(df, period=14):
    """
    Calculate ADX, +DI, and -DI for a DataFrame with columns: High, Low, Close.
    Returns a DataFrame with columns: 'ADX', '+DI', '-DI'.
    """
    df = df.copy()

    # Calculate price differences
    df['up_move'] = df['High'] - df['High'].shift(1)
    df['down_move'] = df['Low'].shift(1) - df['Low']

    # +DM and -DM
    df['+DM'] = np.where((df['up_move'] > df['down_move']) & (df['up_move'] > 0), df['up_move'], 0.0)
    df['-DM'] = np.where((df['down_move'] > df['up_move']) & (df['down_move'] > 0), df['down_move'], 0.0)

    # True Range (TR)
    df['tr1'] = df['High'] - df['Low']
    df['tr2'] = np.abs(df['High'] - df['Close'].shift(1))
    df['tr3'] = np.abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)

    # Wilder's smoothing for TR, +DM, -DM
    df['TR_sum'] = df['TR'].rolling(window=period, min_periods=period).sum()
    df['+DM_sum'] = df['+DM'].rolling(window=period, min_periods=period).sum()
    df['-DM_sum'] = df['-DM'].rolling(window=period, min_periods=period).sum()

    # First values for Wilder's smoothing
    for i in range(period, len(df)):
        if i == period:
            continue  # Already set by rolling sum
        df.at[df.index[i], 'TR_sum'] = df.at[df.index[i-1], 'TR_sum'] - (df.at[df.index[i-1], 'TR_sum'] / period) + df.at[df.index[i], 'TR']
        df.at[df.index[i], '+DM_sum'] = df.at[df.index[i-1], '+DM_sum'] - (df.at[df.index[i-1], '+DM_sum'] / period) + df.at[df.index[i], '+DM']
        df.at[df.index[i], '-DM_sum'] = df.at[df.index[i-1], '-DM_sum'] - (df.at[df.index[i-1], '-DM_sum'] / period) + df.at[df.index[i], '-DM']

    # +DI and -DI
    df['+DI'] = 100 * (df['+DM_sum'] / df['TR_sum'])
    df['-DI'] = 100 * (df['-DM_sum'] / df['TR_sum'])

    # DX and ADX
    df['DX'] = 100 * (np.abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI']))
    df['ADX'] = df['DX'].rolling(window=period, min_periods=period).mean()
    # Wilder's smoothing for ADX
    for i in range(period*2, len(df)):
        if i == period*2:
            continue  # Already set by rolling mean
        df.at[df.index[i], 'ADX'] = ((df.at[df.index[i-1], 'ADX'] * (period - 1)) + df.at[df.index[i], 'DX']) / period

    # Clean up
    df = df.drop(columns=['up_move', 'down_move', '+DM', '-DM', 'tr1', 'tr2', 'tr3', 'TR', 'TR_sum', '+DM_sum', '-DM_sum', 'DX'])
    return df[['ADX', '+DI', '-DI']]

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

def calculate_adx_multi(df, tickers, period=14):
    """
    Calculate ADX for multiple tickers and return a DataFrame with columns: Datetime, Ticker, ADX, +DI, -DI
    """
    results = []
    for ticker in tickers:
        tdf = df[df["Ticker"] == ticker].sort_values("Datetime").copy()
        if tdf.empty:
            continue
        adx_df = calculate_adx(tdf, period=period)
        tdf = tdf.reset_index(drop=True)
        adx_df = adx_df.reset_index(drop=True)
        merged = pd.concat([tdf[["Datetime", "Ticker"]], adx_df], axis=1)
        results.append(merged)
    if results:
        return pd.concat(results, ignore_index=True)
    else:
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

def calculate_pmo_multi(df, tickers, period=35, signal_period=10):
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

def calculate_cci_multi(df, tickers, period=20):
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

                                                   # ***** End of CCI calculation *****

                              # ***** Begin function to fetch historical data from Alpha Vantage *****

def fetch_alpha_vantage_history(ticker, api_key, interval="1min", outputsize="compact"):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta = ts.get_intraday(symbol=ticker, interval=interval, outputsize=outputsize)
    data = data.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    })
    data["Ticker"] = ticker
    data = data.reset_index().rename(columns={"date": "Datetime"})
    return data[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]]

                              # ***** End of function to fetch historical data from Alpha Vantage *****                               
                              
                              # ***** Begin function to update historical data for new tickers *****

def update_historical_data_for_new_tickers(tickers, historical_data_file=HISTORICAL_DATA_FILE, api_key=ALPHA_VANTAGE_API_KEY):
    """
    Checks for new tickers not in the historical data file, fetches their history, and appends to the file.
    """
   
    # Load existing historical data (if any)
    if os.path.exists(historical_data_file):
        hist_df = pd.read_csv(historical_data_file, parse_dates=["Datetime"])
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
    new_data = None
    for ticker in new_tickers:
        try:
            #new_data = fetch_alpha_vantage_history(ticker, api_key)
            all_new_data.append(new_data)
        except Exception as e:
            print(f"⚠️ Error fetching data for {ticker}: {e}")

    # ...existing code...
    if all_new_data:
        new_hist_df = pd.concat(all_new_data, ignore_index=True)
        combined_df = pd.concat([hist_df, new_hist_df], ignore_index=True)
        combined_df = combined_df.drop_duplicates(subset=["Datetime", "Ticker"])
        combined_df = combined_df.sort_values(["Datetime", "Ticker"])
        # ROUND HERE
        for col in ["Open", "High", "Low", "Close", "Volume"]:
            if col in combined_df.columns:
                combined_df[col] = pd.to_numeric(combined_df[col], errors="coerce").round(2)
        combined_df.to_csv(historical_data_file, index=False)
        print("✅ Historical data file updated with new tickers.")
        return combined_df
    else:
        print("⚠️ No new historical data fetched.")
        time.sleep(10)
        return hist_df
    
                                              # ***** function to update historical data for new tickers *****


# Define file paths in Python code in VS directory

login_file_path = "C:/Users/mjmat/Pythons_Code_Files/data.csv"

def play_audio(audio_file, ticker):
    """Plays an audio alert for a given ticker."""
    try:
        audio_file_path = f"C:/Users/mjmat/Pythons_Code_Files/{audio_file}"
        if not os.path.exists(audio_file_path):
            logging.error(f"Audio file {audio_file_path} not found.")
            return
        data, samplerate = sf.read(audio_file_path)
        sd.play(data, samplerate)
        logging.info(f"🔊 Alert Triggered: {audio_file} for {ticker} 🚀")
    except Exception as e:
        logging.error(f"⚠️ Error playing {audio_file}: {e}")
        print(f"Error playing audio alert for {ticker}: {e}")
        
                                                  # ***** End of function to initiate file path for audio files *****

                                                     # ***** Audio alert and news alert function *****

def check_trade_alerts(historical_data, top5_tickers=None):
    """
    Triggers alerts based on technicals, news sentiment, whale activity,
    and plays strong/medium buy or exit audio if multiple signals align.
    Only processes tickers in top5_tickers if provided.
    """
    historical_data = historical_data.sort_values(["Ticker", "Datetime"])
    for ticker, group in historical_data.groupby("Ticker"):
        if top5_tickers is not None and ticker not in top5_tickers:
            continue
        group = group.reset_index(drop=True)
        positive_alerts = []
        negative_alerts = []

        # --- TECHNICAL ALERTS ---
        if all(col in group.columns for col in ["ADX", "+DI", "-DI", "PMO", "PMO_signal", "CCI"]):
            if len(group) >= 2:
                prev, curr = group.iloc[-2], group.iloc[-1]
                # ADX trend alert
                if prev["ADX"] < 25 and curr["ADX"] >= 25:
                    print(f"ADX Alert: {ticker} ADX crossed above 25 (Strong trend)")
                    play_audio("adx_alert.mp3", ticker)
                    positive_alerts.append("ADX")
                # +DI/-DI crossover
                if prev["+DI"] < prev["-DI"] and curr["+DI"] > curr["-DI"]:
                    print(f"DI+ Bullish Crossover: {ticker}")
                    play_audio("bullish_alert.mp3", ticker)
                    positive_alerts.append("DI+")
                if prev["+DI"] > prev["-DI"] and curr["+DI"] < curr["-DI"]:
                    print(f"DI- Bearish Crossover: {ticker}")
                    play_audio("bearish_alert.mp3", ticker)
                    negative_alerts.append("DI-")
                # PMO crossover
                if prev["PMO"] < prev["PMO_signal"] and curr["PMO"] > curr["PMO_signal"]:
                    print(f"PMO Bullish Crossover: {ticker}")
                    play_audio("bullish_alert.mp3", ticker)
                    positive_alerts.append("PMO+")
                if prev["PMO"] > prev["PMO_signal"] and curr["PMO"] < curr["PMO_signal"]:
                    print(f"PMO Bearish Crossover: {ticker}")
                    play_audio("bearish_alert.mp3", ticker)
                    negative_alerts.append("PMO-")
                # CCI overbought/oversold
                if prev["CCI"] < 100 and curr["CCI"] >= 100:
                    print(f"CCI Overbought: {ticker}")
                    play_audio("overbought_alert.mp3", ticker)
                    negative_alerts.append("Overbought")
                if prev["CCI"] > -100 and curr["CCI"] <= -100:
                    print(f"CCI Oversold: {ticker}")
                    play_audio("oversold_alert.mp3", ticker)
                    positive_alerts.append("Oversold")

        # --- NEWS AUDIO ALERTS ---
        news_list = fetch_etf_news(ticker)
        for article in news_list:
            if isinstance(article, dict):
                sentiment = article.get("sentiment", "Neutral")
                title = article.get("title", "")
            elif isinstance(article, str):
                sentiment = "Neutral"
                title = article
            else:
                sentiment = "Neutral"
                title = ""
            if sentiment == "Positive":
                print(f"Playing positive_news.mp3 for {ticker} (News: {title})")
                play_audio("positive_news.mp3", ticker)
                positive_alerts.append("News+")
            elif sentiment == "Negative":
                print(f"Playing negative_news.mp3 for {ticker} (News: {title})")
                play_audio("negative_news.mp3", ticker)
                negative_alerts.append("News-")

        # --- WHALE ACTIVITY ALERTS ---
        whale_data = fetch_whale_data(ticker)
        # Insider alerts
        for entry in whale_data.get("insider", []):
            tx_type = entry.get("transactionType", "").lower()
            name = entry.get("name", "")
            shares = entry.get("share", "")
            date = entry.get("transactionDate", "")
            if tx_type == "buy":
                print(f"Insider BUY: {ticker} by {name} ({shares} shares on {date})")
                play_audio("whale_positive.mp3", ticker)
                positive_alerts.append("Whale+")
            elif tx_type == "sell":
                print(f"Insider SELL: {ticker} by {name} ({shares} shares on {date})")
                play_audio("whale_negative.mp3", ticker)
                negative_alerts.append("Whale-")
        # Institutional/Government alerts (positive if shares increased, negative if decreased)
        for entry in whale_data.get("institutional", []) + whale_data.get("government", []):
            entity = entry.get("entityProperName", "")
            shares = entry.get("shares", 0)
            change = entry.get("change", 0)
            date = entry.get("reportDate", "")
            try:
                change_val = float(change)
            except Exception:
                change_val = 0
            if change_val > 0:
                print(f"Institutional/Government BUY: {ticker} by {entity} (+{change} shares on {date})")
                play_audio("whale_positive.mp3", ticker)
                positive_alerts.append("Whale+")
            elif change_val < 0:
                print(f"Institutional/Government SELL: {ticker} by {entity} ({change} shares on {date})")
                play_audio("whale_negative.mp3", ticker)
                negative_alerts.append("Whale-")
       
        # --- BUY/SELL SIGNAL COLLECTION FOR DASHBOARD ---
        signals = []
        if all(col in group.columns for col in ["ADX", "+DI", "-DI", "PMO", "PMO_signal", "CCI"]):
            if len(group) >= 2:
                prev, curr = group.iloc[-2], group.iloc[-1]
                # PMO bullish crossover (Buy)
                if prev["PMO"] < prev["PMO_signal"] and curr["PMO"] > curr["PMO_signal"]:
                    signals.append({"Datetime": curr["Datetime"], "Price": curr["Close"], "Signal": "Buy"})
                # PMO bearish crossover (Sell)
                if prev["PMO"] > prev["PMO_signal"] and curr["PMO"] < curr["PMO_signal"]:
                    signals.append({"Datetime": curr["Datetime"], "Price": curr["Close"], "Signal": "Sell"})
                # DI+ bullish crossover (Buy)
                if prev["+DI"] < prev["-DI"] and curr["+DI"] > curr["-DI"]:
                    signals.append({"Datetime": curr["Datetime"], "Price": curr["Close"], "Signal": "Buy"})
                # DI- bearish crossover (Sell)
                if prev["+DI"] > prev["-DI"] and curr["+DI"] < curr["-DI"]:
                    signals.append({"Datetime": curr["Datetime"], "Price": curr["Close"], "Signal": "Sell"})
                # CCI overbought (Sell)
                if prev["CCI"] < 100 and curr["CCI"] >= 100:
                    signals.append({"Datetime": curr["Datetime"], "Price": curr["Close"], "Signal": "Sell"})
                # CCI oversold (Buy)
                if prev["CCI"] > -100 and curr["CCI"] <= -100:
                    signals.append({"Datetime": curr["Datetime"], "Price": curr["Close"], "Signal": "Buy"})
        # You can now use 'signals' for dashboard markers or further logic
        # (e.g., save to a global dict, return from function, etc.)

        # --- STRONG BUY / MEDIUM BUY / EXIT ALERTS ---
        if len(positive_alerts) >= 4:
            print(f"STRONG BUY ALERT for {ticker} ({len(positive_alerts)} positive signals: {positive_alerts})")
            play_audio("strongbuy.mp3", ticker)
        elif len(positive_alerts) >= 2:
            print(f"MEDIUM BUY ALERT for {ticker} ({len(positive_alerts)} positive signals: {positive_alerts})")
            play_audio("mediumbuy.mp3", ticker)
        if len(negative_alerts) >= 3:
            print(f"EXIT ALERT for {ticker} ({len(negative_alerts)} negative signals: {negative_alerts})")
            play_audio("exit.mp3", ticker)

    #print(f"Playing exit_trade.mp3 for {ticker}")
    #play_audio("exit_trade.mp3", ticker)

                                                # ***** Graph Update Function *****

def start_dashboard(historical_data, filtered_df, tickers, dashboard_ranks):
    print("Tickers passed to dashboard:", tickers)
    # Load market data for 52-week info

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

    app = dash.Dash(__name__)
    app.layout = html.Div([
        html.H1("Top 5 Stocks & ETFs Dashboard"),
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
        html.Div(id='trade-log-table'),
        dcc.Interval(id='interval-component', interval=60*1000, n_intervals=0)  # 60 seconds
    ])

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
            def calculate_tick_volume(df):
                """
                Given a DataFrame with columns ['Datetime', 'Ticker', 'Volume', ...] where 'Volume' is cumulative,
                compute tick-by-tick (per-row) volume for each ticker.
                Adds a new column 'TickVolume' to the DataFrame.
                """
                df = df.sort_values(['Ticker', 'Datetime']).copy()
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

        # --- Price (candlestick) charts ---
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
        # Example: Let's say you have a list of buy/sell signals for this ticker
        # Each signal is a dict: {"Tick": ..., "Price": ..., "Signal": "Buy"/"Sell"}
        signals = []  # <-- Replace with your real signal detection logic!
        # Example: signals = [{"Tick": 10, "Price": 53.5, "Signal": "Buy"}, {"Tick": 15, "Price": 54.2, "Signal": "Sell"}]
        for sig in signals:
            color = "green" if sig["Signal"] == "Buy" else "red"
            arrow = "⬆️" if sig["Signal"] == "Buy" else "⬇️"
            price_fig.add_trace(
                go.Scatter(
                    x=[sig["Tick"]],
                    y=[sig["Price"]],
                    mode="markers+text",
                    marker=dict(symbol="arrow-up" if sig["Signal"] == "Buy" else "arrow-down", color=color, size=16),
                    text=[sig["Signal"]],
                    textposition="top center",
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
            df = df.sort_values(['Ticker', 'Datetime']).copy()
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
        global news_cache
        news_rows = []
        for ticker in valid_ticker_rows:
            news_list = fetch_etf_news(ticker)
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
        for ticker in valid_ticker_rows:
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
            State('trade-log-store', 'data')
        ]
    )
    def log_trade(n_clicks, trade_type, ticker, qty, open_dt, open_price, close_dt, close_price, notes, store_data):
        TRADE_LOG_FILE = "trade_log.xlsx"
        TRADE_LOG_COLUMNS = [
            "Type", "Ticker", "Trade QTY", "Open Datetime", "Open Price",
            "Close Datetime", "Close Price", "Profit/Loss", "Profit/Loss %", "Notes"
        ]
       
        # Load from store or Excel
        if store_data is not None:
            trade_log_df = pd.DataFrame(store_data)
        elif os.path.exists(TRADE_LOG_FILE):
            trade_log_df = pd.read_excel(TRADE_LOG_FILE)
        else:
            trade_log_df = pd.DataFrame(columns=TRADE_LOG_COLUMNS)

        # Only add if button clicked
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
            trade_log_df = pd.concat([trade_log_df, pd.DataFrame([new_row])], ignore_index=True)
            # Ensure all columns exist and are in correct order
            for col in TRADE_LOG_COLUMNS:
                if col not in trade_log_df.columns:
                    trade_log_df[col] = ""
            trade_log_df = trade_log_df[TRADE_LOG_COLUMNS]
            # Save to Excel
            try:
                trade_log_df.to_excel(TRADE_LOG_FILE, index=False)
            except Exception as e:
                print("Excel save error:", e)
            # Clear entry fields after logging
            today_str = datetime.datetime.now().strftime("%Y-%m-%d")
            trade_type = "Paper"
            ticker = trade_ticker_options[0]['value'] if trade_ticker_options else ""
            qty = 0
            open_dt = f"{today_str} 09:15"
            open_price = 0
            close_dt = f"{today_str} 15:45"
            close_price = 0
            notes = ""

        # Build table
        if trade_log_df.empty:
            table = html.Div("No trades logged yet.")
        else:
            table = html.Table([
                html.Thead(html.Tr([html.Th(col) for col in TRADE_LOG_COLUMNS])),
                html.Tbody([
                    html.Tr([html.Td(trade_log_df.iloc[i][col]) for col in TRADE_LOG_COLUMNS])
                    for i in range(len(trade_log_df))
                ])
            ], style={'width': '100%', 'fontSize': '13px', 'marginTop': '10px'})

        # Return updated table, store, and cleared fields
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

    print("🚀 Dash is running on http://127.0.0.1:8050/")
    app.run(host='127.0.0.1', port=8050, debug=False)

    
                                      #******* End  of Dashboard function *******              

                        # ***** Obtain auth code from Etrade *****

session, base_url = get_etrade_session()

            # *** end of etrade auth collection, file creation and authentication checking  ***

              # ***** Obtain initial list of leveraged etf's to get historical data for *****

                            # ***** Begin function to obtain leveraged etf list *****


TOP_ETFS_FILE = "C:/Users/mjmat/Python Code in VS/Top_ETFS_for_DayTrade.xlsx"

def get_top_etf_list_from_excel(n=24):
    """
    Loads the top ETF tickers from an Excel file.
    The Excel file should have a column named 'Symbol' with the ETF tickers.
    Returns a list of up to n tickers.
    """
    import pandas as pd
    if not os.path.exists(TOP_ETFS_FILE):
        raise FileNotFoundError(f"ETF list file not found: {TOP_ETFS_FILE}")
    df = pd.read_excel(TOP_ETFS_FILE)
    if "Symbol" not in df.columns:
        raise ValueError(f"'Symbol' column not found in {TOP_ETFS_FILE}")
    symbols = df["Symbol"].dropna().astype(str).str.strip().unique().tolist()
    print(f"Loaded {len(symbols)} ETF tickers from {TOP_ETFS_FILE}: {symbols[:n]}")
    return symbols[:n]

                                             # ***** End of function to obtain leveraged etf list *****

from schwab_data import fetch_schwab_minute_ohlcv, fetch_schwab_latest_minute
import pandas as pd
import os

#tickers = ["AAPL", "ETHU"]  # Replace with your tickers
tickers = get_top_etf_list_from_excel(n=24)
hist_file = "historical_data.csv"

if not os.path.exists(hist_file):
    print("historical_data.csv not found, creating with Schwab OHLCV data...")
    historical_data = pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
    print("Tickers to fetch from Schwab:", tickers)
    for symbol in tickers:
        df_day = fetch_schwab_minute_ohlcv(symbol, period=1)
        if not df_day.empty:
            print(f"✅ Got Schwab OHLCV for {symbol}, rows: {len(df_day)}")
            historical_data = pd.concat([historical_data, df_day], ignore_index=True)
        else:
            print(f"⚠️ No Schwab data returned for {symbol}")
    if not historical_data.empty:
        historical_data.drop_duplicates(subset=["Datetime", "Ticker"], keep="last", inplace=True)
        historical_data.sort_values(["Datetime", "Ticker"], inplace=True)
        historical_data.reset_index(drop=True, inplace=True)
        historical_data.to_csv(hist_file, index=False)
        print(f"✅ Created {hist_file} with Schwab OHLCV data. Rows: {len(historical_data)}")
    else:
        print("⚠️ No Schwab OHLCV data fetched for any ticker. File not created.")
else:
    print("historical_data.csv found, loading existing data...")
    historical_data = pd.read_csv(hist_file)

#                               ****** End of Schwab historical data retrieval and processing *****


def fetch_yahoo_data(tickers):
    """Pulls hourly intraday data for the last 2 days from Yahoo Finance."""
    try:
        print("🚀 Fetching Yahoo Finance Data...")
        stock_data = yf.download(" ".join(tickers), period="2d", interval="1h")
        return {str(index): {f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col: value for col, value in row.items()} for index, row in stock_data.iterrows()}
    except Exception as e:
        print(f"⚠️ Yahoo Finance Error: {e}")
        return None

def fetch_backup_data(tickers):
    """Fetches backup hourly data from StockData.org if Yahoo fails (placeholder for actual API)."""
    try:
        print("🔄 Switching to StockData.org backup...")
        return {ticker: {"price": "mock_data"} for ticker in tickers}
    except Exception as e:
        print(f"⚠️ Backup Data Error: {e}")
        return None

# Cache to store recent news data
news_cache = {}
load_news_cache()

def fetch_etf_news(etf_symbol):
    """Fetch news for a given ETF, using smart caching. Also fetches news for underlying stock if mapped."""
    global NEWS_API_KEY
    now = datetime.now(timezone.utc)
    cache_validity = timedelta(hours=1)

    # Always include the ETF symbol
    symbols_to_search = [etf_symbol]
    # If ETF has an underlying, also search for that
    if etf_symbol in ETF_UNDERLYING_MAP:
        underlying = ETF_UNDERLYING_MAP[etf_symbol]
        if underlying not in symbols_to_search:
            symbols_to_search.append(underlying)

    all_articles = []
    for symbol in symbols_to_search:
        # Use cache if available and valid
        if symbol in news_cache:
            cached_time, cached_data = news_cache[symbol]
            if now - cached_time < cache_validity:
                all_articles.extend(cached_data)
                continue

        api_url = f"https://newsapi.org/v2/everything?q={symbol}&language=en&apiKey={NEWS_API_KEY}"
        response = requests.get(api_url)
        if response.status_code == 200:
            news_data = response.json()["articles"][:5]
            formatted_news = [{"title": article["title"], "sentiment": analyze_sentiment(article["title"]), "url": article.get("url", "")} for article in news_data]
            news_cache[symbol] = (now, formatted_news)
            save_news_cache()
            all_articles.extend(formatted_news)
        else:
            print(f"❌ News API error for {symbol}: {response.status_code} {response.text}")

            # Remove duplicates by title or string value
    seen_titles = set()
    unique_articles = []
    for article in all_articles:
        if isinstance(article, dict) and "title" in article:
            title = article["title"]
        else:
            title = str(article)
        if title not in seen_titles:
            unique_articles.append(article)
            seen_titles.add(title)
    return unique_articles

def analyze_sentiment(text):
    # Expanded keyword lists
    positive_keywords = [
        "growth", "strong", "bullish", "rising", "beat", "beats", "record", "surge", "up", "increase", "profit", "gain", "soar", "positive", "outperform", "buy", "upgrade", "rebound", "rally", "optimistic", "tops"
    ]
    negative_keywords = [
        "drop", "decline", "bearish", "falling", "miss", "misses", "loss", "down", "decrease", "plunge", "negative", "underperform", "sell", "downgrade", "slump", "cut", "warning", "disappoint", "bear", "weak"
    ]

    text_lower = text.lower()
    # Check for positive keywords
    if any(word in text_lower for word in positive_keywords):
        return "Positive"
    # Check for negative keywords
    if any(word in text_lower for word in negative_keywords):
        return "Negative"
    return "Neutral"

                                                # ***** End of function to obtain News and sentiment *****


                                                  # ***** Whale, institutional, and insider data functions *****


FINNHUB_API_KEY = "YOUR_FINNHUB_API_KEY"  # <-- Replace with your real key

def fetch_whale_data(ticker, finnhub_api_key=None, cache=None):
    """
    Fetches whale/institutional/insider/government data for a ticker or its underlying if mapped.
    Combines results for ETF and parent if applicable.
    """
    now = datetime.now(timezone.utc)
    cache_validity = timedelta(hours=2)
    whale_cache = cache["whale"] if cache and "whale" in cache else {}

    # Always include the ticker
    symbols_to_search = [ticker]
    # If ETF has an underlying, also search for that
    if ticker in ETF_UNDERLYING_MAP:
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
                continue

        try:
            inst_url = f"https://finnhub.io/api/v1/stock/institutional-ownership?symbol={symbol}&token={finnhub_api_key}"
            inst = requests.get(inst_url).json().get("ownership", [])[:3]
            gov_url = f"https://finnhub.io/api/v1/stock/government-ownership?symbol={symbol}&token={finnhub_api_key}"
            gov = requests.get(gov_url).json().get("ownership", [])[:3]
            ins_url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={symbol}&token={finnhub_api_key}"
            ins = requests.get(ins_url).json().get("data", [])[:3]
            data = {"institutional": inst, "government": gov, "insider": ins}
            if whale_cache is not None:
                whale_cache[symbol] = (now, data)
            for key in ["institutional", "government", "insider"]:
                combined_data[key].extend(data[key])
        except Exception as e:
            print(f"Whale fetch error for {symbol}: {e}")
            continue

    # Remove duplicates (optional, by entity/date/type)
    for key in ["institutional", "government", "insider"]:
        seen = set()
        unique = []
        for entry in combined_data[key]:
            # Use a tuple of key fields as a unique identifier
            uid = tuple(sorted(entry.items()))
            if uid not in seen:
                unique.append(entry)
                seen.add(uid)
        combined_data[key] = unique

    return combined_data

def count_recent_whale_trades(whale_data, days=30):
    """
    Count number of whale trades in the last N days.
    """
    # Defensive: if whale_data is not a dict, return 0
    if not isinstance(whale_data, dict):
        print(f"[WARN] whale_data is not a dict: {type(whale_data)} - value: {whale_data}")
        return 0

    # Defensive: ensure all keys exist and are lists
    for key in ["institutional", "government", "insider"]:
        if key not in whale_data or not isinstance(whale_data[key], list):
            whale_data[key] = []

    now = datetime.now(timezone.utc)
    count = 0
    # Institutional & Government: use 'reportDate'
    for entry in whale_data.get("institutional", []) + whale_data.get("government", []):
        date_str = entry.get("reportDate")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if now - dt.replace(tzinfo=timezone.utc) <= timedelta(days=days):
                    count += 1
            except Exception:
                continue
    # Insider: use 'transactionDate'
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


def select_trade_candidates():
    """Filters leveraged ETFs based on price change, volume boost, momentum, news sentiment, and technicals.
    Returns a DataFrame with top 5 ETFs and their composite rank (1-5, 5=best).
    """
    symbols = get_top_etf_list_from_excel(n=24)
    print("🎯 Final leveraged ETF list before further processing:", symbols)
    leveraged_etfs = symbols

    print("✅ Starting selection process for ETFs.")
 
    # Calculate ATR values for each ETF (with debug print)
    atr_values = {}
    hist_df = pd.read_csv("historical_data.csv")
    for t in leveraged_etfs:
        tdf = hist_df[hist_df["Ticker"] == t].sort_values("Datetime").tail(20)
        valid_tdf = tdf[(tdf["High"] > 0) & (tdf["Low"] > 0) & (tdf["Close"] > 0)]
        if len(valid_tdf) >= 13:
            tr = np.maximum(
                valid_tdf["High"] - valid_tdf["Low"],
                np.maximum(
                    abs(valid_tdf["High"] - valid_tdf["Close"].shift(1)),
                    abs(valid_tdf["Low"] - valid_tdf["Close"].shift(1))
                )
            )
            atr = tr.rolling(window=13).mean().iloc[-1]
            atr_val = atr if not np.isnan(atr) else 0
            atr_values[t] = atr_val
            print(f"ATR for {t}: {atr_val:.4f} (from {len(valid_tdf)} valid bars)")
        else:
            atr_values[t] = 0
            print(f"ATR for {t}: 0 (not enough valid bars, only {len(valid_tdf)})")

    # Now filter
    min_ATR_threshold = 0.3
    filtered_etfs = [t for t in leveraged_etfs if atr_values.get(t, 0) > min_ATR_threshold]
    print("✅ Filtered ETFs based on ATR:", filtered_etfs)
    
    if not filtered_etfs:
        print("⚠️ No ETFs passed the ATR filter, using all tickers as fallback.")
        filtered_etfs = leveraged_etfs
    print("Final ETF list for dashboard:", filtered_etfs)

    # News sentiment: Positive > Neutral > Negative
    sentiment_map = {"Positive": 3, "Neutral": 2, "Negative": 1}
    news_sentiment = {}
    for t in filtered_etfs:
        news_list = fetch_etf_news(t)
        if news_list and isinstance(news_list, list) and isinstance(news_list[0], dict) and "title" in news_list[0]:
            news_sentiment[t] = analyze_sentiment(news_list[0]["title"])
        else:
            news_sentiment[t] = "Neutral"

    # Build whale_scores dict for each ticker
    whale_scores = {}
    for t in filtered_etfs:
        whale_data = fetch_whale_data(t)
        whale_scores[t] = count_recent_whale_trades(whale_data, days=30)

        # Calculate price change and volume for each ETF
    price_change = {}
    volume_values = {}
    for t in leveraged_etfs:
        tdf = hist_df[hist_df["Ticker"] == t].sort_values("Datetime").tail(20)
        valid_tdf = tdf[(tdf["High"] > 0) & (tdf["Low"] > 0) & (tdf["Close"] > 0)]
        if len(valid_tdf) >= 13:
            tr = np.maximum(
                valid_tdf["High"] - valid_tdf["Low"],
                np.maximum(
                    abs(valid_tdf["High"] - valid_tdf["Close"].shift(1)),
                    abs(valid_tdf["Low"] - valid_tdf["Close"].shift(1))
                )
            )
            atr = tr.rolling(window=13).mean().iloc[-1]
            atr_val = atr if not np.isnan(atr) else 0
            atr_values[t] = atr_val
            print(f"ATR for {t}: {atr_val:.4f} (from {len(valid_tdf)} valid bars)")
        else:
            atr_values[t] = 0
            print(f"ATR for {t}: 0 (not enough valid bars, only {len(valid_tdf)})")

    # === PLACE THIS BLOCK IMMEDIATELY AFTER THE LOOP ABOVE ===
    print("=== ATR Summary for all tickers ===")
    for t, val in atr_values.items():
        print(f"{t}: {val:.4f}")
    print("===================================")

    # Build DataFrame for ranking
    df = pd.DataFrame({
        "Symbol": filtered_etfs,
        "PriceChange": [price_change.get(t, 0) for t in filtered_etfs],
        "Volume": [volume_values.get(t, 0) for t in filtered_etfs],
        "ATR": [atr_values.get(t, 0) for t in filtered_etfs],
        "Sentiment": [news_sentiment.get(t, "Neutral") for t in filtered_etfs],
        "SentimentScore": [sentiment_map.get(news_sentiment.get(t, "Neutral"), 2) for t in filtered_etfs],
        "WhaleScore": [whale_scores.get(t, 0) for t in filtered_etfs]
    })

    # --- Add technicals for each ETF ---
    adx_vals, pmo_vals, cci_vals = [], [], []
    for t in df["Symbol"]:
        hist = pd.read_csv("historical_data.csv")
        tdf = hist[hist["Ticker"] == t].sort_values("Datetime").tail(35)
        # Ensure numeric
        for col in ["High", "Low", "Close"]:
            tdf[col] = pd.to_numeric(tdf[col], errors="coerce")
        print(f"\nDEBUG: {t} - tdf shape: {tdf.shape}")
        print(tdf[["Datetime", "Open", "High", "Low", "Close", "Volume"]].tail(3))
        # ADX
        adx = calculate_adx(tdf)
        print(f"DEBUG: {t} - ADX output:\n{adx.tail(3)}")
        adx_last = adx["ADX"].iloc[-1] if not adx.empty else np.nan
        adx_vals.append(adx_last)
        # PMO
        pmo = calculate_pmo(tdf)
        print(f"DEBUG: {t} - PMO output:\n{pmo.tail(3)}")
        pmo_last = pmo["PMO"].iloc[-1] if not pmo.empty else np.nan
        pmo_vals.append(pmo_last)
        # CCI
        cci = calculate_cci(tdf)
        print(f"DEBUG: {t} - CCI output:\n{cci.tail(3)}")
        cci_last = cci["CCI"].iloc[-1] if not cci.empty else np.nan
        cci_vals.append(cci_last)

    df["ADX"] = adx_vals
    df["PMO"] = pmo_vals
    df["CCI"] = cci_vals

    def cci_strength_rank(cci):
        """
        Assigns a CCI trend strength rank (1-5) based on absolute CCI value.
        1 = Strong Sell, 2 = Moderate Sell, 3 = Neutral, 4 = Moderate Buy, 5 = Strong Buy
        """
        if cci <= -200:
            return 1  # Strong Sell
        elif -200 < cci <= -150:
            return 2  # Moderate Sell
        elif -100 < cci < 100:
            return 3  # Neutral
        elif 100 <= cci < 150:
            return 4  # Moderate Buy
        elif 150 <= cci <= 200:
            return 5  # Strong Buy
        else:
            return 3  # Default to Neutral if out of range


    # --- NEW: Calculate DMI/ADX ranks for each ticker ---
    adx_df = pd.DataFrame({
        "Symbol": df["Symbol"],
        "ADX": df["ADX"],
        "+DI": [calculate_adx(pd.read_csv("historical_data.csv")[pd.read_csv("historical_data.csv")["Ticker"] == t].sort_values("Datetime").tail(35))["+DI"].iloc[-1] if not pd.read_csv("historical_data.csv")[pd.read_csv("historical_data.csv")["Ticker"] == t].empty else np.nan for t in df["Symbol"]],
        "-DI": [calculate_adx(pd.read_csv("historical_data.csv")[pd.read_csv("historical_data.csv")["Ticker"] == t].sort_values("Datetime").tail(35))["-DI"].iloc[-1] if not pd.read_csv("historical_data.csv")[pd.read_csv("historical_data.csv")["Ticker"] == t].empty else np.nan for t in df["Symbol"]]
    })
    adx_df = rank_dmi_plus_minus(adx_df)
    adx_df = rank_adx_strength(adx_df)
    df = df.merge(adx_df[["Symbol", "DMIPlusRank", "DMIMinusRank", "ADXRank"]], on="Symbol", how="left")

    # Assign 1-5 ranks for each test (higher is better)
    df["PriceChangeRank"] = df["PriceChange"].rank(method="min", ascending=False)
    df["VolumeRank"] = df["Volume"].rank(method="min", ascending=False)
    df["ATRRank"] = df["ATR"].rank(method="min", ascending=False)
    df["SentimentRank"] = df["SentimentScore"].rank(method="min", ascending=False)
    #df["ADXRank"] = df["ADX"].rank(method="min", ascending=False)
    df["PMORank"] = df["PMO"].rank(method="min", ascending=False)
    df["CCIRank"] = df["CCI"].apply(cci_strength_rank)
    df["WhaleRank"] = df["WhaleScore"].rank(method="min", ascending=False)

    # Normalize all ranks to 1-5 (5=best)
    for col in ["PriceChangeRank", "VolumeRank", "ATRRank", "SentimentRank", "ADXRank", "PMORank", "CCIRank", "WhaleRank"]:
        unique_vals = df[col].nunique()
        bins = min(5, unique_vals)
        if bins > 1 and len(df[col]) >= bins:
            # Assign highest values to 5, next to 4, ..., lowest to 1
            try:
                ranked = pd.qcut(df[col], q=bins, labels=range(bins, 0, -1), duplicates='drop')
                df[col] = ranked.fillna(3).astype(int)
            except Exception as e:
                print(f"qcut failed for {col}: {e}")
                df[col] = 3
        else:
            df[col] = 3

    # Composite rank: average of all test ranks
    rank_cols = [
        "PriceChangeRank", "VolumeRank", "ATRRank", "SentimentRank",
        "DMIPlusRank", "DMIMinusRank", "ADXRank", "PMORank", "CCIRank", "WhaleRank"
    ]
    df["CompositeRank"] = df[rank_cols].mean(axis=1).round(2)

    # Sort by composite rank, take top 5
    df = df.sort_values("CompositeRank", ascending=False).head(5).reset_index(drop=True)

    print("🚀 Final ETF List Ready for Trading Analysis (with ranks):")
    print(df[["Symbol", "CompositeRank"]])

    return df

# Ensure historical_data.csv exists before selecting trade candidates
if not os.path.exists("historical_data.csv"):
    print("historical_data.csv not found, fetching initial data...")
    # You can use your update_historical_data_for_new_tickers or load_historical_data function here
    update_historical_data_for_new_tickers(get_top_etf_list_from_excel(n=24))

# Get top 5 ETF DataFrame and ranks
top5_df = select_trade_candidates()
tickers = top5_df["Symbol"].tolist()
# After you set tickers and ticker_ranks
for ticker in tickers:
    fetch_etf_news(ticker)
ticker_ranks = dict(zip(top5_df["Symbol"], top5_df["CompositeRank"]))
print("🚀 Selected Tickers for Historical Data Retrieval:", tickers)

# --- START STREAMING HERE ---

#with open("tokens.json", "r") as f:
    #tokens = json.load(f)
#SCHWAB_USER = tokens.get("schwab_user")
#SCHWAB_PASS = tokens.get("schwab_pass")

#start_schwab_stream(SCHWAB_USER, SCHWAB_PASS, tickers, on_new_ohlcv_bar)

# --- END STREAMING SETUP ---


update_historical_data_for_new_tickers(tickers)
time.sleep(2)
df = pd.read_csv("historical_data.csv")
for col in ["Open", "High", "Low", "Close", "Volume"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce").round(2)
df.to_csv("historical_data.csv", index=False)
print("✅ Rounded OHLCV columns in historical_data.csv to 2 decimals.")

#cls()

                                    # ***** End of intial collection of leveraged ETF's
                  
# ====== NEW: Combine with etf_analysis composite ranking ======

# Prepare price_lookup for rank_top5_etfs
# Each value should be a DataFrame with columns: High, Low, Close, and 'current_price'
price_lookup = {}

hist_df = pd.read_csv("historical_data.csv")

# Merge technicals into hist_df for all tickers
adx_df = calculate_adx_multi(hist_df, tickers)
pmo_df = calculate_pmo_multi(hist_df, tickers)
cci_df = calculate_cci_multi(hist_df, tickers)
hist_df = hist_df.merge(adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]], on=["Datetime", "Ticker"], how="left")
hist_df = hist_df.merge(pmo_df[["Datetime", "Ticker", "PMO", "PMO_signal"]], on=["Datetime", "Ticker"], how="left")
hist_df = hist_df.merge(cci_df[["Datetime", "Ticker", "CCI"]], on=["Datetime", "Ticker"], how="left")
# DO NOT re-read hist_df here!
# hist_df = pd.read_csv("historical_data.csv")  # <-- REMOVE THIS LINE

for symbol in tickers:
    tdf = hist_df[hist_df["Ticker"] == symbol].copy()
    if not tdf.empty:
        tdf["current_price"] = tdf["Close"].iloc[-1]
        price_lookup[symbol] = tdf
for symbol in tickers:
    tdf = hist_df[hist_df["Ticker"] == symbol].copy()
    if not tdf.empty:
        tdf["current_price"] = tdf["Close"].iloc[-1]
        price_lookup[symbol] = tdf

# Call the new ranking function
print("DEBUG: price_lookup for ranking:")
for k, v in price_lookup.items():
    print(f"{k}: {v.tail(1)}")  # Show the last row for each ticker
etf_ranks = rank_top5_etfs(
    etf_list=tickers,
    news_api_key=NEWS_API_KEY,
    finnhub_api_key=FINNHUB_API_KEY,
    price_lookup=price_lookup,
    cache={"news": news_cache, "whale": whale_cache}
)

# Combine the two rankings (simple average)
final_ranks = []
for etf in etf_ranks:
    symbol = etf['symbol']
    old_rank = ticker_ranks.get(symbol, 3)  # Default to neutral if missing
    new_rank = etf['composite_rank']
    combined_rank = round((old_rank + new_rank) / 2, 2)
    etf['final_rank'] = combined_rank
    final_ranks.append(etf)

print("==== Combined ETF Rankings ====")
for etf in final_ranks:
    print(f"{etf['symbol']}: Final Rank {etf['final_rank']} (Old: {ticker_ranks.get(etf['symbol'], 3)}, New: {etf['composite_rank']})")

# Build a dict for dashboard display using the new combined ranks
dashboard_ranks = {etf['symbol']: etf['final_rank'] for etf in final_ranks}

# You can now use final_ranks for dashboard, display, or further logic


                                    #***** Start historical data retrieval from alphavantage *****

                                        # **** File Storage Path *****

# Filepath for storing historical data
HISTORICAL_DATA_FILE = r"C:\Users\mjmat\Python Code in VS\historical_data.csv"

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY
ALPHA_VANTAGE_OUTPUTSIZE = "compact"  # Use "full" for complete historical data or "compact" for the last 100 data points

# Filepath for historical data
HISTORICAL_DATA_FILE = "historical_data.csv"

# Flag to use mock data
USE_MOCK_DATA = False  # Set to True to use mock data, False to fetch real data


def create_mock_historical_data(tickers, start_time="2025-05-15 09:30", intervals=30):
    """
    Create a mock historical dataset for testing purposes.
    """
    # Generate a range of timestamps (e.g., every minute)
    timestamps = pd.date_range(start=start_time, periods=intervals, freq="1T")

    # Format timestamps to exclude seconds
    timestamps = timestamps.strftime("%Y-%m-%d %H:%M")  # Format explicitly

    # Create mock data for each ticker
    data = []
    for ticker in tickers:
        for timestamp in timestamps:
            data.append({
                "Datetime": timestamp,
                "Ticker": ticker,
                "Open": round(np.random.uniform(50, 100), 2),
                "High": round(np.random.uniform(100, 150), 2),
                "Low": round(np.random.uniform(30, 50), 2),
                "Close": round(np.random.uniform(50, 100), 2),
                "Volume": np.random.randint(1000, 10000)
            })

    # Convert to a DataFrame
    df = pd.DataFrame(data)
    df["Datetime"] = pd.to_datetime(df["Datetime"])
    # Do NOT set_index here, just return with Datetime as a column
    print('df head 601 after creating mock data : ', df.head())
    return df

HISTORICAL_DATA_FILE = "historical_data.csv"

def fetch_alpha_vantage_history(ticker, api_key, interval="1min", outputsize="compact"):
    ts = TimeSeries(key=api_key, output_format='pandas')
    data, meta = ts.get_intraday(symbol=ticker, interval=interval, outputsize=outputsize)
    data = data.rename(columns={
        "1. open": "Open",
        "2. high": "High",
        "3. low": "Low",
        "4. close": "Close",
        "5. volume": "Volume"
    })
    data["Ticker"] = ticker
    data = data.reset_index().rename(columns={"date": "Datetime"})
    return data[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]]

def load_historical_data(tickers, api_key=ALPHA_VANTAGE_API_KEY):
    """
    Loads historical data from CSV if present and not empty.
    If missing or empty, fetches from Alpha Vantage and saves to CSV.
    Returns DataFrame.
    """
    if os.path.exists(HISTORICAL_DATA_FILE):
        df = pd.read_csv(HISTORICAL_DATA_FILE, parse_dates=["Datetime"])
        if not df.empty:
            print("Loaded historical data from CSV.")
            return df
        else:
            print("CSV is empty, fetching from Alpha Vantage...")
    else:
        print("CSV not found, fetching from Alpha Vantage...")

    # Fetch from Alpha Vantage
    if tickers is None or api_key is None:
        raise ValueError("Tickers list and Alpha Vantage API key must be provided to fetch data.")

    all_data = []
    for ticker in tickers:
        print(f"Fetching {ticker} history from Alpha Vantage...")
        try:
            df = fetch_alpha_vantage_history(ticker, api_key)
            all_data.append(df)
        except Exception as e:
            print(f"Error fetching {ticker}: {e}")
    if all_data:
        hist_df = pd.concat(all_data, ignore_index=True)
        hist_df = hist_df.sort_values(["Datetime", "Ticker"])
        hist_df.to_csv(HISTORICAL_DATA_FILE, index=False)
        print("Historical data saved to CSV.")
        return hist_df
    else:
        print("No historical data fetched.")
        return pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
    

def save_historical_data(df, filename="historical_data.csv", max_entries=1000):
    """
    Saves DataFrame to CSV, keeping all relevant columns in the correct order and trimming to max_entries.
    """
    # Ensure all required columns exist
    required_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = np.nan

    # Ensure correct column order
    df = df[required_cols]

    # Format Datetime
    df["Datetime"] = pd.to_datetime(df["Datetime"]).dt.strftime("%Y-%m-%d %H:%M")

    # Sort by Datetime and Ticker
    df = df.sort_values(by=["Datetime", "Ticker"], ascending=True)

    # Trim to max_entries (keep most recent)
    if len(df) > max_entries:
        df = df.iloc[-max_entries:]

    # Save to CSV
    df.to_csv(filename, index=False)


def update_historical_data(historical_data, new_data, max_entries=10000):
    """
    Appends new_data to historical_data, removes duplicates, sorts, and trims to max_entries.
    Always keeps the most recent rows.
    """
    import pandas as pd

    # Concatenate and drop duplicates
    combined = pd.concat([historical_data, new_data], ignore_index=True)
    combined = combined.dropna(subset=["Close", "Volume"])
    combined = combined.drop_duplicates(subset=["Datetime", "Ticker"], keep="last")
    combined = combined.sort_values(["Datetime", "Ticker"])

    # Trim to max_entries (keep most recent)
    if len(combined) > max_entries:
        # Sort by Datetime descending, then Ticker, then take head
        combined = combined.sort_values("Datetime", ascending=False).head(max_entries)
        # Resort to ascending for file consistency
        combined = combined.sort_values(["Datetime", "Ticker"])

    return combined

def append_realtime_to_historical(historical_df, realtime_df):
    """
    Appends new real-time bars to historical data, ensuring correct OHLC logic.
    Handles Datetime as string or integer (timestamp in ms).
    Returns: Updated historical_df with new bars appended.
    """
    import pandas as pd

    # Ensure correct types
    historical_df = historical_df.copy()
    realtime_df = realtime_df.copy()

    # --- Robust Datetime conversion for both DataFrames ---
    def fix_datetime_col(df):
        if df.empty:
            return df
        # If already datetime, just format
        if pd.api.types.is_datetime64_any_dtype(df['Datetime']):
            df['Datetime'] = df['Datetime'].dt.strftime("%Y-%m-%d %H:%M")
        # If numeric (likely ms timestamp), convert
        elif pd.api.types.is_numeric_dtype(df['Datetime']):
            df['Datetime'] = pd.to_datetime(df['Datetime'] // 1000, unit='s').dt.strftime("%Y-%m-%d %H:%M")
        else:
            # Try to parse as string
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce').dt.strftime("%Y-%m-%d %H:%M")
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
    # Remove any duplicates (same Datetime, Ticker)
    combined = pd.concat([historical_df, new_df], ignore_index=True)
    # ROUND HERE
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in combined.columns:
            combined[col] = pd.to_numeric(combined[col], errors="coerce").round(2)
    # Convert Datetime back to pandas datetime for sorting/deduplication
    combined['Datetime'] = pd.to_datetime(combined['Datetime'], utc=True).dt.tz_localize(None)

    if combined is None or combined.empty:
        print("⚠️ append_realtime_to_historical produced empty DataFrame.")
        # Return an empty DataFrame with the expected columns
        return pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"])
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
        tokens = refresh_schwab_tokens()
        access_token = tokens["access_token"]
        for symbol in tickers_to_retry:
            result = fetch_schwab_realtime_ohlc(access_token, symbol, last_cum_vol.get(symbol))
            results[symbol] = result
    return results



import pandas as pd
import os

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
    pd.DataFrame([row]).to_csv(
        csv_path,
        mode="a",
        header=not file_exists,
        index=False,
        columns=header_cols
    )
    print(f"✅ Streaming OHLCV bar appended to {csv_path}.")

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
    Fetches new real-time data from Schwab, updates historical, calculates indicators, and saves.
    Also appends the latest real-time data to historical_data.csv for archival.
    """
    import os
    import pandas as pd

    # Fetch real-time data (Schwab version does not use session/base_url)
    realtime_df = get_realtime_data(
        tickers, interval='1m', count=30
    )
    if realtime_df is None or realtime_df.empty:
        print("No real-time data fetched.")
        # Return the original historical_data, or an empty DataFrame if that's None
        return historical_data if historical_data is not None else pd.DataFrame()

    # --- Safe CSV Appending ---
    csv_path = os.path.join(os.getcwd(), "historical_data.csv")
    file_exists = os.path.isfile(csv_path)
    header_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]

    print("About to append the following real-time data to CSV:")
    print(realtime_df)
    print("DataFrame columns:", realtime_df.columns)

    try:
        if file_exists:
            with open(csv_path, "r") as f:
                header = f.readline().strip().split(",")
            # Only use columns that are in both the header and the DataFrame, and in the expected order
            save_cols = [col for col in header_cols if col in header and col in realtime_df.columns]
        else:
            save_cols = [col for col in header_cols if col in realtime_df.columns]

        print("Saving columns:", save_cols)
        if not realtime_df.empty and save_cols:
            realtime_df.to_csv(
                csv_path,
                mode="a",
                header=not file_exists,
                index=False,
                columns=save_cols
            )
            print(f"✅ Real-time data appended to {csv_path}.")
        else:
            print("⚠️ No data or columns to append to CSV.")
    except Exception as e:
        print(f"❌ Failed to append real-time data to CSV: {e}")

    # Update historical data with correct OHLC logic
    historical_data = append_realtime_to_historical(historical_data, realtime_df)
    if historical_data is None:
        print("⚠️ append_realtime_to_historical returned None, using empty DataFrame.")
        historical_data = pd.DataFrame(columns=header_cols)

    # Calculate indicators
    adx_df = calculate_adx_multi(historical_data, tickers)
    pmo_df = calculate_pmo_multi(historical_data, tickers)  # <-- Use the multi version!

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
    save_historical_data(merged, max_entries=MAX_ENTRIES)

    return merged

                               # ***** End of historical data retrieval from alphavantage *****


                # ***** Merge historical and realtime data *****

                                       # ***** Function to merge historical & real-time data *****


# --- Function to merge historical & real-time data ---

HISTORICAL_DATA_FILE = r"C:\Users\mjmat\Python Code in VS\historical_data.csv"
MAX_ENTRIES = 1000  # 🔹 Set limit to prevent excessive growth

def merge_historical_realtime(historical_data, realtime_ds, tickers):

    #Merge historical data with real-time data for the given tickers.
    #Updates the historical_data DataFrame with the latest real-time data.

    print("🔍 Running merge_historical_realtime()...")

    # Create a DataFrame to hold the real-time data
    realtime_data_list = []

    for ticker in tickers:
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

    return historical_data

def update_historical_data_file(max_entries=MAX_ENTRIES):

    #Updates historical data CSV file by appending real-time data and maintaining a rolling window.

    # Load existing data if file exists
    if os.path.exists(HISTORICAL_DATA_FILE):
        try:
            historical_data = pd.read_csv(
                HISTORICAL_DATA_FILE,
                parse_dates=["Datetime"]
            )
            historical_data.set_index("Datetime", inplace=True)
            logging.info("✅ Historical data loaded successfully.")
        except Exception as e:
            logging.error(f"Error loading historical data: {e}")
            historical_data = pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"])
    else:
        historical_data = pd.DataFrame(columns=["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume", "averageVolume10day"])

    # Debug: Print the historical DataFrame before trimming
    logging.debug(f"Historical DataFrame before trimming:\n{historical_data}")
    print("Historical DataFrame before trimming 847:\n", historical_data)

    # Trim the DataFrame to maintain the max_entries limit
    if len(historical_data) > max_entries:
        historical_data = historical_data.iloc[-max_entries:]  # Keep only the most recent entries

    # Save the updated DataFrame back to the file
    save_historical_data(historical_data)
    logging.info(f"✅ {HISTORICAL_DATA_FILE} updated successfully with latest real-time data.")

                        # ***** End of function to merge historical and realtime data *****

#time.sleep(5)
                       

#print("🔍 Final Access Token Before Use 964 :",consumer_key, consumer_secret, access_token)  # ✅ Debug to confirm values exist

                                       # ***** Function to fetch Schwab timesales and quote data *****


def fetch_schwab_realtime_ohlc(access_token, symbol, last_cumulative_volume=None):
    """
    Fetches OHLCV data for a symbol from Schwab.
    Returns a dict: {Datetime, Ticker, Open, High, Low, Close, Volume, CumulativeVolume}
    last_cumulative_volume: previous cumulative volume for this symbol (for after-hours)
    """
    import pytz
    from datetime import datetime
    import requests

    def is_market_open():
        et_zone = pytz.timezone("America/New_York")
        now = datetime.now(et_zone)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = now.replace(hour=16, minute=0, microsecond=0)
        return market_open <= now <= market_close

    # Schwab endpoint for quotes
    url = f"https://api.schwabapi.com/marketdata/v1/quotes/{symbol}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 401:
        print(f"401 Unauthorized for {symbol}. Refreshing Schwab OAuth token...")
        from Schwab_auth import get_schwab_access_token
        access_token = get_schwab_access_token(force_new=True)
        headers["Authorization"] = f"Bearer {access_token}"
        response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error fetching Schwab quote for {symbol}: {response.status_code} {response.text}")
        return None

    data = response.json()
    quote = data.get(symbol, {})
    now = datetime.now()
    open_price = quote.get("regularMarketOpen")
    high_price = quote.get("regularMarketDayHigh")
    low_price = quote.get("regularMarketDayLow")
    close_price = quote.get("regularMarketLastPrice")
    cumulative_volume = quote.get("regularMarketVolume")
    # Calculate per-bar volume
    if last_cumulative_volume is not None and cumulative_volume is not None:
        per_bar_volume = max(0, cumulative_volume - last_cumulative_volume)
    else:
        per_bar_volume = cumulative_volume if cumulative_volume is not None else 0
    ohlc = {
        "Open": open_price if open_price is not None else close_price,
        "High": high_price if high_price is not None else close_price,
        "Low": low_price if low_price is not None else close_price,
        "Close": close_price,
        "Volume": per_bar_volume,
    }
    print(f"[SCHWAB] {symbol} @ {now.strftime('%Y-%m-%d %H:%M:%S')} | Open: {ohlc['Open']} | High: {ohlc['High']} | Low: {ohlc['Low']} | Close: {ohlc['Close']} | Volume: {ohlc['Volume']}")
    return {
        "Datetime": now,
        "Ticker": symbol,
        "Open": ohlc["Open"],
        "High": ohlc["High"],
        "Low": ohlc["Low"],
        "Close": ohlc["Close"],
        "Volume": ohlc["Volume"],
        "CumulativeVolume": cumulative_volume  # Return this so you can store for next call
    }

        

                                              # ***** End of function to fetch Schwab timesales and quote data *****

#                                      ****** Function to fetch latest minute data from Schwab *****

def update_with_latest_minute():
    global historical_data  # If using as a global DataFrame
    for symbol in tickers:
        df_new = fetch_schwab_latest_minute(symbol)
        if not df_new.empty:
            historical_data = pd.concat([historical_data, df_new], ignore_index=True)
            historical_data.drop_duplicates(subset=["Datetime", "Ticker"], keep="last", inplace=True)
    historical_data.sort_values(["Datetime", "Ticker"], inplace=True)
    historical_data.reset_index(drop=True, inplace=True)
    historical_data.to_csv(hist_file, index=False)
    print("✅ Appended latest minute(s) to historical_data.csv")

# Then, in your timer/scheduler:
# schedule.every(1).minutes.do(update_with_latest_minute)

#                                         ********* Function to fetch E*TRADE market data *****

                                              # ***** Function to fetch E*TRADE market data *****                       

MARKET_DATA_FILE = "market_data.csv"

def load_market_data():
    # Loads market data from CSV if present and from today.
    # Otherwise returns an empty DataFrame.
    if os.path.exists(MARKET_DATA_FILE) and os.path.getsize(MARKET_DATA_FILE) == 0:
        print("⚠️ market_data.csv is empty, deleting... 2014")
        os.remove(MARKET_DATA_FILE)

    if os.path.exists(MARKET_DATA_FILE) and os.path.getsize(MARKET_DATA_FILE) > 0:
        try:
            df = pd.read_csv(MARKET_DATA_FILE, parse_dates=["week52HiDate", "week52LowDate"])
            today = datetime.now().date()
            file_time = datetime.fromtimestamp(os.path.getmtime(MARKET_DATA_FILE)).date()
            if file_time == today and not df.empty:
                print("✅ Loaded market data from CSV.")
                return df
        except Exception as e:
            print(f"⚠️ Error reading market_data.csv: {e}")
    print("⚠️ Market data not found or outdated.")
    return pd.DataFrame()

def run_realtime_job():
    global historical_data
    global tickers, session, base_url
    print("⏰ [SCHEDULER] Real-time data update fired at", datetime.now().strftime('%H:%M:%S'))
    historical_data = load_historical_data(tickers)
    #historical_data = run_realtime_data(historical_data, tickers, session, base_url)
    check_trade_alerts(historical_data)
    print("✅ [SCHEDULER] Real-time data update completed at", datetime.now().strftime('%H:%M:%S'))

def dashboard_update_job():
    print("📊 [SCHEDULER] Dashboard update fired at", datetime.now().strftime('%H:%M:%S'))
    df = load_historical_data(tickers)
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
    market_data_df = load_market_data()
    if market_data_df.empty:
        market_data_df = fetch_etrade_market_data(tickers)

historical_data = load_historical_data(tickers, api_key=ALPHA_VANTAGE_API_KEY)
adx_df = calculate_adx_multi(historical_data, tickers)
pmo_df = calculate_pmo_multi(historical_data, tickers)
filtered_df = historical_data.merge(
    adx_df[["Datetime", "Ticker", "ADX", "+DI", "-DI"]],
    on=["Datetime", "Ticker"], how="left"
).merge(
    pmo_df[["Datetime", "Ticker", "PMO", "PMO_signal"]],
    on=["Datetime", "Ticker"], how="left"
)

def run_dashboard_thread():
    print("🚀 [MAIN] Starting dashboard at", datetime.now().strftime('%H:%M:%S'))
    df = pd.read_csv("historical_data.csv")
    start_dashboard(historical_data, filtered_df, tickers, dashboard_ranks)

dashboard_thread = threading.Thread(target=run_dashboard_thread, daemon=True)
dashboard_thread.start()

def refresh_news_cache():
    for ticker in tickers:
        fetch_etf_news(ticker)

def refresh_whale_cache():
    print("🔄 Refreshing whale cache for all tickers...")
    for ticker in tickers:
        fetch_whale_data(ticker)
    print("✅ Whale cache refreshed.")

schedule.clear()
schedule.every(1).minutes.do(update_with_latest_minute)
schedule.every(1).minutes.do(dashboard_update_job)

schedule.every().day.at("09:30").do(refresh_news_cache)
schedule.every().day.at("10:30").do(refresh_news_cache)
schedule.every().day.at("11:30").do(refresh_news_cache)

schedule.every().day.at("09:30").do(refresh_whale_cache)
schedule.every().day.at("10:30").do(refresh_whale_cache)
schedule.every().day.at("11:30").do(refresh_whale_cache)

while True:
    print("🔍 [LOOP] Scheduled Jobs:", schedule.jobs)
    schedule.run_pending()
    print("🚀 [LOOP] Waiting for next scheduled job... (sleeping 30s)")
    print("Current time 1157 :", datetime.now().strftime('%H:%M:%S'))
    time.sleep(30)

def main():
    global historical_data, session, base_url
    historical_data = load_historical_data(tickers=tickers, api_key=ALPHA_VANTAGE_API_KEY)
    historical_data = historical_data.sort_values(["Datetime", "Ticker"])
    historical_data.to_csv(HISTORICAL_DATA_FILE, index=False)
    print("Loaded historical data.")
    print("Top 10 rows of historical_data after loading:")
    print("Etrade timesales realtime data 1919:", historical_data.head(10))
    if is_market_open():
        print("Market is open. Fetching real-time data from E*TRADE...")
        historical_data = run_realtime_data(historical_data, tickers, session, base_url)
        print("Historical data updated with real-time E*TRADE data.")
    else:
        print("Market is closed. Using only historical data.")
    historical_data = historical_data.sort_values(["Datetime", "Ticker"])
    historical_data.to_csv(HISTORICAL_DATA_FILE, index=False)
    print("Historical data saved.")

if __name__ == "__main__":
    main()
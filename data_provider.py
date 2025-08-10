import os
import time
import json
import pandas as pd
import yfinance as yf

# --- CONFIG ---
CACHE_DIR = "data_cache"
os.makedirs(CACHE_DIR, exist_ok=True)

YAHOO_CACHE_FILE = os.path.join(CACHE_DIR, "yahoo_intraday.csv")
ETRADE_CACHE_FILE = os.path.join(CACHE_DIR, "etrade_extended.csv")
CACHE_EXPIRY_SECONDS = 60 * 10  # 10 minutes for intraday data

def is_cache_fresh(filename, expiry_seconds):
    return os.path.exists(filename) and (time.time() - os.path.getmtime(filename) < expiry_seconds)

def get_yahoo_intraday(ticker, period="2d", interval="1h", force_refresh=False):
    """
    Get intraday data from Yahoo Finance for a single ticker, cache to disk.
    Returns a DataFrame with columns: Datetime, Open, High, Low, Close, Volume.
    """
    cache_file = os.path.join(CACHE_DIR, f"yahoo_intraday_{ticker}.csv")
    if not force_refresh and is_cache_fresh(cache_file, CACHE_EXPIRY_SECONDS):
        print(f"✅ Using cached Yahoo intraday data for {ticker}.")
        df = pd.read_csv(cache_file, parse_dates=["Datetime"])
    else:
        print(f"🚀 Fetching Yahoo intraday data for {ticker}...")
        df = yf.download(ticker, period=period, interval=interval)
        df = df.reset_index().rename(columns={"index": "Datetime"})
        df.to_csv(cache_file, index=False)
    # Ensure numeric columns
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        if col in df.columns and isinstance(df[col], pd.Series):
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

def get_etrade_extended(tickers, force_refresh=False):
    """Get extended hours data from E*TRADE, cache to disk."""
    if not force_refresh and is_cache_fresh(ETRADE_CACHE_FILE, CACHE_EXPIRY_SECONDS):
        print("✅ Using cached E*TRADE extended data.")
        return pd.read_csv(ETRADE_CACHE_FILE, parse_dates=["Datetime"])
    print("🚀 Fetching E*TRADE extended hours data...")
    try:
        from etrade_quotes import get_quotes
        df = get_quotes(tickers, extended_hours=True)
        if not df.empty:
            df.to_csv(ETRADE_CACHE_FILE, index=False)
        else:
            print("⚠️ E*TRADE returned empty DataFrame.")
    except Exception as e:
        print(f"❌ Error fetching E*TRADE data: {e}")
        if os.path.exists(ETRADE_CACHE_FILE):
            print("⚠️ Using stale cached E*TRADE data.")
            return pd.read_csv(ETRADE_CACHE_FILE, parse_dates=["Datetime"])
        else:
            return pd.DataFrame()
    return df

def get_market_data(tickers, source="yahoo", force_refresh=False):
    """
    Main entry point for any app.
    source: "yahoo" or "etrade"
    Returns a DataFrame with OHLCV data.
    """
    if source == "yahoo":
        dfs = []
        for ticker in tickers:
            df = get_yahoo_intraday(ticker, force_refresh=force_refresh)
            if df is not None and not df.empty:
                df["Ticker"] = ticker
                dfs.append(df)
        if dfs:
            return pd.concat(dfs, ignore_index=True)
        else:
            return pd.DataFrame()
    elif source == "etrade":
        return get_etrade_extended(tickers, force_refresh)
    else:
        raise ValueError(f"Unknown data source: {source}")

# Example usage:
if __name__ == "__main__":
    tickers = ["AAPL", "TSLA", "MSFT"]
    print("Yahoo data:")
    dfs = [get_yahoo_intraday(ticker) for ticker in tickers]
    for df in dfs:
        print(df.head())
    print("\nE*TRADE data:")
    df_etrade = get_market_data(tickers, source="etrade")
    print(df_etrade.head())
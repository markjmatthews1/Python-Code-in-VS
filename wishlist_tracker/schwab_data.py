
import json
from urllib import response
import pandas as pd
from datetime import datetime, timedelta
import pytz
from Schwab_auth import get_valid_access_token, refresh_access_token
import requests
from Schwab_auth import ensure_fresh_token
import time


TOKEN_FILE = "tokens.json"

def convert_to_eastern_datetime(df, source_col="datetime", target_col="Datetime"):
    """
    Converts a UTC ms timestamp column to US/Eastern formatted string.
    """
    eastern = pytz.timezone("US/Eastern")
    df[target_col] = (
        pd.to_datetime(df[source_col], unit="ms", utc=True)
        .dt.tz_convert(eastern)
        .dt.strftime("%Y-%m-%d %H:%M")
    )
    return df

def load_schwab_access_token():
    """
    Loads the Schwab access token from tokens.json (nested structure).
    """
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        tokens = token_data.get("token_dictionary", {})
        access_token = tokens.get("access_token")
        if not access_token:
            raise RuntimeError("No access token found in tokens.json!")
        return access_token
    except Exception as e:
        raise RuntimeError(f"Error loading Schwab access token: {e}")


def fetch_schwab_minute_ohlcv(symbol, period=1, retry_on_401=True):
    """
    Fetches 1-min OHLCV for symbol. If 401, auto-refreshes token and retries once.
    Returns DataFrame with columns: Datetime, Ticker, Open, High, Low, Close, Volume
    """
    ensure_fresh_token()
    endpoint = f"https://api.schwabapi.com/marketdata/v1/pricehistory"
    eastern = pytz.timezone("US/Eastern")
    now = datetime.now(eastern)
    # Find most recent weekday (skip Sat/Sun)
    weekday = now.weekday()
    if weekday >= 5:  # Saturday or Sunday
        days_back = weekday - 4  # Go back to Friday
    else:
        days_back = 0
    last_trading_day = now - timedelta(days=days_back)
    last_trading_date = last_trading_day.date()
    # Fetch enough bars for technicals (e.g., 2 days for safety)
    start_dt = eastern.localize(datetime.combine(last_trading_date, datetime.min.time().replace(hour=4, minute=0)))
    end_dt = eastern.localize(datetime.combine(last_trading_date, datetime.min.time().replace(hour=20, minute=0)))
    start_ms = int(start_dt.astimezone(pytz.utc).timestamp() * 1000)
    end_ms = int(end_dt.astimezone(pytz.utc).timestamp() * 1000)
    params = {
        "symbol": symbol,
        "periodType": "day",
        "frequencyType": "minute",
        "frequency": 1,
        "startDate": start_ms,
        "endDate": end_ms,
        "needExtendedHoursData": "true"
    }

    def get_headers():
        return {
            "Authorization": f"Bearer {get_valid_access_token()}",
            "Accept": "application/json"
        }

    print(f"Requesting {symbol} minute bars from {start_dt} to {end_dt} (ms: {start_ms} to {end_ms})")
    response = requests.get(endpoint, headers=get_headers(), params=params)
    if response.status_code == 401 and retry_on_401:
        print(f"🔄 401 Unauthorized for {symbol}, refreshing token and retrying...")
        refresh_access_token()
        response = requests.get(endpoint, headers=get_headers(), params=params)
    if response.status_code != 200:
        print(f"❌ Error fetching OHLCV for {symbol}: {response.status_code}")
        print(f"Response content: {response.text}")
        return pd.DataFrame()

    data = response.json()
    candles = data.get("candles", [])
    if not candles:
        print(f"⚠️ No candles returned for {symbol}")
        print(f"Raw response: {data}")
        return pd.DataFrame()
    df = pd.DataFrame(candles)
    if df.empty:
        print(f"⚠️ Empty DataFrame for {symbol}")
        print(f"Raw candles: {candles}")
        return df

    # Log first and last bar times
    if "datetime" in df.columns:
        first_bar = pd.to_datetime(df["datetime"].iloc[0], unit="ms", utc=True).tz_convert(eastern)
        last_bar = pd.to_datetime(df["datetime"].iloc[-1], unit="ms", utc=True).tz_convert(eastern)
        print(f"First bar: {first_bar}, Last bar: {last_bar}")

    # Rename columns to match code expectations
    column_map = {
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }
    df.rename(columns=column_map, inplace=True)

    # Add Ticker column
    df["Ticker"] = symbol

    # Add readable Datetime column in US/Eastern
    if "datetime" in df.columns:
        df = convert_to_eastern_datetime(df)

    # Enforce correct column order
    expected_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]
    df = df[[col for col in expected_cols if col in df.columns]]

    return df

def fetch_schwab_latest_minute(symbol):
    """
    Fetches the latest 2 minutes of OHLCV bars for a symbol (including premarket and after hours).
    Returns a DataFrame with columns: Datetime, Ticker, Open, High, Low, Close, Volume
    """
   
    access_token = load_schwab_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    endpoint = "https://api.schwabapi.com/marketdata/v1/pricehistory"
    now = datetime.utcnow()
    start = int((now - timedelta(minutes=2)).timestamp() * 1000)
    end = int(now.timestamp() * 1000)
    params = {
        "symbol": symbol,
        "frequencyType": "minute",
        "frequency": 1,
        "startDate": start,
        "endDate": end,
        "needExtendedHoursData": "true"  # <-- Enable premarket and after hours data
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if "candles" in data and data["candles"]:
            df = pd.DataFrame(data["candles"])
            df["Ticker"] = symbol
            df = convert_to_eastern_datetime(df)
            df = df.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume"
            })
            df = df[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
            return df
        else:
            print(f"No OHLCV data returned for symbol: {symbol}")
            return pd.DataFrame()
    else:
        print(f"Error fetching latest OHLCV for {symbol}: {response.status_code} {response.text}")
        return pd.DataFrame()
        
def fetch_minute_bars_for_range(symbol, start_dt, end_dt, max_retries=3):
    """
    Fetches minute bars for a symbol within a date range.
    """
    access_token = load_schwab_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    
    endpoint = "https://api.schwabapi.com/marketdata/v1/pricehistory"
    start_ms = int(start_dt.timestamp() * 1000)
    end_ms = int(end_dt.timestamp() * 1000)
    
    params = {
        "symbol": symbol,
        "periodType": "day",
        "frequencyType": "minute", 
        "frequency": 1,
        "startDate": start_ms,
        "endDate": end_ms,
        "needExtendedHoursData": "true"
    }
    
    for attempt in range(max_retries):
        try:
            response = requests.get(endpoint, headers=headers, params=params, timeout=30)
            
            if response.status_code == 401:
                if attempt == 0:  # Only refresh token on first 401
                    print(f"401 error for {symbol}, refreshing Schwab token...")
                    ensure_fresh_token()
                    # Update headers with new token
                    access_token = load_schwab_access_token()
                    headers["Authorization"] = f"Bearer {access_token}"
                    continue
                else:
                    print(f"Still 401 after token refresh for {symbol}")
                    return pd.DataFrame()
            
            if response.status_code == 200:
                data = response.json()
                if "candles" in data and data["candles"]:
                    df = pd.DataFrame(data["candles"])
                    df = convert_to_eastern_datetime(df)
                    column_map = {
                        "open": "Open",
                        "high": "High", 
                        "low": "Low",
                        "close": "Close",
                        "volume": "Volume"
                    }
                    df.rename(columns=column_map, inplace=True)
                    df["Ticker"] = symbol
                    expected_cols = ["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]
                    df = df[[col for col in expected_cols if col in df.columns]]
                    return df
                else:
                    print(f"No candles data for {symbol}")
                    return pd.DataFrame()
            else:
                print(f"❌ Error fetching OHLCV for {symbol}: {response.status_code}")
                if attempt == max_retries - 1:
                    return pd.DataFrame()
                    
        except requests.exceptions.RequestException as e:
            print(f"Network error for {symbol} (attempt {attempt + 1}): {e}")
            if attempt == max_retries - 1:
                print(f"Max retries exceeded for {symbol} due to network errors")
                return pd.DataFrame()
            time.sleep(2)  # Wait before retry
            
    return pd.DataFrame()
    
def fetch_daily_bars_for_range(symbol, years_back=5):
    import pandas as pd
    endpoint = "https://api.schwabapi.com/marketdata/v1/pricehistory"
    access_token = load_schwab_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    params = {
        "symbol": symbol,
        "periodType": "year",
        "period": years_back,
        "frequencyType": "daily",
        "frequency": 1
    }
    response = requests.get(endpoint, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        candles = data.get("candles", [])
        if candles:
            df = pd.DataFrame(candles)
            df["Ticker"] = symbol
            df = convert_to_eastern_datetime(df)
            df = df.rename(columns={
                "open": "Open",
                "high": "High",
                "low": "Low",
                "close": "Close",
                "volume": "Volume"
            })
            df = df[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
            return df
        else:
            print(f"⚠️ No daily candles returned for {symbol}")
            return pd.DataFrame()
    else:
        print(f"❌ Error fetching daily OHLCV for {symbol}: {response.status_code} {response.text}")
        return pd.DataFrame()
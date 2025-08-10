#!/usr/bin/env python3
"""
Dashboard Diagnostic Tool
Checks key components that might be causing chart update issues
"""

import os
import pandas as pd
import json
from datetime import datetime, timezone
import sys

def check_file_timestamps():
    """Check when key files were last modified"""
    print("=== File Timestamp Check ===")
    files_to_check = [
        "historical_data.csv",
        "settings.json", 
        "dashboard_debug.log",
        "auth_data.json"
    ]
    
    for file in files_to_check:
        if os.path.exists(file):
            timestamp = os.path.getmtime(file)
            readable_time = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            print(f"✅ {file}: Last modified {readable_time}")
        else:
            print(f"❌ {file}: File not found")

def check_settings():
    """Check dashboard settings"""
    print("\n=== Settings Check ===")
    try:
        with open("settings.json", "r") as f:
            settings = json.load(f)
        print(f"✅ Dashboard interval: {settings.get('dashboard_interval', 'NOT SET')} minutes")
        print(f"✅ Volatility lookback: {settings.get('volatility_lookback_bars', 'NOT SET')} bars")
    except Exception as e:
        print(f"❌ Error reading settings: {e}")

def check_historical_data():
    """Check historical data file"""
    print("\n=== Historical Data Check ===")
    try:
        df = pd.read_csv("historical_data.csv")
        print(f"✅ Historical data loaded: {len(df)} rows")
        print(f"✅ Columns: {df.columns.tolist()}")
        
        if 'Datetime' in df.columns:
            df['Datetime'] = pd.to_datetime(df['Datetime'], errors='coerce')
            latest_time = df['Datetime'].max()
            oldest_time = df['Datetime'].min()
            print(f"✅ Data range: {oldest_time} to {latest_time}")
            
            # Check how recent the data is
            now = datetime.now()
            time_diff = now - latest_time.to_pydatetime().replace(tzinfo=None)
            hours_old = time_diff.total_seconds() / 3600
            print(f"✅ Latest data is {hours_old:.1f} hours old")
            
            if hours_old > 2:
                print("⚠️  WARNING: Data is more than 2 hours old!")
        
        if 'Ticker' in df.columns:
            tickers = df['Ticker'].unique()
            print(f"✅ Available tickers: {tickers}")
            
    except Exception as e:
        print(f"❌ Error reading historical data: {e}")

def check_schwab_auth():
    """Check Schwab authentication"""
    print("\n=== Schwab Authentication Check ===")
    try:
        # Check for tokens.json (actual file used by day.py)
        if os.path.exists("tokens.json"):
            with open("tokens.json", "r") as f:
                token_data = json.load(f)
            
            token_dict = token_data.get("token_dictionary", {})
            if "access_token" in token_dict:
                print("✅ Access token found in tokens.json")
                
                # Check if there's an expiry time
                if "expires_at" in token_dict:
                    import time
                    expires_at = token_dict["expires_at"]
                    current_time = time.time()
                    time_left = expires_at - current_time
                    print(f"✅ Token expires in: {time_left:.0f} seconds ({time_left/60:.1f} minutes)")
                    
                    if time_left < 300:  # Less than 5 minutes
                        print("⚠️  WARNING: Token expires very soon!")
                    elif time_left < 0:
                        print("❌ ERROR: Token has expired!")
                else:
                    print("⚠️  No expiry information found")
            else:
                print("❌ No access token found in tokens.json")
        else:
            print("❌ tokens.json not found")
            
        # Also check for auth_data.json (backup/alternative)
        if os.path.exists("auth_data.json"):
            print("✅ auth_data.json also exists (backup)")
        else:
            print("ℹ️  auth_data.json not found (this is OK)")
            
    except Exception as e:
        print(f"❌ Error checking Schwab auth: {e}")

def test_schwab_connection():
    """Test basic Schwab API connection"""
    print("\n=== Schwab API Connection Test ===")
    try:
        # Import and test schwab data module
        sys.path.append('.')
        from schwab_data import fetch_schwab_minute_ohlcv
        
        # Try to fetch a small amount of data for SPY
        print("Testing fetch for SPY...")
        test_data = fetch_schwab_minute_ohlcv("SPY", period=1)
        
        if test_data is not None and not test_data.empty:
            print(f"✅ Successfully fetched {len(test_data)} rows for SPY")
            print(f"✅ Latest data point: {test_data.iloc[-1]['Datetime']}")
        else:
            print("❌ No data returned from Schwab API")
            
    except Exception as e:
        print(f"❌ Error testing Schwab connection: {e}")
        import traceback
        traceback.print_exc()

def check_dashboard_process():
    """Check if the dashboard is running and responding"""
    print("\n=== Dashboard Process Check ===")
    try:
        import requests
        import time
        
        # Check if port 8050 is responding
        try:
            response = requests.get("http://127.0.0.1:8050", timeout=5)
            if response.status_code == 200:
                print("✅ Dashboard is responding on port 8050")
            else:
                print(f"⚠️  Dashboard responding but with status {response.status_code}")
        except requests.exceptions.ConnectionError:
            print("❌ Dashboard not responding on port 8050")
        except requests.exceptions.Timeout:
            print("⚠️  Dashboard is slow to respond")
        except Exception as e:
            print(f"❌ Error checking dashboard: {e}")
            
        # Check if Python processes are running
        import subprocess
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        python_processes = [line for line in result.stdout.split('\n') if 'python.exe' in line]
        print(f"✅ Found {len(python_processes)} Python processes running")
        
        # Check if we can access the historical data file recently
        if os.path.exists("historical_data.csv"):
            timestamp = os.path.getmtime("historical_data.csv")
            file_age = time.time() - timestamp
            print(f"✅ Historical data file age: {file_age/60:.1f} minutes")
            
            if file_age > 600:  # More than 10 minutes
                print("⚠️  Historical data hasn't been updated recently")
        
    except Exception as e:
        print(f"❌ Error checking dashboard process: {e}")

def test_data_update():
    """Test if we can manually trigger a data update"""
    print("\n=== Manual Data Update Test ===")
    try:
        sys.path.append('.')
        
        # Try to load and update historical data
        print("Testing manual data fetch...")
        from schwab_data import fetch_schwab_minute_ohlcv
        
        # Get current data timestamp before update
        old_timestamp = None
        if os.path.exists("historical_data.csv"):
            old_timestamp = os.path.getmtime("historical_data.csv")
            
        # Try to fetch new data for a common ticker
        test_ticker = "SPY"
        new_data = fetch_schwab_minute_ohlcv(test_ticker, period=1)
        
        if new_data is not None and not new_data.empty:
            print(f"✅ Successfully fetched fresh data for {test_ticker}")
            print(f"✅ Data range: {new_data['Datetime'].min()} to {new_data['Datetime'].max()}")
            
            # Check if this would be newer than existing data
            if not new_data.empty:
                latest_new = new_data['Datetime'].max()
                print(f"✅ Latest fetched data: {latest_new}")
                
                # Check current file
                if os.path.exists("historical_data.csv"):
                    existing_df = pd.read_csv("historical_data.csv")
                    existing_df['Datetime'] = pd.to_datetime(existing_df['Datetime'], errors='coerce')
                    latest_existing = existing_df['Datetime'].max()
                    print(f"✅ Latest existing data: {latest_existing}")
                    
                    if latest_new > latest_existing:
                        print("✅ New data is more recent than existing data")
                    else:
                        print("⚠️  New data is not newer than existing data")
        else:
            print("❌ Failed to fetch fresh data")
            
    except Exception as e:
        print(f"❌ Error testing manual data update: {e}")
        import traceback
        traceback.print_exc()

def main():
    print("🔍 Dashboard Diagnostic Tool")
    print("=" * 50)
    print(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    check_file_timestamps()
    check_settings()
    check_historical_data() 
    check_schwab_auth()
    test_schwab_connection()
    check_dashboard_process()
    test_data_update()
    
    print("\n" + "=" * 50)
    print("✅ Diagnostic complete!")
    
    # Final diagnosis
    print("\n🏥 DIAGNOSIS:")
    print("If the dashboard is running but charts aren't updating, possible causes:")
    print("1. ⏰ Scheduler thread may have crashed silently")
    print("2. 🔒 Token refresh might be failing silently") 
    print("3. 📊 Data fetching might be encountering errors")
    print("4. 🔄 The dashboard interval callback might be stuck")
    print("\n💡 SOLUTION: Restart the dashboard completely with 'python day.py'")

if __name__ == "__main__":
    main()

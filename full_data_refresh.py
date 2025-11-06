#!/usr/bin/env python3
"""
Full data refresh for all 24 tickers - Fix the historical data file
"""

import json
import requests
import pandas as pd
import pytz
from datetime import datetime, timedelta
import os

def fetch_all_tickers_today():
    print("🔄 FULL DATA REFRESH FOR ALL TICKERS")
    print("=" * 60)
    
    # All 24 tickers from the day app
    all_tickers = ['AGQ', 'AMD', 'BITU', 'BOIL', 'CWEB', 'DFEN', 'ERX', 'ETHU',
                   'GDXU', 'JNUG', 'LABU', 'MSFU', 'MSTX', 'NAIL', 'NUGT', 'NVDL', 
                   'ROM', 'SDOW', 'SDS', 'SMCX', 'SSO', 'TECL', 'TQQQ', 'TSLT']
    
    try:
        # Load token
        with open('tokens.json', 'r') as f:
            token_data = json.load(f)
        
        tokens = token_data.get('token_dictionary', {})
        access_token = tokens.get('access_token')
        
        if not access_token:
            print("❌ No access token found")
            return
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Set up today's time range
        eastern = pytz.timezone("US/Eastern")
        now = datetime.now(eastern)
        today = now.date()
        
        # Get today's trading session (4am to current time)
        start_dt = eastern.localize(datetime.combine(today, datetime.min.time().replace(hour=4, minute=0)))
        end_dt = now
        
        # Convert to UTC milliseconds
        start_ms = int(start_dt.astimezone(pytz.utc).timestamp() * 1000)
        end_ms = int(end_dt.astimezone(pytz.utc).timestamp() * 1000)
        
        print(f"📅 Date: {today}")
        print(f"🕐 Time range: {start_dt} to {end_dt}")
        print(f"📊 Tickers to fetch: {len(all_tickers)}")
        
        endpoint = "https://api.schwabapi.com/marketdata/v1/pricehistory"
        all_new_data = []
        success_count = 0
        
        for i, ticker in enumerate(all_tickers):
            print(f"\n📡 [{i+1:2d}/{len(all_tickers)}] Fetching {ticker}...", end=" ")
            
            params = {
                "symbol": ticker,
                "periodType": "day", 
                "frequencyType": "minute",
                "frequency": 1,
                "startDate": start_ms,
                "endDate": end_ms,
                "needExtendedHoursData": "true"
            }
            
            try:
                response = requests.get(endpoint, headers=headers, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    candles = data.get("candles", [])
                    
                    if candles:
                        # Convert to DataFrame
                        df = pd.DataFrame(candles)
                        df["Ticker"] = ticker
                        
                        # Convert datetime
                        df["Datetime"] = pd.to_datetime(df["datetime"], unit='ms', utc=True)
                        df["Datetime"] = df["Datetime"].dt.tz_convert(eastern)
                        
                        # Rename columns
                        df = df.rename(columns={
                            "open": "Open",
                            "high": "High",
                            "low": "Low", 
                            "close": "Close",
                            "volume": "Volume"
                        })
                        
                        # Select columns
                        df = df[["Datetime", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
                        all_new_data.append(df)
                        success_count += 1
                        
                        print(f"✅ {len(candles)} bars")
                    else:
                        print(f"⚠️ No data")
                        
                elif response.status_code == 401:
                    print(f"🔐 Auth error - stopping")
                    break
                else:
                    print(f"❌ Error {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Exception: {str(e)[:50]}...")
        
        print(f"\n📊 FETCH SUMMARY:")
        print(f"✅ Successful: {success_count}/{len(all_tickers)} tickers")
        
        if all_new_data:
            # Combine all new data
            new_df = pd.concat(all_new_data, ignore_index=True)
            print(f"📊 Total new rows: {len(new_df)}")
            print(f"📅 Date range: {new_df['Datetime'].min()} to {new_df['Datetime'].max()}")
            
            # Load existing historical data
            historical_file = 'historical_data.csv'
            if os.path.exists(historical_file):
                existing_df = pd.read_csv(historical_file)
                print(f"📁 Existing data: {len(existing_df)} rows")
                
                # Combine with existing data
                combined_df = pd.concat([existing_df, new_df], ignore_index=True)
                
                # Remove duplicates (in case of overlap)
                combined_df['Datetime'] = pd.to_datetime(combined_df['Datetime'])
                combined_df = combined_df.drop_duplicates(subset=['Datetime', 'Ticker'], keep='last')
                combined_df = combined_df.sort_values(['Datetime', 'Ticker'])
                
                print(f"🔄 Combined data: {len(combined_df)} rows (after dedup)")
                
                # Save back to file
                combined_df.to_csv(historical_file, index=False)
                print(f"💾 Updated {historical_file}")
                
                # Show final statistics
                combined_df['Date'] = combined_df['Datetime'].dt.date
                date_counts = combined_df['Date'].value_counts().sort_index()
                print(f"\n📊 FINAL DATA BREAKDOWN:")
                for date, count in date_counts.items():
                    print(f"   {date}: {count} rows")
                    
                return combined_df
            else:
                # No existing file, create new one
                new_df.to_csv(historical_file, index=False) 
                print(f"💾 Created new {historical_file}")
                return new_df
                
        else:
            print(f"❌ No data retrieved - check API connectivity")
            return None
            
    except Exception as e:
        print(f"❌ Critical error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    result = fetch_all_tickers_today()
    if result is not None:
        print(f"\n🎉 SUCCESS: Historical data file updated with today's data!")
    else:
        print(f"\n❌ FAILED: Could not refresh historical data")

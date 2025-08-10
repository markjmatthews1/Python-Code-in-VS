"""
Manual Historical Data Refresh - Get fresh data for all tickers
"""
import pandas as pd
from schwab_data import fetch_schwab_minute_ohlcv
from datetime import datetime
import time

def refresh_historical_data():
    print("🔄 MANUAL HISTORICAL DATA REFRESH")
    print("=" * 50)
    
    # Get candidate tickers from same Excel file that day.py uses
    import pandas as pd
    try:
        df = pd.read_excel('Top_ETFS_for_DayTrade.xlsx')
        candidate_tickers = df['Symbol'].dropna().astype(str).str.strip().tolist()
        print(f"📋 Loaded {len(candidate_tickers)} tickers from Excel: {candidate_tickers}")
    except Exception as e:
        print(f"⚠️ Could not read Excel file, using fallback list: {e}")
        candidate_tickers = [
            'MSFU', 'TQQQ', 'BOIL', 'CWEB', 'DFEN', 'ERX', 'ETHU', 'GDXU', 'LABU', 
            'NAIL', 'NVDU', 'ROM', 'SDOW', 'SDS', 'SMCX', 'SSO', 'TECL', 'TSLT', 
            'AGQ', 'BITU', 'SOXL', 'SPXU', 'TECS', 'UVXY', 'VIXY'
        ]
    
    print(f"📊 Fetching fresh data for {len(candidate_tickers)} tickers...")
    
    all_new_data = []
    success_count = 0
    
    for i, ticker in enumerate(candidate_tickers, 1):
        print(f"   {i:2d}/{len(candidate_tickers)} Fetching {ticker}...", end=" ")
        
        try:
            # Get today's fresh minute data using explicit date range
            from schwab_data import fetch_minute_bars_for_range
            from datetime import date, timedelta
            import pytz
            
            # Get data from yesterday 4 AM to today 8 PM Eastern
            et = pytz.timezone('US/Eastern')
            today = date.today()  # 8/7/2025
            yesterday = today - timedelta(days=1)  # 8/6/2025
            
            start_time = et.localize(datetime.combine(yesterday, datetime.min.time().replace(hour=4)))
            end_time = et.localize(datetime.combine(today, datetime.min.time().replace(hour=20)))
            
            df = fetch_minute_bars_for_range(ticker, start_time, end_time)
            
            if not df.empty:
                print(f"✅ {len(df)} rows")
                all_new_data.append(df)
                success_count += 1
            else:
                print(f"❌ No data")
                
        except Exception as e:
            print(f"❌ Error: {str(e)[:50]}")
        
        # Small delay to avoid rate limiting
        time.sleep(0.1)
    
    print(f"\n📋 FETCH SUMMARY:")
    print(f"   Successful: {success_count}/{len(candidate_tickers)} ({success_count/len(candidate_tickers)*100:.1f}%)")
    
    if success_count == 0:
        print("❌ No data fetched - cannot update historical file")
        return False
    
    # Combine all new data
    print(f"\n🔄 Combining and saving data...")
    new_combined = pd.concat(all_new_data, ignore_index=True)
    print(f"   Total new rows: {len(new_combined)}")
    
    # Load existing historical data
    try:
        existing_df = pd.read_csv("historical_data.csv")
        print(f"   Existing rows: {len(existing_df)}")
        
        # Combine with existing data
        combined_df = pd.concat([existing_df, new_combined], ignore_index=True)
        
        # Remove duplicates (same datetime + ticker)
        combined_df = combined_df.drop_duplicates(subset=["Datetime", "Ticker"], keep="last")
        
        # Sort by datetime and ticker
        combined_df['Datetime_sort'] = pd.to_datetime(combined_df['Datetime'], format='mixed')
        combined_df = combined_df.sort_values(['Ticker', 'Datetime_sort'])
        combined_df = combined_df.drop('Datetime_sort', axis=1)
        
        print(f"   Combined rows: {len(combined_df)}")
        
    except FileNotFoundError:
        print("   No existing file - creating new one")
        combined_df = new_combined
    
    # Save updated historical data
    combined_df.to_csv("historical_data.csv", index=False)
    print(f"✅ Updated historical_data.csv")
    
    # Verify the update
    print(f"\n✓ VERIFICATION:")
    today = datetime.now().date()
    combined_df['Date'] = pd.to_datetime(combined_df['Datetime'], format='mixed').dt.date
    today_data = combined_df[combined_df['Date'] == today]
    today_tickers = today_data['Ticker'].unique()
    
    print(f"   Today's data: {len(today_data)} rows")
    print(f"   Today's tickers: {len(today_tickers)} ({list(today_tickers)})")
    print(f"   Coverage: {len(today_tickers)}/{len(candidate_tickers)} ({len(today_tickers)/len(candidate_tickers)*100:.1f}%)")
    
    if len(today_tickers) >= len(candidate_tickers) * 0.8:  # 80% threshold
        print(f"✅ COVERAGE SUFFICIENT - Dashboard should work now!")
        return True
    else:
        print(f"⚠️ COVERAGE STILL LOW - May need manual investigation")
        return False

if __name__ == "__main__":
    success = refresh_historical_data()
    
    print(f"\n" + "="*50)
    if success:
        print("🎉 HISTORICAL DATA REFRESH COMPLETE!")
        print("   Try running the dashboard now")
        print("   The popup should show much better coverage")
    else:
        print("⚠️ PARTIAL SUCCESS")
        print("   Some data was updated but coverage may still be low")
        print("   Check individual ticker issues")

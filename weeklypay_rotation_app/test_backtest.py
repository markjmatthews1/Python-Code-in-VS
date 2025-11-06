"""
Test script to check what data is actually available for each ticker
"""
import yfinance as yf
from datetime import datetime, timedelta

tickers = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW', 'XOMO', 'JPOW', 'TSLW', 'QDTE']

print("="*80)
print("CHECKING DATA AVAILABILITY FOR WEEKLY DIVIDEND ETFS")
print("="*80)

for ticker in tickers:
    print(f"\n{'='*80}")
    print(f"Ticker: {ticker}")
    print(f"{'='*80}")
    
    try:
        stock = yf.Ticker(ticker)
        
        # Check basic info
        info = stock.info
        print(f"\n📋 Basic Info:")
        print(f"  Name: {info.get('longName', 'N/A')}")
        print(f"  Exchange: {info.get('exchange', 'N/A')}")
        print(f"  First Trade Date: {info.get('firstTradeDateEpochUtc', 'N/A')}")
        
        # Check price history
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        hist = stock.history(start=start_date, end=end_date)
        
        print(f"\n📊 Price Data (Last 90 days):")
        print(f"  Days of data: {len(hist)}")
        if len(hist) > 0:
            print(f"  First date: {hist.index[0].strftime('%Y-%m-%d')}")
            print(f"  Last date: {hist.index[-1].strftime('%Y-%m-%d')}")
            print(f"  Current price: ${hist['Close'].iloc[-1]:.2f}")
        
        # Check dividend history
        dividends = stock.dividends
        
        print(f"\n💰 Dividend Data:")
        print(f"  Total dividends in history: {len(dividends)}")
        
        if len(dividends) > 0:
            print(f"  First dividend: {dividends.index[0].strftime('%Y-%m-%d')} - ${dividends.iloc[0]:.4f}")
            print(f"  Last dividend: {dividends.index[-1].strftime('%Y-%m-%d')} - ${dividends.iloc[-1]:.4f}")
            
            # Count recent dividends (last 90 days)
            recent_divs = dividends[dividends.index >= start_date]
            print(f"  Dividends in last 90 days: {len(recent_divs)}")
            
            if len(recent_divs) > 0:
                print(f"\n  Recent Dividend Dates:")
                for div_date, div_amount in recent_divs.items():
                    print(f"    {div_date.strftime('%Y-%m-%d')}: ${div_amount:.4f}")
            
            # Calculate average weekly frequency
            if len(dividends) >= 2:
                date_range = (dividends.index[-1] - dividends.index[0]).days
                avg_days_between = date_range / (len(dividends) - 1)
                print(f"\n  Average days between dividends: {avg_days_between:.1f}")
                print(f"  Expected for weekly: ~7 days")
        else:
            print("  ❌ NO DIVIDEND DATA FOUND")
        
        print(f"\n✅ Summary for {ticker}:")
        if len(hist) > 0 and len(dividends) > 0:
            recent_divs = dividends[dividends.index >= start_date]
            if len(recent_divs) >= 8:  # Need at least 8 weekly dividends for good backtest
                print(f"  ✅ SUFFICIENT DATA for backtest ({len(recent_divs)} dividends)")
            elif len(recent_divs) >= 3:
                print(f"  ⚠️ LIMITED DATA for backtest ({len(recent_divs)} dividends - need 8+)")
            else:
                print(f"  ❌ INSUFFICIENT DATA for backtest ({len(recent_divs)} dividends)")
        else:
            print(f"  ❌ MISSING CRITICAL DATA (price or dividends)")
            
    except Exception as e:
        print(f"❌ ERROR checking {ticker}: {e}")
        import traceback
        traceback.print_exc()

print(f"\n{'='*80}")
print("DATA CHECK COMPLETE")
print(f"{'='*80}")

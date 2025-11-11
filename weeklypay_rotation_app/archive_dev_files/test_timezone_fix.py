"""
Quick test of the timezone fix
"""
import yfinance as yf
from datetime import datetime, timedelta
import pytz

ticker = "NVDW"
print(f"Testing {ticker}...")

stock = yf.Ticker(ticker)
end_date = datetime.now()
start_date = end_date - timedelta(days=90)

# Make timezone-aware
eastern = pytz.timezone('America/New_York')
start_date_tz = eastern.localize(start_date.replace(hour=0, minute=0, second=0, microsecond=0))

dividends = stock.dividends

print(f"Total dividends: {len(dividends)}")
print(f"Dividend index type: {type(dividends.index[0])}")
print(f"Start date: {start_date} (naive)")
print(f"Start date TZ: {start_date_tz} (aware)")

# This should now work!
try:
    recent_divs = dividends[dividends.index >= start_date_tz]
    print(f"\n✅ SUCCESS! Found {len(recent_divs)} recent dividends")
    for div_date, div_amount in recent_divs.head().items():
        print(f"  {div_date.strftime('%Y-%m-%d')}: ${div_amount:.4f}")
except Exception as e:
    print(f"\n❌ FAILED: {e}")

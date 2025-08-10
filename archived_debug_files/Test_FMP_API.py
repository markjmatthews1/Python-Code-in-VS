import requests
import pandas as pd

FMP_API_KEY = "QWHCIBxksyrCtnS3QOhV369o7bLQFAQh"
symbol = "EIC"

url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{symbol}?apikey={FMP_API_KEY}"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()
    dividends = data.get("historical", [])
    df = pd.DataFrame(dividends)

    if not df.empty:
        df["date"] = pd.to_datetime(df["date"])
        df.sort_values("date", ascending=False, inplace=True)
        print(df[["date", "dividend"]].head(12))  # Show last 12 payouts
    else:
        print("No dividend history found for", symbol)
else:
    print("API request failed with status:", response.status_code)
import requests
from requests_oauthlib import OAuth1
import time
from etrade_auth import get_etrade_session  # Assumes you have this function set up as in your project

SYMBOL = "TQQQ"  # Replace with your desired stock symbol
POLL_INTERVAL = 60  # seconds

def fetch_ohlc(session, base_url, symbol):
    url = f"{base_url}/v1/market/quote/{symbol}.json"
    params = {"detailFlag": "ALL"}
    response = session.get(url, params=params)
    print("=== E*TRADE HTTP Response ===")
    print(f"Requesting symbol: {symbol}")
    print("Status Code:", response.status_code)
    print("Headers:", dict(response.headers))
    print("Body:", response.text)
    print("=============================")
    if response.status_code == 200:
        data = response.json()
        quote_data = data.get("QuoteResponse", {}).get("QuoteData", [{}])[0]
        all_data = quote_data.get("All", {})
        ohlc = {
            "Open": all_data.get("open"),
            "High": all_data.get("high"),
            "Low": all_data.get("low"),
            "Close": all_data.get("lastTrade"),
        }
        print(f"Real-Time OHLC Data for {symbol}:")
        for key, value in ohlc.items():
            print(f"{key}: {value}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    session, base_url = get_etrade_session()
    while True:
        fetch_ohlc(session, base_url, SYMBOL)
        time.sleep(POLL_INTERVAL)
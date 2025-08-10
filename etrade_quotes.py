from etrade_auth import get_etrade_session
import os

def get_quotes(tickers):
    session, base_url = get_etrade_session()
    url = f"{base_url}/v1/market/quote/" + ",".join(tickers)
    headers = {"Accept": "application/json"}
    response = session.get(url, headers=headers, timeout=10)
    print(f"Status code: {response.status_code}")
    print(f"Raw response: {response.text[:500]}")

    if response.status_code == 401:
        if os.path.exists("etrade_tokens.pkl"):
            os.remove("etrade_tokens.pkl")
        print("Token expired, please re-run to re-authenticate.")
        return {}

    if response.status_code != 200:
        print(f"API Error: {response.status_code} - {response.text}")
        return {}

    try:
        data = response.json()
    except Exception as e:
        print(f"JSON decode error: {e}")
        return {}

    import json
    print("Full API response:", json.dumps(data, indent=2))

    quotes = {}
    for quote in data.get("QuoteResponse", {}).get("QuoteData", []):
        # Get symbol from Product
        symbol = None
        if "Product" in quote and "symbol" in quote["Product"]:
            symbol = quote["Product"]["symbol"]
        # Skip if there are error messages for this symbol
        if "messages" in quote:
            print(f"Skipping {symbol}: {quote['messages']}")
            continue
        last_trade = None
        if "All" in quote and "lastTrade" in quote["All"]:
            last_trade = quote["All"]["lastTrade"]
        elif "lastTrade" in quote:
            last_trade = quote["lastTrade"]
        if symbol and last_trade is not None:
            quotes[symbol.upper()] = last_trade
    print("Parsed quotes:", quotes)
    return quotes
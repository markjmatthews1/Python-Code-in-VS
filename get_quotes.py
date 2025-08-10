from etrade_auth import get_etrade_session

def get_quotes(symbols):
    """
    symbols: list of ticker strings
    Returns: dict {symbol: last_trade_price}
    """
    session, base_url = get_etrade_session()
    symbol_str = ",".join(symbols)
    url = f"{base_url}/v1/market/quote/{symbol_str}.json"
    params = {"detailFlag": "ALL"}
    response = session.get(url, params=params)
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}")
        return {}
    data = response.json()
    quotes = {}
    for quote_data in data.get("QuoteResponse", {}).get("QuoteData", []):
        symbol = quote_data.get("symbol")
        all_data = quote_data.get("All", {})
        last_trade = all_data.get("lastTrade")
        if symbol and last_trade is not None:
            quotes[symbol.upper()] = last_trade
    return quotes
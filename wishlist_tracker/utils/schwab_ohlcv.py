"""
utils/schwab_ohlcv.py
---------------------
Fetches real-time OHLCV data from Schwab for a list of tickers.
"""
import asyncio
import json
import os
import pandas as pd
from schwab.streaming import SchwabStreamer

TOKEN_FILE = "tokens.json"


def load_schwab_access_token():
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

async def fetch_ohlcv(symbols, on_bar):
    access_token = load_schwab_access_token()
    streamer = SchwabStreamer(oauth_token=access_token)
    await streamer.connect()
    await streamer.subscribe_chart_equity(symbols, on_bar)
    print(f"Subscribed to real-time OHLCV for: {symbols}")
    await streamer.run_forever()

# Example handler to collect bars into a DataFrame
class OHLCVCollector:
    def __init__(self):
        self.data = {}
    def __call__(self, msg):
        symbol = msg.get('key')
        bar = msg.get('content', {})
        if symbol not in self.data:
            self.data[symbol] = []
        self.data[symbol].append(bar)
    def to_dataframe(self, symbol):
        return pd.DataFrame(self.data.get(symbol, []))

# Usage example (async):
# collector = OHLCVCollector()
# asyncio.run(fetch_ohlcv(["AMD", "MSFU"], collector))
# df = collector.to_dataframe("AMD")

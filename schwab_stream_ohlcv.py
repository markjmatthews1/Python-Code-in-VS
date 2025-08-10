import asyncio
import json
import os
from schwab.streaming import SchwabStreamer

TOKEN_FILE = "tokens.json"
SYMBOLS = ["ETHU", "DFEN"]  # Or set dynamically

def load_schwab_access_token():
    """
    Loads the Schwab access token from tokens.json (nested structure).
    """
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

async def on_chart_message(msg):
    """
    Handler for each incoming OHLCV bar.
    """
    print("Received OHLCV bar:", msg)
    # You can add code here to append to a DataFrame or CSV

async def main():
    access_token = load_schwab_access_token()
    streamer = SchwabStreamer(oauth_token=access_token)
    await streamer.connect()
    await streamer.subscribe_chart_equity(SYMBOLS, on_chart_message)
    print(f"Subscribed to real-time OHLCV for: {SYMBOLS}")
    await streamer.run_forever()

if __name__ == "__main__":
    asyncio.run(main())
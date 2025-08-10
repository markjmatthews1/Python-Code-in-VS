import requests
import json

# Replace with your Schwab API credentials
API_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
ACCESS_TOKEN = "I0.b2F1dGgyLmJkYy5zY2h3YWIuY29t.sFpF82KyP41YGsQki332xezICIuSuewWCs776w_hiLY@"
BASE_URL = "https://api.schwab.com/v1/quotes"

def get_streaming_quotes(symbols):
    """
    Fetch streaming quotes for a list of symbols.
    """
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    params = {
        "symbols": ",".join(symbols),
        "apikey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, headers=headers, params=params)
        response.raise_for_status()  # Raise an error for bad status codes
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        print(f"Error fetching quotes: {e}")
        return None

# Example usage
if __name__ == "__main__":
    stock_symbols = ["AAPL", "MSFT", "GOOGL"]  # Replace with your desired symbols
    quotes = get_streaming_quotes(stock_symbols)
    if quotes:
        print(json.dumps(quotes, indent=4))


timer.sleep(10)

import schwabdev
import requests
import webbrowser
import base64
import json
import time
import asyncio
from flask import Flask, request, redirect, Response
from threading import Thread
#from schwabdev.client import SchwabClient
#from schwabdev.stream import StreamClient
from schwab.auth import easy_client
#from schwabdev import SchwabClient


APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
APP_SECRET = "h9YybKHnDVoDM1Jw"

#app_secret="h9YybKHnDVoDM1Jw",
#callback_url="https://127.0.0.1:5000/callback",

# Initialize Schwab API client
# ================== CONFIGURATION =====================

client = schwabdev.Client(
    app_key='n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai',
    app_secret='h9YybKHnDVoDM1Jw'
)
    

#client.update_tokens_auto()

streamer=client.stream

def response_handler(response):
    print(response)

streamer.start(response_handler)

streamer.send(streamer.level_one_equities("AMD", "012345"))

time.sleep(10)



timer.sleep(10)
TOKEN_FILE = "tokens.json"  # Define the variable at the top of your script
def load_tokens():
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        return token_data
    except FileNotFoundError:
        return None

async def main():
    await client.stream_login()

    def handle_quote(data):
        print("Quote update:", data)

    await client.add_handler('QUOTE', handle_quote)
    await client.subscribe('QUOTE', symbols=['AAPL', 'MSFT'])

    while True:
        await client.read_stream()

asyncio.run(main())




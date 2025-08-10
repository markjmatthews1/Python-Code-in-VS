account_number=91562183
import os
import logging
import asyncio
from tracemalloc import start
from unittest import result
from dotenv import load_dotenv
import schwabdev
import requests

app_key = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
app_secret = "h9YybKHnDVoDM1Jw"
callback_url = "127.0.0.1:5000"
account_number = 91562183

def on_quote_callback(data):
    print("Received quote:", data)

load_dotenv()
logging.basicConfig(level=logging.INFO)

client = schwabdev.Client(
    os.getenv("app_key"),
    os.getenv("app_secret"),
    #os.getenv("callback_url")
    )

#client.update_tokens_auto()

#print("Tokens attributes:", dir(client.tokens))
# --- Add this block to capture the failing REST request ---
#access_token = client.tokens.access_token

#headers = {
 #   "Authorization": f"Bearer {access_token}",
  #  "accept": "application/json"
#}
#url = "https://api.schwabapi.com/trader/v1/accounts"  # Example: replace with the endpoint you want to test

#response = requests.get(url, headers=headers)
#print("Request URL:", url)
#print("Request Headers:", {k: (v if k != "Authorization" else "Bearer [REDACTED]") for k, v in headers.items()})
#print("Response Status:", response.status_code)
#print("Response Headers:", dict(response.headers))
#print("Response Body:", response.text)
#print("Correlation ID:", response.headers.get("X-Correlation-ID"))
streamer = client.stream

def my_data_handler(data):
    print("Received streaming data:", data)
    # Implement your data processing logic here

# Add a handler for Level One Equities data
streamer.add_level_one_equity_handler(my_data_handler)

# Subscribe to Level One Equities data for 'AMD' with specific fields
streamer.level_one_equities_subs('AMD', fields=[0, 1, 2, 3, 4, 5])
print("Subscription result:", result)
print("subscriptions:", streamer.subscriptions)
print("streamer attributes:", dir(streamer))
streamer.start()
print("Subscription result:", result)
print("subscriptions:", streamer.subscriptions)
print("streamer attributes:", dir(streamer))

# Keep the script running to receive data (e.g., using a loop or sleep)
import time
try:
    while True:
        time.sleep(5)
except KeyboardInterrupt:
    print("Streaming stopped.")
finally:
    streamer.stop() # Ensure the stream is properly closed on exit

 

print("line 44:", dir(streamer))
print("line 45:", streamer.level_one_equities.__doc__)
print([m for m in dir(streamer) if "handler" in m])


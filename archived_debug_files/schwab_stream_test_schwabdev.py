import os
import logging
import asyncio
import time
from dotenv import load_dotenv
import schwabdev

account_number=91562183

# ✅ Load environment variables
load_dotenv()

# ✅ Validate API credentials
if len(os.getenv("app_key")) != 32 or len(os.getenv("app_secret")) != 16:
    raise Exception("⚠️ Invalid app key or secret in .env file.")

# ✅ Configure logging for debugging
logging.basicConfig(level=logging.INFO)

# ✅ Initialize Schwabdev client (handles authentication internally)
client = schwabdev.Client(os.getenv("app_key"), os.getenv("app_secret"), os.getenv("callback_url"))

# ✅ Access the built-in streamer
streamer = client.stream

# ✅ Start the streamer asynchronously
async def start_stream():
    await streamer._start_streamer()
    print("✅ Streamer Started Using _start_streamer!")

asyncio.run(start_stream())

# ✅ Subscribe to stock market data (Example: AMD & INTC)
streamer.send(streamer.level_one_equities(["AMD", "INTC"], ["0", "1", "2", "3", "4", "5", "6", "7", "8"]))
print("✅ Stock Subscription Sent!")

# ✅ Subscribe to forex market data (Example: EUR/USD)
streamer.send(streamer.level_one_forex("EUR/USD", ["0", "1", "2", "3", "4", "5", "6", "7", "8"]))
print("✅ Forex Subscription Sent!")

# ✅ Start auto-streaming (waits for market hours)
streamer.start_auto()
print("⏳ Waiting for active trading hours... Stream will launch automatically.")

# ✅ Print Streamer Object Details
print("🔍 Streamer Object:", type(streamer))
print("✅ Stream Active?", streamer.active)

# ⏳ Keep the stream running until market hours begin
while True:
    print("⏳ Still waiting for market hours...")
    time.sleep(60)  # Check every minute


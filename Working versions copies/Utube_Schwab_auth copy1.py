import base64
import requests
import threading
import webbrowser
from flask import Flask, request, redirect, Response
from loguru import logger
import time
import threading
import json


logger.add("debug.log", level="DEBUG")

# ================== CONFIGURATION =====================
APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
APP_SECRET = "h9YybKHnDVoDM1Jw"
REDIRECT_URI = "https://127.0.0.1:5000/callback"
AUTH_URL = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={APP_KEY}&redirect_uri={REDIRECT_URI}"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"

# ================== FLASK SERVER ======================
REDIRECT_URL = "https://127.0.0.1:5000/callback"  # Update to match your registered OAuth redirect

app = Flask(__name__)
SCHWAB_AUTH_URL = "https://api.schwab.com/oauth2/authorize"

# Global token storage
TOKEN_DATA = {}

# ================== TOKEN STORAGE ======================
def save_tokens():
    """Saves tokens to a local JSON file for persistence across runs."""
    with open("tokens.json", "w") as f:
        json.dump(TOKEN_DATA, f)
    logger.info("💾 Tokens saved to tokens.json.")

def load_tokens():
    """Loads tokens from a local JSON file if they exist."""
    global TOKEN_DATA
    try:
        with open("tokens.json", "r") as f:
            TOKEN_DATA = json.load(f)
        logger.info("🔄 Loaded saved tokens.")
    except FileNotFoundError:
        logger.warning("⚠️ No saved tokens found. Fresh authentication required.")

# Load tokens at startup
load_tokens()

# ================== FLASK ROUTES ======================
@app.route("/callback")  # Ensure this matches the REDIRECT_URL
def auth_callback():
    """Handles OAuth callback and exchanges authorization code for tokens."""
    auth_code = request.args.get("code")
    print(f"🔍 Received Authorization Code: {auth_code}")  # Debugging
    if auth_code:
        logger.success(f"✅ Authorization code received: {auth_code}")
        token_info = exchange_for_tokens(auth_code)
        return Response("Authorization successful. You can close this window.", status=200)
    else:
        logger.warning("⚠️ No authorization code received!")
        return Response("Error: No authorization code provided.", status=400)

@app.route("/callback")
def login():
    """Redirects user to Schwab's OAuth authentication URL."""
    auth_url = f"{SCHWAB_AUTH_URL}?client_id={APP_KEY}&redirect_uri={REDIRECT_URL}&response_type=code"
    return redirect(auth_url, code=302)

# ================== TOKEN MANAGEMENT ======================
def exchange_for_tokens(auth_code):
    """Exchanges authorization code for tokens and schedules auto-refresh."""
    print(f"🔄 Exchanging Auth Code: {auth_code}")  # Debugging

    response = requests.post("https://api.schwab.com/token", headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "app_key": APP_KEY
    })

    logger.debug(f"🔍 Raw response content: {response.text}")

    try:
        token_info = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"⚠️ JSON decode error: {e}")
        return {}

    if "access_token" in token_info:
        TOKEN_DATA["access_token"] = token_info["access_token"]
        TOKEN_DATA["refresh_token"] = token_info["refresh_token"]
        TOKEN_DATA["expires_at"] = time.time() + token_info["expires_in"] - 120  # Refresh 2 mins before expiration

        save_tokens()  # **Store tokens persistently**
        schedule_token_refresh()
        logger.success("✅ Tokens stored and refresh scheduled.")
    else:
        logger.error("⚠️ Token exchange failed!")

    return token_info

def refresh_access_token():
    """Automatically refreshes the access token before expiration."""
    if "refresh_token" not in TOKEN_DATA:
        logger.warning("⚠️ No refresh token found! Authentication may be required.")
        return

    logger.info("🔄 Refreshing access token...")

    response = requests.post("https://api.schwab.com/token", headers={
        "Content-Type": "application/x-www-form-urlencoded"
    }, data={
        "grant_type": "refresh_token",
        "refresh_token": TOKEN_DATA["refresh_token"],
        "app_key": APP_KEY
    })

    try:
        token_info = response.json()
    except requests.exceptions.JSONDecodeError as e:
        logger.error(f"⚠️ Token refresh JSON decode error: {e}")
        return
    
    if "access_token" in token_info:
        TOKEN_DATA["access_token"] = token_info["access_token"]
        TOKEN_DATA["expires_at"] = time.time() + token_info.get("expires_in", 1800) - 120  # Default 30 min expiration

        save_tokens()  # **Save refreshed tokens for future runs**
        schedule_token_refresh()
        logger.success("✅ Token refreshed successfully!")
    else:
        logger.error("⚠️ Token refresh failed!")

def schedule_token_refresh():
    """Schedules a token refresh before expiration."""
    delay = TOKEN_DATA.get("expires_at", time.time()) - time.time()
    if delay > 0:
        threading.Timer(delay, refresh_access_token).start()
        logger.info(f"⏳ Refresh scheduled in {round(delay / 60, 2)} minutes.")

# ================== FLASK SERVER START ======================
def start_flask():
    """Starts Flask server with SSL."""
    app.run(host="127.0.0.1", port=5000, ssl_context="adhoc")

# ================== MAIN =============================
def main():
    logger.info("🚀 Starting Flask server. It will remain active until manually stopped...")
    webbrowser.open(f"{SCHWAB_AUTH_URL}?client_id={APP_KEY}&redirect_uri={REDIRECT_URL}&response_type=code")
    print("🌍 Opened browser for Schwab login")  # Debugging
    app.run(host="127.0.0.1", port=5000, ssl_context=("C:/Users/mjmat/mkcert/127.0.0.1.pem", "C:/Users/mjmat/mkcert/127.0.0.1-key.pem"))

if __name__ == "__main__":
    main()
import requests
import webbrowser
import base64
import json
import time
from flask import Flask, request, redirect, Response

# ================== CONFIGURATION =====================
APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
APP_SECRET = "h9YybKHnDVoDM1Jw"
REDIRECT_URL = "https://127.0.0.1:5000/callback"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
AUTH_URL = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={APP_KEY}&redirect_uri={REDIRECT_URL}"

app = Flask(__name__)

# ================== UTILITY FUNCTIONS =====================
def load_tokens():
    """Loads saved tokens from file."""
    try:
        with open("tokens.json", "r") as f:
            token_data = json.load(f)
        print("🔄 Loaded tokens from file:", token_data)
        return token_data
    except FileNotFoundError:
        print("⚠️ No saved tokens found. Starting fresh.")
        return None

def save_tokens(token_data):
    """Saves tokens with expiration tracking."""
    token_data["expires_at"] = time.time() + token_data.get("expires_in", 1800)
    with open("tokens.json", "w") as f:
        json.dump(token_data, f, indent=2)
    print("💾 Tokens saved to tokens.json")

# ================== FLASK ROUTES ======================
@app.route("/callback")
def auth_callback():
    """Handles OAuth callback and exchanges authorization code for tokens."""
    auth_code = request.args.get("code")
    if auth_code:
        print(f"🔍 Received Authorization Code: {auth_code}")
        return exchange_for_tokens(auth_code)
    else:
        return Response("Error: No authorization code provided.", status=400)

@app.route("/login")
def login():
    """Redirects user to Schwab's OAuth authentication URL."""
    return redirect(AUTH_URL, code=302)

# ================== TOKEN EXCHANGE =====================
def exchange_for_tokens(auth_code):
    """Exchanges authorization code for tokens and saves them."""
    auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
    
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    response = requests.post(TOKEN_URL, headers=headers, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URL
    })

    if response.status_code == 200:
        token_info = response.json()
        print("✅ Tokens received:", token_info)
        save_tokens(token_info)
        return Response("Authorization successful! Tokens stored.", status=200)
    else:
        return Response("Error decoding token response!", status=500)

def refresh_access_token():
    """Refreshes the access token when it expires."""
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("⚠️ No refresh token available. Reauthentication required.")
        return None

    # ✅ Corrected Authorization Header (adds Base64 encoding for client authentication)
    auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }

    # ✅ Remove `redirect_uri`, API doesn't require it for token refresh
    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": APP_KEY
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        new_tokens = response.json()
        save_tokens(new_tokens)
        print("🔄 Access token refreshed and saved.")
        return new_tokens
    else:
        print(f"❌ Failed to refresh token: {response.status_code} - {response.text}")
        return None

def fetch_quote(symbol="AAPL"):
    """Fetches quote data using the saved access token."""
    tokens = load_tokens()
    
    if tokens and time.time() > tokens["expires_at"]:
        print("⏰ Access token expired. Refreshing...")
        tokens = refresh_access_token()

    if not tokens:
        print("❌ No valid tokens available.")
        return

    headers = {
        "Authorization": f"Bearer {tokens['access_token']}",
        "Accept": "application/json"
    }

    url = f"https://api.schwabapi.com/marketdata/v1/quotes?symbols={symbol}"

    print(f"🔍 Fetching quote from: {url}")
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print(f"📊 Quote data for {symbol}:")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"⚠️ Failed to fetch quote. Status {response.status_code}: {response.text}")

# ================== MAIN =============================
def main():
    print("🚀 Starting Flask server...")

    existing_tokens = load_tokens()
    if existing_tokens:
        print("✅ Token exists. Testing refresh...")
        fetch_quote("MSFT")
        return

    webbrowser.open(AUTH_URL)
    app.run(
        host="127.0.0.1",
        port=5000,
        ssl_context=("C:/Users/mjmat/mkcert/127.0.0.1.pem", "C:/Users/mjmat/mkcert/127.0.0.1-key.pem")
    )

if __name__ == "__main__":
    main()
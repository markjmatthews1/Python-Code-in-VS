import requests
import webbrowser
import base64
import json
import time
from flask import Flask, request, redirect, Response
import threading
import os
import tkinter as tk
from tkinter import messagebox
from playsound import playsound
import asyncio
import threading
import schwabdev


# ================== CONFIGURATION =====================
APP_KEY = "n3uMFJH8tsA9z2SB2ag0sqNUNm4uPjai"
APP_SECRET = "h9YybKHnDVoDM1Jw"
REDIRECT_URL = "https://127.0.0.1:5000/callback"
TOKEN_URL = "https://api.schwabapi.com/v1/oauth/token"
AUTH_URL = f"https://api.schwabapi.com/v1/oauth/authorize?client_id={APP_KEY}&redirect_uri={REDIRECT_URL}"

TOKEN_FILE = "tokens.json"
REFRESH_INTERVAL = 29 * 60  # 29 minutes

app = Flask(__name__)

# ================== POPUP & AUDIO ALERT =====================
import os

SCHWAB_AUTH_ALERT_PATH = "C:/Users/mjmat/Pythons_Code_Files/schwab_auth_alert.mp3"  # Update if needed

def schwab_auth_popup_and_sound(auth_url):
    # Play audio in a background thread
    def play_auth_alert():
        try:
            playsound(SCHWAB_AUTH_ALERT_PATH)
        except Exception as e:
            print("Audio alert failed:", e)
    threading.Thread(target=play_auth_alert, daemon=True).start()

    # Tkinter popup
    def open_browser():
        webbrowser.open(auth_url)

    root = tk.Tk()
    root.title("Schwab OAuth Required")
    root.geometry("500x220")
    root.configure(bg="#222244")

    label = tk.Label(root, text="Schwab authentication is required.\nClick the button below to open the Schwab login page.", font=("Arial", 13), bg="#222244", fg="white")
    label.pack(pady=20)

    url_btn = tk.Button(root, text="Open Schwab OAuth URL", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=open_browser)
    url_btn.pack(pady=10)

    label2 = tk.Label(root, text="After logging in, return to this app to continue.", font=("Arial", 12), bg="#222244", fg="white")
    label2.pack(pady=10)

    root.mainloop()

    def check_auth_complete():
        if os.path.exists("auth_complete.txt"):
            root.destroy()
        else:
            root.after(1000, check_auth_complete)

    check_auth_complete()
    root.mainloop()

# ================== TOKEN MANAGEMENT =====================
def load_tokens():
    try:
        with open(TOKEN_FILE, "r") as f:
            token_data = json.load(f)
        # Always use the nested dictionary
        return token_data.get("token_dictionary", {})
    except FileNotFoundError:
        return None

def save_tokens(token_data):
    # Save tokens under "token_dictionary" key
    wrapper = {
        "access_token_issued": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "refresh_token_issued": time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime()),
        "token_dictionary": token_data
    }
    wrapper["token_dictionary"]["expires_at"] = time.time() + token_data.get("expires_in", 1800)
    with open(TOKEN_FILE, "w") as f:
        json.dump(wrapper, f, indent=2)

def get_valid_access_token():
    """Returns a valid access token, refreshing if needed."""
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("No tokens found. Please run schwab_auth.py to authenticate.")
    if time.time() > tokens.get("expires_at", 0):
        tokens = refresh_access_token()
        if not tokens:
            raise RuntimeError("Failed to refresh token. Please re-authenticate.")
    return tokens["access_token"]

def ensure_fresh_token(buffer_seconds=120):
    """
    Ensures the access token is valid for at least buffer_seconds into the future.
    Refreshes if needed.
    """
    tokens = load_tokens()
    if not tokens:
        raise RuntimeError("No tokens found. Please run schwab_auth.py to authenticate.")
    if time.time() > tokens.get("expires_at", 0) - buffer_seconds:
        refresh_access_token()

def refresh_access_token():
    tokens = load_tokens()
    if not tokens or "refresh_token" not in tokens:
        print("No refresh token available. Please run Schwab_auth.py directly to re-authenticate.")
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        schwab_auth_popup_and_sound(AUTH_URL)
        return None

    auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "refresh_token",
        "refresh_token": tokens["refresh_token"],
        "client_id": APP_KEY
    }
    response = requests.post(TOKEN_URL, headers=headers, data=data)
    if response.status_code == 200:
        new_tokens = response.json()
        save_tokens(new_tokens)
        print("Access token refreshed and saved.")
        return new_tokens
    else:
        print(f"Failed to refresh token: {response.status_code} - {response.text}")
        print("Please run Schwab_auth.py directly to re-authenticate.")
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
        schwab_auth_popup_and_sound(AUTH_URL)
        return None

# ================== DATA FETCHING =====================
def fetch_quote(symbol="AAPL"):
    """Fetches quote data using the current access token. Returns dict or None."""
    try:
        access_token = get_valid_access_token()
    except Exception as e:
        print(f"Token error: {e}")
        return None

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    url = f"https://api.schwabapi.com/marketdata/v1/quotes?symbols={symbol}"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch quote. Status {response.status_code}: {response.text}")
        return None

# ================== FLASK ROUTES FOR OAUTH =====================
@app.route("/callback")
def auth_callback():
    auth_code = request.args.get("code")
    if auth_code:
        return exchange_for_tokens(auth_code)
    else:
        return Response("Error: No authorization code provided.", status=400)

@app.route("/login")
def login():
    return redirect(AUTH_URL, code=302)

def exchange_for_tokens(auth_code):
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
        save_tokens(token_info)
        # --- Add this block to signal the popup to close ---
        with open("auth_complete.txt", "w") as f:
            f.write("done")
        # ---------------------------------------------------
        return Response("Authorization successful! Tokens stored.", status=200)
    else:
        return Response("Error decoding token response!", status=500)

# ================== OPTIONAL: AUTO REFRESH THREAD =====================
def start_auto_refresh():
    def refresh_loop():
        while True:
            time.sleep(REFRESH_INTERVAL)
            try:
                refresh_access_token()
            except Exception as e:
                print(f"Auto-refresh error: {e}")
    t = threading.Thread(target=refresh_loop, daemon=True)
    t.start()

# ================== MAIN (for first-time auth new tokens not refresh) =====================
def main():
    print("Starting Schwab OAuth flow...")
    existing_tokens = load_tokens()
    if not existing_tokens:
        # Start Flask server in a background thread
        def run_flask():
            app.run(
                host="127.0.0.1",
                port=5000,
                ssl_context=("C:/Users/mjmat/mkcert/127.0.0.1.pem", "C:/Users/mjmat/mkcert/127.0.0.1-key.pem")
            )
        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Show popup and play sound
        schwab_auth_popup_and_sound(AUTH_URL)

if __name__ == "__main__":
    main()
    # Only print the test quote if run directly, not as a subprocess
    tokens = load_tokens()
    if tokens:
        print("Token exists. Fetching MSFT quote as test...")
        print(json.dumps(fetch_quote("MSFT"), indent=2))


def fetch_batch_quotes(symbols):
    """
    Fetches real-time quote data for a list of symbols from Schwab.
    Returns a dict: symbol -> quote dict.
    """
    if isinstance(symbols, (list, tuple)):
        symbol_str = ",".join(symbols)
    else:
        symbol_str = str(symbols)
    try:
        access_token = get_valid_access_token()
    except Exception as e:
        print(f"Token error: {e}")
        return {}
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    url = f"https://api.schwabapi.com/marketdata/v1/quotes?symbols={symbol_str}"
    response = requests.get(url, headers=headers)
    print(f"Schwab API URL: {url}")
    print(f"Schwab API Status: {response.status_code}")
    print(f"Schwab API Response: {response.text}")  # <--- ADD THIS LINE
    if response.status_code == 200:
        data = response.json()
        return data.get("quotes", data)
    else:
        print(f"Failed to fetch batch quotes. Status {response.status_code}: {response.text}")
        return {}
    

# Make sure StreamClient is imported from your Schwab SDK
# from schwab_streaming_sdk import StreamClient

def get_streamer(APP_KEY, APP_SECRET, response_handler):
    client = schwabdev.Client(app_key=APP_KEY, app_secret=APP_SECRET)
    streamer = client.stream
    streamer.start(response_handler)
    return streamer
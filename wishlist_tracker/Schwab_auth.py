import requests
import webbrowser
import base64
import json
import time
from datetime import datetime
from flask import Flask, request, redirect, Response
import threading
import os
import tkinter as tk
from tkinter import messagebox
# With:
try:
    from playsound import playsound
except ImportError:
    print("playsound not available, audio notifications disabled")
    def playsound(file):
        pass  # Do nothing if playsound not available
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

    # Add manual close button as backup
    close_btn = tk.Button(root, text="Close (if auth is complete)", font=("Arial", 10), bg="#f44336", fg="white", command=root.destroy)
    close_btn.pack(pady=5)

    # Global flag to track authentication status
    auth_completed = False
    check_count = 0
    MAX_CHECKS = 300  # 5 minutes timeout (300 seconds)

    # Improved auto-close check function
    def check_auth_complete():
        nonlocal auth_completed, check_count
        check_count += 1
        
        # Check for multiple possible completion signals
        signals = [
            os.path.exists("auth_complete.txt"),
            os.path.exists(TOKEN_FILE) and check_recent_token()
        ]
        
        if any(signals) and not auth_completed:
            auth_completed = True
            print("Authentication complete detected. Closing popup...")
            # Clean up signal files
            try:
                if os.path.exists("auth_complete.txt"):
                    os.remove("auth_complete.txt")
            except Exception as e:
                print(f"Warning: Could not remove auth_complete.txt: {e}")
            root.destroy()
            return
        elif check_count >= MAX_CHECKS:
            print("Authentication timeout reached. Manual close required.")
            return
        else:
            # Check again in 1 second
            root.after(1000, check_auth_complete)

    def check_recent_token():
        """Check if we have a recently created token"""
        try:
            if not os.path.exists(TOKEN_FILE):
                return False
            # Check if token file was modified in the last 30 seconds
            mod_time = os.path.getmtime(TOKEN_FILE)
            return time.time() - mod_time < 30
        except:
            return False

    # Start the auto-close checking immediately
    root.after(1000, check_auth_complete)
    
    # Start the main event loop
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

debug_token_status = None # call this function to check token status

def debug_token_status():
    """Debug function to check token status"""
    try:
        with open("tokens.json", "r") as f:
            tokens = json.load(f)
        
        print("=== TOKEN DEBUG ===")
        print(f"Access token exists: {'schwab' in tokens and 'access_token' in tokens['schwab']}")
        print(f"Refresh token exists: {'schwab' in tokens and 'refresh_token' in tokens['schwab']}")
        
        if 'schwab' in tokens and 'expires_at' in tokens['schwab']:
            expires_at = tokens['schwab']['expires_at']
            current_time = time.time()
            print(f"Token expires at: {datetime.fromtimestamp(expires_at)}")
            print(f"Current time: {datetime.fromtimestamp(current_time)}")
            print(f"Time until expiry: {expires_at - current_time} seconds")
        
        print("=== END TOKEN DEBUG ===")
    except Exception as e:
        print(f"Error checking token status: {e}")

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
    print(f"Exchanging authorization code for tokens...")
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
        print(f"Successfully received tokens from Schwab API")
        
        # Save tokens immediately
        save_tokens(token_info)
        print(f"Tokens saved to {TOKEN_FILE}")
        
        # Create multiple completion signals for reliability
        try:
            # Primary signal file
            with open("auth_complete.txt", "w") as f:
                f.write(f"completed_at_{int(time.time())}")
            print("Auth completion signal file created")
            
            # Secondary signal - update token file timestamp
            os.utime(TOKEN_FILE, None)  # Touch the file to update timestamp
            print("Token file timestamp updated")
            
        except Exception as e:
            print(f"Warning: Could not create completion signals: {e}")
        
        # Give a moment for signals to be detected
        time.sleep(0.5)
            
        return Response("""
        <html>
        <head><title>Authorization Successful</title></head>
        <body style='font-family: Arial; text-align: center; margin-top: 100px;'>
            <h2 style='color: green;'>Authorization Successful!</h2>
            <p>Tokens have been stored successfully.</p>
            <p>The popup window should close automatically.</p>
            <p>You may close this browser tab.</p>
            <script>
                // Try to close the window after a short delay
                setTimeout(function() {
                    window.close();
                }, 2000);
            </script>
        </body>
        </html>
        """, status=200, mimetype='text/html')
    else:
        print(f"Token exchange failed: {response.status_code} - {response.text}")
        return Response(f"""
        <html>
        <head><title>Authorization Failed</title></head>
        <body style='font-family: Arial; text-align: center; margin-top: 100px;'>
            <h2 style='color: red;'>Authorization Failed</h2>
            <p>Error: {response.status_code}</p>
            <p>{response.text}</p>
            <p>Please try again.</p>
        </body>
        </html>
        """, status=500, mimetype='text/html')

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
    if existing_tokens:
        print("Valid tokens already exist. No authentication needed.")
        return
    
    print("No existing tokens found. Starting authentication process...")
    
    # Clean up any stale signal files
    try:
        if os.path.exists("auth_complete.txt"):
            os.remove("auth_complete.txt")
            print("Cleaned up stale auth signal file")
    except:
        pass
    
    # Start Flask server in a background thread
    print("Starting Flask server for OAuth callback...")
    def run_flask():
        app.run(
            host="127.0.0.1",
            port=5000,
            ssl_context=("C:/Users/mjmat/mkcert/127.0.0.1.pem", "C:/Users/mjmat/mkcert/127.0.0.1-key.pem"),
            debug=False,
            use_reloader=False
        )
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Give Flask a moment to start
    time.sleep(1)
    print("Flask server started successfully")

    # Show popup and play sound
    print("Displaying authentication popup...")
    schwab_auth_popup_and_sound(AUTH_URL)
    
    # Wait a moment for potential completion
    time.sleep(2)
    
    # Check if authentication completed
    final_tokens = load_tokens()
    if final_tokens:
        print("Authentication completed successfully!")
    else:
        print("Authentication may not have completed. Check for any error messages above.")

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
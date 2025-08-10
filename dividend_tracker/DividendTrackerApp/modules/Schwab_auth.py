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
    root.geometry("500x280")
    root.configure(bg="#222244")
    
    # Make window stay on top and centered
    root.attributes('-topmost', True)
    root.update_idletasks()
    
    # Center the window
    x = (root.winfo_screenwidth() // 2) - (500 // 2)
    y = (root.winfo_screenheight() // 2) - (280 // 2)
    root.geometry(f"500x280+{x}+{y}")

    label = tk.Label(root, text="Schwab Authentication Required\n\nCRITICAL: You have only 30 seconds after completing\nthe Schwab login to exchange the authorization code!\n\nWork quickly once you click 'Allow' on Schwab's site.", font=("Arial", 12), bg="#222244", fg="white", justify="center")
    label.pack(pady=20)

    url_btn = tk.Button(root, text="Open Schwab Login", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=open_browser, height=2)
    url_btn.pack(pady=10)

    status_label = tk.Label(root, text="Waiting for authentication...", font=("Arial", 10), bg="#222244", fg="yellow")
    status_label.pack(pady=5)

    # Add manual close button as backup
    close_btn = tk.Button(root, text="Close (Auth Complete)", font=("Arial", 10), bg="#f44336", fg="white", command=root.destroy)
    close_btn.pack(pady=10)

    # Timer display - shows 30 second countdown from Schwab's restriction
    timer_label = tk.Label(root, text="Complete login quickly - 30 sec limit!", font=("Arial", 9), bg="#222244", fg="cyan")
    timer_label.pack(pady=2)

    # Fast auto-close check function optimized for 30-second Schwab limit
    def check_auth_complete():
        # Check for auth completion signal file every 200ms for fast response
        if os.path.exists("auth_complete.txt"):
            print("Authentication complete detected. Closing popup...")
            status_label.config(text="Authentication successful! Closing...", fg="green")
            timer_label.config(text="Success - Tokens saved!")
            root.update()
            
            # Clean up the signal file immediately
            def cleanup_and_close():
                try:
                    if os.path.exists("auth_complete.txt"):
                        os.remove("auth_complete.txt")
                        print("Cleaned up auth completion signal file")
                except Exception as e:
                    print(f"Note: Could not remove auth completion file: {e}")
                root.destroy()
            
            # Close quickly to get out of the way
            root.after(1500, cleanup_and_close)
            return
        else:
            # Check again in 200ms for very fast response within 30-second window
            root.after(200, check_auth_complete)

    # Start the auto-close checking after a brief delay
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
    print("� URGENT: Processing authorization code (30-second limit from Schwab!)")
    start_time = time.time()
    
    auth_header = base64.b64encode(f"{APP_KEY}:{APP_SECRET}".encode()).decode()
    headers = {
        "Authorization": f"Basic {auth_header}",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    
    # Make the token exchange request immediately
    response = requests.post(TOKEN_URL, headers=headers, data={
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URL
    })
    
    elapsed = time.time() - start_time
    print(f"⏱️ Token exchange took {elapsed:.2f} seconds")
    
    if response.status_code == 200:
        token_info = response.json()
        print("✅ Token exchange successful! Saving immediately...")
        
        # Save tokens as fast as possible - no retries to save time
        try:
            save_tokens(token_info)
            print("✅ Tokens saved!")
            
            # Quick verification
            saved_tokens = load_tokens()
            if saved_tokens and "access_token" in saved_tokens:
                print(f"✅ Tokens verified in {time.time() - start_time:.2f} total seconds!")
            else:
                print("⚠️ Quick verification failed but tokens may be saved")
        except Exception as e:
            print(f"❌ CRITICAL: Token save failed: {e}")
            return Response("""
            <html>
            <head><title>Schwab Auth Error</title></head>
            <body style="font-family: Arial; text-align: center; margin-top: 100px;">
            <h2 style="color: red;">❌ Token Save Failed</h2>
            <p>Error during token save: {}</p>
            <p>Please try authentication again.</p>
            </body>
            </html>
            """.format(str(e)), status=500, mimetype='text/html')
        
        # Signal completion immediately - no delays
        try:
            with open("auth_complete.txt", "w") as f:
                f.write(f"completed_{int(time.time())}")
            print("✅ Auth completion signal created")
        except Exception as e:
            print(f"Warning: Could not create completion signal: {e}")
        
        total_time = time.time() - start_time
        print(f"🎯 Total process time: {total_time:.2f} seconds (within 30-sec limit: {'✅' if total_time < 25 else '⚠️'})")
            
        return Response(f"""
        <html>
        <head><title>Schwab Auth Complete</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 100px;">
        <h2 style="color: green;">✅ Authorization Successful!</h2>
        <p>Tokens exchanged and saved in {total_time:.1f} seconds.</p>
        <p><strong>This window will close automatically.</strong></p>
        <script>
        // Close quickly since we're racing against 30-second limit
        setTimeout(function() {{
            window.close();
        }}, 2000);
        </script>
        </body>
        </html>
        """, status=200, mimetype='text/html')
    else:
        print(f"Token exchange failed: {response.status_code} - {response.text}")
        return Response(f"""
        <html>
        <head><title>Schwab Auth Error</title></head>
        <body style="font-family: Arial; text-align: center; margin-top: 100px;">
        <h2 style="color: red;">❌ Authorization Failed</h2>
        <p>Error: {response.status_code}</p>
        <p>Details: {response.text}</p>
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
    print("🔐 Starting Schwab OAuth flow...")
    
    # Clean up any leftover auth completion files
    try:
        if os.path.exists("auth_complete.txt"):
            os.remove("auth_complete.txt")
            print("✅ Cleaned up previous auth completion file")
    except:
        pass
    
    existing_tokens = load_tokens()
    if existing_tokens and "access_token" in existing_tokens:
        print("✅ Existing valid tokens found. Testing connection...")
        try:
            # Test the tokens with a simple API call
            access_token = get_valid_access_token()
            print("✅ Schwab authentication is working!")
            return
        except Exception as e:
            print(f"⚠️ Existing tokens failed: {e}")
            print("🔄 Starting fresh authentication...")
    else:
        print("🆕 No existing tokens found. Starting fresh authentication...")
    
    # Start Flask server in a background thread
    def run_flask():
        try:
            app.run(
                host="127.0.0.1",
                port=5000,
                ssl_context=("C:/Users/mjmat/mkcert/127.0.0.1.pem", "C:/Users/mjmat/mkcert/127.0.0.1-key.pem"),
                debug=False  # Disable debug mode to reduce output
            )
        except Exception as e:
            print(f"❌ Flask server error: {e}")
    
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    
    # Give Flask minimal time to start 
    time.sleep(1.5)
    print("🌐 Flask server started. Opening authentication popup...")
    print("🚨 REMEMBER: Schwab limits authorization codes to 30 seconds!")
    print("💨 Work quickly after clicking 'Allow' on Schwab's website!")

    # Show popup and play sound
    schwab_auth_popup_and_sound(AUTH_URL)
    
    # After popup closes, do quick verification
    print("🔍 Quick verification of authentication results...")
    
    # Single quick verification attempt
    try:
        final_tokens = load_tokens()
        if final_tokens and "access_token" in final_tokens:
            # Quick test of the token
            test_token = get_valid_access_token()
            if test_token:
                print("✅ Authentication successful! Tokens are valid.")
                return True
            else:
                print("⚠️ Tokens exist but validation failed")
        else:
            print("⚠️ No valid tokens found")
    except Exception as e:
        print(f"⚠️ Token verification failed: {e}")
    
    print("❌ Authentication may have failed.")
    print("💡 Most common causes:")
    print("   - Took longer than 30 seconds to complete Schwab login")
    print("   - Didn't click 'Allow' on Schwab's permission page")
    print("   - Network timeout during token exchange")
    print("   - Try again and work more quickly after clicking 'Allow'")
    return False

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
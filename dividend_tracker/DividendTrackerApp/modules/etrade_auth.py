import os
import json
from datetime import datetime
import configparser
from requests_oauthlib import OAuth1Session
import tkinter as tk
from tkinter import messagebox
from playsound import playsound
import threading

AUTH_ALERT_PATH = "C:/Users/mjmat/Pythons_Code_Files/auth_required.mp3"

# Load API Credentials from config.ini
config = configparser.ConfigParser()
config_path = os.path.join(os.path.dirname(__file__), "config.ini")
config.read(config_path)



consumer_key = config["ETRADE_API"]["CONSUMER_KEY"]
consumer_secret = config["ETRADE_API"]["CONSUMER_SECRET"]
prod_base_url = "https://api.etrade.com"

# OAuth URLs
request_token_url = prod_base_url + "/oauth/request_token"
authorize_url = "https://us.etrade.com/e/t/etws/authorize"
access_token_url = prod_base_url + "/oauth/access_token"

# Auth storage file - USE SHARED TOKENS from main directory
auth_file_path = "C:/Users/mjmat/Python Code in VS/auth_data.json"

def save_tokens(oauth_token, oauth_token_secret):
    """ Store OAuth tokens in a JSON file with today's date. """
    with open(auth_file_path, "w") as file:
        json.dump({
            "oauth_token": oauth_token,
            "oauth_token_secret": oauth_token_secret,
            "date": datetime.now().strftime("%Y-%m-%d")
        }, file)

def load_tokens():
    """ Load OAuth tokens if they exist and are from today. """
    if os.path.exists(auth_file_path):
        with open(auth_file_path, "r") as file:
            data = json.load(file)
        token_date = data.get("date")
        if token_date:
            token_date = datetime.strptime(token_date, "%Y-%m-%d").date()
            today = datetime.now().date()
            if token_date < today:
                # Token is from yesterday or earlier, delete and force refresh
                os.remove(auth_file_path)
                print("❌ OAuth token expired (from previous day). File deleted.")
                return None, None
        return data.get("oauth_token"), data.get("oauth_token_secret")
    return None, None

def get_auth_token():
    """ Fetch request token from E*TRADE. """
    oauth = OAuth1Session(consumer_key, consumer_secret, callback_uri="oob")
    response = oauth.fetch_request_token(request_token_url)
    oauth_token = response.get("oauth_token")
    oauth_token_secret = response.get("oauth_token_secret")
    return oauth_token, oauth_token_secret

def authorize_etrade(force_new=False):
    """
    Handles the E*TRADE OAuth process with GUI and audio alert.
    If force_new is True, always starts a new OAuth flow and deletes any old token file.
    Returns (oauth_token, oauth_token_secret) or (None, None) if not successful.
    """
    # Delete old token file if forcing new auth
    if force_new and os.path.exists(auth_file_path):
        os.remove(auth_file_path)
        print("❌ Old OAuth token file deleted (force_new=True).")

    # Try to load tokens if not forcing new auth
    if not force_new:
        oauth_token, oauth_token_secret = load_tokens()
        if oauth_token and oauth_token_secret:
            print("\n✅ Using stored OAuth token. In Etrade auth.")
            return oauth_token, oauth_token_secret

    # If no valid tokens, start new OAuth process
    oauth_token, oauth_token_secret = get_auth_token()
    auth_url = f"{authorize_url}?key={consumer_key}&token={oauth_token}"

    # --- AUDIO ALERT HERE ---
    def play_auth_alert():
        try:
            playsound(AUTH_ALERT_PATH)
        except Exception as e:
            print("Audio alert failed:", e)
    threading.Thread(target=play_auth_alert, daemon=True).start()

    # --- Tkinter GUI for OAuth ---
    def open_browser():
        import webbrowser
        webbrowser.open(auth_url)

    def submit_code():
        code = code_entry.get()
        if not code:
            messagebox.showerror("Error", "Please enter the verification code.")
            return
        try:
            oauth = OAuth1Session(
                consumer_key,
                consumer_secret,
                oauth_token, oauth_token_secret
            )
            access_token_response = oauth.fetch_access_token(access_token_url, verifier=code)
            final_token = access_token_response.get("oauth_token")
            final_secret = access_token_response.get("oauth_token_secret")
            save_tokens(final_token, final_secret)
            def show_auto_close_message(title, message, duration=1000):
                popup = tk.Toplevel()
                popup.title(title)
                popup.geometry("350x100")
                popup.configure(bg="#222244")
                label = tk.Label(popup, text=message, font=("Arial", 14), bg="#222244", fg="white")
                label.pack(expand=True, fill="both", padx=10, pady=20)
                popup.after(duration, popup.destroy)
            print("✅ Access token exchange successful. Token and secret saved.")  # <--- ADD THIS LINE
            show_auto_close_message("Success", "✅ Access Token Saved Successfully.", duration=1000)
            root.destroy()
            nonlocal_tokens[0] = final_token
            nonlocal_tokens[1] = final_secret
        except Exception as e:
            messagebox.showerror("Error", f"Failed to authorize: {e}")
            print(f"❌ Access token exchange failed: {e}")  # <--- ADD THIS LINE
            # Delete token file on failure
            if os.path.exists(auth_file_path):
                os.remove(auth_file_path)
                print("❌ OAuth token file deleted due to failed authorization.")

    # Use a mutable object to pass tokens out of nested function
    nonlocal_tokens = [None, None]

    root = tk.Tk()
    root.title("E*TRADE OAuth Authorization")
    root.geometry("500x300")
    root.configure(bg="#222244")

    label = tk.Label(root, text="Step 1: Click the button to open the E*TRADE authorization page.", font=("Arial", 12), bg="#222244", fg="white")
    label.pack(pady=10)

    url_btn = tk.Button(root, text="Open E*TRADE Authorization URL", font=("Arial", 14, "bold"), bg="#4CAF50", fg="white", command=open_browser)
    url_btn.pack(pady=10)

    label2 = tk.Label(root, text="Step 2: After authorizing, paste the verification code below:", font=("Arial", 12), bg="#222244", fg="white")
    label2.pack(pady=10)

    code_entry = tk.Entry(root, font=("Arial", 16), width=30, bg="#e0e0e0")
    code_entry.pack(pady=10)

    submit_btn = tk.Button(root, text="Submit Code", font=("Arial", 14, "bold"), bg="#2196F3", fg="white", command=submit_code)
    submit_btn.pack(pady=10)

    root.mainloop()

    # Return tokens if successfully set
    if nonlocal_tokens[0] and nonlocal_tokens[1]:
        return nonlocal_tokens[0], nonlocal_tokens[1]
    else:
        print("❌ OAuth process was not completed or failed.")
        # Always try to delete the token file if it exists
        try:
            if os.path.exists(auth_file_path):
                os.remove(auth_file_path)
                print("❌ OAuth token file deleted due to incomplete or failed authorization.")
        except Exception as e:
            print(f"⚠️ Failed to delete token file: {e}")
        return None, None
      

def get_etrade_session(force_new=False):
    """
    Returns an authenticated OAuth1Session and base_url.
    Handles token refresh automatically.
    If force_new is True, always starts a new OAuth flow.
    """
    from requests_oauthlib import OAuth1Session

    oauth_token, oauth_token_secret = authorize_etrade(force_new=force_new)
    if not oauth_token or not oauth_token_secret:
        raise Exception("❌ Could not obtain valid OAuth tokens. Please re-authorize.")
    session = OAuth1Session(
        consumer_key,
        consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret
    )
    base_url = prod_base_url
    return session, base_url

def fetch_etrade_market_data(tickers, retry=True):
    # Fetches daily market data (quote) for each ticker, including 52-week high/low and their dates.
    # Returns a DataFrame.
    # If a 401 error is encountered, refreshes the OAuth token and retries once.
    # Cleans ticker symbols and skips any that return an error in the API response.
    import time
    import pandas as pd
    from datetime import datetime

    status = None
    global session, base_url  # Ensure we update the global session/base_url
    print("Tickers to fetch market data for 1926:", tickers)
    def _pull_market_data(session, base_url, tickers):
        all_market_data = []
        # Clean ticker symbols: uppercase, strip spaces, remove empties/None
        clean_tickers = [
            str(t).strip().upper()
            for t in tickers
            if t and isinstance(t, str) and t.strip().isalpha() and len(t.strip()) > 1
        ]
        for symbol in clean_tickers:
            url_q = f"{base_url}/v1/market/quote/{symbol}.json"
            response_q = session.get(url_q)
            if response_q.status_code == 401:
                return None, 401
            print("=== E*TRADE HTTP Response ===")
            print("Requesting symbol:", symbol)
            print("Status Code:", response_q.status_code)
            print("Headers:", dict(response_q.headers))
            print("Body:", response_q.text)
            print("=============================")
            data_q = response_q.json()
            # Skip if error message in response
            if "Messages" in data_q.get("QuoteResponse", {}):
                print(f"⚠️ Skipping invalid or unsupported symbol: {symbol} - {data_q['QuoteResponse']['Messages']}")
                continue
            quote_data = data_q.get("QuoteResponse", {}).get("QuoteData", [{}])
            all_data = quote_data[0].get("All", {})
            week52High = all_data.get("high52", None)
            week52Low = all_data.get("low52", None)
            week52HiDate = all_data.get("week52HiDate", None)
            week52LowDate = all_data.get("week52LowDate", None)
            week52HiDate = datetime.fromtimestamp(week52HiDate) if week52HiDate else None
            week52LowDate = datetime.fromtimestamp(week52LowDate) if week52LowDate else None

            all_market_data.append({
                "Ticker": symbol,
                "bid": round(all_data.get("bid", 0), 2),
                "ask": round(all_data.get("ask", 0), 2),
                "bidSize": all_data.get("bidSize", 0),
                "askSize": all_data.get("askSize", 0),
                "prevClose": round(all_data.get("previousClose", 0), 2),
                "change": round(all_data.get("changeClose", 0), 2),
                "changePercent": round(all_data.get("changeClosePercentage", 0), 2),
                "marketCap": all_data.get("marketCap", 0),
                "averageVolume10day": round(all_data.get("averageVolume", 0), 2),
                "week52High": round(week52High, 2) if week52High else None,
                "week52Low": round(week52Low, 2) if week52Low else None,
                "week52HiDate": week52HiDate,
                "week52LowDate": week52LowDate
            })
            time.sleep(0.3)
        return pd.DataFrame(all_market_data), 200

    # Get session and base_url if not already set
    try:
        session
        base_url
    except NameError:
        session, base_url = get_etrade_session()

    df_market, status = _pull_market_data(session, base_url, tickers)
    if status == 401 and retry:
        print("❌ 401 Unauthorized: OAuth token expired. Refreshing token...")
        session, base_url = get_etrade_session(force_new=True)
        df_market, status = _pull_market_data(session, base_url, tickers)
        if status == 401:
            raise Exception("❌ Failed to refresh OAuth token. Please re-authorize manually.")
    elif status == 401:
        raise Exception("❌ Failed to refresh OAuth token. Please re-authorize manually.")

    if df_market is None:
        print("❌ No market data fetched.")
        return pd.DataFrame()

    df_market.to_csv("market_data.csv", index=False)
    print("✅ Market data saved to CSV.")
    return df_market

if __name__ == "__main__":
    oauth_token, oauth_token_secret = authorize_etrade()
    print("\n✅ Final OAuth Token:", oauth_token)
    print("\n✅ Final OAuth Token Secret:", oauth_token_secret)
    print("\n🔗 Authorize here:", f"{authorize_url}?key={consumer_key}&token={oauth_token}")

                               # ***** end of etrade auth collection, file creation and authentication checking  *****


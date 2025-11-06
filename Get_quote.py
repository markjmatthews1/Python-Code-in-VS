import tkinter as tk
from tkinter import messagebox
from etrade_auth import get_etrade_session
import requests
import datetime
import sys
import subprocess
import yfinance as yf



                                                   # ***** Get quote from E*TRADE *****
#API key d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0, API secret d0o631hr01qn5ghnfap0

# ==== Finnhub API Key ====
FINNHUB_API_KEY = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"  # <-- Replace with your actual Finnhub API key

# Initialize global session variables
session = None
base_url = None

def initialize_etrade_session(force_new=False):
    """Initialize E*TRADE session and set global variables"""
    global session, base_url
    try:
        print("Initializing E*TRADE session...")
        if force_new:
            print("Forcing new authentication (expired tokens)...")
        session, base_url = get_etrade_session(force_new=force_new)
        print(f"Session initialized successfully. Base URL: {base_url}")
        return True
    except Exception as e:
        print(f"Failed to initialize E*TRADE session: {e}")
        return False

def get_etrade_quote(symbol, retry=True):
    global session, base_url
    
    # Check if session is initialized
    if session is None or base_url is None:
        print("Session not initialized, attempting to initialize...")
        if not initialize_etrade_session():
            raise Exception("Failed to initialize E*TRADE session")

    url = f"{base_url}/v1/market/quote/{symbol}.json"
    
    try:
        response = session.get(url)
        
        if response.status_code == 401 and retry:
            print("E*TRADE token expired, refreshing session...")
            if initialize_etrade_session(force_new=True):  # Force complete re-auth
                # Only retry ONCE with retry=False
                return get_etrade_quote(symbol, retry=False)
            else:
                raise Exception("Failed to refresh E*TRADE session")
                
        if response.status_code == 401:
            # If we already retried, raise an error
            raise Exception("E*TRADE authentication failed after token refresh (401 Unauthorized).")
            
        if response.status_code != 200:
            raise Exception(f"API error: {response.status_code} {response.text}")
            
        data = response.json()
        try:
            quote = data['QuoteResponse']['QuoteData'][0]['All']
            return quote
        except Exception as e:
            raise Exception(f"Could not parse quote data: {e}")
            
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {e}")

def get_yahoo_data(symbol):
    ticker = yf.Ticker(symbol)
    # Dividend frequency
    dividends = ticker.dividends
    freq = "N/A"
    if len(dividends) > 2:
        last_dates = dividends.index[-3:]
        intervals = [(last_dates[i] - last_dates[i-1]).days for i in range(1, len(last_dates))]
        avg_interval = sum(intervals) / len(intervals)
        if 25 < avg_interval < 40:
            freq = "Monthly"
        elif 80 < avg_interval < 100:
            freq = "Quarterly"
        elif 170 < avg_interval < 200:
            freq = "Semi-Annual"
        elif 350 < avg_interval < 370:
            freq = "Annual"
        else:
            freq = "Irregular"
    return freq

def get_finnhub_earnings(symbol):
    url = f"https://finnhub.io/api/v1/stock/earnings?symbol={symbol}&token={FINNHUB_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    if data:
        last = data[0]
        return {
            "last_earnings_date": last.get("date", "N/A"),
            "actual": last.get("actual", "N/A"),
            "estimate": last.get("estimate", "N/A"),
            "surprise": last.get("surprise", "N/A"),
            "surprisePercent": last.get("surprisePercent", "N/A")
        }
    return {}

def get_finnhub_next_earnings(symbol):
    url = f"https://finnhub.io/api/v1/calendar/earnings?symbol={symbol}&token={FINNHUB_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    try:
        earnings = data['earningsCalendar'][0]
        return earnings.get('date', 'N/A')
    except Exception:
        return "N/A"

def get_finnhub_consensus(symbol):
    url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={FINNHUB_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    return data  # Contains targetHigh, targetLow, targetMean, targetMedian

def get_finnhub_news(symbol):
    from datetime import datetime, timedelta
    today = datetime.now().strftime('%Y-%m-%d')
    last_month = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={last_month}&to={today}&token={FINNHUB_API_KEY}"
    resp = requests.get(url)
    data = resp.json()
    return data[:5] if isinstance(data, list) else []

def show_quote():
    symbol = symbol_entry.get().strip().upper()
    if not symbol:
        messagebox.showerror("Input Error", "Please enter a symbol.")
        return
    try:
        quote = get_etrade_quote(symbol)
        frequency = quote.get('frequency', 'N/A')
        declared_div = quote.get('declaredDividend')
        if declared_div is not None:
            try:
                declared_div = float(declared_div) * 100
            except Exception:
                declared_div = "N/A"
        else:
            declared_div = "N/A"

        # Yahoo for dividend frequency
        yahoo_freq = get_yahoo_data(symbol)

        # Finnhub for earnings, consensus, news
        earnings = get_finnhub_earnings(symbol)
        next_earnings = get_finnhub_next_earnings(symbol)
        consensus = get_finnhub_consensus(symbol)
        news = get_finnhub_news(symbol)

        output = [
            f"Symbol: {symbol}",
            f"Previous Close: {quote.get('previousClose', 'N/A')}",
            f"Last Trade: {quote.get('lastTrade', 'N/A')}",
            f"Change: {quote.get('changeClose', 'N/A')}",
            f"Change Percent: {quote.get('changeClosePercentage', 'N/A')}%",
            f"52 Week Low: {quote.get('low52', 'N/A')}",
            f"52 Week High: {quote.get('high52', 'N/A')}",
            f"Yield: {quote.get('yield', 'N/A')}",
            f"Dividend Type (E*TRADE): {frequency}",
            f"Dividend Type (Yahoo): {yahoo_freq}",
            f"Declared Dividend: {declared_div}",
            f"Next Earnings Date: {next_earnings}",
            f"Last Earnings Date: {earnings.get('last_earnings_date', 'N/A')}",
            f"Actual EPS: {earnings.get('actual', 'N/A')}",
            f"Estimate EPS: {earnings.get('estimate', 'N/A')}",
            f"Surprise: {earnings.get('surprise', 'N/A')}",
            f"Surprise %: {earnings.get('surprisePercent', 'N/A')}",
            f"Consensus Price Target (Mean): {consensus.get('targetMean', 'N/A')}",
            "",
            "Last 5 News Headlines (Finnhub):"
        ]
        for article in news:
            output.append(f"- {article.get('headline', 'N/A')}")

        result_text.config(state='normal')
        result_text.delete(1.0, tk.END)
        result_text.insert(tk.END, "\n".join(output))
        result_text.config(state='disabled')
    except Exception as e:
        messagebox.showerror("Quote Error", str(e))

def reset_for_new_quote():
    symbol_entry.delete(0, tk.END)
    result_text.config(state='normal')
    result_text.delete(1.0, tk.END)
    result_text.config(state='disabled')

def return_to_menu():
    root.destroy()
   
if __name__ == "__main__":
    # Initialize E*TRADE authentication
    print("Starting Get Quote application...")
    
    # Check if we need fresh tokens (expired)
    from datetime import datetime
    import json
    import os
    
    auth_file_path = "C:/Users/mjmat/Python Code in VS/auth_data.json"
    force_new_auth = False
    
    if os.path.exists(auth_file_path):
        try:
            with open(auth_file_path, "r") as file:
                data = json.load(file)
            token_date = data.get("date")
            today = datetime.now().strftime("%Y-%m-%d")
            
            if token_date != today:
                print(f"⚠️ Tokens are from {token_date}, but today is {today}")
                print("🔄 Will force new authentication with E*TRADE website")
                force_new_auth = True
            else:
                print(f"✅ Tokens are current (from {token_date})")
        except Exception as e:
            print(f"⚠️ Error checking token date: {e}")
            force_new_auth = True
    else:
        print("⚠️ No token file found, will need new authentication")
        force_new_auth = True
    
    if not initialize_etrade_session(force_new=force_new_auth):
        messagebox.showerror("Authentication Error", 
                           "Failed to authenticate with E*TRADE. Please check your credentials and try again.")
        sys.exit(1)

    # Build GUI
    root = tk.Tk()
    root.title("E*TRADE Stock/ETF Quote")
    root.geometry("1000x900")
    root.configure(bg="#222244")

    tk.Label(root, text="Enter Symbol:", font=("Arial", 16, "bold"), bg="#222244", fg="white").pack(pady=10)
    symbol_entry = tk.Entry(root, font=("Arial", 16), width=20, bg="#e0e0e0")
    symbol_entry.pack(pady=5)

    # Top button row frame
    top_btn_frame = tk.Frame(root, bg="#222244")
    top_btn_frame.pack(pady=10, fill="x")

    another_btn = tk.Button(top_btn_frame, text="Get Another Quote", font=("Arial", 14, "bold"),
                            bg="#2196F3", fg="white", command=reset_for_new_quote, height=1, width=18)
    quote_btn = tk.Button(top_btn_frame, text="Get Quote", font=("Arial", 16, "bold"),
                          bg="#4CAF50", fg="white", command=show_quote, height=1, width=18)
    menu_btn = tk.Button(top_btn_frame, text="Return to Etrade Menu", font=("Arial", 14, "bold"),
                         bg="#F44336", fg="white", command=return_to_menu, height=1, width=18)

    # Place buttons in grid: another_btn | quote_btn | menu_btn
    another_btn.grid(row=0, column=0, padx=20, pady=5, sticky="w")
    quote_btn.grid(row=0, column=1, padx=20, pady=5)
    menu_btn.grid(row=0, column=2, padx=20, pady=5, sticky="e")
    top_btn_frame.grid_columnconfigure(0, weight=1)
    top_btn_frame.grid_columnconfigure(1, weight=1)
    top_btn_frame.grid_columnconfigure(2, weight=1)

        # Create a frame to center the result_text widget
    center_frame = tk.Frame(root, bg="#222244")
    center_frame.pack(expand=True, fill="both")

    result_text = tk.Text(center_frame, font=("Consolas", 16), width=100, height=30, bg="#e0e0e0", state='disabled')
    result_text.pack(expand=True)

    root.mainloop()

# **** End of Stock ETF Quote section ****
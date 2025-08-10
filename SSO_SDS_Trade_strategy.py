import yfinance as yf
import os
import pickle
import tkinter as tk
from tkinter import ttk
from playsound import playsound
import csv
import re
import pandas as pd


# --- CONFIG ---
EWW_TICKER = "EWW"
TLT_TICKER = "TLT"
SSO_TICKER = "SSO"
SDS_TICKER = "SDS"
POSITION_FILE = "sso_sds_position.pkl"
REFRESH_SECONDS = 60  # Auto-refresh interval in seconds
TRADE_LOG_FILE = "sso_sds_trade_log.csv"

ALERT_SOUNDS = {
    "WAIT": "C:/Users/mjmat/Pythons_Code_Files/wait_alert.mp3",
    "BUY": "C:/Users/mjmat/Pythons_Code_Files/buy_alert.mp3",
    "SELL": "C:/Users/mjmat/Pythons_Code_Files/sell_alert.mp3"
}

def play_alert(action):
    if "SELL SSO" in action:
        playsound(ALERT_SOUNDS["SELL"], block=False)
    elif "BUY" in action or "SELL SDS & BUY SSO" in action:
        playsound(ALERT_SOUNDS["BUY"], block=False)
    elif "WAIT" in action:
        playsound(ALERT_SOUNDS["WAIT"], block=False)

def get_last_close(ticker):
    data = yf.download(ticker, period="5d", interval="1d", progress=False)
    if data.empty:
        raise Exception(f"No data for {ticker}")
    return data["Close"].iloc[-1].item()

def get_indicator(ticker):
    data = yf.download(ticker, period="6d", interval="1d", progress=False)
    if len(data) < 2:
        raise Exception(f"Not enough data for {ticker}")
    prev = data["Close"].iloc[-2].item()
    last = data["Close"].iloc[-1].item()
    return round((last - prev) / prev, 4)

def load_position():
    if os.path.exists(POSITION_FILE):
        with open(POSITION_FILE, "rb") as f:
            return pickle.load(f)
    return None

def save_position(pos):
    with open(POSITION_FILE, "wb") as f:
        pickle.dump(pos, f)

def log_trade(action, ticker, open_date, open_price, close_date, close_price):
    """Append a trade to the trade log CSV."""
    file_exists = os.path.isfile(TRADE_LOG_FILE)

    def to_float(val):
        try:
            if val is None or val == "":
                return ""
            # If it's a pandas Series, get the scalar value
            if hasattr(val, "item"):
                val = val.item()
            return round(float(val), 2)
        except Exception:
            return ""

    open_price = to_float(open_price)
    close_price = to_float(close_price)

    with open(TRADE_LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(["Action", "Ticker", "Open Date", "Open Price", "Close Date", "Close Price"])
        writer.writerow([action, ticker, open_date, open_price, close_date, close_price])

def get_market_datetime():
    """Return current date and time, and whether market is open."""
    import datetime
    now = datetime.datetime.now()
    market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
    is_open = market_open <= now <= market_close and now.weekday() < 5
    return now, is_open

def get_today_open(ticker):
    import datetime
    today = datetime.datetime.now().date()
    data = yf.download(ticker, period="2d", interval="1d", progress=False)
    if data.empty:
        return None, None
    for idx, row in data.iterrows():
        if idx.date() == today:
            return today.strftime("%m/%d/%y"), float(row["Open"])
    return None, None

def get_signal():
    eww_val = get_indicator(EWW_TICKER)
    tlt_val = get_indicator(TLT_TICKER)
    position = load_position()
    sso_close = get_last_close(SSO_TICKER)
    now, is_market_open = get_market_datetime()
    today_str = now.strftime("%m/%d/%y")

    action = ""
    ticker = ""
    price = ""
    details = ""
    open_info = None  # (date_str, open_price)

    # Load pending trade memory
    pending_file = "pending_trade.pkl"
    pending_trade = None
    if os.path.exists(pending_file):
        with open(pending_file, "rb") as f:
            pending_trade = pickle.load(f)

    # If there is a pending trade from after-hours, execute it at today's open
    if pending_trade and pending_trade.get("execute_on") == today_str and is_market_open:
        # Prevent duplicate trades: check if this action for today is already in the trade log
        already_logged = False
        if os.path.exists(TRADE_LOG_FILE):
            try:
                df_log = pd.read_csv(TRADE_LOG_FILE)
                # Check for a trade with today's date and the same action
                if pending_trade["action"] == "BUY SSO":
                    already_logged = ((df_log["Action"] == "BUY SSO") & (df_log["Open Date"] == today_str)).any()
                elif pending_trade["action"] == "BUY SDS":
                    already_logged = ((df_log["Action"] == "BUY SDS") & (df_log["Open Date"] == today_str)).any()
            except Exception:
                already_logged = False
        if not already_logged:
            if pending_trade["action"] == "BUY SSO":
                date_str, open_price = get_today_open("SSO")
                open_info = (date_str, open_price)
                save_position({"type": "SSO", "date": date_str, "open": open_price})
                log_trade("BUY SSO", "SSO", date_str, open_price, "", "")
                os.remove(pending_file)
                action = "BUY SSO"
                ticker = "SSO"
                price = f"${open_price:.2f}" if open_price is not None else "Market Open"
                details = "Executed pending BUY SSO at market open"
            elif pending_trade["action"] == "BUY SDS":
                date_str, open_price = get_today_open("SDS")
                open_info = (date_str, open_price)
                save_position({"type": "SDS", "date": date_str, "open": open_price})
                log_trade("BUY SDS", "SDS", date_str, open_price, "", "")
                os.remove(pending_file)
                action = "BUY SDS"
                ticker = "SDS"
                price = f"${open_price:.2f}" if open_price is not None else "Market Open"
                details = "Executed pending BUY SDS at market open"
            # You can add more actions as needed
            return {
                "EWW": eww_val,
                "TLT": tlt_val,
                "Position": position["type"] if isinstance(position, dict) else position,
                "Action": action,
                "Ticker": ticker,
                "Price": price,
                "Details": details,
                "OpenInfo": open_info
            }
        else:
            # Trade already logged for today, just return info
            if pending_trade["action"] == "BUY SSO":
                date_str, open_price = get_today_open("SSO")
                open_info = (date_str, open_price)
                action = "WAIT"
                ticker = "SSO"
                price = f"${open_price:.2f}" if open_price is not None else "Market Open"
                details = "BUY SSO already executed for today."
            elif pending_trade["action"] == "BUY SDS":
                date_str, open_price = get_today_open("SDS")
                open_info = (date_str, open_price)
                action = "WAIT"
                ticker = "SDS"
                price = f"${open_price:.2f}" if open_price is not None else "Market Open"
                details = "BUY SDS already executed for today."
            return {
                "EWW": eww_val,
                "TLT": tlt_val,
                "Position": position["type"] if isinstance(position, dict) else position,
                "Action": action,
                "Ticker": ticker,
                "Price": price,
                "Details": details,
                "OpenInfo": open_info
            }

    # Main logic - REVERSED STRATEGY
    if eww_val < tlt_val:
        # When EWW < TLT: Market uncertainty/stress -> Buy SDS (bet against S&P)
        if position and isinstance(position, dict) and position.get("type") == "SSO":
            # Switch from SSO to SDS
            if is_market_open:
                # Sell SSO, Buy SDS now
                date_str, open_price = get_today_open("SDS")
                open_info = (date_str, open_price)
                # Log close of SSO
                prev_date = position.get("date")
                prev_open = position.get("open")
                close_price = get_last_close("SSO")
                log_trade("SELL SSO", "SSO", prev_date, prev_open, date_str, close_price)
                # Log open of SDS
                log_trade("BUY SDS", "SDS", date_str, open_price, "", "")
                save_position({"type": "SDS", "date": date_str, "open": open_price})
                action = "SELL SSO & BUY SDS"
                ticker = "SDS"
                price = f"${open_price:.2f}" if open_price is not None else "Market Open"
                details = "Sold SSO and bought SDS at market open (Market Uncertainty)"
            else:
                # Market closed, schedule for next open
                with open(pending_file, "wb") as f:
                    pickle.dump({"action": "BUY SDS", "execute_on": (now + pd.Timedelta(days=1)).strftime("%m/%d/%y")}, f)
                action = "WAIT"
                ticker = "SDS"
                price = "Pending"
                details = "Switch to SDS scheduled for next market open (Market Uncertainty)"
                open_info = (position.get("date"), position.get("open"))
        elif position and isinstance(position, dict) and position.get("type") == "SDS":
            action = "WAIT"
            ticker = "SDS"
            price = "N/A"
            details = "Already own SDS. Sit and wait. (Market Uncertainty)"
            open_info = (position.get("date"), position.get("open"))
        else:
            if is_market_open:
                date_str, open_price = get_today_open("SDS")
                open_info = (date_str, open_price)
                save_position({"type": "SDS", "date": date_str, "open": open_price})
                log_trade("BUY SDS", "SDS", date_str, open_price, "", "")
                action = "BUY SDS"
                ticker = "SDS"
                price = f"${open_price:.2f}" if open_price is not None else "Market Open"
                details = "Bought SDS at market open (Market Uncertainty)"
            else:
                # Market closed, schedule for next open
                with open(pending_file, "wb") as f:
                    pickle.dump({"action": "BUY SDS", "execute_on": (now + pd.Timedelta(days=1)).strftime("%m/%d/%y")}, f)
                action = "WAIT"
                ticker = "SDS"
                price = "Pending"
                details = "Buy SDS scheduled for next market open (Market Uncertainty)"
           
    elif position and isinstance(position, dict) and position.get("type") == "SDS":
        # When EWW >= TLT: Market confidence -> Switch to SSO
        sds_close = get_last_close("SDS")
        limit_price = round(sds_close * 1.024, 2)
        if is_market_open:
            # Sell SDS now, Buy SSO
            prev_date = position.get("date")
            prev_open = position.get("open")
            close_price = get_last_close("SDS")
            # Get today's open for SSO
            date_str, open_price = get_today_open("SSO")
            log_trade("SELL SDS", "SDS", prev_date, prev_open, today_str, close_price)
            log_trade("BUY SSO", "SSO", date_str, open_price, "", "")
            save_position({"type": "SSO", "date": date_str, "open": open_price})
            action = "SELL SDS & BUY SSO"
            ticker = "SSO"
            price = f"${open_price:.2f}" if open_price is not None else "Market Open"
            details = "Sold SDS and bought SSO (Market Confidence)"
            open_info = (prev_date, prev_open)
        else:
            # Market closed, schedule for next open
            with open(pending_file, "wb") as f:
                pickle.dump({"action": "BUY SSO", "execute_on": (now + pd.Timedelta(days=1)).strftime("%m/%d/%y")}, f)
            action = "WAIT"
            ticker = "SSO"
            price = "Pending"
            details = "Switch to SSO scheduled for next market open (Market Confidence)"
            open_info = (position.get("date"), position.get("open"))
    else:
        # When EWW >= TLT: Market confidence -> Buy SSO (default position)
        if is_market_open:
            date_str, open_price = get_today_open("SSO")
            open_info = (date_str, open_price)
            save_position({"type": "SSO", "date": date_str, "open": open_price})
            log_trade("BUY SSO", "SSO", date_str, open_price, "", "")
            action = "BUY SSO"
            ticker = "SSO"
            price = f"${open_price:.2f}" if open_price is not None else "Market Open"
            details = "Bought SSO at market open (Market Confidence)"
        else:
            # Market closed, schedule for next open
            with open(pending_file, "wb") as f:
                pickle.dump({"action": "BUY SSO", "execute_on": (now + pd.Timedelta(days=1)).strftime("%m/%d/%y")}, f)
            action = "WAIT"
            ticker = "SSO"
            price = "Pending"
            details = "Buy SSO scheduled for next market open (Market Confidence)"


    return {
        "EWW": eww_val,
        "TLT": tlt_val,
        "Position": position["type"] if isinstance(position, dict) else position,
        "Action": action,
        "Ticker": ticker,
        "Price": price,
        "Details": details,
        "OpenInfo": open_info
    }

class SignalGUI:
    ACTION_COLORS = {
        "WAIT": "#f0e68c",         # Khaki
        "BUY SSO": "#b6ffb6",      # Light green (Market Confidence)
        "BUY SDS": "#ffcc99",      # Light orange (Market Uncertainty)
        "SELL SSO & BUY SDS": "#ffcc99",  # Light orange (Switch to Uncertainty)
        "SELL SDS & BUY SSO": "#b6ffb6",  # Light green (Switch to Confidence)
        "SELL SSO (Limit)": "#ffb6b6",   # Light red (deprecated - old logic)
        "SELL SDS (Limit)": "#ffb6b6",   # Light red (new sell logic if needed)
    }

    def __init__(self, root):
        self.root = root
        self.root.title("SSO/SDS Trade Log")
        self.root.minsize(900, 400)
        self.frm = tk.Frame(root, padx=40, pady=20, bg="#222244")
        self.frm.pack(fill="both", expand=True)
        # self.build_table()  # <-- REMOVE or COMMENT OUT this line

        # Title
        self.title_label = tk.Label(self.frm, text="SSO/SDS Trade Signal", font=("Arial", 20, "bold"), fg="#ffffff", bg="#222244")
        self.title_label.grid(column=0, row=0, columnspan=2, pady=(0, 20))

        # Info labels
        info_font = ("Arial", 14)
        self.labels = []  # <-- Make sure this is initialized!
        for i in range(7):
            lbl = tk.Label(self.frm, text="", font=info_font, fg="#ffffff", bg="#222244", anchor="w")
            lbl.grid(column=0, row=i+1, sticky="w", pady=2)
            self.labels.append(lbl)

        # Action label (big and bold)
        self.action_label = tk.Label(self.frm, text="", font=("Arial", 18, "bold"), width=25, pady=10)
        self.action_label.grid(column=0, row=8, pady=(20, 10), columnspan=2)

        # Prettier buttons with medium blue background and white text
        button_style = {"font": ("Arial", 12), "bg": "#3572b0", "fg": "#fff", "activebackground": "#285a8c", "activeforeground": "#fff"}

        tk.Button(self.frm, text="Close", command=root.destroy, **button_style).grid(column=0, row=9, pady=10, sticky="w")
        tk.Button(self.frm, text="Show Trade Log", command=show_trade_log_gui, **button_style).grid(column=1, row=9, pady=10, sticky="e")

        self.last_action = None  # <-- Make sure this is initialized!
        self.update_signal()

    def update_signal(self):
        try:
            signal = get_signal()
            open_info = signal.get("OpenInfo")
            open_label = ""
            if open_info and open_info[0] and open_info[1] is not None:
                # If open_info[1] is a Series, get the scalar value
                open_price = open_info[1]
                if hasattr(open_price, "item"):
                    try:
                        open_price = open_price.item()
                    except Exception:
                        open_price = float(open_price)
                open_label = f"Market price at open: {open_info[0]}; Open Market price: ${open_price:.2f}"
            texts = [
                f"EWW: {signal['EWW']:.4f}",
                f"TLT: {signal['TLT']:.4f}",
                open_label,
                f"Current Position: {signal['Position']}",
                f"Ticker: {signal['Ticker']}",
                f"Entry/Exit Price: {signal['Price']}",
                f"Details: {signal['Details']}"
            ]
            for lbl, txt in zip(self.labels, texts):
                lbl.config(text=txt)

            # Colorful action label
            action = signal['Action']
            color = self.ACTION_COLORS.get(action, "#cccccc")
            self.action_label.config(text=f"Action: {action}", bg=color)

            # Play alert if action changes
            if self.last_action is not None and action != self.last_action:
                play_alert(action)
            self.last_action = action
        except Exception as e:
            self.labels[0].config(text=f"Error: {e}")

        # Schedule next refresh
        self.root.after(REFRESH_SECONDS * 1000, self.update_signal)

class TradeLogGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("SSO/SDS Trade Log")
        self.root.minsize(900, 400)
        self.frm = tk.Frame(root, padx=40, pady=20, bg="#222244")
        self.frm.pack(fill="both", expand=True)
        self.build_summary()  # <-- KEEP this line here
        self.build_table()

    def extract_float(self, val):
        if isinstance(val, (int, float)):
            return float(val)
        if isinstance(val, str):
            import re
            match = re.search(r"[-+]?\d*\.\d+|\d+", val)
            if match:
                return float(match.group())
        return float('nan')

    def calculate_trade_pairs(self, df):
        """Calculate P&L by matching buy/sell pairs correctly."""
        df = df.copy()
        df["P&L"] = 0.0
        df["P&L %"] = ""
        df["Trade Pair"] = ""
        
        # Separate by ticker and calculate P&L for each
        for ticker in df['Ticker'].unique():
            ticker_df = df[df['Ticker'] == ticker].copy()
            ticker_df = ticker_df.sort_values('Open Date')
            
            buy_stack = []  # Stack to hold open buy positions
            
            for idx, row in ticker_df.iterrows():
                action = str(row['Action']).upper()
                
                if 'BUY' in action:
                    # This is a buy order
                    open_price = self.extract_float(row["Open Price"])
                    if not pd.isna(open_price):
                        buy_stack.append({
                            'index': idx,
                            'price': open_price,
                            'date': row['Open Date']
                        })
                
                elif 'SELL' in action:
                    # This is a sell order - match with most recent buy
                    close_price = self.extract_float(row["Close Price"])
                    if not pd.isna(close_price) and buy_stack:
                        buy_order = buy_stack.pop()  # Get most recent buy (LIFO)
                        
                        # Calculate P&L
                        pnl = close_price - buy_order['price']
                        pnl_pct = (pnl / buy_order['price']) * 100 if buy_order['price'] != 0 else 0
                        
                        # Update the sell row
                        df.at[idx, "P&L"] = pnl
                        df.at[idx, "P&L %"] = f"{pnl_pct:.2f}%"
                        df.at[idx, "Trade Pair"] = f"Buy: {buy_order['date']} @ ${buy_order['price']:.2f}"
                        
                        # Update the corresponding buy row
                        df.at[buy_order['index'], "Trade Pair"] = f"Sell: {row['Close Date']} @ ${close_price:.2f}"
        
        return df

    def build_summary(self):
        """Display total P/L and P/L by ticker at the top."""
        import pandas as pd
        import os
        if not os.path.exists(TRADE_LOG_FILE):
            return
        
        df = pd.read_csv(TRADE_LOG_FILE)
        df = self.calculate_trade_pairs(df)
        
        # Calculate totals
        total_pl = df["P&L"].sum()
        pl_by_ticker = df.groupby("Ticker")["P&L"].sum()
        
        # Count completed trades
        completed_trades = len(df[df["P&L"] != 0])
        
        # Display summary
        summary_text = f"Total P/L: ${total_pl:.2f} | Completed Trades: {completed_trades} | "
        for ticker in ["SSO", "SDS"]:
            pl = pl_by_ticker.get(ticker, 0.0)
            trades = len(df[(df['Ticker'] == ticker) & (df["P&L"] != 0)])
            summary_text += f"{ticker}: ${pl:.2f} ({trades} trades) | "
        
        label = tk.Label(self.frm, text=summary_text, font=("Arial", 14, "bold"), fg="#fff", bg="#3572b0", pady=8)
        label.pack(fill="x", pady=(0, 10))

    def build_table(self):
        if not os.path.exists(TRADE_LOG_FILE):
            tk.Label(self.frm, text="No trades logged yet.", font=("Arial", 14), fg="#fff", bg="#222244").pack()
            return
        
        df = pd.read_csv(TRADE_LOG_FILE)
        df = self.calculate_trade_pairs(df)
        
        # Format P&L columns for display
        df["P&L_Display"] = df["P&L"].apply(lambda x: f"${x:.2f}" if x != 0 else "")
        df["P&L %"] = df["P&L %"].fillna("")
        
        # Reorder columns for better display
        display_columns = ["Action", "Ticker", "Open Date", "Open Price", "Close Date", "Close Price", "P&L_Display", "P&L %", "Trade Pair"]
        column_headers = ["Action", "Ticker", "Open Date", "Open Price", "Close Date", "Close Price", "P&L", "P&L %", "Trade Pair"]
        
        # Create main container with proper scrolling
        main_container = tk.Frame(self.frm, bg="#222244")
        main_container.pack(fill="both", expand=True)
        
        # Create canvas and scrollbar
        canvas = tk.Canvas(main_container, bg="#222244", highlightthickness=0)
        v_scrollbar = tk.Scrollbar(main_container, orient="vertical", command=canvas.yview)
        h_scrollbar = tk.Scrollbar(main_container, orient="horizontal", command=canvas.xview)
        
        # Create scrollable frame
        scrollable_frame = tk.Frame(canvas, bg="#222244")
        
        # Configure scrolling
        def configure_scroll_region(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        def bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", on_mousewheel)
        
        def unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        
        scrollable_frame.bind("<Configure>", configure_scroll_region)
        canvas.bind("<Enter>", bind_mousewheel)
        canvas.bind("<Leave>", unbind_mousewheel)
        canvas.bind('<Button-4>', lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind('<Button-5>', lambda e: canvas.yview_scroll(1, "units"))
        
        # Enable keyboard scrolling when canvas has focus
        canvas.bind("<Up>", lambda e: canvas.yview_scroll(-1, "units"))
        canvas.bind("<Down>", lambda e: canvas.yview_scroll(1, "units"))
        canvas.bind("<Prior>", lambda e: canvas.yview_scroll(-10, "units"))  # Page Up
        canvas.bind("<Next>", lambda e: canvas.yview_scroll(10, "units"))    # Page Down
        canvas.focus_set()
        
        # Create window in canvas
        canvas_frame = canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        
        # Configure canvas scrolling
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        
        # Header row with better styling
        for j, header in enumerate(column_headers):
            header_label = tk.Label(
                scrollable_frame, 
                text=header, 
                font=("Arial", 11, "bold"), 
                fg="#fff", 
                bg="#444466", 
                padx=8, 
                pady=6, 
                borderwidth=1, 
                relief="solid",
                wraplength=100
            )
            header_label.grid(row=0, column=j, sticky="nsew")
        
        # Data rows with improved formatting and coloring
        for i, row in df.iterrows():
            # Determine row colors based on action
            action = str(row["Action"]).upper()
            if i % 2 == 0:
                bg_base = "#eaf6ff"
                bg_buy = "#c8f7c5"
                bg_sell = "#ffd6d6"
            else:
                bg_base = "#d0e6f7"
                bg_buy = "#b0eab0"
                bg_sell = "#ffb6b6"
            
            if "BUY" in action:
                bg = bg_buy
                fg = "#006400"
            elif "SELL" in action:
                bg = bg_sell
                fg = "#8b0000"
            else:
                bg = bg_base
                fg = "#222"
            
            # Create cells for each column
            for j, col in enumerate(display_columns):
                if col == "P&L_Display":
                    val = row[col]
                    # Color P&L based on positive/negative
                    if val and val != "$0.00":
                        try:
                            amount = float(val.replace("$", ""))
                            cell_fg = "#006400" if amount >= 0 else "#8b0000"
                            font_weight = "bold"
                        except:
                            cell_fg = fg
                            font_weight = "normal"
                    else:
                        cell_fg = fg
                        font_weight = "normal"
                        val = ""
                    
                    cell_label = tk.Label(
                        scrollable_frame, 
                        text=val, 
                        font=("Arial", 10, font_weight), 
                        fg=cell_fg, 
                        bg=bg, 
                        padx=6, 
                        pady=4, 
                        borderwidth=1, 
                        relief="solid",
                        wraplength=80
                    )
                
                elif col == "P&L %":
                    val = row[col]
                    # Color P&L % based on positive/negative
                    if val and val != "":
                        try:
                            pct = float(val.replace("%", ""))
                            cell_fg = "#006400" if pct >= 0 else "#8b0000"
                            font_weight = "bold"
                        except:
                            cell_fg = fg
                            font_weight = "normal"
                    else:
                        cell_fg = fg
                        font_weight = "normal"
                        val = ""
                    
                    cell_label = tk.Label(
                        scrollable_frame, 
                        text=val, 
                        font=("Arial", 10, font_weight), 
                        fg=cell_fg, 
                        bg=bg, 
                        padx=6, 
                        pady=4, 
                        borderwidth=1, 
                        relief="solid",
                        wraplength=80
                    )
                
                else:
                    val = row[col] if col in row else ""
                    if pd.isna(val):
                        val = ""
                    
                    cell_label = tk.Label(
                        scrollable_frame, 
                        text=str(val), 
                        font=("Arial", 10), 
                        fg=fg, 
                        bg=bg, 
                        padx=6, 
                        pady=4, 
                        borderwidth=1, 
                        relief="solid",
                        wraplength=120
                    )
                
                cell_label.grid(row=i+1, column=j, sticky="nsew")
        
        # Configure column weights for proper resizing
        for j in range(len(column_headers)):
            scrollable_frame.grid_columnconfigure(j, weight=1, minsize=100)
        
        # Bind frame to canvas width
        def configure_canvas_width(event):
            canvas_width = event.width
            canvas.itemconfig(canvas_frame, width=canvas_width)
        
        canvas.bind('<Configure>', configure_canvas_width)

def show_gui():
    root = tk.Tk()
    root.configure(bg="#222244")
    SignalGUI(root)
    root.mainloop()

def show_trade_log_gui():
    root = tk.Tk()
    root.configure(bg="#222244")
    TradeLogGUI(root)
    root.mainloop()
    
if __name__ == "__main__":
    show_gui()
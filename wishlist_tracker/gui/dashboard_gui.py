"""
Wishlist Tracker Dashboard GUI
-----------------------------
Displays all tickers with real-time data (current price, 52-week high/low, and sold put columns).
Links to the ticker management popup for editing the watchlist.
"""
import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

# Ensure project root is in sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from wishlist_tracker.utils.watchlist_manager import load_watchlist
from wishlist_tracker.utils.etrade_data import fetch_and_update_watchlist
from wishlist_tracker.utils.option_chain import fetch_put_option_chain

WATCHLIST_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'watchlist.csv')

class DashboardGUI:
    def __init__(self, master):
        self.master = master
        master.title("Wishlist Tracker Dashboard")
        master.geometry("1600x700")  # Wider for all columns
        master.configure(bg="#e3f0ff")

        # Title and controls
        title = tk.Label(master, text="Wishlist Tracker Dashboard", font=("Segoe UI", 18, "bold"), bg="#e3f0ff", fg="#232946")
        title.pack(pady=10)
        btn_frame = tk.Frame(master, bg="#e3f0ff")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Refresh Data", command=self.refresh_data, bg="#a3cef1", fg="#232946", font=("Segoe UI", 11, "bold"), width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Manage Tickers", command=self.open_ticker_manager, bg="#b8c1ec", fg="#232946", font=("Segoe UI", 11, "bold"), width=14).pack(side=tk.LEFT, padx=5)

        # Table
        columns = ("Symbol", "Current Price", "52W High", "52W Low", "Premium", "Put Below", "Put Target", "Put Above", "Trend/Entry", "Entry Price", "Exit Price", "Stop Loss", "Notes")
        self.tree = ttk.Treeview(master, columns=columns, show="headings", height=25)
        col_widths = [90, 110, 110, 110, 110, 140, 140, 140, 120, 110, 110, 110, 180]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor="center")
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview",
                        background="#b8c1ec",
                        foreground="#232946",
                        rowheight=25,
                        fieldbackground="#b8c1ec",
                        font=("Segoe UI", 11))
        style.configure("Treeview.Heading",
                        background="#232946",
                        foreground="#b8c1ec",
                        font=("Segoe UI", 12, "bold"))
        style.map('Treeview', background=[('selected', '#a3cef1')])

        self.refresh_data()

    def refresh_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        watchlist = load_watchlist(WATCHLIST_CSV)
        fetch_and_update_watchlist(watchlist)
        import configparser
        from wishlist_tracker.utils.technicals import sma, ema, rsi, macd, fibonacci_levels, pivot_points
        from schwab_data import fetch_schwab_minute_ohlcv

        # Load technicals config
        config = configparser.ConfigParser()
        config.read(os.path.join(os.path.dirname(__file__), '..', 'config', 'technicals_setup.ini'))
        sma_period = config.getint('SMA', 'period', fallback=20)
        ema_period = config.getint('EMA', 'period', fallback=9)
        rsi_period = config.getint('RSI', 'period', fallback=14)
        macd_fast = config.getint('MACD', 'fast_period', fallback=12)
        macd_slow = config.getint('MACD', 'slow_period', fallback=26)
        macd_signal = config.getint('MACD', 'signal_period', fallback=9)
        fib_lookback = config.getint('Fibonacci', 'lookback_days', fallback=20)
        piv_method = config.get('Pivots', 'method', fallback='classic')

        # Fetch 1-min OHLCV for each symbol (synchronously)
        rows = []
        for inst in watchlist:
            puts = []
            try:
                puts = fetch_put_option_chain(inst.symbol, float(inst.current_price or 0))
                print(f"DEBUG: {inst.symbol} puts returned: {puts}")
            except Exception as e:
                print(f"DEBUG: Exception fetching puts for {inst.symbol}: {e}")
                puts = []
            # puts: [below, target, above]
            def fmt_money(val):
                try:
                    return f"${float(val):,.2f}"
                except:
                    return val
            def fmt_num(val):
                try:
                    return f"{float(val):.2f}"
                except:
                    return val

            put_below = put_target = put_above = ""
            premium_val = ""
            if puts and len(puts) == 3:
                below, target, above = puts
            elif puts and len(puts) == 2:
                below, target = puts[0], puts[1]
                above = None
            elif puts and len(puts) == 1:
                below = None
                target = puts[0]
                above = None
            else:
                below = target = above = None

            def put_str(p):
                if not p:
                    return ""
                if p['premium'] is None:
                    return f"{p['strike']:.2f} @ No Bid/Ask ({p['expiration']})"
                return f"{p['strike']:.2f} @ ${p['premium']:.2f} ({p['expiration']})"

            put_below = put_str(below)
            put_target = put_str(target)
            if target and target['premium'] is not None and inst.current_price:
                try:
                    premium_val = target['strike'] - target['premium'] - float(inst.current_price)
                    premium_val_num = target['strike'] - target['premium'] - float(inst.current_price)
                    premium_val = fmt_money(premium_val)
                except Exception:
                    premium_val = ""
                    premium_val_num = float('inf')
            else:
                premium_val_num = float('inf')
            put_above = put_str(above)

            # --- Compute technicals using Schwab 1-min historical OHLCV ---
            df = fetch_schwab_minute_ohlcv(inst.symbol)
            trend_entry = ""
            if not df.empty and 'Close' in df:
                try:
                    sma_val = sma(df['Close'], sma_period).iloc[-1]
                    ema_val = ema(df['Close'], ema_period).iloc[-1]
                    rsi_val = rsi(df['Close'], rsi_period).iloc[-1]
                    macd_line, signal_line, hist = macd(df['Close'], macd_fast, macd_slow, macd_signal)
                    macd_val = macd_line.iloc[-1]
                    fib_levels = fibonacci_levels(df['Close'], fib_lookback)
                    pivots = pivot_points(df.rename(columns={'High':'high','Low':'low','Close':'close'}), piv_method)
                    # Simple trend/entry logic
                    if ema_val > sma_val and rsi_val > 50 and macd_val > 0:
                        trend_entry = "Uptrend/Entry"
                    elif ema_val < sma_val and rsi_val < 50 and macd_val < 0:
                        trend_entry = "Downtrend/Avoid"
                    else:
                        trend_entry = "Neutral/Wait"
                except Exception as e:
                    trend_entry = f"Error: {e}"
            else:
                trend_entry = "No Data"

            # Entry/Exit/Stop logic for uptrend
            entry_price = exit_price = stop_loss = ""
            if trend_entry == "Uptrend/Entry" and not df.empty and 'Close' in df:
                last_close = df['Close'].iloc[-1]
                entry_price = fmt_money(last_close)
                exit_price = fmt_money(last_close * 1.02)  # Example: 2% target
                stop_loss = fmt_money(last_close * 0.98)   # Example: 2% stop
            row = (
                inst.symbol,
                fmt_money(inst.current_price) if inst.current_price else '',
                fmt_money(getattr(inst, 'high_52wk', '')),
                fmt_money(getattr(inst, 'low_52wk', '')),
                premium_val,
                put_below, put_target, put_above,
                trend_entry,
                entry_price, exit_price, stop_loss,
                inst.notes or '',
                premium_val_num
            )
            rows.append(row)

        # Sort rows by premium_val_num (most negative at the top)
        rows.sort(key=lambda r: r[-1])
        for row in rows:
            self.tree.insert('', 'end', values=row[:-1])

    def open_ticker_manager(self):
        import subprocess
        gui_path = os.path.join(os.path.dirname(__file__), 'ticker_manager_gui.py')
        subprocess.Popen([sys.executable, gui_path])

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()

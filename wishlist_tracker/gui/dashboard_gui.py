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
import pandas as pd
import requests

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

        # Header frame with fixed height to prevent expansion
        header_frame = tk.Frame(master, bg="#e3f0ff", height=60)
        header_frame.pack(fill=tk.X, pady=10, padx=20)
        header_frame.pack_propagate(False)  # Prevent children from affecting frame size
        
        # Store reference to master for spinner overlay
        self.master_frame = master
        
        # Left side - Empty space (spinner will be overlaid)
        left_spacer = tk.Label(header_frame, text="", bg="#e3f0ff", width=8)
        left_spacer.pack(side=tk.LEFT)
        
        # Center - Title
        self.title_label = tk.Label(header_frame, text="Wishlist Tracker Dashboard", font=("Segoe UI", 18, "bold"), bg="#e3f0ff", fg="#232946")
        self.title_label.pack(side=tk.LEFT, expand=True)
        
        # Right side - Last update time - Changed to "Working...." initially
        self.last_update_label = tk.Label(header_frame, text="Working....", font=("Arial", 12), bg="#e3f0ff", fg="#232946")
        self.last_update_label.pack(side=tk.RIGHT)
        
        # Create spinner overlay (positioned absolutely, won't affect header height)
        self.spinner_overlay = tk.Label(master, text="", font=("Segoe UI", 100), bg="#e3f0ff", fg="#ff4444")
        self.spinner_active = False
        self.spinner_chars = ["◐", "◓", "◑", "◒"]
        self.spinner_colors = ["#ff4444", "#44ff44", "#4444ff", "#ffaa00"]  # Red, Green, Blue, Orange
        self.spinner_index = 0
        # Initially hidden
        self.spinner_overlay.place_forget()
        
        # Status label for showing current activity
        # Status line between header and buttons - Changed to Arial 12
        self.status_label = tk.Label(master, text="🚀 Starting up...", font=("Arial", 12), bg="#e3f0ff", fg="#232946")
        self.status_label.pack(pady=2)
        
        btn_frame = tk.Frame(master, bg="#e3f0ff")
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Refresh Data", command=self.refresh_data, bg="#a3cef1", fg="#232946", font=("Segoe UI", 11, "bold"), width=14).pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Manage Tickers", command=self.open_ticker_manager, bg="#b8c1ec", fg="#232946", font=("Segoe UI", 11, "bold"), width=14).pack(side=tk.LEFT, padx=5)

        # Table
        columns = ("Symbol", "Current Price", "52W High", "52W Low", "Premium", "Put Below", "Put Target", "Put Above", "Trend/Entry", "Entry Price", "Exit Price", "Stop Loss", "Notes")
        self.tree = ttk.Treeview(master, columns=columns, show="headings", height=25)
        col_widths = [90, 110, 110, 110, 124, 140, 160, 140, 120, 110, 110, 110, 180]  # Put Target now 160 (was 148)
        
        # NUCLEAR OPTION: Force exact column sizes with minwidth=width to prevent shrinking
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            # Set minwidth=width to prevent columns from shrinking below target size
            self.tree.column(col, width=width, minwidth=width, stretch=False, anchor="center")
        
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)
        
        # Extra enforcement for Put Target column - make it exactly 160 pixels
        self.tree.column("Put Target", width=160, minwidth=160, stretch=False, anchor="center")
        
        print("🔧 [WISHLIST] Put Target column header reverted to standard size")

        # Bind to window events to continuously enforce column width
        self.master.bind('<Configure>', self.on_window_resize)
        self.tree.bind('<Configure>', self.on_tree_configure)

        # Schedule a delayed column width enforcement after GUI is fully loaded
        self.master.after(100, self.force_column_widths)

        # Initialize OAuth completion monitoring
        self.oauth_retry_pending = False
        self.oauth_completion_check()

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

        # Automatically start data refresh on startup (no manual button click needed)
        print("🚀 [WISHLIST] Starting automatic data refresh on app startup...")
        self.master.after(500, self.refresh_data)  # Small delay to ensure GUI is ready

    def start_spinner(self):
        """Start the spinning wheel animation as overlay"""
        self.spinner_active = True
        self.spinner_index = 0
        # Position spinner overlay centered vertically in header (header height is 60px, spinner needs to be centered)
        self.spinner_overlay.place(x=30, y=5)  # Moved up to center in header frame
        # Remove title padding since spinner is now overlaid
        self.title_label.pack_configure(padx=(0, 0))
        self._animate_spinner()
    
    def stop_spinner(self):
        """Stop the spinning wheel animation and hide overlay"""
        self.spinner_active = False
        self.spinner_overlay.place_forget()  # Hide the overlay
        # Recenter the title by adding some padding when spinner is hidden
        self.title_label.pack_configure(padx=(50, 0))
    
    def _animate_spinner(self):
        """Animate the spinning wheel overlay with flashy colors"""
        if self.spinner_active:
            # Update both character and color for flashy effect
            self.spinner_overlay.config(
                text=self.spinner_chars[self.spinner_index],
                fg=self.spinner_colors[self.spinner_index]
            )
            self.spinner_index = (self.spinner_index + 1) % len(self.spinner_chars)
            self.master.after(200, self._animate_spinner)  # Update every 200ms
    
    def force_column_widths(self):
        """Force column widths after GUI is fully loaded"""
        columns = ("Symbol", "Current Price", "52W High", "52W Low", "Premium", "Put Below", "Put Target", "Put Above", "Trend/Entry", "Entry Price", "Exit Price", "Stop Loss", "Notes")
        col_widths = [90, 110, 110, 110, 124, 140, 160, 140, 120, 110, 110, 110, 180]
        for col, width in zip(columns, col_widths):
            # Force exact column sizes with minwidth=width to prevent shrinking
            self.tree.column(col, width=width, minwidth=width, stretch=False, anchor="center")
        
        # Extra aggressive enforcement on Put Target column
        self.tree.column("Put Target", width=160, minwidth=160, stretch=False, anchor="center")
        
        # Force an immediate display update
        self.tree.update_idletasks()
        
        # Set it again after the update to override any auto-sizing
        self.tree.column("Put Target", width=160, minwidth=160, stretch=False, anchor="center")
        
        print("✅ [WISHLIST] Column widths ENFORCED - Put Target: 160px (minwidth=160, stretch=False)")
        
        # Schedule continuous enforcement every 3 seconds to constantly override tkinter's auto-sizing
        self.master.after(3000, self.force_column_widths)
    
    def on_window_resize(self, event):
        """Handle window resize events by enforcing column widths"""
        if event.widget == self.master:
            # Force column widths when window is resized
            self.tree.column("Put Target", width=160, minwidth=160, stretch=False, anchor="center")
    
    def on_tree_configure(self, event):
        """Handle tree configure events by enforcing column widths"""
        # Force column widths when tree is reconfigured
        self.tree.column("Put Target", width=160, minwidth=160, stretch=False, anchor="center")
    
    def update_last_refresh_time(self):
        """Update the last refresh timestamp"""
        from datetime import datetime
        current_time = datetime.now().strftime("%H:%M:%S")
        self.last_update_label.config(text=f"Last updated: {current_time}")

    def refresh_data(self):
        """Refresh data with threading to prevent GUI freezing"""
        import threading
        
        print("🚀 [WISHLIST] Starting threaded data refresh...")
        self.start_spinner()  # Start spinning wheel
        self.status_label.config(text="🔄 Loading E*Trade data...")
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Start data fetching in background thread
        def fetch_data_background():
            try:
                watchlist = load_watchlist(WATCHLIST_CSV)
                
                # Enhanced E*Trade data fetch with OAuth auto-continuation
                try:
                    print("🔄 [WISHLIST] Fetching E*Trade data...")
                    fetch_and_update_watchlist(watchlist)
                    print("✅ [WISHLIST] E*Trade data fetched successfully")
                    # Update GUI on main thread
                    self.master.after(0, lambda: self.status_label.config(text="📊 Calculating put options..."))
                    self.oauth_retry_pending = False  # Ensure flag is cleared on success
                    
                    # SUCCESS PATH: Schedule completion on main thread
                    print("🔄 [WISHLIST] E*Trade fetch completed, scheduling sorting and GUI update...")
                    self.master.after(0, lambda: self._complete_refresh(watchlist))
                    return  # Exit function after successful completion
                    
                except Exception as e:
                    print(f"⚠️ [WISHLIST] E*Trade fetch failed, may need OAuth: {e}")
                    # Update GUI on main thread
                    self.master.after(0, lambda: self.status_label.config(text="🔐 OAuth required - please complete popup..."))
                    # Set flag for OAuth completion monitoring
                    self.oauth_retry_pending = True
                    
                    # Check if OAuth might have actually completed successfully
                    try:
                        from etrade_auth import load_tokens
                        token, secret = load_tokens()
                        if token and secret:
                            print("🔍 [WISHLIST] OAuth tokens found after error - attempting immediate retry...")
                            self.master.after(500, self._immediate_retry_after_oauth)  # Very quick retry
                            return
                    except:
                        pass
                    
                    # Schedule automatic retry after a shorter delay for better UX
                    print("🔄 [WISHLIST] OAuth may be required - scheduling automatic retry...")
                    print("🔐 [WISHLIST] Please complete OAuth in popup if it appears - app will continue automatically")
                    self.master.after(2000, self._retry_refresh_after_oauth)  # Retry after 2 seconds
                    return  # Exit early, will retry automatically
                
            except Exception as e:
                print(f"❌ [WISHLIST] Background data fetch failed: {e}")
                self.master.after(0, lambda: self.status_label.config(text=f"❌ Error: {str(e)[:30]}..."))
        
        # Start background thread
        thread = threading.Thread(target=fetch_data_background, daemon=True)
        thread.start()

    def _immediate_retry_after_oauth(self):
        """Immediate retry when OAuth tokens are detected after an error"""
        print("🚀 [WISHLIST] Immediate retry - OAuth tokens detected...")
        self.status_label.config(text="🔄 OAuth completed - fetching data...")
        try:
            watchlist = load_watchlist(WATCHLIST_CSV)
            
            # Add timeout awareness for potential hanging
            print("🔄 [WISHLIST] Starting data fetch with timeout protection...")
            fetch_and_update_watchlist(watchlist)
            
            print("✅ [WISHLIST] Immediate OAuth retry successful!")
            self.oauth_retry_pending = False  # Clear pending flag
            self.status_label.config(text="📊 Calculating put options...")
            self._complete_refresh(watchlist)
            
        except TimeoutError as te:
            print(f"⏰ [WISHLIST] Immediate retry timed out: {te}")
            self.status_label.config(text="⏰ Data fetch timed out - retrying...")
            # Try again with shorter timeout expectation
            print("🔄 [WISHLIST] Timeout detected, trying again...")
            self.master.after(1000, self._retry_refresh_after_oauth)
            
        except Exception as e:
            print(f"⚠️ [WISHLIST] Immediate retry failed: {e}")
            # Check if it might be another OAuth error
            error_str = str(e).lower()
            if 'oauth' in error_str or 'unauthorized' in error_str or 'access token' in error_str:
                print("🔑 [WISHLIST] Possible OAuth error in immediate retry - scheduling another attempt")
                self.status_label.config(text="🔑 OAuth issue detected - retrying...")
                self.master.after(2000, self._retry_refresh_after_oauth)
            else:
                # Fall back to normal retry schedule
                print("🔄 [WISHLIST] Falling back to scheduled retry...")
                self.status_label.config(text="❌ Retry failed - trying again...")
                self.master.after(1500, self._retry_refresh_after_oauth)

    def _retry_refresh_after_oauth(self):
        """Retry refresh after OAuth completion"""
        print("🚀 [WISHLIST] First auto-retry attempt after OAuth...")
        self.status_label.config(text="🔄 Retrying after OAuth...")
        try:
            watchlist = load_watchlist(WATCHLIST_CSV)
            fetch_and_update_watchlist(watchlist)
            print("✅ [WISHLIST] OAuth retry successful - data refreshed!")
            self.oauth_retry_pending = False  # Clear pending flag
            self.status_label.config(text="📊 Calculating put options...")
            self._complete_refresh(watchlist)
        except Exception as e:
            print(f"⚠️ [WISHLIST] First retry still needs OAuth: {e}")
            self.status_label.config(text="🔐 Still waiting for OAuth completion...")
            # Keep oauth_retry_pending = True for monitoring to continue
            # Schedule one more attempt after additional delay
            print("🔄 [WISHLIST] Scheduling final retry attempt...")
            self.master.after(3000, self._final_retry_refresh)

    def _final_retry_refresh(self):
        """Final retry attempt"""
        print("🚀 [WISHLIST] Final auto-retry attempt...")
        self.status_label.config(text="🔄 Final retry attempt...")
        try:
            watchlist = load_watchlist(WATCHLIST_CSV)
            fetch_and_update_watchlist(watchlist)
            print("✅ [WISHLIST] Final retry successful!")
            self.oauth_retry_pending = False  # Clear pending flag
            self.status_label.config(text="📊 Calculating put options...")
            self._complete_refresh(watchlist)
        except Exception as e:
            print(f"❌ [WISHLIST] Final retry failed: {e}")
            self.oauth_retry_pending = False  # Clear pending flag to stop monitoring
            self.status_label.config(text="❌ Authentication failed - please try Refresh Data")
            # Show error message to user
            from tkinter import messagebox
            messagebox.showerror("E*Trade Authentication Error", 
                               "Failed to authenticate with E*Trade after multiple attempts.\n"
                               "Please check your internet connection and try the Refresh Data button again.\n\n"
                               "The app will continue monitoring for OAuth completion in the background.")

    def _complete_refresh(self, watchlist):
        """Complete the data refresh process"""
        print("🚀 [WISHLIST] Starting _complete_refresh - sorting and GUI update...")
        import configparser
        from wishlist_tracker.utils.technicals import sma, ema, rsi, macd, fibonacci_levels, pivot_points

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
        no_options_count = 0  # Track tickers with no tradeable options
        network_errors = 0    # Track network/API errors
        
        total_tickers = len(watchlist)
        for i, inst in enumerate(watchlist, 1):
            # Update status to show progress
            self.status_label.config(text=f"📊 Processing {i}/{total_tickers}: {inst.symbol} - fetching options...")
            self.master.update()  # Force GUI update
            
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

            def put_str(p, is_target=False):
                if not p:
                    return "No Tradeable Options (Bid=$0.00)"
                if p['premium'] is None:
                    result = f"{p['strike']:.2f} @ No Market ({p['expiration']})"
                else:
                    result = f"{p['strike']:.2f} @ ${p['premium']:.2f} ({p['expiration']})"
                
                # No highlighting - just return the clean result
                return result

            if not puts or all(p is None for p in puts):
                # No valid options found (all filtered out due to bid = $0.00)
                put_below = put_target = put_above = "No Market (Bid=$0.00)"
                premium_val = "No Market"
                premium_val_num = float('inf')
                no_options_count += 1  # Count tickers with no tradeable options
            else:
                put_below = put_str(below, is_target=False)
                put_target = put_str(target, is_target=True)  # Highlight the target put
                put_above = put_str(above, is_target=False)
                
                if target and target['premium'] is not None and inst.current_price:
                    try:
                        # Enhanced premium calculation: Strike - Premium - Current Price
                        # Example: $55 strike - $6 premium - $50 current = -$1 (extra cost)
                        # Positive value = extra profit, Negative value = extra cost
                        current_price_float = float(inst.current_price)
                        strike_price = target['strike']
                        premium_received = target['premium']
                        
                        premium_to_current = strike_price - premium_received - current_price_float
                        premium_val_num = premium_to_current
                        
                        # Format with proper sign indication
                        if premium_to_current >= 0:
                            premium_val = f"+${premium_to_current:.2f}"  # Extra profit
                        else:
                            premium_val = f"-${abs(premium_to_current):.2f}"  # Extra cost
                            
                    except Exception:
                        premium_val = ""
                        premium_val_num = float('inf')
                else:
                    premium_val = ""
                    premium_val_num = float('inf')

            # --- Simple trend analysis using E*TRADE data (faster, non-blocking) ---
            trend_entry = ""
            try:
                # Use simple price-based trend analysis as fallback
                current_price = float(inst.current_price) if inst.current_price else 0
                high_52wk = float(inst.high_52wk) if inst.high_52wk else 0
                low_52wk = float(inst.low_52wk) if inst.low_52wk else 0
                
                if current_price > 0 and high_52wk > 0 and low_52wk > 0:
                    # Simple momentum based on 52-week range position
                    range_position = (current_price - low_52wk) / (high_52wk - low_52wk)
                    
                    if range_position > 0.7:  # In top 30% of 52-week range
                        trend_entry = "Uptrend/Entry"
                    elif range_position < 0.3:  # In bottom 30% of 52-week range
                        trend_entry = "Downtrend/Avoid"
                    else:
                        trend_entry = "Neutral/Wait"
                else:
                    trend_entry = "Insufficient Data"
            except Exception as e:
                print(f"⚠️ [WISHLIST] Trend calc error for {inst.symbol}: {e}")
                trend_entry = "Calc Error"

            # Entry/Exit/Stop logic for uptrend
            entry_price = exit_price = stop_loss = ""
            if trend_entry == "Uptrend/Entry":
                try:
                    last_close = float(inst.current_price)
                    entry_price = fmt_money(last_close)
                    exit_price = fmt_money(last_close * 1.02)  # Example: 2% target
                    stop_loss = fmt_money(last_close * 0.98)   # Example: 2% stop
                except:
                    pass
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
                premium_val_num,  # For primary sort (highest premium to current price)
                1 if trend_entry == "Uptrend/Entry" else 0  # For secondary sort (uptrend priority)
            )
            rows.append(row)

        # Enhanced Three-Tier Sorting:
        # 1. First Priority: All uptrend tickers (regardless of premium, sorted by highest premium)
        # 2. Second Priority: Non-uptrend tickers with positive premium (sorted by highest premium)
        # 3. Third Priority: Non-uptrend tickers with negative premium (sorted by highest premium)
        
        # Separate into three groups
        uptrend_tickers = []
        non_uptrend_positive = []
        non_uptrend_negative = []
        
        for row in rows:
            premium_value = row[-2]  # premium_val_num
            is_uptrend = row[-1] == 1  # uptrend flag
            has_positive_premium = premium_value != float('inf') and premium_value > 0
            
            if is_uptrend:
                uptrend_tickers.append(row)
            elif has_positive_premium:
                non_uptrend_positive.append(row)
            else:
                non_uptrend_negative.append(row)
        
        print(f"🎯 [WISHLIST] Sorted: {len(uptrend_tickers)} uptrend, {len(non_uptrend_positive)} positive premium, {len(non_uptrend_negative)} negative premium")
        
        # Sort each group by premium (MOST NEGATIVE first = BEST profit potential)
        # More negative = lower cost basis = better deal
        uptrend_tickers.sort(key=lambda r: r[-2] if r[-2] != float('inf') else 999, reverse=False)  # Most negative first
        non_uptrend_positive.sort(key=lambda r: r[-2] if r[-2] != float('inf') else 999, reverse=True)  # Highest positive first
        non_uptrend_negative.sort(key=lambda r: r[-2] if r[-2] != float('inf') else 999, reverse=False)  # Most negative first
        
        # Combine: uptrend first, then non-uptrend positive, then non-uptrend negative
        final_rows = uptrend_tickers + non_uptrend_positive + non_uptrend_negative
        
        for row in final_rows:
            # Remove the sorting helper values before inserting into tree
            self.tree.insert('', 'end', values=row[:-2])
        
        # Force column widths after data insertion to prevent auto-resizing
        columns = ("Symbol", "Current Price", "52W High", "52W Low", "Premium", "Put Below", "Put Target", "Put Above", "Trend/Entry", "Entry Price", "Exit Price", "Stop Loss", "Notes")
        col_widths = [90, 110, 110, 110, 124, 140, 160, 140, 120, 110, 110, 110, 180]  # Put Target now 160
        for col, width in zip(columns, col_widths):
            # Set minwidth=width to prevent any shrinking below target size
            self.tree.column(col, width=width, minwidth=width, stretch=False, anchor="center")
        # Extra enforcement for Put Target column 
        self.tree.column("Put Target", width=160, minwidth=160, stretch=False, anchor="center")
        
        print("🔒 [WISHLIST] Post-data column widths SET - Put Target: 160px (minwidth=160)")
        
        # Update status message based on options availability and network issues
        total_tickers = len(watchlist)
        if network_errors > 0:
            if no_options_count == total_tickers:
                self.status_label.config(text=f"⚠️ Ready - All {total_tickers} tickers: no options + {network_errors} network errors")
            elif no_options_count > 0:
                tradeable_count = total_tickers - no_options_count
                self.status_label.config(text=f"⚠️ Ready - {tradeable_count}/{total_tickers} tradeable, {network_errors} trend errors")
            else:
                self.status_label.config(text=f"⚠️ Ready - All data loaded, {network_errors} trend calculation errors")
        elif no_options_count == total_tickers:
            self.status_label.config(text=f"⚠️ Ready - All {total_tickers} tickers have no tradeable options (bid=$0.00)")
        elif no_options_count > 0:
            tradeable_count = total_tickers - no_options_count
            self.status_label.config(text=f"✅ Ready - {tradeable_count}/{total_tickers} tickers: best premiums first, uptrend boost in top tier")
        else:
            self.status_label.config(text="✅ Ready - Best premiums first with uptrend priority in top tier!")
        
        # Stop spinner and update timestamp
        self.stop_spinner()
        self.update_last_refresh_time()
        print("✅ [WISHLIST] Dashboard refresh completed successfully!")

    def oauth_completion_check(self):
        """Periodically check if OAuth has completed and auto-refresh if needed"""
        # Only continue monitoring if OAuth retry is pending
        if not self.oauth_retry_pending:
            print("� [WISHLIST] OAuth monitoring stopped - no pending retry")
            return
            
        print("�🔍 [WISHLIST] Checking for OAuth completion...")
        # Try a simple test to see if E*Trade auth is working
        try:
            from etrade_auth import load_tokens
            token, secret = load_tokens()
            if token and secret:
                print("🚀 [WISHLIST] OAuth tokens detected - triggering auto-refresh!")
                self.oauth_retry_pending = False  # Stop monitoring
                self.status_label.config(text="🔄 OAuth completed - refreshing data...")
                
                # More aggressive retry - try immediately since tokens are ready
                print("✅ [WISHLIST] Starting immediate data fetch after OAuth detection")
                try:
                    self.refresh_data()
                    return  # Success - exit monitoring
                except Exception as e:
                    print(f"⚠️ [WISHLIST] Direct refresh failed after OAuth: {e}")
                    # Fall back to delayed retry
                    self.master.after(1000, self.refresh_data)
                    return  # Exit monitoring either way
        except Exception as oauth_check_error:
            print(f"🔍 [WISHLIST] OAuth check error: {oauth_check_error}")
        
        # Schedule next check only if monitoring should continue
        if self.oauth_retry_pending:
            self.master.after(2000, self.oauth_completion_check)  # Check every 2 seconds
        else:
            print("🛑 [WISHLIST] OAuth monitoring stopped")

    def open_ticker_manager(self):
        import subprocess
        gui_path = os.path.join(os.path.dirname(__file__), 'ticker_manager_gui.py')
        subprocess.Popen([sys.executable, gui_path])

if __name__ == "__main__":
    root = tk.Tk()
    app = DashboardGUI(root)
    root.mainloop()

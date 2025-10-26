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
from wishlist_tracker.utils.market_hours import get_market_status_display

WATCHLIST_CSV = os.path.join(os.path.dirname(__file__), '..', 'data', 'watchlist.csv')

class DashboardGUI:
    def __init__(self, master):
        self.master = master
        master.title("Wishlist Tracker Dashboard")
        master.geometry("1600x700")  # Wider for all columns
        master.configure(bg="#e3f0ff")

        # Header frame with fixed height to prevent expansion
        header_frame = tk.Frame(master, bg="#e3f0ff", height=80)  # Increased height for market status
        header_frame.pack(fill=tk.X, pady=10, padx=20)
        header_frame.pack_propagate(False)  # Prevent children from affecting frame size
        
        # Store reference to master for spinner overlay
        self.master_frame = master
        
        # Left side - Market Status Indicator
        self.market_status_frame = tk.Frame(header_frame, bg="#e3f0ff")
        self.market_status_frame.pack(side=tk.LEFT, padx=10)
        
        self.market_status_label = tk.Label(
            self.market_status_frame,
            text="Checking market...",
            font=("Segoe UI", 10, "bold"),
            bg="#e3f0ff",
            fg="#666666"
        )
        self.market_status_label.pack(anchor="w")
        
        self.market_warning_label = tk.Label(
            self.market_status_frame,
            text="",
            font=("Arial", 9),
            bg="#e3f0ff",
            fg="#ff6600",
            wraplength=200
        )
        self.market_warning_label.pack(anchor="w")
        
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

        # Table - UPDATED for Enhanced Scoring + ROI metrics + Liquidity + Technical Indicators
        columns = ("Symbol", "Current Price", "52W High", "52W Low", "Top #1 (Score)", "Score", "Daily ROI %", "Total $", "Days", "Liq", "Top #2", "Top #3", "Trend", "Notes")
        self.tree = ttk.Treeview(master, columns=columns, show="headings", height=25)
        col_widths = [80, 110, 110, 110, 180, 60, 90, 90, 60, 60, 180, 180, 160, 180]  # Added Score column (60px)
        
        # Configure column widths
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, minwidth=width, stretch=False, anchor="center")
        
        self.tree.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

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
                        rowheight=28,  # Increased for better readability
                        fieldbackground="#b8c1ec",
                        font=("Arial", 12))  # PHASE 1: Increased to 12pt
        style.configure("Treeview.Heading",
                        background="#232946",
                        foreground="#b8c1ec",
                        font=("Arial", 12, "bold"))  # PHASE 1: Arial 12pt
        style.map('Treeview', background=[('selected', '#a3cef1')])
        
        # Define color tags for ROI-based row coloring
        self.tree.tag_configure('excellent', background='#90EE90')  # Green - ROI >= 0.40%
        self.tree.tag_configure('good', background='#FFFF99')       # Yellow - ROI 0.33-0.40%
        self.tree.tag_configure('marginal', background='#FFB366')   # Orange - ROI < 0.33%
        self.tree.tag_configure('no_data', background='#D3D3D3')    # Gray - No data

        # Update market status display
        self.update_market_status()
        
        # Automatically start data refresh on startup (no manual button click needed)
        print("🚀 [WISHLIST] Starting automatic data refresh on app startup...")
        self.master.after(500, self.refresh_data)  # Small delay to ensure GUI is ready

    def update_market_status(self):
        """Update the market status indicator in the header"""
        try:
            status = get_market_status_display()
            
            # Color mapping
            color_map = {
                'green': '#00aa00',    # Market open
                'yellow': '#ff9900',   # After hours
                'orange': '#ff6600',   # Pre-market
                'red': '#cc0000'       # Weekend
            }
            
            status_color = color_map.get(status['color'], '#666666')
            
            # Update status text with emoji
            status_emoji = {
                'OPEN': '🟢',
                'PRE_MARKET': '🟡',
                'AFTER_HOURS': '🟠',
                'WEEKEND': '🔴'
            }
            emoji = status_emoji.get(status['state'], '⚪')
            
            self.market_status_label.config(
                text=f"{emoji} {status['status_text']}",
                fg=status_color
            )
            
            # Show warning if market is closed
            if status['warning']:
                self.market_warning_label.config(text=status['warning'])
            else:
                self.market_warning_label.config(text="")
                
        except Exception as e:
            print(f"Error updating market status: {e}")
            self.market_status_label.config(text="⚪ Market status unknown", fg="#666666")
        
        # Refresh market status every 60 seconds
        self.master.after(60000, self.update_market_status)

    def start_spinner(self):
        """Start the spinning wheel animation as overlay"""
        self.spinner_active = True
        self.spinner_index = 0
        # Position spinner overlay centered vertically in header (header height is 80px now)
        self.spinner_overlay.place(x=30, y=15)  # Adjusted for larger header
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
        """Force column widths after GUI is fully loaded - Phase 3: Updated for technical indicators"""
        columns = ("Symbol", "Current Price", "52W High", "52W Low", "Top #1 (Score)", "Score", "Daily ROI %", "Total $", "Days", "Liq", "Top #2", "Top #3", "Trend", "Notes")
        col_widths = [80, 110, 110, 110, 180, 90, 90, 60, 60, 180, 180, 160, 180]  # PHASE 3: Trend 160px for score display
        for col, width in zip(columns, col_widths):
            self.tree.column(col, width=width, minwidth=width, stretch=False, anchor="center")
        
        # Force an immediate display update
        self.tree.update_idletasks()
        
        print("✅ [WISHLIST] Column widths enforced for ROI-based display with liquidity")
        
        # Schedule continuous enforcement every 3 seconds
        self.master.after(3000, self.force_column_widths)
    
    def on_window_resize(self, event):
        """Handle window resize events by enforcing column widths"""
        if event.widget == self.master:
            # Force column widths when window is resized (no specific column enforcement needed)
            pass
    
    def on_tree_configure(self, event):
        """Handle tree configure events by enforcing column widths"""
        # Force column widths when tree is reconfigured (no specific column enforcement needed)
        pass
    
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
            
            # PHASE 1: ROI-based display (Top 3 by daily ROI)
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

            top1 = top2 = top3 = None
            daily_roi = total_premium = days_to_exp = ""
            
            if puts and len(puts) >= 3:
                top1, top2, top3 = puts[0], puts[1], puts[2]
            elif puts and len(puts) == 2:
                top1, top2 = puts[0], puts[1]
            elif puts and len(puts) == 1:
                top1 = puts[0]

            def put_str_roi(p):
                """Format put option string with ROI metrics and trend indicators"""
                if not p:
                    return ""
                if p.get('premium') is None or p.get('premium') == 0:
                    return f"${p['strike']:.2f} @ No Market"
                
                # Get trend strength from option data (if available from Phase 2)
                trend_indicator = ""
                if p.get('trend_strength'):
                    strength = p['trend_strength']
                    if strength >= 8:
                        trend_indicator = " ⬆️⬆️⬆️"  # Strong uptrend
                    elif strength >= 5:
                        trend_indicator = " ⬆️⬆️"    # Moderate uptrend
                    elif strength >= 3:
                        trend_indicator = " ⬆️"      # Weak uptrend
                
                # Format: $55.00 @ $8.00 (11/21) ⬆️⬆️⬆️
                exp_date = p.get('expiration', '')
                result = f"${p['strike']:.2f} @ ${p['premium']:.2f} ({exp_date}){trend_indicator}"
                
                return result

            # Extract metrics from top option (for dedicated columns)
            enhanced_score = ""
            if top1 and top1.get('premium'):
                daily_roi = f"{top1.get('daily_roi', 0):.2f}%"
                total_premium = f"${top1.get('premium_dollars', 0):,.0f}"
                days_to_exp = str(top1.get('days_to_expiry', ''))
                liquidity_display = top1.get('liquidity_display', '')  # PHASE 2: Get liquidity
                roi_for_sorting = top1.get('daily_roi', 0)
                # ENHANCED: Get enhanced score (0-100 quality rating)
                if top1.get('enhanced_score'):
                    score_val = top1['enhanced_score']
                    enhanced_score = f"{score_val:.0f}"
                    # Update sorting to use enhanced score instead of just ROI
                    roi_for_sorting = score_val  # Use enhanced score for sorting
            else:
                liquidity_display = ""  # PHASE 2: No liquidity if no option
                roi_for_sorting = 0
            
            # Format all three options
            if not puts or all(p is None for p in puts):
                top1_str = top2_str = top3_str = "No Market (Bid=$0.00)"
                daily_roi = ""
                total_premium = ""
                days_to_exp = ""
                liquidity_display = ""  # PHASE 2
                enhanced_score = ""  # No score if no options
                row_tag = 'no_data'
                no_options_count += 1
            else:
                top1_str = put_str_roi(top1)
                top2_str = put_str_roi(top2)
                top3_str = put_str_roi(top3)
                
                # ENHANCED: Determine row color based on enhanced score (0-100)
                # Color coding: 80+ = Excellent (green), 60-79 = Good (yellow), <60 = Marginal (orange)
                if top1 and top1.get('enhanced_score'):
                    score_val = top1['enhanced_score']
                    if score_val >= 80:
                        row_tag = 'excellent'  # Green - High quality
                    elif score_val >= 60:
                        row_tag = 'good'       # Yellow - Good quality
                    else:
                        row_tag = 'marginal'   # Orange - Lower quality
                else:
                    # Fallback to ROI if no enhanced score
                    if top1 and top1.get('daily_roi'):
                        roi_val = top1['daily_roi']
                        if roi_val >= 0.40:
                            row_tag = 'excellent'  # Green
                        elif roi_val >= 0.33:
                            row_tag = 'good'       # Yellow
                        else:
                            row_tag = 'marginal'   # Orange
                    else:
                        row_tag = 'no_data'  # Gray

            # --- PHASE 3: Enhanced Trend Analysis with Technical Indicators ---
            trend_entry = ""
            trend_score_for_sorting = 0
            try:
                from wishlist_tracker.utils.trend_analysis import get_trend_analysis
                
                # Get comprehensive technical analysis
                trend = get_trend_analysis(inst.symbol, current_price=inst.current_price)
                
                # Format display: emoji + score + category
                # Example: "🟢 85 UPTREND" or "🟡 50 Neutral"
                trend_entry = f"{trend['emoji']} {trend['score']} {trend['display']}"
                trend_score_for_sorting = trend['score']  # Use score for sorting (0-100)
                
            except Exception as e:
                # Fallback to simple 52-week range analysis if Phase 3 fails
                try:
                    current_price = float(inst.current_price) if inst.current_price else 0
                    high_52wk = float(inst.high_52wk) if inst.high_52wk else 0
                    low_52wk = float(inst.low_52wk) if inst.low_52wk else 0
                    
                    if current_price > 0 and high_52wk > 0 and low_52wk > 0:
                        range_position = (current_price - low_52wk) / (high_52wk - low_52wk)
                        
                        if range_position > 0.7:
                            trend_entry = "Uptrend ⬆️"
                            trend_score_for_sorting = 70
                        elif range_position < 0.3:
                            trend_entry = "Downtrend ⬇️"
                            trend_score_for_sorting = 20
                        else:
                            trend_entry = "Neutral ➡️"
                            trend_score_for_sorting = 50
                    else:
                        trend_entry = "Insufficient Data"
                        trend_score_for_sorting = 0
                except Exception as fallback_error:
                    print(f"⚠️ [WISHLIST] Trend calc error for {inst.symbol}: {fallback_error}")
                    trend_entry = "Calc Error"
                    trend_score_for_sorting = 0

            # ENHANCED: Build row with enhanced score column
            row = (
                inst.symbol,
                fmt_money(inst.current_price) if inst.current_price else '',
                fmt_money(getattr(inst, 'high_52wk', '')),
                fmt_money(getattr(inst, 'low_52wk', '')),
                top1_str,  # Top #1 (Score)
                enhanced_score,  # Score (0-100 quality rating)
                daily_roi,  # Daily ROI %
                total_premium,  # Total $
                days_to_exp,  # Days
                liquidity_display,  # Liquidity score with color
                top2_str,  # Top #2
                top3_str,  # Top #3
                trend_entry,  # Trend with technical score (e.g., "🟢 85 UPTREND")
                inst.notes or '',  # Notes
                roi_for_sorting,  # For sorting (enhanced_score or ROI - not displayed)
                trend_score_for_sorting  # Trend score 0-100 for sorting
            )
            rows.append((row, row_tag))  # Store row with its color tag

        # ENHANCED: Multi-tier sorting with enhanced quality scores
        # 1. Primary: Quality tier (excellent > good > marginal > no_data)
        # 2. Secondary: Trend score 0-100 within each tier (higher score = better)
        # 3. Tertiary: Enhanced score/ROI value (highest first within same tier+trend)
        
        def sort_key(item):
            row_data, tag = item
            score_value = row_data[-2]  # enhanced_score or roi_for_sorting
            trend_score = row_data[-1]  # trend_score_for_sorting (0-100, higher = better)
            
            # Quality tier priority (lower number = higher priority)
            tier_priority = {
                'excellent': 0,  # Green (Score ≥80 or ROI ≥0.40%)
                'good': 1,       # Yellow (Score 60-79 or ROI 0.33-0.40%)
                'marginal': 2,   # Orange (Score <60 or ROI <0.33%)
                'no_data': 3     # Gray (no data)
            }
            
            tier = tier_priority.get(tag, 99)
            
            # Use numeric trend score (0-100, higher is better)
            # Negate trend_score so higher scores appear first (lower sort value)
            trend_rank = -trend_score if trend_score > 0 else 999
            
            # Return tuple for sorting: (tier, -trend_score, -enhanced_score) 
            # Negative values to sort highest scores first within each tier
            return (tier, trend_rank, -score_value if score_value > 0 else 999)
        
        rows.sort(key=sort_key)
        
        print(f"🎯 [WISHLIST] Displaying {len(rows)} tickers sorted by Quality Score → Trend → Enhanced Score")
        
        # Insert rows with color tags
        for row_data, tag in rows:
            display_row = row_data[:-2]  # Remove roi_for_sorting and trend (last 2 elements)
            self.tree.insert("", "end", values=display_row, tags=(tag,))
        
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

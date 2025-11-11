"""
Simple Tkinter GUI for WeeklyPay™ Rotation Dashboard
Backup option if Streamlit has issues
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import datetime
import sys
from pathlib import Path
import threading
import pytz
import os
import pandas as pd
import yfinance as yf

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.etf_tracker import ETFTracker
from src.signal_engine import RotationRulesEngine
from src.data_collector import DataCollector

# Import rotation engine for timing and NAV-based rotation logic
try:
    from rotation_engine import RotationEngine
    ROTATION_ENGINE_AVAILABLE = True
except ImportError:
    ROTATION_ENGINE_AVAILABLE = False
    print("WARNING: rotation_engine.py not found - rotation features disabled")

# Import settings manager for dynamic ticker loading
try:
    from settings_manager import WeeklyPaySettingsManager
    SETTINGS_MANAGER_AVAILABLE = True
except ImportError:
    SETTINGS_MANAGER_AVAILABLE = False
    print("WARNING: settings_manager.py not found - using fallback ticker list")

def get_current_prices(tickers):
    """
    Fetch live current prices for a list of tickers using yfinance.
    
    Args:
        tickers: List of ticker symbols
        
    Returns:
        dict: {ticker: current_price}
    """
    prices = {}
    
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Try multiple price fields
            current_price = (
                info.get('currentPrice') or 
                info.get('regularMarketPrice') or 
                info.get('previousClose')
            )
            
            if current_price:
                prices[ticker] = float(current_price)
            else:
                print(f"Warning: Could not get price for {ticker}")
                prices[ticker] = None
                
        except Exception as e:
            print(f"Error fetching price for {ticker}: {str(e)}")
            prices[ticker] = None
    
    return prices

class WeeklyPayGUI:
    """Simple GUI for WeeklyPay™ rotation system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WeeklyPay™ Rotation Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg='white')
        
        # Initialize system components
        self.data = None
        self.auto_refresh_enabled = True  # Auto-refresh enabled by default
        self.refresh_interval = 60000  # 60 seconds in milliseconds
        self.setup_system()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
        
        # Start auto-refresh timer
        self.start_auto_refresh()
    
    def start_auto_refresh(self):
        """Start the auto-refresh timer"""
        if self.auto_refresh_enabled:
            self.refresh_data_async()
            # Schedule next refresh
            self.refresh_timer = self.root.after(self.refresh_interval, self.start_auto_refresh)
    
    def stop_auto_refresh(self):
        """Stop the auto-refresh timer"""
        if hasattr(self, 'refresh_timer'):
            self.root.after_cancel(self.refresh_timer)
    
    def toggle_auto_refresh(self):
        """Toggle auto-refresh on/off"""
        self.auto_refresh_enabled = not self.auto_refresh_enabled
        if self.auto_refresh_enabled:
            self.auto_refresh_btn.config(text="⚡ Auto: ON", bg="#28a745")
            self.start_auto_refresh()
        else:
            self.auto_refresh_btn.config(text="⚡ Auto: OFF", bg="#dc3545")
            self.stop_auto_refresh()
    
    def setup_system(self):
        """Initialize the rotation system"""
        try:
            self.tracker = ETFTracker("data/etf_list.json")
            self.engine = RotationRulesEngine(self.tracker)
            self.data_collector = DataCollector(self.tracker)
            self.data_collector.set_signal_engine(self.engine)
            
            # Initialize rotation engine for timing and NAV alerts
            if ROTATION_ENGINE_AVAILABLE:
                self.rotation_engine = RotationEngine()
            else:
                self.rotation_engine = None
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize system: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Create main canvas with scrollbar
        main_canvas = tk.Canvas(self.root, bg='white', highlightthickness=0)
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=main_canvas.yview)
        self.scrollable_frame = tk.Frame(main_canvas, bg='white')
        
        # Configure scrolling
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: main_canvas.configure(scrollregion=main_canvas.bbox("all"))
        )
        
        main_canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        main_canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        scrollbar.pack(side="right", fill="y")
        main_canvas.pack(side="left", fill="both", expand=True)
        
        # Bind mousewheel scrolling
        def _on_mousewheel(event):
            main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        main_canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Title (inside scrollable frame)
        title_frame = tk.Frame(self.scrollable_frame, bg='white')
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="📈 WeeklyPay™ Rotation Dashboard",
            font=("Arial", 20, "bold"),
            fg="#1f77b4",
            bg='white'
        )
        title_label.pack()
        
        # ===================================================================
        # ROTATION ENGINE ALERT PANEL - Shows urgent buy/sell opportunities
        # ===================================================================
        if self.rotation_engine:
            self.create_rotation_alert_panel()
        
        # Control buttons (inside scrollable frame)
        control_frame = tk.Frame(self.scrollable_frame, bg='white')
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh Data",
            command=self.refresh_data_async,
            font=("Arial", 12),
            bg="#28a745",
            fg="white",
            relief=tk.RAISED
        )
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Auto-refresh toggle button
        self.auto_refresh_btn = tk.Button(
            control_frame,
            text="⚡ Auto: ON",
            command=self.toggle_auto_refresh,
            font=("Arial", 12),
            bg="#28a745",
            fg="white",
            relief=tk.RAISED
        )
        self.auto_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        export_btn = tk.Button(
            control_frame,
            text="📤 Export Signals",
            command=self.export_signals,
            font=("Arial", 12),
            bg="#007bff",
            fg="white",
            relief=tk.RAISED
        )
        export_btn.pack(side=tk.LEFT, padx=5)
        
        # Status label (with last refresh time)
        self.status_label = tk.Label(
            control_frame,
            text="Status: Ready | Auto-refresh: Every 60s",
            font=("Arial", 10),
            bg='white',
            fg="#666"
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Create notebook for tabs (inside scrollable frame)
        self.notebook = ttk.Notebook(self.scrollable_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Tab 1: Rotation Alerts
        self.alerts_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.alerts_frame, text="🚨 Rotation Alerts")
        self.create_alerts_tab()
        
        # Tab 2: Sector Momentum
        self.momentum_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.momentum_frame, text="📈 Sector Momentum")
        self.create_momentum_tab()
        
        # Tab 3: Earnings Calendar
        self.earnings_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.earnings_frame, text="📅 Earnings")
        self.create_earnings_tab()
        
        # Tab 4: Dividend Payouts
        self.payouts_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.payouts_frame, text="💰 Payouts")
        self.create_payouts_tab()
        
        # Tab 5: Trade Entry
        self.trade_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.trade_frame, text="📝 Trade Entry")
        self.create_trade_tab()
        
        # Tab 6: Performance
        self.performance_frame = tk.Frame(self.notebook, bg='white')
        self.notebook.add(self.performance_frame, text="📊 Performance")
        self.create_performance_tab()
    
    def create_rotation_alert_panel(self):
        """Create rotation engine alert panel at top of dashboard"""
        # Get current holdings
        holdings = self.get_current_holdings_for_rotation()
        
        # Get rotation alert data
        current_time = self.rotation_engine.get_current_time_et()
        is_market_open = self.rotation_engine.is_market_open()
        
        if holdings:
            categorized = self.rotation_engine.analyze_holdings(holdings)
            alert = self.rotation_engine.get_rotation_alert(holdings)
        else:
            alert = {
                'urgency': 'info',
                'message': '💼 No current holdings. Ready to start rotation.',
                'actions': []
            }
            categorized = {'ready_to_sell': [], 'must_hold': [], 'hold_for_nav': []}
        
        # Get next rotation targets
        next_targets = self.rotation_engine.find_next_rotation_targets()
        
        # Determine alert color
        if alert['urgency'] == 'critical':
            bg_color = '#ff4757'  # Red
            fg_color = 'white'
        elif alert['urgency'] == 'important':
            bg_color = '#ffa502'  # Orange
            fg_color = 'white'
        else:
            bg_color = '#1e90ff'  # Blue
            fg_color = 'white'
        
        # Create alert frame (inside scrollable frame)
        alert_frame = tk.Frame(self.scrollable_frame, bg=bg_color, relief=tk.RAISED, bd=3)
        alert_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Header with time and market status
        header_text = f"🚨 ROTATION ALERT - {current_time.strftime('%A, %B %d, %Y at %I:%M %p ET')}\n"
        header_text += f"{'🟢 Market OPEN' if is_market_open else '🔴 Market CLOSED'}"
        
        header_label = tk.Label(
            alert_frame,
            text=header_text,
            font=("Arial", 12, "bold"),
            bg=bg_color,
            fg=fg_color
        )
        header_label.pack(pady=5)
        
        # Alert message
        message_label = tk.Label(
            alert_frame,
            text=alert['message'],
            font=("Arial", 14, "bold"),
            bg=bg_color,
            fg=fg_color,
            wraplength=900
        )
        message_label.pack(pady=5)
        
        # Actions section
        if alert['actions']:
            actions_frame = tk.Frame(alert_frame, bg=bg_color)
            actions_frame.pack(fill=tk.X, padx=20, pady=10)
            
            tk.Label(
                actions_frame,
                text="🎯 RECOMMENDED ACTIONS:",
                font=("Arial", 12, "bold"),
                bg=bg_color,
                fg=fg_color
            ).pack(anchor='w')
            
            for action in alert['actions']:
                if action['type'] == 'sell':
                    action_text = f"📤 SELL {action['ticker']} - NAV: {action['nav_pct']:+.2f}% - {action['reason']}"
                    action_bg = '#27ae60'
                elif action['type'] == 'buy':
                    action_text = f"📥 BUY {action['ticker']} - Deadline: {action['deadline']} - Ex-Div: {action['ex_div_date']}"
                    action_bg = '#e67e22'
                else:
                    continue
                
                action_label = tk.Label(
                    actions_frame,
                    text=action_text,
                    font=("Arial", 11),
                    bg=action_bg,
                    fg='white',
                    relief=tk.RAISED,
                    bd=2,
                    padx=10,
                    pady=5
                )
                action_label.pack(anchor='w', pady=2)
        
        # Holdings status section
        if holdings:
            holdings_frame = tk.Frame(alert_frame, bg=bg_color)
            holdings_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # Create 3 columns for holdings status
            status_container = tk.Frame(holdings_frame, bg=bg_color)
            status_container.pack(fill=tk.X)
            
            # Ready to Sell
            ready_frame = tk.Frame(status_container, bg='#27ae60', relief=tk.RAISED, bd=2)
            ready_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            tk.Label(
                ready_frame,
                text="✅ Ready to Sell",
                font=("Arial", 11, "bold"),
                bg='#27ae60',
                fg='white'
            ).pack(pady=3)
            
            if categorized['ready_to_sell']:
                for h in categorized['ready_to_sell']:
                    tk.Label(
                        ready_frame,
                        text=f"{h['ticker']} {h['nav_pct']:+.2f}%",
                        font=("Arial", 10),
                        bg='#27ae60',
                        fg='white'
                    ).pack()
            else:
                tk.Label(
                    ready_frame,
                    text="(None)",
                    font=("Arial", 10, "italic"),
                    bg='#27ae60',
                    fg='white'
                ).pack()
            
            # Must Hold
            hold_frame = tk.Frame(status_container, bg='#e67e22', relief=tk.RAISED, bd=2)
            hold_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            tk.Label(
                hold_frame,
                text="🔒 Must Hold",
                font=("Arial", 11, "bold"),
                bg='#e67e22',
                fg='white'
            ).pack(pady=3)
            
            if categorized['must_hold']:
                for h in categorized['must_hold']:
                    tk.Label(
                        hold_frame,
                        text=f"{h['ticker']} {h['dividend_status']}",
                        font=("Arial", 10),
                        bg='#e67e22',
                        fg='white'
                    ).pack()
            else:
                tk.Label(
                    hold_frame,
                    text="(None)",
                    font=("Arial", 10, "italic"),
                    bg='#e67e22',
                    fg='white'
                ).pack()
            
            # Hold for NAV
            loss_frame = tk.Frame(status_container, bg='#e74c3c', relief=tk.RAISED, bd=2)
            loss_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            
            tk.Label(
                loss_frame,
                text="🔴 Hold for NAV",
                font=("Arial", 11, "bold"),
                bg='#e74c3c',
                fg='white'
            ).pack(pady=3)
            
            if categorized['hold_for_nav']:
                for h in categorized['hold_for_nav']:
                    tk.Label(
                        loss_frame,
                        text=f"{h['ticker']} {h['nav_pct']:+.2f}%",
                        font=("Arial", 10),
                        bg='#e74c3c',
                        fg='white'
                    ).pack()
            else:
                tk.Label(
                    loss_frame,
                    text="(None)",
                    font=("Arial", 10, "italic"),
                    bg='#e74c3c',
                    fg='white'
                ).pack()
        
        # Next rotation opportunities
        if next_targets:
            targets_frame = tk.Frame(alert_frame, bg=bg_color)
            targets_frame.pack(fill=tk.X, padx=20, pady=10)
            
            # Get the ex-dividend day name for the group
            ex_day_name = next_targets[0]['next_ex_div_date'].strftime('%A')
            
            tk.Label(
                targets_frame,
                text=f"🎯 NEXT ROTATION GROUP - {ex_day_name} Ex-Dividend ({len(next_targets)} tickers):",
                font=("Arial", 11, "bold"),
                bg=bg_color,
                fg=fg_color
            ).pack(anchor='w', pady=5)
            
            for target in next_targets:  # Show all in the group
                urgency_icon = '⏰ URGENT' if target['is_urgent'] else '📅 Ready'
                target_text = f"{urgency_icon} | {target['ticker']} - Buy by: {target['deadline_description']} - Ex-Div: {target['next_ex_div_date'].strftime('%a %m/%d')}"
                
                tk.Label(
                    targets_frame,
                    text=target_text,
                    font=("Arial", 10),
                    bg=bg_color,
                    fg=fg_color,
                    anchor='w'
                ).pack(anchor='w', pady=1)
    
    def get_current_holdings_for_rotation(self):
        """Load current holdings from weeklypay_trades.csv for rotation engine"""
        holdings = []
        
        try:
            if not os.path.exists('weeklypay_trades.csv'):
                return holdings
                
            trades_df = pd.read_csv('weeklypay_trades.csv')
            if trades_df.empty:
                return holdings
                
            trades_df['Date'] = pd.to_datetime(trades_df['Date'])
            
            # Calculate current positions
            position_summary = {}
            
            for _, row in trades_df.iterrows():
                ticker = row['Ticker']
                if ticker not in position_summary:
                    position_summary[ticker] = {
                        'shares': 0,
                        'total_cost': 0,
                        'purchase_dates': []
                    }
                
                if row['Action'] == 'BUY':
                    position_summary[ticker]['shares'] += row['Quantity']
                    position_summary[ticker]['total_cost'] += row['Total']
                    position_summary[ticker]['purchase_dates'].append(row['Date'])
                elif row['Action'] == 'SELL':
                    position_summary[ticker]['shares'] -= row['Quantity']
            
            # Convert to holdings format
            eastern = pytz.timezone('America/New_York')
            
            # Get current prices for all tickers with positions
            tickers_with_positions = [t for t, d in position_summary.items() if d['shares'] > 0]
            current_prices = get_current_prices(tickers_with_positions)
            
            for ticker, data in position_summary.items():
                if data['shares'] > 0:
                    avg_purchase_price = data['total_cost'] / data['shares']
                    most_recent_purchase = max(data['purchase_dates'])
                    
                    if most_recent_purchase.tzinfo is None:
                        most_recent_purchase = eastern.localize(most_recent_purchase)
                    
                    # Use live price if available, fallback to purchase price + 1%
                    current_price = current_prices.get(ticker)
                    if current_price is None:
                        current_price = avg_purchase_price * 1.01
                    
                    holdings.append({
                        'ticker': ticker,
                        'purchase_date': most_recent_purchase,
                        'purchase_price': avg_purchase_price,
                        'current_price': current_price,
                        'shares': data['shares']
                    })
                    
        except Exception as e:
            print(f"Error loading holdings: {str(e)}")
        
        return holdings
    
    def create_alerts_tab(self):
        """Create rotation alerts tab"""
        
        # Week display
        week_frame = tk.Frame(self.alerts_frame, bg='white')
        week_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.week_label = tk.Label(
            week_frame,
            text="📅 Week: Loading...",
            font=("Arial", 14, "bold"),
            bg='white'
        )
        self.week_label.pack()
        
        # Rotation signals
        signals_frame = tk.Frame(self.alerts_frame, bg='white')
        signals_frame.pack(fill=tk.BOTH, expand=True, padx=10)
        
        # Rotate In column
        rotate_in_frame = tk.Frame(signals_frame, bg='white')
        rotate_in_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            rotate_in_frame,
            text="🟢 ROTATE IN",
            font=("Arial", 14, "bold"),
            fg="#155724",
            bg='white'
        ).pack(pady=5)
        
        self.rotate_in_text = tk.Text(
            rotate_in_frame,
            height=10,
            font=("Arial", 11),
            bg="#d4edda",
            fg="#155724",
            relief=tk.SUNKEN,
            bd=2
        )
        self.rotate_in_text.pack(fill=tk.BOTH, expand=True)
        
        # Rotate Out column
        rotate_out_frame = tk.Frame(signals_frame, bg='white')
        rotate_out_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)
        
        tk.Label(
            rotate_out_frame,
            text="🔴 ROTATE OUT",
            font=("Arial", 14, "bold"),
            fg="#721c24",
            bg='white'
        ).pack(pady=5)
        
        self.rotate_out_text = tk.Text(
            rotate_out_frame,
            height=10,
            font=("Arial", 11),
            bg="#f8d7da",
            fg="#721c24",
            relief=tk.SUNKEN,
            bd=2
        )
        self.rotate_out_text.pack(fill=tk.BOTH, expand=True)
        
        # Key insights
        insights_frame = tk.Frame(self.alerts_frame, bg='white')
        insights_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            insights_frame,
            text="📝 Key Insights",
            font=("Arial", 12, "bold"),
            bg='white'
        ).pack(anchor=tk.W)
        
        self.insights_text = tk.Text(
            insights_frame,
            height=5,
            font=("Arial", 10),
            bg="#fff3cd",
            fg="#856404",
            relief=tk.SUNKEN,
            bd=2
        )
        self.insights_text.pack(fill=tk.X)
    
    def create_momentum_tab(self):
        """Create sector momentum tab"""
        
        # Sector RSI display
        tk.Label(
            self.momentum_frame,
            text="📊 Sector RSI (14-day)",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)
        
        # Create treeview for sector data
        columns = ('Sector', 'RSI', 'Signal', 'Price', 'SMA 5', 'SMA 20')
        self.momentum_tree = ttk.Treeview(self.momentum_frame, columns=columns, show='headings', height=8)
        
        # Define headings
        for col in columns:
            self.momentum_tree.heading(col, text=col)
            self.momentum_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.momentum_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add scrollbar
        momentum_scroll = ttk.Scrollbar(self.momentum_frame, orient=tk.VERTICAL, command=self.momentum_tree.yview)
        self.momentum_tree.configure(yscrollcommand=momentum_scroll.set)
        momentum_scroll.pack(side=tk.RIGHT, fill=tk.Y)
    
    def create_earnings_tab(self):
        """Create earnings calendar tab"""
        
        tk.Label(
            self.earnings_frame,
            text="📅 Earnings Calendar",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)
        
        # Earnings treeview
        earnings_columns = ('Symbol', 'ETF', 'Date', 'Timing', 'Status')
        self.earnings_tree = ttk.Treeview(self.earnings_frame, columns=earnings_columns, show='headings', height=10)
        
        for col in earnings_columns:
            self.earnings_tree.heading(col, text=col)
            self.earnings_tree.column(col, width=120, anchor=tk.CENTER)
        
        self.earnings_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_payouts_tab(self):
        """Create dividend payouts tab"""
        
        tk.Label(
            self.payouts_frame,
            text="💰 Weekly Dividend Payouts",
            font=("Arial", 14, "bold"),
            bg='white'
        ).pack(pady=10)
        
        # Payouts treeview
        payout_columns = ('ETF', 'Amount', 'NAV', 'Yield %', 'Ex Date', 'Source')
        self.payouts_tree = ttk.Treeview(self.payouts_frame, columns=payout_columns, show='headings', height=10)
        
        for col in payout_columns:
            self.payouts_tree.heading(col, text=col)
            self.payouts_tree.column(col, width=100, anchor=tk.CENTER)
        
        self.payouts_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def create_trade_tab(self):
        """Create trade entry tab with Quick Fill functionality"""
        # Title
        title_label = tk.Label(
            self.trade_frame,
            text="📝 WeeklyPay™ Trade Entry",
            font=("Arial", 16, "bold"),
            bg='white',
            fg="#1f77b4"
        )
        title_label.pack(pady=10)
        
        # Main form frame
        form_frame = tk.Frame(self.trade_frame, bg='white', relief=tk.RAISED, bd=2)
        form_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Investment amount
        inv_frame = tk.Frame(form_frame, bg='white')
        inv_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            inv_frame,
            text="💰 Target Investment per Ticker:",
            font=("Arial", 11, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.investment_amount = tk.DoubleVar(value=4000.00)
        investment_entry = tk.Entry(
            inv_frame,
            textvariable=self.investment_amount,
            font=("Arial", 11),
            width=15
        )
        investment_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(
            inv_frame,
            text="USD",
            font=("Arial", 11),
            bg='white'
        ).pack(side=tk.LEFT)
        
        # Ticker selection
        ticker_frame = tk.Frame(form_frame, bg='white')
        ticker_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            ticker_frame,
            text="🎯 Ticker:",
            font=("Arial", 11, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.selected_ticker = tk.StringVar(value='')
        self.ticker_dropdown = ttk.Combobox(
            ticker_frame,
            textvariable=self.selected_ticker,
            font=("Arial", 11),
            width=15,
            state='readonly'
        )
        self.ticker_dropdown.pack(side=tk.LEFT, padx=5)
        
        # Quick Fill button
        quick_fill_btn = tk.Button(
            ticker_frame,
            text="⚡ Quick Fill Top Pick",
            command=self.quick_fill_trade,
            font=("Arial", 10, "bold"),
            bg="#28a745",
            fg="white",
            relief=tk.RAISED
        )
        quick_fill_btn.pack(side=tk.LEFT, padx=10)
        
        # Price
        price_frame = tk.Frame(form_frame, bg='white')
        price_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            price_frame,
            text="💲 Price:",
            font=("Arial", 11, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.trade_price = tk.DoubleVar(value=0.0)
        price_entry = tk.Entry(
            price_frame,
            textvariable=self.trade_price,
            font=("Arial", 11),
            width=15
        )
        price_entry.pack(side=tk.LEFT, padx=5)
        
        # Quantity
        qty_frame = tk.Frame(form_frame, bg='white')
        qty_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            qty_frame,
            text="📊 Quantity:",
            font=("Arial", 11, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.trade_quantity = tk.IntVar(value=0)
        qty_entry = tk.Entry(
            qty_frame,
            textvariable=self.trade_quantity,
            font=("Arial", 11),
            width=15
        )
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        # Total
        total_frame = tk.Frame(form_frame, bg='white')
        total_frame.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Label(
            total_frame,
            text="💵 Total:",
            font=("Arial", 11, "bold"),
            bg='white'
        ).pack(side=tk.LEFT, padx=5)
        
        self.trade_total_label = tk.Label(
            total_frame,
            text="$0.00",
            font=("Arial", 11, "bold"),
            bg='white',
            fg="#28a745"
        )
        self.trade_total_label.pack(side=tk.LEFT, padx=5)
        
        # Update total when price or quantity changes
        def update_total(*args):
            try:
                price = self.trade_price.get()
                qty = self.trade_quantity.get()
                total = price * qty
                self.trade_total_label.config(text=f"${total:,.2f}")
            except:
                self.trade_total_label.config(text="$0.00")
        
        self.trade_price.trace('w', update_total)
        self.trade_quantity.trace('w', update_total)
        
        # Action buttons
        action_frame = tk.Frame(form_frame, bg='white')
        action_frame.pack(fill=tk.X, padx=10, pady=20)
        
        tk.Button(
            action_frame,
            text="💚 Record BUY",
            command=lambda: self.record_trade('BUY'),
            font=("Arial", 12, "bold"),
            bg="#28a745",
            fg="white",
            relief=tk.RAISED,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔴 Record SELL",
            command=lambda: self.record_trade('SELL'),
            font=("Arial", 12, "bold"),
            bg="#dc3545",
            fg="white",
            relief=tk.RAISED,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            action_frame,
            text="🔄 Clear Form",
            command=self.clear_trade_form,
            font=("Arial", 12),
            bg="#6c757d",
            fg="white",
            relief=tk.RAISED,
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Status message
        self.trade_status = tk.Label(
            form_frame,
            text="",
            font=("Arial", 10),
            bg='white',
            fg="#666"
        )
        self.trade_status.pack(pady=10)
        
        # Populate ticker dropdown
        self.update_ticker_dropdown()
    
    def update_ticker_dropdown(self):
        """Update ticker dropdown with next rotation group first"""
        try:
            if self.rotation_engine:
                next_targets = self.rotation_engine.find_next_rotation_targets()
                next_group_tickers = [t['ticker'] for t in next_targets]
                
                # Get all tickers (you may need to adjust this based on available data)
                if SETTINGS_MANAGER_AVAILABLE:
                    settings_manager = WeeklyPaySettingsManager()
                    all_tickers_info = settings_manager.get_all_tickers_info()
                    all_tickers = sorted(list(all_tickers_info.keys()))
                else:
                    # Fallback to hardcoded list
                    all_tickers = ['QDTE', 'XDTE', 'YMAX', 'ULTY', 'JEPQ', 'JEPI', 
                                   'SVOL', 'YMAG', 'YBTC', 'YETH', 'NVDW', 'TSLY',
                                   'CONY', 'MSTY', 'APLY', 'GOOY', 'AMZY', 'NVDY']
                
                # Sort: next group first, then alphabetically
                other_tickers = sorted([t for t in all_tickers if t not in next_group_tickers])
                ticker_list = [''] + next_group_tickers + other_tickers
                
                self.ticker_dropdown['values'] = ticker_list
            else:
                self.ticker_dropdown['values'] = ['']
        except Exception as e:
            print(f"Error updating ticker dropdown: {str(e)}")
            self.ticker_dropdown['values'] = ['']
    
    def quick_fill_trade(self):
        """Quick fill trade form with top pick from next rotation group"""
        try:
            if not self.rotation_engine:
                messagebox.showwarning("Warning", "Rotation engine not available")
                return
            
            # Get next rotation targets
            next_targets = self.rotation_engine.find_next_rotation_targets()
            if not next_targets:
                messagebox.showinfo("Info", "No rotation targets available")
                return
            
            # Get top pick (first in list)
            top_pick = next_targets[0]
            ticker = top_pick['ticker']
            
            # Fetch live price
            self.trade_status.config(text="Fetching live price...", fg="#007bff")
            self.root.update()
            
            prices = get_current_prices([ticker])
            current_price = prices.get(ticker)
            
            if not current_price:
                messagebox.showerror("Error", f"Could not fetch price for {ticker}")
                self.trade_status.config(text="Error fetching price", fg="#dc3545")
                return
            
            # Calculate quantity
            investment = self.investment_amount.get()
            quantity = int(investment / current_price)
            
            # Populate form
            self.selected_ticker.set(ticker)
            self.trade_price.set(round(current_price, 2))
            self.trade_quantity.set(quantity)
            
            self.trade_status.config(
                text=f"✅ Quick Fill: {ticker} @ ${current_price:.2f} × {quantity} shares = ${current_price * quantity:,.2f}",
                fg="#28a745"
            )
            
        except Exception as e:
            messagebox.showerror("Error", f"Quick fill failed: {str(e)}")
            self.trade_status.config(text=f"Error: {str(e)}", fg="#dc3545")
    
    def record_trade(self, action):
        """Record a BUY or SELL trade to weeklypay_trades.csv"""
        try:
            ticker = self.selected_ticker.get()
            price = self.trade_price.get()
            quantity = self.trade_quantity.get()
            
            if not ticker or price <= 0 or quantity <= 0:
                messagebox.showwarning("Warning", "Please fill all fields with valid values")
                return
            
            # Prepare trade data
            trade_date = datetime.now().strftime('%Y-%m-%d')
            total = price * quantity
            
            trade_row = {
                'Date': trade_date,
                'Action': action,
                'Ticker': ticker,
                'Quantity': quantity,
                'Price': price,
                'Total': total
            }
            
            # Append to CSV
            df_new = pd.DataFrame([trade_row])
            
            if os.path.exists('weeklypay_trades.csv'):
                df_existing = pd.read_csv('weeklypay_trades.csv')
                df_combined = pd.concat([df_existing, df_new], ignore_index=True)
            else:
                df_combined = df_new
            
            df_combined.to_csv('weeklypay_trades.csv', index=False)
            
            messagebox.showinfo("Success", f"{action} trade recorded:\n{ticker} × {quantity} @ ${price:.2f} = ${total:,.2f}")
            self.trade_status.config(text=f"✅ {action} recorded successfully", fg="#28a745")
            
            # Refresh rotation alert panel
            if hasattr(self, 'scrollable_frame'):
                # Clear and recreate rotation alert panel
                for widget in self.scrollable_frame.winfo_children():
                    if isinstance(widget, tk.Frame) and widget.cget('bg') in ['#ff4757', '#ffa502', '#1e90ff']:
                        widget.destroy()
                        break
                
                if self.rotation_engine:
                    self.create_rotation_alert_panel()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to record trade: {str(e)}")
            self.trade_status.config(text=f"Error: {str(e)}", fg="#dc3545")
    
    def clear_trade_form(self):
        """Clear all trade form fields"""
        self.selected_ticker.set('')
        self.trade_price.set(0.0)
        self.trade_quantity.set(0)
        self.trade_status.config(text="Form cleared", fg="#666")
    
    def create_performance_tab(self):
        """Create performance metrics tab with FIFO calculations"""
        # Title
        title_label = tk.Label(
            self.performance_frame,
            text="📊 Performance Metrics",
            font=("Arial", 16, "bold"),
            bg='white',
            fg="#1f77b4"
        )
        title_label.pack(pady=10)
        
        # Metrics frame
        metrics_frame = tk.Frame(self.performance_frame, bg='white', relief=tk.RAISED, bd=2)
        metrics_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create labels for metrics
        self.perf_total_invested_label = tk.Label(
            metrics_frame,
            text="💰 Total Invested (Open Positions): $0.00",
            font=("Arial", 12, "bold"),
            bg='white',
            anchor='w'
        )
        self.perf_total_invested_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.perf_total_dividends_label = tk.Label(
            metrics_frame,
            text="💵 Total Dividends Received: $0.00",
            font=("Arial", 12),
            bg='white',
            fg="#28a745",
            anchor='w'
        )
        self.perf_total_dividends_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.perf_realized_gains_label = tk.Label(
            metrics_frame,
            text="📈 Realized Capital Gains: $0.00",
            font=("Arial", 12),
            bg='white',
            fg="#007bff",
            anchor='w'
        )
        self.perf_realized_gains_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.perf_unrealized_gains_label = tk.Label(
            metrics_frame,
            text="📊 Unrealized Gains/Loss: $0.00",
            font=("Arial", 12),
            bg='white',
            anchor='w'
        )
        self.perf_unrealized_gains_label.pack(fill=tk.X, padx=10, pady=5)
        
        self.perf_total_return_label = tk.Label(
            metrics_frame,
            text="🎯 Total Return: $0.00",
            font=("Arial", 14, "bold"),
            bg='white',
            fg="#1f77b4",
            anchor='w'
        )
        self.perf_total_return_label.pack(fill=tk.X, padx=10, pady=10)
        
        # Realized Returns section
        realized_frame = tk.Frame(metrics_frame, bg='#e8f5e9', relief=tk.RAISED, bd=2)
        realized_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            realized_frame,
            text="💵 Realized Returns (Cash in Pocket)",
            font=("Arial", 13, "bold"),
            bg='#e8f5e9',
            fg="#2e7d32"
        ).pack(pady=5)
        
        self.perf_realized_total_label = tk.Label(
            realized_frame,
            text="Total Realized: $0.00",
            font=("Arial", 12, "bold"),
            bg='#e8f5e9',
            fg="#2e7d32",
            anchor='w'
        )
        self.perf_realized_total_label.pack(fill=tk.X, padx=10, pady=5)
        
        # Refresh button
        refresh_perf_btn = tk.Button(
            metrics_frame,
            text="🔄 Refresh Performance",
            command=self.update_performance,
            font=("Arial", 11, "bold"),
            bg="#007bff",
            fg="white",
            relief=tk.RAISED
        )
        refresh_perf_btn.pack(pady=10)
        
        # Load initial performance
        self.update_performance()
    
    def calculate_trade_performance_fifo(self, trades_df):
        """
        Calculate performance metrics using FIFO cost basis matching.
        Returns dict with Total Invested, Dividends, Realized Gains, Unrealized Gains, Total Return
        """
        if trades_df.empty:
            return {
                'total_invested': 0.0,
                'total_dividends': 0.0,
                'realized_gains': 0.0,
                'unrealized_gains': 0.0,
                'total_return': 0.0,
                'total_realized': 0.0
            }
        
        # Ensure Date is datetime
        trades_df['Date'] = pd.to_datetime(trades_df['Date'])
        
        # Calculate metrics
        total_dividends = trades_df[trades_df['Action'] == 'DIVIDEND']['Total'].sum()
        total_realized_gains = 0.0
        
        # Calculate realized gains using FIFO
        for ticker in trades_df['Ticker'].unique():
            ticker_trades = trades_df[trades_df['Ticker'] == ticker].sort_values('Date')
            
            buys = []
            for _, row in ticker_trades[ticker_trades['Action'] == 'BUY'].iterrows():
                buys.append((row['Quantity'], row['Price']))
            
            sells = ticker_trades[ticker_trades['Action'] == 'SELL']
            
            for _, sell in sells.iterrows():
                shares_to_match = sell['Quantity']
                sold_proceeds = sell['Total']
                sold_cost_basis = 0.0
                
                # Match with FIFO buys
                remaining_to_match = shares_to_match
                buy_idx = 0
                
                while remaining_to_match > 0 and buy_idx < len(buys):
                    buy_qty, buy_price = buys[buy_idx]
                    shares_to_use = min(buy_qty, remaining_to_match)
                    
                    sold_cost_basis += shares_to_use * buy_price
                    remaining_to_match -= shares_to_use
                    
                    # Update buy quantity
                    buys[buy_idx] = (buy_qty - shares_to_use, buy_price)
                    if buys[buy_idx][0] == 0:
                        buy_idx += 1
                
                realized_gain = sold_proceeds - sold_cost_basis
                total_realized_gains += realized_gain
        
        # Calculate current positions and unrealized gains
        position_summary = {}
        
        for _, row in trades_df.iterrows():
            ticker = row['Ticker']
            if ticker not in position_summary:
                position_summary[ticker] = {'shares': 0, 'total_cost': 0}
            
            if row['Action'] == 'BUY':
                position_summary[ticker]['shares'] += row['Quantity']
                position_summary[ticker]['total_cost'] += row['Total']
            elif row['Action'] == 'SELL':
                # Calculate cost basis of sold shares using FIFO
                shares_to_reduce = row['Quantity']
                ticker_buys = trades_df[(trades_df['Ticker'] == ticker) & 
                                       (trades_df['Action'] == 'BUY') & 
                                       (trades_df['Date'] <= row['Date'])].sort_values('Date')
                
                cost_to_reduce = 0
                remaining = shares_to_reduce
                
                for _, buy in ticker_buys.iterrows():
                    if remaining <= 0:
                        break
                    shares_from_buy = min(buy['Quantity'], remaining)
                    cost_to_reduce += shares_from_buy * buy['Price']
                    remaining -= shares_from_buy
                
                position_summary[ticker]['shares'] -= shares_to_reduce
                position_summary[ticker]['total_cost'] -= cost_to_reduce
        
        # Calculate total invested (only open positions)
        total_invested = sum(d['total_cost'] for d in position_summary.values() if d['shares'] > 0)
        
        # Calculate unrealized gains
        total_unrealized_gains = 0.0
        tickers_with_positions = [t for t, d in position_summary.items() if d['shares'] > 0]
        
        if tickers_with_positions:
            current_prices = get_current_prices(tickers_with_positions)
            
            for ticker, data in position_summary.items():
                if data['shares'] > 0:
                    avg_cost = data['total_cost'] / data['shares']
                    current_price = current_prices.get(ticker, avg_cost)
                    
                    current_value = data['shares'] * current_price
                    cost_basis = data['total_cost']
                    unrealized_gain = current_value - cost_basis
                    
                    total_unrealized_gains += unrealized_gain
        
        total_return = total_dividends + total_realized_gains + total_unrealized_gains
        total_realized = total_dividends + total_realized_gains
        
        return {
            'total_invested': total_invested,
            'total_dividends': total_dividends,
            'realized_gains': total_realized_gains,
            'unrealized_gains': total_unrealized_gains,
            'total_return': total_return,
            'total_realized': total_realized
        }
    
    def update_performance(self):
        """Update performance metrics display"""
        try:
            if not os.path.exists('weeklypay_trades.csv'):
                return
            
            trades_df = pd.read_csv('weeklypay_trades.csv')
            if trades_df.empty:
                return
            
            # Calculate performance
            perf = self.calculate_trade_performance_fifo(trades_df)
            
            # Update labels
            self.perf_total_invested_label.config(
                text=f"💰 Total Invested (Open Positions): ${perf['total_invested']:,.2f}"
            )
            
            self.perf_total_dividends_label.config(
                text=f"💵 Total Dividends Received: ${perf['total_dividends']:,.2f}"
            )
            
            gains_color = "#28a745" if perf['realized_gains'] >= 0 else "#dc3545"
            self.perf_realized_gains_label.config(
                text=f"📈 Realized Capital Gains: ${perf['realized_gains']:+,.2f}",
                fg=gains_color
            )
            
            unrealized_color = "#28a745" if perf['unrealized_gains'] >= 0 else "#dc3545"
            self.perf_unrealized_gains_label.config(
                text=f"📊 Unrealized Gains/Loss: ${perf['unrealized_gains']:+,.2f}",
                fg=unrealized_color
            )
            
            total_color = "#28a745" if perf['total_return'] >= 0 else "#dc3545"
            self.perf_total_return_label.config(
                text=f"🎯 Total Return: ${perf['total_return']:+,.2f}",
                fg=total_color
            )
            
            realized_total_color = "#2e7d32" if perf['total_realized'] >= 0 else "#c62828"
            self.perf_realized_total_label.config(
                text=f"Total Realized (Cash): ${perf['total_realized']:+,.2f}",
                fg=realized_total_color
            )
            
        except Exception as e:
            print(f"Error updating performance: {str(e)}")
    
    def refresh_data_async(self):
        """Refresh data in background thread"""
        self.status_label.config(text="Status: Refreshing...")
        self.root.update()
        
        # Run in background thread to prevent GUI freezing
        thread = threading.Thread(target=self.refresh_data)
        thread.daemon = True
        thread.start()
    
    def refresh_data(self):
        """Refresh all system data"""
        try:
            # Collect data
            results = self.data_collector.collect_all_data()
            
            # Add sample earnings
            self.engine.add_earnings_event("AMD", "2025-10-08")
            self.engine.add_earnings_event("META", "2025-09-30")
            self.engine.add_earnings_event("NFLX", "2025-10-09")
            self.engine.add_earnings_event("NVDA", "2025-10-07")
            
            # Integrate weekly payouts
            self.engine.integrate_weekly_payouts(self.data_collector.weekly_payouts)
            
            # Generate signals
            signals = self.engine.generate_rotation_signals()
            alert = self.engine.generate_alert_format(self.data_collector.weekly_payouts)
            
            self.data = {
                'signals': signals,
                'alert': alert,
                'results': results
            }
            
            # Update GUI on main thread
            self.root.after(0, self.update_gui)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to refresh data: {e}"))
            self.root.after(0, lambda: self.status_label.config(text="Status: Error"))
    
    def update_gui(self):
        """Update GUI with new data"""
        if not self.data:
            return
        
        try:
            # Update alerts tab
            self.update_alerts()
            self.update_momentum()
            self.update_earnings()
            self.update_payouts()
            
            # Update performance tab
            self.update_performance()
            
            # Update ticker dropdown in trade tab
            self.update_ticker_dropdown()
            
            # Show last update time with Eastern Time
            eastern = pytz.timezone('US/Eastern')
            now_et = datetime.now(eastern)
            auto_status = "ON" if self.auto_refresh_enabled else "OFF"
            self.status_label.config(text=f"Status: Updated {now_et.strftime('%I:%M:%S %p ET')} | Auto: {auto_status}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update GUI: {e}")
    
    def update_alerts(self):
        """Update rotation alerts"""
        signals = self.data['signals']
        alert = self.data['alert']
        
        # Update week label
        self.week_label.config(text=f"📅 Week: {alert['week']}")
        
        # Update rotate in
        self.rotate_in_text.delete(1.0, tk.END)
        for symbol in signals['rotate_in']:
            etf_data = self.tracker.get_etf_metadata(symbol)
            underlying = etf_data.underlying_ticker if etf_data else "N/A"
            self.rotate_in_text.insert(tk.END, f"📈 {symbol} ({underlying})\n")
        
        # Update rotate out
        self.rotate_out_text.delete(1.0, tk.END)
        for symbol in signals['rotate_out']:
            etf_data = self.tracker.get_etf_metadata(symbol)
            underlying = etf_data.underlying_ticker if etf_data else "N/A"
            self.rotate_out_text.insert(tk.END, f"📉 {symbol} ({underlying})\n")
        
        # Update insights
        self.insights_text.delete(1.0, tk.END)
        for note in alert['notes']:
            self.insights_text.insert(tk.END, f"• {note}\n")
    
    def update_momentum(self):
        """Update sector momentum"""
        # Clear existing data
        for item in self.momentum_tree.get_children():
            self.momentum_tree.delete(item)
        
        # Add momentum data
        momentum_data = self.data_collector.sector_momentum.momentum_data
        for sector, momentum in momentum_data.items():
            self.momentum_tree.insert('', tk.END, values=(
                sector,
                f"{momentum.rsi_14:.1f}",
                momentum.momentum_signal,
                f"${momentum.price:.2f}",
                f"${momentum.sma_5:.2f}",
                f"${momentum.sma_20:.2f}"
            ))
    
    def update_earnings(self):
        """Update earnings calendar"""
        # Clear existing data
        for item in self.earnings_tree.get_children():
            self.earnings_tree.delete(item)
        
        # Add earnings data
        for event in self.engine.earnings_calendar:
            # Find corresponding ETF
            etf_symbol = "Unknown"
            for etf in self.tracker.get_etf_list():
                etf_data = self.tracker.get_etf_metadata(etf)
                if etf_data and etf_data.underlying_ticker == event.symbol:
                    etf_symbol = etf
                    break
            
            status = "THIS WEEK" if event.is_this_week else "POST" if event.is_post_earnings else "FUTURE"
            
            self.earnings_tree.insert('', tk.END, values=(
                event.symbol,
                etf_symbol,
                event.earnings_date,
                "Unknown",
                status
            ))
    
    def update_payouts(self):
        """Update dividend payouts"""
        # Clear existing data
        for item in self.payouts_tree.get_children():
            self.payouts_tree.delete(item)
        
        # Add payout data
        payout_data = self.data_collector.weekly_payouts.payout_data
        for symbol, payout in payout_data.items():
            self.payouts_tree.insert('', tk.END, values=(
                symbol,
                f"${payout.dividend_amount:.3f}",
                f"${payout.nav_price:.2f}",
                f"{payout.payout_percentage:.2f}%",
                payout.ex_date,
                payout.data_source.title()
            ))
    
    def export_signals(self):
        """Export rotation signals to file"""
        if not self.data:
            messagebox.showwarning("Warning", "No data to export. Please refresh first.")
            return
        
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Export Rotation Signals"
            )
            
            if filename:
                with open(filename, 'w') as f:
                    json.dump(self.data['alert'], f, indent=2)
                messagebox.showinfo("Success", f"Signals exported to {filename}")
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export: {e}")

def main():
    """Launch the tkinter GUI"""
    root = tk.Tk()
    app = WeeklyPayGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
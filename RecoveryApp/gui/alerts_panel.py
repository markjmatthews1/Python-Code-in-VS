"""
Alerts Panel for RecoveryApp
Monitors positions for viable trade opportunities and provides notifications
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta
import threading
import time
from typing import List, Dict, Any, Optional
import json
import os

# Import models and utilities
from utils.models import TickerPosition, TradeEntry
from utils.ui_utils import UIConfig, create_styled_button, create_styled_frame, create_styled_label
from utils.strategy_engine import (
    OptionChainAnalyzer, 
    PutOverlayEvaluator, 
    CallOverlayEvaluator, 
    SyntheticRecoveryEvaluator,
    estimate_recovery_time
)

class AlertCondition:
    """Represents an alert condition for monitoring"""
    def __init__(self, position: TickerPosition, strategy_type: str, min_premium: float = 0.0, 
                 max_strike_distance: float = 0.1, alert_name: str = ""):
        self.position = position
        self.strategy_type = strategy_type  # 'put_overlay', 'call_overlay', 'synthetic'
        self.min_premium = min_premium
        self.max_strike_distance = max_strike_distance  # % from current price
        self.alert_name = alert_name or f"{position.ticker} {strategy_type}"
        self.created_at = datetime.now()
        self.last_triggered = None
        self.enabled = True
        self.trigger_count = 0
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'ticker': self.position.ticker,
            'strategy_type': self.strategy_type,
            'min_premium': self.min_premium,
            'max_strike_distance': self.max_strike_distance,
            'alert_name': self.alert_name,
            'created_at': self.created_at.isoformat(),
            'last_triggered': self.last_triggered.isoformat() if self.last_triggered else None,
            'enabled': self.enabled,
            'trigger_count': self.trigger_count
        }
    
    @classmethod
    def from_dict(cls, data: dict, position: TickerPosition) -> 'AlertCondition':
        """Create AlertCondition from dictionary"""
        alert = cls(
            position=position,
            strategy_type=data['strategy_type'],
            min_premium=data.get('min_premium', 0.0),
            max_strike_distance=data.get('max_strike_distance', 0.1),
            alert_name=data.get('alert_name', '')
        )
        alert.created_at = datetime.fromisoformat(data.get('created_at', datetime.now().isoformat()))
        alert.last_triggered = datetime.fromisoformat(data['last_triggered']) if data.get('last_triggered') else None
        alert.enabled = data.get('enabled', True)
        alert.trigger_count = data.get('trigger_count', 0)
        return alert

class AlertsPanel:
    """Main alerts panel for monitoring and notification"""
    
    def __init__(self, parent_frame, portfolio_manager):
        self.parent_frame = parent_frame
        self.portfolio = portfolio_manager
        self.alerts: List[AlertCondition] = []
        
        # Initialize strategy analyzers
        self.option_analyzer = OptionChainAnalyzer()
        self.put_evaluator = PutOverlayEvaluator(self.option_analyzer)
        self.call_evaluator = CallOverlayEvaluator(self.option_analyzer)
        self.synthetic_evaluator = SyntheticRecoveryEvaluator(self.option_analyzer)
        
        self.monitoring_active = False
        self.monitoring_thread = None
        self.refresh_interval = 300  # 5 minutes default
        self.alerts_file = "alerts_config.json"
        
        # Alert notification settings
        self.sound_enabled = True
        self.popup_enabled = True
        self.log_enabled = True
        self.alert_log = []
        
        self.create_interface()
        self.load_alerts()
        
    def create_interface(self):
        """Create the alerts panel interface"""
        # Create main scrollable container
        self.canvas = tk.Canvas(self.parent_frame, bg=UIConfig.COLORS['bg_primary'])
        self.scrollbar = ttk.Scrollbar(self.parent_frame, orient="vertical", command=self.canvas.yview)
        self.main_frame = create_styled_frame(self.canvas)
        
        # Configure scrolling
        self.main_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.main_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)
        
        # Pack canvas and scrollbar
        self.canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        self.scrollbar.pack(side="right", fill="y")
        
        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Header
        self.create_header()
        
        # Control panel
        self.create_control_panel()
        
        # Alerts list
        self.create_alerts_list()
        
        # Alert log
        self.create_alert_log()
        
        # Add alert dialog
        self.create_add_alert_section()
    
    def create_header(self):
        """Create header with title and status"""
        header_frame = tk.Frame(self.main_frame, bg=UIConfig.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🚨 Strategy Alerts Monitor",
            font=('Arial', 20, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Status indicator
        self.status_frame = tk.Frame(header_frame, bg=UIConfig.COLORS['bg_primary'])
        self.status_frame.pack(side=tk.RIGHT)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="⚫ Monitoring: OFF",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.status_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Last check time
        self.last_check_label = tk.Label(
            self.status_frame,
            text="Last Check: Never",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.last_check_label.pack(side=tk.RIGHT, padx=(0, 20))
    
    def create_control_panel(self):
        """Create monitoring control panel"""
        control_frame = create_styled_frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Monitoring controls
        monitor_frame = tk.Frame(control_frame, bg=UIConfig.COLORS['bg_secondary'])
        monitor_frame.pack(side=tk.LEFT, padx=10, pady=10)
        
        tk.Label(
            monitor_frame,
            text="Monitoring Control:",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W)
        
        button_frame = tk.Frame(monitor_frame, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.start_button = create_styled_button(
            button_frame, "▶️ Start Monitoring", self.start_monitoring,
            style='success'
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = create_styled_button(
            button_frame, "⏹️ Stop Monitoring", self.stop_monitoring,
            style='danger'
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.check_now_button = create_styled_button(
            button_frame, "🔍 Check Now", self.check_now,
            style='warning'
        )
        self.check_now_button.pack(side=tk.LEFT)
        
        # Settings frame
        settings_frame = tk.Frame(control_frame, bg=UIConfig.COLORS['bg_secondary'])
        settings_frame.pack(side=tk.RIGHT, padx=10, pady=10)
        
        tk.Label(
            settings_frame,
            text="Settings:",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W)
        
        settings_controls = tk.Frame(settings_frame, bg=UIConfig.COLORS['bg_secondary'])
        settings_controls.pack(fill=tk.X, pady=(5, 0))
        
        tk.Label(
            settings_controls,
            text="Refresh Interval:",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT)
        
        self.interval_var = tk.StringVar(value=str(self.refresh_interval // 60))
        interval_spinbox = tk.Spinbox(
            settings_controls,
            from_=1, to=60, width=5,
            textvariable=self.interval_var,
            command=self.update_interval
        )
        interval_spinbox.pack(side=tk.LEFT, padx=(5, 0))
        
        tk.Label(
            settings_controls,
            text="min",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(2, 10))
        
        # Notification settings
        self.sound_var = tk.BooleanVar(value=self.sound_enabled)
        sound_check = tk.Checkbutton(
            settings_controls,
            text="Sound",
            variable=self.sound_var,
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            command=self.update_sound_setting
        )
        sound_check.pack(side=tk.LEFT, padx=(0, 5))
        
        self.popup_var = tk.BooleanVar(value=self.popup_enabled)
        popup_check = tk.Checkbutton(
            settings_controls,
            text="Popup",
            variable=self.popup_var,
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            command=self.update_popup_setting
        )
        popup_check.pack(side=tk.LEFT)
    
    def create_alerts_list(self):
        """Create the alerts list display"""
        list_frame = create_styled_frame(self.main_frame)
        list_frame.pack(fill=tk.X, pady=(0, 15))  # Changed from expand=True to fill=X only
        
        tk.Label(
            list_frame,
            text="Active Alerts:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Treeview for alerts
        columns = ('Alert Name', 'Ticker', 'Strategy', 'Min Premium', 'Strike Distance', 'Status', 'Last Triggered')
        
        tree_frame = tk.Frame(list_frame, bg=UIConfig.COLORS['bg_secondary'])
        tree_frame.pack(fill=tk.X, padx=10, pady=(0, 10))  # Changed from expand=True
        
        self.alerts_tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=6)  # Fixed height
        
        # Configure columns
        self.alerts_tree.heading('#1', text='Alert Name')
        self.alerts_tree.heading('#2', text='Ticker')
        self.alerts_tree.heading('#3', text='Strategy')
        self.alerts_tree.heading('#4', text='Min Premium')
        self.alerts_tree.heading('#5', text='Strike Distance')
        self.alerts_tree.heading('#6', text='Status')
        self.alerts_tree.heading('#7', text='Last Triggered')
        
        self.alerts_tree.column('#1', width=150)
        self.alerts_tree.column('#2', width=80)
        self.alerts_tree.column('#3', width=120)
        self.alerts_tree.column('#4', width=100)
        self.alerts_tree.column('#5', width=120)
        self.alerts_tree.column('#6', width=80)
        self.alerts_tree.column('#7', width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.alerts_tree.yview)
        h_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.alerts_tree.xview)
        self.alerts_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack treeview and scrollbars
        self.alerts_tree.pack(side=tk.LEFT, fill=tk.X)  # Changed from expand=True
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Context menu for alerts
        self.create_alert_context_menu()
        
        # Alert management buttons
        button_frame = tk.Frame(list_frame, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        create_styled_button(
            button_frame, "🗑️ Delete Alert", self.delete_selected_alert,
            style='danger'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            button_frame, "⏸️ Toggle Alert", self.toggle_selected_alert,
            style='warning'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            button_frame, "📊 Test Alert", self.test_selected_alert,
            style='primary'
        ).pack(side=tk.LEFT)
    
    def create_alert_log(self):
        """Create alert log display"""
        log_frame = create_styled_frame(self.main_frame)
        log_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            log_frame,
            text="Alert Log (Recent Activity):",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Text widget for log
        log_text_frame = tk.Frame(log_frame, bg=UIConfig.COLORS['bg_secondary'])
        log_text_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.log_text = tk.Text(
            log_text_frame,
            height=6,
            font=('Consolas', 9),
            bg=UIConfig.COLORS['bg_primary'],
            fg=UIConfig.COLORS['text_light'],
            wrap=tk.WORD
        )
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Log control buttons
        log_button_frame = tk.Frame(log_frame, bg=UIConfig.COLORS['bg_secondary'])
        log_button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        create_styled_button(
            log_button_frame, "🗑️ Clear Log", self.clear_log,
            style='warning'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            log_button_frame, "💾 Export Log", self.export_log,
            style='primary'
        ).pack(side=tk.LEFT)
    
    def create_add_alert_section(self):
        """Create add new alert section"""
        add_frame = create_styled_frame(self.main_frame)
        add_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            add_frame,
            text="Add New Alert:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Add alert form
        form_frame = tk.Frame(add_frame, bg=UIConfig.COLORS['bg_secondary'])
        form_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Row 1: Ticker and Strategy
        row1 = tk.Frame(form_frame, bg=UIConfig.COLORS['bg_secondary'])
        row1.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(row1, text="Ticker:", font=('Arial', 10), 
                fg=UIConfig.COLORS['text_light'], bg=UIConfig.COLORS['bg_secondary']).pack(side=tk.LEFT)
        
        self.ticker_var = tk.StringVar()
        ticker_combo = ttk.Combobox(row1, textvariable=self.ticker_var, width=10)
        ticker_combo['values'] = [pos.ticker for pos in self.portfolio.positions]
        ticker_combo.pack(side=tk.LEFT, padx=(5, 20))
        
        tk.Label(row1, text="Strategy:", font=('Arial', 10),
                fg=UIConfig.COLORS['text_light'], bg=UIConfig.COLORS['bg_secondary']).pack(side=tk.LEFT)
        
        self.strategy_var = tk.StringVar()
        strategy_combo = ttk.Combobox(row1, textvariable=self.strategy_var, width=15)
        strategy_combo['values'] = ['put_overlay', 'call_overlay', 'synthetic_recovery']
        strategy_combo.pack(side=tk.LEFT, padx=(5, 0))
        
        # Row 2: Parameters
        row2 = tk.Frame(form_frame, bg=UIConfig.COLORS['bg_secondary'])
        row2.pack(fill=tk.X, pady=(0, 5))
        
        tk.Label(row2, text="Min Premium ($):", font=('Arial', 10),
                fg=UIConfig.COLORS['text_light'], bg=UIConfig.COLORS['bg_secondary']).pack(side=tk.LEFT)
        
        self.min_premium_var = tk.StringVar(value="1.00")
        premium_entry = tk.Entry(row2, textvariable=self.min_premium_var, width=8)
        premium_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        tk.Label(row2, text="Max Strike Distance (%):", font=('Arial', 10),
                fg=UIConfig.COLORS['text_light'], bg=UIConfig.COLORS['bg_secondary']).pack(side=tk.LEFT)
        
        self.strike_distance_var = tk.StringVar(value="10")
        distance_entry = tk.Entry(row2, textvariable=self.strike_distance_var, width=8)
        distance_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        # Row 3: Alert name and add button
        row3 = tk.Frame(form_frame, bg=UIConfig.COLORS['bg_secondary'])
        row3.pack(fill=tk.X)
        
        tk.Label(row3, text="Alert Name:", font=('Arial', 10),
                fg=UIConfig.COLORS['text_light'], bg=UIConfig.COLORS['bg_secondary']).pack(side=tk.LEFT)
        
        self.alert_name_var = tk.StringVar()
        name_entry = tk.Entry(row3, textvariable=self.alert_name_var, width=25)
        name_entry.pack(side=tk.LEFT, padx=(5, 20))
        
        create_styled_button(
            row3, "➕ Add Alert", self.add_new_alert,
            style='success'
        ).pack(side=tk.LEFT)
    
    def create_alert_context_menu(self):
        """Create context menu for alerts tree"""
        self.context_menu = tk.Menu(self.alerts_tree, tearoff=0)
        self.context_menu.add_command(label="Edit Alert", command=self.edit_selected_alert)
        self.context_menu.add_command(label="Test Alert", command=self.test_selected_alert)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Alert", command=self.delete_selected_alert)
        
        def show_context_menu(event):
            self.context_menu.post(event.x_root, event.y_root)
        
        self.alerts_tree.bind("<Button-3>", show_context_menu)
    
    # Monitoring Control Methods
    def start_monitoring(self):
        """Start the monitoring thread"""
        if not self.monitoring_active and self.alerts:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self.monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            self.status_label.config(text="🟢 Monitoring: ON", fg=UIConfig.COLORS['success'])
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_message("📡 Alert monitoring started")
        elif not self.alerts:
            messagebox.showwarning("No Alerts", "Please add at least one alert before starting monitoring.")
    
    def stop_monitoring(self):
        """Stop the monitoring thread"""
        if self.monitoring_active:
            self.monitoring_active = False
            self.status_label.config(text="⚫ Monitoring: OFF", fg=UIConfig.COLORS['text_light'])
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_message("⏹️ Alert monitoring stopped")
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                self.check_all_alerts()
                self.update_last_check_time()
                
                # Sleep in small intervals to allow for responsive stopping
                for _ in range(self.refresh_interval):
                    if not self.monitoring_active:
                        break
                    time.sleep(1)
                    
            except Exception as e:
                self.log_message(f"❌ Monitoring error: {str(e)}")
                time.sleep(60)  # Wait before retrying
    
    def check_now(self):
        """Manually trigger alert checking"""
        self.log_message("🔍 Manual alert check initiated...")
        
        # Run check in separate thread to avoid blocking UI
        threading.Thread(target=self.check_all_alerts, daemon=True).start()
    
    def check_all_alerts(self):
        """Check all enabled alerts for triggers"""
        triggered_count = 0
        
        for alert in self.alerts:
            if alert.enabled:
                try:
                    if self.check_alert_condition(alert):
                        self.trigger_alert(alert)
                        triggered_count += 1
                except Exception as e:
                    self.log_message(f"❌ Error checking alert '{alert.alert_name}': {str(e)}")
        
        if triggered_count == 0:
            self.log_message(f"✅ Alert check complete - No triggers found ({len([a for a in self.alerts if a.enabled])} alerts checked)")
    
    def check_alert_condition(self, alert: AlertCondition) -> bool:
        """Check if an alert condition is met"""
        try:
            # Get current stock price (use cost basis as placeholder for testing)
            current_price = alert.position.cost_basis * 0.85  # Simulate underwater position
            
            # Check strategy based on type
            if alert.strategy_type == 'put_overlay':
                strategies = self.put_evaluator.evaluate_put_overlay(
                    alert.position.ticker, 
                    alert.position.cost_basis, 
                    alert.position.qty
                )
            elif alert.strategy_type == 'call_overlay':
                strategies = self.call_evaluator.evaluate_call_overlay(
                    alert.position.ticker, 
                    alert.position.cost_basis, 
                    alert.position.qty
                )
            elif alert.strategy_type == 'synthetic_recovery':
                strategies = self.synthetic_evaluator.evaluate_synthetic_recovery(
                    alert.position.ticker, 
                    alert.position.cost_basis, 
                    alert.position.qty
                )
            else:
                return False
            
            if not strategies or 'recommendations' not in strategies:
                return False
            
            recommendations = strategies['recommendations']
            if not recommendations:
                return False
            
            # Check the best recommendation against alert conditions
            best_rec = recommendations[0]
            
            # Check premium condition
            premium = best_rec.get('premium_income', 0)
            if premium < alert.min_premium:
                return False
            
            # Check strike distance condition
            strike = best_rec.get('strike', 0)
            
            if current_price > 0 and strike > 0:
                distance_pct = abs(strike - current_price) / current_price
                if distance_pct > alert.max_strike_distance:
                    return False
            
            return True
            
        except Exception as e:
            self.log_message(f"❌ Error in alert condition check: {str(e)}")
            return False
    
    def trigger_alert(self, alert: AlertCondition):
        """Trigger an alert notification"""
        alert.last_triggered = datetime.now()
        alert.trigger_count += 1
        
        message = f"🚨 ALERT TRIGGERED: {alert.alert_name}\n"
        message += f"Ticker: {alert.position.ticker}\n"
        message += f"Strategy: {alert.strategy_type}\n"
        message += f"Triggered at: {alert.last_triggered.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Log the alert
        self.log_message(message.replace('\n', ' | '))
        
        # Show popup if enabled
        if self.popup_enabled:
            messagebox.showinfo("Trade Alert", message)
        
        # Play sound if enabled (basic system beep)
        if self.sound_enabled:
            try:
                import winsound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except ImportError:
                pass  # Sound not available
        
        # Update the alerts tree display
        self.refresh_alerts_display()
        
        # Save alerts to persist trigger information
        self.save_alerts()
    
    # Alert Management Methods
    def add_new_alert(self):
        """Add a new alert from the form"""
        ticker = self.ticker_var.get().strip().upper()
        strategy = self.strategy_var.get()
        
        if not ticker or not strategy:
            messagebox.showwarning("Invalid Input", "Please select both ticker and strategy.")
            return
        
        # Find the position
        position = self.portfolio.get_position(ticker)
        
        if not position:
            messagebox.showerror("Position Not Found", f"No position found for ticker {ticker}")
            return
        
        try:
            min_premium = float(self.min_premium_var.get())
            strike_distance = float(self.strike_distance_var.get()) / 100.0  # Convert percentage
            alert_name = self.alert_name_var.get().strip() or f"{ticker} {strategy}"
            
            # Create new alert
            new_alert = AlertCondition(
                position=position,
                strategy_type=strategy,
                min_premium=min_premium,
                max_strike_distance=strike_distance,
                alert_name=alert_name
            )
            
            self.alerts.append(new_alert)
            self.refresh_alerts_display()
            self.save_alerts()
            
            # Clear form
            self.ticker_var.set("")
            self.strategy_var.set("")
            self.min_premium_var.set("1.00")
            self.strike_distance_var.set("10")
            self.alert_name_var.set("")
            
            self.log_message(f"➕ Added new alert: {alert_name}")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please enter valid numeric values: {str(e)}")
    
    def delete_selected_alert(self):
        """Delete the selected alert"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an alert to delete.")
            return
        
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this alert?"):
            item = selection[0]
            index = self.alerts_tree.index(item)
            
            if 0 <= index < len(self.alerts):
                deleted_alert = self.alerts.pop(index)
                self.refresh_alerts_display()
                self.save_alerts()
                self.log_message(f"🗑️ Deleted alert: {deleted_alert.alert_name}")
    
    def toggle_selected_alert(self):
        """Toggle enabled/disabled status of selected alert"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an alert to toggle.")
            return
        
        item = selection[0]
        index = self.alerts_tree.index(item)
        
        if 0 <= index < len(self.alerts):
            alert = self.alerts[index]
            alert.enabled = not alert.enabled
            self.refresh_alerts_display()
            self.save_alerts()
            
            status = "enabled" if alert.enabled else "disabled"
            self.log_message(f"⏸️ Alert '{alert.alert_name}' {status}")
    
    def test_selected_alert(self):
        """Test the selected alert condition"""
        selection = self.alerts_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select an alert to test.")
            return
        
        item = selection[0]
        index = self.alerts_tree.index(item)
        
        if 0 <= index < len(self.alerts):
            alert = self.alerts[index]
            self.log_message(f"🧪 Testing alert: {alert.alert_name}")
            
            # Run test in separate thread
            threading.Thread(target=lambda: self.run_alert_test(alert), daemon=True).start()
    
    def run_alert_test(self, alert: AlertCondition):
        """Run alert test in background"""
        try:
            result = self.check_alert_condition(alert)
            if result:
                self.log_message(f"✅ Test PASSED - Alert '{alert.alert_name}' would trigger")
                self.trigger_alert(alert)
            else:
                self.log_message(f"❌ Test FAILED - Alert '{alert.alert_name}' conditions not met")
        except Exception as e:
            self.log_message(f"❌ Test ERROR - Alert '{alert.alert_name}': {str(e)}")
    
    def edit_selected_alert(self):
        """Edit the selected alert (placeholder)"""
        messagebox.showinfo("Coming Soon", "Alert editing feature will be available in the next update.")
    
    # Display and UI Update Methods
    def refresh_alerts_display(self):
        """Refresh the alerts tree display"""
        # Clear existing items
        for item in self.alerts_tree.get_children():
            self.alerts_tree.delete(item)
        
        # Add current alerts
        for alert in self.alerts:
            status = "✅ Enabled" if alert.enabled else "❌ Disabled"
            last_triggered = alert.last_triggered.strftime('%Y-%m-%d %H:%M') if alert.last_triggered else "Never"
            
            self.alerts_tree.insert('', tk.END, values=(
                alert.alert_name,
                alert.position.ticker,
                alert.strategy_type,
                f"${alert.min_premium:.2f}",
                f"{alert.max_strike_distance*100:.1f}%",
                status,
                last_triggered
            ))
    
    def update_last_check_time(self):
        """Update the last check time display"""
        current_time = datetime.now().strftime('%H:%M:%S')
        self.last_check_label.config(text=f"Last Check: {current_time}")
    
    def log_message(self, message: str):
        """Add a message to the alert log"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_entry = f"[{timestamp}] {message}\n"
        
        # Add to log list
        self.alert_log.append(log_entry)
        
        # Keep only last 100 entries
        if len(self.alert_log) > 100:
            self.alert_log = self.alert_log[-100:]
        
        # Update UI in main thread
        if self.log_text:
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
    
    def clear_log(self):
        """Clear the alert log"""
        self.alert_log.clear()
        self.log_text.delete(1.0, tk.END)
        self.log_message("📋 Alert log cleared")
    
    def export_log(self):
        """Export alert log to file"""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"alert_log_{timestamp}.txt"
            
            with open(filename, 'w') as f:
                f.writelines(self.alert_log)
            
            messagebox.showinfo("Export Complete", f"Alert log exported to {filename}")
            self.log_message(f"💾 Alert log exported to {filename}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export log: {str(e)}")
    
    # Settings Methods
    def update_interval(self):
        """Update monitoring interval"""
        try:
            minutes = int(self.interval_var.get())
            self.refresh_interval = minutes * 60
            self.log_message(f"⏱️ Monitoring interval updated to {minutes} minutes")
        except ValueError:
            pass
    
    def update_sound_setting(self):
        """Update sound notification setting"""
        self.sound_enabled = self.sound_var.get()
        status = "enabled" if self.sound_enabled else "disabled"
        self.log_message(f"🔊 Sound notifications {status}")
    
    def update_popup_setting(self):
        """Update popup notification setting"""
        self.popup_enabled = self.popup_var.get()
        status = "enabled" if self.popup_enabled else "disabled"
        self.log_message(f"💬 Popup notifications {status}")
    
    # Persistence Methods
    def save_alerts(self):
        """Save alerts to JSON file"""
        try:
            alerts_data = {
                'alerts': [alert.to_dict() for alert in self.alerts],
                'settings': {
                    'refresh_interval': self.refresh_interval,
                    'sound_enabled': self.sound_enabled,
                    'popup_enabled': self.popup_enabled
                },
                'saved_at': datetime.now().isoformat()
            }
            
            with open(self.alerts_file, 'w') as f:
                json.dump(alerts_data, f, indent=2)
                
        except Exception as e:
            self.log_message(f"❌ Failed to save alerts: {str(e)}")
    
    def load_alerts(self):
        """Load alerts from JSON file"""
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    data = json.load(f)
                
                # Load settings
                settings = data.get('settings', {})
                self.refresh_interval = settings.get('refresh_interval', 300)
                self.sound_enabled = settings.get('sound_enabled', True)
                self.popup_enabled = settings.get('popup_enabled', True)
                
                # Update UI
                self.interval_var.set(str(self.refresh_interval // 60))
                self.sound_var.set(self.sound_enabled)
                self.popup_var.set(self.popup_enabled)
                
                # Load alerts
                for alert_data in data.get('alerts', []):
                    ticker = alert_data['ticker']
                    
                    # Find matching position
                    position = self.portfolio.get_position(ticker)
                    
                    if position:
                        alert = AlertCondition.from_dict(alert_data, position)
                        self.alerts.append(alert)
                        self.log_message(f"✅ Loaded alert: {alert.alert_name}")
                    else:
                        self.log_message(f"⚠️ Skipped alert for {ticker} - position not found in portfolio")
                
                self.refresh_alerts_display()
                self.log_message(f"📋 Loaded {len(self.alerts)} alerts from configuration")
        
        except Exception as e:
            self.log_message(f"❌ Error loading alerts: {str(e)}")
            print(f"Alert loading error: {e}")  # Debug output

    def cleanup(self):
        """Cleanup when panel is closed"""
        self.stop_monitoring()
        self.save_alerts()
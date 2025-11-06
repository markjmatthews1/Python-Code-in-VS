#!/usr/bin/env python3
"""
Simple Live Dashboard Demo
Shows the visible Phase 4 changes without layout conflicts
"""

import tkinter as tk
from tkinter import ttk
import threading
import time
from datetime import datetime

class SimpleLiveDashboardDemo:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("🔴 Live Dashboard - Phase 4 Demo")
        self.window.geometry("900x600")
        self.window.configure(bg='#f0f0f0')
        
        self.is_monitoring = False
        self.setup_gui()
        
    def setup_gui(self):
        """Setup the dashboard GUI"""
        # Title
        title_label = ttk.Label(
            self.window, 
            text="🔴 CATALYST SCANNER LIVE DASHBOARD", 
            font=('Segoe UI', 16, 'bold')
        )
        title_label.pack(pady=10)
        
        # Control Panel
        control_frame = ttk.LabelFrame(self.window, text="Control Panel", padding=10)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        # Start/Stop Button
        self.toggle_button = ttk.Button(
            control_frame,
            text="▶ START LIVE MONITORING",
            command=self.toggle_monitoring,
            style='Accent.TButton'
        )
        self.toggle_button.pack(side='left', padx=(0, 10))
        
        # Status
        self.status_label = ttk.Label(
            control_frame,
            text="⚫ OFFLINE",
            font=('Segoe UI', 10, 'bold'),
            foreground='red'
        )
        self.status_label.pack(side='left', padx=(0, 20))
        
        # Update Frequency
        ttk.Label(control_frame, text="Update Every:").pack(side='left', padx=(0, 5))
        self.frequency_var = tk.StringVar(value="10")
        frequency_combo = ttk.Combobox(
            control_frame,
            textvariable=self.frequency_var,
            values=["5", "10", "30", "60"],
            width=5,
            state="readonly"
        )
        frequency_combo.pack(side='left', padx=(0, 5))
        ttk.Label(control_frame, text="seconds").pack(side='left')
        
        # Last Update
        self.last_update_label = ttk.Label(
            control_frame,
            text="Never updated",
            font=('Segoe UI', 9)
        )
        self.last_update_label.pack(side='right')
        
        # Tabbed Interface
        self.notebook = ttk.Notebook(self.window)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Create tabs
        self.create_live_scores_tab()
        self.create_portfolio_tab()
        self.create_performance_tab()
        self.create_risk_tab()
        
        # Status Bar
        status_frame = ttk.Frame(self.window)
        status_frame.pack(fill='x', side='bottom')
        self.connection_status = ttk.Label(
            status_frame,
            text="🔌 Ready to connect to real-time data",
            relief='sunken'
        )
        self.connection_status.pack(fill='x', padx=5, pady=2)
        
    def create_live_scores_tab(self):
        """Create live catalyst scores tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="🎯 Live Scores")
        
        # Sample data table
        columns = ("Ticker", "Catalyst", "Score", "Confidence", "Last Update")
        self.scores_tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)
        
        for col in columns:
            self.scores_tree.heading(col, text=col)
            self.scores_tree.column(col, width=120)
        
        self.scores_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add sample data
        sample_data = [
            ("AAPL", "Earnings Report", "8.5", "92%", "2 min ago"),
            ("MSFT", "Product Launch", "7.2", "85%", "1 min ago"),
            ("GOOGL", "AI Development", "6.8", "78%", "3 min ago"),
            ("TSLA", "Production Update", "7.9", "88%", "30 sec ago"),
            ("NVDA", "Chip Demand", "9.1", "95%", "1 min ago")
        ]
        
        for item in sample_data:
            self.scores_tree.insert("", "end", values=item)
            
    def create_portfolio_tab(self):
        """Create portfolio impact tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📊 Portfolio Impact")
        
        # Portfolio summary
        summary_frame = ttk.LabelFrame(frame, text="Portfolio Summary", padding=10)
        summary_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(summary_frame, text="Total Portfolio Value:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(summary_frame, text="$127,450.00", foreground='green').grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        ttk.Label(summary_frame, text="Today's P&L:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w')
        ttk.Label(summary_frame, text="+$2,340.00 (+1.87%)", foreground='green').grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        ttk.Label(summary_frame, text="Risk Level:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w')
        ttk.Label(summary_frame, text="🟡 MODERATE", foreground='orange').grid(row=2, column=1, sticky='w', padx=(10, 0))
        
        # Holdings table
        holdings_frame = ttk.LabelFrame(frame, text="Live Holdings Impact", padding=5)
        holdings_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        holdings_cols = ("Ticker", "Shares", "Value", "Today P&L", "Catalyst Impact")
        self.holdings_tree = ttk.Treeview(holdings_frame, columns=holdings_cols, show="headings", height=10)
        
        for col in holdings_cols:
            self.holdings_tree.heading(col, text=col)
            self.holdings_tree.column(col, width=100)
            
        self.holdings_tree.pack(fill='both', expand=True)
        
        # Sample holdings data
        holdings_data = [
            ("AAPL", "100", "$15,230", "+$340", "🟢 Positive"),
            ("MSFT", "75", "$25,650", "+$180", "🟢 Positive"),
            ("GOOGL", "50", "$12,450", "-$120", "🟡 Neutral"),
            ("TSLA", "25", "$18,750", "+$890", "🟢 Strong"),
            ("NVDA", "30", "$35,670", "+$1,200", "🟢 Very Strong")
        ]
        
        for item in holdings_data:
            self.holdings_tree.insert("", "end", values=item)
            
    def create_performance_tab(self):
        """Create performance tracking tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="📈 Performance")
        
        # Performance metrics
        metrics_frame = ttk.LabelFrame(frame, text="Prediction Accuracy", padding=10)
        metrics_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(metrics_frame, text="Total Predictions:", font=('Segoe UI', 10, 'bold')).grid(row=0, column=0, sticky='w')
        ttk.Label(metrics_frame, text="247").grid(row=0, column=1, sticky='w', padx=(10, 0))
        
        ttk.Label(metrics_frame, text="Successful Hits:", font=('Segoe UI', 10, 'bold')).grid(row=1, column=0, sticky='w')
        ttk.Label(metrics_frame, text="189 (76.5%)", foreground='green').grid(row=1, column=1, sticky='w', padx=(10, 0))
        
        ttk.Label(metrics_frame, text="Average Score:", font=('Segoe UI', 10, 'bold')).grid(row=2, column=0, sticky='w')
        ttk.Label(metrics_frame, text="7.8/10").grid(row=2, column=1, sticky='w', padx=(10, 0))
        
        # Recent predictions
        recent_frame = ttk.LabelFrame(frame, text="Recent Predictions", padding=5)
        recent_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        recent_cols = ("Date", "Ticker", "Catalyst", "Predicted", "Actual", "Result")
        self.recent_tree = ttk.Treeview(recent_frame, columns=recent_cols, show="headings", height=10)
        
        for col in recent_cols:
            self.recent_tree.heading(col, text=col)
            self.recent_tree.column(col, width=90)
            
        self.recent_tree.pack(fill='both', expand=True)
        
        # Sample recent data
        recent_data = [
            ("2025-01-26", "AAPL", "Earnings", "📈 UP", "📈 UP", "✅ HIT"),
            ("2025-01-25", "MSFT", "Product", "📈 UP", "📈 UP", "✅ HIT"),
            ("2025-01-24", "GOOGL", "AI News", "📈 UP", "📉 DOWN", "❌ MISS"),
            ("2025-01-23", "TSLA", "Production", "📈 UP", "📈 UP", "✅ HIT"),
            ("2025-01-22", "NVDA", "Guidance", "📈 UP", "📈 UP", "✅ HIT")
        ]
        
        for item in recent_data:
            self.recent_tree.insert("", "end", values=item)
            
    def create_risk_tab(self):
        """Create risk monitoring tab"""
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="⚠️ Risk Monitor")
        
        # Risk alerts
        alerts_frame = ttk.LabelFrame(frame, text="Active Risk Alerts", padding=10)
        alerts_frame.pack(fill='x', padx=5, pady=5)
        
        self.risk_text = tk.Text(alerts_frame, height=6, font=('Segoe UI', 9))
        self.risk_text.pack(fill='x')
        
        # Sample risk alerts
        risk_alerts = """🟡 MODERATE RISK: Portfolio concentrated in tech sector (78%)
🟢 LOW RISK: Diversification score improved to 7.2/10
🟡 MODERATE RISK: TSLA position size exceeds 15% of portfolio
🟢 LOW RISK: All positions have stop losses in place
🔵 INFO: VIX below 20 - market volatility low"""
        
        self.risk_text.insert('1.0', risk_alerts)
        self.risk_text.config(state='disabled')
        
        # Risk metrics table
        metrics_frame = ttk.LabelFrame(frame, text="Risk Metrics", padding=5)
        metrics_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        risk_cols = ("Metric", "Current Value", "Target Range", "Status")
        self.risk_tree = ttk.Treeview(metrics_frame, columns=risk_cols, show="headings", height=8)
        
        for col in risk_cols:
            self.risk_tree.heading(col, text=col)
            self.risk_tree.column(col, width=130)
            
        self.risk_tree.pack(fill='both', expand=True)
        
        # Sample risk metrics
        risk_data = [
            ("Portfolio Beta", "1.12", "0.8 - 1.2", "🟢 Normal"),
            ("Max Drawdown", "8.5%", "< 10%", "🟢 Good"),
            ("Sector Concentration", "78%", "< 60%", "🟡 High"),
            ("Position Size Max", "15.2%", "< 15%", "🟡 Elevated"),
            ("Correlation Risk", "0.65", "< 0.7", "🟢 Acceptable"),
            ("Volatility (30d)", "18.5%", "< 25%", "🟢 Low")
        ]
        
        for item in risk_data:
            self.risk_tree.insert("", "end", values=item)
    
    def toggle_monitoring(self):
        """Toggle live monitoring on/off"""
        if not self.is_monitoring:
            self.start_monitoring()
        else:
            self.stop_monitoring()
    
    def start_monitoring(self):
        """Start live monitoring"""
        self.is_monitoring = True
        self.toggle_button.config(text="⏹ STOP MONITORING")
        self.status_label.config(text="🟢 LIVE", foreground='green')
        self.connection_status.config(text="🔌 Connected - Streaming real-time data")
        
        # Start update thread
        self.update_thread = threading.Thread(target=self.update_loop, daemon=True)
        self.update_thread.start()
        
        print("🟢 Live monitoring STARTED!")
        
    def stop_monitoring(self):
        """Stop live monitoring"""
        self.is_monitoring = False
        self.toggle_button.config(text="▶ START LIVE MONITORING")
        self.status_label.config(text="⚫ OFFLINE", foreground='red')
        self.connection_status.config(text="🔌 Disconnected - Ready to reconnect")
        
        print("⚫ Live monitoring STOPPED!")
        
    def update_loop(self):
        """Main update loop for live data"""
        while self.is_monitoring:
            try:
                # Update timestamp
                now = datetime.now().strftime("%H:%M:%S")
                self.window.after(0, lambda: self.last_update_label.config(text=f"Last update: {now}"))
                
                # Simulate data updates (in real version, this would fetch actual data)
                time.sleep(int(self.frequency_var.get()))
                
            except Exception as e:
                print(f"Update error: {e}")
                break
    
    def run(self):
        """Run the dashboard"""
        print("🚀 Starting Live Dashboard Demo...")
        print("=" * 50)
        print("This is what's NEW in Phase 4:")
        print("✨ Real-time monitoring with START/STOP controls")
        print("✨ Professional tabbed interface")
        print("✨ Live portfolio impact tracking")
        print("✨ Performance prediction accuracy")
        print("✨ Risk monitoring and alerts")
        print("=" * 50)
        print("Click '▶ START LIVE MONITORING' to see it in action!")
        
        self.window.mainloop()

if __name__ == "__main__":
    demo = SimpleLiveDashboardDemo()
    demo.run()
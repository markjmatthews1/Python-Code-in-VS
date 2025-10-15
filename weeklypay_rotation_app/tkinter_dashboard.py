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

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.etf_tracker import ETFTracker
from src.signal_engine import RotationRulesEngine
from src.data_collector import DataCollector

class WeeklyPayGUI:
    """Simple GUI for WeeklyPay™ rotation system"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("WeeklyPay™ Rotation Dashboard")
        self.root.geometry("1000x700")
        self.root.configure(bg='white')
        
        # Initialize system components
        self.data = None
        self.setup_system()
        
        # Create GUI elements
        self.create_widgets()
        
        # Load initial data
        self.refresh_data()
    
    def setup_system(self):
        """Initialize the rotation system"""
        try:
            self.tracker = ETFTracker("data/etf_list.json")
            self.engine = RotationRulesEngine(self.tracker)
            self.data_collector = DataCollector(self.tracker)
            self.data_collector.set_signal_engine(self.engine)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize system: {e}")
    
    def create_widgets(self):
        """Create GUI widgets"""
        
        # Title
        title_frame = tk.Frame(self.root, bg='white')
        title_frame.pack(fill=tk.X, padx=10, pady=10)
        
        title_label = tk.Label(
            title_frame,
            text="📈 WeeklyPay™ Rotation Dashboard",
            font=("Arial", 20, "bold"),
            fg="#1f77b4",
            bg='white'
        )
        title_label.pack()
        
        # Control buttons
        control_frame = tk.Frame(self.root, bg='white')
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
        
        # Status label
        self.status_label = tk.Label(
            control_frame,
            text="Status: Ready",
            font=("Arial", 10),
            bg='white',
            fg="#666"
        )
        self.status_label.pack(side=tk.RIGHT, padx=5)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
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
            
            self.status_label.config(text=f"Status: Updated {datetime.datetime.now().strftime('%H:%M:%S')}")
            
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
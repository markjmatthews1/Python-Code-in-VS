"""
WeeklyPay™ Manual Data Entry GUI
Interactive GUI for entering earnings dates and other financial data 
when API sources are unreliable or unavailable.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from datetime import datetime, timedelta
import json
import os
from typing import Dict, Tuple, Optional

class WeeklyPayDataEntryGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("WeeklyPay™ Manual Data Entry")
        self.root.geometry("800x600")
        self.root.configure(bg='#2c3e50')
        
        # Data storage
        self.manual_data_file = "manual_earnings_data.json"
        self.manual_data = self.load_manual_data()
        
        # ETF to stock mapping
        self.underlying_stocks = {
            'NVDW': 'NVDA',
            'AMDW': 'AMD', 
            'HOOW': 'HOOD',
            'MSFW': 'MSFT',
            'GOOW': 'GOOGL',
            'NFLW': 'NFLX'
        }
        
        self.setup_gui()
        
    def load_manual_data(self) -> Dict:
        """Load previously entered manual data"""
        if os.path.exists(self.manual_data_file):
            try:
                with open(self.manual_data_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading manual data: {e}")
        return {}
    
    def save_manual_data(self):
        """Save manual data to file"""
        try:
            with open(self.manual_data_file, 'w') as f:
                json.dump(self.manual_data, f, indent=2)
            print(f"Manual data saved to {self.manual_data_file}")
        except Exception as e:
            print(f"Error saving manual data: {e}")
    
    def setup_gui(self):
        """Setup the main GUI interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title_label = tk.Label(
            title_frame, 
            text="WeeklyPay™ Manual Data Entry",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title_label.pack()
        
        subtitle_label = tk.Label(
            title_frame,
            text="Enter earnings dates when API data is unreliable",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        subtitle_label.pack()
        
        # Main content area
        main_frame = tk.Frame(self.root, bg='#34495e')
        main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Left panel - ETF list and current data
        left_frame = tk.Frame(main_frame, bg='#34495e')
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(
            left_frame,
            text="Current Earnings Data",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(0, 10))
        
        # Treeview for current data
        self.tree = ttk.Treeview(
            left_frame,
            columns=('Stock', 'Current Date', 'Days Away', 'Source'),
            show='tree headings'
        )
        self.tree.heading('#0', text='ETF')
        self.tree.heading('Stock', text='Underlying Stock')
        self.tree.heading('Current Date', text='Earnings Date')
        self.tree.heading('Days Away', text='Days Away')
        self.tree.heading('Source', text='Data Source')
        
        # Column widths
        self.tree.column('#0', width=60)
        self.tree.column('Stock', width=80)
        self.tree.column('Current Date', width=100)
        self.tree.column('Days Away', width=80)
        self.tree.column('Source', width=120)
        
        self.tree.pack(fill='both', expand=True)
        
        # Right panel - Manual entry
        right_frame = tk.Frame(main_frame, bg='#34495e')
        right_frame.pack(side='right', fill='y', padx=(10, 0))
        
        tk.Label(
            right_frame,
            text="Manual Data Entry",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(0, 20))
        
        # ETF selection
        tk.Label(
            right_frame,
            text="Select ETF:",
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(anchor='w')
        
        self.etf_var = tk.StringVar(value="HOOW")
        self.etf_combo = ttk.Combobox(
            right_frame,
            textvariable=self.etf_var,
            values=list(self.underlying_stocks.keys()),
            state='readonly',
            width=15
        )
        self.etf_combo.pack(pady=(5, 15), anchor='w')
        
        # Date entry
        tk.Label(
            right_frame,
            text="Earnings Date (YYYY-MM-DD):",
            font=('Arial', 10),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(anchor='w')
        
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(
            right_frame,
            textvariable=self.date_var,
            font=('Arial', 10),
            width=20
        )
        self.date_entry.pack(pady=(5, 15), anchor='w')
        
        # Quick date buttons
        quick_frame = tk.Frame(right_frame, bg='#34495e')
        quick_frame.pack(fill='x', pady=(0, 15))
        
        tk.Label(
            quick_frame,
            text="Quick dates:",
            font=('Arial', 9),
            bg='#34495e',
            fg='#95a5a6'
        ).pack(anchor='w')
        
        button_frame = tk.Frame(quick_frame, bg='#34495e')
        button_frame.pack(fill='x', pady=5)
        
        # Quick date buttons
        quick_dates = [
            ("1 week", 7),
            ("2 weeks", 14),
            ("3 weeks", 21),
            ("1 month", 30)
        ]
        
        for text, days in quick_dates:
            btn = tk.Button(
                button_frame,
                text=text,
                command=lambda d=days: self.set_quick_date(d),
                bg='#3498db',
                fg='white',
                font=('Arial', 8),
                width=8
            )
            btn.pack(side='left', padx=2)
        
        # Action buttons
        btn_frame = tk.Frame(right_frame, bg='#34495e')
        btn_frame.pack(fill='x', pady=20)
        
        self.save_btn = tk.Button(
            btn_frame,
            text="Save Entry",
            command=self.save_entry,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        )
        self.save_btn.pack(pady=5)
        
        self.delete_btn = tk.Button(
            btn_frame,
            text="Delete Entry",
            command=self.delete_entry,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10),
            width=15
        )
        self.delete_btn.pack(pady=5)
        
        self.refresh_btn = tk.Button(
            btn_frame,
            text="Refresh Display",
            command=self.refresh_display,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10),
            width=15
        )
        self.refresh_btn.pack(pady=5)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready for manual data entry")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg='#95a5a6',
            fg='#2c3e50',
            font=('Arial', 9),
            anchor='w'
        )
        status_bar.pack(fill='x', side='bottom')
        
        # Load and display current data
        self.refresh_display()
    
    def set_quick_date(self, days_ahead: int):
        """Set date entry to a quick date option"""
        future_date = datetime.now() + timedelta(days=days_ahead)
        self.date_var.set(future_date.strftime('%Y-%m-%d'))
    
    def validate_date(self, date_str: str) -> Optional[datetime]:
        """Validate and parse date string"""
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter date in YYYY-MM-DD format")
            return None
    
    def save_entry(self):
        """Save manual earnings entry"""
        etf = self.etf_var.get()
        date_str = self.date_var.get().strip()
        
        if not etf or not date_str:
            messagebox.showerror("Missing Data", "Please select an ETF and enter a date")
            return
        
        # Validate date
        earnings_date = self.validate_date(date_str)
        if not earnings_date:
            return
        
        # Check if date is in the past
        if earnings_date.date() < datetime.now().date():
            result = messagebox.askyesno(
                "Past Date Warning",
                f"The date {date_str} is in the past. Are you sure you want to save this?"
            )
            if not result:
                return
        
        # Save the data
        self.manual_data[etf] = {
            'earnings_date': date_str,
            'underlying_stock': self.underlying_stocks[etf],
            'entry_timestamp': datetime.now().isoformat(),
            'source': 'manual_entry'
        }
        
        self.save_manual_data()
        self.refresh_display()
        
        days_away = (earnings_date - datetime.now()).days
        self.status_var.set(f"Saved: {etf} earnings on {date_str} ({days_away} days away)")
        
        # Clear the entry
        self.date_var.set("")
    
    def delete_entry(self):
        """Delete manual entry for selected ETF"""
        etf = self.etf_var.get()
        
        if etf not in self.manual_data:
            messagebox.showinfo("No Entry", f"No manual entry found for {etf}")
            return
        
        result = messagebox.askyesno(
            "Confirm Delete",
            f"Delete manual entry for {etf}?"
        )
        
        if result:
            del self.manual_data[etf]
            self.save_manual_data()
            self.refresh_display()
            self.status_var.set(f"Deleted manual entry for {etf}")
    
    def refresh_display(self):
        """Refresh the display with current data"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        current_date = datetime.now()
        
        # Display data for each ETF
        for etf, stock in self.underlying_stocks.items():
            if etf in self.manual_data:
                # Use manual data
                data = self.manual_data[etf]
                earnings_date = datetime.strptime(data['earnings_date'], '%Y-%m-%d')
                days_away = (earnings_date - current_date).days
                source = "Manual Entry"
                date_str = data['earnings_date']
            else:
                # Show that API data would be used
                date_str = "API Data"
                days_away = "N/A"
                source = "API (Auto)"
            
            self.tree.insert(
                '',
                'end',
                text=etf,
                values=(stock, date_str, days_away, source)
            )
    
    def get_manual_earnings_data(self) -> Dict:
        """Return manual earnings data for external use"""
        return self.manual_data.copy()
    
    def run(self):
        """Run the GUI"""
        self.root.mainloop()

def prompt_for_missing_data(missing_tickers: list) -> Dict:
    """
    Prompt user for missing earnings data
    Returns dictionary with manual entries
    """
    if not missing_tickers:
        return {}
    
    # Create a focused dialog for missing data
    root = tk.Tk()
    root.title("Missing Earnings Data")
    root.geometry("500x400")
    root.configure(bg='#2c3e50')
    
    # Center the window
    root.geometry("+%d+%d" % (root.winfo_screenwidth()/2-250, root.winfo_screenheight()/2-200))
    
    result_data = {}
    
    def close_dialog():
        root.quit()
        root.destroy()
    
    # Title
    tk.Label(
        root,
        text="⚠️ Missing Earnings Data",
        font=('Arial', 16, 'bold'),
        bg='#2c3e50',
        fg='#e74c3c'
    ).pack(pady=20)
    
    tk.Label(
        root,
        text="API data unavailable for the following ETFs.\nPlease enter earnings dates manually:",
        font=('Arial', 10),
        bg='#2c3e50',
        fg='#ecf0f1',
        justify='center'
    ).pack(pady=10)
    
    # Entry frame
    entry_frame = tk.Frame(root, bg='#34495e')
    entry_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    entries = {}
    
    for i, ticker in enumerate(missing_tickers):
        row_frame = tk.Frame(entry_frame, bg='#34495e')
        row_frame.pack(fill='x', pady=5)
        
        tk.Label(
            row_frame,
            text=f"{ticker}:",
            font=('Arial', 10, 'bold'),
            bg='#34495e',
            fg='#ecf0f1',
            width=8
        ).pack(side='left')
        
        entry = tk.Entry(
            row_frame,
            font=('Arial', 10),
            width=15
        )
        entry.pack(side='left', padx=10)
        entries[ticker] = entry
        
        # Quick date buttons for each ticker
        for days, text in [(7, "1w"), (14, "2w"), (21, "3w"), (30, "1m")]:
            btn = tk.Button(
                row_frame,
                text=text,
                command=lambda e=entry, d=days: e.insert(0, (datetime.now() + timedelta(days=d)).strftime('%Y-%m-%d')),
                bg='#3498db',
                fg='white',
                font=('Arial', 8),
                width=3
            )
            btn.pack(side='left', padx=1)
    
    def save_and_close():
        for ticker, entry in entries.items():
            date_str = entry.get().strip()
            if date_str:
                try:
                    # Validate date format
                    datetime.strptime(date_str, '%Y-%m-%d')
                    result_data[ticker] = date_str
                except ValueError:
                    messagebox.showerror("Invalid Date", f"Invalid date format for {ticker}: {date_str}")
                    return
        close_dialog()
    
    # Buttons
    btn_frame = tk.Frame(root, bg='#2c3e50')
    btn_frame.pack(fill='x', pady=10)
    
    tk.Button(
        btn_frame,
        text="Save & Continue",
        command=save_and_close,
        bg='#27ae60',
        fg='white',
        font=('Arial', 10, 'bold'),
        width=15
    ).pack(side='left', padx=20)
    
    tk.Button(
        btn_frame,
        text="Skip (Use Estimates)",
        command=close_dialog,
        bg='#95a5a6',
        fg='white',
        font=('Arial', 10),
        width=15
    ).pack(side='right', padx=20)
    
    root.mainloop()
    
    return result_data

if __name__ == "__main__":
    # Test the GUI
    app = WeeklyPayDataEntryGUI()
    app.run()
"""
WeeklyPay Trade Diagnostic & Recovery Tool
Helps diagnose missing trades and provides manual entry/editing interface

Features:
- View all trades in color-coded table
- Add missing trades manually
- Edit existing trades (double-click or use Edit button)
- Delete incorrect trades
- Real-time statistics and status updates
"""

import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import pandas as pd
from datetime import datetime
import os
import csv

class TradeDiagnosticTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🔧 WeeklyPay Trade Diagnostic & Recovery Tool")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # BUGFIX: Use absolute path to ensure we always access the same CSV file
        # regardless of where the tool is launched from
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.trade_file = os.path.join(script_dir, "weeklypay_trades.csv")
        
        # Log the file path for debugging
        print(f"📂 Trade file location: {self.trade_file}")
        
        self.setup_gui()
        self.load_and_display_trades()
        
    def setup_gui(self):
        """Setup the diagnostic interface"""
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50')
        title_frame.pack(fill='x', padx=20, pady=10)
        
        title = tk.Label(
            title_frame,
            text="🔧 WeeklyPay Trade Diagnostic & Recovery Tool",
            font=('Arial', 18, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        )
        title.pack()
        
        subtitle = tk.Label(
            title_frame,
            text="View, Add, Edit, and Delete trades • Double-click to edit",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#95a5a6'
        )
        subtitle.pack()
        
        # Main container
        main_container = tk.Frame(self.root, bg='#34495e')
        main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # === LEFT PANEL: Current Trades Display ===
        left_panel = tk.Frame(main_container, bg='#34495e')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        tk.Label(
            left_panel,
            text="📊 Current Trades in CSV",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(0, 10))
        
        # Treeview for trades
        tree_frame = tk.Frame(left_panel, bg='#34495e')
        tree_frame.pack(fill='both', expand=True)
        
        # Scrollbars
        v_scroll = ttk.Scrollbar(tree_frame, orient='vertical')
        h_scroll = ttk.Scrollbar(tree_frame, orient='horizontal')
        
        self.tree = ttk.Treeview(
            tree_frame,
            columns=('Date', 'Ticker', 'Action', 'Qty', 'Price', 'Total', 'Notes'),
            show='tree headings',
            yscrollcommand=v_scroll.set,
            xscrollcommand=h_scroll.set
        )
        
        v_scroll.config(command=self.tree.yview)
        h_scroll.config(command=self.tree.xview)
        
        # Column configuration
        self.tree.column('#0', width=30)
        self.tree.column('Date', width=100)
        self.tree.column('Ticker', width=70)
        self.tree.column('Action', width=80)
        self.tree.column('Qty', width=60)
        self.tree.column('Price', width=80)
        self.tree.column('Total', width=100)
        self.tree.column('Notes', width=150)
        
        # Headings
        self.tree.heading('Date', text='Date')
        self.tree.heading('Ticker', text='Ticker')
        self.tree.heading('Action', text='Action')
        self.tree.heading('Qty', text='Quantity')
        self.tree.heading('Price', text='Price')
        self.tree.heading('Total', text='Total')
        self.tree.heading('Notes', text='Notes')
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scroll.grid(row=0, column=1, sticky='ns')
        h_scroll.grid(row=1, column=0, sticky='ew')
        
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Stats frame
        stats_frame = tk.Frame(left_panel, bg='#2c3e50', pady=10)
        stats_frame.pack(fill='x', pady=(10, 0))
        
        self.stats_label = tk.Label(
            stats_frame,
            text="",
            font=('Arial', 10),
            bg='#2c3e50',
            fg='#ecf0f1',
            justify='left'
        )
        self.stats_label.pack(padx=10, pady=5)
        
        # === RIGHT PANEL: Manual Entry Form ===
        right_panel = tk.Frame(main_container, bg='#34495e', width=350)
        right_panel.pack(side='right', fill='both', padx=(10, 0))
        right_panel.pack_propagate(False)
        
        tk.Label(
            right_panel,
            text="➕ Add Missing Trade",
            font=('Arial', 12, 'bold'),
            bg='#34495e',
            fg='#ecf0f1'
        ).pack(pady=(0, 10))
        
        # Form fields
        form_frame = tk.Frame(right_panel, bg='#34495e')
        form_frame.pack(fill='x', padx=10)
        
        # Date
        tk.Label(form_frame, text="📅 Date (YYYY-MM-DD):", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(form_frame, textvariable=self.date_var, font=('Arial', 10), width=25).pack(fill='x', pady=(0, 10))
        
        # Ticker
        tk.Label(form_frame, text="🎯 Ticker:", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.ticker_var = tk.StringVar()
        ticker_entry = tk.Entry(form_frame, textvariable=self.ticker_var, font=('Arial', 10), width=25)
        ticker_entry.pack(fill='x', pady=(0, 10))
        
        # Action
        tk.Label(form_frame, text="⚡ Action:", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.action_var = tk.StringVar(value='BUY')
        action_frame = tk.Frame(form_frame, bg='#34495e')
        action_frame.pack(fill='x', pady=(0, 10))
        
        for action in ['BUY', 'SELL', 'DIVIDEND']:
            tk.Radiobutton(
                action_frame,
                text=action,
                variable=self.action_var,
                value=action,
                bg='#34495e',
                fg='#ecf0f1',
                selectcolor='#2c3e50',
                font=('Arial', 9)
            ).pack(side='left', padx=5)
        
        # Quantity
        tk.Label(form_frame, text="🔢 Quantity:", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.qty_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.qty_var, font=('Arial', 10), width=25).pack(fill='x', pady=(0, 10))
        
        # Price
        tk.Label(form_frame, text="💰 Price:", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.price_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.price_var, font=('Arial', 10), width=25).pack(fill='x', pady=(0, 10))
        
        # Notes
        tk.Label(form_frame, text="📝 Notes:", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.notes_var = tk.StringVar()
        tk.Entry(form_frame, textvariable=self.notes_var, font=('Arial', 10), width=25).pack(fill='x', pady=(0, 10))
        
        # WeeklyPay Score (optional)
        tk.Label(form_frame, text="⭐ WeeklyPay Score (optional):", bg='#34495e', fg='#ecf0f1', font=('Arial', 9)).pack(anchor='w')
        self.score_var = tk.StringVar(value="N/A")
        tk.Entry(form_frame, textvariable=self.score_var, font=('Arial', 10), width=25).pack(fill='x', pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='#34495e')
        button_frame.pack(fill='x')
        
        tk.Button(
            button_frame,
            text="💾 Add Trade",
            command=self.add_trade,
            bg='#27ae60',
            fg='white',
            font=('Arial', 10, 'bold'),
            relief='flat',
            cursor='hand2'
        ).pack(fill='x', pady=(0, 5))
        
        tk.Button(
            button_frame,
            text="🔄 Refresh Display",
            command=self.load_and_display_trades,
            bg='#3498db',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2'
        ).pack(fill='x', pady=(0, 5))
        
        tk.Button(
            button_frame,
            text="✏️ Edit Selected",
            command=self.edit_selected_trade,
            bg='#f39c12',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2'
        ).pack(fill='x', pady=(0, 5))
        
        tk.Button(
            button_frame,
            text="🗑️ Delete Selected",
            command=self.delete_selected_trade,
            bg='#e74c3c',
            fg='white',
            font=('Arial', 10),
            relief='flat',
            cursor='hand2'
        ).pack(fill='x', pady=(0, 5))
        
        # Status message area
        status_frame = tk.Frame(right_panel, bg='#2c3e50', pady=10)
        status_frame.pack(fill='both', expand=True, padx=10, pady=(20, 0))
        
        tk.Label(
            status_frame,
            text="ℹ️ Status Messages:",
            font=('Arial', 9, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack(anchor='w')
        
        self.status_text = scrolledtext.ScrolledText(
            status_frame,
            height=8,
            width=40,
            font=('Courier', 8),
            bg='#1c2833',
            fg='#ecf0f1',
            wrap='word'
        )
        self.status_text.pack(fill='both', expand=True, pady=(5, 0))
        
        # Bind double-click to edit
        self.tree.bind('<Double-Button-1>', self.on_trade_double_click)
        
    def log_status(self, message):
        """Add status message with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert('1.0', f"[{timestamp}] {message}\n")
        self.status_text.see('1.0')
        
    def load_and_display_trades(self):
        """Load trades from CSV and display in tree"""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        try:
            if not os.path.exists(self.trade_file):
                self.log_status(f"❌ File not found: {self.trade_file}")
                self.stats_label.config(text="📂 File: Not Found\n💼 Trades: 0")
                return
            
            df = pd.read_csv(self.trade_file)
            
            if df.empty:
                self.log_status("⚠️ CSV file is empty")
                self.stats_label.config(text="📂 File: Found\n💼 Trades: 0")
                return
            
            # Display trades
            for idx, row in df.iterrows():
                action = row['Action']
                
                # Color code based on action
                if action == 'BUY':
                    tag = 'buy'
                elif action == 'SELL':
                    tag = 'sell'
                elif action == 'DIVIDEND':
                    tag = 'dividend'
                else:
                    tag = 'other'
                
                self.tree.insert('', 'end', text=str(idx+1), values=(
                    row['Date'],
                    row['Ticker'],
                    row['Action'],
                    row['Quantity'],
                    f"${row['Price']:.2f}",
                    f"${row['Total']:.2f}",
                    row['Notes'] if pd.notna(row['Notes']) else ''
                ), tags=(tag,))
            
            # Configure tag colors
            self.tree.tag_configure('buy', background='#d4edda')
            self.tree.tag_configure('sell', background='#f8d7da')
            self.tree.tag_configure('dividend', background='#fff3cd')
            self.tree.tag_configure('other', background='#e2e3e5')
            
            # Update stats
            total_trades = len(df)
            buy_count = len(df[df['Action'] == 'BUY'])
            sell_count = len(df[df['Action'] == 'SELL'])
            div_count = len(df[df['Action'] == 'DIVIDEND'])
            total_invested = df[df['Action'] == 'BUY']['Total'].sum()
            total_dividends = df[df['Action'] == 'DIVIDEND']['Total'].sum()
            
            stats_text = f"""📂 File: {self.trade_file}
💼 Total Trades: {total_trades}
🟢 Buys: {buy_count}
🔴 Sells: {sell_count}
💰 Dividends: {div_count}
💵 Total Invested: ${total_invested:,.2f}
💸 Total Dividends: ${total_dividends:,.2f}"""
            
            self.stats_label.config(text=stats_text)
            self.log_status(f"✅ Loaded {total_trades} trades from CSV")
            
        except Exception as e:
            self.log_status(f"❌ Error loading trades: {e}")
            messagebox.showerror("Error", f"Failed to load trades:\n{e}")
    
    def add_trade(self):
        """Add a new trade to the CSV"""
        try:
            # Validate inputs
            if not self.ticker_var.get():
                messagebox.showwarning("Missing Data", "Please enter a ticker symbol")
                return
            
            if not self.qty_var.get() or not self.price_var.get():
                messagebox.showwarning("Missing Data", "Please enter quantity and price")
                return
            
            # Calculate values
            qty = float(self.qty_var.get())
            price = float(self.price_var.get())
            total = qty * price
            action = self.action_var.get()
            
            # Determine dividend fields
            if action == 'DIVIDEND':
                dividend_per_share = price
                total_dividends = total
            else:
                dividend_per_share = 0
                total_dividends = 0
            
            # Create new row
            new_row = {
                'Date': self.date_var.get(),
                'Ticker': self.ticker_var.get().upper(),
                'Action': action,
                'Quantity': qty,
                'Price': price,
                'Total': total,
                'Notes': self.notes_var.get(),
                'WeeklyPay_Score': self.score_var.get(),
                'Dividend_Per_Share': dividend_per_share,
                'Total_Dividends': total_dividends
            }
            
            # Append to CSV
            file_exists = os.path.exists(self.trade_file)
            
            with open(self.trade_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=new_row.keys())
                
                if not file_exists:
                    writer.writeheader()
                
                writer.writerow(new_row)
            
            # Clear form
            self.ticker_var.set('')
            self.qty_var.set('')
            self.price_var.set('')
            self.notes_var.set('')
            self.score_var.set('N/A')
            
            # Refresh display
            self.load_and_display_trades()
            
            self.log_status(f"✅ Added: {action} {qty} {new_row['Ticker']} @ ${price:.2f}")
            messagebox.showinfo("Success", f"Trade added successfully!\n\n{action} {qty} {new_row['Ticker']} @ ${price:.2f}")
            
        except ValueError as e:
            messagebox.showerror("Invalid Input", f"Please check your numeric values:\n{e}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add trade:\n{e}")
            self.log_status(f"❌ Error adding trade: {e}")
    
    def delete_selected_trade(self):
        """Delete the selected trade from CSV"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select a trade to delete")
            return
        
        # Get the row number
        item = selected[0]
        row_number = int(self.tree.item(item, 'text')) - 1  # Convert to 0-based index
        
        # Confirm deletion
        values = self.tree.item(item, 'values')
        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Delete this trade?\n\n{values[0]} - {values[1]} {values[2]} {values[3]} @ {values[4]}"
        )
        
        if not confirm:
            return
        
        try:
            # Load CSV
            df = pd.read_csv(self.trade_file)
            
            # Delete row
            df = df.drop(df.index[row_number])
            
            # Save back
            df.to_csv(self.trade_file, index=False)
            
            # Refresh display
            self.load_and_display_trades()
            
            self.log_status(f"✅ Deleted trade at row {row_number + 1}")
            messagebox.showinfo("Success", "Trade deleted successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete trade:\n{e}")
            self.log_status(f"❌ Error deleting trade: {e}")
    
    def on_trade_double_click(self, event):
        """Handle double-click on trade to edit"""
        self.edit_selected_trade()
    
    def edit_selected_trade(self):
        """Edit the selected trade"""
        selected = self.tree.selection()
        
        if not selected:
            messagebox.showwarning("No Selection", "Please select a trade to edit")
            return
        
        # Get the row number
        item = selected[0]
        row_number = int(self.tree.item(item, 'text')) - 1  # Convert to 0-based index
        
        try:
            # Load CSV
            df = pd.read_csv(self.trade_file)
            row = df.iloc[row_number]
            
            # Create edit dialog
            self.show_edit_dialog(row_number, row)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load trade for editing:\n{e}")
            self.log_status(f"❌ Error loading trade: {e}")
    
    def show_edit_dialog(self, row_number, row):
        """Show dialog to edit trade details"""
        # Create edit window
        edit_window = tk.Toplevel(self.root)
        edit_window.title(f"✏️ Edit Trade #{row_number + 1}")
        edit_window.geometry("450x550")
        edit_window.configure(bg='#34495e')
        edit_window.transient(self.root)
        edit_window.grab_set()
        
        # Title
        title_frame = tk.Frame(edit_window, bg='#2c3e50', pady=15)
        title_frame.pack(fill='x')
        
        tk.Label(
            title_frame,
            text=f"✏️ Edit Trade #{row_number + 1}",
            font=('Arial', 14, 'bold'),
            bg='#2c3e50',
            fg='#ecf0f1'
        ).pack()
        
        tk.Label(
            title_frame,
            text=f"Original: {row['Date']} - {row['Ticker']} {row['Action']}",
            font=('Arial', 9),
            bg='#2c3e50',
            fg='#95a5a6'
        ).pack()
        
        # Form
        form_frame = tk.Frame(edit_window, bg='#34495e', pady=20)
        form_frame.pack(fill='both', expand=True, padx=20)
        
        # Create variables with current values
        date_var = tk.StringVar(value=str(row['Date']))
        ticker_var = tk.StringVar(value=str(row['Ticker']))
        action_var = tk.StringVar(value=str(row['Action']))
        qty_var = tk.StringVar(value=str(row['Quantity']))
        price_var = tk.StringVar(value=str(row['Price']))
        notes_var = tk.StringVar(value=str(row['Notes']) if pd.notna(row['Notes']) else '')
        score_var = tk.StringVar(value=str(row['WeeklyPay_Score']) if pd.notna(row['WeeklyPay_Score']) else 'N/A')
        
        # Date field
        tk.Label(form_frame, text="📅 Date (YYYY-MM-DD):", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        date_entry = tk.Entry(form_frame, textvariable=date_var, font=('Arial', 11), width=30)
        date_entry.pack(fill='x', pady=(0, 15))
        
        # Ticker field
        tk.Label(form_frame, text="🎯 Ticker:", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        ticker_entry = tk.Entry(form_frame, textvariable=ticker_var, font=('Arial', 11), width=30)
        ticker_entry.pack(fill='x', pady=(0, 15))
        
        # Action field
        tk.Label(form_frame, text="⚡ Action:", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        action_frame = tk.Frame(form_frame, bg='#34495e')
        action_frame.pack(fill='x', pady=(0, 15))
        
        for action in ['BUY', 'SELL', 'DIVIDEND']:
            tk.Radiobutton(
                action_frame,
                text=action,
                variable=action_var,
                value=action,
                bg='#34495e',
                fg='#ecf0f1',
                selectcolor='#2c3e50',
                font=('Arial', 10)
            ).pack(side='left', padx=10)
        
        # Quantity field
        tk.Label(form_frame, text="🔢 Quantity:", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        qty_entry = tk.Entry(form_frame, textvariable=qty_var, font=('Arial', 11), width=30)
        qty_entry.pack(fill='x', pady=(0, 15))
        
        # Price field
        tk.Label(form_frame, text="💰 Price:", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        price_entry = tk.Entry(form_frame, textvariable=price_var, font=('Arial', 11), width=30)
        price_entry.pack(fill='x', pady=(0, 15))
        
        # Notes field
        tk.Label(form_frame, text="📝 Notes:", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        notes_entry = tk.Entry(form_frame, textvariable=notes_var, font=('Arial', 11), width=30)
        notes_entry.pack(fill='x', pady=(0, 15))
        
        # WeeklyPay Score field
        tk.Label(form_frame, text="⭐ WeeklyPay Score:", bg='#34495e', fg='#ecf0f1', font=('Arial', 10, 'bold')).pack(anchor='w', pady=(0, 5))
        score_entry = tk.Entry(form_frame, textvariable=score_var, font=('Arial', 11), width=30)
        score_entry.pack(fill='x', pady=(0, 20))
        
        # Buttons
        button_frame = tk.Frame(form_frame, bg='#34495e')
        button_frame.pack(fill='x', pady=(10, 0))
        
        def save_changes():
            """Save the edited trade"""
            try:
                # Validate inputs
                qty = float(qty_var.get())
                price = float(price_var.get())
                total = qty * price
                action = action_var.get()
                
                # Determine dividend fields
                if action == 'DIVIDEND':
                    dividend_per_share = price
                    total_dividends = total
                else:
                    dividend_per_share = 0
                    total_dividends = 0
                
                # Load CSV
                df = pd.read_csv(self.trade_file)
                
                # Update row
                df.loc[row_number, 'Date'] = date_var.get()
                df.loc[row_number, 'Ticker'] = ticker_var.get().upper()
                df.loc[row_number, 'Action'] = action
                df.loc[row_number, 'Quantity'] = qty
                df.loc[row_number, 'Price'] = price
                df.loc[row_number, 'Total'] = total
                df.loc[row_number, 'Notes'] = notes_var.get()
                df.loc[row_number, 'WeeklyPay_Score'] = score_var.get()
                df.loc[row_number, 'Dividend_Per_Share'] = dividend_per_share
                df.loc[row_number, 'Total_Dividends'] = total_dividends
                
                # Save back
                df.to_csv(self.trade_file, index=False)
                
                # Close dialog
                edit_window.destroy()
                
                # Refresh display
                self.load_and_display_trades()
                
                self.log_status(f"✅ Updated trade #{row_number + 1}: {ticker_var.get()} {action}")
                messagebox.showinfo("Success", "Trade updated successfully!")
                
            except ValueError as e:
                messagebox.showerror("Invalid Input", f"Please check your numeric values:\n{e}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save changes:\n{e}")
                self.log_status(f"❌ Error updating trade: {e}")
        
        def cancel_edit():
            """Cancel editing"""
            edit_window.destroy()
        
        # Save button
        tk.Button(
            button_frame,
            text="💾 Save Changes",
            command=save_changes,
            bg='#27ae60',
            fg='white',
            font=('Arial', 11, 'bold'),
            relief='flat',
            cursor='hand2',
            width=15
        ).pack(side='left', padx=(0, 10))
        
        # Cancel button
        tk.Button(
            button_frame,
            text="❌ Cancel",
            command=cancel_edit,
            bg='#7f8c8d',
            fg='white',
            font=('Arial', 11),
            relief='flat',
            cursor='hand2',
            width=15
        ).pack(side='left')
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

if __name__ == "__main__":
    app = TradeDiagnosticTool()
    app.run()

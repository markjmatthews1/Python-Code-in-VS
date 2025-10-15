"""
Trade Tracker GUI Components
Provides interface for manual trade entry and status tracking
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from utils.models import TradeEntry
from utils.ui_utils import UIConfig, create_styled_button, create_styled_frame

class TradeTrackerPanel:
    """
    Trade tracker panel for managing recovery trades
    """
    def __init__(self, parent, portfolio_manager):
        self.parent = parent
        self.portfolio = portfolio_manager
        self.selected_ticker = None
        self.selected_trade_index = None
        
        # Trade form variables
        self.setup_form_variables()
        
        # Create the main panel
        self.create_trade_tracker_panel()
    
    def setup_form_variables(self):
        """Initialize form variables for trade entry"""
        self.ticker_var = tk.StringVar()
        self.trade_type_var = tk.StringVar(value="short_put")
        self.strike_var = tk.StringVar()
        self.expiry_var = tk.StringVar()
        self.premium_var = tk.StringVar()
        self.quantity_var = tk.StringVar(value="1")
        self.commission_var = tk.StringVar(value="0.65")
        self.status_var = tk.StringVar(value="open")
        self.notes_var = tk.StringVar()
    
    def create_trade_tracker_panel(self):
        """Create the complete trade tracker interface"""
        # Main container
        main_frame = tk.Frame(self.parent, bg=UIConfig.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(
            main_frame,
            text="Recovery Trade Tracker",
            font=UIConfig.TITLE_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Create two main sections: Trade Entry Form and Trade Table
        self.create_trade_entry_section(main_frame)
        self.create_trade_table_section(main_frame)
    
    def create_trade_entry_section(self, parent):
        """Create the trade entry form section"""
        # Trade Entry Frame
        entry_frame = tk.LabelFrame(
            parent,
            text="Add New Trade",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            relief=tk.RAISED,
            bd=2
        )
        entry_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Form container
        form_container = tk.Frame(entry_frame, bg=UIConfig.COLORS['bg_secondary'])
        form_container.pack(padx=20, pady=15)
        
        # Row 1: Ticker and Trade Type
        row1_frame = tk.Frame(form_container, bg=UIConfig.COLORS['bg_secondary'])
        row1_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Ticker dropdown
        tk.Label(
            row1_frame,
            text="Position:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        self.ticker_dropdown = ttk.Combobox(
            row1_frame,
            textvariable=self.ticker_var,
            values=self.get_ticker_list(),
            font=UIConfig.DEFAULT_FONT,
            state="readonly",
            width=10
        )
        self.ticker_dropdown.pack(side=tk.LEFT, padx=(0, 20))
        
        # Trade Type dropdown
        tk.Label(
            row1_frame,
            text="Trade Type:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        trade_types = [
            "short_put", "short_call", "covered_call", 
            "protective_put", "synthetic", "buy_write"
        ]
        
        self.trade_type_dropdown = ttk.Combobox(
            row1_frame,
            textvariable=self.trade_type_var,
            values=trade_types,
            font=UIConfig.DEFAULT_FONT,
            state="readonly",
            width=12
        )
        self.trade_type_dropdown.pack(side=tk.LEFT, padx=(0, 20))
        
        # Status dropdown
        tk.Label(
            row1_frame,
            text="Status:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        status_options = ["open", "assigned", "closed", "expired"]
        
        self.status_dropdown = ttk.Combobox(
            row1_frame,
            textvariable=self.status_var,
            values=status_options,
            font=UIConfig.DEFAULT_FONT,
            state="readonly",
            width=10
        )
        self.status_dropdown.pack(side=tk.LEFT)
        
        # Row 2: Strike, Expiry, Premium
        row2_frame = tk.Frame(form_container, bg=UIConfig.COLORS['bg_secondary'])
        row2_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Strike Price
        tk.Label(
            row2_frame,
            text="Strike:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        strike_entry = tk.Entry(
            row2_frame,
            textvariable=self.strike_var,
            font=UIConfig.DEFAULT_FONT,
            width=8,
            relief=tk.FLAT,
            bd=3
        )
        strike_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Expiry Date
        tk.Label(
            row2_frame,
            text="Expiry:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        expiry_entry = tk.Entry(
            row2_frame,
            textvariable=self.expiry_var,
            font=UIConfig.DEFAULT_FONT,
            width=12,
            relief=tk.FLAT,
            bd=3
        )
        expiry_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Premium
        tk.Label(
            row2_frame,
            text="Premium:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        premium_entry = tk.Entry(
            row2_frame,
            textvariable=self.premium_var,
            font=UIConfig.DEFAULT_FONT,
            width=8,
            relief=tk.FLAT,
            bd=3
        )
        premium_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Quantity
        tk.Label(
            row2_frame,
            text="Qty:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        qty_entry = tk.Entry(
            row2_frame,
            textvariable=self.quantity_var,
            font=UIConfig.DEFAULT_FONT,
            width=6,
            relief=tk.FLAT,
            bd=3
        )
        qty_entry.pack(side=tk.LEFT)
        
        # Row 3: Commission and Notes
        row3_frame = tk.Frame(form_container, bg=UIConfig.COLORS['bg_secondary'])
        row3_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Commission
        tk.Label(
            row3_frame,
            text="Commission:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        commission_entry = tk.Entry(
            row3_frame,
            textvariable=self.commission_var,
            font=UIConfig.DEFAULT_FONT,
            width=8,
            relief=tk.FLAT,
            bd=3
        )
        commission_entry.pack(side=tk.LEFT, padx=(0, 15))
        
        # Notes
        tk.Label(
            row3_frame,
            text="Notes:",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        notes_entry = tk.Entry(
            row3_frame,
            textvariable=self.notes_var,
            font=UIConfig.DEFAULT_FONT,
            width=30,
            relief=tk.FLAT,
            bd=3
        )
        notes_entry.pack(side=tk.LEFT)
        
        # Buttons Row
        button_frame = tk.Frame(form_container, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, pady=(10, 0))
        
        add_button = create_styled_button(
            button_frame, 
            "Add Trade", 
            self.add_trade, 
            'success'
        )
        add_button.pack(side=tk.LEFT, padx=(0, 10))
        
        update_button = create_styled_button(
            button_frame, 
            "Update Trade", 
            self.update_trade, 
            'primary'
        )
        update_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = create_styled_button(
            button_frame, 
            "Clear Form", 
            self.clear_form, 
            'warning'
        )
        clear_button.pack(side=tk.LEFT, padx=(0, 10))
        
        refresh_button = create_styled_button(
            button_frame, 
            "Refresh Tickers", 
            self.refresh_ticker_list, 
            'info'
        )
        refresh_button.pack(side=tk.RIGHT)
        
        # Add placeholder text hints
        self.add_placeholder_hints(form_container)
    
    def add_placeholder_hints(self, parent):
        """Add helpful placeholder text"""
        hint_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        hint_frame.pack(fill=tk.X, pady=(10, 0))
        
        hints = [
            "💡 Tips: Strike price in dollars (e.g., 42.50)",
            "📅 Expiry format: YYYY-MM-DD (e.g., 2025-11-15)",
            "💰 Premium: Positive for collected, negative for paid",
            "📝 Use notes to track strategy details"
        ]
        
        for hint in hints:
            tk.Label(
                hint_frame,
                text=hint,
                font=('Arial', 10),
                fg=UIConfig.COLORS['info'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w', pady=1)
    
    def create_trade_table_section(self, parent):
        """Create the trade table section"""
        # Trade Table Frame
        table_frame = tk.LabelFrame(
            parent,
            text="Active Trades",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            relief=tk.RAISED,
            bd=2
        )
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Table container with scrollbars
        table_container = tk.Frame(table_frame, bg=UIConfig.COLORS['bg_secondary'])
        table_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create Treeview for trade table
        columns = (
            'Ticker', 'Type', 'Strike', 'Expiry', 'Premium', 
            'Qty', 'Status', 'Net Premium', 'Entry Date', 'Notes'
        )
        
        self.trade_tree = ttk.Treeview(
            table_container,
            columns=columns,
            show='headings',
            height=12
        )
        
        # Configure column headings and widths
        column_configs = {
            'Ticker': (60, 'center'),
            'Type': (100, 'center'),
            'Strike': (70, 'center'),
            'Expiry': (90, 'center'),
            'Premium': (80, 'center'),
            'Qty': (50, 'center'),
            'Status': (80, 'center'),
            'Net Premium': (90, 'center'),
            'Entry Date': (90, 'center'),
            'Notes': (150, 'w')
        }
        
        for col, (width, anchor) in column_configs.items():
            self.trade_tree.heading(col, text=col, anchor='center')
            self.trade_tree.column(col, width=width, anchor=anchor)
        
        # Add scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL, command=self.trade_tree.yview)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL, command=self.trade_tree.xview)
        self.trade_tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack table and scrollbars
        self.trade_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind selection event
        self.trade_tree.bind('<<TreeviewSelect>>', self.on_trade_select)
        
        # Trade actions frame
        actions_frame = tk.Frame(table_frame, bg=UIConfig.COLORS['bg_secondary'])
        actions_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        edit_button = create_styled_button(
            actions_frame, 
            "Edit Selected", 
            self.edit_selected_trade, 
            'primary'
        )
        edit_button.pack(side=tk.LEFT, padx=(0, 10))
        
        delete_button = create_styled_button(
            actions_frame, 
            "Delete Selected", 
            self.delete_selected_trade, 
            'danger'
        )
        delete_button.pack(side=tk.LEFT, padx=(0, 10))
        
        status_button = create_styled_button(
            actions_frame, 
            "Change Status", 
            self.change_trade_status, 
            'warning'
        )
        status_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Summary labels
        self.create_trade_summary(actions_frame)
        
        # Load initial data
        self.refresh_trade_table()
    
    def create_trade_summary(self, parent):
        """Create trade summary labels"""
        summary_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        summary_frame.pack(side=tk.RIGHT)
        
        self.active_trades_label = tk.Label(
            summary_frame,
            text="Active Trades: 0",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.active_trades_label.pack(side=tk.RIGHT, padx=(0, 15))
        
        self.total_premium_label = tk.Label(
            summary_frame,
            text="Total Premium: $0.00",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.total_premium_label.pack(side=tk.RIGHT, padx=(0, 15))
    
    def get_ticker_list(self):
        """Get list of available tickers from portfolio"""
        return self.portfolio.get_all_tickers()
    
    def refresh_ticker_list(self):
        """Refresh the ticker dropdown list"""
        tickers = self.get_ticker_list()
        self.ticker_dropdown['values'] = tickers
        if tickers and not self.ticker_var.get():
            self.ticker_var.set(tickers[0])
    
    def add_trade(self):
        """Add a new trade to the selected position"""
        try:
            # Validate form data
            ticker = self.ticker_var.get()
            if not ticker:
                messagebox.showerror("Error", "Please select a position first")
                return
            
            # Get position
            position = self.portfolio.get_position(ticker)
            if not position:
                messagebox.showerror("Error", f"Position {ticker} not found")
                return
            
            # Validate required fields
            if not all([self.strike_var.get(), self.expiry_var.get(), self.premium_var.get()]):
                messagebox.showerror("Error", "Please fill in Strike, Expiry, and Premium")
                return
            
            # Create trade entry
            trade = TradeEntry(
                type=self.trade_type_var.get(),
                strike=float(self.strike_var.get()),
                expiry=self.expiry_var.get(),
                premium=float(self.premium_var.get()),
                status=self.status_var.get(),
                quantity=int(self.quantity_var.get() or 1),
                commission=float(self.commission_var.get() or 0),
                notes=self.notes_var.get()
            )
            
            # Add trade to position
            position.add_trade(trade)
            
            # Save portfolio immediately to sync with other tabs
            try:
                self.portfolio.save_to_file("recovery_portfolio.json")
                print(f"✅ Portfolio saved after adding trade to {ticker}")
            except Exception as save_error:
                print(f"Warning: Could not save portfolio after adding trade: {save_error}")
            
            # Refresh displays (this will refresh the current trade tracker)
            self.refresh_trade_table()
            self.clear_form()
            
            messagebox.showinfo("Success", f"Trade added to {ticker} successfully! Check Portfolio Overview and other tabs to see the update.")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding trade: {e}")
    
    def update_trade(self):
        """Update the selected trade"""
        if self.selected_ticker is None or self.selected_trade_index is None:
            messagebox.showerror("Error", "Please select a trade to update")
            return
        
        try:
            # Get position and trade
            position = self.portfolio.get_position(self.selected_ticker)
            if not position or self.selected_trade_index >= len(position.trades):
                messagebox.showerror("Error", "Selected trade not found")
                return
            
            # Update trade data
            trade = position.trades[self.selected_trade_index]
            trade.type = self.trade_type_var.get()
            trade.strike = float(self.strike_var.get())
            trade.expiry = self.expiry_var.get()
            trade.premium = float(self.premium_var.get())
            trade.status = self.status_var.get()
            trade.quantity = int(self.quantity_var.get() or 1)
            trade.commission = float(self.commission_var.get() or 0)
            trade.notes = self.notes_var.get()
            
            # Save portfolio to sync changes
            try:
                self.portfolio.save_to_file("recovery_portfolio.json")
                print(f"✅ Portfolio saved after updating trade")
            except Exception as save_error:
                print(f"Warning: Could not save portfolio after updating trade: {save_error}")
            
            # Refresh displays
            self.refresh_trade_table()
            self.clear_form()
            
            messagebox.showinfo("Success", "Trade updated successfully!")
            
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating trade: {e}")
    
    def clear_form(self):
        """Clear the trade entry form"""
        self.strike_var.set("")
        self.expiry_var.set("")
        self.premium_var.set("")
        self.quantity_var.set("1")
        self.commission_var.set("0.65")
        self.status_var.set("open")
        self.notes_var.set("")
        self.selected_ticker = None
        self.selected_trade_index = None
    
    def refresh_trade_table(self):
        """Refresh the trade table with current data"""
        # Clear existing items
        for item in self.trade_tree.get_children():
            self.trade_tree.delete(item)
        
        # Add trades from all positions
        total_premium = 0
        active_count = 0
        
        for position in self.portfolio:
            for trade in position.trades:
                # Calculate display values
                net_premium = trade.net_premium()
                total_premium += net_premium
                
                if trade.is_active():
                    active_count += 1
                
                # Status color coding
                status_color = self.get_status_color(trade.status)
                
                # Insert trade into table
                item = self.trade_tree.insert('', 'end', values=(
                    position.ticker,
                    trade.type.replace('_', ' ').title(),
                    f"${trade.strike:.2f}",
                    trade.expiry,
                    f"${trade.premium:.2f}",
                    trade.quantity,
                    trade.status.title(),
                    f"${net_premium:.2f}",
                    trade.entry_date,
                    trade.notes
                ))
                
                # Apply status-based coloring
                self.trade_tree.set(item, 'Status', trade.status.title())
        
        # Update summary
        self.active_trades_label.config(text=f"Active Trades: {active_count}")
        self.total_premium_label.config(text=f"Total Premium: ${total_premium:.2f}")
        
        # Update ticker dropdown
        self.refresh_ticker_list()
    
    def get_status_color(self, status):
        """Get color for trade status"""
        colors = {
            'open': UIConfig.COLORS['warning'],
            'assigned': UIConfig.COLORS['info'],
            'closed': UIConfig.COLORS['success'],
            'expired': UIConfig.COLORS['danger']
        }
        return colors.get(status, UIConfig.COLORS['text_light'])
    
    def on_trade_select(self, event):
        """Handle trade selection in table"""
        selection = self.trade_tree.selection()
        if not selection:
            return
        
        # Get selected trade data
        item = selection[0]
        values = self.trade_tree.item(item, 'values')
        
        if len(values) >= 10:
            ticker = values[0]
            position = self.portfolio.get_position(ticker)
            
            if position:
                # Find the trade by matching data
                for i, trade in enumerate(position.trades):
                    if (trade.strike == float(values[2].replace('$', '')) and
                        trade.expiry == values[3] and
                        trade.premium == float(values[4].replace('$', ''))):
                        
                        self.selected_ticker = ticker
                        self.selected_trade_index = i
                        break
    
    def edit_selected_trade(self):
        """Load selected trade into form for editing"""
        if self.selected_ticker is None or self.selected_trade_index is None:
            messagebox.showerror("Error", "Please select a trade to edit")
            return
        
        # Get trade data
        position = self.portfolio.get_position(self.selected_ticker)
        if not position or self.selected_trade_index >= len(position.trades):
            messagebox.showerror("Error", "Selected trade not found")
            return
        
        trade = position.trades[self.selected_trade_index]
        
        # Load into form
        self.ticker_var.set(self.selected_ticker)
        self.trade_type_var.set(trade.type)
        self.strike_var.set(str(trade.strike))
        self.expiry_var.set(trade.expiry)
        self.premium_var.set(str(trade.premium))
        self.quantity_var.set(str(trade.quantity))
        self.commission_var.set(str(trade.commission))
        self.status_var.set(trade.status)
        self.notes_var.set(trade.notes)
    
    def delete_selected_trade(self):
        """Delete the selected trade"""
        if self.selected_ticker is None or self.selected_trade_index is None:
            messagebox.showerror("Error", "Please select a trade to delete")
            return
        
        # Confirm deletion
        position = self.portfolio.get_position(self.selected_ticker)
        if not position or self.selected_trade_index >= len(position.trades):
            messagebox.showerror("Error", "Selected trade not found")
            return
        
        trade = position.trades[self.selected_trade_index]
        
        if messagebox.askyesno("Confirm Delete", 
                              f"Delete {trade.type} trade for {self.selected_ticker}?\n"
                              f"Strike: ${trade.strike}, Expiry: {trade.expiry}"):
            
            position.remove_trade(self.selected_trade_index)
            
            # Save portfolio to sync changes
            try:
                self.portfolio.save_to_file("recovery_portfolio.json")
                print(f"✅ Portfolio saved after deleting trade")
            except Exception as save_error:
                print(f"Warning: Could not save portfolio after deleting trade: {save_error}")
            
            self.refresh_trade_table()
            self.clear_form()
            messagebox.showinfo("Success", "Trade deleted successfully!")
    
    def change_trade_status(self):
        """Change status of selected trade"""
        if self.selected_ticker is None or self.selected_trade_index is None:
            messagebox.showerror("Error", "Please select a trade first")
            return
        
        # Create status selection dialog
        self.show_status_dialog()
    
    def show_status_dialog(self):
        """Show dialog for changing trade status"""
        position = self.portfolio.get_position(self.selected_ticker)
        if not position or self.selected_trade_index >= len(position.trades):
            return
        
        trade = position.trades[self.selected_trade_index]
        
        # Create dialog window
        dialog = tk.Toplevel(self.parent)
        dialog.title("Change Trade Status")
        dialog.geometry("300x200")
        dialog.configure(bg=UIConfig.COLORS['bg_primary'])
        dialog.resizable(False, False)
        
        # Center the dialog
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Dialog content
        tk.Label(
            dialog,
            text=f"Change status for {trade.type}",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(pady=20)
        
        tk.Label(
            dialog,
            text=f"Strike: ${trade.strike}, Expiry: {trade.expiry}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(pady=(0, 20))
        
        # Status selection
        status_var = tk.StringVar(value=trade.status)
        
        status_frame = tk.Frame(dialog, bg=UIConfig.COLORS['bg_primary'])
        status_frame.pack(pady=10)
        
        for status in ["open", "assigned", "closed", "expired"]:
            tk.Radiobutton(
                status_frame,
                text=status.title(),
                variable=status_var,
                value=status,
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_primary'],
                selectcolor=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
        
        # Buttons
        button_frame = tk.Frame(dialog, bg=UIConfig.COLORS['bg_primary'])
        button_frame.pack(pady=20)
        
        def update_status():
            trade.status = status_var.get()
            self.refresh_trade_table()
            dialog.destroy()
            messagebox.showinfo("Success", "Trade status updated!")
        
        create_styled_button(button_frame, "Update", update_status, 'success').pack(side=tk.LEFT, padx=5)
        create_styled_button(button_frame, "Cancel", dialog.destroy, 'danger').pack(side=tk.LEFT, padx=5)
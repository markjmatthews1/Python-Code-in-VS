"""
RecoveryApp Main GUI Shell
Tabbed interface for managing underwater positions and recovery strategies
"""
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import sys
import os

# Add current directory to path for importing models
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.models import TickerPosition, TradeEntry, PortfolioManager
from utils.ui_utils import UIConfig, create_styled_button, create_styled_frame, create_styled_label
from gui.trade_tracker import TradeTrackerPanel
from gui.strategy_cards_panel import StrategyCardsPanel
from gui.alerts_panel import AlertsPanel
from gui.automation_panel import AutomationPanel

class RecoveryAppGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("RecoveryApp™ - Underwater Position Recovery Tool")
        self.root.geometry("1200x800")
        self.root.configure(bg=UIConfig.COLORS['bg_primary'])
        
        # Initialize portfolio manager
        self.portfolio = PortfolioManager()
        self.load_portfolio()
        
        # Configure default font and style
        self.setup_styles()
        
        # Create main interface
        self.setup_main_interface()
        
        # Bind close event to save portfolio
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_styles(self):
        """Configure ttk styles for consistent appearance"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure notebook (tab) style
        self.style.configure('Custom.TNotebook', 
                           background=UIConfig.COLORS['bg_primary'],
                           borderwidth=0)
        
        self.style.configure('Custom.TNotebook.Tab',
                           background=UIConfig.COLORS['bg_secondary'],
                           foreground=UIConfig.COLORS['text_light'],
                           padding=[20, 10],
                           font=UIConfig.DEFAULT_FONT)
        
        self.style.map('Custom.TNotebook.Tab',
                      background=[('selected', UIConfig.COLORS['accent']),
                                ('active', UIConfig.COLORS['highlight'])])
        
        # Configure frame style
        self.style.configure('Custom.TFrame',
                           background=UIConfig.COLORS['bg_primary'])
    
    def setup_main_interface(self):
        """Create the main tabbed interface"""
        # Main container
        main_container = tk.Frame(self.root, bg=UIConfig.COLORS['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Title header
        title_frame = tk.Frame(main_container, bg=UIConfig.COLORS['bg_primary'])
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        title_label = tk.Label(
            title_frame,
            text="RecoveryApp™",
            font=('Arial', 28, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        subtitle_label = tk.Label(
            title_frame,
            text="Underwater Position Recovery Tool",
            font=('Arial', 14),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        subtitle_label.pack(side=tk.LEFT, padx=(20, 0), pady=(10, 0))
        
        # Portfolio summary in header
        self.create_portfolio_summary(title_frame)
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(main_container, style='Custom.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Create main tabs
        self.create_portfolio_overview_tab()
        self.create_add_position_tab()
        self.create_trade_tracker_tab()
        self.create_alerts_tab()
        self.create_automation_tab()
        
        # Create individual ticker tabs
        self.refresh_ticker_tabs()
    
    def create_portfolio_summary(self, parent):
        """Create portfolio summary display in header"""
        summary_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=2)
        summary_frame.pack(side=tk.RIGHT, padx=(20, 0))
        
        self.portfolio_summary_frame = summary_frame
        self.update_portfolio_summary()
    
    def update_portfolio_summary(self):
        """Update portfolio summary display"""
        # Clear existing widgets
        for widget in self.portfolio_summary_frame.winfo_children():
            widget.destroy()
        
        # Calculate portfolio metrics
        total_investment = self.portfolio.total_investment()
        total_premium = self.portfolio.total_premium_collected()
        position_count = len(self.portfolio)
        
        # Create summary labels
        tk.Label(
            self.portfolio_summary_frame,
            text="Portfolio Summary",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(padx=10, pady=(5, 0))
        
        tk.Label(
            self.portfolio_summary_frame,
            text=f"Positions: {position_count}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(padx=10)
        
        tk.Label(
            self.portfolio_summary_frame,
            text=f"Investment: ${total_investment:,.2f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(padx=10)
        
        tk.Label(
            self.portfolio_summary_frame,
            text=f"Premium: ${total_premium:,.2f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(padx=10, pady=(0, 5))
    
    def create_portfolio_overview_tab(self):
        """Create the portfolio overview tab"""
        overview_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(overview_frame, text="📊 Portfolio Overview")
        
        # Main content frame
        content_frame = tk.Frame(overview_frame, bg=UIConfig.COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(
            content_frame,
            text="Portfolio Positions",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        header_label.pack(pady=(0, 20))
        
        # Positions list frame
        self.positions_frame = tk.Frame(content_frame, bg=UIConfig.COLORS['bg_primary'])
        self.positions_frame.pack(fill=tk.BOTH, expand=True)
        
        self.refresh_positions_display()
    
    def refresh_positions_display(self):
        """Refresh the positions display in overview tab"""
        # Clear existing widgets
        for widget in self.positions_frame.winfo_children():
            widget.destroy()
        
        if len(self.portfolio) == 0:
            no_positions_label = tk.Label(
                self.positions_frame,
                text="No positions added yet. Use the 'Add Position' tab to get started.",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_primary']
            )
            no_positions_label.pack(expand=True)
            return
        
        # Create scrollable frame for positions
        canvas = tk.Canvas(self.positions_frame, bg=UIConfig.COLORS['bg_primary'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.positions_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=UIConfig.COLORS['bg_primary'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Position cards
        for i, position in enumerate(self.portfolio):
            self.create_position_card(scrollable_frame, position, i)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
    
    def create_position_card(self, parent, position, index):
        """Create a card display for a position"""
        card_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Header row
        header_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        ticker_label = tk.Label(
            header_frame,
            text=position.ticker,
            font=('Arial', 16, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        ticker_label.pack(side=tk.LEFT)
        
        # Action buttons
        button_frame = tk.Frame(header_frame, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(side=tk.RIGHT)
        
        edit_btn = create_styled_button(button_frame, "Edit", lambda p=position: self.edit_position(p), 'primary')
        edit_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        delete_btn = create_styled_button(button_frame, "Delete", lambda p=position: self.delete_position(p), 'danger')
        delete_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Details grid
        details_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Position details
        details = [
            ("Shares:", f"{position.qty:,}"),
            ("Cost Basis:", f"${position.cost_basis:.2f}"),
            ("Investment:", f"${position.total_investment():,.2f}"),
            ("Purchase Date:", position.purchase_date),
            ("Active Trades:", f"{len(position.get_active_trades())}"),
            ("Premium Collected:", f"${position.total_premium_collected():.2f}"),
            ("Effective Basis:", f"${position.effective_cost_basis():.2f}")
        ]
        
        for i, (label, value) in enumerate(details):
            row = i // 3
            col = (i % 3) * 2
            
            tk.Label(
                details_frame,
                text=label,
                font=('Arial', 11, 'bold'),
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).grid(row=row, column=col, sticky='w', padx=(0, 10), pady=2)
            
            tk.Label(
                details_frame,
                text=value,
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).grid(row=row, column=col+1, sticky='w', padx=(0, 20), pady=2)
    
    def create_add_position_tab(self):
        """Create the add position tab with input fields"""
        add_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(add_frame, text="➕ Add Position")
        
        # Main content frame
        content_frame = tk.Frame(add_frame, bg=UIConfig.COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=50)
        
        # Title
        title_label = tk.Label(
            content_frame,
            text="Add New Underwater Position",
            font=UIConfig.TITLE_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(pady=(0, 30))
        
        # Input form frame
        form_frame = tk.Frame(content_frame, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=2)
        form_frame.pack(fill=tk.X, padx=100, pady=20)
        
        # Form fields
        self.create_position_form(form_frame)
    
    def create_position_form(self, parent):
        """Create the position input form"""
        form_inner = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        form_inner.pack(padx=40, pady=30)
        
        # Input variables
        self.ticker_var = tk.StringVar()
        self.cost_basis_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        self.purchase_date_var = tk.StringVar(value=datetime.now().strftime('%Y-%m-%d'))
        self.target_price_var = tk.StringVar()
        self.notes_var = tk.StringVar()
        
        # Form fields
        fields = [
            ("Ticker Symbol *", self.ticker_var, "e.g., SOXL, NVDA, AMD"),
            ("Cost Basis *", self.cost_basis_var, "e.g., 42.50"),
            ("Quantity *", self.qty_var, "e.g., 100"),
            ("Purchase Date *", self.purchase_date_var, "YYYY-MM-DD"),
            ("Target Recovery Price", self.target_price_var, "Optional - defaults to cost basis"),
            ("Notes", self.notes_var, "Optional notes about this position")
        ]
        
        self.entries = {}
        
        for i, (label_text, var, placeholder) in enumerate(fields):
            # Label
            label = tk.Label(
                form_inner,
                text=label_text,
                font=('Arial', 12, 'bold'),
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary'],
                anchor='w'
            )
            label.grid(row=i, column=0, sticky='w', pady=(10, 5), padx=(0, 20))
            
            # Entry
            entry = tk.Entry(
                form_inner,
                textvariable=var,
                font=UIConfig.DEFAULT_FONT,
                width=30,
                relief=tk.FLAT,
                bd=5
            )
            entry.grid(row=i, column=1, sticky='w', pady=(10, 5))
            
            # Placeholder text
            placeholder_label = tk.Label(
                form_inner,
                text=placeholder,
                font=('Arial', 10),
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            )
            placeholder_label.grid(row=i, column=2, sticky='w', padx=(10, 0), pady=(10, 5))
            
            self.entries[label_text.replace(' *', '').replace(' ', '_').lower()] = entry
        
        # Buttons frame
        button_frame = tk.Frame(form_inner, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.grid(row=len(fields), column=0, columnspan=3, pady=(30, 0))
        
        add_button = create_styled_button(button_frame, "Add Position", self.add_position, 'success')
        add_button.pack(side=tk.LEFT, padx=(0, 10))
        
        clear_button = create_styled_button(button_frame, "Clear Form", self.clear_form, 'warning')
        clear_button.pack(side=tk.LEFT)
    
    def create_trade_tracker_tab(self):
        """Create the trade tracker tab"""
        trade_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(trade_frame, text="📈 Trade Tracker")
        
        # Create the trade tracker panel
        self.trade_tracker = TradeTrackerPanel(trade_frame, self.portfolio)
    
    def create_alerts_tab(self):
        """Create the alerts monitoring tab"""
        alerts_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(alerts_frame, text="🚨 Strategy Alerts")
        
        # Create the alerts panel
        self.alerts_panel = AlertsPanel(alerts_frame, self.portfolio)
    
    def create_automation_tab(self):
        """Create the automation engine tab"""
        automation_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(automation_frame, text="🤖 Automation")
        
        # Create the automation panel
        self.automation_panel = AutomationPanel(automation_frame, self.portfolio)
    
    def refresh_ticker_tabs(self):
        """Refresh individual ticker tabs"""
        # Remove existing ticker tabs (keep first 5 tabs: Overview, Add Position, Trade Tracker, Alerts, Automation)
        while len(self.notebook.tabs()) > 5:
            self.notebook.forget(5)
        
        # Add tab for each ticker
        for position in self.portfolio:
            self.create_ticker_tab(position)
    
    def create_ticker_tab(self, position):
        """Create a tab for individual ticker"""
        ticker_frame = ttk.Frame(self.notebook, style='Custom.TFrame')
        self.notebook.add(ticker_frame, text=f"📊 {position.ticker}")
        
        # Content
        content_frame = tk.Frame(ticker_frame, bg=UIConfig.COLORS['bg_primary'])
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        title_label = tk.Label(
            content_frame,
            text=f"{position.ticker} Recovery Dashboard",
            font=UIConfig.TITLE_FONT,
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(pady=(0, 20))
        
        # Create horizontal paned window
        paned = tk.PanedWindow(content_frame, orient=tk.HORIZONTAL, bg=UIConfig.COLORS['bg_primary'])
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - Position details and strategies
        left_panel = tk.Frame(paned, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
        left_panel_inner = tk.Frame(left_panel, bg=UIConfig.COLORS['bg_secondary'])
        left_panel_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Position Summary
        summary_label = tk.Label(
            left_panel_inner, 
            text="Position Summary",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        summary_label.pack(pady=(0, 10))
        
        # Position details
        # Mock current price for demo (in real app, this would come from API)
        current_price = position.cost_basis * 0.85  # Simulate 15% loss
        market_value = current_price * position.qty
        unrealized_pnl = market_value - position.total_investment()
        unrealized_pnl_percent = (unrealized_pnl / position.total_investment()) * 100
        
        details_text = f"""Ticker: {position.ticker}
Shares: {position.qty:,}
Cost Basis: ${position.cost_basis:.2f}
Current Price: ${current_price:.2f}
Market Value: ${market_value:,.2f}
Unrealized P&L: ${unrealized_pnl:,.2f} ({unrealized_pnl_percent:.1f}%)"""
        
        details_label = tk.Label(
            left_panel_inner,
            text=details_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'] if unrealized_pnl >= 0 else UIConfig.COLORS['danger'],
            bg=UIConfig.COLORS['bg_secondary'],
            justify=tk.LEFT
        )
        details_label.pack(pady=(0, 20))
        
        # Strategy Panel
        strategy_label = tk.Label(
            left_panel_inner,
            text="Recovery Strategies",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        strategy_label.pack(pady=(0, 10))
        
        # Add strategy cards panel
        strategy_panel = StrategyCardsPanel(left_panel_inner, position)
        
        # Right panel - Trade tracker
        right_panel = tk.Frame(paned, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
        right_panel_inner = tk.Frame(right_panel, bg=UIConfig.COLORS['bg_secondary'])
        right_panel_inner.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Trade Tracker
        tracker_label = tk.Label(
            right_panel_inner,
            text="Trade Tracker",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        tracker_label.pack(pady=(0, 10))
        
        # Add trade tracker panel
        # Create trade tracker for this specific ticker
        trade_tracker = TradeTrackerPanel(right_panel_inner, self.portfolio)
        # Set the selected ticker to focus on this position
        trade_tracker.selected_ticker = position.ticker
        trade_tracker.ticker_var.set(position.ticker)
        
        paned.add(left_panel, minsize=350)
        paned.add(right_panel, minsize=550)
    
    def add_position(self):
        """Add a new position from form data"""
        try:
            # Validate required fields
            ticker = self.ticker_var.get().strip().upper()
            cost_basis = float(self.cost_basis_var.get())
            qty = int(self.qty_var.get())
            purchase_date = self.purchase_date_var.get().strip()
            
            if not ticker or not cost_basis or not qty or not purchase_date:
                messagebox.showerror("Error", "Please fill in all required fields (marked with *)")
                return
            
            # Optional fields
            target_price = None
            if self.target_price_var.get().strip():
                target_price = float(self.target_price_var.get())
            
            notes = self.notes_var.get().strip()
            
            # Create position
            position = TickerPosition(
                ticker=ticker,
                cost_basis=cost_basis,
                qty=qty,
                purchase_date=purchase_date,
                target_recovery_price=target_price,
                notes=notes
            )
            
            # Add to portfolio
            self.portfolio.add_position(position)
            
            # Refresh displays
            self.refresh_positions_display()
            self.refresh_ticker_tabs()
            self.update_portfolio_summary()
            if hasattr(self, 'trade_tracker'):
                self.trade_tracker.refresh_trade_table()
            
            # Clear form
            self.clear_form()
            
            # Save portfolio
            self.save_portfolio()
            
            messagebox.showinfo("Success", f"Position {ticker} added successfully!")
            
        except ValueError as e:
            if "already exists" in str(e):
                messagebox.showerror("Error", f"Position for {ticker} already exists!")
            else:
                messagebox.showerror("Error", f"Invalid input: {e}")
        except Exception as e:
            messagebox.showerror("Error", f"Error adding position: {e}")
    
    def clear_form(self):
        """Clear the add position form"""
        self.ticker_var.set("")
        self.cost_basis_var.set("")
        self.qty_var.set("")
        self.purchase_date_var.set(datetime.now().strftime('%Y-%m-%d'))
        self.target_price_var.set("")
        self.notes_var.set("")
    
    def edit_position(self, position):
        """Edit an existing position"""
        messagebox.showinfo("Coming Soon", f"Edit functionality for {position.ticker} coming in Phase 2!")
    
    def delete_position(self, position):
        """Delete a position"""
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the {position.ticker} position?"):
            self.portfolio.remove_position(position.ticker)
            self.refresh_positions_display()
            self.refresh_ticker_tabs()
            self.update_portfolio_summary()
            if hasattr(self, 'trade_tracker'):
                self.trade_tracker.refresh_trade_table()
            self.save_portfolio()
            messagebox.showinfo("Success", f"Position {position.ticker} deleted successfully!")
    
    def save_portfolio(self):
        """Save portfolio to file"""
        try:
            self.portfolio.save_to_file("recovery_portfolio.json")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving portfolio: {e}")
    
    def load_portfolio(self):
        """Load portfolio from file"""
        try:
            self.portfolio.load_from_file("recovery_portfolio.json")
        except Exception as e:
            print(f"Could not load portfolio: {e}")
    
    def on_closing(self):
        """Handle application closing"""
        # Cleanup alerts panel if it exists
        if hasattr(self, 'alerts_panel'):
            self.alerts_panel.cleanup()
        
        # Cleanup automation panel if it exists
        if hasattr(self, 'automation_panel'):
            self.automation_panel.cleanup()
        
        self.save_portfolio()
        self.root.destroy()

def main():
    """Main entry point for RecoveryApp GUI"""
    root = tk.Tk()
    app = RecoveryAppGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
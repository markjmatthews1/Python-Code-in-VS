"""
Strategy Display Panel for RecoveryApp
Shows recovery strategy suggestions for individual positions
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from utils.ui_utils import UIConfig, create_styled_button
from utils.strategy_engine import evaluate_put_overlay, evaluate_call_overlay

class StrategyPanel:
    """
    Panel to display recovery strategy suggestions
    """
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position
        self.strategies = []
        self.is_loading = False
        
        self.create_strategy_panel()
        self.load_strategies()
    
    def create_strategy_panel(self):
        """Create the strategy suggestion panel"""
        # Main strategy frame
        strategy_frame = tk.LabelFrame(
            self.parent,
            text=f"Recovery Strategies for {self.position.ticker}",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            relief=tk.RAISED,
            bd=2
        )
        strategy_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Position summary
        self.create_position_summary(strategy_frame)
        
        # Strategy suggestions area
        self.create_strategy_suggestions(strategy_frame)
        
        # Action buttons
        self.create_action_buttons(strategy_frame)
    
    def create_position_summary(self, parent):
        """Create position summary section"""
        summary_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        summary_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        # Position details
        details_text = (
            f"Position: {self.position.qty:,} shares @ ${self.position.cost_basis:.2f} "
            f"(Total: ${self.position.total_investment():,.2f})"
        )
        
        if self.position.trades:
            premium_collected = self.position.total_premium_collected()
            effective_basis = self.position.effective_cost_basis()
            details_text += f" | Premium Collected: ${premium_collected:.2f} | Effective Basis: ${effective_basis:.2f}"
        
        tk.Label(
            summary_frame,
            text=details_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=800
        ).pack(anchor='w')
    
    def create_strategy_suggestions(self, parent):
        """Create strategy suggestions display"""
        suggestions_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        suggestions_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Title
        title_label = tk.Label(
            suggestions_frame,
            text="💡 Recommended Put Overlay Strategies",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        title_label.pack(pady=(5, 10))
        
        # Strategies container
        self.strategies_container = tk.Frame(suggestions_frame, bg=UIConfig.COLORS['bg_secondary'])
        self.strategies_container.pack(fill=tk.BOTH, expand=True)
        
        # Loading message
        self.loading_label = tk.Label(
            self.strategies_container,
            text="🔄 Analyzing option chains and calculating strategies...",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.loading_label.pack(expand=True)
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        refresh_button = create_styled_button(
            button_frame,
            "🔄 Refresh Strategies",
            self.refresh_strategies,
            'primary'
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.status_label = tk.Label(
            button_frame,
            text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def load_strategies(self):
        """Load strategies in background thread"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.loading_label.config(text="🔄 Analyzing option chains...")
        
        # Run strategy evaluation in background
        thread = threading.Thread(target=self._fetch_strategies)
        thread.daemon = True
        thread.start()
    
    def _fetch_strategies(self):
        """Fetch strategies in background thread"""
        try:
            strategies = evaluate_put_overlay(
                self.position.ticker,
                self.position.cost_basis,
                self.position.qty
            )
            
            # Update UI in main thread
            self.parent.after(0, lambda: self._update_strategies_display(strategies))
            
        except Exception as e:
            error_msg = f"Error loading strategies: {e}"
            self.parent.after(0, lambda: self._show_error(error_msg))
        finally:
            self.is_loading = False
    
    def _update_strategies_display(self, strategies):
        """Update the strategies display with results"""
        # Clear loading message
        self.loading_label.destroy()
        
        self.strategies = strategies
        
        if not strategies:
            no_strategies_label = tk.Label(
                self.strategies_container,
                text="No viable put overlay strategies found at current market conditions.",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['warning'],
                bg=UIConfig.COLORS['bg_secondary']
            )
            no_strategies_label.pack(expand=True)
            return
        
        # Create strategy cards
        for i, strategy in enumerate(strategies[:3], 1):
            self.create_strategy_card(self.strategies_container, strategy, i)
        
        # Update status
        self.status_label.config(text=f"Last updated: {datetime.now().strftime('%H:%M:%S')}")
    
    def create_strategy_card(self, parent, strategy, rank):
        """Create a card for displaying strategy details"""
        # Card frame
        card_frame = tk.Frame(
            parent,
            bg=UIConfig.COLORS['bg_primary'],
            relief=tk.RAISED,
            bd=2
        )
        card_frame.pack(fill=tk.X, pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, padx=15, pady=(10, 5))
        
        # Rank and score
        rank_label = tk.Label(
            header_frame,
            text=f"#{rank}",
            font=('Arial', 16, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        rank_label.pack(side=tk.LEFT)
        
        score_label = tk.Label(
            header_frame,
            text=f"Score: {strategy['combined_score']:.1f}",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_primary']
        )
        score_label.pack(side=tk.RIGHT)
        
        # Strategy details
        details_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_primary'])
        details_frame.pack(fill=tk.X, padx=15, pady=5)
        
        # Main strategy info
        strategy_text = (
            f"Sell ${strategy['strike']:.2f} Put • Expires {strategy['expiry']} "
            f"({strategy['days_to_expiry']} days)"
        )
        
        tk.Label(
            details_frame,
            text=strategy_text,
            font=('Arial', 13, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        # Premium info
        premium_text = f"💰 Premium: ${strategy['bid']:.2f} per share (${strategy['premium_income']:.0f} total)"
        
        tk.Label(
            details_frame,
            text=premium_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w', pady=(2, 0))
        
        # Risk and probability
        risk_color = {
            'LOW': UIConfig.COLORS['success'],
            'MEDIUM': UIConfig.COLORS['warning'],
            'HIGH': UIConfig.COLORS['danger']
        }.get(strategy['risk_level'], UIConfig.COLORS['text_light'])
        
        risk_text = (
            f"⚠️ Risk: {strategy['risk_level']} • "
            f"Assignment Probability: {strategy['prob_assignment']:.1%}"
        )
        
        tk.Label(
            details_frame,
            text=risk_text,
            font=UIConfig.DEFAULT_FONT,
            fg=risk_color,
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w', pady=(2, 0))
        
        # Scenarios
        scenarios_frame = tk.Frame(details_frame, bg=UIConfig.COLORS['bg_primary'])
        scenarios_frame.pack(fill=tk.X, pady=(5, 0))
        
        # If assigned scenario
        assigned = strategy['scenario_assigned']
        assigned_text = f"📈 If Assigned: {assigned['analysis']}"
        
        tk.Label(
            scenarios_frame,
            text=assigned_text,
            font=('Arial', 10),
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_primary'],
            wraplength=500
        ).pack(anchor='w')
        
        # If expires scenario
        expires = strategy['scenario_expires']
        expires_text = f"⏰ If Expires: {expires['analysis']}"
        
        tk.Label(
            scenarios_frame,
            text=expires_text,
            font=('Arial', 10),
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_primary'],
            wraplength=500
        ).pack(anchor='w')
        
        # Action button
        action_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_primary'])
        action_frame.pack(fill=tk.X, padx=15, pady=(5, 10))
        
        execute_button = create_styled_button(
            action_frame,
            f"Execute ${strategy['strike']:.2f} Put",
            lambda s=strategy: self.execute_strategy(s),
            'success'
        )
        execute_button.pack(side=tk.RIGHT)
    
    def execute_strategy(self, strategy):
        """Execute the selected strategy"""
        # This would integrate with the trade tracker
        strategy_text = (
            f"Execute strategy for {self.position.ticker}:\n\n"
            f"Sell ${strategy['strike']:.2f} Put\n"
            f"Expiration: {strategy['expiry']}\n"
            f"Premium: ${strategy['bid']:.2f}\n"
            f"Total Income: ${strategy['premium_income']:.0f}\n\n"
            f"This will add the trade to your Trade Tracker."
        )
        
        if messagebox.askyesno("Execute Strategy", strategy_text):
            # Create trade entry (this would be integrated with the trade tracker)
            messagebox.showinfo("Strategy Executed", 
                              f"${strategy['strike']:.2f} put strategy added to trade tracker!")
    
    def refresh_strategies(self):
        """Refresh strategy suggestions"""
        if self.is_loading:
            return
        
        # Clear existing strategies
        for widget in self.strategies_container.winfo_children():
            widget.destroy()
        
        # Show loading message
        self.loading_label = tk.Label(
            self.strategies_container,
            text="🔄 Refreshing strategies...",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.loading_label.pack(expand=True)
        
        # Reload strategies
        self.load_strategies()
    
    def _show_error(self, error_msg):
        """Show error message"""
        self.loading_label.destroy()
        
        error_label = tk.Label(
            self.strategies_container,
            text=f"❌ {error_msg}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['danger'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        error_label.pack(expand=True)
"""
Enhanced Strategy Cards Display for RecoveryApp
Color-coded strategy suggestions with comprehensive trade details
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime, timedelta
from utils.ui_utils import UIConfig, create_styled_button
from utils.strategy_engine import (
    evaluate_put_overlay, 
    evaluate_call_overlay, 
    build_synthetic_recovery,
    estimate_recovery_time
)

class StrategyCardsPanel:
    """
    Enhanced panel displaying color-coded strategy cards per ticker
    """
    def __init__(self, parent, position):
        self.parent = parent
        self.position = position
        self.all_strategies = {
            'put_overlays': [],
            'call_overlays': [], 
            'synthetic_recovery': None,
            'recovery_time': None
        }
        self.is_loading = False
        
        self.create_strategy_cards_panel()
        self.load_all_strategies()
    
    def create_strategy_cards_panel(self):
        """Create the enhanced strategy cards panel"""
        # Main container
        main_frame = tk.Frame(self.parent, bg=UIConfig.COLORS['bg_primary'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header with position info
        self.create_enhanced_header(main_frame)
        
        # Strategy cards container with scrolling
        self.create_cards_container(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
    
    def create_enhanced_header(self, parent):
        """Create enhanced header with position details and recovery metrics"""
        header_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=2)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Title section
        title_section = tk.Frame(header_frame, bg=UIConfig.COLORS['bg_secondary'])
        title_section.pack(fill=tk.X, padx=15, pady=10)
        
        # Main title
        title_label = tk.Label(
            title_section,
            text=f"🎯 Recovery Strategies for {self.position.ticker}",
            font=('Arial', 18, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        title_label.pack(anchor='w')
        
        # Position metrics
        metrics_frame = tk.Frame(header_frame, bg=UIConfig.COLORS['bg_secondary'])
        metrics_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Calculate position metrics
        total_investment = self.position.total_investment()
        premium_collected = self.position.total_premium_collected() if self.position.trades else 0
        effective_basis = self.position.effective_cost_basis() if self.position.trades else self.position.cost_basis
        
        # Current market metrics (mock for now - will be updated when strategies load)
        current_price = self.position.cost_basis * 0.85  # Mock 15% loss
        current_value = current_price * self.position.qty
        unrealized_pnl = current_value - total_investment + premium_collected
        pnl_percent = (unrealized_pnl / total_investment) * 100
        
        # Position details
        pos_details = (
            f"📊 Position: {self.position.qty:,} shares @ ${self.position.cost_basis:.2f} | "
            f"Current: ${current_price:.2f} | "
            f"Total Investment: ${total_investment:,.0f}"
        )
        
        tk.Label(
            metrics_frame,
            text=pos_details,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # P&L and recovery metrics
        pnl_color = UIConfig.COLORS['danger'] if unrealized_pnl < 0 else UIConfig.COLORS['success']
        pnl_details = (
            f"💰 Current Value: ${current_value:,.0f} | "
            f"Unrealized P&L: ${unrealized_pnl:,.0f} ({pnl_percent:+.1f}%) | "
            f"Recovery Needed: {((self.position.cost_basis - current_price) / current_price) * 100:.1f}%"
        )
        
        tk.Label(
            metrics_frame,
            text=pnl_details,
            font=UIConfig.DEFAULT_FONT,
            fg=pnl_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Premium summary if trades exist
        if premium_collected > 0:
            premium_details = (
                f"🎁 Premium Collected: ${premium_collected:.2f} | "
                f"Effective Cost Basis: ${effective_basis:.2f} | "
                f"Total Trades: {len(self.position.trades)}"
            )
            
            tk.Label(
                metrics_frame,
                text=premium_details,
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['success'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
    
    def create_cards_container(self, parent):
        """Create scrollable container for strategy cards"""
        # Container frame with scrollbar
        container_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        container_frame.pack(fill=tk.BOTH, expand=True)
        
        # Canvas and scrollbar for scrolling
        self.canvas = tk.Canvas(
            container_frame,
            bg=UIConfig.COLORS['bg_primary'],
            highlightthickness=0
        )
        
        scrollbar = ttk.Scrollbar(
            container_frame,
            orient="vertical",
            command=self.canvas.yview
        )
        
        self.scrollable_frame = tk.Frame(self.canvas, bg=UIConfig.COLORS['bg_primary'])
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Bind mousewheel to canvas
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        
        # Loading message
        self.loading_frame = tk.Frame(self.scrollable_frame, bg=UIConfig.COLORS['bg_primary'])
        self.loading_frame.pack(fill=tk.BOTH, expand=True, pady=50)
        
        tk.Label(
            self.loading_frame,
            text="🔄 Loading comprehensive strategy analysis...",
            font=('Arial', 14),
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack()
        
        tk.Label(
            self.loading_frame,
            text="Analyzing put overlays, call overlays, synthetic recovery, and time estimation",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(pady=(5, 0))
    
    def _on_mousewheel(self, event):
        """Handle mouse wheel scrolling"""
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def create_action_buttons(self, parent):
        """Create action buttons for strategy management"""
        button_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # Refresh strategies button
        refresh_btn = create_styled_button(
            button_frame,
            "🔄 Refresh Strategies",
            self.refresh_strategies,
            'primary'
        )
        refresh_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Export strategies button
        export_btn = create_styled_button(
            button_frame,
            "📊 Export Analysis",
            self.export_strategies,
            'info'
        )
        export_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="Ready to analyze strategies",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def load_all_strategies(self):
        """Load all strategy types in background thread"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.status_label.config(text="🔄 Analyzing strategies...")
        
        # Run analysis in background thread
        thread = threading.Thread(target=self._fetch_strategies_background)
        thread.daemon = True
        thread.start()
    
    def _fetch_strategies_background(self):
        """Fetch all strategies in background thread"""
        try:
            ticker = self.position.ticker
            cost_basis = self.position.cost_basis
            qty = self.position.qty
            
            # Update status
            self.parent.after(0, lambda: self.status_label.config(text="🔄 Analyzing put overlays..."))
            
            # Fetch put overlay strategies
            put_strategies = evaluate_put_overlay(ticker, cost_basis, qty)
            
            # Update status
            self.parent.after(0, lambda: self.status_label.config(text="🔄 Analyzing call overlays..."))
            
            # Fetch call overlay strategies
            call_strategies = evaluate_call_overlay(ticker, cost_basis, qty)
            
            # Update status
            self.parent.after(0, lambda: self.status_label.config(text="🔄 Building synthetic recovery..."))
            
            # Fetch synthetic recovery strategy
            synthetic_strategy = build_synthetic_recovery(ticker, cost_basis, qty)
            
            # Update status
            self.parent.after(0, lambda: self.status_label.config(text="🔄 Estimating recovery time..."))
            
            # Get current price and estimate recovery time
            from utils.strategy_engine import OptionChainAnalyzer
            analyzer = OptionChainAnalyzer()
            current_price = analyzer.get_current_price(ticker)
            
            recovery_time_analysis = None
            if current_price:
                recovery_time_analysis = estimate_recovery_time(ticker, current_price, cost_basis)
            
            # Store all strategies
            self.all_strategies = {
                'put_overlays': put_strategies,
                'call_overlays': call_strategies,
                'synthetic_recovery': synthetic_strategy,
                'recovery_time': recovery_time_analysis
            }
            
            # Update UI in main thread
            self.parent.after(0, self._display_all_strategies)
            
        except Exception as e:
            error_msg = f"Error loading strategies: {e}"
            self.parent.after(0, lambda: self._show_error(error_msg))
        finally:
            self.is_loading = False
    
    def _display_all_strategies(self):
        """Display all strategies as color-coded cards"""
        # Clear loading content
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        # Create main strategies frame
        strategies_frame = tk.Frame(self.scrollable_frame, bg=UIConfig.COLORS['bg_primary'])
        strategies_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Display recovery time summary at top
        self._create_recovery_time_summary(strategies_frame)
        
        # Display strategy cards
        self._create_put_overlay_cards(strategies_frame)
        self._create_call_overlay_cards(strategies_frame)
        self._create_synthetic_recovery_card(strategies_frame)
        
        # Display strategy comparison
        self._create_strategy_comparison(strategies_frame)
        
        # Update status
        total_strategies = (
            len(self.all_strategies['put_overlays']) + 
            len(self.all_strategies['call_overlays']) +
            (1 if self.all_strategies['synthetic_recovery'] else 0)
        )
        
        self.status_label.config(
            text=f"✅ Analysis complete: {total_strategies} strategies found - {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _create_recovery_time_summary(self, parent):
        """Create recovery time summary card"""
        recovery_time = self.all_strategies.get('recovery_time')
        if not recovery_time:
            return
        
        # Recovery time summary frame
        time_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=2)
        time_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Header
        header_frame = tk.Frame(time_frame, bg=UIConfig.COLORS['accent'])
        header_frame.pack(fill=tk.X)
        
        tk.Label(
            header_frame,
            text="⏰ Recovery Time Analysis",
            font=('Arial', 14, 'bold'),
            fg='white',
            bg=UIConfig.COLORS['accent']
        ).pack(pady=8)
        
        # Content
        content_frame = tk.Frame(time_frame, bg=UIConfig.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        breakeven_window = recovery_time['breakeven_window']
        estimates = recovery_time['estimates']
        
        # Breakeven window (main metric)
        window_color = UIConfig.COLORS['success'] if breakeven_window <= 90 else UIConfig.COLORS['warning'] if breakeven_window <= 180 else UIConfig.COLORS['danger']
        
        tk.Label(
            content_frame,
            text=f"🎯 Estimated Breakeven Window: {breakeven_window} days ({estimates.get('most_likely_calendar', 'N/A')})",
            font=('Arial', 12, 'bold'),
            fg=window_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Time range
        time_range = (
            f"📅 Range: {estimates['optimistic_days']} - {estimates['pessimistic_days']} days "
            f"({estimates.get('optimistic_calendar', 'N/A')} - {estimates.get('pessimistic_calendar', 'N/A')})"
        )
        
        tk.Label(
            content_frame,
            text=time_range,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
    
    def _create_put_overlay_cards(self, parent):
        """Create put overlay strategy cards"""
        put_strategies = self.all_strategies['put_overlays']
        if not put_strategies:
            return
        
        # Section header
        section_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        section_frame.pack(fill=tk.X, pady=(15, 10))
        
        tk.Label(
            section_frame,
            text="📉 Put Overlay Strategies (Protective Insurance)",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        # Strategy cards
        cards_container = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        cards_container.pack(fill=tk.X, pady=(0, 15))
        
        for i, strategy in enumerate(put_strategies[:3]):  # Top 3 strategies
            self._create_put_strategy_card(cards_container, strategy, i + 1)
    
    def _create_put_strategy_card(self, parent, strategy, rank):
        """Create individual put strategy card"""
        # Card frame with ranking color
        rank_colors = [UIConfig.COLORS['success'], UIConfig.COLORS['warning'], UIConfig.COLORS['info']]
        card_color = rank_colors[rank - 1] if rank <= 3 else UIConfig.COLORS['bg_secondary']
        
        card_frame = tk.Frame(parent, bg=card_color, relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg=card_color)
        header_frame.pack(fill=tk.X, padx=10, pady=(8, 5))
        
        # Rank and trade type
        rank_label = tk.Label(
            header_frame,
            text=f"#{rank}",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg=card_color
        )
        rank_label.pack(side=tk.LEFT)
        
        trade_type_label = tk.Label(
            header_frame,
            text="PUT OVERLAY",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg=card_color
        )
        trade_type_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Score
        score_label = tk.Label(
            header_frame,
            text=f"Score: {strategy.get('combined_score', 0):.1f}",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg=card_color
        )
        score_label.pack(side=tk.RIGHT)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        details_frame = tk.Frame(content_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Strike and expiry
        strike_price = strategy.get('strike_price', 0)
        expiry = strategy.get('expiry', 'N/A')
        
        strike_expiry_text = f"🎯 Strike: ${strike_price:.2f} | 📅 Expiry: {expiry}"
        tk.Label(
            details_frame,
            text=strike_expiry_text,
            font=('Arial', 11, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Premium and net impact
        premium = strategy.get('premium', 0) * strategy.get('contracts', 1)
        protection_level = strategy.get('protection_level', 0)
        
        premium_text = f"💰 Premium: ${premium:.2f} | 🛡️ Protection Level: {protection_level:.1f}%"
        tk.Label(
            details_frame,
            text=premium_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Insurance cost and recommendation
        insurance_cost = strategy.get('insurance_cost_pct', 0)
        recommendation = strategy.get('recommendation', 'No recommendation available')
        
        cost_text = f"📊 Insurance Cost: {insurance_cost:.1f}% of position value"
        tk.Label(
            details_frame,
            text=cost_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        tk.Label(
            details_frame,
            text=f"💡 {recommendation}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w', pady=(5, 0))
    
    def _create_call_overlay_cards(self, parent):
        """Create call overlay strategy cards"""
        call_strategies = self.all_strategies['call_overlays']
        if not call_strategies:
            return
        
        # Section header
        section_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        section_frame.pack(fill=tk.X, pady=(15, 10))
        
        tk.Label(
            section_frame,
            text="📈 Call Overlay Strategies (Income Generation)",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        # Strategy cards
        cards_container = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        cards_container.pack(fill=tk.X, pady=(0, 15))
        
        for i, strategy in enumerate(call_strategies[:3]):  # Top 3 strategies
            self._create_call_strategy_card(cards_container, strategy, i + 1)
    
    def _create_call_strategy_card(self, parent, strategy, rank):
        """Create individual call strategy card"""
        # Card frame with ranking color (green theme for calls)
        rank_colors = [UIConfig.COLORS['success'], '#27ae60', '#2ecc71']
        card_color = rank_colors[rank - 1] if rank <= 3 else UIConfig.COLORS['bg_secondary']
        
        card_frame = tk.Frame(parent, bg=card_color, relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg=card_color)
        header_frame.pack(fill=tk.X, padx=10, pady=(8, 5))
        
        # Rank and trade type
        rank_label = tk.Label(
            header_frame,
            text=f"#{rank}",
            font=('Arial', 12, 'bold'),
            fg='white',
            bg=card_color
        )
        rank_label.pack(side=tk.LEFT)
        
        trade_type_label = tk.Label(
            header_frame,
            text="COVERED CALL",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg=card_color
        )
        trade_type_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Score
        score_label = tk.Label(
            header_frame,
            text=f"Score: {strategy.get('combined_score', 0):.1f}",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg=card_color
        )
        score_label.pack(side=tk.RIGHT)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        details_frame = tk.Frame(content_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Strike and expiry
        strike_price = strategy.get('strike', 0)
        expiry = strategy.get('expiry', 'N/A')
        
        strike_expiry_text = f"🎯 Strike: ${strike_price:.2f} | 📅 Expiry: {expiry}"
        tk.Label(
            details_frame,
            text=strike_expiry_text,
            font=('Arial', 11, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Premium and yield
        total_premium = strategy.get('total_premium', 0)
        monthly_yield = strategy.get('monthly_yield_pct', 0)
        
        premium_text = f"💰 Premium Income: ${total_premium:.2f} | 📊 Monthly Yield: {monthly_yield:.2f}%"
        tk.Label(
            details_frame,
            text=premium_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Assignment probability and time-to-recovery impact
        assignment_prob = strategy.get('assignment_probability', 0)
        recovery_time = self.all_strategies.get('recovery_time', {})
        base_recovery_days = recovery_time.get('breakeven_window', 365) if recovery_time else 365
        
        # Estimate call impact on recovery time
        if total_premium > 0:
            premium_impact_days = max(0, base_recovery_days - (total_premium / (self.position.cost_basis * self.position.qty) * base_recovery_days))
            time_impact_text = f"⏰ Time-to-Recovery Impact: -{int(base_recovery_days - premium_impact_days)} days (accelerated by premium)"
        else:
            time_impact_text = f"⏰ Time-to-Recovery: No significant impact"
        
        assignment_text = f"🎲 Assignment Probability: {assignment_prob:.1f}%"
        tk.Label(
            details_frame,
            text=assignment_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        tk.Label(
            details_frame,
            text=time_impact_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Recommendation
        recommendation = strategy.get('recommendation', 'No recommendation available')
        tk.Label(
            details_frame,
            text=f"💡 {recommendation}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w', pady=(5, 0))
    
    def _create_synthetic_recovery_card(self, parent):
        """Create synthetic recovery strategy card"""
        synthetic_strategy = self.all_strategies['synthetic_recovery']
        if not synthetic_strategy:
            return
        
        # Section header
        section_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        section_frame.pack(fill=tk.X, pady=(15, 10))
        
        tk.Label(
            section_frame,
            text="🔄 Synthetic Recovery Strategy (Accelerated Recovery)",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['highlight'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        # Strategy card
        card_frame = tk.Frame(parent, bg=UIConfig.COLORS['highlight'], relief=tk.RAISED, bd=2)
        card_frame.pack(fill=tk.X, pady=5)
        
        # Card header
        header_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['highlight'])
        header_frame.pack(fill=tk.X, padx=10, pady=(8, 5))
        
        # Trade type
        trade_type_label = tk.Label(
            header_frame,
            text="SYNTHETIC RECOVERY",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg=UIConfig.COLORS['highlight']
        )
        trade_type_label.pack(side=tk.LEFT)
        
        # Viability score
        viability_score = synthetic_strategy.get('viability_score', 0)
        score_label = tk.Label(
            header_frame,
            text=f"Viability Score: {viability_score:.1f}",
            font=('Arial', 10, 'bold'),
            fg='white',
            bg=UIConfig.COLORS['highlight']
        )
        score_label.pack(side=tk.RIGHT)
        
        # Card content
        content_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=2, pady=(0, 2))
        
        details_frame = tk.Frame(content_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=10, pady=8)
        
        # Double down details
        double_down = synthetic_strategy.get('double_down', {})
        additional_shares = double_down.get('additional_shares', 0)
        additional_investment = double_down.get('additional_investment', 0)
        new_cost_basis = double_down.get('new_cost_basis', 0)
        
        double_down_text = f"📈 Double Down: Buy {additional_shares} more shares (${additional_investment:,.0f} additional investment)"
        tk.Label(
            details_frame,
            text=double_down_text,
            font=('Arial', 11, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        cost_basis_text = f"💰 New Cost Basis: ${new_cost_basis:.2f}"
        tk.Label(
            details_frame,
            text=cost_basis_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Best call option details
        best_call = synthetic_strategy.get('best_call', {})
        if best_call:
            call_strike = best_call.get('strike', 0)
            call_premium = best_call.get('total_premium', 0)
            effective_cost_basis = synthetic_strategy.get('effective_cost_basis', 0)
            
            call_text = f"📞 Best Call: ${call_strike:.2f} strike, ${call_premium:.0f} premium income"
            tk.Label(
                details_frame,
                text=call_text,
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
            
            effective_text = f"🎯 Effective Cost Basis: ${effective_cost_basis:.2f} (after premium)"
            tk.Label(
                details_frame,
                text=effective_text,
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['success'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
        
        # Time-to-recovery impact
        recovery_time = self.all_strategies.get('recovery_time', {})
        base_recovery_days = recovery_time.get('breakeven_window', 365) if recovery_time else 365
        
        # Estimate synthetic recovery acceleration
        if best_call and double_down:
            recovery_reduction = double_down.get('recovery_needed_pct', 0)
            accelerated_days = max(30, int(base_recovery_days * (1 - recovery_reduction / 100)))
            acceleration = base_recovery_days - accelerated_days
            
            time_impact_text = f"⏰ Time-to-Recovery: ~{accelerated_days} days (accelerated by {acceleration} days)"
        else:
            time_impact_text = f"⏰ Time-to-Recovery: Analysis pending"
        
        tk.Label(
            details_frame,
            text=time_impact_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Risk level and recommendation
        risk_level = synthetic_strategy.get('risk_level', 'UNKNOWN')
        recommendation = synthetic_strategy.get('recommendation', 'No recommendation available')
        
        risk_color = UIConfig.COLORS['success'] if 'LOW' in risk_level else UIConfig.COLORS['warning'] if 'MEDIUM' in risk_level else UIConfig.COLORS['danger']
        
        risk_text = f"⚠️ Risk Level: {risk_level}"
        tk.Label(
            details_frame,
            text=risk_text,
            font=UIConfig.DEFAULT_FONT,
            fg=risk_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        tk.Label(
            details_frame,
            text=f"💡 {recommendation}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w', pady=(5, 0))
    
    def _create_strategy_comparison(self, parent):
        """Create strategy comparison summary"""
        # Section header
        section_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_primary'])
        section_frame.pack(fill=tk.X, pady=(20, 10))
        
        tk.Label(
            section_frame,
            text="📊 Strategy Comparison & Recommendation",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        # Comparison card
        comparison_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=2)
        comparison_frame.pack(fill=tk.X, pady=5)
        
        content_frame = tk.Frame(comparison_frame, bg=UIConfig.COLORS['bg_secondary'])
        content_frame.pack(fill=tk.X, padx=15, pady=10)
        
        # Calculate best strategies
        put_score = self.all_strategies['put_overlays'][0]['combined_score'] if self.all_strategies['put_overlays'] else 0
        call_score = self.all_strategies['call_overlays'][0]['combined_score'] if self.all_strategies['call_overlays'] else 0
        synthetic_score = self.all_strategies['synthetic_recovery'].get('viability_score', 0) if self.all_strategies['synthetic_recovery'] else 0
        
        # Display scores
        scores_text = f"Put Overlay Best: {put_score:.1f} | Call Overlay Best: {call_score:.1f} | Synthetic Recovery: {synthetic_score:.1f}"
        tk.Label(
            content_frame,
            text=scores_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Determine and display recommendation
        best_strategy = max([
            ('Put Overlay Protection', put_score),
            ('Call Overlay Income', call_score),
            ('Synthetic Recovery', synthetic_score)
        ], key=lambda x: x[1])
        
        recommendation_text = f"🏆 Recommended Strategy: {best_strategy[0]} (Score: {best_strategy[1]:.1f})"
        tk.Label(
            content_frame,
            text=recommendation_text,
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', pady=(5, 0))
        
        # Recovery time context
        recovery_time = self.all_strategies.get('recovery_time')
        if recovery_time:
            context_text = f"📅 Natural Recovery Time: {recovery_time['breakeven_window']} days - Strategy can accelerate or protect during this period"
            tk.Label(
                content_frame,
                text=context_text,
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['info'],
                bg=UIConfig.COLORS['bg_secondary'],
                wraplength=700
            ).pack(anchor='w', pady=(5, 0))
    
    def refresh_strategies(self):
        """Refresh all strategies"""
        self.load_all_strategies()
    
    def export_strategies(self):
        """Export strategy analysis to file"""
        try:
            # Create export data
            export_data = {
                'ticker': self.position.ticker,
                'analysis_time': datetime.now().isoformat(),
                'position': {
                    'ticker': self.position.ticker,
                    'quantity': self.position.qty,
                    'cost_basis': self.position.cost_basis,
                    'total_investment': self.position.total_investment()
                },
                'strategies': self.all_strategies
            }
            
            # For now, show success message (actual export can be implemented later)
            messagebox.showinfo(
                "Export Strategies",
                f"Strategy analysis for {self.position.ticker} ready for export.\n"
                f"Found {len(self.all_strategies['put_overlays'])} put strategies, "
                f"{len(self.all_strategies['call_overlays'])} call strategies, "
                f"and synthetic recovery analysis."
            )
            
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting strategies: {e}")
    
    def _show_error(self, error_msg):
        """Show error message"""
        self.status_label.config(text=f"❌ Error: {error_msg}")
        
        # Clear loading content and show error
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        error_frame = tk.Frame(self.scrollable_frame, bg=UIConfig.COLORS['bg_primary'])
        error_frame.pack(fill=tk.BOTH, expand=True, pady=50)
        
        tk.Label(
            error_frame,
            text="❌ Strategy Analysis Error",
            font=('Arial', 16, 'bold'),
            fg=UIConfig.COLORS['danger'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack()
        
        tk.Label(
            error_frame,
            text=error_msg,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary'],
            wraplength=600
        ).pack(pady=(10, 0))
        
        # Retry button
        retry_btn = create_styled_button(
            error_frame,
            "🔄 Retry Analysis",
            self.refresh_strategies,
            'primary'
        )
        retry_btn.pack(pady=(20, 0))
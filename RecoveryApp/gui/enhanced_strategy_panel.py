"""
Enhanced Strategy Display Panel for RecoveryApp
Shows both put overlay and covered call recovery strategies
"""
import tkinter as tk
from tkinter import ttk, messagebox
import threading
from datetime import datetime
from utils.ui_utils import UIConfig, create_styled_button
from utils.strategy_engine import evaluate_put_overlay, evaluate_call_overlay, build_synthetic_recovery, estimate_recovery_time

class EnhancedStrategyPanel:
    """
    Enhanced panel to display both put and call recovery strategies
    """
    def __init__(self, parent, ticker):
        self.parent = parent
        self.ticker = ticker
        self.put_strategies = []
        self.call_strategies = []
        self.is_loading = False
        
        # Mock position data for demo
        self.cost_basis = 42.50 if ticker == "SOXL" else 120.00
        self.qty = 100
        
        self.create_strategy_panel()
        
    def create_strategy_panel(self):
        """Create the enhanced strategy panel with tabs"""
        # Main container
        main_frame = tk.Frame(self.parent, bg=UIConfig.COLORS['bg_secondary'])
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Header with position info
        self.create_header(main_frame)
        
        # Strategy notebook with tabs
        self.create_strategy_notebook(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
    
    def create_header(self, parent):
        """Create header with position summary"""
        header_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Title
        title_label = tk.Label(
            header_frame,
            text=f"Recovery Strategies for {self.ticker}",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        title_label.pack(anchor='w')
        
        # Position details
        current_price = self.cost_basis * 0.85  # Simulate 15% loss
        total_investment = self.cost_basis * self.qty
        current_value = current_price * self.qty
        unrealized_loss = current_value - total_investment
        
        details_text = (
            f"Position: {self.qty:,} shares @ ${self.cost_basis:.2f} "
            f"(Current: ${current_price:.2f}) | "
            f"Unrealized P&L: ${unrealized_loss:,.0f} "
            f"({(unrealized_loss/total_investment)*100:.1f}%)"
        )
        
        tk.Label(
            header_frame,
            text=details_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['danger'] if unrealized_loss < 0 else UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', pady=(5, 0))
    
    def create_strategy_notebook(self, parent):
        """Create tabbed interface for different strategy types"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Put Strategies Tab
        self.put_frame = tk.Frame(self.notebook, bg=UIConfig.COLORS['bg_primary'])
        self.notebook.add(self.put_frame, text="📉 Put Overlays")
        
        # Call Strategies Tab
        self.call_frame = tk.Frame(self.notebook, bg=UIConfig.COLORS['bg_primary'])
        self.notebook.add(self.call_frame, text="📈 Covered Calls")
        
        # Synthetic Recovery Tab
        self.synthetic_frame = tk.Frame(self.notebook, bg=UIConfig.COLORS['bg_primary'])
        self.notebook.add(self.synthetic_frame, text="🔄 Synthetic Recovery")
        
        # Recovery Time Tab
        self.recovery_time_frame = tk.Frame(self.notebook, bg=UIConfig.COLORS['bg_primary'])
        self.notebook.add(self.recovery_time_frame, text="⏰ Recovery Time")
        
        # Create content for each tab
        self.setup_put_strategies_tab()
        self.setup_call_strategies_tab()
        self.setup_synthetic_strategies_tab()
        self.setup_recovery_time_tab()
    
    def setup_put_strategies_tab(self):
        """Setup put overlay strategies tab"""
        # Description
        desc_frame = tk.Frame(self.put_frame, bg=UIConfig.COLORS['bg_primary'])
        desc_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            desc_frame,
            text="💡 Put Overlay Strategy: Sell cash-secured puts to potentially acquire more shares at lower prices",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_primary'],
            wraplength=600
        ).pack(anchor='w')
        
        # Strategy display area
        self.put_strategies_frame = tk.Frame(self.put_frame, bg=UIConfig.COLORS['bg_primary'])
        self.put_strategies_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Loading label
        self.put_loading_label = tk.Label(
            self.put_strategies_frame,
            text="Click 'Analyze Strategies' to load put overlay suggestions",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.put_loading_label.pack(expand=True)
    
    def setup_call_strategies_tab(self):
        """Setup covered call strategies tab"""
        # Description
        desc_frame = tk.Frame(self.call_frame, bg=UIConfig.COLORS['bg_primary'])
        desc_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(
            desc_frame,
            text="💡 Covered Call Strategy: Sell calls against your shares to generate income while waiting for recovery",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['info'],
            bg=UIConfig.COLORS['bg_primary'],
            wraplength=600
        ).pack(anchor='w')
        
        # Strategy display area
        self.call_strategies_frame = tk.Frame(self.call_frame, bg=UIConfig.COLORS['bg_primary'])
        self.call_strategies_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        # Loading label
        self.call_loading_label = tk.Label(
            self.call_strategies_frame,
            text="Click 'Analyze Strategies' to load covered call suggestions",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.call_loading_label.pack(expand=True)
    
    def create_action_buttons(self, parent):
        """Create action buttons"""
        button_frame = tk.Frame(parent, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Analyze button
        analyze_button = create_styled_button(
            button_frame,
            "🔍 Analyze Strategies",
            self.analyze_strategies,
            'primary'
        )
        analyze_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Refresh button
        refresh_button = create_styled_button(
            button_frame,
            "🔄 Refresh",
            self.refresh_strategies,
            'info'
        )
        refresh_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Status label
        self.status_label = tk.Label(
            button_frame,
            text="Ready to analyze",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.status_label.pack(side=tk.RIGHT)
    
    def analyze_strategies(self):
        """Analyze both put and call strategies"""
        if self.is_loading:
            return
        
        self.is_loading = True
        self.status_label.config(text="🔄 Analyzing strategies...")
        
        # Update loading labels
        self.put_loading_label.config(text="🔄 Analyzing put overlay strategies...")
        self.call_loading_label.config(text="🔄 Analyzing covered call strategies...")
        self.synthetic_loading_label.config(text="🔄 Analyzing synthetic recovery strategy...")
        self.recovery_time_loading_label.config(text="🔄 Estimating recovery time...")
        
        # Run analysis in background thread
        thread = threading.Thread(target=self._fetch_all_strategies)
        thread.daemon = True
        thread.start()
    
    def _fetch_all_strategies(self):
        """Fetch all strategies (put, call, synthetic, and recovery time) in background"""
        try:
            # Fetch put strategies
            put_strategies = evaluate_put_overlay(self.ticker, self.cost_basis, self.qty)
            
            # Fetch call strategies
            call_strategies = evaluate_call_overlay(self.ticker, self.cost_basis, self.qty)
            
            # Fetch synthetic recovery strategy
            synthetic_strategy = build_synthetic_recovery(self.ticker, self.cost_basis, self.qty)
            
            # Get current price for recovery time estimation
            from utils.strategy_engine import OptionChainAnalyzer
            analyzer = OptionChainAnalyzer()
            current_price = analyzer.get_current_price(self.ticker)
            
            # Estimate recovery time
            recovery_time_analysis = None
            if current_price:
                recovery_time_analysis = estimate_recovery_time(self.ticker, current_price, self.cost_basis)
            
            # Update UI in main thread
            self.parent.after(0, lambda: self._update_all_strategies(put_strategies, call_strategies, synthetic_strategy, recovery_time_analysis))
            
        except Exception as e:
            error_msg = f"Error analyzing strategies: {e}"
            self.parent.after(0, lambda: self._show_error(error_msg))
        finally:
            self.is_loading = False
    
    def _update_all_strategies(self, put_strategies, call_strategies, synthetic_strategy, recovery_time_analysis):
        """Update all strategy displays"""
        self.put_strategies = put_strategies
        self.call_strategies = call_strategies
        self.synthetic_strategy = synthetic_strategy
        self.recovery_time_analysis = recovery_time_analysis
        
        # Update put strategies display
        self._update_put_strategies_display()
        
        # Update call strategies display
        self._update_call_strategies_display()
        
        # Update synthetic strategy display
        self.display_synthetic_strategy(synthetic_strategy)
        
        # Update recovery time display
        self.display_recovery_time_analysis(recovery_time_analysis)
        
        # Update status
        recovery_time_text = f", recovery time: {recovery_time_analysis['breakeven_window']} days" if recovery_time_analysis else ""
        self.status_label.config(
            text=f"Found {len(put_strategies)} put, {len(call_strategies)} call strategies, synthetic recovery{recovery_time_text} - {datetime.now().strftime('%H:%M:%S')}"
        )
    
    def _update_put_strategies_display(self):
        """Update put strategies display"""
        # Clear existing content
        for widget in self.put_strategies_frame.winfo_children():
            widget.destroy()
        
        if not self.put_strategies:
            tk.Label(
                self.put_strategies_frame,
                text="No viable put overlay strategies found",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['warning'],
                bg=UIConfig.COLORS['bg_primary']
            ).pack(expand=True)
            return
        
        # Display strategies
        for i, strategy in enumerate(self.put_strategies, 1):
            self._create_put_strategy_card(strategy, i)
    
    def _update_call_strategies_display(self):
        """Update call strategies display"""
        # Clear existing content
        for widget in self.call_strategies_frame.winfo_children():
            widget.destroy()
        
        if not self.call_strategies:
            tk.Label(
                self.call_strategies_frame,
                text="No viable covered call strategies found",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['warning'],
                bg=UIConfig.COLORS['bg_primary']
            ).pack(expand=True)
            return
        
        # Display strategies
        for i, strategy in enumerate(self.call_strategies, 1):
            self._create_call_strategy_card(strategy, i)
    
    def _create_put_strategy_card(self, strategy, rank):
        """Create strategy card for put overlay"""
        card_frame = tk.Frame(
            self.put_strategies_frame,
            bg=UIConfig.COLORS['bg_secondary'],
            relief=tk.RAISED,
            bd=2
        )
        card_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(
            header_frame,
            text=f"#{rank} Put Overlay - Strike ${strategy['strike']} (Score: {strategy['combined_score']:.1f})",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT)
        
        # Strategy details
        details_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        details_text = (
            f"Premium: ${strategy['bid']:.2f} (${strategy['premium_income']:.0f} total) | "
            f"Expiry: {strategy['expiry']} | "
            f"Assignment Prob: {strategy['prob_assignment']:.1%} | "
            f"Risk: {strategy['risk_level']}"
        )
        
        tk.Label(
            details_frame,
            text=details_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w')
        
        # Recommendation
        tk.Label(
            details_frame,
            text=f"💡 {strategy.get('recommendation', 'Strategy recommendation')}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w', pady=(5, 0))
    
    def _create_call_strategy_card(self, strategy, rank):
        """Create strategy card for covered call"""
        card_frame = tk.Frame(
            self.call_strategies_frame,
            bg=UIConfig.COLORS['bg_secondary'],
            relief=tk.RAISED,
            bd=2
        )
        card_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Header
        header_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        header_frame.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        tk.Label(
            header_frame,
            text=f"#{rank} Covered Call - Strike ${strategy['strike']} (Score: {strategy['combined_score']:.1f})",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(side=tk.LEFT)
        
        # Strategy details
        details_frame = tk.Frame(card_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        details_text = (
            f"Premium: ${strategy['bid']:.2f} (${strategy['premium_income']:.0f} total) | "
            f"Yield: {strategy['premium_yield']:.1f}% annualized | "
            f"Expiry: {strategy['expiry']} | "
            f"Risk: {strategy['risk_level']}"
        )
        
        tk.Label(
            details_frame,
            text=details_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w')
        
        # Recommendation
        tk.Label(
            details_frame,
            text=f"💡 {strategy.get('recommendation', 'Strategy recommendation')}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w', pady=(5, 0))
    
    def setup_synthetic_strategies_tab(self):
        """Setup synthetic recovery strategies tab"""
        # Description
        desc_frame = tk.Frame(self.synthetic_frame, bg=UIConfig.COLORS['bg_primary'])
        desc_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            desc_frame,
            text="🔄 Synthetic Recovery Strategy",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        tk.Label(
            desc_frame,
            text="Double down position and sell covered calls to accelerate recovery with premium income",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w', pady=(5, 0))
        
        # Synthetic strategy content frame
        self.synthetic_content_frame = tk.Frame(self.synthetic_frame, bg=UIConfig.COLORS['bg_primary'])
        self.synthetic_content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Synthetic loading message
        self.synthetic_loading_label = tk.Label(
            self.synthetic_content_frame,
            text="Click 'Analyze Strategies' to generate synthetic recovery analysis",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.synthetic_loading_label.pack(pady=20)
    
    def display_synthetic_strategy(self, strategy):
        """Display synthetic recovery strategy results"""
        # Clear previous content
        for widget in self.synthetic_content_frame.winfo_children():
            widget.destroy()
        
        if not strategy:
            tk.Label(
                self.synthetic_content_frame,
                text="No viable synthetic recovery strategy found",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['danger'],
                bg=UIConfig.COLORS['bg_primary']
            ).pack(pady=20)
            return
        
        # Strategy overview
        overview_frame = tk.Frame(self.synthetic_content_frame, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
        overview_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        tk.Label(
            overview_frame,
            text="🎯 Synthetic Recovery Strategy",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        # Strategy details
        details_frame = tk.Frame(overview_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Double down metrics
        double_down = strategy.get('double_down', {})
        tk.Label(
            details_frame,
            text=f"📈 Double Down: Buy {double_down.get('additional_shares', 0)} more shares @ ${double_down.get('current_price', 0):.2f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        tk.Label(
            details_frame,
            text=f"💰 Additional Investment: ${double_down.get('additional_investment', 0):,.0f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        tk.Label(
            details_frame,
            text=f"📊 New Cost Basis: ${double_down.get('new_cost_basis', 0):.2f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        recovery_pct = double_down.get('recovery_needed_pct', 0)
        recovery_color = UIConfig.COLORS['success'] if recovery_pct < 10 else UIConfig.COLORS['warning'] if recovery_pct < 20 else UIConfig.COLORS['danger']
        tk.Label(
            details_frame,
            text=f"🎯 Recovery Needed: {recovery_pct:.1f}%",
            font=UIConfig.DEFAULT_FONT,
            fg=recovery_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Best call option
        best_call = strategy.get('best_call', {})
        if best_call:
            tk.Label(
                details_frame,
                text=f"📞 Best Call: ${best_call.get('strike', 0):.2f} strike",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w', pady=(10, 0))
            
            tk.Label(
                details_frame,
                text=f"💵 Premium Income: ${best_call.get('total_premium', 0):,.0f}",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['success'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
            
            tk.Label(
                details_frame,
                text=f"📉 Effective Cost Basis: ${strategy.get('effective_cost_basis', 0):.2f}",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['success'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
        
        # Scores and recommendation
        viability_score = strategy.get('viability_score', 0)
        score_color = UIConfig.COLORS['success'] if viability_score >= 80 else UIConfig.COLORS['warning'] if viability_score >= 60 else UIConfig.COLORS['danger']
        
        tk.Label(
            details_frame,
            text=f"🏆 Viability Score: {viability_score:.1f}/100",
            font=UIConfig.DEFAULT_FONT,
            fg=score_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', pady=(10, 0))
        
        risk_level = strategy.get('risk_level', 'UNKNOWN')
        risk_color = UIConfig.COLORS['success'] if 'LOW' in risk_level else UIConfig.COLORS['warning'] if 'MEDIUM' in risk_level else UIConfig.COLORS['danger']
        
        tk.Label(
            details_frame,
            text=f"⚠️ Risk Level: {risk_level}",
            font=UIConfig.DEFAULT_FONT,
            fg=risk_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Scenarios
        scenarios_frame = tk.Frame(self.synthetic_content_frame, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
        scenarios_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(
            scenarios_frame,
            text="📊 Potential Outcomes",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        scenarios_content = tk.Frame(scenarios_frame, bg=UIConfig.COLORS['bg_secondary'])
        scenarios_content.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        # Calls expire scenario
        tk.Label(
            scenarios_content,
            text=f"✅ If Calls Expire: Keep ${best_call.get('total_premium', 0):,.0f} premium, breakeven at ${strategy.get('effective_cost_basis', 0):.2f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w')
        
        # Calls assigned scenario
        total_shares = double_down.get('original_shares', 0) + double_down.get('additional_shares', 0)
        assignment_proceeds = best_call.get('strike', 0) * total_shares + best_call.get('total_premium', 0)
        
        tk.Label(
            scenarios_content,
            text=f"📈 If Calls Assigned: Shares called at ${best_call.get('strike', 0):.2f}, total proceeds ${assignment_proceeds:,.0f}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w')
        
        # Recommendation
        tk.Label(
            details_frame,
            text=f"💡 {strategy.get('recommendation', 'Strategy recommendation')}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['success'],
            bg=UIConfig.COLORS['bg_secondary'],
            wraplength=600
        ).pack(anchor='w', pady=(5, 0))
    
    def setup_recovery_time_tab(self):
        """Setup recovery time estimation tab"""
        # Description
        desc_frame = tk.Frame(self.recovery_time_frame, bg=UIConfig.COLORS['bg_primary'])
        desc_frame.pack(fill=tk.X, padx=15, pady=10)
        
        tk.Label(
            desc_frame,
            text="⏰ Recovery Time Estimation",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w')
        
        tk.Label(
            desc_frame,
            text="Estimate breakeven window using historical data and implied volatility analysis",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        ).pack(anchor='w', pady=(5, 0))
        
        # Recovery time content frame
        self.recovery_time_content_frame = tk.Frame(self.recovery_time_frame, bg=UIConfig.COLORS['bg_primary'])
        self.recovery_time_content_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Recovery time loading message
        self.recovery_time_loading_label = tk.Label(
            self.recovery_time_content_frame,
            text="Click 'Analyze Strategies' to generate recovery time analysis",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.recovery_time_loading_label.pack(pady=20)
    
    def display_recovery_time_analysis(self, recovery_analysis):
        """Display recovery time estimation results"""
        # Clear previous content
        for widget in self.recovery_time_content_frame.winfo_children():
            widget.destroy()
        
        if not recovery_analysis:
            tk.Label(
                self.recovery_time_content_frame,
                text="Recovery time analysis not available",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['danger'],
                bg=UIConfig.COLORS['bg_primary']
            ).pack(pady=20)
            return
        
        # Main analysis frame
        analysis_frame = tk.Frame(self.recovery_time_content_frame, bg=UIConfig.COLORS['bg_secondary'], relief=tk.RAISED, bd=1)
        analysis_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Title
        tk.Label(
            analysis_frame,
            text="📊 Recovery Time Analysis",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', padx=15, pady=(10, 5))
        
        # Position details
        details_frame = tk.Frame(analysis_frame, bg=UIConfig.COLORS['bg_secondary'])
        details_frame.pack(fill=tk.X, padx=15, pady=(0, 10))
        
        current_price = recovery_analysis['current_price']
        target_price = recovery_analysis['target_price']
        required_return = recovery_analysis['required_return_pct']
        
        tk.Label(
            details_frame,
            text=f"💰 Current Price: ${current_price:.2f} → Target: ${target_price:.2f} ({required_return:+.1f}%)",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Volatility information
        hist_vol = recovery_analysis['historical_volatility']
        impl_vol = recovery_analysis['implied_volatility']
        
        tk.Label(
            details_frame,
            text=f"📈 Historical Volatility: {hist_vol:.1%} | Implied Volatility: {impl_vol:.1%}",
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w')
        
        # Time estimates
        estimates = recovery_analysis['estimates']
        breakeven_window = recovery_analysis['breakeven_window']
        
        # Main breakeven window
        window_color = UIConfig.COLORS['success'] if breakeven_window <= 90 else UIConfig.COLORS['warning'] if breakeven_window <= 180 else UIConfig.COLORS['danger']
        
        tk.Label(
            details_frame,
            text=f"🎯 Breakeven Window: {breakeven_window} days ({estimates.get('most_likely_calendar', 'N/A')})",
            font=UIConfig.HEADER_FONT,
            fg=window_color,
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor='w', pady=(10, 5))
        
        # Time range estimates
        estimates_text = f"📅 Time Estimates:\n"
        estimates_text += f"   Optimistic: {estimates['optimistic_days']} days ({estimates.get('optimistic_calendar', 'N/A')})\n"
        estimates_text += f"   Most Likely: {estimates['most_likely_days']} days ({estimates.get('most_likely_calendar', 'N/A')})\n"
        estimates_text += f"   Pessimistic: {estimates['pessimistic_days']} days ({estimates.get('pessimistic_calendar', 'N/A')})"
        
        tk.Label(
            details_frame,
            text=estimates_text,
            font=UIConfig.DEFAULT_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary'],
            justify=tk.LEFT
        ).pack(anchor='w', pady=(5, 10))
        
        # Market context
        context = recovery_analysis.get('market_context', {})
        if context:
            tk.Label(
                details_frame,
                text=f"🏢 Asset Class: {context.get('asset_class', 'Unknown')} | Difficulty: {context.get('difficulty_level', 'Unknown')}",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
            
            tk.Label(
                details_frame,
                text=f"📊 Market Sentiment: {context.get('market_sentiment', 'Unknown')}",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
        
        # Volatility regime
        vol_regime = recovery_analysis.get('volatility_regime', {})
        if vol_regime:
            regime_color = UIConfig.COLORS['danger'] if 'HIGH_FEAR' in vol_regime.get('regime', '') else UIConfig.COLORS['success']
            
            tk.Label(
                details_frame,
                text=f"📊 Volatility Regime: {vol_regime.get('regime', 'Unknown')}",
                font=UIConfig.DEFAULT_FONT,
                fg=regime_color,
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
            
            tk.Label(
                details_frame,
                text=f"   {vol_regime.get('description', '')}",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['text_light'],
                bg=UIConfig.COLORS['bg_secondary']
            ).pack(anchor='w')
        
        # Recommendation
        recommendation = recovery_analysis.get('recommendation', '')
        if recommendation:
            tk.Label(
                details_frame,
                text=f"💡 Recommendation: {recommendation}",
                font=UIConfig.DEFAULT_FONT,
                fg=UIConfig.COLORS['success'],
                bg=UIConfig.COLORS['bg_secondary'],
                wraplength=600
            ).pack(anchor='w', pady=(10, 0))
    
    def refresh_strategies(self):
        """Refresh strategy analysis"""
        self.analyze_strategies()
    
    def _show_error(self, error_msg):
        """Show error message"""
        self.status_label.config(text=f"Error: {error_msg}")
        self.put_loading_label.config(text="Error loading put strategies")
        self.call_loading_label.config(text="Error loading call strategies")
        messagebox.showerror("Strategy Analysis Error", error_msg)

# For backward compatibility, alias the enhanced panel as StrategyPanel
StrategyPanel = EnhancedStrategyPanel
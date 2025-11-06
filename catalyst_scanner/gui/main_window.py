"""
Main Window for Catalyst Scanner

Primary GUI interface with accessible design featuring Arial 12+ fonts
and high-contrast flashy colors for easy readability.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from datetime import datetime
from typing import Dict

from gui.gui_styles import (
    apply_theme_to_root, create_themed_frame, create_themed_label, 
    create_themed_button, GUI_COLORS, FONTS, PADDING
)
from gui.settings_dialog import show_settings_dialog
from gui.monitoring_service_dialog import show_monitoring_service_dialog
from data_collectors.portfolio_loader import load_user_portfolio
from data_collectors.earnings_calendar import EarningsCalendarCollector
from data_collectors.schwab_news_feed import SchwabNewsFeedCollector
from data_collectors.technical_analysis import TechnicalAnalysisCollector
from utils.auth_manager import get_auth_manager
from utils.auto_refresh_manager import AutoRefreshManager
from alerts.alert_system import AlertSystem
from analyzers.insights_generator import InsightsGenerator

class CatalystScannerMainWindow:
    """Main window class for Catalyst Scanner application"""
    
    def __init__(self, root, app_instance=None):
        """Initialize the main window"""
        self.root = root
        self.app_instance = app_instance  # Reference to main app for Phase 4 integration
        self.logger = logging.getLogger(__name__)  # Add missing logger
        self.last_update_time = datetime.now()
        self.last_update_label = None
        self.portfolio_loader = None
        self.portfolio_status_label = None
        self.earnings_collector = EarningsCalendarCollector()
        self.earnings_data = {}
        
        # Initialize authentication manager and news feed collector
        self.auth_manager = get_auth_manager()
        self.news_collector = SchwabNewsFeedCollector(self.auth_manager)
        self.news_data = {}
        
        # Initialize technical analysis collector
        self.technical_collector = TechnicalAnalysisCollector(self.auth_manager)
        self.technical_data = {}
        
        # Initialize auto-refresh manager
        self.auto_refresh_manager = AutoRefreshManager()
        self.auto_refresh_manager.add_refresh_callback(self.auto_refresh_callback)
        
        # Initialize alert system
        self.alert_system = AlertSystem()
        
        self.setup_main_window()
        self.create_menu()
        self.create_main_layout()
        self.load_portfolio_data()
        self.load_earnings_calendar()  # Load earnings after portfolio
        self.load_news_feed()           # Load news feed after portfolio
        self.load_technical_analysis()  # Load technical analysis after portfolio
        self.load_header_positions()    # Load saved header positions
        
        # Start auto-refresh if enabled
        if self.auto_refresh_manager.get_setting('auto_refresh_enabled', True):
            self.auto_refresh_manager.start_auto_refresh()
        
        # Set up window close handler
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)
        
        logging.info("Main window initialized successfully")
    
    def setup_main_window(self):
        """Setup the main window properties"""
        # Apply theme to root
        apply_theme_to_root(self.root)
        
        # Configure window
        self.root.title("Catalyst Scanner - Investment Catalyst Tracking")
        self.root.configure(bg=GUI_COLORS['background'])
        
        # Configure grid weights for responsive design
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
    
    def create_menu(self):
        """Create the main menu bar"""
        menubar = tk.Menu(self.root, 
                         bg=GUI_COLORS['panel_bg'],
                         fg=GUI_COLORS['text_primary'],
                         font=FONTS['normal'])
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0,
                           bg=GUI_COLORS['panel_bg'],
                           fg=GUI_COLORS['text_primary'],
                           font=FONTS['normal'])
        file_menu.add_command(label="Open Portfolio", command=self.open_portfolio)
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0,
                           bg=GUI_COLORS['panel_bg'],
                           fg=GUI_COLORS['text_primary'],
                           font=FONTS['normal'])
        view_menu.add_command(label="Refresh Data", command=self.refresh_data)
        view_menu.add_command(label="Full Screen", command=self.toggle_fullscreen)
        view_menu.add_separator()
        view_menu.add_command(label="🔴 Live Dashboard", command=self.open_live_dashboard)
        menubar.add_cascade(label="View", menu=view_menu)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0,
                           bg=GUI_COLORS['panel_bg'],
                           fg=GUI_COLORS['text_primary'],
                           font=FONTS['normal'])
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)
        
        self.root.config(menu=menubar)
    
    def create_main_layout(self):
        """Create the main application layout"""
        # Main container
        main_container = create_themed_frame(self.root, style='normal')
        main_container.grid(row=0, column=0, sticky='nsew', 
                           padx=PADDING['medium'], pady=PADDING['medium'])
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        # Title bar
        self.create_title_bar(main_container)
        
        # Main content area with scrollable canvas
        self.create_content_area(main_container)
        
        # Status bar
        self.create_status_bar(main_container)
    
    def create_title_bar(self, parent):
        """Create the title and control bar"""
        title_frame = create_themed_frame(parent, style='accent')
        title_frame.grid(row=0, column=0, sticky='ew', pady=(0, PADDING['medium']))
        title_frame.grid_columnconfigure(1, weight=1)  # Changed to make center column expandable
        
        # Title
        title_label = create_themed_label(title_frame, 
                                         "🔍 CATALYST SCANNER", 
                                         style='header')
        title_label.grid(row=0, column=0, padx=PADDING['large'], 
                        pady=PADDING['medium'], sticky='w')
        
        # Last Update timestamp
        self.last_update_label = create_themed_label(title_frame, 
                                                     self._format_last_update(), 
                                                     style='normal')
        self.last_update_label.grid(row=0, column=1, padx=PADDING['medium'], 
                                   pady=PADDING['medium'], sticky='e')
        
        # Control buttons
        controls_frame = create_themed_frame(title_frame, style='accent')
        controls_frame.grid(row=0, column=2, padx=PADDING['large'], 
                           pady=PADDING['medium'], sticky='e')
        
        refresh_btn = create_themed_button(controls_frame, "REFRESH", 
                                          command=self.refresh_data,
                                          style='action')
        refresh_btn.grid(row=0, column=0, padx=(0, PADDING['small']))
        
        settings_btn = create_themed_button(controls_frame, "SETTINGS", 
                                           command=self.open_settings,
                                           style='normal')
        settings_btn.grid(row=0, column=1, padx=(PADDING['small'], PADDING['small']))
        
        monitor_btn = create_themed_button(controls_frame, "🎯 MONITOR", 
                                          command=self.open_monitoring_service,
                                          style='accent')
        monitor_btn.grid(row=0, column=2, padx=(PADDING['small'], 0))
    
    def create_content_area(self, parent):
        """Create the main scrollable content area"""
        # Create canvas and scrollbar for scrolling
        canvas_frame = create_themed_frame(parent, style='normal')
        canvas_frame.grid(row=1, column=0, sticky='nsew')
        canvas_frame.grid_rowconfigure(0, weight=1)
        canvas_frame.grid_columnconfigure(0, weight=1)
        
        # Canvas with scrollbar
        self.canvas = tk.Canvas(canvas_frame, 
                               bg=GUI_COLORS['background'],
                               highlightthickness=0)
        
        # Create custom scrollbar with proper direction handling
        self.scrollbar = ttk.Scrollbar(canvas_frame, orient="vertical")
        
        # Configure scrollbar and canvas with proper binding
        def custom_scrollbar_set(*args):
            """Custom scrollbar set method to ensure proper direction"""
            self.scrollbar.set(*args)
        
        def custom_canvas_yview(*args):
            """Custom canvas yview method to ensure proper scrolling"""
            return self.canvas.yview(*args)
        
        # Set up the scrollbar-canvas relationship
        self.canvas.configure(yscrollcommand=custom_scrollbar_set)
        self.scrollbar.configure(command=custom_canvas_yview)
        
        self.canvas.grid(row=0, column=0, sticky='nsew')
        self.scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Scrollable content frame
        self.content_frame = create_themed_frame(self.canvas, style='normal')
        self.canvas_window = self.canvas.create_window((0, 0), 
                                                      window=self.content_frame, 
                                                      anchor="nw")
        
        # Configure scrolling
        self.content_frame.bind("<Configure>", self.on_content_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        
        # Add mouse wheel support for scrolling
        self.bind_mouse_wheel()
        
        # Create the content panels
        self.create_content_panels()
    
    def bind_mouse_wheel(self):
        """Bind mouse wheel events for scrolling"""
        def on_mouse_wheel(event):
            # Scroll the canvas with mouse wheel
            # On Windows, event.delta provides the scroll direction and amount
            # Positive delta = scroll up (should move content down, showing earlier content)
            # Negative delta = scroll down (should move content up, showing later content)
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        
        def bind_to_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        
        def unbind_from_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Also bind to the content frame for better responsiveness
        def bind_content_mousewheel(event):
            self.canvas.bind_all("<MouseWheel>", on_mouse_wheel)
        
        def unbind_content_mousewheel(event):
            self.canvas.unbind_all("<MouseWheel>")
        
        # Bind mouse wheel when entering the canvas area or content
        self.canvas.bind('<Enter>', bind_to_mousewheel)
        self.canvas.bind('<Leave>', unbind_from_mousewheel)
        self.content_frame.bind('<Enter>', bind_content_mousewheel)
        self.content_frame.bind('<Leave>', unbind_content_mousewheel)
    
    def create_content_panels(self):
        """Create the main content panels"""
        # Morning Brief Panel
        self.create_morning_brief_panel()
        
        # News Feed Panel
        self.create_news_feed_panel()
        
        # Technical Analysis Panel
        self.create_technical_analysis_panel()
        
        # Impact Ranking Panel
        self.create_impact_ranking_panel()
        
        # Earnings Calendar Panel
        self.create_earnings_calendar_panel()
        
        # Opportunity Scanner Panel (initially collapsed)
        self.create_opportunity_panel()
    
    def create_morning_brief_panel(self):
        """Create the Enhanced Morning Brief panel with intelligent insights"""
        brief_frame = create_themed_frame(self.content_frame, style='panel')
        brief_frame.grid(row=0, column=0, sticky='ew', 
                        padx=PADDING['medium'], pady=PADDING['medium'])
        brief_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header with refresh button
        header_frame = create_themed_frame(brief_frame, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', 
                         padx=PADDING['small'], pady=PADDING['small'])
        header_frame.grid_columnconfigure(0, weight=1)  # Make left column expandable
        
        header_label = create_themed_label(header_frame, 
                                          "🌅 YOUR MORNING BRIEF", 
                                          style='subheader')
        header_label.grid(row=0, column=0, padx=PADDING['medium'], 
                         pady=PADDING['small'], sticky='w')
        
        # Refresh button
        refresh_btn = create_themed_button(header_frame, "🔄 Refresh", 
                                         command=self.refresh_morning_brief,
                                         style='small')
        refresh_btn.grid(row=0, column=1, padx=PADDING['small'], 
                        pady=PADDING['small'], sticky='e')
        
        # Portfolio status and risk level in header
        self.portfolio_status_label = create_themed_label(header_frame, 
                                                         "Loading portfolio...", 
                                                         style='normal')
        self.portfolio_status_label.grid(row=0, column=2, padx=PADDING['medium'], 
                                        pady=PADDING['small'], sticky='e')
        
        # Main insights section
        insights_frame = create_themed_frame(brief_frame, style='panel')
        insights_frame.grid(row=1, column=0, sticky='ew', 
                          padx=PADDING['medium'], pady=PADDING['small'])
        insights_frame.grid_columnconfigure(0, weight=1)
        
        # Today's Top 3 Actions header
        actions_header = create_themed_label(insights_frame, 
                                           "📈 TODAY'S TOP 3 ACTIONS", 
                                           style='accent')
        actions_header.grid(row=0, column=0, sticky='w', 
                          padx=PADDING['medium'], pady=PADDING['small'])
        
        # Container for dynamic action items
        self.actions_container = create_themed_frame(insights_frame, style='panel')
        self.actions_container.grid(row=1, column=0, sticky='ew', 
                                  padx=PADDING['medium'], pady=PADDING['small'])
        self.actions_container.grid_columnconfigure(0, weight=1)
        
        # Portfolio risk summary section
        risk_frame = create_themed_frame(brief_frame, style='panel')
        risk_frame.grid(row=2, column=0, sticky='ew', 
                       padx=PADDING['medium'], pady=PADDING['small'])
        risk_frame.grid_columnconfigure(0, weight=1)
        
        risk_header = create_themed_label(risk_frame, 
                                        "⚠️ PORTFOLIO RISK SUMMARY", 
                                        style='accent')
        risk_header.grid(row=0, column=0, sticky='w', 
                        padx=PADDING['medium'], pady=PADDING['small'])
        
        # Risk content container
        self.risk_container = create_themed_frame(risk_frame, style='panel')
        self.risk_container.grid(row=1, column=0, sticky='ew', 
                               padx=PADDING['medium'], pady=PADDING['small'])
        self.risk_container.grid_columnconfigure(0, weight=1)
        
        # Market context section
        market_frame = create_themed_frame(brief_frame, style='panel')
        market_frame.grid(row=3, column=0, sticky='ew', 
                         padx=PADDING['medium'], pady=PADDING['small'])
        market_frame.grid_columnconfigure(0, weight=1)
        
        market_header = create_themed_label(market_frame, 
                                          "🌍 MARKET CONTEXT", 
                                          style='accent')
        market_header.grid(row=0, column=0, sticky='w', 
                          padx=PADDING['medium'], pady=PADDING['small'])
        
        # Market content container
        self.market_container = create_themed_frame(market_frame, style='panel')
        self.market_container.grid(row=1, column=0, sticky='ew', 
                                 padx=PADDING['medium'], pady=PADDING['small'])
        self.market_container.grid_columnconfigure(0, weight=1)
        
        # Initialize the insights generator
        self.insights_generator = InsightsGenerator()
        
        # Load initial insights
        self.load_morning_brief_content()
    
    def refresh_morning_brief(self):
        """Refresh the morning brief with latest data"""
        try:
            self.status_label.config(text="Refreshing morning brief...")
            self.load_morning_brief_content()
            
            # Also refresh impact ranking panel
            if hasattr(self, 'update_impact_ranking_display'):
                self.update_impact_ranking_display()
            
            # Also refresh opportunity scanner
            if hasattr(self, 'update_opportunity_display'):
                self.update_opportunity_display()
            
            self.status_label.config(text="Morning brief updated successfully!")
        except Exception as e:
            self.logger.error(f"Error refreshing morning brief: {e}")
            self.status_label.config(text="Error refreshing morning brief")
    
    def load_morning_brief_content(self):
        """Load and display intelligent morning brief content"""
        try:
            # Clear existing content
            self.clear_container(self.actions_container)
            self.clear_container(self.risk_container)
            self.clear_container(self.market_container)
            
            # Show loading state
            loading_label = create_themed_label(self.actions_container, 
                                              "🔄 Analyzing catalyst events and generating insights...", 
                                              style='normal')
            loading_label.grid(row=0, column=0, sticky='w', 
                              padx=PADDING['large'], pady=PADDING['medium'])
            
            # Update display to show loading
            self.root.update_idletasks()
            
            # Gather data from collectors
            portfolio_data = self.get_portfolio_data()
            earnings_data = self.get_earnings_data()
            news_data = self.get_news_data()
            technical_data = self.get_technical_data()
            
            # Generate insights
            insights = self.insights_generator.generate_daily_insights(
                portfolio_data, earnings_data, news_data, technical_data
            )
            
            # Clear loading and display insights
            self.clear_container(self.actions_container)
            self.display_top_actions(insights['top_insights'])
            self.display_risk_summary(insights)
            self.display_market_context(insights['market_context'])
            
            # Update portfolio status
            risk_level = insights['portfolio_risk_level']
            risk_score = insights['portfolio_risk_score']
            status_text = f"Risk: {risk_level} ({risk_score:.1f}/10) | {insights['total_catalysts']} Catalysts"
            
            # Color code the status based on risk level
            if risk_level == 'HIGH':
                style = 'warning'
            elif risk_level == 'MEDIUM':
                style = 'accent'
            else:
                style = 'success'
            
            self.portfolio_status_label.config(text=status_text)
            
        except Exception as e:
            self.logger.error(f"Error loading morning brief content: {e}")
            self.display_error_state()
    
    def display_top_actions(self, insights: list):
        """Display the top 3 actionable insights"""
        if not insights:
            no_actions_label = create_themed_label(self.actions_container, 
                                                  "✅ No immediate actions required - portfolio looking stable", 
                                                  style='success')
            no_actions_label.grid(row=0, column=0, sticky='w', 
                                 padx=PADDING['large'], pady=PADDING['medium'])
            return
        
        for i, insight in enumerate(insights):
            # Create frame for this action
            action_frame = create_themed_frame(self.actions_container, style='panel')
            action_frame.grid(row=i, column=0, sticky='ew', 
                            padx=PADDING['small'], pady=PADDING['small'])
            action_frame.grid_columnconfigure(1, weight=1)
            
            # Priority indicator
            priority_color = self.get_priority_color(insight['priority'])
            priority_indicator = tk.Label(action_frame, text="●", 
                                        fg=priority_color, 
                                        font=("Arial", 14),
                                        bg=action_frame['bg'])
            priority_indicator.grid(row=0, column=0, padx=PADDING['small'], 
                                   pady=PADDING['small'], sticky='w')
            
            # Action text
            action_text = f"{i+1}. {insight['action']}"
            action_label = create_themed_label(action_frame, action_text, style='normal')
            action_label.grid(row=0, column=1, sticky='w', 
                            padx=PADDING['small'], pady=PADDING['small'])
            
            # Details line
            details = f"   {insight['ticker']} | Score: {insight['impact_score']:.1f} | Confidence: {insight['confidence']:.0%} | {insight['risk_level']} Risk"
            details_label = create_themed_label(action_frame, details, style='small')
            details_label.grid(row=1, column=1, sticky='w', 
                             padx=PADDING['small'], pady=(0, PADDING['small']))
            
            # Reasoning (if available)
            if insight.get('reasoning'):
                reasoning_text = f"   💡 {insight['reasoning']}"
                reasoning_label = create_themed_label(action_frame, reasoning_text, style='small')
                reasoning_label.grid(row=2, column=1, sticky='w', 
                                   padx=PADDING['small'], pady=(0, PADDING['small']))
    
    def display_risk_summary(self, insights: dict):
        """Display portfolio risk summary"""
        risk_level = insights['portfolio_risk_level']
        risk_score = insights['portfolio_risk_score']
        
        # Main risk indicator
        risk_text = f"Overall Portfolio Risk: {risk_level} ({risk_score:.1f}/10)"
        risk_style = self.get_risk_style(risk_level)
        
        main_risk_label = create_themed_label(self.risk_container, risk_text, style=risk_style)
        main_risk_label.grid(row=0, column=0, sticky='w', 
                           padx=PADDING['large'], pady=PADDING['small'])
        
        # High impact catalyst count
        high_impact_count = insights['high_impact_count']
        if high_impact_count > 0:
            impact_text = f"⚡ {high_impact_count} high-impact catalysts affecting your holdings"
            impact_label = create_themed_label(self.risk_container, impact_text, style='warning')
            impact_label.grid(row=1, column=0, sticky='w', 
                            padx=PADDING['large'], pady=PADDING['small'])
        
        # Total catalyst exposure
        total_catalysts = insights['total_catalysts']
        catalyst_text = f"📊 Monitoring {total_catalysts} total catalyst events"
        catalyst_label = create_themed_label(self.risk_container, catalyst_text, style='normal')
        catalyst_label.grid(row=2, column=0, sticky='w', 
                          padx=PADDING['large'], pady=PADDING['small'])
    
    def display_market_context(self, market_context: dict):
        """Display market context information"""
        market_sentiment = market_context.get('market_sentiment', 'NEUTRAL')
        technical_breadth = market_context.get('technical_breadth', 'NEUTRAL')
        
        # Market sentiment
        sentiment_text = f"Market Sentiment: {market_sentiment}"
        sentiment_style = self.get_sentiment_style(market_sentiment)
        sentiment_label = create_themed_label(self.market_container, sentiment_text, style=sentiment_style)
        sentiment_label.grid(row=0, column=0, sticky='w', 
                           padx=PADDING['large'], pady=PADDING['small'])
        
        # Technical breadth
        breadth_text = f"Technical Breadth: {technical_breadth}"
        breadth_style = self.get_sentiment_style(technical_breadth)
        breadth_label = create_themed_label(self.market_container, breadth_text, style=breadth_style)
        breadth_label.grid(row=1, column=0, sticky='w', 
                         padx=PADDING['large'], pady=PADDING['small'])
        
        # Additional context if available
        if 'sentiment_details' in market_context:
            details = market_context['sentiment_details']
            if sum(details.values()) > 0:
                context_text = f"News Analysis: {details.get('positive', 0)} positive, {details.get('negative', 0)} negative, {details.get('neutral', 0)} neutral"
                context_label = create_themed_label(self.market_container, context_text, style='small')
                context_label.grid(row=2, column=0, sticky='w', 
                                 padx=PADDING['large'], pady=PADDING['small'])
    
    def display_error_state(self):
        """Display error state for morning brief"""
        error_label = create_themed_label(self.actions_container, 
                                        "⚠️ Unable to generate insights - system initializing", 
                                        style='warning')
        error_label.grid(row=0, column=0, sticky='w', 
                        padx=PADDING['large'], pady=PADDING['medium'])
        
        retry_label = create_themed_label(self.actions_container, 
                                        "Please try refreshing in a moment", 
                                        style='normal')
        retry_label.grid(row=1, column=0, sticky='w', 
                        padx=PADDING['large'], pady=PADDING['small'])
    
    def clear_container(self, container):
        """Clear all widgets from a container"""
        for widget in container.winfo_children():
            widget.destroy()
    
    def get_priority_color(self, priority: str) -> str:
        """Get color for priority indicator"""
        colors = {
            'HIGH': '#ff4444',
            'MEDIUM': '#ffaa00', 
            'LOW': '#00aa00',
            'INFO': '#4488ff'
        }
        return colors.get(priority, '#888888')
    
    def get_risk_style(self, risk_level: str) -> str:
        """Get style for risk level"""
        styles = {
            'HIGH': 'warning',
            'MEDIUM': 'accent',
            'LOW': 'success',
            'UNKNOWN': 'normal'
        }
        return styles.get(risk_level, 'normal')
    
    def get_sentiment_style(self, sentiment: str) -> str:
        """Get style for sentiment display"""
        styles = {
            'BULLISH': 'success',
            'BEARISH': 'warning',
            'NEUTRAL': 'normal'
        }
        return styles.get(sentiment, 'normal')
    
    def get_portfolio_data(self) -> dict:
        """Get current portfolio data"""
        try:
            # Only use real portfolio data - no sample data for trading accuracy
            if hasattr(self, 'portfolio_loader') and self.portfolio_loader:
                return self.portfolio_loader.get_portfolio_data()
            return {}
        except Exception as e:
            self.logger.error(f"Error getting portfolio data: {e}")
            return {}
    
    def get_earnings_data(self) -> dict:
        """Get earnings calendar data"""
        try:
            # Only use real earnings data - no hardcoded dates for trading safety
            if hasattr(self, 'earnings_collector') and self.earnings_collector:
                # Get tickers from portfolio if available
                tickers = []
                if hasattr(self, 'portfolio_loader') and self.portfolio_loader:
                    try:
                        tickers = self.portfolio_loader.get_tickers()
                    except:
                        pass
                
                # If no portfolio tickers, use empty list (will return empty data)
                if tickers:
                    return self.earnings_collector.fetch_earnings_calendar(tickers)
                else:
                    self.logger.info("No portfolio tickers available for earnings calendar")
            return {}
        except Exception as e:
            self.logger.error(f"Error getting earnings data: {e}")
            return {}
    
    def get_news_data(self) -> list:
        """Get news feed data"""
        try:
            # This would normally come from your news collector
            return [
                {
                    'title': 'Market Analysis: Tech Sector Shows Strength',
                    'sentiment': 'positive',
                    'publishedAt': '2025-09-30'
                }
            ]
        except Exception as e:
            self.logger.error(f"Error getting news data: {e}")
            return []
    
    def get_technical_data(self) -> dict:
        """Get technical analysis data"""
        try:
            # Only use real technical data - no hardcoded analysis for trading safety
            if hasattr(self, 'technical_collector') and self.technical_collector:
                # Check if the method exists, otherwise return empty dict
                if hasattr(self.technical_collector, 'get_technical_analysis'):
                    return self.technical_collector.get_technical_analysis()
                else:
                    self.logger.warning("Technical collector missing get_technical_analysis method")
            return {}
        except Exception as e:
            self.logger.error(f"Error getting technical data: {e}")
            return {}
    
    def create_news_feed_panel(self):
        """Create the Schwab News Feed panel"""
        news_frame = create_themed_frame(self.content_frame, style='panel')
        news_frame.grid(row=1, column=0, sticky='ew', 
                       padx=PADDING['medium'], pady=PADDING['medium'])
        news_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header_frame = create_themed_frame(news_frame, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', 
                         padx=PADDING['small'], pady=PADDING['small'])
        header_frame.grid_columnconfigure(0, weight=1)
        
        header_label = create_themed_label(header_frame, 
                                          "📰 SCHWAB NEWS FEED (Last 24 Hours)", 
                                          style='subheader')
        header_label.grid(row=0, column=0, padx=PADDING['medium'], 
                         pady=PADDING['small'], sticky='w')
        
        # Status indicator
        self.news_status_label = create_themed_label(header_frame, 
                                                    "Loading news...", 
                                                    style='normal')
        self.news_status_label.grid(row=0, column=1, padx=PADDING['medium'], 
                                   pady=PADDING['small'], sticky='e')
        
        # News content frame (scrollable)
        self.news_content_frame = create_themed_frame(news_frame, style='panel')
        self.news_content_frame.grid(row=1, column=0, sticky='ew', 
                                    padx=PADDING['medium'], pady=PADDING['medium'])
        self.news_content_frame.grid_columnconfigure(0, weight=1)
        
        # Initially show loading message
        loading_label = create_themed_label(self.news_content_frame, 
                                          "Loading news feed from Schwab...", 
                                          style='normal')
        loading_label.grid(row=0, column=0, padx=PADDING['large'], 
                          pady=PADDING['large'])
    
    def create_technical_analysis_panel(self):
        """Create the Technical Analysis panel with fixed headers and perfectly aligned scrollable content"""
        technical_frame = create_themed_frame(self.content_frame, style='panel')
        technical_frame.grid(row=2, column=0, sticky='ew', 
                           padx=PADDING['medium'], pady=PADDING['medium'])
        technical_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header_frame = create_themed_frame(technical_frame, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', 
                         padx=PADDING['small'], pady=PADDING['small'])
        header_frame.grid_columnconfigure(0, weight=1)
        
        header_label = create_themed_label(header_frame, 
                                          "📊 TECHNICAL ANALYSIS (Portfolio Signals)", 
                                          style='subheader')
        header_label.grid(row=0, column=0, padx=PADDING['medium'], 
                         pady=PADDING['small'], sticky='w')
        
        # Status indicator
        self.technical_status_label = create_themed_label(header_frame, 
                                                         "Loading analysis...", 
                                                         style='normal')
        self.technical_status_label.grid(row=0, column=1, padx=PADDING['medium'], 
                                        pady=PADDING['small'], sticky='e')
        
        # Create a unified container for both headers and scrollable content
        content_container = create_themed_frame(technical_frame, style='panel')
        content_container.grid(row=1, column=0, sticky='ew', 
                              padx=PADDING['medium'], pady=(PADDING['medium'], PADDING['medium']))
        content_container.grid_columnconfigure(0, weight=1)
        
        # Configure shared column settings for perfect alignment
        headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
        column_weights = [1, 1, 1, 1, 2, 1]
        column_minsizes = [80, 70, 80, 60, 100, 80]
        
        # Fixed headers frame within the unified container
        self.headers_frame = create_themed_frame(content_container, style='panel')
        self.headers_frame.grid(row=0, column=0, sticky='ew', padx=0, pady=(0, 0))
        
        # Configure header columns
        for i, (weight, minsize) in enumerate(zip(column_weights, column_minsizes)):
            self.headers_frame.grid_columnconfigure(i, weight=weight, minsize=minsize)
        
        # Create fixed table headers
        for i, header in enumerate(headers):
            header_label = create_themed_label(self.headers_frame, header, style='highlight')
            header_label.grid(row=0, column=i, padx=PADDING['small'], 
                             pady=PADDING['small'], sticky='w')
        
        # Scrollable container frame within the unified container  
        scroll_frame = create_themed_frame(content_container, style='panel')
        scroll_frame.grid(row=1, column=0, sticky='ew', padx=0, pady=(0, 0))
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Create canvas and scrollbar
        self.technical_canvas = tk.Canvas(scroll_frame, 
                                        bg=GUI_COLORS['panel_bg'],
                                        highlightthickness=0,
                                        height=250)
        self.technical_scrollbar = ttk.Scrollbar(scroll_frame, 
                                               orient="vertical", 
                                               command=self.technical_canvas.yview)
        self.technical_canvas.configure(yscrollcommand=self.technical_scrollbar.set)
        
        # Grid canvas and scrollbar with no additional padding
        self.technical_canvas.grid(row=0, column=0, sticky='nsew')
        self.technical_scrollbar.grid(row=0, column=1, sticky='ns')
        
        # Content frame inside canvas
        self.technical_content_frame = create_themed_frame(self.technical_canvas, style='panel')
        self.technical_canvas_window = self.technical_canvas.create_window(
            0, 0, anchor='nw', window=self.technical_content_frame)
        
        # Configure content frame columns to EXACTLY match headers
        for i, (weight, minsize) in enumerate(zip(column_weights, column_minsizes)):
            self.technical_content_frame.grid_columnconfigure(i, weight=weight, minsize=minsize)
        
        # Initially show loading message
        loading_label = create_themed_label(self.technical_content_frame, 
                                          "Loading technical analysis...", 
                                          style='normal')
        loading_label.grid(row=0, column=0, columnspan=6, padx=PADDING['large'], 
                          pady=PADDING['large'])
        
        # Bind events for scrolling and resizing
        self.technical_content_frame.bind('<Configure>', self._on_technical_frame_configure)
        self.technical_canvas.bind('<Configure>', self._on_technical_canvas_configure)
        
        # Enhanced mouse wheel binding for responsive scrolling
        widgets_to_bind = [
            self.technical_canvas, scroll_frame, content_container, 
            technical_frame, self.headers_frame
        ]
        
        for widget in widgets_to_bind:
            widget.bind('<MouseWheel>', self._on_technical_mousewheel)
            widget.bind('<Enter>', lambda e, w=widget: w.focus_set())
        
        # Force alignment update after creation
        self.root.after(100, self._align_technical_columns)
        
        # Add debug alignment commands (can be called from console)
        self.root.after(200, self._setup_alignment_debug)
    
    def _setup_alignment_debug(self):
        """Setup alignment debugging - make app accessible globally"""
        try:
            # Make this window instance globally accessible for debugging
            import __main__
            __main__.app = self
            
            print("\n" + "="*50)
            print("🔧 HEADER ALIGNMENT DEBUG MODE READY")
            print("="*50)
            print("Data columns are perfect! Use these commands to adjust headers:")
            print()
            print("app.show_header_positions()           # See current header positions")
            print("app.adjust_header_only('Price', 5)    # Move Price header 5px right")
            print("app.adjust_header_only('RSI', -3)     # Move RSI header 3px left")
            print("app.reset_headers_only()              # Reset all headers")
            print("app.quick_header_adjustments()        # Show all commands")
            print()
            print("📋 Available columns: Ticker, Price, Change %, RSI, Signal, Momentum")
            print("=" * 50)
            
        except Exception as e:
            logging.error(f"Debug setup error: {e}")
    
    def _adjust_header_in_settings(self, header_name, pixels, display_label):
        """Adjust header from settings dialog and update display"""
        try:
            # Apply the adjustment
            success = self.adjust_header_only(header_name, pixels)
            
            if success:
                # Get the actual current offset from the header widget
                headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
                if header_name in headers:
                    column_index = headers.index(header_name)
                    
                    # Find the header widget to get its actual offset
                    header_widget = None
                    for child in self.headers_frame.winfo_children():
                        grid_info = child.grid_info()
                        if grid_info and int(grid_info.get('column', -1)) == column_index:
                            header_widget = child
                            break
                    
                    # Get the actual total offset from the widget
                    if header_widget and hasattr(header_widget, '_total_offset'):
                        current_offset = header_widget._total_offset
                    else:
                        current_offset = 0
                    
                    # Update the display label with actual offset
                    display_label.config(text=f"{current_offset:+d} px")
                    
                    # Visual feedback
                    original_color = display_label.cget('fg')
                    display_label.config(fg=GUI_COLORS['success'])
                    self.root.after(500, lambda: display_label.config(fg=original_color))
            else:
                # Error feedback
                original_color = display_label.cget('fg')
                display_label.config(fg=GUI_COLORS['danger'])
                self.root.after(1000, lambda: display_label.config(fg=original_color))
                
        except Exception as e:
            error_msg = f"Settings header adjustment error: {e}"
            logging.error(error_msg)
            self.update_status(error_msg)
    
    def get_header_offset(self, header_name):
        """Get current offset for a specific header"""
        try:
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            if header_name not in headers:
                return 0
                
            column_index = headers.index(header_name)
            
            # Find the header widget to get its current offset
            for child in self.headers_frame.winfo_children():
                grid_info = child.grid_info()
                if grid_info and int(grid_info.get('column', -1)) == column_index:
                    return getattr(child, '_total_offset', 0)
            
            return 0
        except Exception as e:
            logging.error(f"Error getting header offset for {header_name}: {e}")
            return 0
    
    def _reset_header_in_settings(self, header_name, display_label):
        """Reset specific header from settings dialog"""
        try:
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            if header_name in headers:
                column_index = headers.index(header_name)
                
                # Find the header widget
                header_widget = None
                for child in self.headers_frame.winfo_children():
                    grid_info = child.grid_info()
                    if grid_info and int(grid_info.get('column', -1)) == column_index:
                        header_widget = child
                        break
                
                if header_widget:
                    # Get current offset
                    current_offset = getattr(header_widget, '_total_offset', 0)
                    
                    if current_offset != 0:
                        # Reset the widget positioning
                        header_widget.place_forget()  # Remove any place positioning
                        header_widget._total_offset = 0
                        
                        # Restore to original grid position
                        if hasattr(header_widget, '_original_grid_info'):
                            original_info = header_widget._original_grid_info
                            header_widget.grid(**original_info)
                        else:
                            # Fallback to standard grid positioning
                            header_widget.grid(row=0, column=column_index, padx=PADDING['small'], sticky='w')
                        
                        # Update display
                        display_label.config(text="0 px")
                        self.update_status(f"Reset '{header_name}' header to original position")
            
        except Exception as e:
            logging.error(f"Settings header reset error: {e}")
            self.update_status(f"Error resetting {header_name} header")
    
    def _reset_all_headers_in_settings(self):
        """Reset all headers from settings dialog"""
        try:
            self.reset_headers_only()
            
            # Reset all offset tracking
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            for header in headers:
                setattr(self, f'_{header.lower().replace(" ", "_").replace("%", "pct")}_offset', 0)
            
            # Update all display labels if settings window is open
            self._update_current_header_positions()
            
        except Exception as e:
            logging.error(f"Settings reset all headers error: {e}")
    
    def _update_current_header_positions(self):
        """Update current header position tracking"""
        try:
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            for header in headers:
                # Initialize offset tracking if not exists
                attr_name = f'_{header.lower().replace(" ", "_").replace("%", "pct")}_offset'
                if not hasattr(self, attr_name):
                    setattr(self, attr_name, 0)
            
        except Exception as e:
            logging.error(f"Header position update error: {e}")
    
    def _debug_header_structure(self):
        """Debug method to check header frame structure"""
        try:
            debug_info = []
            debug_info.append("=== HEADER FRAME DEBUG ===")
            
            if hasattr(self, 'headers_frame'):
                debug_info.append(f"✅ headers_frame exists: {self.headers_frame}")
                
                children = self.headers_frame.winfo_children()
                debug_info.append(f"📊 Children count: {len(children)}")
                
                for i, child in enumerate(children):
                    grid_info = child.grid_info()
                    widget_text = getattr(child, 'cget', lambda x: 'N/A')('text') if hasattr(child, 'cget') else 'N/A'
                    debug_info.append(f"  Child {i}: {type(child).__name__}")
                    debug_info.append(f"    Text: '{widget_text}'")
                    debug_info.append(f"    Grid: {grid_info}")
                    debug_info.append("")
            else:
                debug_info.append("❌ headers_frame NOT FOUND")
            
            # Show debug info in a message box
            debug_text = "\n".join(debug_info)
            messagebox.showinfo("Header Frame Debug", debug_text)
            
            # Also update status
            self.update_status(f"Debug: Found {len(children) if hasattr(self, 'headers_frame') else 0} header children")
            
        except Exception as e:
            error_msg = f"Debug error: {e}"
            logging.error(error_msg)
            messagebox.showerror("Debug Error", error_msg)
    
    def update_technical_analysis_display(self):
        """Update the technical analysis panel with current data"""
        if not hasattr(self, 'technical_content_frame'):
            return
        
        # Clear existing data rows (all rows since headers are now separate)
        for widget in self.technical_content_frame.winfo_children():
            widget.destroy()
        
        # Get technical analysis data
        if hasattr(self, 'technical_collector') and self.technical_collector.technical_data:
            display_data = self.technical_collector.format_for_display(14)  # Show all tickers with scrolling
        else:
            display_data = []
        
        if display_data:
            # Display technical analysis data - start from row 0 since headers are separate
            for i, data in enumerate(display_data):
                # Ticker - column 0
                ticker_label = create_themed_label(self.technical_content_frame, 
                                                  data['ticker'], style='info')
                ticker_label.grid(row=i, column=0, padx=PADDING['small'], 
                                 pady=2, sticky='w')
                
                # Price - column 1
                price_text = f"${data['current_price']:.2f}" if data['current_price'] else "N/A"
                price_label = create_themed_label(self.technical_content_frame, 
                                                 price_text, style='normal')
                price_label.grid(row=i, column=1, padx=PADDING['small'], 
                                pady=2, sticky='w')
                
                # Change % - column 2
                change_pct = data['daily_change_pct']
                if change_pct is not None:
                    change_text = f"{change_pct:+.2f}%"
                    change_style = 'success' if change_pct > 0 else 'danger' if change_pct < 0 else 'normal'
                else:
                    change_text = "N/A"
                    change_style = 'normal'
                
                change_label = create_themed_label(self.technical_content_frame, 
                                                  change_text, style=change_style)
                change_label.grid(row=i, column=2, padx=PADDING['small'], 
                                 pady=2, sticky='w')
                
                # RSI - column 3
                rsi_value = data['rsi']
                if rsi_value is not None:
                    rsi_text = f"{rsi_value:.1f}"
                    # Color code RSI
                    if rsi_value >= 70:
                        rsi_style = 'danger'  # Overbought
                    elif rsi_value <= 30:
                        rsi_style = 'success'  # Oversold (potential buy)
                    else:
                        rsi_style = 'normal'
                else:
                    rsi_text = "N/A"
                    rsi_style = 'normal'
                
                rsi_label = create_themed_label(self.technical_content_frame, 
                                               rsi_text, style=rsi_style)
                rsi_label.grid(row=i, column=3, padx=PADDING['small'], 
                              pady=2, sticky='w')
                
                # Signal - column 4 (wider column)
                signal = data['primary_signal'].replace('_', ' ').title()
                if signal == 'No Signal':
                    signal = 'Neutral'
                signal_type = data['signal_type']
                signal_style = {'bullish': 'success', 'bearish': 'danger', 'neutral': 'normal'}.get(signal_type, 'normal')
                
                signal_label = create_themed_label(self.technical_content_frame, 
                                                  signal, style=signal_style)
                signal_label.grid(row=i, column=4, padx=PADDING['small'], 
                                 pady=2, sticky='w')
                
                # Momentum - column 5
                if 'momentum' in data and data['momentum']:
                    momentum_signal = data['momentum'].get('momentum_signal', 'neutral')
                    momentum_text = momentum_signal.replace('_', ' ').title()
                    momentum_style = {'strong_bullish': 'success', 'moderate_bullish': 'success',
                                    'strong_bearish': 'danger', 'moderate_bearish': 'danger',
                                    'neutral': 'normal'}.get(momentum_signal, 'normal')
                else:
                    momentum_text = "Neutral"
                    momentum_style = 'normal'
                
                momentum_label = create_themed_label(self.technical_content_frame, 
                                                    momentum_text, style=momentum_style)
                momentum_label.grid(row=i, column=5, padx=PADDING['small'], 
                                   pady=2, sticky='w')
                
                # Bind mouse wheel to each row for better scroll responsiveness
                for widget in [ticker_label, price_label, change_label, rsi_label, signal_label, momentum_label]:
                    widget.bind('<MouseWheel>', self._on_technical_mousewheel)
        else:
            # Show no data message
            no_data_label = create_themed_label(self.technical_content_frame, 
                                               "No technical analysis data available", 
                                               style='normal')
            no_data_label.grid(row=0, column=0, columnspan=6, padx=PADDING['large'], 
                              pady=PADDING['large'])
            no_data_label.bind('<MouseWheel>', self._on_technical_mousewheel)
    
    def create_impact_ranking_panel(self):
        """Create the Impact Ranking panel"""
        ranking_frame = create_themed_frame(self.content_frame, style='panel')
        ranking_frame.grid(row=3, column=0, sticky='ew', 
                          padx=PADDING['medium'], pady=PADDING['medium'])
        ranking_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header_frame = create_themed_frame(ranking_frame, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', 
                         padx=PADDING['small'], pady=PADDING['small'])
        header_frame.grid_columnconfigure(0, weight=1)
        
        header_label = create_themed_label(header_frame, 
                                          "📈 IMPACT RANKING (Next 7 Days)", 
                                          style='subheader')
        header_label.grid(row=0, column=0, padx=PADDING['medium'], 
                         pady=PADDING['small'], sticky='w')
        
        # Table headers
        table_frame = create_themed_frame(ranking_frame, style='panel')
        table_frame.grid(row=1, column=0, sticky='ew', 
                        padx=PADDING['medium'], pady=PADDING['medium'])
        table_frame.grid_columnconfigure(1, weight=1)
        
        headers = ["Priority", "Ticker", "Event Type", "Date/Time", "Impact Score"]
        for i, header in enumerate(headers):
            header_label = create_themed_label(table_frame, header, style='highlight')
            header_label.grid(row=0, column=i, padx=PADDING['small'], 
                             pady=PADDING['small'], sticky='w')
        
        # Store reference to ranking content frame for updates
        self.ranking_content_frame = table_frame
        
        # Initial data display (will be updated when data loads)
        self.update_impact_ranking_display()
    
    def update_impact_ranking_display(self):
        """Update the impact ranking panel with current data"""
        if not hasattr(self, 'ranking_content_frame'):
            return
        
        # Clear existing data rows (keep headers)
        for widget in self.ranking_content_frame.winfo_children():
            row = int(widget.grid_info()['row'])
            if row > 0:  # Keep header row (row 0)
                widget.destroy()
        
        try:
            # Import impact scorer and generate ranked events
            from analyzers.impact_scorer import CatalystImpactScorer
            from datetime import datetime, timedelta
            
            impact_scorer = CatalystImpactScorer()
            catalyst_events = []
            
            # Create sample events based on current portfolio data
            if hasattr(self, 'technical_data') and self.technical_data:
                for ticker, analysis in self.technical_data.items():
                    rsi_data = analysis.get('rsi', {})
                    if isinstance(rsi_data, dict):
                        rsi = rsi_data.get('rsi', 50)
                        if isinstance(rsi, (int, float)):
                            if rsi <= 30:
                                catalyst_events.append({
                                    'ticker': ticker,
                                    'type': 'oversold_signal',
                                    'date': datetime.now().strftime('%Y-%m-%d'),
                                    'description': f'{ticker} RSI oversold at {rsi:.1f}',
                                    'source': 'technical_analysis'
                                })
                            elif rsi >= 70:
                                catalyst_events.append({
                                    'ticker': ticker,
                                    'type': 'overbought_signal', 
                                    'date': datetime.now().strftime('%Y-%m-%d'),
                                    'description': f'{ticker} RSI overbought at {rsi:.1f}',
                                    'source': 'technical_analysis'
                                })
            
            # Real catalyst events only - no sample data for trading accuracy
            # Only use actual earnings calendar and news data from verified sources
            # Removed hardcoded SMCI and sample events that were showing fake dates
            
            # Score and rank events
            if catalyst_events and hasattr(self, 'portfolio_loader') and self.portfolio_loader:
                # Create portfolio data for scoring
                portfolio_tickers = self.portfolio_loader.get_tickers()
                portfolio_data = {ticker: {'value': 1000, 'shares': 10} for ticker in portfolio_tickers}
                
                scored_events = []
                for event in catalyst_events:
                    try:
                        score, breakdown = impact_scorer.calculate_impact_score(
                            event, portfolio_data, self.technical_data or {}
                        )
                        
                        priority = 'HIGH' if score >= 7.0 else 'MEDIUM' if score >= 4.0 else 'LOW'
                        scored_events.append({
                            'event': event,
                            'score': score,
                            'priority': priority,
                            'breakdown': breakdown
                        })
                    except Exception as e:
                        logging.debug(f"Error scoring event {event.get('ticker', 'Unknown')}: {e}")
                        continue
                
                # Sort by score (highest first)
                scored_events.sort(key=lambda x: x['score'], reverse=True)
                
                # Display top 5 events
                for i, scored_event in enumerate(scored_events[:5], 1):
                    event = scored_event['event']
                    priority = scored_event['priority']
                    score = scored_event['score']
                    
                    # Format date
                    event_date = datetime.strptime(event['date'], '%Y-%m-%d').strftime('%m/%d')
                    
                    # Style based on priority
                    priority_style = 'danger' if priority == 'HIGH' else 'warning' if priority == 'MEDIUM' else 'info'
                    
                    # Create row
                    create_themed_label(self.ranking_content_frame, priority, style=priority_style).grid(
                        row=i, column=0, padx=PADDING['small'], pady=2, sticky='w')
                    create_themed_label(self.ranking_content_frame, event['ticker'], style='normal').grid(
                        row=i, column=1, padx=PADDING['small'], pady=2, sticky='w')
                    create_themed_label(self.ranking_content_frame, event['type'], style='normal').grid(
                        row=i, column=2, padx=PADDING['small'], pady=2, sticky='w')
                    create_themed_label(self.ranking_content_frame, event_date, style='normal').grid(
                        row=i, column=3, padx=PADDING['small'], pady=2, sticky='w')
                    create_themed_label(self.ranking_content_frame, f"{score:.1f}/10", style='info').grid(
                        row=i, column=4, padx=PADDING['small'], pady=2, sticky='w')
                
                logging.info(f"Impact ranking updated with {len(scored_events)} events")
            
            else:
                # No data available
                create_themed_label(self.ranking_content_frame, "PENDING", style='warning').grid(
                    row=1, column=0, padx=PADDING['small'], pady=2, sticky='w')
                create_themed_label(self.ranking_content_frame, "Loading...", style='normal').grid(
                    row=1, column=1, padx=PADDING['small'], pady=2, sticky='w')
                create_themed_label(self.ranking_content_frame, "System initialization", style='normal').grid(
                    row=1, column=2, padx=PADDING['small'], pady=2, sticky='w')
                create_themed_label(self.ranking_content_frame, "Now", style='normal').grid(
                    row=1, column=3, padx=PADDING['small'], pady=2, sticky='w')
                create_themed_label(self.ranking_content_frame, "N/A", style='info').grid(
                    row=1, column=4, padx=PADDING['small'], pady=2, sticky='w')
                    
        except Exception as e:
            logging.error(f"Error updating impact ranking display: {e}")
            # Show error state
            create_themed_label(self.ranking_content_frame, "ERROR", style='danger').grid(
                row=1, column=0, padx=PADDING['small'], pady=2, sticky='w')
            create_themed_label(self.ranking_content_frame, "System", style='normal').grid(
                row=1, column=1, padx=PADDING['small'], pady=2, sticky='w')
            create_themed_label(self.ranking_content_frame, "Data loading error", style='normal').grid(
                row=1, column=2, padx=PADDING['small'], pady=2, sticky='w')
            create_themed_label(self.ranking_content_frame, "Now", style='normal').grid(
                row=1, column=3, padx=PADDING['small'], pady=2, sticky='w')
            create_themed_label(self.ranking_content_frame, "0/10", style='danger').grid(
                row=1, column=4, padx=PADDING['small'], pady=2, sticky='w')
    
    def create_earnings_calendar_panel(self):
        """Create the Earnings Calendar panel"""
        calendar_frame = create_themed_frame(self.content_frame, style='panel')
        calendar_frame.grid(row=4, column=0, sticky='ew', 
                           padx=PADDING['medium'], pady=PADDING['medium'])
        calendar_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header_frame = create_themed_frame(calendar_frame, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', 
                         padx=PADDING['small'], pady=PADDING['small'])
        header_frame.grid_columnconfigure(0, weight=1)
        
        header_label = create_themed_label(header_frame, 
                                          "📅 EARNINGS CALENDAR (Your Holdings)", 
                                          style='subheader')
        header_label.grid(row=0, column=0, padx=PADDING['medium'], 
                         pady=PADDING['small'], sticky='w')
        
        # Calendar content
        content_frame = create_themed_frame(calendar_frame, style='panel')
        content_frame.grid(row=1, column=0, sticky='ew', 
                          padx=PADDING['medium'], pady=PADDING['medium'])
        
        # Store reference to earnings content frame for updates
        self.earnings_content_frame = content_frame
        
        # Initial earnings data (will be updated when data loads)
        self.update_earnings_calendar_display()
    
    def update_earnings_calendar_display(self):
        """Update the earnings calendar panel with current data"""
        if not hasattr(self, 'earnings_content_frame'):
            return
        
        # Clear existing widgets
        for widget in self.earnings_content_frame.winfo_children():
            widget.destroy()
        
        # Get upcoming earnings
        if hasattr(self, 'earnings_collector'):
            upcoming_earnings = self.earnings_collector.format_earnings_for_display(5)
        else:
            upcoming_earnings = []
        
        if upcoming_earnings:
            # Display upcoming earnings
            for i, event in enumerate(upcoming_earnings):
                # Date and ticker
                event_text = f"{event['date_display']}: {event['ticker']} ({event['time_display']})"
                
                # Color based on impact level
                if event['impact_level'] == 'HIGH':
                    style = 'danger'
                elif event['impact_level'] == 'MEDIUM':
                    style = 'warning'
                else:
                    style = 'normal'
                
                event_label = create_themed_label(self.earnings_content_frame, event_text, style=style)
                event_label.grid(row=i, column=0, sticky='w', 
                               padx=PADDING['large'], pady=PADDING['small'])
        else:
            # No earnings found
            no_earnings_label = create_themed_label(
                self.earnings_content_frame, 
                "No earnings scheduled in next 7 days", 
                style='normal'
            )
            no_earnings_label.grid(row=0, column=0, sticky='w', 
                                 padx=PADDING['large'], pady=PADDING['medium'])
    
    def create_opportunity_panel(self):
        """Create the Opportunity Scanner panel"""
        opportunity_frame = create_themed_frame(self.content_frame, style='panel')
        opportunity_frame.grid(row=4, column=0, sticky='ew', 
                              padx=PADDING['medium'], pady=PADDING['medium'])
        opportunity_frame.grid_columnconfigure(0, weight=1)
        
        # Panel header
        header_frame = create_themed_frame(opportunity_frame, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', 
                         padx=PADDING['small'], pady=PADDING['small'])
        header_frame.grid_columnconfigure(0, weight=1)
        
        header_label = create_themed_label(header_frame, 
                                          "🔍 OPPORTUNITY SCANNER", 
                                          style='subheader')
        header_label.grid(row=0, column=0, padx=PADDING['medium'], 
                         pady=PADDING['small'], sticky='w')
        
        # Opportunity content frame
        content_frame = create_themed_frame(opportunity_frame, style='panel')
        content_frame.grid(row=1, column=0, sticky='ew', 
                          padx=PADDING['medium'], pady=PADDING['medium'])
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Store reference for updates
        self.opportunity_content_frame = content_frame
        
        # Initial display
        self.update_opportunity_display()
    
    def update_opportunity_display(self):
        """Update the opportunity scanner panel with current opportunities"""
        if not hasattr(self, 'opportunity_content_frame'):
            return
        
        # Clear existing content
        for widget in self.opportunity_content_frame.winfo_children():
            widget.destroy()
        
        try:
            # Import opportunity scanner
            from analyzers.opportunity_scanner import OpportunityScanner
            
            scanner = OpportunityScanner()
            
            # Gather data for opportunity scanning
            if hasattr(self, 'portfolio_loader') and self.portfolio_loader and hasattr(self, 'technical_data'):
                # Get portfolio data
                portfolio_tickers = self.portfolio_loader.get_tickers()
                portfolio_data = {ticker: {'value': 1000, 'shares': 10} for ticker in portfolio_tickers}
                
                # Use real catalyst events only - no hardcoded data for trading safety
                catalyst_events = []
                
                # TODO: Connect to real earnings calendar API
                # real_catalyst_events = self.earnings_collector.get_upcoming_events() if hasattr(self, 'earnings_collector') else []
                # catalyst_events.extend(real_catalyst_events)
                
                # Scan for opportunities
                opportunities = scanner.scan_opportunities(
                    portfolio_data, 
                    self.technical_data or {}, 
                    catalyst_events
                )
                
                if opportunities:
                    # Display header
                    header_text = f"🎯 Found {len(opportunities)} High-Quality Opportunities"
                    header_label = create_themed_label(self.opportunity_content_frame, header_text, style='highlight')
                    header_label.grid(row=0, column=0, sticky='w', padx=PADDING['large'], pady=PADDING['small'])
                    
                    # Display opportunities
                    for i, opp in enumerate(opportunities[:5], 1):  # Show top 5
                        self._create_opportunity_widget(opp, i)
                    
                    logging.info(f"Opportunity scanner updated with {len(opportunities)} opportunities")
                else:
                    # No opportunities found
                    no_opp_label = create_themed_label(self.opportunity_content_frame, 
                                                     "📊 No high-quality opportunities identified at this time", 
                                                     style='normal')
                    no_opp_label.grid(row=0, column=0, padx=PADDING['large'], pady=PADDING['medium'])
                    
                    status_label = create_themed_label(self.opportunity_content_frame, 
                                                     "🔄 Continue monitoring for catalyst-driven setups", 
                                                     style='info')
                    status_label.grid(row=1, column=0, padx=PADDING['large'], pady=PADDING['small'])
            
            else:
                # Portfolio/technical data not loaded yet
                loading_label = create_themed_label(self.opportunity_content_frame, 
                                                   "⏳ Opportunity scanner will activate once portfolio and technical data are loaded", 
                                                   style='info')
                loading_label.grid(row=0, column=0, padx=PADDING['large'], pady=PADDING['medium'])
                
                status_label = create_themed_label(self.opportunity_content_frame, 
                                                 "📈 Load portfolio data to begin scanning for opportunities", 
                                                 style='normal')
                status_label.grid(row=1, column=0, padx=PADDING['large'], pady=PADDING['small'])
        
        except Exception as e:
            logging.error(f"Error updating opportunity display: {e}")
            # Show error state
            error_label = create_themed_label(self.opportunity_content_frame, 
                                            "❌ Error loading opportunity scanner", 
                                            style='danger')
            error_label.grid(row=0, column=0, padx=PADDING['large'], pady=PADDING['medium'])
    
    def _create_opportunity_widget(self, opportunity: Dict, index: int):
        """Create a widget for displaying an individual opportunity"""
        try:
            # Create opportunity frame
            opp_frame = create_themed_frame(self.opportunity_content_frame, style='panel')
            opp_frame.grid(row=index, column=0, sticky='ew', 
                          padx=PADDING['small'], pady=PADDING['small'])
            opp_frame.grid_columnconfigure(1, weight=1)
            
            # Opportunity score indicator
            score = opportunity.get('opportunity_score', 0)
            risk_level = opportunity.get('risk_level', 'MEDIUM')
            
            # Score color based on value
            if score >= 8.0:
                score_style = 'success'
                score_icon = "🔥"
            elif score >= 6.5:
                score_style = 'warning'
                score_icon = "⚡"
            else:
                score_style = 'info'
                score_icon = "📊"
            
            # Score label
            score_text = f"{score_icon} {score:.1f}"
            score_label = create_themed_label(opp_frame, score_text, style=score_style)
            score_label.grid(row=0, column=0, padx=PADDING['small'], pady=PADDING['small'], sticky='w')
            
            # Main opportunity text
            ticker = opportunity.get('ticker', 'N/A')
            setup = opportunity.get('setup', 'Setup')
            main_text = f"{ticker} - {setup}"
            main_label = create_themed_label(opp_frame, main_text, style='normal')
            main_label.grid(row=0, column=1, sticky='w', padx=PADDING['small'], pady=PADDING['small'])
            
            # Risk indicator
            risk_color = 'danger' if risk_level == 'HIGH' else 'warning' if risk_level == 'MEDIUM' else 'success'
            risk_label = create_themed_label(opp_frame, f"{risk_level} RISK", style=risk_color)
            risk_label.grid(row=0, column=2, padx=PADDING['small'], pady=PADDING['small'], sticky='e')
            
            # Description
            description = opportunity.get('description', 'No description available')
            desc_label = create_themed_label(opp_frame, f"💡 {description}", style='small')
            desc_label.grid(row=1, column=1, columnspan=2, sticky='w', 
                           padx=PADDING['small'], pady=(0, PADDING['small']))
            
            # Timeframe and entry reason
            timeframe = opportunity.get('timeframe', 'Unknown timeframe')
            entry_reason = opportunity.get('entry_reason', 'Entry criteria')
            details_text = f"⏰ {timeframe} | 🎯 {entry_reason}"
            details_label = create_themed_label(opp_frame, details_text, style='small')
            details_label.grid(row=2, column=1, columnspan=2, sticky='w', 
                              padx=PADDING['small'], pady=(0, PADDING['small']))
        
        except Exception as e:
            logging.debug(f"Error creating opportunity widget: {e}")
    
    def create_status_bar(self, parent):
        """Create the status bar"""
        status_frame = create_themed_frame(parent, style='accent')
        status_frame.grid(row=2, column=0, sticky='ew', pady=(PADDING['medium'], 0))
        status_frame.grid_columnconfigure(0, weight=1)
        
        self.status_label = create_themed_label(status_frame, 
                                               "Status: Catalyst Scanner initialized - Ready to load portfolio data",
                                               style='normal')
        self.status_label.grid(row=0, column=0, padx=PADDING['medium'], 
                              pady=PADDING['small'], sticky='w')
    
    def on_content_configure(self, event):
        """Handle content frame configuration"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def on_canvas_configure(self, event):
        """Handle canvas configuration"""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
    
    # Menu and button callbacks
    def open_portfolio(self):
        """Open portfolio file"""
        messagebox.showinfo("Portfolio", "Portfolio loading functionality will be implemented in Phase 1")
        self.update_status("Portfolio loading functionality coming soon...")
    
    def open_settings(self):
        """Open comprehensive settings dialog"""
        try:
            show_settings_dialog(self.root, self.auto_refresh_manager, self.alert_system, self)
        except Exception as e:
            logging.error(f"Error opening settings dialog: {e}")
            messagebox.showerror("Error", f"Could not open settings: {e}")
    
    def open_monitoring_service(self):
        """Open the monitoring service management dialog"""
        try:
            show_monitoring_service_dialog(self.root)
        except Exception as e:
            logging.error(f"Error opening monitoring service dialog: {e}")
            messagebox.showerror("Error", f"Could not open monitoring service dialog: {e}")
    
    def refresh_data(self):
        """Refresh all data and check for alerts"""
        # Store old technical data for comparison
        old_technical_data = self.technical_data.copy() if hasattr(self, 'technical_data') else {}
        
        # Update timestamp and refresh all data
        self.update_last_update_time()
        self.load_portfolio_data()
        self.load_earnings_calendar()
        self.load_news_feed()
        self.load_technical_analysis()
        
        # Check for alerts if alert system is available
        if hasattr(self, 'alert_system') and self.alert_system:
            try:
                self.check_for_alerts(old_technical_data, self.technical_data)
            except Exception as e:
                logging.error(f"Error checking alerts: {e}")
        
        self.update_status("Data refreshed successfully")
        # Only show messagebox if refresh was triggered manually (not auto-refresh)
        if not getattr(self, '_auto_refresh_in_progress', False):
            messagebox.showinfo("Refresh", "Data refresh completed!")
    
    def check_for_alerts(self, old_data: dict, new_data: dict):
        """Check for alert conditions and trigger alerts"""
        try:
            if not old_data or not new_data:
                return
            
            # Check each ticker for changes
            for ticker in new_data:
                if ticker not in old_data:
                    continue
                
                old_ticker_data = old_data[ticker]
                new_ticker_data = new_data[ticker]
                
                # Check for RSI extreme conditions
                if 'rsi' in new_ticker_data:
                    rsi = new_ticker_data['rsi']
                    if isinstance(rsi, (int, float)):
                        self.alert_system.check_rsi_extreme(ticker, rsi)
                
                # Check for signal changes
                old_signal = old_ticker_data.get('signal', '')
                new_signal = new_ticker_data.get('signal', '')
                if old_signal and new_signal and old_signal != new_signal:
                    self.alert_system.trigger_signal_change_alert(ticker, old_signal, new_signal)
                
                # Check for momentum changes
                old_momentum = old_ticker_data.get('momentum', '')
                new_momentum = new_ticker_data.get('momentum', '')
                if old_momentum and new_momentum and old_momentum != new_momentum:
                    self.alert_system.trigger_momentum_change_alert(ticker, old_momentum, new_momentum)
                
        except Exception as e:
            logging.error(f"Error in check_for_alerts: {e}")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        current_state = self.root.attributes('-fullscreen')
        self.root.attributes('-fullscreen', not current_state)
        self.update_status(f"Fullscreen: {'On' if not current_state else 'Off'}")
    
    def open_live_dashboard(self):
        """Open Phase 4 Live Dashboard"""
        try:
            if self.app_instance and hasattr(self.app_instance, 'show_live_dashboard'):
                self.app_instance.show_live_dashboard()
            else:
                messagebox.showinfo(
                    "Live Dashboard",
                    "Live Dashboard is a Phase 4 feature.\n\n"
                    "This advanced real-time monitoring system includes:\n"
                    "• Real-time catalyst scoring\n"
                    "• Portfolio impact analysis\n"
                    "• Performance tracking\n"
                    "• Risk monitoring\n\n"
                    "Please ensure Phase 4 integration is complete."
                )
        except Exception as e:
            logging.error(f"Error opening live dashboard: {e}")
            messagebox.showerror(
                "Error",
                f"Failed to open Live Dashboard: {e}\n\n"
                "Please check the logs for more details."
            )
    
    def show_about(self):
        """Show about dialog"""
        about_text = """Catalyst Scanner v1.0 - Phase 4 Integrated
        
Investment Catalyst Tracking Application

Core Features:
• Morning Brief - Daily catalyst summary
• Impact Ranking - Events ranked by portfolio impact
• Earnings Calendar - Upcoming earnings for your holdings
• Opportunity Scanner - Catalyst-driven entry points

Phase 4 Advanced Features:
• 🔴 Live Dashboard - Real-time catalyst monitoring
• ⚡ Real-time Market Data - Live price and volume streaming
• 🎯 ML-Enhanced Scoring - AI-powered catalyst analysis
• 📊 Portfolio Impact Assessment - Real-time P&L tracking
• 📈 Performance Tracking - Prediction accuracy monitoring
• ⚠️ Risk Monitoring - Advanced portfolio risk analysis

Designed for accessibility with:
• Arial 12+ fonts for easy reading
• High-contrast colors
• Large, clear interface elements

Phase 4 Integration - October 2025"""
        
        messagebox.showinfo("About Catalyst Scanner", about_text)
    
    def on_window_close(self):
        """Handle window close event with proper cleanup"""
        try:
            # Stop auto-refresh
            if hasattr(self, 'auto_refresh_manager') and self.auto_refresh_manager:
                self.auto_refresh_manager.stop_auto_refresh()
                logging.info("Auto-refresh stopped")
            
            # Save current header positions
            self.save_header_positions()
            
            # Destroy the window
            self.root.destroy()
            
        except Exception as e:
            logging.error(f"Error during window close: {e}")
            self.root.destroy()
    
    def auto_refresh_callback(self):
        """Callback for auto-refresh system"""
        try:
            # Set flag to prevent showing messagebox during auto-refresh
            self._auto_refresh_in_progress = True
            
            # Refresh data
            self.refresh_data()
            
            logging.info("Auto-refresh completed successfully")
            
        except Exception as e:
            logging.error(f"Error during auto-refresh: {e}")
        finally:
            # Clear the flag
            self._auto_refresh_in_progress = False
    
    def update_status(self, message):
        """Update the status bar"""
        self.status_label.config(text=f"Status: {message}")
        self.root.update_idletasks()
        logging.info(f"Status updated: {message}")
    
    def _format_last_update(self):
        """Format the last update timestamp for display"""
        return f"Last Update: {self.last_update_time.strftime('%I:%M:%S %p')}"
    
    def update_last_update_time(self):
        """Update the last update timestamp and refresh the display"""
        self.last_update_time = datetime.now()
        if self.last_update_label:
            self.last_update_label.config(text=self._format_last_update())
        logging.info(f"Last update time refreshed: {self.last_update_time}")
    
    def save_header_positions(self):
        """Save current header positions to config file"""
        try:
            import json
            import os
            
            # Create config directory if it doesn't exist
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, 'header_positions.json')
            
            # Collect current header positions
            header_positions = {}
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            
            if hasattr(self, 'headers_frame'):
                for child in self.headers_frame.winfo_children():
                    try:
                        widget_text = child.cget('text') if hasattr(child, 'cget') else ''
                        if widget_text in headers and hasattr(child, '_total_offset'):
                            header_positions[widget_text] = child._total_offset
                            print(f"DEBUG: Saving {widget_text} offset: {child._total_offset}")
                    except:
                        continue
            
            # Save to file
            with open(config_file, 'w') as f:
                json.dump(header_positions, f, indent=2)
            
            print(f"DEBUG: Saved header positions to {config_file}")
            return True
            
        except Exception as e:
            logging.error(f"Error saving header positions: {e}")
            return False
    
    def load_header_positions(self):
        """Load header positions from config file and apply them"""
        try:
            import json
            import os
            
            config_dir = os.path.dirname(os.path.abspath(__file__))
            config_file = os.path.join(config_dir, 'header_positions.json')
            
            if not os.path.exists(config_file):
                print("DEBUG: No header positions config file found")
                return False
            
            # Load positions from file
            with open(config_file, 'r') as f:
                header_positions = json.load(f)
            
            print(f"DEBUG: Loaded header positions: {header_positions}")
            
            # Apply positions after a short delay to ensure UI is ready
            self.root.after(100, lambda: self._apply_saved_positions(header_positions))
            return True
            
        except Exception as e:
            logging.error(f"Error loading header positions: {e}")
            return False
    
    def _apply_saved_positions(self, header_positions):
        """Apply saved header positions to widgets"""
        try:
            if not hasattr(self, 'headers_frame') or not header_positions:
                return
            
            for header_name, offset in header_positions.items():
                if offset != 0:  # Only apply non-zero offsets
                    print(f"DEBUG: Applying saved offset for {header_name}: {offset}")
                    # Apply the offset using the existing adjustment method
                    self.adjust_header_only(header_name, offset)
            
            self.update_status(f"Restored header positions for {len(header_positions)} headers")
            
        except Exception as e:
            logging.error(f"Error applying saved header positions: {e}")
    
    def load_portfolio_data(self):
        """Load portfolio data from Excel file"""
        try:
            self.portfolio_loader = load_user_portfolio()
            
            if self.portfolio_loader.is_portfolio_loaded():
                tickers = self.portfolio_loader.get_tickers()
                summary = self.portfolio_loader.get_portfolio_summary()
                
                status_msg = f"Portfolio loaded: {len(tickers)} tickers"
                self.update_portfolio_status(status_msg, "success")
                
                logging.info(f"Portfolio loaded successfully: {len(tickers)} tickers")
                logging.info(f"Tickers: {tickers}")
                
                # Update the brief panel with portfolio info
                self.update_portfolio_display(tickers, summary)
                
            else:
                self.update_portfolio_status("Portfolio not loaded", "warning")
                logging.warning("Portfolio could not be loaded")
                
        except Exception as e:
            error_msg = f"Portfolio loading error: {str(e)}"
            self.update_portfolio_status(error_msg, "error")
            logging.error(f"Portfolio loading failed: {e}")
    
    def update_portfolio_status(self, message: str, level: str = "info"):
        """Update portfolio status display"""
        if self.portfolio_status_label:
            color_map = {
                "success": GUI_COLORS['success'],
                "warning": GUI_COLORS['warning'],
                "error": GUI_COLORS['danger'],
                "info": GUI_COLORS['info']
            }
            
            color = color_map.get(level, GUI_COLORS['text_primary'])
            self.portfolio_status_label.config(text=message, fg=color)
    
    def update_portfolio_display(self, tickers: list, summary: dict):
        """Update the portfolio information in the GUI panels"""
        # This will be expanded when we add more detailed panels
        ticker_count = len(tickers)
        ticker_list = ', '.join(tickers[:5])  # Show first 5 tickers
        
        if ticker_count > 5:
            ticker_list += f" (+{ticker_count - 5} more)"
        
        portfolio_info = f"Tracking {ticker_count} tickers: {ticker_list}"
        self.update_status(portfolio_info)
    
    def load_earnings_calendar(self):
        """Load earnings calendar data for portfolio tickers"""
        try:
            if self.portfolio_loader and self.portfolio_loader.is_portfolio_loaded():
                tickers = self.portfolio_loader.get_tickers()
                
                # Fetch earnings calendar
                earnings_data = self.earnings_collector.fetch_earnings_calendar(tickers, days_ahead=7)
                self.earnings_data = earnings_data
                
                # Get upcoming earnings for display
                upcoming_earnings = self.earnings_collector.format_earnings_for_display(5)
                
                # Update earnings panel
                self.update_earnings_display(upcoming_earnings)
                
                logging.info(f"Earnings calendar loaded for {len(tickers)} tickers")
                
            else:
                logging.warning("Cannot load earnings calendar - portfolio not loaded")
                
        except Exception as e:
            logging.error(f"Earnings calendar loading failed: {e}")
    
    def update_earnings_display(self, upcoming_earnings: list):
        """Update the earnings calendar display"""
        # Update the earnings calendar panel
        self.update_earnings_calendar_display()
        
        # Update status with earnings summary
        if upcoming_earnings:
            earnings_summary = f"Next earnings: {upcoming_earnings[0]['ticker']} on {upcoming_earnings[0]['date_display']}"
        else:
            earnings_summary = "No earnings scheduled in next 7 days"
        
        logging.info(f"Earnings summary: {earnings_summary}")
    
    def load_news_feed(self):
        """Load Schwab news feed for portfolio tickers"""
        try:
            if self.portfolio_loader and self.portfolio_loader.is_portfolio_loaded():
                tickers = self.portfolio_loader.get_tickers()
                
                # Check authentication status
                auth_status = self.auth_manager.get_auth_status()
                if not auth_status.get('schwab', False):
                    logging.warning("Schwab authentication not available - news feed disabled")
                    self.update_news_status("⚠️ Auth required")
                    return
                
                # Fetch news feed for portfolio tickers
                self.news_data = self.news_collector.get_news_for_portfolio(tickers, hours_back=24)
                
                # Format news for display
                formatted_news = self._format_news_for_display(5)
                
                # Update news panel
                self.update_news_display(formatted_news)
                
                logging.info(f"News feed loaded: {len(self.news_data)} articles for {len(tickers)} tickers")
                
            else:
                logging.warning("Cannot load news feed - portfolio not loaded")
                
        except Exception as e:
            logging.error(f"News feed loading failed: {e}")
            self.update_news_status("❌ Load failed")
    
    def load_technical_analysis(self):
        """Load technical analysis for portfolio tickers"""
        try:
            if self.portfolio_loader and self.portfolio_loader.is_portfolio_loaded():
                tickers = self.portfolio_loader.get_tickers()
                
                # Analyze technical indicators for portfolio
                self.technical_data = self.technical_collector.analyze_portfolio_technicals(tickers)
                
                # Update technical analysis display
                self.update_technical_analysis_display()
                
                # Update impact ranking with new technical data
                self.update_impact_ranking_display()
                
                # Update opportunity scanner with new technical data
                self.update_opportunity_display()
                
                # Update status
                analyzed_count = len(self.technical_data)
                self.update_technical_status(f"✅ {analyzed_count} analyzed")
                
                logging.info(f"Technical analysis loaded: {analyzed_count} tickers analyzed")
                
            else:
                logging.warning("Cannot load technical analysis - portfolio not loaded")
                self.update_technical_status("⚠️ Portfolio required")
                
        except Exception as e:
            logging.error(f"Technical analysis loading failed: {e}")
            self.update_technical_status("❌ Load failed")
    
    def update_technical_status(self, status_text: str):
        """Update technical analysis status label"""
        if hasattr(self, 'technical_status_label'):
            self.technical_status_label.config(text=status_text)
    
    def update_news_display(self, news_articles: list):
        """Update the news feed display panel"""
        try:
            # Clear existing content
            for widget in self.news_content_frame.winfo_children():
                widget.destroy()
            
            if not news_articles:
                # Show no news message
                no_news_label = create_themed_label(self.news_content_frame, 
                                                   "📰 No recent news found for your portfolio tickers", 
                                                   style='normal')
                no_news_label.grid(row=0, column=0, padx=PADDING['large'], 
                                  pady=PADDING['large'])
                self.update_news_status("✅ No news")
                return
            
            # Display news articles
            for i, article in enumerate(news_articles):
                self._create_news_article_widget(article, i)
            
            # Update status
            total_articles = len(self.news_data) if self.news_data else 0
            self.update_news_status(f"✅ {total_articles} articles")
            
        except Exception as e:
            logging.error(f"News display update failed: {e}")
            self.update_news_status("❌ Display error")
    
    def _create_news_article_widget(self, article: dict, row: int):
        """Create a widget for displaying a single news article"""
        try:
            # Article container frame
            article_frame = create_themed_frame(self.news_content_frame, style='normal')
            article_frame.grid(row=row, column=0, sticky='ew', 
                              padx=PADDING['small'], pady=PADDING['small'])
            article_frame.grid_columnconfigure(1, weight=1)
            
            # Impact level indicator
            impact_level = article.get('impact_score', 0)
            if impact_level >= 8:
                impact_style = 'danger'
                impact_text = 'HIGH'
            elif impact_level >= 6:
                impact_style = 'warning'
                impact_text = 'MED'
            else:
                impact_style = 'success'
                impact_text = 'LOW'
            
            impact_label = create_themed_label(article_frame, impact_text, style=impact_style)
            impact_label.grid(row=0, column=0, padx=PADDING['small'], pady=PADDING['small'], sticky='w')
            
            # Ticker label
            ticker = article.get('ticker', 'N/A')
            ticker_label = create_themed_label(article_frame, ticker, style='highlight')
            ticker_label.grid(row=0, column=1, padx=PADDING['small'], pady=PADDING['small'], sticky='w')
            
            # Sentiment indicator
            sentiment = article.get('sentiment', 'neutral')
            sentiment_color = {
                'bullish': 'success',
                'bearish': 'danger', 
                'neutral': 'normal'
            }.get(sentiment, 'normal')
            
            sentiment_symbol = {
                'bullish': '📈',
                'bearish': '📉',
                'neutral': '➖'
            }.get(sentiment, '➖')
            
            sentiment_label = create_themed_label(article_frame, sentiment_symbol, style=sentiment_color)
            sentiment_label.grid(row=0, column=2, padx=PADDING['small'], pady=PADDING['small'], sticky='w')
            
            # Catalyst type
            catalyst_type = article.get('catalyst_type', 'general')
            catalyst_label = create_themed_label(article_frame, catalyst_type.upper(), style='info')
            catalyst_label.grid(row=0, column=3, padx=PADDING['small'], pady=PADDING['small'], sticky='w')
            
            # Timestamp
            timestamp = article.get('timestamp', 'Unknown')
            time_label = create_themed_label(article_frame, timestamp, style='normal')
            time_label.grid(row=0, column=4, padx=PADDING['small'], pady=PADDING['small'], sticky='e')
            
            # Headline (wrapped)
            headline = article.get('headline', 'No headline')
            if len(headline) > 100:
                headline = headline[:97] + "..."
            
            headline_label = create_themed_label(article_frame, headline, style='normal')
            headline_label.grid(row=1, column=0, columnspan=5, sticky='ew', 
                               padx=PADDING['medium'], pady=(0, PADDING['small']))
            
        except Exception as e:
            logging.error(f"Failed to create news article widget: {e}")
    
    def _format_news_for_display(self, max_articles: int = 5) -> list:
        """Format news articles for GUI display"""
        try:
            if not self.news_data:
                return []
            
            # Sort by impact score and timestamp
            sorted_articles = sorted(self.news_data, 
                                   key=lambda x: (x.get('impact_score', 0), x.get('timestamp', '')), 
                                   reverse=True)
            
            return sorted_articles[:max_articles]
            
        except Exception as e:
            logging.error(f"News formatting failed: {e}")
            return []
    
    def update_news_status(self, status_text: str):
        """Update the news feed status label"""
        if hasattr(self, 'news_status_label') and self.news_status_label:
            self.news_status_label.config(text=status_text)
    
    def _on_technical_frame_configure(self, event):
        """Handle technical analysis frame resize to update scrollbar"""
        try:
            # Update the scroll region to encompass the inner frame
            self.technical_canvas.configure(scrollregion=self.technical_canvas.bbox("all"))
        except Exception as e:
            logging.error(f"Technical frame configure error: {e}")
    
    def _on_technical_canvas_configure(self, event):
        """Handle canvas resize to update inner frame width and maintain alignment"""
        try:
            # Update the canvas window width to match canvas width exactly
            canvas_width = event.width
            
            # Account for scrollbar width to prevent horizontal scrolling
            scrollbar_width = self.technical_scrollbar.winfo_reqwidth() if hasattr(self, 'technical_scrollbar') else 20
            content_width = canvas_width - scrollbar_width
            
            # Update the content frame width to match available space
            self.technical_canvas.itemconfig(self.technical_canvas_window, width=content_width)
            
            # Force update of the scroll region
            self.technical_canvas.update_idletasks()
            self.technical_canvas.configure(scrollregion=self.technical_canvas.bbox("all"))
            
        except Exception as e:
            logging.error(f"Technical canvas configure error: {e}")
    
    def _on_technical_mousewheel(self, event):
        """Handle mouse wheel scrolling for technical analysis panel"""
        try:
            # Check if we have a scrollable canvas
            if hasattr(self, 'technical_canvas'):
                # Calculate scroll amount (negative for proper direction)
                scroll_amount = -1 * (event.delta / 120)
                
                # Scroll the canvas content
                self.technical_canvas.yview_scroll(int(scroll_amount), "units")
                
                # Prevent event from bubbling up to parent widgets
                return "break"
        except Exception as e:
            logging.error(f"Technical mousewheel error: {e}")
            return "break"
    
    def _align_technical_columns(self):
        """Force perfect alignment between headers and content columns"""
        try:
            if hasattr(self, 'headers_frame') and hasattr(self, 'technical_content_frame'):
                # Get the actual column widths from the headers frame
                self.root.update_idletasks()
                
                # Force both frames to have identical column configurations
                headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
                column_weights = [1, 1, 1, 1, 2, 1]
                column_minsizes = [80, 70, 80, 60, 100, 80]
                
                for i, (weight, minsize) in enumerate(zip(column_weights, column_minsizes)):
                    # Configure both frames identically
                    self.headers_frame.grid_columnconfigure(i, weight=weight, minsize=minsize, uniform=f"col{i}")
                    self.technical_content_frame.grid_columnconfigure(i, weight=weight, minsize=minsize, uniform=f"col{i}")
                
                # Update canvas scroll region
                if hasattr(self, 'technical_canvas'):
                    self.technical_canvas.configure(scrollregion=self.technical_canvas.bbox("all"))
                    
        except Exception as e:
            logging.error(f"Technical alignment error: {e}")
    
    def adjust_header_only(self, column_name: str, offset_pixels: int):
        """
        Adjust ONLY the header position without affecting data columns - UNLIMITED RANGE
        
        Args:
            column_name: Name of the column ("Ticker", "Price", "Change %", "RSI", "Signal", "Momentum")
            offset_pixels: Number of pixels to move right (+) or left (-) - NO LIMITS
        """
        try:
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            
            if column_name not in headers:
                self.update_status(f"Invalid column name: {column_name}")
                return False
            
            column_index = headers.index(column_name)
            
            # Check if headers_frame exists
            if not hasattr(self, 'headers_frame'):
                self.update_status("Headers frame not found")
                return False
            
            # Find the header widget for this column
            header_widget = None
            widget_count = 0
            for child in self.headers_frame.winfo_children():
                widget_count += 1
                try:
                    # Try to get widget text to match header name
                    widget_text = child.cget('text') if hasattr(child, 'cget') else ''
                    if widget_text == column_name:
                        header_widget = child
                        break
                except:
                    # If no text, fall back to grid_info for widgets still in grid
                    grid_info = child.grid_info()
                    if grid_info and int(grid_info.get('column', -1)) == column_index:
                        header_widget = child
                        break
            
            if header_widget is None:
                self.update_status(f"Header widget not found for {column_name}")
                return False
            
            # Initialize if first time
            if not hasattr(header_widget, '_total_offset'):
                header_widget._total_offset = 0
                header_widget._original_grid_info = header_widget.grid_info().copy()
                header_widget._using_place = False
                
                # Capture the actual current position while still in grid
                self.headers_frame.update_idletasks()
                header_widget._original_x = header_widget.winfo_x()
                header_widget._original_y = header_widget.winfo_y()
            
            # Add the new offset to the cumulative total
            old_offset = header_widget._total_offset
            header_widget._total_offset += offset_pixels
            total_offset = header_widget._total_offset
            
            # Switch to place positioning if not already done
            if not header_widget._using_place:
                header_widget.grid_remove()
                header_widget._using_place = True
            
            # Force frame update to get accurate dimensions
            self.headers_frame.update_idletasks()
            
            # Get frame dimensions
            frame_width = self.headers_frame.winfo_width()
            frame_height = self.headers_frame.winfo_height()
            
            # If frame not rendered yet, use fallback dimensions
            if frame_width <= 1:
                frame_width = 800  # Reasonable fallback
            if frame_height <= 1:
                frame_height = 30  # Header height
            
            # For first move, use actual current position as base to prevent jump
            if not hasattr(header_widget, '_placed_yet'):
                # This is the first time we're placing this widget
                base_x = header_widget._original_x
                base_y = header_widget._original_y
                header_widget._placed_yet = True
            else:
                # Subsequent moves: use calculated column position
                column_width = frame_width / len(headers)
                base_x = column_index * column_width + 10
                base_y = 5
            
            # Apply the total offset
            final_x = base_x + total_offset
            final_y = base_y
            
            # Only prevent going too far left (but allow some negative for left movement)
            if final_x < -50:  # Allow some negative movement, but not too extreme
                final_x = -50
            elif final_x > frame_width + 100:  # Prevent going too far right
                final_x = frame_width + 100
            
            # Use place() for absolute positioning
            header_widget.place(x=final_x, y=final_y, anchor='nw')
            
            # Force visual update
            self.root.update_idletasks()
            
            # Update status with movement info
            direction = 'right' if offset_pixels > 0 else 'left'
            self.update_status(f"Moved '{column_name}' header {abs(offset_pixels)}px {direction} (total: {total_offset:+d}px)")
            
            # Auto-save header positions after successful adjustment
            self.save_header_positions()
            
            return True
            
        except Exception as e:
            error_msg = f"Header adjustment error for {column_name}: {e}"
            logging.error(error_msg)
            self.update_status(error_msg)
            return False
    
    def reset_headers_only(self):
        """Reset ONLY headers to default alignment using original grid positioning"""
        try:
            if hasattr(self, 'headers_frame'):
                headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
                
                for child in self.headers_frame.winfo_children():
                    # Clear any place positioning
                    child.place_forget()
                    
                    # Reset offset tracking
                    if hasattr(child, '_total_offset'):
                        child._total_offset = 0
                        child._using_place = False
                    
                    # Get the original column from widget text
                    try:
                        widget_text = child.cget('text') if hasattr(child, 'cget') else ''
                        if widget_text in headers:
                            column_index = headers.index(widget_text)
                            
                            # Re-grid with original settings
                            child.grid(row=0, column=column_index, 
                                     padx=PADDING['small'], 
                                     pady=PADDING['small'], 
                                     sticky='w')
                    except Exception as inner_e:
                        logging.warning(f"Individual widget reset failed: {inner_e}")
                        # Fallback: just reset to grid with default padding
                        child.grid(padx=PADDING['small'], 
                                 pady=PADDING['small'], 
                                 sticky='w')
                
                # Force update
                self.root.update_idletasks()
                
                # Auto-save cleared header positions
                self.save_header_positions()
                
                self.update_status("Reset all headers to default positions")
                return True
            else:
                self.update_status("Headers frame not found for reset")
                return False
            
        except Exception as e:
            error_msg = f"Header reset error: {e}"
            logging.error(error_msg)
            self.update_status(error_msg)
            return False
    
    def show_header_positions(self):
        """Show current header positions for fine-tuning"""
        try:
            headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
            print("\n=== CURRENT HEADER POSITIONS ===")
            
            if hasattr(self, 'headers_frame'):
                for i, header in enumerate(headers):
                    for child in self.headers_frame.winfo_children():
                        grid_info = child.grid_info()
                        if grid_info and int(grid_info.get('column', -1)) == i:
                            padx = grid_info.get('padx', PADDING['small'])
                            if isinstance(padx, tuple):
                                offset = padx[0] - PADDING['small']
                                print(f"{header}: offset = {offset:+d} pixels")
                            else:
                                print(f"{header}: padx = {padx}")
                            break
            
            print("\nTo adjust: app.adjust_header_only('Column Name', +/- pixels)")
            print("Examples:")
            print("  app.adjust_header_only('Price', 5)      # Move Price header 5px right")
            print("  app.adjust_header_only('RSI', -3)       # Move RSI header 3px left")
            print("  app.reset_headers_only()                # Reset all headers")
            
        except Exception as e:
            logging.error(f"Header position display error: {e}")
    
    def quick_header_adjustments(self):
        """Quick access method for common header adjustments"""
        print("\n=== QUICK HEADER ADJUSTMENT COMMANDS ===")
        print("Copy and paste these commands to adjust headers:")
        print()
        print("# Show current positions:")
        print("app.show_header_positions()")
        print()
        print("# Move headers (adjust numbers as needed):")
        print("app.adjust_header_only('Ticker', 0)")
        print("app.adjust_header_only('Price', 0)")
        print("app.adjust_header_only('Change %', 0)")
        print("app.adjust_header_only('RSI', 0)")
        print("app.adjust_header_only('Signal', 0)")
        print("app.adjust_header_only('Momentum', 0)")
        print()
        print("# Reset if needed:")
        print("app.reset_headers_only()")
        print()
        print("Positive numbers = move right, Negative numbers = move left")
"""
Settings GUI
Comprehensive settings dialog for auto-refresh and alerts
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import logging
from typing import Dict, Callable, Optional

# Import GUI styles for consistent theming
try:
    from gui.gui_styles import (
        GUI_COLORS, FONTS, PADDING,
        create_themed_frame, create_themed_label, create_themed_button
    )
except ImportError:
    # Fallback colors if gui_styles not available
    GUI_COLORS = {
        'background': '#1e1e1e',
        'panel_bg': '#2d2d2d',
        'accent': '#007acc',
        'text_primary': '#ffffff',
        'text_secondary': '#cccccc',
        'success': '#4CAF50',
        'warning': '#FF9800',
        'danger': '#f44336',
        'info': '#2196F3'
    }
    FONTS = {
        'header': ('Arial', 16, 'bold'),
        'subheader': ('Arial', 14, 'bold'),
        'normal': ('Arial', 12),
        'small': ('Arial', 10)
    }
    PADDING = {'small': 5, 'medium': 10, 'large': 15}
    
    # Fallback functions for themed widgets
    def create_themed_frame(parent, style='normal'):
        return tk.Frame(parent, bg=GUI_COLORS['panel_bg'])
    
    def create_themed_label(parent, text, style='normal'):
        return tk.Label(parent, text=text, bg=GUI_COLORS['panel_bg'], 
                       fg=GUI_COLORS['text_primary'], font=FONTS['normal'])
    
    def create_themed_button(parent, text, command=None, style='normal'):
        return tk.Button(parent, text=text, command=command, 
                        bg=GUI_COLORS['accent'], fg='white', font=FONTS['normal'])


class SettingsDialog:
    """
    Settings dialog for configuring auto-refresh and alert preferences
    """
    
    def __init__(self, parent, auto_refresh_manager=None, alert_system=None, main_window=None):
        """Initialize the settings dialog"""
        self.parent = parent
        self.auto_refresh_manager = auto_refresh_manager
        self.alert_system = alert_system
        self.main_window = main_window  # Reference to main window for header alignment
        self.logger = logging.getLogger(__name__)
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("⚙️ Catalyst Scanner Settings")
        self.dialog.geometry("900x800")  # Much larger size
        self.dialog.configure(bg=GUI_COLORS['background'])
        self.dialog.resizable(True, True)
        
        # Set minimum size
        self.dialog.minsize(800, 700)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center on parent
        self._center_dialog()
        
        # Settings variables
        self.refresh_vars = {}
        self.alert_vars = {}
        self.header_adjustments = {}  # Store header offset display labels
        
        # Create GUI
        self.create_widgets()
        self.load_current_settings()
        
        # Handle dialog close
        self.dialog.protocol("WM_DELETE_WINDOW", self.on_cancel)
    
    def _center_dialog(self):
        """Center dialog on parent window"""
        try:
            # Update dialog to get actual size
            self.dialog.update_idletasks()
            
            # Get parent geometry
            parent_x = self.parent.winfo_rootx()
            parent_y = self.parent.winfo_rooty()
            parent_width = self.parent.winfo_width()
            parent_height = self.parent.winfo_height()
            
            # Get dialog size
            dialog_width = self.dialog.winfo_reqwidth()
            dialog_height = self.dialog.winfo_reqheight()
            
            # Calculate center position
            x = parent_x + (parent_width - dialog_width) // 2
            y = parent_y + (parent_height - dialog_height) // 2
            
            self.dialog.geometry(f"{dialog_width}x{dialog_height}+{x}+{y}")
            
        except Exception as e:
            self.logger.debug(f"Error centering dialog: {e}")
    
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container with scrollable frame
        main_frame = tk.Frame(self.dialog, bg=GUI_COLORS['background'])
        main_frame.pack(fill='both', expand=True, padx=PADDING['large'], pady=PADDING['large'])
        
        # Create notebook for tabs with styling
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook', background=GUI_COLORS['panel_bg'])
        style.configure('TNotebook.Tab', padding=[PADDING['medium'], PADDING['small']])
        
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill='both', expand=True, pady=(0, PADDING['medium']))
        
        # Create tabs
        self.create_refresh_tab()
        self.create_alert_tab()
        self.create_sms_tab()
        self.create_email_tab()
        self.create_header_alignment_tab()  # Add header alignment tab
        
        # Button frame with accent background
        button_frame = tk.Frame(main_frame, bg=GUI_COLORS['panel_bg'], relief='raised', bd=2)
        button_frame.pack(fill='x', pady=(PADDING['medium'], 0))
        
        # Buttons with improved styling
        tk.Button(button_frame, text="✅ Save & Apply", 
                 command=self.on_save, 
                 bg=GUI_COLORS['success'], fg='white',
                 font=FONTS['normal'], 
                 relief='raised', bd=3,
                 padx=PADDING['large'], pady=PADDING['small']
                 ).pack(side='right', padx=(PADDING['small'], PADDING['medium']), 
                       pady=PADDING['small'])
        
        tk.Button(button_frame, text="❌ Cancel", 
                 command=self.on_cancel, 
                 bg=GUI_COLORS['danger'], fg='white',
                 font=FONTS['normal'],
                 relief='raised', bd=3,
                 padx=PADDING['large'], pady=PADDING['small']
                 ).pack(side='right', pady=PADDING['small'])
        
        tk.Button(button_frame, text="🔄 Reset to Defaults", 
                 command=self.on_reset, 
                 bg=GUI_COLORS['warning'], fg='white',
                 font=FONTS['normal'],
                 relief='raised', bd=3,
                 padx=PADDING['large'], pady=PADDING['small']
                 ).pack(side='left', padx=PADDING['medium'], 
                       pady=PADDING['small'])
    
    def create_refresh_tab(self):
        """Create auto-refresh settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔄 Auto Refresh")
        
        # Create scrollable frame with better colors
        canvas = tk.Canvas(tab_frame, bg=GUI_COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=GUI_COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Auto Refresh Section with colorful styling
        refresh_section = tk.LabelFrame(scrollable_frame, 
                                       text="🔄 Auto Refresh Settings", 
                                       bg=GUI_COLORS['panel_bg'], 
                                       fg=GUI_COLORS['accent'], 
                                       font=FONTS['subheader'],
                                       relief='raised', bd=3)
        refresh_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        # Enable auto refresh with better styling
        self.refresh_vars['enabled'] = tk.BooleanVar()
        refresh_checkbox = tk.Checkbutton(refresh_section, 
                                         text="✅ Enable automatic refresh", 
                                         variable=self.refresh_vars['enabled'],
                                         bg=GUI_COLORS['panel_bg'], 
                                         fg=GUI_COLORS['text_primary'], 
                                         selectcolor=GUI_COLORS['accent'],
                                         font=FONTS['normal'],
                                         activebackground=GUI_COLORS['accent'],
                                         activeforeground='white')
        refresh_checkbox.pack(anchor='w', padx=PADDING['large'], pady=PADDING['medium'])
        
        # Refresh interval with colorful frame
        interval_frame = tk.Frame(refresh_section, bg=GUI_COLORS['panel_bg'], 
                                 relief='sunken', bd=2)
        interval_frame.pack(fill='x', padx=PADDING['large'], pady=PADDING['medium'])
        
        tk.Label(interval_frame, text="⏱️ Refresh interval:", 
                bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal']).pack(side='left', padx=PADDING['small'])
        
        self.refresh_vars['interval'] = tk.IntVar()
        interval_spinbox = tk.Spinbox(interval_frame, from_=15, to=480, increment=15,
                                     textvariable=self.refresh_vars['interval'],
                                     width=12, font=FONTS['normal'],
                                     bg='white', fg='black',
                                     buttonbackground=GUI_COLORS['accent'],
                                     relief='raised', bd=2)
        interval_spinbox.pack(side='left', padx=PADDING['medium'])
        
        tk.Label(interval_frame, text="minutes", 
                bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_secondary'], 
                font=FONTS['normal']).pack(side='left', padx=PADDING['small'])
        
        # Market hours only
        self.refresh_vars['market_hours_only'] = tk.BooleanVar()
        market_hours_checkbox = tk.Checkbutton(refresh_section, 
                                              text="🕘 Refresh only during market hours (9:30 AM - 4:00 PM ET)", 
                                              variable=self.refresh_vars['market_hours_only'],
                                              bg=GUI_COLORS['panel_bg'], 
                                              fg=GUI_COLORS['text_primary'], 
                                              selectcolor=GUI_COLORS['accent'],
                                              font=FONTS['normal'],
                                              activebackground=GUI_COLORS['accent'],
                                              activeforeground='white')
        market_hours_checkbox.pack(anchor='w', padx=PADDING['large'], pady=PADDING['small'])
        
        # Weekend refresh
        self.refresh_vars['weekend_refresh'] = tk.BooleanVar()
        weekend_checkbox = tk.Checkbutton(refresh_section, 
                                         text="📅 Allow refresh on weekends", 
                                         variable=self.refresh_vars['weekend_refresh'],
                                         bg=GUI_COLORS['panel_bg'], 
                                         fg=GUI_COLORS['text_primary'], 
                                         selectcolor=GUI_COLORS['accent'],
                                         font=FONTS['normal'],
                                         activebackground=GUI_COLORS['accent'],
                                         activeforeground='white')
        weekend_checkbox.pack(anchor='w', padx=PADDING['large'], pady=PADDING['small'])
        
        # Status section with info color
        status_section = tk.LabelFrame(scrollable_frame, 
                                      text="📊 Current Status", 
                                      bg=GUI_COLORS['panel_bg'], 
                                      fg=GUI_COLORS['info'], 
                                      font=FONTS['subheader'],
                                      relief='raised', bd=3)
        status_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        self.refresh_status_label = tk.Label(status_section, 
                                           text="🔄 Loading status...", 
                                           bg=GUI_COLORS['panel_bg'], 
                                           fg=GUI_COLORS['success'], 
                                           font=FONTS['normal'])
        self.refresh_status_label.pack(anchor='w', padx=PADDING['large'], pady=PADDING['medium'])
        
        # Manual refresh button with accent color
        refresh_button = tk.Button(status_section, 
                                  text="🚀 Manual Refresh Now", 
                                  command=self.manual_refresh, 
                                  bg=GUI_COLORS['info'], 
                                  fg='white',
                                  font=FONTS['normal'],
                                  relief='raised', bd=3,
                                  padx=PADDING['large'], 
                                  pady=PADDING['small'],
                                  activebackground=GUI_COLORS['accent'])
        refresh_button.pack(anchor='w', padx=PADDING['large'], pady=PADDING['medium'])
    
    def create_alert_tab(self):
        """Create alert settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="🔔 Visual & Audio Alerts")
        
        # Create scrollable frame with better colors
        canvas = tk.Canvas(tab_frame, bg=GUI_COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=GUI_COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # General Alert Settings
        general_section = tk.LabelFrame(scrollable_frame, 
                                       text="🔔 General Alert Settings", 
                                       bg=GUI_COLORS['panel_bg'], 
                                       fg=GUI_COLORS['warning'], 
                                       font=FONTS['subheader'],
                                       relief='raised', bd=3)
        general_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        # Visual alerts
        self.alert_vars['visual_enabled'] = tk.BooleanVar()
        visual_checkbox = tk.Checkbutton(general_section, 
                                        text="👁️ Enable visual popup alerts", 
                      variable=self.alert_vars['visual_enabled'],
                      bg='#3b3b3b', fg='white', selectcolor='#2b2b2b',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Audio alerts
        self.alert_vars['audio_enabled'] = tk.BooleanVar()
        tk.Checkbutton(general_section, text="Enable audio alerts", 
                      variable=self.alert_vars['audio_enabled'],
                      bg='#3b3b3b', fg='white', selectcolor='#2b2b2b',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Popup duration
        duration_frame = tk.Frame(general_section, bg='#3b3b3b')
        duration_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(duration_frame, text="Popup duration:", 
                bg='#3b3b3b', fg='white', font=('Arial', 10)).pack(side='left')
        
        self.alert_vars['popup_duration'] = tk.IntVar()
        duration_spinbox = tk.Spinbox(duration_frame, from_=5, to=60, increment=5,
                                     textvariable=self.alert_vars['popup_duration'],
                                     width=10, font=('Arial', 10))
        duration_spinbox.pack(side='left', padx=(10, 5))
        
        tk.Label(duration_frame, text="seconds", 
                bg='#3b3b3b', fg='white', font=('Arial', 10)).pack(side='left')
        
        # Cooldown period
        cooldown_frame = tk.Frame(general_section, bg='#3b3b3b')
        cooldown_frame.pack(fill='x', padx=10, pady=5)
        
        tk.Label(cooldown_frame, text="Alert cooldown:", 
                bg='#3b3b3b', fg='white', font=('Arial', 10)).pack(side='left')
        
        self.alert_vars['cooldown_minutes'] = tk.IntVar()
        cooldown_spinbox = tk.Spinbox(cooldown_frame, from_=5, to=120, increment=5,
                                     textvariable=self.alert_vars['cooldown_minutes'],
                                     width=10, font=('Arial', 10))
        cooldown_spinbox.pack(side='left', padx=(10, 5))
        
        tk.Label(cooldown_frame, text="minutes", 
                bg='#3b3b3b', fg='white', font=('Arial', 10)).pack(side='left')
        
        # Alert Triggers Section
        triggers_section = tk.LabelFrame(scrollable_frame, text="Alert Triggers", 
                                        bg='#3b3b3b', fg='white', font=('Arial', 12, 'bold'))
        triggers_section.pack(fill='x', padx=10, pady=10)
        
        # RSI extreme alerts
        self.alert_vars['alert_rsi_extreme'] = tk.BooleanVar()
        tk.Checkbutton(triggers_section, text="Alert on RSI extreme conditions", 
                      variable=self.alert_vars['alert_rsi_extreme'],
                      bg='#3b3b3b', fg='white', selectcolor='#2b2b2b',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # RSI threshold
        rsi_frame = tk.Frame(triggers_section, bg='#3b3b3b')
        rsi_frame.pack(fill='x', padx=30, pady=2)
        
        tk.Label(rsi_frame, text="RSI extreme threshold:", 
                bg='#3b3b3b', fg='white', font=('Arial', 9)).pack(side='left')
        
        self.alert_vars['rsi_threshold'] = tk.IntVar()
        rsi_spinbox = tk.Spinbox(rsi_frame, from_=15, to=35, increment=5,
                                textvariable=self.alert_vars['rsi_threshold'],
                                width=8, font=('Arial', 9))
        rsi_spinbox.pack(side='left', padx=(10, 5))
        
        tk.Label(rsi_frame, text="(alerts when RSI < threshold or > 100-threshold)", 
                bg='#3b3b3b', fg='#aaaaaa', font=('Arial', 8)).pack(side='left')
        
        # Signal change alerts
        self.alert_vars['alert_signal_change'] = tk.BooleanVar()
        tk.Checkbutton(triggers_section, text="Alert on technical signal changes", 
                      variable=self.alert_vars['alert_signal_change'],
                      bg='#3b3b3b', fg='white', selectcolor='#2b2b2b',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Momentum change alerts
        self.alert_vars['alert_momentum_change'] = tk.BooleanVar()
        tk.Checkbutton(triggers_section, text="Alert on significant momentum changes", 
                      variable=self.alert_vars['alert_momentum_change'],
                      bg='#3b3b3b', fg='white', selectcolor='#2b2b2b',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Opportunity score alerts
        self.alert_vars['alert_opportunity_score'] = tk.BooleanVar()
        tk.Checkbutton(triggers_section, text="Alert on high opportunity scores", 
                      variable=self.alert_vars['alert_opportunity_score'],
                      bg='#3b3b3b', fg='white', selectcolor='#2b2b2b',
                      font=('Arial', 10)).pack(anchor='w', padx=10, pady=5)
        
        # Opportunity threshold
        opp_frame = tk.Frame(triggers_section, bg='#3b3b3b')
        opp_frame.pack(fill='x', padx=30, pady=2)
        
        tk.Label(opp_frame, text="Opportunity score threshold:", 
                bg='#3b3b3b', fg='white', font=('Arial', 9)).pack(side='left')
        
        self.alert_vars['opportunity_threshold'] = tk.DoubleVar()
        opp_spinbox = tk.Spinbox(opp_frame, from_=5.0, to=9.5, increment=0.5,
                                textvariable=self.alert_vars['opportunity_threshold'],
                                width=8, font=('Arial', 9), format="%.1f")
        opp_spinbox.pack(side='left', padx=(10, 5))
        
        tk.Label(opp_frame, text="/10", 
                bg='#3b3b3b', fg='#aaaaaa', font=('Arial', 9)).pack(side='left')
    
    def create_sms_tab(self):
        """Create SMS alert settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📱 SMS Alerts")
        
        # Create scrollable frame with colorful styling
        canvas = tk.Canvas(tab_frame, bg=GUI_COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=GUI_COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # SMS Configuration Section
        sms_section = tk.LabelFrame(scrollable_frame, 
                                   text="📱 SMS Alert Configuration", 
                                   bg=GUI_COLORS['panel_bg'], 
                                   fg=GUI_COLORS['info'], 
                                   font=FONTS['subheader'],
                                   relief='raised', bd=3)
        sms_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        # Enable SMS
        sms_enable_frame = tk.Frame(sms_section, bg=GUI_COLORS['panel_bg'], relief='sunken', bd=2)
        sms_enable_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        self.alert_vars['sms_enabled'] = tk.BooleanVar()
        sms_check = tk.Checkbutton(sms_enable_frame, text="📲 Enable SMS Alerts", 
                                  variable=self.alert_vars['sms_enabled'],
                                  bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                                  selectcolor=GUI_COLORS['panel_bg'],
                                  font=FONTS['normal'], relief='flat')
        sms_check.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])
        
        # Phone number configuration
        phone_section = tk.LabelFrame(sms_section, text="📞 Phone Number", 
                                     bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['accent'],
                                     font=FONTS['normal'], relief='sunken', bd=2)
        phone_section.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        phone_frame = tk.Frame(phone_section, bg=GUI_COLORS['panel_bg'])
        phone_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        tk.Label(phone_frame, text="📱 Phone Number:", 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal']).pack(side='left')
        
        self.alert_vars['phone_number'] = tk.StringVar()
        phone_entry = tk.Entry(phone_frame, textvariable=self.alert_vars['phone_number'],
                              font=FONTS['normal'], width=20, bg='white', fg='black')
        phone_entry.pack(side='left', padx=(PADDING['medium'], PADDING['small']))
        
        tk.Label(phone_frame, text="(e.g., +1234567890)", 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'], 
                font=FONTS['small']).pack(side='left')
        
        # SMS Provider Selection
        provider_section = tk.LabelFrame(sms_section, text="🔧 SMS Provider", 
                                        bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['accent'],
                                        font=FONTS['normal'], relief='sunken', bd=2)
        provider_section.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        # Provider options with better visibility
        self.alert_vars['sms_provider'] = tk.StringVar()
        provider_frame = tk.Frame(provider_section, bg=GUI_COLORS['panel_bg'])
        provider_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        # Create radio buttons with improved styling for visibility
        mock_radio = tk.Radiobutton(provider_frame, text="🧪 Mock (Testing)", 
                      variable=self.alert_vars['sms_provider'], value='mock',
                      bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'],
                      selectcolor='#4CAF50', activebackground=GUI_COLORS['panel_bg'],
                      activeforeground=GUI_COLORS['accent'], font=FONTS['normal'],
                      relief='flat', bd=0, highlightthickness=0)
        mock_radio.pack(anchor='w', pady=2)
        
        twilio_radio = tk.Radiobutton(provider_frame, text="📞 Twilio (Recommended)", 
                      variable=self.alert_vars['sms_provider'], value='twilio',
                      bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'],
                      selectcolor='#2196F3', activebackground=GUI_COLORS['panel_bg'],
                      activeforeground=GUI_COLORS['accent'], font=FONTS['normal'],
                      relief='flat', bd=0, highlightthickness=0)
        twilio_radio.pack(anchor='w', pady=2)
        
        aws_radio = tk.Radiobutton(provider_frame, text="☁️ AWS SNS", 
                      variable=self.alert_vars['sms_provider'], value='aws_sns',
                      bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'],
                      selectcolor='#FF9800', activebackground=GUI_COLORS['panel_bg'],
                      activeforeground=GUI_COLORS['accent'], font=FONTS['normal'],
                      relief='flat', bd=0, highlightthickness=0)
        aws_radio.pack(anchor='w', pady=2)
        
        # Provider Configuration Section
        config_section = tk.LabelFrame(sms_section, text="🔧 Provider Configuration", 
                                      bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['accent'],
                                      font=FONTS['normal'], relief='sunken', bd=2)
        config_section.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        # Create notebook for provider-specific settings
        provider_notebook = ttk.Notebook(config_section)
        provider_notebook.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        # Twilio Configuration Tab
        twilio_frame = tk.Frame(provider_notebook, bg=GUI_COLORS['panel_bg'])
        provider_notebook.add(twilio_frame, text="📞 Twilio Setup")
        
        # Twilio credentials
        self.alert_vars['twilio_account_sid'] = tk.StringVar()
        self.alert_vars['twilio_auth_token'] = tk.StringVar()
        self.alert_vars['twilio_from_number'] = tk.StringVar()
        
        # Account SID
        sid_frame = tk.Frame(twilio_frame, bg=GUI_COLORS['panel_bg'])
        sid_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(sid_frame, text="Account SID:", bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], font=FONTS['normal']).pack(side='left')
        tk.Entry(sid_frame, textvariable=self.alert_vars['twilio_account_sid'],
                font=FONTS['small'], width=40, bg='white', fg='black').pack(side='left', padx=(10, 0))
        
        # Auth Token
        token_frame = tk.Frame(twilio_frame, bg=GUI_COLORS['panel_bg'])
        token_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(token_frame, text="Auth Token:", bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], font=FONTS['normal']).pack(side='left')
        tk.Entry(token_frame, textvariable=self.alert_vars['twilio_auth_token'],
                font=FONTS['small'], width=40, bg='white', fg='black', show='*').pack(side='left', padx=(10, 0))
        
        # From Number
        from_frame = tk.Frame(twilio_frame, bg=GUI_COLORS['panel_bg'])
        from_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(from_frame, text="From Number:", bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], font=FONTS['normal']).pack(side='left')
        tk.Entry(from_frame, textvariable=self.alert_vars['twilio_from_number'],
                font=FONTS['small'], width=20, bg='white', fg='black').pack(side='left', padx=(10, 0))
        
        # Twilio help text
        help_text = tk.Label(twilio_frame, 
                           text="Get credentials from https://console.twilio.com\n"
                                "Account SID starts with 'AC', Auth Token is 32 characters\n"
                                "From Number format: +1234567890",
                           bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'],
                           font=FONTS['small'], justify='left')
        help_text.pack(anchor='w', padx=10, pady=5)
        
        # AWS Configuration Tab
        aws_frame = tk.Frame(provider_notebook, bg=GUI_COLORS['panel_bg'])
        provider_notebook.add(aws_frame, text="☁️ AWS SNS Setup")
        
        # AWS credentials
        self.alert_vars['aws_access_key'] = tk.StringVar()
        self.alert_vars['aws_secret_key'] = tk.StringVar()
        self.alert_vars['aws_region'] = tk.StringVar(value='us-east-1')
        
        # Access Key
        key_frame = tk.Frame(aws_frame, bg=GUI_COLORS['panel_bg'])
        key_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(key_frame, text="Access Key ID:", bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], font=FONTS['normal']).pack(side='left')
        tk.Entry(key_frame, textvariable=self.alert_vars['aws_access_key'],
                font=FONTS['small'], width=30, bg='white', fg='black').pack(side='left', padx=(10, 0))
        
        # Secret Key
        secret_frame = tk.Frame(aws_frame, bg=GUI_COLORS['panel_bg'])
        secret_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(secret_frame, text="Secret Access Key:", bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], font=FONTS['normal']).pack(side='left')
        tk.Entry(secret_frame, textvariable=self.alert_vars['aws_secret_key'],
                font=FONTS['small'], width=30, bg='white', fg='black', show='*').pack(side='left', padx=(10, 0))
        
        # Region
        region_frame = tk.Frame(aws_frame, bg=GUI_COLORS['panel_bg'])
        region_frame.pack(fill='x', padx=10, pady=5)
        tk.Label(region_frame, text="Region:", bg=GUI_COLORS['panel_bg'], 
                fg=GUI_COLORS['text_primary'], font=FONTS['normal']).pack(side='left')
        tk.Entry(region_frame, textvariable=self.alert_vars['aws_region'],
                font=FONTS['small'], width=15, bg='white', fg='black').pack(side='left', padx=(10, 0))
        
        # AWS help text
        aws_help_text = tk.Label(aws_frame, 
                               text="Create IAM user with SNS permissions in AWS Console\n"
                                    "Generate access keys for programmatic access\n"
                                    "Common regions: us-east-1, us-west-2, eu-west-1",
                               bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'],
                               font=FONTS['small'], justify='left')
        aws_help_text.pack(anchor='w', padx=10, pady=5)
        
        # Test SMS Button Section
        test_section = tk.Frame(sms_section, bg=GUI_COLORS['panel_bg'], relief='raised', bd=3)
        test_section.pack(fill='x', padx=PADDING['medium'], pady=PADDING['medium'])
        
        # Create test buttons with improved styling
        test_button = tk.Button(test_section, text="📤 Send Test SMS", 
                               command=self._send_test_sms,
                               bg='#4CAF50', fg='white', font=FONTS['normal'],
                               relief='raised', bd=2, padx=PADDING['large'], 
                               pady=PADDING['small'], cursor='hand2',
                               activebackground='#45a049', activeforeground='white')
        test_button.pack(side='left', padx=PADDING['medium'])
        
        status_button = tk.Button(test_section, text="🔍 Check SMS Status", 
                                 command=self._check_sms_status,
                                 bg='#2196F3', fg='white', font=FONTS['normal'],
                                 relief='raised', bd=2, padx=PADDING['large'], 
                                 pady=PADDING['small'], cursor='hand2',
                                 activebackground='#1976D2', activeforeground='white')
        status_button.pack(side='left', padx=PADDING['small'])
        
        # SMS Service Status
        status_section = tk.LabelFrame(scrollable_frame, text="📊 SMS Service Status", 
                                      bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['info'],
                                      font=FONTS['subheader'], relief='raised', bd=3)
        status_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        # Status display
        self.sms_status_label = tk.Label(status_section, 
                                        text="🔄 SMS service status will appear here...", 
                                        bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'], 
                                        font=FONTS['normal'], justify='left')
        self.sms_status_label.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])
        
        # SMS Features Info
        features_section = tk.LabelFrame(scrollable_frame, text="✨ SMS Features", 
                                        bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['success'],
                                        font=FONTS['subheader'], relief='raised', bd=3)
        features_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        features_text = (
            "📱 Real-time SMS alerts for market events\n"
            "🎯 Customizable alert triggers and thresholds\n"
            "📞 Multiple SMS provider support (Twilio, AWS SNS)\n"
            "🧪 Mock mode for testing without charges\n"
            "📊 SMS delivery tracking and status\n"
            "⚙️ Rate limiting and daily message limits\n"
            "🔒 Secure credential management"
        )
        
        tk.Label(features_section, text=features_text, 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal'], justify='left').pack(anchor='w', 
                                                           padx=PADDING['medium'], 
                                                           pady=PADDING['medium'])
    
    def create_email_tab(self):
        """Create email alerts settings tab"""
        try:
            # Import the email settings panel
            from gui.email_settings_panel import EmailSettingsPanel
            
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text="📧 Email Alerts")
            
            # Create the email settings panel
            self.email_panel = EmailSettingsPanel(
                tab_frame, 
                alert_system=self.alert_system,
                on_settings_changed=self._on_email_settings_changed
            )
            self.email_panel.pack(fill='both', expand=True)
            
        except ImportError as e:
            self.logger.error(f"Failed to import EmailSettingsPanel: {e}")
            # Create a simple fallback panel
            self._create_simple_email_tab(tab_frame)
        except Exception as e:
            self.logger.error(f"Error creating email tab: {e}")
    
    def _create_simple_email_tab(self, tab_frame):
        """Create a simple email tab as fallback"""
        # Create scrollable frame
        canvas = tk.Canvas(tab_frame, bg=GUI_COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=GUI_COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Email alerts section
        email_section = tk.LabelFrame(scrollable_frame, text="📧 Email Alert Settings", 
                                     bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['info'],
                                     font=FONTS['subheader'], relief='raised', bd=3)
        email_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        # Initialize email variables if not already done
        if not hasattr(self, 'email_vars'):
            self.email_vars = {}
            self.email_vars['enabled'] = tk.BooleanVar(value=False)
            self.email_vars['recipient'] = tk.StringVar(value="")
            self.email_vars['provider'] = tk.StringVar(value="gmail")
            self.email_vars['username'] = tk.StringVar(value="")
            self.email_vars['password'] = tk.StringVar(value="")
        
        # Email enabled checkbox
        email_enabled_cb = tk.Checkbutton(email_section, text="🔔 Enable Email Alerts", 
                                         variable=self.email_vars['enabled'],
                                         bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                                         font=FONTS['normal'], selectcolor=GUI_COLORS['accent'],
                                         activebackground=GUI_COLORS['panel_bg'], 
                                         activeforeground=GUI_COLORS['text_primary'])
        email_enabled_cb.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])
        
        # Recipient email
        recipient_frame = tk.Frame(email_section, bg=GUI_COLORS['panel_bg'])
        recipient_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        tk.Label(recipient_frame, text="📧 Recipient Email:", 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal']).pack(side='left')
        
        recipient_entry = tk.Entry(recipient_frame, textvariable=self.email_vars['recipient'], 
                                  font=FONTS['normal'], width=30,
                                  bg='white', fg='black', insertbackground='black')
        recipient_entry.pack(side='right', padx=(PADDING['medium'], 0))
        
        # Email provider selection
        provider_frame = tk.Frame(email_section, bg=GUI_COLORS['panel_bg'])
        provider_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        tk.Label(provider_frame, text="📮 Email Provider:", 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal']).pack(side='left')
        
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.email_vars['provider'], 
                                     values=['gmail', 'outlook', 'yahoo'], 
                                     state='readonly', width=20)
        provider_combo.pack(side='right', padx=(PADDING['medium'], 0))
        
        # Email username (sender email)
        username_frame = tk.Frame(email_section, bg=GUI_COLORS['panel_bg'])
        username_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        tk.Label(username_frame, text="📧 Your Email:", 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal']).pack(side='left')
        
        username_entry = tk.Entry(username_frame, textvariable=self.email_vars['username'], 
                                  font=FONTS['normal'], width=30,
                                  bg='white', fg='black', insertbackground='black')
        username_entry.pack(side='right', padx=(PADDING['medium'], 0))
        
        # Email password (app password)
        password_frame = tk.Frame(email_section, bg=GUI_COLORS['panel_bg'])
        password_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        tk.Label(password_frame, text="🔑 App Password:", 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
                font=FONTS['normal']).pack(side='left')
        
        password_entry = tk.Entry(password_frame, textvariable=self.email_vars['password'], 
                                  font=FONTS['normal'], width=30, show='*',
                                  bg='white', fg='black', insertbackground='black')
        password_entry.pack(side='right', padx=(PADDING['medium'], 0))
        
        # Help text for app passwords
        help_frame = tk.Frame(email_section, bg=GUI_COLORS['panel_bg'])
        help_frame.pack(fill='x', padx=PADDING['medium'], pady=PADDING['small'])
        
        help_text = "💡 For Gmail: Use App Password (not regular password)\n" \
                   "   Go to Google Account → Security → App Passwords"
        tk.Label(help_frame, text=help_text, 
                bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'], 
                font=FONTS['small'], justify='left').pack(anchor='w')
        
        # Test section
        test_section = tk.Frame(email_section, bg=GUI_COLORS['panel_bg'], relief='raised', bd=3)
        test_section.pack(fill='x', padx=PADDING['medium'], pady=PADDING['medium'])
        
        test_button = tk.Button(test_section, text="📤 Send Test Email", 
                               command=self._send_test_email,
                               bg='#4CAF50', fg='white', font=FONTS['normal'],
                               relief='raised', bd=2, padx=PADDING['large'], 
                               pady=PADDING['small'], cursor='hand2',
                               activebackground='#45a049', activeforeground='white')
        test_button.pack(side='left', padx=PADDING['medium'])
        
        status_button = tk.Button(test_section, text="🔍 Check Email Status", 
                                 command=self._check_email_status,
                                 bg='#2196F3', fg='white', font=FONTS['normal'],
                                 relief='raised', bd=2, padx=PADDING['large'], 
                                 pady=PADDING['small'], cursor='hand2',
                                 activebackground='#1976D2', activeforeground='white')
        status_button.pack(side='left', padx=PADDING['small'])
        
        # Email status display
        status_section = tk.LabelFrame(scrollable_frame, text="📊 Email Service Status", 
                                      bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['info'],
                                      font=FONTS['subheader'], relief='raised', bd=3)
        status_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        self.email_status_label = tk.Label(status_section, 
                                          text="🔄 Email service status will appear here...", 
                                          bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'], 
                                          font=FONTS['normal'], justify='left')
        self.email_status_label.pack(anchor='w', padx=PADDING['medium'], pady=PADDING['small'])
    
    def _on_email_settings_changed(self, settings):
        """Handle email settings changes from the email panel"""
        try:
            if self.alert_system:
                # Update alert system with new email settings
                for key, value in settings.items():
                    self.alert_system.update_setting(key, value)
                self.logger.info("Email settings updated successfully")
            else:
                self.logger.warning("No alert system available to update email settings")
        except Exception as e:
            self.logger.error(f"Error updating email settings: {e}")
    
    def _send_test_email(self):
        """Send a test email"""
        try:
            if self.alert_system:
                # First try to update credentials
                self.alert_system.update_setting('email_username', self.email_vars['username'].get())
                self.alert_system.update_setting('email_password', self.email_vars['password'].get())
                self.alert_system.update_setting('email_recipient', self.email_vars['recipient'].get())
                self.alert_system.update_setting('email_provider', self.email_vars['provider'].get())
                self.alert_system.update_email_credentials()
                
                # Now try to send test email
                result = self.alert_system.test_email_service()
                if result.get('success'):
                    messagebox.showinfo("Email Test", "Test email sent successfully!")
                    self.email_status_label.config(text=f"✅ Test email sent: {result.get('message', '')}")
                else:
                    messagebox.showerror("Email Test Failed", f"Failed to send test email: {result.get('error', 'Unknown error')}")
                    self.email_status_label.config(text=f"❌ Test failed: {result.get('error', 'Unknown error')}")
            else:
                messagebox.showerror("Email Test Failed", "Email alert system not available")
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            messagebox.showerror("Email Test Error", f"Error: {e}")
    
    def _check_email_status(self):
        """Check email service status"""
        try:
            if self.alert_system:
                # First try to update credentials
                self.alert_system.update_setting('email_username', self.email_vars['username'].get())
                self.alert_system.update_setting('email_password', self.email_vars['password'].get())
                self.alert_system.update_setting('email_recipient', self.email_vars['recipient'].get())
                self.alert_system.update_setting('email_provider', self.email_vars['provider'].get())
                self.alert_system.update_email_credentials()
                
                # Test connection first
                if self.alert_system.email_service:
                    success, message = self.alert_system.email_service.test_connection()
                    
                    if success:
                        status_text = f"✅ Email connection successful: {message}"
                        # Get detailed status
                        status = self.alert_system.get_email_service_status()
                        if status.get('available'):
                            status_text += f" | Provider: {status.get('provider', 'Unknown')}"
                            if status.get('recipient_email'):
                                status_text += f" | Recipient: {status.get('recipient_email')}"
                    else:
                        status_text = f"❌ Email connection failed: {message}"
                else:
                    status_text = "❌ Email service not available"
                
                self.email_status_label.config(text=status_text)
                
                # Also show in message box
                messagebox.showinfo("Email Connection Test", status_text)
            else:
                messagebox.showerror("Status Check Failed", "Email alert system not available")
        except Exception as e:
            self.logger.error(f"Error checking email status: {e}")
            messagebox.showerror("Status Check Error", f"Error: {e}")
    
    def load_current_settings(self):
        """Load current settings into the GUI"""
        try:
            self.logger.info("Loading current settings into dialog...")
            
            # Load refresh settings
            if self.auto_refresh_manager:
                self.logger.debug("Loading auto-refresh settings...")
                self.refresh_vars['enabled'].set(self.auto_refresh_manager.get_setting('auto_refresh_enabled', True))
                self.refresh_vars['interval'].set(self.auto_refresh_manager.get_setting('refresh_interval_minutes', 120))
                self.refresh_vars['market_hours_only'].set(self.auto_refresh_manager.get_setting('market_hours_only', True))
                self.refresh_vars['weekend_refresh'].set(self.auto_refresh_manager.get_setting('weekend_refresh', False))
                
                # Update status
                status = self.auto_refresh_manager.get_status()
                status_text = f"Status: {'Running' if status.get('running') else 'Stopped'} | "
                status_text += f"Last: {status.get('last_refresh', 'Never')} | "
                status_text += f"Next: {status.get('next_refresh', 'Unknown')}"
                self.refresh_status_label.config(text=status_text)
            else:
                self.logger.warning("No auto_refresh_manager available for settings")
            
            # Load alert settings
            if self.alert_system:
                self.logger.debug("Loading alert settings...")
                self.alert_vars['visual_enabled'].set(self.alert_system.get_setting('visual_alerts_enabled', True))
                self.alert_vars['audio_enabled'].set(self.alert_system.get_setting('audio_alerts_enabled', True))
                self.alert_vars['sms_enabled'].set(self.alert_system.get_setting('sms_alerts_enabled', False))
                self.alert_vars['popup_duration'].set(self.alert_system.get_setting('popup_duration_seconds', 10))
                self.alert_vars['cooldown_minutes'].set(self.alert_system.get_setting('cooldown_minutes', 30))
                self.alert_vars['alert_rsi_extreme'].set(self.alert_system.get_setting('alert_on_rsi_extreme', True))
                self.alert_vars['rsi_threshold'].set(self.alert_system.get_setting('rsi_extreme_threshold', 25))
                self.alert_vars['alert_signal_change'].set(self.alert_system.get_setting('alert_on_signal_change', True))
                self.alert_vars['alert_momentum_change'].set(self.alert_system.get_setting('alert_on_momentum_change', True))
                self.alert_vars['alert_opportunity_score'].set(self.alert_system.get_setting('alert_on_opportunity_score_change', True))
                self.alert_vars['opportunity_threshold'].set(self.alert_system.get_setting('opportunity_score_threshold', 7.0))
                self.alert_vars['phone_number'].set(self.alert_system.get_setting('sms_phone_number', ''))
                self.alert_vars['sms_provider'].set(self.alert_system.get_setting('sms_provider', 'mock'))
                
                # Load SMS provider credentials
                self.alert_vars['twilio_account_sid'].set(self.alert_system.get_setting('twilio_account_sid', ''))
                self.alert_vars['twilio_auth_token'].set(self.alert_system.get_setting('twilio_auth_token', ''))
                self.alert_vars['twilio_from_number'].set(self.alert_system.get_setting('twilio_phone_number', ''))
                self.alert_vars['aws_access_key'].set(self.alert_system.get_setting('aws_access_key', ''))
                self.alert_vars['aws_secret_key'].set(self.alert_system.get_setting('aws_secret_key', ''))
                self.alert_vars['aws_region'].set(self.alert_system.get_setting('aws_region', 'us-east-1'))
                
                # Load email settings if email variables exist
                if hasattr(self, 'email_vars'):
                    self.email_vars['enabled'].set(self.alert_system.get_setting('email_alerts_enabled', False))
                    self.email_vars['recipient'].set(self.alert_system.get_setting('email_recipient', ''))
                    self.email_vars['provider'].set(self.alert_system.get_setting('email_provider', 'gmail'))
                    self.email_vars['username'].set(self.alert_system.get_setting('email_username', ''))
                    self.email_vars['password'].set(self.alert_system.get_setting('email_password', ''))
            else:
                self.logger.warning("No alert_system available for settings")
                
            self.logger.info("Settings loaded successfully")
                
        except Exception as e:
            self.logger.error(f"Error loading current settings: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
    
    def create_header_alignment_tab(self):
        """Create header alignment settings tab"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text="📊 Header Alignment")
        
        # Create scrollable frame with better colors
        canvas = tk.Canvas(tab_frame, bg=GUI_COLORS['background'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(tab_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=GUI_COLORS['background'])
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Header alignment section
        header_section = tk.LabelFrame(scrollable_frame, 
                                      text="📊 Technical Analysis Header Alignment", 
                                      bg=GUI_COLORS['panel_bg'], 
                                      fg=GUI_COLORS['info'], 
                                      font=FONTS['subheader'],
                                      relief='raised', bd=3)
        header_section.pack(fill='x', padx=PADDING['large'], pady=PADDING['large'])
        
        # Instructions
        instructions = tk.Label(header_section,
                               text="Fine-tune header positions to align perfectly with data columns.\n" +
                                    "Use +/- buttons to move headers left or right by pixels.",
                               bg=GUI_COLORS['panel_bg'],
                               fg=GUI_COLORS['text_secondary'],
                               font=FONTS['normal'],
                               justify='left')
        instructions.pack(pady=PADDING['medium'], padx=PADDING['large'])
        
        # Header adjustment controls
        headers = ["Ticker", "Price", "Change %", "RSI", "Signal", "Momentum"]
        self.header_adjustments = {}
        
        for i, header in enumerate(headers):
            # Frame for each header control
            control_frame = tk.Frame(header_section, bg=GUI_COLORS['panel_bg'], 
                                   relief='sunken', bd=2)
            control_frame.pack(fill='x', pady=PADDING['small'], padx=PADDING['large'])
            
            # Header name with color coding
            name_label = tk.Label(control_frame, text=f"🎯 {header}:", 
                                 bg=GUI_COLORS['panel_bg'], 
                                 fg=GUI_COLORS['accent'], 
                                 font=FONTS['normal'])
            name_label.pack(side='left', padx=(PADDING['medium'], PADDING['small']))
            
            # Current offset display
            current_offset = self._get_current_header_offset(header)
            
            offset_label = tk.Label(control_frame, text="Offset:", 
                                   bg=GUI_COLORS['panel_bg'], 
                                   fg=GUI_COLORS['text_primary'], 
                                   font=FONTS['normal'])
            offset_label.pack(side='left', padx=(PADDING['medium'], PADDING['small']))
            
            offset_display = tk.Label(control_frame, text=f"{current_offset:+d} px", 
                                     bg=GUI_COLORS['panel_bg'], 
                                     fg=GUI_COLORS['success'], 
                                     font=FONTS['normal'])
            offset_display.pack(side='left', padx=(0, PADDING['medium']))
            
            # Store the offset display for updates
            self.header_adjustments[header] = offset_display
            
            # Buttons frame
            buttons_frame = tk.Frame(control_frame, bg=GUI_COLORS['panel_bg'])
            buttons_frame.pack(side='right', padx=PADDING['medium'])
            
            # Row 1: Large movements
            button_row1 = tk.Frame(buttons_frame, bg=GUI_COLORS['panel_bg'])
            button_row1.pack(fill='x', pady=2)
            
            tk.Button(button_row1, text="←←← -20", 
                     command=lambda h=header, d=offset_display: self._adjust_header_in_settings(h, -20, d),
                     bg=GUI_COLORS['danger'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=1)
            
            tk.Button(button_row1, text="←← -5", 
                     command=lambda h=header, d=offset_display: self._adjust_header_in_settings(h, -5, d),
                     bg=GUI_COLORS['warning'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=1)
            
            tk.Button(button_row1, text="→→ +5",
                     command=lambda h=header, d=offset_display: self._adjust_header_in_settings(h, 5, d),
                     bg=GUI_COLORS['warning'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=1)
            
            tk.Button(button_row1, text="→→→ +20",
                     command=lambda h=header, d=offset_display: self._adjust_header_in_settings(h, 20, d),
                     bg=GUI_COLORS['danger'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=1)
            
            # Row 2: Fine movements and reset
            button_row2 = tk.Frame(buttons_frame, bg=GUI_COLORS['panel_bg'])
            button_row2.pack(fill='x', pady=2)
            
            tk.Button(button_row2, text="← -1", 
                     command=lambda h=header, d=offset_display: self._adjust_header_in_settings(h, -1, d),
                     bg=GUI_COLORS['accent'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=1)
            
            tk.Button(button_row2, text="→ +1",
                     command=lambda h=header, d=offset_display: self._adjust_header_in_settings(h, 1, d),
                     bg=GUI_COLORS['accent'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=1)
            
            tk.Button(button_row2, text="Reset",
                     command=lambda h=header, d=offset_display: self._reset_header_in_settings(h, d),
                     bg=GUI_COLORS['info'], fg='white', font=FONTS['small'],
                     relief='raised', bd=2).pack(side='left', padx=(5, 0))
        
        # Reset all headers button
        reset_all_frame = tk.Frame(header_section, bg=GUI_COLORS['panel_bg'], 
                                  relief='raised', bd=3)
        reset_all_frame.pack(fill='x', pady=PADDING['large'], padx=PADDING['large'])
        
        tk.Button(reset_all_frame, text="🔄 Reset All Headers", 
                 command=self._reset_all_headers_in_settings,
                 bg=GUI_COLORS['danger'], fg='white', font=FONTS['normal'],
                 relief='raised', bd=3, padx=PADDING['large'], 
                 pady=PADDING['small']).pack()
    
    def _get_current_header_offset(self, header: str) -> int:
        """Get current header offset from the main window"""
        try:
            if self.main_window and hasattr(self.main_window, 'get_header_offset'):
                return self.main_window.get_header_offset(header)
            return 0
        except Exception:
            return 0
    
    def _adjust_header_in_settings(self, header: str, adjustment: int, display_label):
        """Adjust header position and update display"""
        try:
            if self.main_window and hasattr(self.main_window, '_adjust_header_in_settings'):
                self.main_window._adjust_header_in_settings(header, adjustment, display_label)
            
        except Exception as e:
            self.logger.error(f"Error adjusting header {header}: {e}")
    
    def _reset_header_in_settings(self, header: str, display_label):
        """Reset header position and update display"""
        try:
            if self.main_window and hasattr(self.main_window, '_reset_header_in_settings'):
                self.main_window._reset_header_in_settings(header, display_label)
                        
        except Exception as e:
            self.logger.error(f"Error resetting header {header}: {e}")
    
    def _reset_all_headers_in_settings(self):
        """Reset all headers and update displays"""
        try:
            if self.main_window and hasattr(self.main_window, '_reset_all_headers_in_settings'):
                self.main_window._reset_all_headers_in_settings()
                
            # Update all displays
            for header, display_label in self.header_adjustments.items():
                current_offset = self._get_current_header_offset(header)
                display_label.config(text=f"{current_offset:+d} px")
                
        except Exception as e:
            self.logger.error(f"Error resetting all headers: {e}")
    
    def on_save(self):
        """Save settings and apply changes"""
        try:
            self.logger.info("Saving settings...")
            
            # Save refresh settings
            if self.auto_refresh_manager:
                self.logger.debug("Saving auto-refresh settings...")
                self.auto_refresh_manager.update_setting('auto_refresh_enabled', self.refresh_vars['enabled'].get())
                self.auto_refresh_manager.update_setting('refresh_interval_minutes', self.refresh_vars['interval'].get())
                self.auto_refresh_manager.update_setting('market_hours_only', self.refresh_vars['market_hours_only'].get())
                self.auto_refresh_manager.update_setting('weekend_refresh', self.refresh_vars['weekend_refresh'].get())
                
                # Restart refresh if enabled
                if self.refresh_vars['enabled'].get():
                    if not self.auto_refresh_manager.is_running():
                        self.auto_refresh_manager.start_auto_refresh()
                else:
                    if self.auto_refresh_manager.is_running():
                        self.auto_refresh_manager.stop_auto_refresh()
            
            # Save alert settings
            if self.alert_system:
                self.logger.debug("Saving alert settings...")
                self.alert_system.update_setting('visual_alerts_enabled', self.alert_vars['visual_enabled'].get())
                self.alert_system.update_setting('audio_alerts_enabled', self.alert_vars['audio_enabled'].get())
                self.alert_system.update_setting('sms_alerts_enabled', self.alert_vars['sms_enabled'].get())
                self.alert_system.update_setting('popup_duration_seconds', self.alert_vars['popup_duration'].get())
                self.alert_system.update_setting('cooldown_minutes', self.alert_vars['cooldown_minutes'].get())
                self.alert_system.update_setting('alert_on_rsi_extreme', self.alert_vars['alert_rsi_extreme'].get())
                self.alert_system.update_setting('rsi_extreme_threshold', self.alert_vars['rsi_threshold'].get())
                self.alert_system.update_setting('alert_on_signal_change', self.alert_vars['alert_signal_change'].get())
                self.alert_system.update_setting('alert_on_momentum_change', self.alert_vars['alert_momentum_change'].get())
                self.alert_system.update_setting('alert_on_opportunity_score_change', self.alert_vars['alert_opportunity_score'].get())
                self.alert_system.update_setting('opportunity_score_threshold', self.alert_vars['opportunity_threshold'].get())
                self.alert_system.update_setting('sms_phone_number', self.alert_vars['phone_number'].get())
                self.alert_system.update_setting('sms_provider', self.alert_vars['sms_provider'].get())
                
                # Save SMS provider credentials
                self.alert_system.update_setting('twilio_account_sid', self.alert_vars['twilio_account_sid'].get())
                self.alert_system.update_setting('twilio_auth_token', self.alert_vars['twilio_auth_token'].get())
                self.alert_system.update_setting('twilio_phone_number', self.alert_vars['twilio_from_number'].get())
                self.alert_system.update_setting('aws_access_key_id', self.alert_vars['aws_access_key'].get())
                self.alert_system.update_setting('aws_secret_access_key', self.alert_vars['aws_secret_key'].get())
                self.alert_system.update_setting('aws_region', self.alert_vars['aws_region'].get())
                
                # Auto-enable SMS if valid credentials are provided
                provider = self.alert_vars['sms_provider'].get()
                if provider == 'twilio':
                    sid = self.alert_vars['twilio_account_sid'].get()
                    token = self.alert_vars['twilio_auth_token'].get()
                    if sid and token:
                        self.alert_system.update_setting('sms_alerts_enabled', True)
                        self.alert_vars['sms_enabled'].set(True)  # Update the GUI checkbox too
                elif provider == 'aws_sns':
                    key = self.alert_vars['aws_access_key'].get()
                    secret = self.alert_vars['aws_secret_key'].get()
                    if key and secret:
                        self.alert_system.update_setting('sms_alerts_enabled', True)
                        self.alert_vars['sms_enabled'].set(True)  # Update the GUI checkbox too
                
                # Update SMS service with new credentials
                self.alert_system.update_sms_credentials()
                
                # Save email settings if email variables exist
                if hasattr(self, 'email_vars'):
                    self.alert_system.update_setting('email_alerts_enabled', self.email_vars['enabled'].get())
                    self.alert_system.update_setting('email_recipient', self.email_vars['recipient'].get())
                    self.alert_system.update_setting('email_provider', self.email_vars['provider'].get())
                    self.alert_system.update_setting('email_username', self.email_vars['username'].get())
                    self.alert_system.update_setting('email_password', self.email_vars['password'].get())
                    
                    # Auto-enable email if username, password, and recipient are provided
                    username = self.email_vars['username'].get()
                    password = self.email_vars['password'].get()
                    recipient = self.email_vars['recipient'].get()
                    if username and password and recipient and '@' in recipient:
                        self.alert_system.update_setting('email_alerts_enabled', True)
                        self.email_vars['enabled'].set(True)  # Update the GUI checkbox too
                    
                    # Update email service with new credentials
                    self.alert_system.update_email_credentials()
            
            self.logger.info("Settings saved successfully!")
            messagebox.showinfo("Settings Saved", "Settings have been saved and applied successfully!")
            self.dialog.destroy()
            
        except Exception as e:
            self.logger.error(f"Error saving settings: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            messagebox.showerror("Error", f"Error saving settings: {e}")
    
    def on_cancel(self):
        """Cancel settings dialog"""
        self.dialog.destroy()
    
    def on_reset(self):
        """Reset to default settings"""
        try:
            if messagebox.askyesno("Reset Settings", "Are you sure you want to reset all settings to defaults?"):
                # Reset refresh settings
                if self.auto_refresh_manager:
                    for key, value in self.auto_refresh_manager.default_settings.items():
                        self.auto_refresh_manager.update_setting(key, value)
                
                # Reset alert settings
                if self.alert_system:
                    for key, value in self.alert_system.default_settings.items():
                        self.alert_system.update_setting(key, value)
                
                # Reload GUI
                self.load_current_settings()
                messagebox.showinfo("Settings Reset", "All settings have been reset to defaults!")
                
        except Exception as e:
            self.logger.error(f"Error resetting settings: {e}")
            messagebox.showerror("Error", f"Error resetting settings: {e}")
    
    def manual_refresh(self):
        """Trigger manual refresh"""
        try:
            if self.auto_refresh_manager:
                success = self.auto_refresh_manager.manual_refresh()
                if success:
                    messagebox.showinfo("Manual Refresh", "Manual refresh completed successfully!")
                    # Update status
                    status = self.auto_refresh_manager.get_status()
                    status_text = f"Status: {'Running' if status.get('running') else 'Stopped'} | "
                    status_text += f"Last: {status.get('last_refresh', 'Never')} | "
                    status_text += f"Next: {status.get('next_refresh', 'Unknown')}"
                    self.refresh_status_label.config(text=status_text)
                else:
                    messagebox.showerror("Error", "Manual refresh failed!")
            else:
                messagebox.showwarning("Not Available", "Auto refresh manager not available")
                
        except Exception as e:
            self.logger.error(f"Error during manual refresh: {e}")
            messagebox.showerror("Error", f"Error during manual refresh: {e}")
    
    def _send_test_sms(self):
        """Send a test SMS message"""
        try:
            if not self.alert_system:
                messagebox.showwarning("Not Available", "Alert system not available")
                return
            
            phone_number = self.alert_vars['phone_number'].get()
            if not phone_number:
                messagebox.showwarning("Missing Phone", "Please enter a phone number first")
                return
                
            # Update the phone number in alert system first
            self.alert_system.update_setting('sms_phone_number', phone_number)
            
            # Send test SMS
            result = self.alert_system.send_test_sms()
            
            # Handle result safely
            if isinstance(result, dict) and result.get('success', False):
                messagebox.showinfo("SMS Test", "SMS Test sent successfully!")
                self.sms_status_label.config(text="SMS Test sent successfully", 
                                             fg=GUI_COLORS['success'])
            else:
                error_msg = result.get('error', 'Unknown error') if isinstance(result, dict) else str(result)
                messagebox.showerror("SMS Test Failed", f"Failed to send test SMS: {error_msg}")
                self.sms_status_label.config(text=f"Failed to send test SMS: {error_msg}", 
                                           fg=GUI_COLORS['error'])
                
        except Exception as e:
            self.logger.error(f"Error sending test SMS: {e}")
            messagebox.showerror("Error", f"Error sending test SMS: {e}")
            self.sms_status_label.config(text=f"Error: {e}", fg=GUI_COLORS['error'])
    
    def _check_sms_status(self):
        """Check SMS service status"""
        try:
            if not self.alert_system:
                messagebox.showwarning("Not Available", "Alert system not available")
                return
            
            status = self.alert_system.get_sms_service_status()
            
            # Update status label
            provider = status.get('current_provider', 'Unknown')
            if status.get('mock_mode', False):
                status_text = f"SMS service ready (Mock mode: {provider})"
                status_color = GUI_COLORS['warning']
            elif status.get('enabled', False):
                status_text = f"SMS service connected ({provider})"
                status_color = GUI_COLORS['success']
            else:
                status_text = f"SMS service disabled ({provider})"
                status_color = GUI_COLORS['error']
            
            self.sms_status_label.config(text=status_text, fg=status_color)
            
            # Show detailed status in message box
            detailed_status = (
                f"Provider: {provider}\n"
                f"Enabled: {'Yes' if status.get('enabled', False) else 'No'}\n"
                f"Mock Mode: {'Yes' if status.get('mock_mode', False) else 'No'}\n"
                f"SMS Alerts: {'Yes' if status.get('sms_alerts_enabled', False) else 'No'}\n"
                f"Phone Number: {status.get('phone_number', 'Not set')}\n"
                f"Twilio Available: {'Yes' if status.get('twilio_available', False) else 'No'}\n"
                f"AWS Available: {'Yes' if status.get('aws_available', False) else 'No'}"
            )
            
            messagebox.showinfo("SMS Service Status", detailed_status)
            
        except Exception as e:
            self.logger.error(f"Error checking SMS status: {e}")
            messagebox.showerror("Error", f"Error checking SMS status: {e}")


def show_settings_dialog(parent, auto_refresh_manager=None, alert_system=None, main_window=None):
    """Show the settings dialog"""
    dialog = SettingsDialog(parent, auto_refresh_manager, alert_system, main_window)
    return dialog


if __name__ == "__main__":
    # Test the settings dialog
    root = tk.Tk()
    root.title("Test")
    root.geometry("400x300")
    root.configure(bg='#2b2b2b')
    
    def open_settings():
        show_settings_dialog(root)
    
    tk.Button(root, text="Open Settings", command=open_settings).pack(pady=50)
    
    root.mainloop()
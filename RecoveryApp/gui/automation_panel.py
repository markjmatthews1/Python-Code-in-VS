"""
Automation Panel for RecoveryApp
Provides GUI interface for automation engine control and monitoring
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime, timedelta
import threading
import json
from typing import Dict, Any, Optional

# Import automation components
from utils.automation_engine import AutomationEngine, PersistenceManager, MarketHours
from utils.models import PortfolioManager
from utils.ui_utils import UIConfig, create_styled_button, create_styled_frame, create_styled_label

class AutomationPanel:
    """GUI panel for automation engine control and monitoring"""
    
    def __init__(self, parent_frame, portfolio_manager: PortfolioManager):
        self.parent_frame = parent_frame
        self.portfolio = portfolio_manager
        
        # Initialize automation components
        self.persistence = PersistenceManager()
        self.automation_engine = AutomationEngine(self.portfolio, self.persistence)
        
        # Add callback for updates
        self.automation_engine.add_update_callback(self.on_automation_update)
        
        # UI state
        self.status_update_timer = None
        
        self.create_interface()
        self.load_persisted_data()
        self.start_status_updates()
    
    def create_interface(self):
        """Create the automation panel interface"""
        # Main container
        self.main_frame = create_styled_frame(self.parent_frame)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Header
        self.create_header()
        
        # Control panel
        self.create_control_panel()
        
        # Status monitoring
        self.create_status_panel()
        
        # Schedule management
        self.create_schedule_panel()
        
        # Data management
        self.create_data_panel()
        
        # Activity log
        self.create_activity_log()
    
    def create_header(self):
        """Create header with title and market status"""
        header_frame = tk.Frame(self.main_frame, bg=UIConfig.COLORS['bg_primary'])
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title
        title_label = tk.Label(
            header_frame,
            text="🤖 Automation Engine",
            font=('Arial', 20, 'bold'),
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(side=tk.LEFT)
        
        # Market status
        self.market_status_frame = tk.Frame(header_frame, bg=UIConfig.COLORS['bg_primary'])
        self.market_status_frame.pack(side=tk.RIGHT)
        
        self.market_status_label = tk.Label(
            self.market_status_frame,
            text="Market Status: Checking...",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.market_status_label.pack(side=tk.RIGHT, padx=(0, 10))
        
        # Next market open
        self.next_open_label = tk.Label(
            self.market_status_frame,
            text="Next Open: Calculating...",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        self.next_open_label.pack(side=tk.RIGHT, padx=(0, 20))
    
    def create_control_panel(self):
        """Create automation control panel"""
        control_frame = create_styled_frame(self.main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            control_frame,
            text="Automation Control:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Control buttons
        button_frame = tk.Frame(control_frame, bg=UIConfig.COLORS['bg_secondary'])
        button_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.start_button = create_styled_button(
            button_frame, "🚀 Start Automation", self.start_automation,
            style='success'
        )
        self.start_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.stop_button = create_styled_button(
            button_frame, "⏹️ Stop Automation", self.stop_automation,
            style='danger'
        )
        self.stop_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.refresh_button = create_styled_button(
            button_frame, "🔄 Manual Refresh", self.manual_refresh,
            style='primary'
        )
        self.refresh_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.scan_button = create_styled_button(
            button_frame, "🔍 Market Scan", self.manual_scan,
            style='warning'
        )
        self.scan_button.pack(side=tk.LEFT)
        
        # Status indicator
        self.automation_status_label = tk.Label(
            button_frame,
            text="⚫ Automation: OFF",
            font=('Arial', 12, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.automation_status_label.pack(side=tk.RIGHT, padx=(20, 0))
    
    def create_status_panel(self):
        """Create status monitoring panel"""
        status_frame = create_styled_frame(self.main_frame)
        status_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            status_frame,
            text="System Status:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Status grid
        status_grid = tk.Frame(status_frame, bg=UIConfig.COLORS['bg_secondary'])
        status_grid.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Left column
        left_status = tk.Frame(status_grid, bg=UIConfig.COLORS['bg_secondary'])
        left_status.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.last_scan_label = tk.Label(
            left_status,
            text="Last Scan: Never",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.last_scan_label.pack(anchor=tk.W)
        
        self.portfolio_size_label = tk.Label(
            left_status,
            text="Portfolio Size: 0 positions",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.portfolio_size_label.pack(anchor=tk.W)
        
        self.scheduled_tasks_label = tk.Label(
            left_status,
            text="Scheduled Tasks: 0",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.scheduled_tasks_label.pack(anchor=tk.W)
        
        # Right column
        right_status = tk.Frame(status_grid, bg=UIConfig.COLORS['bg_secondary'])
        right_status.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        self.scan_interval_label = tk.Label(
            right_status,
            text="Scan Interval: 5 minutes",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.scan_interval_label.pack(anchor=tk.W)
        
        self.data_status_label = tk.Label(
            right_status,
            text="Data Status: Ready",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.data_status_label.pack(anchor=tk.W)
        
        self.uptime_label = tk.Label(
            right_status,
            text="Uptime: 00:00:00",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.uptime_label.pack(anchor=tk.W)
    
    def create_schedule_panel(self):
        """Create schedule management panel"""
        schedule_frame = create_styled_frame(self.main_frame)
        schedule_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            schedule_frame,
            text="Scheduled Operations:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Schedule list
        schedule_list_frame = tk.Frame(schedule_frame, bg=UIConfig.COLORS['bg_secondary'])
        schedule_list_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        # Treeview for schedule
        columns = ('Task', 'Schedule', 'Next Run', 'Status')
        
        self.schedule_tree = ttk.Treeview(schedule_list_frame, columns=columns, show='headings', height=6)
        
        for col in columns:
            self.schedule_tree.heading(col, text=col)
            self.schedule_tree.column(col, width=150)
        
        # Add sample scheduled tasks
        sample_tasks = [
            ('Daily Refresh', '09:00 daily', 'Tomorrow 09:00', 'Active'),
            ('Pre-market Prep', '08:00 daily', 'Tomorrow 08:00', 'Active'),
            ('End of Day Summary', '16:30 daily', 'Today 16:30', 'Active'),
            ('Weekly Review', 'Monday 08:30', 'Next Monday', 'Active'),
            ('Data Backup', '23:00 daily', 'Today 23:00', 'Active')
        ]
        
        for task in sample_tasks:
            self.schedule_tree.insert('', tk.END, values=task)
        
        self.schedule_tree.pack(fill=tk.X)
    
    def create_data_panel(self):
        """Create data management panel"""
        data_frame = create_styled_frame(self.main_frame)
        data_frame.pack(fill=tk.X, pady=(0, 15))
        
        tk.Label(
            data_frame,
            text="Data Management:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Data management buttons
        data_buttons = tk.Frame(data_frame, bg=UIConfig.COLORS['bg_secondary'])
        data_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        create_styled_button(
            data_buttons, "💾 Save Portfolio", self.save_portfolio,
            style='primary'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            data_buttons, "📁 Load Portfolio", self.load_portfolio,
            style='primary'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            data_buttons, "📊 Export Data", self.export_data,
            style='warning'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            data_buttons, "🗑️ Clear Cache", self.clear_cache,
            style='danger'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            data_buttons, "💾 Backup Now", self.backup_now,
            style='success'
        ).pack(side=tk.LEFT)
        
        # Data status info
        data_info = tk.Frame(data_frame, bg=UIConfig.COLORS['bg_secondary'])
        data_info.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        self.data_size_label = tk.Label(
            data_info,
            text="Data Directory: data/ (calculating size...)",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.data_size_label.pack(anchor=tk.W)
        
        self.last_backup_label = tk.Label(
            data_info,
            text="Last Backup: Never",
            font=('Arial', 10),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        )
        self.last_backup_label.pack(anchor=tk.W)
    
    def create_activity_log(self):
        """Create activity log display"""
        log_frame = create_styled_frame(self.main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        tk.Label(
            log_frame,
            text="Activity Log:",
            font=('Arial', 14, 'bold'),
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_secondary']
        ).pack(anchor=tk.W, padx=10, pady=(10, 5))
        
        # Log text area
        log_text_frame = tk.Frame(log_frame, bg=UIConfig.COLORS['bg_secondary'])
        log_text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.activity_log = scrolledtext.ScrolledText(
            log_text_frame,
            height=8,
            font=('Consolas', 9),
            bg=UIConfig.COLORS['bg_primary'],
            fg=UIConfig.COLORS['text_light'],
            wrap=tk.WORD
        )
        self.activity_log.pack(fill=tk.BOTH, expand=True)
        
        # Log control buttons
        log_buttons = tk.Frame(log_frame, bg=UIConfig.COLORS['bg_secondary'])
        log_buttons.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        create_styled_button(
            log_buttons, "🗑️ Clear Log", self.clear_activity_log,
            style='warning'
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        create_styled_button(
            log_buttons, "💾 Export Log", self.export_activity_log,
            style='primary'
        ).pack(side=tk.LEFT)
        
        # Add initial log entry
        self.log_activity("🤖 Automation Panel initialized")
    
    # Control Methods
    def start_automation(self):
        """Start the automation engine"""
        try:
            self.automation_engine.start_automation()
            self.automation_status_label.config(
                text="🟢 Automation: ON", 
                fg=UIConfig.COLORS['success']
            )
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.log_activity("🚀 Automation engine started")
        except Exception as e:
            messagebox.showerror("Automation Error", f"Failed to start automation: {str(e)}")
            self.log_activity(f"❌ Failed to start automation: {str(e)}")
    
    def stop_automation(self):
        """Stop the automation engine"""
        try:
            self.automation_engine.stop_automation()
            self.automation_status_label.config(
                text="⚫ Automation: OFF", 
                fg=UIConfig.COLORS['text_light']
            )
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.log_activity("⏹️ Automation engine stopped")
        except Exception as e:
            messagebox.showerror("Automation Error", f"Failed to stop automation: {str(e)}")
    
    def manual_refresh(self):
        """Trigger manual refresh"""
        self.log_activity("🔄 Manual refresh initiated...")
        threading.Thread(target=self.automation_engine.daily_refresh, daemon=True).start()
    
    def manual_scan(self):
        """Trigger manual market scan"""
        self.log_activity("🔍 Manual market scan initiated...")
        threading.Thread(target=self.automation_engine.market_hour_scan, daemon=True).start()
    
    # Data Management Methods
    def save_portfolio(self):
        """Save portfolio data"""
        try:
            success = self.persistence.save_portfolio(self.portfolio)
            if success:
                self.log_activity("💾 Portfolio saved successfully")
                messagebox.showinfo("Save Complete", "Portfolio saved successfully")
            else:
                messagebox.showerror("Save Error", "Failed to save portfolio")
        except Exception as e:
            messagebox.showerror("Save Error", f"Error saving portfolio: {str(e)}")
    
    def load_portfolio(self):
        """Load portfolio data"""
        try:
            self.portfolio = self.persistence.load_portfolio()
            self.log_activity(f"📁 Portfolio loaded: {len(self.portfolio.positions)} positions")
            messagebox.showinfo("Load Complete", f"Portfolio loaded: {len(self.portfolio.positions)} positions")
            self.update_status_display()
        except Exception as e:
            messagebox.showerror("Load Error", f"Error loading portfolio: {str(e)}")
    
    def export_data(self):
        """Export all data"""
        try:
            export_file = f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            
            export_data = {
                'portfolio': [pos.__dict__ for pos in self.portfolio.positions],
                'recovery_status': self.persistence.load_recovery_status(),
                'export_timestamp': datetime.now().isoformat()
            }
            
            with open(export_file, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            self.log_activity(f"📊 Data exported to {export_file}")
            messagebox.showinfo("Export Complete", f"Data exported to {export_file}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting data: {str(e)}")
    
    def clear_cache(self):
        """Clear cached data"""
        if messagebox.askyesno("Clear Cache", "Are you sure you want to clear all cached data?"):
            try:
                # Clear cache files
                import os
                cache_file = self.persistence.market_data_cache
                if os.path.exists(cache_file):
                    os.remove(cache_file)
                
                self.log_activity("🗑️ Cache cleared")
                messagebox.showinfo("Cache Cleared", "Cache has been cleared")
            except Exception as e:
                messagebox.showerror("Cache Error", f"Error clearing cache: {str(e)}")
    
    def backup_now(self):
        """Trigger immediate backup"""
        self.log_activity("💾 Manual backup initiated...")
        threading.Thread(target=self.automation_engine.backup_data, daemon=True).start()
    
    # Status Update Methods
    def start_status_updates(self):
        """Start periodic status updates"""
        self.update_status_display()
        self.status_update_timer = self.main_frame.after(5000, self.start_status_updates)  # Update every 5 seconds
    
    def update_status_display(self):
        """Update all status displays"""
        try:
            # Market status
            if MarketHours.is_market_open():
                self.market_status_label.config(
                    text="🟢 Market: OPEN", 
                    fg=UIConfig.COLORS['success']
                )
            else:
                self.market_status_label.config(
                    text="🔴 Market: CLOSED", 
                    fg=UIConfig.COLORS['danger']
                )
            
            # Next market open
            next_open = MarketHours.next_market_open()
            self.next_open_label.config(
                text=f"Next Open: {next_open.strftime('%m/%d %H:%M')}"
            )
            
            # Portfolio size
            self.portfolio_size_label.config(
                text=f"Portfolio Size: {len(self.portfolio.positions)} positions"
            )
            
            # Get automation status
            status = self.automation_engine.get_status()
            
            # Update status labels
            if status.get('last_scan'):
                scan_time = datetime.fromisoformat(status['last_scan']).strftime('%H:%M:%S')
                self.last_scan_label.config(text=f"Last Scan: {scan_time}")
            
            self.scheduled_tasks_label.config(
                text=f"Scheduled Tasks: {status.get('scheduled_tasks', 0)}"
            )
            
        except Exception as e:
            self.log_activity(f"⚠️ Status update error: {str(e)}")
    
    def on_automation_update(self):
        """Callback for automation updates"""
        self.log_activity("🔄 Automation update received")
        self.update_status_display()
    
    # Logging Methods
    def log_activity(self, message: str):
        """Add message to activity log"""
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_entry = f"[{timestamp}] {message}\\n"
        
        self.activity_log.insert(tk.END, log_entry)
        self.activity_log.see(tk.END)
    
    def clear_activity_log(self):
        """Clear the activity log"""
        self.activity_log.delete(1.0, tk.END)
        self.log_activity("📋 Activity log cleared")
    
    def export_activity_log(self):
        """Export activity log to file"""
        try:
            log_content = self.activity_log.get(1.0, tk.END)
            log_file = f"activity_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            
            with open(log_file, 'w') as f:
                f.write(log_content)
            
            self.log_activity(f"💾 Activity log exported to {log_file}")
            messagebox.showinfo("Export Complete", f"Activity log exported to {log_file}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Error exporting log: {str(e)}")
    
    # Data Loading
    def load_persisted_data(self):
        """Load any persisted data on startup"""
        try:
            # Load portfolio if exists
            if hasattr(self.persistence, 'portfolio_file'):
                import os
                if os.path.exists(self.persistence.portfolio_file):
                    loaded_portfolio = self.persistence.load_portfolio()
                    if loaded_portfolio.positions:
                        self.portfolio.positions = loaded_portfolio.positions
                        self.log_activity(f"📁 Loaded {len(self.portfolio.positions)} positions from storage")
        except Exception as e:
            self.log_activity(f"⚠️ Error loading persisted data: {str(e)}")
    
    def cleanup(self):
        """Cleanup when panel is closed"""
        if self.status_update_timer:
            self.main_frame.after_cancel(self.status_update_timer)
        
        self.automation_engine.stop_automation()
        self.log_activity("🛑 Automation panel shutting down")
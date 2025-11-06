"""
Monitoring Service Dialog for Catalyst Scanner

Provides GUI interface to manage the background monitoring service
with the same 5 options as the terminal interface.

Author: Investment Catalyst Team
Date: October 3, 2025
"""

import tkinter as tk
from tkinter import ttk, messagebox
import subprocess
import threading
import os
import json
import sys
from datetime import datetime

from gui.gui_styles import (
    apply_theme_to_root, create_themed_frame, create_themed_label, 
    create_themed_button, GUI_COLORS, FONTS, PADDING
)


class MonitoringServiceDialog:
    """Dialog for managing the background monitoring service"""
    
    def __init__(self, parent):
        """Initialize the monitoring service dialog"""
        self.parent = parent
        self.dialog = None
        self.status_label = None
        self.log_text = None
        self.service_running = False
        
        # Get the catalyst_scanner root directory
        self.catalyst_root = self._get_catalyst_root()
        
    def _get_catalyst_root(self):
        """Get the catalyst_scanner root directory"""
        current_file = os.path.abspath(__file__)
        # Navigate up from gui/ to catalyst_scanner/
        gui_dir = os.path.dirname(current_file)
        catalyst_root = os.path.dirname(gui_dir)
        return catalyst_root
        
    def show_dialog(self):
        """Show the monitoring service management dialog"""
        # Create dialog window
        self.dialog = tk.Toplevel(self.parent)
        self.dialog.title("🎯 Background Monitoring Service Manager")
        self.dialog.geometry("600x500")
        self.dialog.resizable(True, True)
        
        # Apply theme
        apply_theme_to_root(self.dialog)
        
        # Configure grid
        self.dialog.grid_rowconfigure(1, weight=1)
        self.dialog.grid_columnconfigure(0, weight=1)
        
        # Create header
        self.create_header()
        
        # Create main content area
        self.create_content_area()
        
        # Create button area
        self.create_button_area()
        
        # Initialize status
        self.refresh_status()
        
        # Center dialog on parent
        self.dialog.transient(self.parent)
        self.dialog.grab_set()
        
    def create_header(self):
        """Create the dialog header"""
        header_frame = create_themed_frame(self.dialog, style='accent')
        header_frame.grid(row=0, column=0, sticky='ew', padx=PADDING['medium'], pady=PADDING['medium'])
        header_frame.grid_columnconfigure(1, weight=1)
        
        # Title
        title_label = create_themed_label(header_frame, 
                                        "🎯 Background Monitoring Service", 
                                        style='header')
        title_label.grid(row=0, column=0, padx=PADDING['medium'], pady=PADDING['small'], sticky='w')
        
        # Status indicator
        self.status_label = create_themed_label(header_frame, 
                                               "Status: Checking...", 
                                               style='normal')
        self.status_label.grid(row=0, column=1, padx=PADDING['medium'], pady=PADDING['small'], sticky='e')
        
    def create_content_area(self):
        """Create the main content area with status and logs"""
        content_frame = create_themed_frame(self.dialog, style='normal')
        content_frame.grid(row=1, column=0, sticky='nsew', padx=PADDING['medium'], pady=(0, PADDING['medium']))
        content_frame.grid_rowconfigure(1, weight=1)
        content_frame.grid_columnconfigure(0, weight=1)
        
        # Service info
        info_frame = create_themed_frame(content_frame, style='panel')
        info_frame.grid(row=0, column=0, sticky='ew', pady=(0, PADDING['medium']))
        info_frame.grid_columnconfigure(0, weight=1)
        
        info_text = """
🔍 Portfolio Monitoring: 14 Bryan Perry tickers
⏰ Check Interval: 5 minutes  
🚨 Alert Thresholds: High (7.5+), Critical (8.5+)
📱 Notifications: Email, SMS, System alerts
        """.strip()
        
        info_label = create_themed_label(info_frame, info_text, style='normal')
        info_label.grid(row=0, column=0, padx=PADDING['medium'], pady=PADDING['medium'], sticky='w')
        
        # Log display
        log_frame = create_themed_frame(content_frame, style='panel')
        log_frame.grid(row=1, column=0, sticky='nsew')
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)
        
        log_label = create_themed_label(log_frame, "📝 Recent Activity:", style='subheader')
        log_label.grid(row=0, column=0, padx=PADDING['medium'], pady=(PADDING['medium'], PADDING['small']), sticky='w')
        
        # Text widget for logs
        self.log_text = tk.Text(log_frame, 
                               height=12, 
                               bg=GUI_COLORS['background'],
                               fg=GUI_COLORS['text_primary'],
                               font=FONTS['mono_small'],
                               wrap=tk.WORD)
        self.log_text.grid(row=1, column=0, sticky='nsew', padx=PADDING['medium'], pady=(0, PADDING['medium']))
        
        # Scrollbar for logs
        scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        scrollbar.grid(row=1, column=1, sticky='ns', pady=(0, PADDING['medium']))
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
    def create_button_area(self):
        """Create the button area with service controls"""
        button_frame = create_themed_frame(self.dialog, style='accent')
        button_frame.grid(row=2, column=0, sticky='ew', padx=PADDING['medium'], pady=(0, PADDING['medium']))
        
        # Service control buttons
        start_btn = create_themed_button(button_frame, "🚀 Start Service", 
                                       command=self.start_service,
                                       style='action')
        start_btn.grid(row=0, column=0, padx=(PADDING['medium'], PADDING['small']), pady=PADDING['small'])
        
        stop_btn = create_themed_button(button_frame, "🛑 Stop Service", 
                                      command=self.stop_service,
                                      style='warning')
        stop_btn.grid(row=0, column=1, padx=PADDING['small'], pady=PADDING['small'])
        
        status_btn = create_themed_button(button_frame, "📊 Refresh Status", 
                                        command=self.refresh_status,
                                        style='normal')
        status_btn.grid(row=0, column=2, padx=PADDING['small'], pady=PADDING['small'])
        
        config_btn = create_themed_button(button_frame, "⚙️ Check Config", 
                                        command=self.check_configuration,
                                        style='normal')
        config_btn.grid(row=0, column=3, padx=PADDING['small'], pady=PADDING['small'])
        
        close_btn = create_themed_button(button_frame, "❌ Close", 
                                       command=self.close_dialog,
                                       style='normal')
        close_btn.grid(row=0, column=4, padx=(PADDING['small'], PADDING['medium']), pady=PADDING['small'])
        
    def start_service(self):
        """Start the background monitoring service"""
        def run_start():
            try:
                self.log_message("🚀 Starting background monitoring service...")
                
                # Check if already running
                if self.check_service_running():
                    self.log_message("⚠️ Service appears to be already running")
                    messagebox.showwarning("Service Running", "The monitoring service appears to be already running.")
                    return
                
                # Start the service
                if os.name == 'nt':  # Windows
                    subprocess.Popen(['python', 'start_monitoring.py'], 
                                   creationflags=subprocess.CREATE_NEW_CONSOLE,
                                   cwd=self.catalyst_root)
                else:  # Unix/Linux
                    subprocess.Popen(['python', 'start_monitoring.py'],
                                   cwd=self.catalyst_root)
                
                self.log_message("✅ Service start command sent")
                self.log_message("💡 Check the new console window for service status")
                
                # Update status after a delay
                self.dialog.after(3000, self.refresh_status)
                
            except Exception as e:
                error_msg = f"❌ Failed to start service: {e}"
                self.log_message(error_msg)
                messagebox.showerror("Start Error", f"Failed to start monitoring service:\n{e}")
        
        # Run in thread to prevent GUI blocking
        threading.Thread(target=run_start, daemon=True).start()
        
    def stop_service(self):
        """Stop the background monitoring service"""
        def run_stop():
            try:
                self.log_message("🛑 Stopping background monitoring service...")
                
                if os.name == 'nt':  # Windows
                    # More targeted approach - kill python processes running monitoring
                    result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                          capture_output=True, text=True)
                    if 'python.exe' in result.stdout:
                        subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                                     capture_output=True)
                        self.log_message("✅ Service stop command sent")
                    else:
                        self.log_message("ℹ️ No Python processes found")
                else:  # Unix/Linux
                    subprocess.run(['pkill', '-f', 'background_monitoring'], 
                                 capture_output=True)
                    self.log_message("✅ Service stop command sent")
                
                # Update status after a delay
                self.dialog.after(2000, self.refresh_status)
                
            except Exception as e:
                error_msg = f"❌ Failed to stop service: {e}"
                self.log_message(error_msg)
                messagebox.showerror("Stop Error", f"Failed to stop monitoring service:\n{e}")
        
        # Run in thread to prevent GUI blocking
        threading.Thread(target=run_stop, daemon=True).start()
        
    def refresh_status(self):
        """Refresh the service status display"""
        def run_refresh():
            try:
                # Check if service is running
                is_running = self.check_service_running()
                self.service_running = is_running
                
                # Update status label
                if is_running:
                    status_text = "Status: ✅ RUNNING"
                    status_color = GUI_COLORS['success']
                else:
                    status_text = "Status: ❌ STOPPED"
                    status_color = GUI_COLORS['danger']
                
                # Update UI in main thread
                self.dialog.after(0, lambda: self.update_status_ui(status_text, status_color))
                
                # Load recent logs
                self.load_recent_logs()
                
            except Exception as e:
                self.log_message(f"❌ Error checking status: {e}")
        
        # Run in thread to prevent GUI blocking
        threading.Thread(target=run_refresh, daemon=True).start()
        
    def update_status_ui(self, status_text, status_color):
        """Update the status UI elements"""
        if self.status_label:
            self.status_label.configure(text=status_text, foreground=status_color)
        
    def check_service_running(self):
        """Check if the monitoring service is running"""
        try:
            if os.name == 'nt':  # Windows
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                      capture_output=True, text=True)
                return 'python.exe' in result.stdout
            else:  # Unix/Linux
                result = subprocess.run(['pgrep', '-f', 'background_monitoring'], 
                                      capture_output=True, text=True)
                return bool(result.stdout.strip())
        except:
            return False
    
    def check_configuration(self):
        """Check and display service configuration"""
        def run_check():
            try:
                self.log_message("🔍 Checking service configuration...")
                
                # Check config file
                config_file = os.path.join(self.catalyst_root, 'config', 'monitoring_service.json')
                
                if os.path.exists(config_file):
                    with open(config_file, 'r') as f:
                        config = json.load(f)
                    
                    self.log_message("✅ Configuration file found")
                    self.log_message(f"   • Monitoring enabled: {config.get('monitoring_enabled', False)}")
                    self.log_message(f"   • Check interval: {config.get('check_interval_minutes', 5)} minutes")
                    self.log_message(f"   • Portfolio tickers: {len(config.get('portfolio_tickers', []))}")
                    self.log_message(f"   • Market hours only: {config.get('market_hours_only', True)}")
                else:
                    self.log_message("⚠️ Configuration file not found")
                
                # Run configuration check script
                check_script = os.path.join(self.catalyst_root, 'check_service_status.py')
                if os.path.exists(check_script):
                    self.log_message("🧪 Running configuration test...")
                    result = subprocess.run(['python', check_script], 
                                          capture_output=True, text=True, cwd=os.path.dirname(check_script))
                    if result.stdout:
                        for line in result.stdout.split('\n')[:10]:  # First 10 lines
                            if line.strip():
                                self.log_message(f"   {line}")
                
            except Exception as e:
                self.log_message(f"❌ Error checking configuration: {e}")
        
        # Run in thread to prevent GUI blocking
        threading.Thread(target=run_check, daemon=True).start()
        
    def load_recent_logs(self):
        """Load recent log entries"""
        try:
            # Try to find the most recent log file
            log_dir = os.path.join(self.catalyst_root, 'logs')
            if os.path.exists(log_dir):
                log_files = [f for f in os.listdir(log_dir) if f.startswith('monitoring_service_')]
                if log_files:
                    latest_log = max(log_files)
                    log_path = os.path.join(log_dir, latest_log)
                    
                    with open(log_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-20:]  # Last 20 lines
                        
                    # Update log display in main thread
                    self.dialog.after(0, lambda: self.update_log_display(recent_lines))
                    return
            
            # Also check for main log file
            main_log = os.path.join(self.catalyst_root, 'monitoring_service.log')
            if os.path.exists(main_log):
                with open(main_log, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    recent_lines = lines[-20:]  # Last 20 lines
                    
                # Update log display in main thread
                self.dialog.after(0, lambda: self.update_log_display(recent_lines))
                
        except Exception as e:
            self.log_message(f"Could not load logs: {e}")
    
    def update_log_display(self, lines):
        """Update the log display with new lines"""
        if self.log_text:
            self.log_text.delete(1.0, tk.END)
            for line in lines:
                self.log_text.insert(tk.END, line)
            self.log_text.see(tk.END)
    
    def log_message(self, message):
        """Add a message to the log display"""
        if self.log_text:
            timestamp = datetime.now().strftime("%H:%M:%S")
            log_entry = f"[{timestamp}] {message}\n"
            self.log_text.insert(tk.END, log_entry)
            self.log_text.see(tk.END)
    
    def close_dialog(self):
        """Close the dialog"""
        if self.dialog:
            self.dialog.destroy()


def show_monitoring_service_dialog(parent):
    """Show the monitoring service dialog"""
    dialog = MonitoringServiceDialog(parent)
    dialog.show_dialog()
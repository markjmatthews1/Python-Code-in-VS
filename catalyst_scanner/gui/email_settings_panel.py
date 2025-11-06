"""
Email Settings GUI Integration for Catalyst Scanner
==================================================
Adds email configuration to the settings dialog.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import logging
from typing import Dict
import threading


class EmailSettingsPanel:
    """
    Email settings panel for the Catalyst Scanner settings dialog
    """
    
    def __init__(self, parent_frame, alert_system=None, on_settings_changed=None):
        self.parent_frame = parent_frame
        self.alert_system = alert_system
        self.email_service = alert_system.email_service if alert_system else None
        self.on_change_callback = on_settings_changed
        self.logger = logging.getLogger(__name__)
        
        # Variables for form fields
        self.vars = {}
        self.test_in_progress = False
        
        # Create the email settings section
        self.create_email_settings()
        
        # Load current settings
        self.load_current_settings()
    
    def create_email_settings(self):
        """Create the email settings UI components"""
        
        # Main email frame
        email_frame = ttk.LabelFrame(self.parent_frame, text="📧 Email Alert Settings", padding="10")
        email_frame.pack(fill="x", padx=10, pady=5)
        
        # Enable/disable email alerts
        self.vars['enabled'] = tk.BooleanVar()
        enabled_frame = ttk.Frame(email_frame)
        enabled_frame.pack(fill="x", pady=2)
        
        ttk.Checkbutton(enabled_frame, text="Enable Email Alerts", 
                       variable=self.vars['enabled'],
                       command=self._on_enabled_changed).pack(side="left")
        
        # Test mode checkbox
        self.vars['test_mode'] = tk.BooleanVar()
        ttk.Checkbutton(enabled_frame, text="Test Mode (no actual emails)", 
                       variable=self.vars['test_mode'],
                       command=self._on_setting_changed).pack(side="right")
        
        # Provider selection
        provider_frame = ttk.Frame(email_frame)
        provider_frame.pack(fill="x", pady=5)
        
        ttk.Label(provider_frame, text="Email Provider:").pack(side="left")
        self.vars['provider'] = tk.StringVar()
        provider_combo = ttk.Combobox(provider_frame, textvariable=self.vars['provider'],
                                    values=["gmail", "outlook", "yahoo", "custom"],
                                    state="readonly", width=15)
        provider_combo.pack(side="left", padx=(5, 10))
        provider_combo.bind('<<ComboboxSelected>>', self._on_provider_changed)
        
        # Help button for provider setup
        help_btn = ttk.Button(provider_frame, text="Setup Help", 
                            command=self._show_setup_help, width=12)
        help_btn.pack(side="right")
        
        # Email credentials section
        creds_frame = ttk.LabelFrame(email_frame, text="Email Credentials", padding="5")
        creds_frame.pack(fill="x", pady=5)
        
        # Sender email
        sender_frame = ttk.Frame(creds_frame)
        sender_frame.pack(fill="x", pady=2)
        ttk.Label(sender_frame, text="Your Email:", width=15).pack(side="left")
        self.vars['sender_email'] = tk.StringVar()
        sender_entry = ttk.Entry(sender_frame, textvariable=self.vars['sender_email'], width=30)
        sender_entry.pack(side="left", padx=(5, 0))
        sender_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Sender password (app password)
        password_frame = ttk.Frame(creds_frame)
        password_frame.pack(fill="x", pady=2)
        ttk.Label(password_frame, text="App Password:", width=15).pack(side="left")
        self.vars['sender_password'] = tk.StringVar()
        password_entry = ttk.Entry(password_frame, textvariable=self.vars['sender_password'], 
                                 show="*", width=30)
        password_entry.pack(side="left", padx=(5, 0))
        password_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Recipient email
        recipient_frame = ttk.Frame(creds_frame)
        recipient_frame.pack(fill="x", pady=2)
        ttk.Label(recipient_frame, text="Send Alerts To:", width=15).pack(side="left")
        self.vars['recipient_email'] = tk.StringVar()
        recipient_entry = ttk.Entry(recipient_frame, textvariable=self.vars['recipient_email'], width=30)
        recipient_entry.pack(side="left", padx=(5, 0))
        recipient_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Alert preferences section
        prefs_frame = ttk.LabelFrame(email_frame, text="Alert Preferences", padding="5")
        prefs_frame.pack(fill="x", pady=5)
        
        # Subject prefix
        subject_frame = ttk.Frame(prefs_frame)
        subject_frame.pack(fill="x", pady=2)
        ttk.Label(subject_frame, text="Subject Prefix:", width=15).pack(side="left")
        self.vars['subject_prefix'] = tk.StringVar()
        subject_entry = ttk.Entry(subject_frame, textvariable=self.vars['subject_prefix'], width=25)
        subject_entry.pack(side="left", padx=(5, 0))
        subject_entry.bind('<KeyRelease>', self._on_setting_changed)
        
        # Daily limit
        limit_frame = ttk.Frame(prefs_frame)
        limit_frame.pack(fill="x", pady=2)
        ttk.Label(limit_frame, text="Daily Limit:", width=15).pack(side="left")
        self.vars['daily_limit'] = tk.StringVar()
        limit_spin = ttk.Spinbox(limit_frame, textvariable=self.vars['daily_limit'], 
                               from_=1, to=500, width=10)
        limit_spin.pack(side="left", padx=(5, 10))
        limit_spin.bind('<KeyRelease>', self._on_setting_changed)
        
        # Rate limit
        ttk.Label(limit_frame, text="Rate Limit (min):").pack(side="left")
        self.vars['rate_limit_minutes'] = tk.StringVar()
        rate_spin = ttk.Spinbox(limit_frame, textvariable=self.vars['rate_limit_minutes'],
                              from_=1, to=60, width=10)
        rate_spin.pack(side="left", padx=(5, 0))
        rate_spin.bind('<KeyRelease>', self._on_setting_changed)
        
        # Action buttons
        button_frame = ttk.Frame(email_frame)
        button_frame.pack(fill="x", pady=10)
        
        # Test connection button
        self.test_btn = ttk.Button(button_frame, text="Test Connection", 
                                 command=self._test_connection, width=15)
        self.test_btn.pack(side="left", padx=(0, 5))
        
        # Send test email button
        self.test_email_btn = ttk.Button(button_frame, text="Send Test Email", 
                                       command=self._send_test_email, width=15)
        self.test_email_btn.pack(side="left", padx=5)
        
        # Status label
        self.status_label = ttk.Label(button_frame, text="", foreground="gray")
        self.status_label.pack(side="right")
        
        # Store references to enable/disable widgets
        self.email_widgets = [
            provider_combo, sender_entry, password_entry, recipient_entry,
            subject_entry, limit_spin, rate_spin, self.test_btn, self.test_email_btn
        ]
    
    def load_current_settings(self):
        """Load current email settings into the form"""
        
        config = self.email_service.config
        
        # Set values from config
        self.vars['enabled'].set(config.get('enabled', False))
        self.vars['test_mode'].set(config.get('test_mode', True))
        self.vars['provider'].set(config.get('provider', 'gmail'))
        self.vars['sender_email'].set(config.get('sender_email', ''))
        self.vars['sender_password'].set(config.get('sender_password', ''))
        self.vars['recipient_email'].set(config.get('recipient_email', ''))
        self.vars['subject_prefix'].set(config.get('subject_prefix', '[Catalyst Alert]'))
        self.vars['daily_limit'].set(str(config.get('daily_limit', 100)))
        self.vars['rate_limit_minutes'].set(str(config.get('rate_limit_minutes', 2)))
        
        # Update widget states
        self._on_enabled_changed()
    
    def save_settings(self):
        """Save current form values to email service configuration"""
        
        try:
            # Update email service config
            self.email_service.config['enabled'] = self.vars['enabled'].get()
            self.email_service.config['test_mode'] = self.vars['test_mode'].get()
            self.email_service.config['provider'] = self.vars['provider'].get()
            self.email_service.config['sender_email'] = self.vars['sender_email'].get().strip()
            self.email_service.config['sender_password'] = self.vars['sender_password'].get()
            self.email_service.config['recipient_email'] = self.vars['recipient_email'].get().strip()
            self.email_service.config['subject_prefix'] = self.vars['subject_prefix'].get().strip()
            
            # Convert string values to integers
            try:
                self.email_service.config['daily_limit'] = int(self.vars['daily_limit'].get())
            except ValueError:
                self.email_service.config['daily_limit'] = 100
                
            try:
                self.email_service.config['rate_limit_minutes'] = int(self.vars['rate_limit_minutes'].get())
            except ValueError:
                self.email_service.config['rate_limit_minutes'] = 2
            
            # Save to file
            self.email_service.save_config()
            
            self.logger.info("Email settings saved successfully")
            self._update_status("Settings saved ✓", "green")
            
        except Exception as e:
            self.logger.error(f"Error saving email settings: {e}")
            self._update_status("Save failed ✗", "red")
    
    def _on_enabled_changed(self):
        """Handle email enabled/disabled state change"""
        
        enabled = self.vars['enabled'].get()
        
        # Enable/disable all email widgets
        state = "normal" if enabled else "disabled"
        for widget in self.email_widgets:
            widget.configure(state=state)
        
        if enabled:
            self._update_status("Email alerts enabled", "blue")
        else:
            self._update_status("Email alerts disabled", "gray")
        
        self._on_setting_changed()
    
    def _on_provider_changed(self, event=None):
        """Handle email provider change"""
        
        provider = self.vars['provider'].get()
        
        # Auto-update SMTP settings based on provider
        if provider in self.email_service.smtp_providers:
            provider_settings = self.email_service.smtp_providers[provider]
            self.email_service.config.update(provider_settings)
            self._update_status(f"Provider set to {provider.title()}", "blue")
        
        self._on_setting_changed()
    
    def _on_setting_changed(self, event=None):
        """Handle any setting change"""
        
        if self.on_change_callback:
            self.on_change_callback()
    
    def _test_connection(self):
        """Test email server connection"""
        
        if self.test_in_progress:
            return
        
        def test_thread():
            self.test_in_progress = True
            try:
                # Save current settings first
                self.save_settings()
                
                # Test connection
                self._update_status("Testing connection...", "blue")
                success, message = self.email_service.test_connection()
                
                if success:
                    self._update_status("Connection successful ✓", "green")
                    messagebox.showinfo("Connection Test", "Email connection successful!")
                else:
                    self._update_status("Connection failed ✗", "red")
                    messagebox.showerror("Connection Test", f"Connection failed:\\n{message}")
                    
            except Exception as e:
                self._update_status("Test error ✗", "red")
                messagebox.showerror("Connection Test", f"Test error:\\n{e}")
            finally:
                self.test_in_progress = False
        
        # Run test in background thread
        threading.Thread(target=test_thread, daemon=True).start()
    
    def _send_test_email(self):
        """Send a test email"""
        
        if self.test_in_progress:
            return
        
        def send_thread():
            self.test_in_progress = True
            try:
                # Save current settings first
                self.save_settings()
                
                # Send test email
                self._update_status("Sending test email...", "blue")
                success = self.email_service.send_test_email()
                
                if success:
                    if self.email_service.config['test_mode']:
                        self._update_status("Test email simulated ✓", "green")
                        messagebox.showinfo("Test Email", "Test email simulated successfully!\\n(Test mode is enabled)")
                    else:
                        self._update_status("Test email sent ✓", "green")
                        messagebox.showinfo("Test Email", "Test email sent successfully!")
                else:
                    self._update_status("Test email failed ✗", "red")
                    messagebox.showerror("Test Email", "Failed to send test email. Check your settings.")
                    
            except Exception as e:
                self._update_status("Test error ✗", "red")
                messagebox.showerror("Test Email", f"Test error:\\n{e}")
            finally:
                self.test_in_progress = False
        
        # Run test in background thread
        threading.Thread(target=send_thread, daemon=True).start()
    
    def _show_setup_help(self):
        """Show email provider setup instructions"""
        
        provider = self.vars['provider'].get()
        instructions = self.email_service.get_setup_instructions()
        
        help_text = instructions.get(provider, "No setup instructions available for this provider.")
        
        # Create help window
        help_window = tk.Toplevel(self.parent_frame)
        help_window.title(f"{provider.title()} Setup Instructions")
        help_window.geometry("600x400")
        help_window.transient(self.parent_frame)
        help_window.grab_set()
        
        # Add text widget with instructions
        text_frame = ttk.Frame(help_window)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        text_widget = tk.Text(text_frame, wrap="word", font=("Consolas", 10))
        scrollbar = ttk.Scrollbar(text_frame, orient="vertical", command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        text_widget.insert("1.0", help_text)
        text_widget.configure(state="disabled")
        
        # Close button
        close_btn = ttk.Button(help_window, text="Close", command=help_window.destroy)
        close_btn.pack(pady=10)
    
    def _update_status(self, message: str, color: str = "black"):
        """Update the status label"""
        
        self.status_label.configure(text=message, foreground=color)
        
        # Auto-clear status after 5 seconds
        self.parent_frame.after(5000, lambda: self.status_label.configure(text=""))


# Test the email settings panel
if __name__ == "__main__":
    print("🧪 Testing Email Settings Panel...")
    
    # Create test window
    root = tk.Tk()
    root.title("Email Settings Test")
    root.geometry("700x600")
    
    # Import email service
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(__file__)))
    
    from alerts.email_service_fixed import EmailService
    
    # Create email service
    email_service = EmailService()
    
    # Create main frame
    main_frame = ttk.Frame(root)
    main_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    # Create email settings panel
    email_panel = EmailSettingsPanel(main_frame, email_service)
    
    # Add save button for testing
    save_btn = ttk.Button(main_frame, text="Save Settings", 
                         command=email_panel.save_settings)
    save_btn.pack(pady=10)
    
    print("📧 Email settings panel created")
    print("📧 Test the interface and configuration")
    
    root.mainloop()
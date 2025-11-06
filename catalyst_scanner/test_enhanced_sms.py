"""
Enhanced SMS Settings Test
Test the improved SMS settings with better visibility
"""

import sys
import os

# Add the project directory to the path
project_dir = r'c:\Users\mjmat\Python Code in VS\catalyst_scanner'
if project_dir not in sys.path:
    sys.path.insert(0, project_dir)

import tkinter as tk
from tkinter import ttk, messagebox

# Import GUI styles
try:
    from gui.gui_styles import GUI_COLORS, FONTS, PADDING
except ImportError:
    # Fallback colors
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

def test_sms_functionality():
    """Test SMS settings with mock functionality"""
    # Mock alert system for testing
    class MockAlertSystem:
        def get_sms_service_status(self):
            return {
                'current_provider': 'mock',
                'enabled': True,
                'mock_mode': True,
                'sms_alerts_enabled': True,
                'phone_number': '+1234567890',
                'twilio_available': False,
                'aws_available': False
            }
        
        def send_test_sms(self):
            return {"success": True, "message": "Test SMS sent successfully in mock mode!"}
        
        def update_setting(self, key, value):
            print(f"Setting updated: {key} = {value}")
    
    def send_test_sms():
        """Test SMS sending function"""
        phone_number = phone_var.get()
        provider = provider_var.get()
        
        if not phone_number:
            messagebox.showwarning("Missing Phone", "Please enter a phone number first")
            return
        
        if not provider:
            messagebox.showwarning("Missing Provider", "Please select an SMS provider")
            return
        
        # Simulate sending test SMS
        messagebox.showinfo("SMS Test", f"Test SMS sent to {phone_number} via {provider}")
        status_label.config(text=f"Test SMS sent via {provider}", fg='#4CAF50')
    
    def check_sms_status():
        """Check SMS status function"""
        provider = provider_var.get() or 'none'
        phone = phone_var.get() or 'not set'
        
        status_info = (
            f"Provider: {provider}\n"
            f"Phone Number: {phone}\n"
            f"Status: Ready for testing\n"
            f"Mock Mode: Yes"
        )
        
        messagebox.showinfo("SMS Service Status", status_info)
        status_label.config(text=f"SMS service ready ({provider})", fg='#2196F3')

    # Create main window
    root = tk.Tk()
    root.title("SMS Settings Test")
    root.geometry("600x500")
    root.configure(bg=GUI_COLORS['background'])
    
    # Create main frame
    main_frame = tk.Frame(root, bg=GUI_COLORS['background'])
    main_frame.pack(fill='both', expand=True, padx=20, pady=20)
    
    # Title
    title_label = tk.Label(main_frame, text="📱 SMS Alert Settings", 
                          bg=GUI_COLORS['background'], fg=GUI_COLORS['text_primary'],
                          font=FONTS['header'])
    title_label.pack(pady=(0, 20))
    
    # SMS Configuration Section
    sms_section = tk.LabelFrame(main_frame, text="📱 SMS Alert Configuration", 
                               bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['info'], 
                               font=FONTS['subheader'], relief='raised', bd=3)
    sms_section.pack(fill='x', pady=10)
    
    # Phone number section
    phone_section = tk.LabelFrame(sms_section, text="📞 Phone Number", 
                                 bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['accent'],
                                 font=FONTS['normal'])
    phone_section.pack(fill='x', padx=10, pady=10)
    
    phone_frame = tk.Frame(phone_section, bg=GUI_COLORS['panel_bg'])
    phone_frame.pack(fill='x', padx=10, pady=5)
    
    tk.Label(phone_frame, text="📱 Phone Number:", 
            bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'], 
            font=FONTS['normal']).pack(side='left')
    
    phone_var = tk.StringVar(value="+1234567890")  # Pre-filled for testing
    phone_entry = tk.Entry(phone_frame, textvariable=phone_var,
                          font=FONTS['normal'], width=20, bg='white', fg='black')
    phone_entry.pack(side='left', padx=(10, 5))
    
    tk.Label(phone_frame, text="(e.g., +1234567890)", 
            bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'], 
            font=FONTS['small']).pack(side='left')
    
    # Provider selection section
    provider_section = tk.LabelFrame(sms_section, text="🔧 SMS Provider", 
                                    bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['accent'],
                                    font=FONTS['normal'])
    provider_section.pack(fill='x', padx=10, pady=10)
    
    provider_frame = tk.Frame(provider_section, bg=GUI_COLORS['panel_bg'])
    provider_frame.pack(fill='x', padx=10, pady=5)
    
    provider_var = tk.StringVar(value='mock')  # Default to mock
    
    # Create radio buttons with improved styling
    mock_radio = tk.Radiobutton(provider_frame, text="🧪 Mock (Testing)", 
                  variable=provider_var, value='mock',
                  bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'],
                  selectcolor='#4CAF50', activebackground=GUI_COLORS['panel_bg'],
                  activeforeground=GUI_COLORS['accent'], font=FONTS['normal'],
                  relief='flat', bd=0, highlightthickness=0)
    mock_radio.pack(anchor='w', pady=2)
    
    twilio_radio = tk.Radiobutton(provider_frame, text="📞 Twilio (Recommended)", 
                  variable=provider_var, value='twilio',
                  bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'],
                  selectcolor='#2196F3', activebackground=GUI_COLORS['panel_bg'],
                  activeforeground=GUI_COLORS['accent'], font=FONTS['normal'],
                  relief='flat', bd=0, highlightthickness=0)
    twilio_radio.pack(anchor='w', pady=2)
    
    aws_radio = tk.Radiobutton(provider_frame, text="☁️ AWS SNS", 
                  variable=provider_var, value='aws_sns',
                  bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_primary'],
                  selectcolor='#FF9800', activebackground=GUI_COLORS['panel_bg'],
                  activeforeground=GUI_COLORS['accent'], font=FONTS['normal'],
                  relief='flat', bd=0, highlightthickness=0)
    aws_radio.pack(anchor='w', pady=2)
    
    # Test buttons section
    test_section = tk.Frame(sms_section, bg=GUI_COLORS['panel_bg'], relief='raised', bd=3)
    test_section.pack(fill='x', padx=10, pady=10)
    
    test_button = tk.Button(test_section, text="📤 Send Test SMS", 
                           command=send_test_sms,
                           bg='#4CAF50', fg='white', font=FONTS['normal'],
                           relief='raised', bd=2, padx=15, pady=5, cursor='hand2',
                           activebackground='#45a049', activeforeground='white')
    test_button.pack(side='left', padx=10)
    
    status_button = tk.Button(test_section, text="🔍 Check SMS Status", 
                             command=check_sms_status,
                             bg='#2196F3', fg='white', font=FONTS['normal'],
                             relief='raised', bd=2, padx=15, pady=5, cursor='hand2',
                             activebackground='#1976D2', activeforeground='white')
    status_button.pack(side='left', padx=5)
    
    # Status display
    status_section = tk.LabelFrame(main_frame, text="📊 SMS Service Status", 
                                  bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['info'],
                                  font=FONTS['subheader'])
    status_section.pack(fill='x', pady=10)
    
    status_label = tk.Label(status_section, 
                           text="SMS service ready for testing...", 
                           bg=GUI_COLORS['panel_bg'], fg=GUI_COLORS['text_secondary'], 
                           font=FONTS['normal'], justify='left')
    status_label.pack(anchor='w', padx=10, pady=5)
    
    # Instructions
    instructions = tk.Label(main_frame, 
                           text="1. Select an SMS provider using the radio buttons\n"
                                "2. Enter your phone number\n"
                                "3. Click 'Send Test SMS' to test functionality\n"
                                "4. Click 'Check SMS Status' to see current configuration",
                           bg=GUI_COLORS['background'], fg=GUI_COLORS['text_secondary'],
                           font=FONTS['small'], justify='left')
    instructions.pack(pady=20)
    
    # Set initial status
    check_sms_status()
    
    root.mainloop()

if __name__ == "__main__":
    test_sms_functionality()
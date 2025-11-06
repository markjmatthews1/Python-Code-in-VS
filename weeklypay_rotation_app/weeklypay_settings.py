"""
WeeklyPay Settings GUI
Manage ticker ex-dividend dates, pay dates, and ticker list
"""

import customtkinter as ctk
from datetime import datetime, timedelta
import json
from pathlib import Path
from tkinter import messagebox
import calendar

class WeeklyPaySettingsGUI:
    def __init__(self):
        # File paths
        self.settings_file = Path(__file__).parent / "data" / "weeklypay_settings.json"
        self.settings_file.parent.mkdir(exist_ok=True)
        
        # Load or create default settings
        self.settings = self.load_settings()
        
        # Create main window
        self.root = ctk.CTk()
        self.root.title("WeeklyPay Settings")
        self.root.geometry("900x700")
        
        # Color scheme
        self.colors = {
            'bg': '#1a1a1a',
            'fg': '#ffffff',
            'button': '#2fa572',
            'button_hover': '#258a5f',
            'entry_bg': '#2b2b2b',
            'entry_fg': '#ffffff',
            'frame_bg': '#252525',
            'header_bg': '#1e3a8a',
            'error': '#ef4444',
            'success': '#22c55e',
            'monday': '#3b82f6',
            'tuesday': '#8b5cf6',
            'thursday': '#f59e0b',
            'wednesday': '#10b981'
        }
        
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.setup_ui()
        
    def load_settings(self):
        """Load settings from JSON file or return defaults"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
        
        # Default settings based on current code
        return {
            'tickers': {
                'NVDW': {
                    'name': 'GraniteShares 1x Long NVDA Daily ETF',
                    'ex_dividend_day': 'Monday',  # CORRECTED based on user info
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-11-04',  # Today (Monday)
                    'sector': 'Technology',
                    'active': True
                },
                'AMDW': {
                    'name': 'GraniteShares 1x Long AMD Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'HOOW': {
                    'name': 'GraniteShares 1x Long META Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'MSFW': {
                    'name': 'GraniteShares 1x Long MSFT Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'GOOW': {
                    'name': 'GraniteShares 1x Long GOOGL Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'NFLW': {
                    'name': 'GraniteShares 1x Long NFLX Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Communication',
                    'active': True
                },
                'XOMO': {
                    'name': 'Roundhill XOM WeeklyPay ETF',
                    'ex_dividend_day': 'Thursday',
                    'pay_day': 'Friday',
                    'last_ex_date': '2025-10-03',
                    'sector': 'Energy',
                    'active': True
                },
                'QDTE': {
                    'name': 'Roundhill QDTE WeeklyPay ETF',
                    'ex_dividend_day': 'Thursday',
                    'pay_day': 'Friday',
                    'last_ex_date': '2025-10-03',
                    'sector': 'Technology',
                    'active': True
                },
                'TSLW': {
                    'name': 'GraniteShares 1x Long TSLA Daily ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-10-27',
                    'sector': 'Technology',
                    'active': True
                },
                'BRKW': {
                    'name': 'GraniteShares 1x Long BRK.B Daily ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-10-27',
                    'sector': 'Financials',
                    'active': True
                }
            }
        }
    
    def save_settings(self):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            return True
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save settings: {e}")
            return False
    
    def setup_ui(self):
        """Create the settings interface"""
        # Header
        header_frame = ctk.CTkFrame(self.root, fg_color=self.colors['header_bg'])
        header_frame.pack(fill='x', padx=10, pady=(10, 5))
        
        ctk.CTkLabel(
            header_frame,
            text="⚙️ WeeklyPay Settings",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=self.colors['fg']
        ).pack(pady=15)
        
        # Main container with scrollable frame
        main_container = ctk.CTkScrollableFrame(self.root, fg_color=self.colors['bg'])
        main_container.pack(fill='both', expand=True, padx=10, pady=5)
        
        # Instructions
        instructions = ctk.CTkFrame(main_container, fg_color=self.colors['frame_bg'])
        instructions.pack(fill='x', pady=(0, 10))
        
        ctk.CTkLabel(
            instructions,
            text="💡 Manage your weekly dividend ETF settings below.\nUpdate ex-dividend days and pay days as needed.",
            font=ctk.CTkFont(size=12),
            text_color='#9ca3af',
            justify='left'
        ).pack(padx=15, pady=10)
        
        # Ticker list
        self.ticker_widgets = {}
        for ticker, data in sorted(self.settings['tickers'].items()):
            self.create_ticker_frame(main_container, ticker, data)
        
        # Add new ticker button
        add_button_frame = ctk.CTkFrame(main_container, fg_color=self.colors['bg'])
        add_button_frame.pack(fill='x', pady=10)
        
        ctk.CTkButton(
            add_button_frame,
            text="➕ Add New Ticker",
            command=self.add_new_ticker,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover'],
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40
        ).pack(pady=5)
        
        # Bottom button bar
        button_frame = ctk.CTkFrame(self.root, fg_color=self.colors['bg'])
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ctk.CTkButton(
            button_frame,
            text="💾 Save Settings",
            command=self.save_and_close,
            fg_color=self.colors['success'],
            hover_color='#16a34a',
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=200
        ).pack(side='left', padx=5)
        
        ctk.CTkButton(
            button_frame,
            text="❌ Cancel",
            command=self.root.destroy,
            fg_color=self.colors['error'],
            hover_color='#dc2626',
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            width=150
        ).pack(side='left', padx=5)
        
        # Export button
        ctk.CTkButton(
            button_frame,
            text="📤 Export for Code",
            command=self.export_for_code,
            fg_color='#6366f1',
            hover_color='#4f46e5',
            font=ctk.CTkFont(size=14),
            height=45,
            width=180
        ).pack(side='right', padx=5)
    
    def create_ticker_frame(self, parent, ticker, data):
        """Create a frame for a single ticker's settings"""
        frame = ctk.CTkFrame(parent, fg_color=self.colors['frame_bg'])
        frame.pack(fill='x', pady=5, padx=5)
        
        # Color code by ex-dividend day
        day_colors = {
            'Monday': self.colors['monday'],
            'Tuesday': self.colors['tuesday'],
            'Wednesday': self.colors['wednesday'],
            'Thursday': self.colors['thursday'],
            'Friday': self.colors['success']
        }
        indicator_color = day_colors.get(data['ex_dividend_day'], '#6b7280')
        
        # Left indicator bar
        indicator = ctk.CTkFrame(frame, fg_color=indicator_color, width=6)
        indicator.pack(side='left', fill='y', padx=(5, 10))
        
        # Content area
        content = ctk.CTkFrame(frame, fg_color=self.colors['frame_bg'])
        content.pack(side='left', fill='both', expand=True, padx=5, pady=10)
        
        # Row 1: Ticker symbol and name
        row1 = ctk.CTkFrame(content, fg_color='transparent')
        row1.pack(fill='x', pady=(0, 5))
        
        ctk.CTkLabel(
            row1,
            text=ticker,
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color=indicator_color
        ).pack(side='left', padx=(0, 10))
        
        name_entry = ctk.CTkEntry(
            row1,
            placeholder_text="ETF Name",
            width=350,
            fg_color=self.colors['entry_bg'],
            text_color=self.colors['entry_fg']
        )
        name_entry.pack(side='left', padx=5)
        name_entry.insert(0, data.get('name', ''))
        
        sector_entry = ctk.CTkEntry(
            row1,
            placeholder_text="Sector",
            width=120,
            fg_color=self.colors['entry_bg'],
            text_color=self.colors['entry_fg']
        )
        sector_entry.pack(side='left', padx=5)
        sector_entry.insert(0, data.get('sector', 'Technology'))
        
        # Row 2: Ex-dividend and pay day settings
        row2 = ctk.CTkFrame(content, fg_color='transparent')
        row2.pack(fill='x', pady=5)
        
        ctk.CTkLabel(
            row2,
            text="Ex-Dividend Day:",
            font=ctk.CTkFont(size=12)
        ).pack(side='left', padx=(0, 5))
        
        ex_div_day = ctk.CTkOptionMenu(
            row2,
            values=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            width=120,
            fg_color=self.colors['entry_bg'],
            button_color=self.colors['button'],
            button_hover_color=self.colors['button_hover']
        )
        ex_div_day.pack(side='left', padx=5)
        ex_div_day.set(data['ex_dividend_day'])
        
        ctk.CTkLabel(
            row2,
            text="Pay Day:",
            font=ctk.CTkFont(size=12)
        ).pack(side='left', padx=(15, 5))
        
        pay_day = ctk.CTkOptionMenu(
            row2,
            values=['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'],
            width=120,
            fg_color=self.colors['entry_bg'],
            button_color=self.colors['button'],
            button_hover_color=self.colors['button_hover']
        )
        pay_day.pack(side='left', padx=5)
        pay_day.set(data['pay_day'])
        
        ctk.CTkLabel(
            row2,
            text="Last Ex-Date:",
            font=ctk.CTkFont(size=12)
        ).pack(side='left', padx=(15, 5))
        
        last_date = ctk.CTkEntry(
            row2,
            placeholder_text="YYYY-MM-DD",
            width=120,
            fg_color=self.colors['entry_bg'],
            text_color=self.colors['entry_fg']
        )
        last_date.pack(side='left', padx=5)
        last_date.insert(0, data.get('last_ex_date', ''))
        
        # Active checkbox
        active_var = ctk.BooleanVar(value=data.get('active', True))
        active_check = ctk.CTkCheckBox(
            row2,
            text="Active",
            variable=active_var,
            fg_color=self.colors['button'],
            hover_color=self.colors['button_hover']
        )
        active_check.pack(side='left', padx=(15, 5))
        
        # Delete button
        delete_btn = ctk.CTkButton(
            frame,
            text="🗑️",
            command=lambda: self.delete_ticker(ticker, frame),
            fg_color=self.colors['error'],
            hover_color='#dc2626',
            width=50,
            height=60
        )
        delete_btn.pack(side='right', padx=5)
        
        # Store references
        self.ticker_widgets[ticker] = {
            'frame': frame,
            'name_entry': name_entry,
            'sector_entry': sector_entry,
            'ex_div_day': ex_div_day,
            'pay_day': pay_day,
            'last_date': last_date,
            'active_var': active_var
        }
    
    def add_new_ticker(self):
        """Add a new ticker dialog"""
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Add New Ticker")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ctk.CTkLabel(
            dialog,
            text="Add New WeeklyPay Ticker",
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=15)
        
        # Ticker symbol
        ctk.CTkLabel(dialog, text="Ticker Symbol:").pack(pady=(10, 5))
        ticker_entry = ctk.CTkEntry(dialog, width=200)
        ticker_entry.pack(pady=5)
        
        # ETF Name
        ctk.CTkLabel(dialog, text="ETF Name:").pack(pady=(10, 5))
        name_entry = ctk.CTkEntry(dialog, width=300)
        name_entry.pack(pady=5)
        
        def save_new_ticker():
            ticker = ticker_entry.get().strip().upper()
            name = name_entry.get().strip()
            
            if not ticker:
                messagebox.showerror("Error", "Please enter a ticker symbol")
                return
            
            if ticker in self.settings['tickers']:
                messagebox.showerror("Error", f"Ticker {ticker} already exists")
                return
            
            # Add with default settings
            self.settings['tickers'][ticker] = {
                'name': name or f'{ticker} ETF',
                'ex_dividend_day': 'Tuesday',
                'pay_day': 'Wednesday',
                'last_ex_date': datetime.now().strftime('%Y-%m-%d'),
                'sector': 'Technology',
                'active': True
            }
            
            # Refresh UI
            dialog.destroy()
            self.refresh_ticker_list()
        
        ctk.CTkButton(
            dialog,
            text="Add Ticker",
            command=save_new_ticker,
            fg_color=self.colors['success'],
            height=40,
            width=150
        ).pack(pady=20)
    
    def delete_ticker(self, ticker, frame):
        """Delete a ticker from settings"""
        if messagebox.askyesno("Confirm Delete", f"Delete ticker {ticker}?"):
            del self.settings['tickers'][ticker]
            del self.ticker_widgets[ticker]
            frame.destroy()
    
    def refresh_ticker_list(self):
        """Refresh the ticker list display"""
        self.root.destroy()
        self.__init__()
        self.run()
    
    def save_and_close(self):
        """Save all settings and close"""
        # Update settings from widgets
        for ticker, widgets in self.ticker_widgets.items():
            self.settings['tickers'][ticker] = {
                'name': widgets['name_entry'].get(),
                'sector': widgets['sector_entry'].get(),
                'ex_dividend_day': widgets['ex_div_day'].get(),
                'pay_day': widgets['pay_day'].get(),
                'last_ex_date': widgets['last_date'].get(),
                'active': widgets['active_var'].get()
            }
        
        if self.save_settings():
            messagebox.showinfo("Success", "Settings saved successfully!")
            self.root.destroy()
    
    def export_for_code(self):
        """Export settings in Python code format"""
        export_window = ctk.CTkToplevel(self.root)
        export_window.title("Export for Code")
        export_window.geometry("700x600")
        
        ctk.CTkLabel(
            export_window,
            text="Copy this to update simple_dashboard.py:",
            font=ctk.CTkFont(size=14, weight="bold")
        ).pack(pady=10)
        
        # Generate Python code
        code_lines = ["last_known_ex_div = {"]
        for ticker, data in sorted(self.settings['tickers'].items()):
            if data.get('active', True):
                date_str = data.get('last_ex_date', '2025-01-01')
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
                    code_lines.append(
                        f"    '{ticker}': datetime({date_obj.year}, {date_obj.month}, {date_obj.day}),  "
                        f"# {data['ex_dividend_day']} (pays {data['pay_day']})"
                    )
                except:
                    pass
        code_lines.append("}")
        
        code_text = "\n".join(code_lines)
        
        text_box = ctk.CTkTextbox(export_window, width=650, height=450, font=ctk.CTkFont(family="Consolas", size=11))
        text_box.pack(pady=10, padx=20)
        text_box.insert("1.0", code_text)
        
        def copy_to_clipboard():
            self.root.clipboard_clear()
            self.root.clipboard_append(code_text)
            messagebox.showinfo("Copied", "Code copied to clipboard!")
        
        ctk.CTkButton(
            export_window,
            text="📋 Copy to Clipboard",
            command=copy_to_clipboard,
            fg_color=self.colors['button'],
            height=40,
            width=200
        ).pack(pady=10)
    
    def run(self):
        """Run the settings GUI"""
        self.root.mainloop()


if __name__ == "__main__":
    app = WeeklyPaySettingsGUI()
    app.run()

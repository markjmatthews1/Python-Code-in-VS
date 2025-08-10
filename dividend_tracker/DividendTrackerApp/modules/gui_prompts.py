#!/usr/bin/env python3
"""
GUI Prompts Module for Dividend Tracker
Provides colorful popup dialogs for user input
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class ColorfulK401Prompt:
    """Colorful popup for 401k value input"""
    
    def __init__(self):
        self.result = None
        self.root = None
    
    def show_popup(self):
        """Show the colorful 401k input popup"""
        
        # Create root window
        self.root = tk.Tk()
        self.root.title("💰 401k Value Update")
        self.root.geometry("450x300")
        self.root.resizable(False, False)
        
        # Make it stay on top
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.focus_force()
        
        # Center the window on screen
        self.center_window()
        
        # Set colors and styling
        bg_color = "#2E86AB"  # Nice blue
        accent_color = "#A23B72"  # Purple accent
        text_color = "#F18F01"  # Orange text
        button_color = "#C73E1D"  # Red button
        
        self.root.configure(bg=bg_color)
        
        # Main frame with padding
        main_frame = tk.Frame(self.root, bg=bg_color, padx=20, pady=20)
        main_frame.pack(fill="both", expand=True)
        
        # Title with emoji
        title_label = tk.Label(
            main_frame,
            text="📊 Weekly 401k Value Update 💰",
            font=("Arial", 16, "bold"),
            fg="white",
            bg=bg_color
        )
        title_label.pack(pady=(0, 20))
        
        # Subtitle
        subtitle_label = tk.Label(
            main_frame,
            text="Enter your current 401k account value",
            font=("Arial", 12),
            fg="white",
            bg=bg_color
        )
        subtitle_label.pack(pady=(0, 15))
        
        # Input frame
        input_frame = tk.Frame(main_frame, bg=bg_color)
        input_frame.pack(pady=10)
        
        # Dollar sign label
        dollar_label = tk.Label(
            input_frame,
            text="$",
            font=("Arial", 18, "bold"),
            fg=text_color,
            bg=bg_color
        )
        dollar_label.pack(side="left", padx=(0, 5))
        
        # Input entry
        self.entry = tk.Entry(
            input_frame,
            font=("Arial", 16),
            width=15,
            justify="center",
            relief="raised",
            bd=3
        )
        self.entry.pack(side="left")
        self.entry.focus()
        
        # Bind Enter key
        self.entry.bind('<Return>', self.on_submit)
        
        # Example text
        example_label = tk.Label(
            main_frame,
            text="Example: 125000 (don't include commas)",
            font=("Arial", 10, "italic"),
            fg="lightgray",
            bg=bg_color
        )
        example_label.pack(pady=(5, 20))
        
        # Button frame
        button_frame = tk.Frame(main_frame, bg=bg_color)
        button_frame.pack(pady=10)
        
        # Submit button
        submit_btn = tk.Button(
            button_frame,
            text="💾 Update Value",
            font=("Arial", 12, "bold"),
            fg="white",
            bg=button_color,
            activebackground="#8B0000",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=8,
            command=self.on_submit
        )
        submit_btn.pack(side="left", padx=(0, 10))
        
        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="❌ Cancel",
            font=("Arial", 12),
            fg="white",
            bg="#666666",
            activebackground="#404040",
            activeforeground="white",
            relief="raised",
            bd=3,
            padx=20,
            pady=8,
            command=self.on_cancel
        )
        cancel_btn.pack(side="left")
        
        # Status label
        self.status_label = tk.Label(
            main_frame,
            text="",
            font=("Arial", 10),
            fg="yellow",
            bg=bg_color
        )
        self.status_label.pack(pady=(15, 0))
        
        # Start the GUI
        self.root.mainloop()
        
        return self.result
    
    def center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def on_submit(self, event=None):
        """Handle submit button click"""
        try:
            value_text = self.entry.get().strip()
            if not value_text:
                self.show_error("Please enter a value!")
                return
            
            # Clean the input
            clean_value = value_text.replace(',', '').replace('$', '').replace(' ', '')
            value = float(clean_value)
            
            if value <= 0:
                self.show_error("Please enter a positive value!")
                return
            
            self.result = value
            self.show_success(f"✅ Value set to ${value:,.2f}")
            self.root.after(1000, self.root.destroy)  # Close after 1 second
            
        except ValueError:
            self.show_error("Please enter a valid number!")
    
    def on_cancel(self):
        """Handle cancel button click"""
        self.result = None
        self.root.destroy()
    
    def show_error(self, message):
        """Show error message"""
        self.status_label.configure(text=f"❌ {message}", fg="red")
        self.entry.focus()
        
        # Flash the entry field
        original_bg = self.entry.cget("bg")
        self.entry.configure(bg="#FFCCCC")
        self.root.after(500, lambda: self.entry.configure(bg=original_bg))
    
    def show_success(self, message):
        """Show success message"""
        self.status_label.configure(text=message, fg="lightgreen")


def get_k401_value():
    """
    Show colorful popup to get 401k value
    Returns: float value or None if cancelled
    """
    try:
        prompt = ColorfulK401Prompt()
        return prompt.show_popup()
    except Exception as e:
        print(f"⚠️ GUI popup failed, falling back to console: {e}")
        # Fallback to console input
        while True:
            try:
                value_input = input("💰 Enter this week's 401k value: $")
                return float(value_input.replace(',', '').replace('$', ''))
            except ValueError:
                print("❌ Invalid input. Please enter a numeric value.")


def test_popup():
    """Test the popup GUI"""
    print("🧪 Testing 401k popup GUI...")
    value = get_k401_value()
    if value is not None:
        print(f"✅ Got value: ${value:,.2f}")
    else:
        print("❌ User cancelled")


if __name__ == "__main__":
    test_popup()

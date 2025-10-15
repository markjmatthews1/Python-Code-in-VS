"""
Common GUI utilities for RecoveryApp
Provides standardized colors, fonts, and UI components
"""
import tkinter as tk
from tkinter import ttk

class UIConfig:
    """Standard UI configuration for RecoveryApp"""
    
    # Standard font
    DEFAULT_FONT = ('Arial', 12)
    TITLE_FONT = ('Arial', 16, 'bold')
    HEADER_FONT = ('Arial', 14, 'bold')
    
    # Color scheme
    COLORS = {
        'bg_primary': '#2c3e50',      # Dark blue-gray
        'bg_secondary': '#34495e',     # Lighter blue-gray
        'accent': '#3498db',           # Blue
        'success': '#27ae60',          # Green
        'warning': '#f39c12',          # Orange
        'danger': '#e74c3c',           # Red
        'text_light': '#ecf0f1',       # Light gray
        'text_dark': '#2c3e50',        # Dark blue-gray
        'highlight': '#9b59b6',        # Purple
        'info': '#17a2b8'              # Teal
    }

def create_styled_button(parent, text, command=None, style='primary'):
    """Create a styled button with standard appearance"""
    colors = UIConfig.COLORS
    
    if style == 'primary':
        bg_color = colors['accent']
        fg_color = colors['text_light']
    elif style == 'success':
        bg_color = colors['success']
        fg_color = colors['text_light']
    elif style == 'warning':
        bg_color = colors['warning']
        fg_color = colors['text_dark']
    elif style == 'danger':
        bg_color = colors['danger']
        fg_color = colors['text_light']
    else:
        bg_color = colors['bg_secondary']
        fg_color = colors['text_light']
    
    button = tk.Button(
        parent,
        text=text,
        command=command,
        font=UIConfig.DEFAULT_FONT,
        bg=bg_color,
        fg=fg_color,
        relief='flat',
        padx=20,
        pady=5,
        cursor='hand2'
    )
    
    # Hover effects
    def on_enter(e):
        button.configure(relief='raised')
    
    def on_leave(e):
        button.configure(relief='flat')
    
    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)
    
    return button

def create_styled_frame(parent, style='primary'):
    """Create a styled frame with standard appearance"""
    colors = UIConfig.COLORS
    
    if style == 'primary':
        bg_color = colors['bg_primary']
    elif style == 'secondary':
        bg_color = colors['bg_secondary']
    else:
        bg_color = colors['bg_primary']
    
    frame = tk.Frame(parent, bg=bg_color)
    return frame

def create_styled_label(parent, text, style='normal'):
    """Create a styled label with standard appearance"""
    colors = UIConfig.COLORS
    
    if style == 'title':
        font = UIConfig.TITLE_FONT
        fg_color = colors['text_light']
    elif style == 'header':
        font = UIConfig.HEADER_FONT
        fg_color = colors['text_light']
    elif style == 'success':
        font = UIConfig.DEFAULT_FONT
        fg_color = colors['success']
    elif style == 'warning':
        font = UIConfig.DEFAULT_FONT
        fg_color = colors['warning']
    elif style == 'danger':
        font = UIConfig.DEFAULT_FONT
        fg_color = colors['danger']
    else:
        font = UIConfig.DEFAULT_FONT
        fg_color = colors['text_light']
    
    label = tk.Label(
        parent,
        text=text,
        font=font,
        fg=fg_color,
        bg=parent['bg']
    )
    
    return label
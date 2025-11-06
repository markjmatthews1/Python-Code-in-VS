"""
GUI Styles for Catalyst Scanner

Accessible design with Arial 12+ fonts and flashy, high-contrast colors
optimized for readability by older eyes.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import tkinter as tk
from tkinter import ttk

# Color scheme for high contrast and accessibility
GUI_COLORS = {
    'background': '#1a1a2e',           # Dark navy background
    'panel_bg': '#16213e',             # Slightly lighter panel background
    'accent': '#0f4c75',               # Deep blue accent
    'success': '#00ff41',              # Bright lime green for positive
    'warning': '#ffaa00',              # Bright orange for warnings
    'danger': '#ff4444',               # Bright red for alerts
    'info': '#00aaff',                 # Bright blue for info
    'text_primary': '#ffffff',         # Pure white text
    'text_secondary': '#cccccc',       # Light gray text
    'highlight': '#ffff00',            # Bright yellow for highlights
    'button_active': '#ff6b6b',        # Bright coral for active buttons
    'border': '#4a4a4a',               # Gray borders
    'high_impact': '#ff0066',          # Bright magenta for high impact
    'medium_impact': '#ff9900',        # Bright orange for medium impact
    'low_impact': '#0099ff'            # Bright blue for low impact
}

# Font definitions for accessibility
FONTS = {
    'header': ('Arial', 16, 'bold'),
    'subheader': ('Arial', 14, 'bold'),
    'normal': ('Arial', 12, 'normal'),
    'bold': ('Arial', 12, 'bold'),
    'large': ('Arial', 14, 'normal'),
    'button': ('Arial', 12, 'bold'),
    'status': ('Arial', 11, 'normal'),
    'small': ('Arial', 10, 'normal'),  # Added missing small font
    'mono_small': ('Consolas', 10, 'normal')  # Added missing mono font
}

# Widget padding for better spacing
PADDING = {
    'small': 5,
    'medium': 10,
    'large': 15,
    'xlarge': 20
}

def apply_theme_to_root(root):
    """Apply the main theme to the root window"""
    root.configure(bg=GUI_COLORS['background'])
    
    # Configure ttk styles
    style = ttk.Style()
    style.theme_use('clam')  # Use clam theme as base
    
    # Configure ttk widgets
    style.configure('Title.TLabel',
                   background=GUI_COLORS['background'],
                   foreground=GUI_COLORS['text_primary'],
                   font=FONTS['header'])
    
    style.configure('Heading.TLabel',
                   background=GUI_COLORS['panel_bg'],
                   foreground=GUI_COLORS['text_primary'],
                   font=FONTS['subheader'])
    
    style.configure('Normal.TLabel',
                   background=GUI_COLORS['panel_bg'],
                   foreground=GUI_COLORS['text_primary'],
                   font=FONTS['normal'])
    
    style.configure('Success.TLabel',
                   background=GUI_COLORS['panel_bg'],
                   foreground=GUI_COLORS['success'],
                   font=FONTS['bold'])
    
    style.configure('Warning.TLabel',
                   background=GUI_COLORS['panel_bg'],
                   foreground=GUI_COLORS['warning'],
                   font=FONTS['bold'])
    
    style.configure('Danger.TLabel',
                   background=GUI_COLORS['panel_bg'],
                   foreground=GUI_COLORS['danger'],
                   font=FONTS['bold'])
    
    # Button styles
    style.configure('Action.TButton',
                   background=GUI_COLORS['button_active'],
                   foreground=GUI_COLORS['text_primary'],
                   font=FONTS['button'],
                   padding=(10, 5))
    
    style.configure('Normal.TButton',
                   background=GUI_COLORS['accent'],
                   foreground=GUI_COLORS['text_primary'],
                   font=FONTS['button'],
                   padding=(10, 5))

def create_themed_frame(parent, style='normal'):
    """Create a themed frame with appropriate styling"""
    if style == 'panel':
        bg_color = GUI_COLORS['panel_bg']
        relief = 'raised'
        bd = 2
    elif style == 'accent':
        bg_color = GUI_COLORS['accent']
        relief = 'raised'
        bd = 2
    else:
        bg_color = GUI_COLORS['background']
        relief = 'flat'
        bd = 0
    
    frame = tk.Frame(parent,
                    bg=bg_color,
                    relief=relief,
                    bd=bd,
                    highlightbackground=GUI_COLORS['border'],
                    highlightthickness=1)
    return frame

def create_themed_label(parent, text, style='normal', **kwargs):
    """Create a themed label with appropriate styling"""
    if style == 'header':
        font = FONTS['header']
        fg = GUI_COLORS['text_primary']
    elif style == 'subheader':
        font = FONTS['subheader']
        fg = GUI_COLORS['text_primary']
    elif style == 'success':
        font = FONTS['bold']
        fg = GUI_COLORS['success']
    elif style == 'warning':
        font = FONTS['bold']
        fg = GUI_COLORS['warning']
    elif style == 'danger':
        font = FONTS['bold']
        fg = GUI_COLORS['danger']
    elif style == 'info':
        font = FONTS['bold']
        fg = GUI_COLORS['info']
    elif style == 'highlight':
        font = FONTS['bold']
        fg = GUI_COLORS['highlight']
    else:
        font = FONTS['normal']
        fg = GUI_COLORS['text_primary']
    
    # Get parent background color
    try:
        bg = parent.cget('bg')
    except:
        bg = GUI_COLORS['background']
    
    label = tk.Label(parent,
                    text=text,
                    font=font,
                    fg=fg,
                    bg=bg,
                    **kwargs)
    return label

def create_themed_button(parent, text, command=None, style='normal', **kwargs):
    """Create a themed button with appropriate styling"""
    if style == 'action':
        bg = GUI_COLORS['button_active']
        fg = GUI_COLORS['text_primary']
        active_bg = GUI_COLORS['danger']
    elif style == 'success':
        bg = GUI_COLORS['success']
        fg = GUI_COLORS['background']
        active_bg = GUI_COLORS['highlight']
    elif style == 'warning':
        bg = GUI_COLORS['warning']
        fg = GUI_COLORS['background']
        active_bg = GUI_COLORS['highlight']
    elif style == 'danger':
        bg = GUI_COLORS['danger']
        fg = GUI_COLORS['text_primary']
        active_bg = GUI_COLORS['highlight']
    else:
        bg = GUI_COLORS['accent']
        fg = GUI_COLORS['text_primary']
        active_bg = GUI_COLORS['button_active']
    
    button = tk.Button(parent,
                      text=text,
                      command=command,
                      font=FONTS['button'],
                      bg=bg,
                      fg=fg,
                      activebackground=active_bg,
                      activeforeground=GUI_COLORS['text_primary'],
                      relief='raised',
                      bd=3,
                      padx=PADDING['medium'],
                      pady=PADDING['small'],
                      **kwargs)
    return button

def get_impact_color(impact_score):
    """Get color based on impact score (1-10)"""
    if impact_score >= 8:
        return GUI_COLORS['high_impact']
    elif impact_score >= 6:
        return GUI_COLORS['medium_impact']
    else:
        return GUI_COLORS['low_impact']

def get_impact_style(impact_score):
    """Get style name based on impact score"""
    if impact_score >= 8:
        return 'danger'
    elif impact_score >= 6:
        return 'warning'
    else:
        return 'info'
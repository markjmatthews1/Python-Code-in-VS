#!/usr/bin/env python3
"""
Red Dot Location Helper
Shows exactly where the red dot appears in the menu
"""

import tkinter as tk
from tkinter import ttk
import time

def show_red_dot_location():
    """Demo showing exactly where the red dot appears"""
    
    root = tk.Tk()
    root.title("🔍 Where to Find the Red Dot")
    root.geometry("700x500")
    
    # Create the exact same menu structure as your main app
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load Portfolio")
    file_menu.add_command(label="Save Data")
    
    # View menu - THE IMPORTANT ONE!
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Refresh Data")
    view_menu.add_command(label="Full Screen")
    view_menu.add_separator()
    # HERE'S THE RED DOT!
    view_menu.add_command(label="🔴 Live Dashboard", command=show_red_dot_clicked)
    
    # Help menu
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About")
    
    # Main content with instructions
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill='both', expand=True)
    
    # Title
    title = ttk.Label(main_frame, text="🔍 RED DOT LOCATION GUIDE", 
                     font=('Segoe UI', 16, 'bold'))
    title.pack(pady=10)
    
    # Instructions
    instructions = tk.Text(main_frame, height=20, font=('Segoe UI', 11), wrap='word')
    instructions.pack(fill='both', expand=True, pady=10)
    
    guide_text = """🎯 STEP-BY-STEP TO FIND THE RED DOT:

1. Look at the menu bar at the top of this window
   You should see: File | View | Help

2. Click on "View" in the menu bar
   (Go ahead and try it now!)

3. A dropdown menu will appear with these options:
   • Refresh Data
   • Full Screen
   • ――――――――――――― (separator line)
   • 🔴 Live Dashboard  ← THE RED DOT IS HERE!

4. The red circle emoji (🔴) marks the new Phase 4 feature

🚀 IN YOUR MAIN CATALYST SCANNER:

When you run python catalyst_scanner.py, you'll see the EXACT same menu structure.

The red dot (🔴) is in the View menu dropdown, not visible until you click "View".

📋 WHAT THE RED DOT DOES:

Clicking "🔴 Live Dashboard" opens a new window with:
• Real-time catalyst scoring
• Portfolio impact analysis  
• Performance tracking
• Risk monitoring

🎊 Try clicking "View" → "🔴 Live Dashboard" above to see what happens!

💡 NOTE: The red dot is a MENU ITEM, not a button on the main screen.
It's inside the View menu dropdown."""
    
    instructions.insert('1.0', guide_text)
    instructions.config(state='disabled')
    
    # Highlight button
    highlight_btn = ttk.Button(main_frame, 
                              text="👆 Click 'View' Menu Above to See the Red Dot!",
                              style='Accent.TButton')
    highlight_btn.pack(pady=10)
    
    # Auto-highlight the View menu after 3 seconds
    def auto_highlight():
        try:
            # Flash the View menu to draw attention
            for i in range(3):
                root.after(1000 * i, lambda: print(f"🔴 Look at the 'View' menu in the menu bar!"))
        except:
            pass
    
    root.after(2000, auto_highlight)
    
    root.mainloop()

def show_red_dot_clicked():
    """Show what happens when red dot is clicked"""
    import tkinter.messagebox as mb
    mb.showinfo("🔴 Live Dashboard", 
                "SUCCESS! You found the red dot!\n\n"
                "In the real Catalyst Scanner, this opens the\n"
                "Phase 4 Live Dashboard with real-time monitoring!\n\n"
                "The red dot is located in:\n"
                "View Menu → 🔴 Live Dashboard")

if __name__ == "__main__":
    print("🔍 Showing exactly where the red dot appears...")
    print("The red dot is in the View menu dropdown!")
    show_red_dot_location()
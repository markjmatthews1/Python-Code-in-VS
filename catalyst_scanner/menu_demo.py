#!/usr/bin/env python3
"""
Quick Menu Demo - Shows the new Live Dashboard menu item
"""

import tkinter as tk
from tkinter import ttk, messagebox

def show_phase4_menu():
    """Demo showing the new menu structure with Live Dashboard"""
    
    root = tk.Tk()
    root.title("Catalyst Scanner - Phase 4 Menu Demo")
    root.geometry("600x400")
    
    # Create menu bar
    menubar = tk.Menu(root)
    root.config(menu=menubar)
    
    # File menu (existing)
    file_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="File", menu=file_menu)
    file_menu.add_command(label="Load Portfolio")
    file_menu.add_command(label="Save Settings")
    file_menu.add_separator()
    file_menu.add_command(label="Exit")
    
    # View menu (ENHANCED with Phase 4)
    view_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="View", menu=view_menu)
    view_menu.add_command(label="Refresh Data")
    view_menu.add_command(label="Full Screen")
    view_menu.add_separator()
    # NEW IN PHASE 4!
    view_menu.add_command(label="🔴 Live Dashboard", command=show_live_dashboard_info)
    
    # Help menu (existing)
    help_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Help", menu=help_menu)
    help_menu.add_command(label="About")
    
    # Main content
    main_frame = ttk.Frame(root, padding=20)
    main_frame.pack(fill='both', expand=True)
    
    title = ttk.Label(main_frame, text="🔍 CATALYST SCANNER", 
                     font=('Segoe UI', 18, 'bold'))
    title.pack(pady=10)
    
    info = ttk.Label(main_frame, text="Phase 4 Menu Enhancement Demo", 
                    font=('Segoe UI', 12))
    info.pack(pady=5)
    
    instructions = tk.Text(main_frame, height=15, font=('Segoe UI', 10))
    instructions.pack(fill='both', expand=True, pady=10)
    
    demo_text = """🆕 WHAT'S NEW IN THE MENU BAR:

BEFORE Phase 4:
📋 View Menu had:
   • Refresh Data
   • Full Screen

AFTER Phase 4:
📋 View Menu now has:
   • Refresh Data  
   • Full Screen
   • 🔴 Live Dashboard  ← NEW!

🎯 HOW TO SEE THE DIFFERENCE:

1. Look at the menu bar above
2. Click on "View" menu
3. You'll see the NEW "🔴 Live Dashboard" option
4. Click it to open the advanced monitoring window

🚀 PHASE 4 VISUAL CHANGES:

✨ Red circle emoji (🔴) identifies the Live Dashboard
✨ Clicking opens a separate window with tabbed interface
✨ Professional real-time monitoring capabilities
✨ 4 tabs: Live Scores, Portfolio Impact, Performance, Risk Monitor
✨ Start/Stop controls for live monitoring
✨ Status indicators and connection monitoring

This is the main visible entry point to all Phase 4 features!"""
    
    instructions.insert('1.0', demo_text)
    instructions.config(state='disabled')
    
    # Highlight button
    highlight_btn = ttk.Button(main_frame, 
                              text="👆 Click 'View' Menu Above to See the New Option!", 
                              style='Accent.TButton')
    highlight_btn.pack(pady=10)
    
    root.mainloop()

def show_live_dashboard_info():
    """Show info about the Live Dashboard"""
    messagebox.showinfo("🔴 Live Dashboard", 
                       "This opens the Phase 4 Live Dashboard!\n\n"
                       "Features:\n"
                       "• Real-time catalyst scoring\n"
                       "• Portfolio impact analysis\n"
                       "• Performance tracking\n"
                       "• Risk monitoring\n\n"
                       "The actual Live Dashboard is in the main app!")

if __name__ == "__main__":
    print("🎯 Showing Phase 4 Menu Changes...")
    show_phase4_menu()
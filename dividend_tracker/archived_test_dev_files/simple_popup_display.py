#!/usr/bin/env python3
"""
Simple Dividend Completion Popup - Fallback Version
This version focuses on core functionality with minimal dependencies
"""

import tkinter as tk
from tkinter import messagebox
import os
from datetime import datetime

def create_simple_completion_popup():
    """Create a simple completion popup"""
    
    # Create main window
    root = tk.Tk()
    root.title("🎯 Dividend Tracker - Processing Complete")
    root.geometry("600x400")
    root.configure(bg='#f0f8ff')
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Main frame
    main_frame = tk.Frame(root, bg='#f0f8ff', padx=30, pady=30)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Header
    header_frame = tk.Frame(main_frame, bg='#2c3e50', relief=tk.RAISED, bd=3)
    header_frame.pack(fill=tk.X, pady=(0, 20))
    
    title_label = tk.Label(header_frame, 
                          text="🎯 DIVIDEND TRACKER", 
                          font=("Arial", 20, "bold"), 
                          bg='#2c3e50', fg='white', pady=15)
    title_label.pack()
    
    subtitle_label = tk.Label(header_frame, 
                             text="✅ Weekly Processing Complete", 
                             font=("Arial", 12), 
                             bg='#2c3e50', fg='#bdc3c7', pady=(0, 15))
    subtitle_label.pack()
    
    # Status message
    status_frame = tk.Frame(main_frame, bg='#d4edda', relief=tk.RAISED, bd=2)
    status_frame.pack(fill=tk.X, pady=20)
    
    status_label = tk.Label(status_frame, 
                           text="🎉 Your dividend data has been processed successfully!\n\n"
                                "📊 Portfolio values updated\n"
                                "💰 Dividend estimates calculated\n"
                                "📈 Excel report ready\n"
                                "🎯 Showing dividend stocks ≥4% yield only", 
                           font=("Arial", 12), 
                           bg='#d4edda', fg='#155724', 
                           justify=tk.LEFT, pady=20, padx=20)
    status_label.pack()
    
    # Timestamp
    time_label = tk.Label(main_frame, 
                         text=f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
                         font=("Arial", 10), 
                         bg='#f0f8ff', fg='#6c757d')
    time_label.pack(pady=10)
    
    # Buttons frame
    button_frame = tk.Frame(main_frame, bg='#f0f8ff')
    button_frame.pack(pady=20)
    
    # OK Button
    ok_button = tk.Button(button_frame, text="✅ OK", font=("Arial", 12, "bold"),
                         bg='#28a745', fg='white', padx=30, pady=10,
                         command=root.destroy)
    ok_button.pack(side=tk.LEFT, padx=10)
    
    # View Excel Button
    def open_excel():
        try:
            excel_file = os.path.join(os.path.dirname(__file__), "outputs", "Dividends_2025.xlsx")
            if os.path.exists(excel_file):
                os.startfile(excel_file)
                print("📊 Opening Excel report...")
            else:
                messagebox.showwarning("File Not Found", "Excel report file not found!")
        except Exception as e:
            messagebox.showerror("Error", f"Could not open Excel file: {e}")
    
    excel_button = tk.Button(button_frame, text="📊 View Excel Report", 
                            font=("Arial", 12, "bold"),
                            bg='#007bff', fg='white', padx=30, pady=10,
                            command=open_excel)
    excel_button.pack(side=tk.LEFT, padx=10)
    
    # Keep window on top initially
    root.attributes('-topmost', True)
    root.focus_force()
    
    # Remove topmost after 3 seconds
    def remove_topmost():
        root.attributes('-topmost', False)
    
    root.after(3000, remove_topmost)
    
    # Start GUI
    root.mainloop()

def show_simple_completion_popup():
    """Show the simple completion popup"""
    try:
        print("🎯 Showing dividend processing completion popup...")
        create_simple_completion_popup()
        print("✅ Popup completed!")
    except Exception as e:
        print(f"❌ Error showing popup: {e}")
        print("\n🎯 DIVIDEND TRACKER - PROCESSING COMPLETE")
        print("="*50)
        print("✅ Your dividend data has been processed successfully!")
        print("📊 Check outputs/Dividends_2025.xlsx for full results")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)

if __name__ == "__main__":
    show_simple_completion_popup()

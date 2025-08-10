#!/usr/bin/env python3
"""
Debug Test - Check what's working
"""

import sys
import os
print("🧪 Debug Test Starting...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

# Test 1: Basic functionality
print("\n✅ Test 1: Basic Python - PASSED")

# Test 2: Check if tkinter is available
try:
    import tkinter as tk
    print("✅ Test 2: Tkinter import - PASSED")
    
    # Test 3: Can we create a window?
    try:
        root = tk.Tk()
        root.withdraw()  # Hide the window immediately
        print("✅ Test 3: Tkinter window creation - PASSED")
        root.destroy()
        
        # Test 4: Try the simple popup
        print("\n🎯 Test 4: Simple popup test...")
        
        def create_test_popup():
            window = tk.Tk()
            window.title("🧪 Test Popup")
            window.geometry("400x200")
            window.configure(bg='lightblue')
            
            label = tk.Label(window, text="✅ Popup Test Successful!\n\nThis popup works!", 
                           font=("Arial", 14), bg='lightblue', pady=20)
            label.pack()
            
            button = tk.Button(window, text="Close", command=window.destroy,
                             font=("Arial", 12), padx=20, pady=5)
            button.pack(pady=10)
            
            # Center the window
            window.update_idletasks()
            x = (window.winfo_screenwidth() // 2) - (window.winfo_width() // 2)
            y = (window.winfo_screenheight() // 2) - (window.winfo_height() // 2)
            window.geometry(f"+{x}+{y}")
            
            # Make it appear on top
            window.attributes('-topmost', True)
            window.focus_force()
            
            print("🪟 Popup window should appear now...")
            window.mainloop()
            print("✅ Popup closed successfully")
        
        create_test_popup()
        print("✅ Test 4: Simple popup - PASSED")
        
    except Exception as e:
        print(f"❌ Test 3: Tkinter window creation failed: {e}")
        
except ImportError as e:
    print(f"❌ Test 2: Tkinter import failed: {e}")
    print("💡 Tkinter might not be installed with your Python")

print("\n🧪 Debug test completed!")
input("Press Enter to exit...")

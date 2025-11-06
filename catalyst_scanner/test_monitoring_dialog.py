#!/usr/bin/env python3
"""
Test the new monitoring service dialog integration
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import tkinter as tk
    from gui.monitoring_service_dialog import show_monitoring_service_dialog
    from gui.gui_styles import apply_theme_to_root
    
    def test_dialog():
        root = tk.Tk()
        root.title("Test Monitoring Dialog")
        root.geometry("300x200")
        apply_theme_to_root(root)
        
        # Create test button
        test_btn = tk.Button(root, text="Open Monitoring Service Dialog", 
                           command=lambda: show_monitoring_service_dialog(root))
        test_btn.pack(expand=True)
        
        root.mainloop()
    
    if __name__ == "__main__":
        test_dialog()
        
except Exception as e:
    print(f"Test error: {e}")
    import traceback
    traceback.print_exc()
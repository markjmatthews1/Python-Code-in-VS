#!/usr/bin/env python3
"""
Quick launcher for the main window with monitoring button
"""

import sys
import os
import subprocess

# Add the catalyst_scanner directory to Python path
catalyst_dir = r"C:\Users\mjmat\Python Code in VS\catalyst_scanner"
sys.path.insert(0, catalyst_dir)
os.chdir(catalyst_dir)

try:
    import tkinter as tk
    from gui.main_window import CatalystScannerMainWindow
    from gui.gui_styles import apply_theme_to_root
    
    def main():
        root = tk.Tk()
        root.title("🎯 Catalyst Scanner - Investment Research Platform")
        root.geometry("2800x900")  # Made twice as wide: 1400 -> 2800
        
        # Apply theme
        apply_theme_to_root(root)
        
        # Configure grid
        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(0, weight=1)
        
        # Create main window
        main_window = CatalystScannerMainWindow(root)
        
        def on_closing():
            """Handle main window closing"""
            import tkinter.messagebox as msgbox
            
            # Check if monitoring service might be running
            try:
                result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                       capture_output=True, text=True)
                python_count = result.stdout.count('python.exe')
                
                if python_count > 1:  # More than just this GUI
                    response = msgbox.askyesno(
                        "🎯 Background Monitoring Active", 
                        "Background monitoring service appears to be running.\n\n"
                        "• Closing this window will NOT stop monitoring\n"
                        "• Your portfolio will continue being monitored 24/7\n"
                        "• Use 🎯 MONITOR button → 🛑 Stop Service to stop monitoring\n\n"
                        "Close the main window anyway?"
                    )
                    if response:
                        root.destroy()
                else:
                    root.destroy()
            except:
                # If error checking, just ask to confirm
                response = msgbox.askyesno(
                    "🎯 Close Catalyst Scanner", 
                    "Close the main window?\n\n"
                    "Note: Any background monitoring will continue running."
                )
                if response:
                    root.destroy()
        
        # Set close protocol
        root.protocol("WM_DELETE_WINDOW", on_closing)
        
        print("🎯 Catalyst Scanner main window loaded successfully!")
        print("✨ Features available:")
        print("   • Portfolio analysis")
        print("   • Real-time insights")
        print("   • Background monitoring service (🎯 MONITOR button)")
        print("   • Settings and configuration")
        
        root.mainloop()
    
    if __name__ == "__main__":
        main()
        
except Exception as e:
    print(f"❌ Error starting Catalyst Scanner: {e}")
    import traceback
    traceback.print_exc()
    input("Press Enter to exit...")
"""
Test the updated colorful settings dialog
"""

import tkinter as tk
import sys
import os

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from gui.settings_dialog import show_settings_dialog
    from utils.auto_refresh_manager import AutoRefreshManager
    from alerts.alert_system import AlertSystem
    
    print("🎨 TESTING COLORFUL SETTINGS DIALOG")
    
    # Create test GUI
    root = tk.Tk()
    root.title("Settings Dialog Test")
    root.geometry("400x200")
    root.configure(bg='#1e1e1e')
    
    # Create auto-refresh and alert systems
    auto_refresh_manager = AutoRefreshManager()
    alert_system = AlertSystem()
    
    def open_settings():
        """Open the settings dialog"""
        try:
            show_settings_dialog(root, auto_refresh_manager, alert_system)
            print("✅ Settings dialog opened successfully!")
        except Exception as e:
            print(f"❌ Error opening settings: {e}")
            import traceback
            traceback.print_exc()
    
    # Create test button
    test_button = tk.Button(root, 
                           text="🎨 Open Colorful Settings", 
                           command=open_settings,
                           font=('Arial', 14, 'bold'),
                           bg='#007acc', fg='white',
                           padx=20, pady=10,
                           relief='raised', bd=3)
    test_button.pack(expand=True)
    
    instructions = tk.Label(root,
                           text="Click the button to test the enlarged, colorful settings dialog!",
                           bg='#1e1e1e', fg='white',
                           font=('Arial', 12),
                           wraplength=350)
    instructions.pack(pady=10)
    
    print("🚀 Test window ready - click the button to test settings!")
    root.mainloop()

except Exception as e:
    print(f"❌ Import or setup error: {e}")
    import traceback
    traceback.print_exc()
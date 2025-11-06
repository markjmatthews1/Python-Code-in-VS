"""
Test Auto-Refresh and Alert Integration
Quick test to verify the new features work together
"""

import tkinter as tk
import sys
import os

# Add the parent directory to the path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

from gui.main_window import CatalystScannerMainWindow
from gui.settings_dialog import show_settings_dialog
from utils.auto_refresh_manager import AutoRefreshManager
from alerts.alert_system import AlertSystem


def test_integration():
    """Test the integration of auto-refresh and alert systems"""
    print("Testing Auto-Refresh and Alert Integration...")
    
    # Create main window
    root = tk.Tk()
    app = CatalystScannerMainWindow(root)
    
    print("✅ Main window created successfully")
    print(f"✅ Auto-refresh manager: {'Available' if hasattr(app, 'auto_refresh_manager') else 'Missing'}")
    print(f"✅ Alert system: {'Available' if hasattr(app, 'alert_system') else 'Missing'}")
    
    # Test auto-refresh settings
    if hasattr(app, 'auto_refresh_manager'):
        refresh_status = app.auto_refresh_manager.get_status()
        print(f"✅ Auto-refresh status: {refresh_status.get('running', 'Unknown')}")
        print(f"✅ Refresh interval: {app.auto_refresh_manager.get_setting('refresh_interval_minutes', 'Unknown')} minutes")
    
    # Test alert settings
    if hasattr(app, 'alert_system'):
        visual_enabled = app.alert_system.get_setting('visual_alerts_enabled', 'Unknown')
        audio_enabled = app.alert_system.get_setting('audio_alerts_enabled', 'Unknown')
        print(f"✅ Visual alerts: {'Enabled' if visual_enabled else 'Disabled'}")
        print(f"✅ Audio alerts: {'Enabled' if audio_enabled else 'Disabled'}")
    
    # Add test button to open settings
    def open_test_settings():
        try:
            show_settings_dialog(root, app.auto_refresh_manager, app.alert_system)
            print("✅ Settings dialog opened successfully")
        except Exception as e:
            print(f"❌ Settings dialog error: {e}")
    
    test_button = tk.Button(root, text="🔧 Test Settings Dialog", 
                           command=open_test_settings,
                           font=('Arial', 12, 'bold'),
                           bg='#4CAF50', fg='white',
                           padx=20, pady=10)
    test_button.pack(pady=20)
    
    print("\n🎯 Integration test complete! Look for:")
    print("   • Auto-refresh status in title bar")
    print("   • Settings menu working")
    print("   • Test button to open settings dialog")
    print("   • All systems properly initialized")
    
    # Start the GUI
    root.mainloop()


if __name__ == "__main__":
    test_integration()
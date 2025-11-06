"""
Test FIXED Live Dashboard Panel
==============================

Test the updated Live Dashboard Panel with the proven working TreeView approach.

Author: GitHub Copilot
Date: October 3, 2025
"""

import tkinter as tk
import sys
import os

# Add paths
catalyst_path = os.path.dirname(__file__)
sys.path.insert(0, catalyst_path)
parent_path = os.path.dirname(catalyst_path)
sys.path.insert(0, parent_path)

def test_fixed_live_dashboard():
    """Test the FIXED Live Dashboard Panel"""
    print("🎯 Testing FIXED Live Dashboard Panel...")
    
    # Create main window
    root = tk.Tk()
    root.title("FIXED Live Dashboard Panel Test")
    root.geometry("1200x800")
    
    try:
        # Import the fixed live dashboard panel
        from gui.live_dashboard_panel import LiveDashboardPanel
        
        # Create live dashboard panel (no portfolio loader needed - it will use test data)
        dashboard = LiveDashboardPanel(root, None)
        print("✅ Fixed Live Dashboard Panel created successfully")
        
        print("\n🚀 FIXED Live Dashboard Panel test window opened!")
        print("   - This should now show portfolio data using the proven working method")
        print("   - You should see 8 portfolio tickers with catalyst scores")
        print("   - Status should show 'Online' with proper summary stats")
        print("   - Close window when done testing")
        
    except Exception as e:
        print(f"❌ Error creating fixed dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        # Create error label
        error_label = tk.Label(root, text=f"Fixed Dashboard Error: {e}", 
                              font=("Arial", 14), fg="red")
        error_label.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_fixed_live_dashboard()
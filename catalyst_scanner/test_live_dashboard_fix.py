"""
Test Live Dashboard - Simplified TreeView Fix
============================================

This script tests the fixed Live Dashboard TreeView implementation
using the working approach from our minimal test.

Author: GitHub Copilot
Date: October 3, 2025
"""

import tkinter as tk
import sys
import os

# Add catalyst_scanner to path
catalyst_path = os.path.dirname(__file__)
sys.path.insert(0, catalyst_path)

# Add parent directory for portfolio loading
parent_path = os.path.dirname(catalyst_path)
sys.path.insert(0, parent_path)

def test_live_dashboard():
    """Test the fixed live dashboard implementation"""
    print("🧪 Testing Fixed Live Dashboard...")
    
    # Create main window
    root = tk.Tk()
    root.title("Live Dashboard Test - Fixed TreeView")
    root.geometry("1200x800")
    
    try:
        # Import portfolio loader from correct location
        from data_collectors.portfolio_loader import PortfolioLoader
        
        # Create portfolio loader with explicit path to Bryan Perry file
        bryan_perry_path = os.path.join(parent_path, "Bryan Perry Transactions.xlsx")
        print(f"🔍 Looking for Bryan Perry file at: {bryan_perry_path}")
        print(f"🔍 File exists: {os.path.exists(bryan_perry_path)}")
        
        portfolio_loader = PortfolioLoader(bryan_perry_path)
        
        # Test portfolio loading
        load_success = portfolio_loader.load_portfolio()
        print(f"✅ Portfolio load result: {load_success}")
        
        if load_success:
            tickers = portfolio_loader.get_tickers()
            portfolio_data = portfolio_loader.get_portfolio_data()
            print(f"✅ Portfolio loader: {len(tickers)} tickers, {len(portfolio_data)} data entries")
            print(f"   📊 Tickers: {tickers[:5]}...")  # Show first 5
        else:
            print("⚠️ Portfolio loading failed, using fallback data")
            portfolio_loader = None
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Creating fallback test...")
        portfolio_loader = None
        
        # Import fixed live dashboard
        from gui.live_dashboard_panel import LiveDashboardPanel
        
        # Create live dashboard panel
        dashboard = LiveDashboardPanel(root, portfolio_loader)
        print("✅ Live dashboard panel created successfully")
        
        # Force an immediate data load to test TreeView
        dashboard._load_real_portfolio_data()
        print("✅ Portfolio data load triggered")
        
        print("\n🚀 Live Dashboard test window opened!")
        print("   - Check if you can see the portfolio data in the TreeView")
        print("   - This uses the same approach as the working minimal test")
        print("   - Close window when done testing")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Creating fallback test...")
        
        # Create simple fallback
        from gui.live_dashboard_panel import LiveDashboardPanel
        dashboard = LiveDashboardPanel(root, None)  # No portfolio loader
        
    except Exception as e:
        print(f"❌ Error creating dashboard: {e}")
        import traceback
        traceback.print_exc()
        
        # Create error label
        error_label = tk.Label(root, text=f"Dashboard Error: {e}", 
                              font=("Arial", 14), fg="red")
        error_label.pack(expand=True)
    
    root.mainloop()

if __name__ == "__main__":
    test_live_dashboard()
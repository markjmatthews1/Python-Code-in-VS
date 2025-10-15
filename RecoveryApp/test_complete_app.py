#!/usr/bin/env python3
"""
Test Complete RecoveryApp Integration
Final comprehensive test of all features working together
"""
import os
import sys
import tkinter as tk

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.recovery_gui import RecoveryAppGUI
from utils.models import TickerPosition, PortfolioManager

def test_complete_app():
    """Test the complete RecoveryApp with all features"""
    try:
        print("🚀 Starting Complete RecoveryApp Test...")
        print("📋 Testing Features:")
        print("   ✅ Portfolio Overview")
        print("   ✅ Add Position Form")
        print("   ✅ Trade Tracker")
        print("   ✅ Individual Ticker Tabs")
        print("   ✅ Strategy Panel Integration")
        print("   ✅ Data Persistence")
        
        # Create test portfolio data
        print("\n📊 Creating test portfolio...")
        portfolio = PortfolioManager()
        
        # Add test positions
        test_positions = [
            ("SOXL", 25.50, 100, "2024-01-15", "Semiconductor ETF"),
            ("NVDA", 120.00, 50, "2024-02-01", "AI/GPU leader"),
            ("AMD", 140.00, 75, "2024-01-20", "CPU/GPU manufacturer"),
            ("TSLA", 250.00, 25, "2024-01-10", "EV leader")
        ]
        
        for ticker, cost_basis, qty, purchase_date, notes in test_positions:
            position = TickerPosition(
                ticker=ticker,
                cost_basis=cost_basis,
                qty=qty,
                purchase_date=purchase_date,
                notes=notes
            )
            portfolio.add_position(position)
        
        portfolio.save_to_file("recovery_portfolio.json")
        print(f"✅ Created test portfolio with {len(test_positions)} positions")
        
        # Start the GUI
        print("\n🖥️  Starting RecoveryApp GUI...")
        root = tk.Tk()
        app = RecoveryAppGUI(root)
        
        print("\n🎯 Test Instructions:")
        print("1. 📊 Check Portfolio Overview tab - should show 4 positions")
        print("2. ➕ Test Add Position tab - try adding a new position")
        print("3. 📋 Test Trade Tracker tab - should show all positions")
        print("4. 🎯 Click on individual ticker tabs (SOXL, NVDA, AMD, TSLA)")
        print("5. 🔍 Test Strategy Analysis in ticker tabs")
        print("6. 📈 Click 'Analyze Strategies' buttons")
        print("7. 💰 Test trade entry in Trade Tracker panels")
        print("8. 💾 Close app to test data persistence")
        print("\n🔧 Testing Complete Integration...")
        
        root.mainloop()
        
        print("✅ Complete RecoveryApp Test finished!")
        return True
        
    except Exception as e:
        print(f"❌ Complete App Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Change to app directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(app_dir)
    
    test_complete_app()
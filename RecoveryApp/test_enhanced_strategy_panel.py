#!/usr/bin/env python3
"""
Test Enhanced Strategy Panel
Tests the enhanced strategy panel with both put and call overlays
"""
import os
import sys
import tkinter as tk

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui.enhanced_strategy_panel import EnhancedStrategyPanel
from utils.ui_utils import UIConfig

class EnhancedStrategyTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enhanced Strategy Panel Test")
        self.root.geometry("1000x800")
        self.root.configure(bg=UIConfig.COLORS['bg_primary'])
        
        self.create_interface()
    
    def create_interface(self):
        """Create test interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Enhanced Strategy Panel Test - Put & Call Overlays",
            font=UIConfig.TITLE_FONT,
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(pady=20)
        
        # Notebook for testing different tickers
        self.notebook = tk.ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create tabs for each ticker
        test_tickers = ["SOXL", "NVDA", "AMD", "TSLA"]
        for ticker in test_tickers:
            self.create_ticker_tab(ticker)
    
    def create_ticker_tab(self, ticker):
        """Create a tab to test enhanced strategy panel for specific ticker"""
        tab_frame = tk.Frame(self.root, bg=UIConfig.COLORS['bg_primary'])
        self.notebook.add(tab_frame, text=f"{ticker} Strategies")
        
        # Enhanced Strategy Panel
        strategy_panel = EnhancedStrategyPanel(tab_frame, ticker)
    
    def run(self):
        """Run the test application"""
        print("🧪 Enhanced Strategy Panel Test")
        print("📊 Testing enhanced strategy panels with put and call overlays")
        print("🎯 Ticker tabs available: SOXL, NVDA, AMD, TSLA")
        print("✅ Click 'Analyze Strategies' buttons to test both strategy types")
        print("🔄 Switch between tabs to test multiple tickers")
        print("📈 Use tabs within panels to switch between Put and Call strategies")
        print("❌ Close window to complete test")
        
        self.root.mainloop()

def test_enhanced_strategy_panel():
    """Run enhanced strategy panel test"""
    try:
        print("🚀 Starting Enhanced Strategy Panel Test...")
        
        # Test imports
        print("✅ Testing imports...")
        from gui.enhanced_strategy_panel import EnhancedStrategyPanel
        from utils.strategy_engine import evaluate_put_overlay, evaluate_call_overlay
        print("✅ All imports successful")
        
        # Test GUI integration
        print("✅ Testing enhanced GUI integration...")
        app = EnhancedStrategyTester()
        app.run()
        
        print("✅ Enhanced Strategy Panel Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Enhanced Strategy Panel Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_enhanced_strategy_panel()
#!/usr/bin/env python3
"""
Test Strategy Panel Integration
Tests the integration of strategy panel with main GUI
"""
import os
import sys
import tkinter as tk
from tkinter import ttk

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.models import TickerPosition, PortfolioManager
from gui.strategy_panel import StrategyPanel
from utils.ui_utils import UIConfig

class StrategyIntegrationTester:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Strategy Panel Integration Test")
        self.root.geometry("900x700")
        self.root.configure(bg=UIConfig.COLORS['bg_primary'])
        
        # Test portfolio
        self.portfolio = PortfolioManager()
        self.setup_test_positions()
        
        self.create_interface()
    
    def setup_test_positions(self):
        """Create test positions for strategy testing"""
        test_positions = [
            ("SOXL", 25.50, 100, "2024-01-15"),
            ("NVDA", 120.00, 50, "2024-02-01"),
            ("AMD", 140.00, 75, "2024-01-20"),
            ("TSLA", 250.00, 25, "2024-01-10")
        ]
        
        for ticker, cost_basis, qty, purchase_date in test_positions:
            position = TickerPosition(
                ticker=ticker,
                cost_basis=cost_basis,
                qty=qty,
                purchase_date=purchase_date
            )
            self.portfolio.add_position(position)
    
    def create_interface(self):
        """Create test interface"""
        # Title
        title_label = tk.Label(
            self.root,
            text="Strategy Panel Integration Test",
            font=UIConfig.TITLE_FONT,
            fg=UIConfig.COLORS['accent'],
            bg=UIConfig.COLORS['bg_primary']
        )
        title_label.pack(pady=20)
        
        # Notebook for testing different tickers
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Create tabs for each position
        for ticker in ["SOXL", "NVDA", "AMD", "TSLA"]:
            self.create_strategy_tab(ticker)
    
    def create_strategy_tab(self, ticker):
        """Create a tab to test strategy panel for specific ticker"""
        tab_frame = ttk.Frame(self.notebook)
        self.notebook.add(tab_frame, text=f"{ticker} Strategies")
        
        # Container
        container = tk.Frame(tab_frame, bg=UIConfig.COLORS['bg_primary'])
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Header
        header_label = tk.Label(
            container,
            text=f"{ticker} Recovery Strategies",
            font=UIConfig.HEADER_FONT,
            fg=UIConfig.COLORS['text_light'],
            bg=UIConfig.COLORS['bg_primary']
        )
        header_label.pack(pady=(0, 20))
        
        # Strategy Panel
        strategy_panel = StrategyPanel(container, ticker)
        strategy_panel.pack(fill=tk.BOTH, expand=True)
    
    def run(self):
        """Run the test application"""
        print("🧪 Strategy Panel Integration Test")
        print("📊 Testing strategy panels for: SOXL, NVDA, AMD, TSLA")
        print("✅ Click 'Analyze Strategies' buttons to test integration")
        print("🔄 Switch between tabs to test multiple tickers")
        print("❌ Close window to complete test")
        
        self.root.mainloop()

def test_strategy_integration():
    """Run strategy integration test"""
    try:
        print("🚀 Starting Strategy Panel Integration Test...")
        
        # Test imports
        print("✅ Testing imports...")
        from gui.strategy_panel import StrategyPanel
        from utils.strategy_engine import OptionChainAnalyzer, PutOverlayEvaluator
        print("✅ All imports successful")
        
        # Test GUI integration
        print("✅ Testing GUI integration...")
        app = StrategyIntegrationTester()
        app.run()
        
        print("✅ Strategy Panel Integration Test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Strategy Integration Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_strategy_integration()
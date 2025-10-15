#!/usr/bin/env python3
"""
Complete test of the Enhanced Strategy Panel with all three strategy types
Tests the GUI integration with put overlays, call overlays, and synthetic recovery
"""

import tkinter as tk
from tkinter import ttk
import time
import threading
from gui.enhanced_strategy_panel import EnhancedStrategyPanel

def test_enhanced_strategy_panel():
    """Test the enhanced strategy panel with all strategy types"""
    print("🧪 Enhanced Strategy Panel Complete Testing Suite")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("Enhanced Strategy Panel Test - All Strategies")
    root.geometry("1000x800")
    
    # Test with different tickers
    test_tickers = ["SOXL", "NVDA", "AMD"]
    
    # Create notebook for multiple tests
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    panels = {}
    
    for ticker in test_tickers:
        # Create frame for each ticker test
        test_frame = tk.Frame(notebook)
        notebook.add(test_frame, text=f"{ticker} Strategies")
        
        # Create enhanced strategy panel
        panel = EnhancedStrategyPanel(test_frame, ticker)
        panels[ticker] = panel
        
        print(f"✅ Created enhanced strategy panel for {ticker}")
    
    # Add control panel
    control_frame = tk.Frame(root)
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def analyze_all_strategies():
        """Analyze strategies for all tickers"""
        print("\n🚀 Starting strategy analysis for all tickers...")
        for ticker, panel in panels.items():
            print(f"  📊 Analyzing {ticker}...")
            panel.analyze_strategies()
    
    def refresh_all_strategies():
        """Refresh all strategy analyses"""
        print("\n🔄 Refreshing all strategies...")
        for ticker, panel in panels.items():
            panel.refresh_strategies()
    
    # Control buttons
    tk.Button(
        control_frame,
        text="🚀 Analyze All Strategies",
        command=analyze_all_strategies,
        bg='#4CAF50',
        fg='white',
        font=('Arial', 12, 'bold'),
        padx=20
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        control_frame,
        text="🔄 Refresh All",
        command=refresh_all_strategies,
        bg='#2196F3',
        fg='white',
        font=('Arial', 12),
        padx=20
    ).pack(side=tk.LEFT, padx=5)
    
    # Add instruction label
    instruction_frame = tk.Frame(root)
    instruction_frame.pack(fill=tk.X, padx=10, pady=5)
    
    tk.Label(
        instruction_frame,
        text="📋 Instructions: Click 'Analyze All Strategies' to load put overlays, call overlays, and synthetic recovery for all tickers",
        font=('Arial', 10),
        fg='#666',
        wraplength=800
    ).pack()
    
    print("\n🎯 Enhanced Strategy Panel Test Setup Complete!")
    print("Features being tested:")
    print("  ✅ Put Overlay Strategies - Traditional protective puts")
    print("  ✅ Call Overlay Strategies - Covered calls for income")
    print("  ✅ Synthetic Recovery - Double down + covered calls")
    print("  ✅ Multi-ticker comparison")
    print("  ✅ Real-time strategy analysis")
    print("  ✅ Comprehensive risk assessment")
    print("\n💡 Use the tabs to switch between different tickers")
    print("💡 Each tab shows all three strategy types for comparison")
    
    # Auto-analyze after a short delay
    def auto_analyze():
        time.sleep(2)
        root.after(0, analyze_all_strategies)
    
    auto_thread = threading.Thread(target=auto_analyze)
    auto_thread.daemon = True
    auto_thread.start()
    
    root.mainloop()

if __name__ == "__main__":
    test_enhanced_strategy_panel()
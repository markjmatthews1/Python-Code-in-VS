#!/usr/bin/env python3
"""
Test Enhanced Strategy Cards Display Panel
Tests the new color-coded strategy cards with comprehensive trade details
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
from gui.strategy_cards_panel import StrategyCardsPanel
from utils.models import TickerPosition, TradeEntry

def test_strategy_cards_display():
    """Test the enhanced strategy cards display"""
    print("🧪 Enhanced Strategy Cards Display Testing Suite")
    print("=" * 60)
    
    # Create test window
    root = tk.Tk()
    root.title("Strategy Cards Display Test")
    root.geometry("1400x900")
    
    # Create test positions with different scenarios
    test_positions = [
        TickerPosition(
            ticker="SOXL",
            qty=100,
            cost_basis=42.50,
            purchase_date="2024-01-15",
            trades=[
                TradeEntry(
                    type="short_put",
                    strike=35.0,
                    expiry="2025-11-15",
                    premium=2.50,
                    status="open"
                )
            ]
        ),
        TickerPosition(
            ticker="NVDA",
            qty=50,
            cost_basis=120.00,
            purchase_date="2024-02-20",
            trades=[]
        ),
        TickerPosition(
            ticker="TSLA",
            qty=25,
            cost_basis=250.00,
            purchase_date="2024-03-10",
            trades=[
                TradeEntry(
                    type="covered_call",
                    strike=260.0,
                    expiry="2025-10-25",
                    premium=8.75,
                    status="open"
                )
            ]
        )
    ]
    
    # Create notebook for multiple position tests
    from tkinter import ttk
    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    panels = {}
    
    for position in test_positions:
        # Create frame for each position test
        test_frame = tk.Frame(notebook)
        notebook.add(test_frame, text=f"{position.ticker} Strategy Cards")
        
        # Create strategy cards panel
        panel = StrategyCardsPanel(test_frame, position)
        panels[position.ticker] = panel
        
        print(f"✅ Created strategy cards panel for {position.ticker}")
        print(f"   Position: {position.qty} shares @ ${position.cost_basis:.2f}")
        print(f"   Existing trades: {len(position.trades)}")
    
    # Add control panel
    control_frame = tk.Frame(root)
    control_frame.pack(fill=tk.X, padx=10, pady=5)
    
    def refresh_all_panels():
        """Refresh all strategy card panels"""
        print("\n🔄 Refreshing all strategy card panels...")
        for ticker, panel in panels.items():
            print(f"  📊 Refreshing {ticker}...")
            panel.refresh_strategies()
    
    def export_all_analyses():
        """Export all strategy analyses"""
        print("\n📊 Exporting all strategy analyses...")
        for ticker, panel in panels.items():
            print(f"  📁 Exporting {ticker} analysis...")
            panel.export_strategies()
    
    # Control buttons
    tk.Button(
        control_frame,
        text="🔄 Refresh All Strategy Cards",
        command=refresh_all_panels,
        bg='#4CAF50',
        fg='white',
        font=('Arial', 12, 'bold'),
        padx=20
    ).pack(side=tk.LEFT, padx=5)
    
    tk.Button(
        control_frame,
        text="📊 Export All Analyses",
        command=export_all_analyses,
        bg='#2196F3',
        fg='white',
        font=('Arial', 12),
        padx=20
    ).pack(side=tk.LEFT, padx=5)
    
    # Add instruction label
    instruction_frame = tk.Frame(root)
    instruction_frame.pack(fill=tk.X, padx=10, pady=5)
    
    instructions = (
        "📋 Strategy Cards Features: "
        "Color-coded ranking | Trade type identification | Strike & expiry details | "
        "Premium & net impact | Time-to-recovery analysis | Comprehensive scoring"
    )
    
    tk.Label(
        instruction_frame,
        text=instructions,
        font=('Arial', 10),
        fg='#666',
        wraplength=1200
    ).pack()
    
    print("\n🎯 Enhanced Strategy Cards Test Setup Complete!")
    print("Features being tested:")
    print("  ✅ Color-coded strategy cards with ranking")
    print("  ✅ Trade type identification (PUT/CALL/SYNTHETIC)")
    print("  ✅ Strike price and expiry display")
    print("  ✅ Premium income and net impact calculations")
    print("  ✅ Time-to-recovery impact analysis")
    print("  ✅ Comprehensive strategy comparison")
    print("  ✅ Recovery time estimation integration")
    print("  ✅ Multi-position testing across different scenarios")
    
    print("\n💡 Use the tabs to switch between different positions")
    print("💡 Each tab shows comprehensive strategy analysis with visual cards")
    print("💡 Cards are color-coded by ranking and strategy type")
    print("💡 Scroll down to see all strategy types and comparisons")
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_strategy_cards_display()
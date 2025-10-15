#!/usr/bin/env python3
"""
Test the fixed AlertsPanel layout to ensure Add Alert section is visible
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import tkinter as tk

# Mock portfolio manager for testing
class MockPortfolioManager:
    def __init__(self):
        self.positions = []

def test_fixed_alerts_panel():
    """Test the fixed AlertsPanel to verify Add Alert section is visible"""
    
    root = tk.Tk()
    root.title("Fixed AlertsPanel Test")
    root.geometry("1200x800")
    
    try:
        from gui.alerts_panel import AlertsPanel
        
        # Create mock portfolio manager
        portfolio_manager = MockPortfolioManager()
        
        # Create main frame
        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create AlertsPanel
        alerts_panel = AlertsPanel(main_frame, portfolio_manager)
        
        # Add some test content to make sure scrolling works
        print("AlertsPanel created successfully!")
        print("Check that:")
        print("1. Add Alert section is visible at the bottom")
        print("2. Alert Name field is visible")
        print("3. ➕ Add Alert button is visible")
        print("4. Scroll bar appears if content is too tall")
        
        root.mainloop()
        
    except Exception as e:
        print(f"Error creating AlertsPanel: {e}")
        # Create simple test layout instead
        create_simple_layout_test(root)

def create_simple_layout_test(root):
    """Create a simple layout test to verify scrolling works"""
    
    # Create scrollable frame
    canvas = tk.Canvas(root, bg='lightgray')
    scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
    scrollable_frame = tk.Frame(canvas, bg='lightgray')
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")
    
    # Add test content
    for i in range(20):
        frame = tk.Frame(scrollable_frame, bg='blue' if i % 2 else 'red', height=50)
        frame.pack(fill=tk.X, pady=2)
        tk.Label(frame, text=f"Section {i}", fg='white', bg=frame['bg']).pack(pady=10)
    
    # Add "Add Alert" section at bottom
    add_frame = tk.Frame(scrollable_frame, bg='green', height=100)
    add_frame.pack(fill=tk.X, pady=10)
    tk.Label(add_frame, text="➕ ADD ALERT SECTION (Should be visible!)", 
             fg='white', bg='green', font=('Arial', 14, 'bold')).pack(pady=20)
    
    # Mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    print("Simple layout test created - check if green 'ADD ALERT SECTION' is visible at bottom!")
    root.mainloop()

if __name__ == "__main__":
    test_fixed_alerts_panel()
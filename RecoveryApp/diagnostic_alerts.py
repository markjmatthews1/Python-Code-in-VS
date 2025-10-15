"""
Alerts Panel Diagnostic - Find the Add Alert Button
"""
import tkinter as tk
from tkinter import ttk
from gui.alerts_panel import AlertsPanel
from utils.models import PortfolioManager, TickerPosition

def diagnostic_test():
    """Diagnostic test to locate the Add Alert button"""
    print("🔍 Alerts Panel Button Diagnostic...")
    
    # Create your actual portfolio data
    portfolio = PortfolioManager()
    
    # Load your real portfolio
    try:
        portfolio.load_from_file("recovery_portfolio.json")
        print(f"✅ Loaded real portfolio with {len(portfolio.positions)} positions:")
        for pos in portfolio.positions:
            print(f"   - {pos.ticker}: {pos.qty} shares @ ${pos.cost_basis}")
    except Exception as e:
        print(f"⚠️ Could not load portfolio: {e}")
        return
    
    root = tk.Tk()
    root.title("🔍 Alerts Panel Diagnostic")
    root.geometry("1000x800")
    
    # Create main frame
    main_frame = tk.Frame(root, bg='white')
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Add title
    title = tk.Label(main_frame, text="🔍 Diagnostic: Looking for Add Alert Button", 
                     font=('Arial', 16, 'bold'), bg='white', fg='red')
    title.pack(pady=10)
    
    # Instructions
    instructions = tk.Text(main_frame, height=4, bg='lightyellow')
    instructions.pack(fill=tk.X, padx=10, pady=5)
    instructions.insert('1.0', '''
DIAGNOSTIC INSTRUCTIONS:
1. Scroll down through the alerts panel below
2. Look for "Add New Alert:" section 
3. You should see: Ticker dropdown, Strategy dropdown, Premium field, Strike Distance field
4. At the bottom right should be a green "➕ Add Alert" button
''')
    instructions.config(state=tk.DISABLED)
    
    # Create scrollable frame for alerts panel
    canvas = tk.Canvas(main_frame, bg='white')
    scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
    scrollable_frame = ttk.Frame(canvas)
    
    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )
    
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    
    # Pack canvas and scrollbar
    canvas.pack(side="left", fill="both", expand=True, padx=10)
    scrollbar.pack(side="right", fill="y")
    
    # Create alerts panel inside scrollable frame
    try:
        alerts_panel = AlertsPanel(scrollable_frame, portfolio)
        print("✅ Alerts panel created - check the GUI window!")
        
        # Bind mouse wheel to canvas
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        print("\n🎯 What to do:")
        print("1. Check the GUI window that opened")
        print("2. Scroll down to find 'Add New Alert:' section")
        print("3. The ticker dropdown should show: SOXL, PINS")
        print("4. Fill out the form and try clicking '➕ Add Alert'")
        print("5. Close the window when done testing")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    diagnostic_test()
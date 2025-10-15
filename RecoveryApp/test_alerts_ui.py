"""
Quick test to verify th    # Create alerts panel
    try:
        alerts_panel = AlertsPanel(alerts_frame, portfolio)
        # Note: AlertsPanel creates its own widgets inside the frame, no need to pack
        print("✅ Alerts panel created successfully")rts Panel UI
"""
import tkinter as tk
from gui.alerts_panel import AlertsPanel
from utils.models import PortfolioManager, TickerPosition

def test_alerts_panel():
    """Test the alerts panel UI"""
    print("🧪 Testing Alerts Panel...")
    
    # Create test data
    portfolio = PortfolioManager()
    
    # Add test positions (like your real ones)
    soxl = TickerPosition("SOXL", 54.43, 110, "2025-06-26")
    pins = TickerPosition("PINS", 43.79, 200, "2025-06-12")
    
    portfolio.add_position(soxl)
    portfolio.add_position(pins)
    
    print(f"✅ Created test portfolio with {len(portfolio.positions)} positions")
    
    # Create GUI
    root = tk.Tk()
    root.title("Alerts Panel Test")
    root.geometry("900x700")
    
    # Create frame for alerts panel
    alerts_frame = tk.Frame(root)
    alerts_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create alerts panel
    try:
        alerts_panel = AlertsPanel(alerts_frame, portfolio)
        # Note: AlertsPanel creates its own widgets inside the frame, no need to pack
        print("✅ Alerts panel created successfully")
        
        print("\n📋 What to check:")
        print("1. Look for 'Add New Alert:' section")
        print("2. Verify ticker dropdown has SOXL and PINS")
        print("3. Check if '➕ Add Alert' button is visible")
        print("4. Try filling out the form and clicking the button")
        
        root.mainloop()
        
    except Exception as e:
        print(f"❌ Error creating alerts panel: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_alerts_panel()
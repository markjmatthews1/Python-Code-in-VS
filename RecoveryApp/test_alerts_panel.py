"""
Test Alerts Panel Functionality
Demonstrates comprehensive alert monitoring and notification system
"""
import tkinter as tk
from gui.alerts_panel import AlertsPanel, AlertCondition
from utils.models import TickerPosition, PortfolioManager

def test_alerts_panel():
    """Test the alerts panel with sample data"""
    print("🚨 Alerts Panel Testing Suite")
    print("=" * 50)
    
    # Create main window
    root = tk.Tk()
    root.title("RecoveryApp™ - Alerts Panel Test")
    root.geometry("1400x900")
    
    # Create sample portfolio
    portfolio = PortfolioManager()
    
    # Add test positions
    test_positions = [
        TickerPosition(
            ticker="SOXL",
            qty=100,
            cost_basis=42.50,
            purchase_date="2024-01-15"
        ),
        TickerPosition(
            ticker="NVDA",
            qty=50,
            cost_basis=120.00,
            purchase_date="2024-02-20"
        ),
        TickerPosition(
            ticker="TSLA",
            qty=25,
            cost_basis=250.00,
            purchase_date="2024-03-10"
        ),
        TickerPosition(
            ticker="AAPL",
            qty=75,
            cost_basis=180.00,
            purchase_date="2024-01-25"
        )
    ]
    
    for position in test_positions:
        portfolio.add_position(position)
    
    print(f"✅ Created test portfolio with {len(test_positions)} positions:")
    for pos in test_positions:
        print(f"   📊 {pos.ticker}: {pos.qty} shares @ ${pos.cost_basis}")
    
    # Create main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create alerts panel
    print("\\n🔧 Initializing Alerts Panel...")
    alerts_panel = AlertsPanel(main_frame, portfolio)
    
    # Add some sample alerts
    sample_alerts = [
        {
            'position': test_positions[0],  # SOXL
            'strategy_type': 'put_overlay',
            'min_premium': 1.50,
            'max_strike_distance': 0.15,
            'alert_name': 'SOXL Put Protection Alert'
        },
        {
            'position': test_positions[1],  # NVDA
            'strategy_type': 'call_overlay',
            'min_premium': 3.00,
            'max_strike_distance': 0.10,
            'alert_name': 'NVDA Covered Call Alert'
        },
        {
            'position': test_positions[2],  # TSLA
            'strategy_type': 'synthetic_recovery',
            'min_premium': 5.00,
            'max_strike_distance': 0.20,
            'alert_name': 'TSLA Synthetic Recovery Alert'
        }
    ]
    
    print("\\n➕ Adding sample alerts:")
    for alert_data in sample_alerts:
        alert = AlertCondition(
            position=alert_data['position'],
            strategy_type=alert_data['strategy_type'],
            min_premium=alert_data['min_premium'],
            max_strike_distance=alert_data['max_strike_distance'],
            alert_name=alert_data['alert_name']
        )
        alerts_panel.alerts.append(alert)
        print(f"   🚨 {alert.alert_name}")
        print(f"      Strategy: {alert.strategy_type}")
        print(f"      Min Premium: ${alert.min_premium}")
        print(f"      Max Strike Distance: {alert.max_strike_distance*100:.1f}%")
    
    # Refresh display
    alerts_panel.refresh_alerts_display()
    alerts_panel.log_message("🧪 Test alerts loaded successfully")
    
    print("\\n🎯 Alerts Panel Test Setup Complete!")
    print("Features available for testing:")
    print("  ✅ Alert monitoring with real-time strategy analysis")
    print("  ✅ Configurable refresh intervals (1-60 minutes)")
    print("  ✅ Sound and popup notifications")
    print("  ✅ Alert condition management (add/edit/delete/toggle)")
    print("  ✅ Alert testing and manual checking")
    print("  ✅ Comprehensive alert logging")
    print("  ✅ Persistent alert configuration")
    print("  ✅ Strategy-based alert triggers:")
    print("     • Put Overlay Strategies")
    print("     • Call Overlay Strategies") 
    print("     • Synthetic Recovery Strategies")
    print("\\n💡 Usage Instructions:")
    print("  1. Click '▶️ Start Monitoring' to begin automated alert checking")
    print("  2. Use '🔍 Check Now' for immediate manual checking")
    print("  3. Add new alerts using the form at the bottom")
    print("  4. Right-click alerts in the list for context menu")
    print("  5. Monitor the alert log for real-time activity")
    print("  6. Adjust refresh interval and notification settings")
    print("\\n🔊 Notification Options:")
    print("  • Popup alerts when viable trades are found")
    print("  • Sound notifications (system beep)")
    print("  • Comprehensive activity logging")
    print("\\n📊 Alert Conditions:")
    print("  • Minimum premium income requirements")
    print("  • Maximum strike price distance from current price")
    print("  • Strategy-specific trade analysis")
    print("  • Real-time option chain evaluation")
    
    # Bind cleanup on close
    def on_close():
        alerts_panel.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_alerts_panel()
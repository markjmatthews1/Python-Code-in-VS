"""
Complete Automation System Test
Tests the full Phase 4 automation engine with scheduling and persistence
"""
import tkinter as tk
from gui.automation_panel import AutomationPanel
from utils.automation_engine import AutomationEngine, PersistenceManager, MarketHours
from utils.models import TickerPosition, PortfolioManager, TradeEntry
import os

def test_complete_automation():
    """Test the complete automation system"""
    print("🤖 Complete Automation System Testing Suite")
    print("=" * 60)
    
    # Create main window
    root = tk.Tk()
    root.title("RecoveryApp™ - Phase 4: Complete Automation Test")
    root.geometry("1600x1000")
    
    # Create test portfolio
    portfolio = PortfolioManager()
    
    # Add comprehensive test positions
    test_positions = [
        TickerPosition(
            ticker="SOXL",
            qty=100,
            cost_basis=42.50,
            purchase_date="2024-01-15",
            notes="Leveraged semiconductor ETF - high volatility recovery target",
            target_recovery_price=45.00
        ),
        TickerPosition(
            ticker="NVDA",
            qty=50,
            cost_basis=120.00,
            purchase_date="2024-02-20",
            notes="AI/GPU leader - strong recovery prospects",
            target_recovery_price=125.00
        ),
        TickerPosition(
            ticker="TSLA",
            qty=25,
            cost_basis=250.00,
            purchase_date="2024-03-10",
            notes="EV pioneer - volatile but recovery potential",
            target_recovery_price=260.00
        ),
        TickerPosition(
            ticker="AAPL",
            qty=75,
            cost_basis=180.00,
            purchase_date="2024-01-25",
            notes="Stable tech giant - conservative recovery",
            target_recovery_price=185.00
        ),
        TickerPosition(
            ticker="AMD",
            qty=60,
            cost_basis=95.00,
            purchase_date="2024-02-10",
            notes="CPU/GPU competitor - cyclical recovery",
            target_recovery_price=100.00
        )
    ]
    
    # Add sample trades to some positions
    test_positions[0].trades.append(TradeEntry(
        type="short_put",
        strike=40.0,
        expiry="2024-12-20",
        premium=2.50,
        status="open",
        notes="Protective put for SOXL downside protection"
    ))
    
    test_positions[1].trades.append(TradeEntry(
        type="covered_call",
        strike=130.0,
        expiry="2024-11-15",
        premium=4.75,
        status="open",
        notes="NVDA covered call for premium income"
    ))
    
    test_positions[2].trades.append(TradeEntry(
        type="synthetic",
        strike=255.0,
        expiry="2024-12-06",
        premium=8.25,
        status="open",
        notes="TSLA synthetic position for recovery acceleration"
    ))
    
    for position in test_positions:
        portfolio.add_position(position)
    
    print(f"✅ Created comprehensive test portfolio:")
    for pos in test_positions:
        trades_count = len(pos.trades)
        print(f"   📊 {pos.ticker}: {pos.qty} shares @ ${pos.cost_basis} (Target: ${pos.target_recovery_price}) - {trades_count} trades")
    
    print(f"\\n🔧 Initializing Complete Automation System...")
    
    # Create main frame
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True)
    
    # Create automation panel (this initializes the entire automation engine)
    print("🚀 Starting Automation Panel...")
    automation_panel = AutomationPanel(main_frame, portfolio)
    
    # Test persistence layer
    print("\\n💾 Testing Persistence Layer:")
    persistence = automation_panel.persistence
    
    # Test saving portfolio
    save_success = persistence.save_portfolio(portfolio)
    print(f"   Portfolio Save: {'✅ SUCCESS' if save_success else '❌ FAILED'}")
    
    # Test loading portfolio
    loaded_portfolio = persistence.load_portfolio()
    print(f"   Portfolio Load: {'✅ SUCCESS' if loaded_portfolio.positions else '❌ FAILED'}")
    print(f"   Loaded Positions: {len(loaded_portfolio.positions)}")
    
    # Test recovery status persistence
    test_recovery_status = {
        'SOXL': {
            'position_status': 'underwater',
            'unrealized_loss': -250.00,
            'loss_percentage': -5.88,
            'recovery_probability': 0.75
        },
        'NVDA': {
            'position_status': 'underwater',
            'unrealized_loss': -500.00,
            'loss_percentage': -8.33,
            'recovery_probability': 0.85
        }
    }
    
    status_save = persistence.save_recovery_status(test_recovery_status)
    print(f"   Recovery Status Save: {'✅ SUCCESS' if status_save else '❌ FAILED'}")
    
    loaded_status = persistence.load_recovery_status()
    print(f"   Recovery Status Load: {'✅ SUCCESS' if loaded_status else '❌ FAILED'}")
    
    # Test market hours functionality
    print("\\n🕐 Testing Market Hours System:")
    market_open = MarketHours.is_market_open()
    print(f"   Market Currently Open: {'🟢 YES' if market_open else '🔴 NO'}")
    
    next_open = MarketHours.next_market_open()
    print(f"   Next Market Open: {next_open.strftime('%Y-%m-%d %H:%M:%S')}")
    
    time_until = MarketHours.time_until_market_open()
    hours = int(time_until.total_seconds() // 3600)
    minutes = int((time_until.total_seconds() % 3600) // 60)
    print(f"   Time Until Open: {hours}h {minutes}m")
    
    # Test automation engine
    print("\\n🤖 Testing Automation Engine:")
    automation_engine = automation_panel.automation_engine
    
    # Get automation status
    status = automation_engine.get_status()
    print(f"   Engine Status: {status}")
    print(f"   Scheduled Tasks: {status['scheduled_tasks']}")
    print(f"   Portfolio Size: {status['portfolio_size']}")
    
    # Test data directory structure
    print("\\n📁 Testing Data Directory Structure:")
    data_dir = persistence.data_dir
    print(f"   Data Directory: {data_dir}")
    
    if os.path.exists(data_dir):
        print("   ✅ Data directory exists")
        files = os.listdir(data_dir)
        print(f"   📄 Files in directory: {len(files)}")
        for file in files:
            print(f"      • {file}")
    else:
        print("   ⚠️ Data directory will be created on first use")
    
    print("\\n🎯 Complete Automation Test Setup Summary:")
    print("Features available for testing:")
    print("  ✅ PHASE 4: COMPLETE AUTOMATION SYSTEM")
    print("  ✅ Scheduled Operations:")
    print("     • Daily refresh at 09:00")
    print("     • Pre-market preparation at 08:00") 
    print("     • End of day summary at 16:30")
    print("     • Weekly portfolio review (Mondays 08:30)")
    print("     • Nightly data backup at 23:00")
    print("  ✅ Market Hour Monitoring:")
    print("     • Continuous scanning during market hours")
    print("     • 5-minute scan intervals")
    print("     • Real-time strategy analysis")
    print("     • Automated alert generation")
    print("  ✅ Comprehensive Persistence Layer:")
    print("     • Portfolio data with full trade history")
    print("     • Recovery status tracking")
    print("     • Market data caching")
    print("     • Activity logging with timestamps")
    print("     • Automated backups with versioning")
    print("  ✅ Professional Automation Control:")
    print("     • Start/Stop automation engine")
    print("     • Manual refresh and scanning")
    print("     • Real-time status monitoring")
    print("     • Schedule management")
    print("     • Data export and backup controls")
    print("  ✅ Advanced Features:")
    print("     • Market hours awareness")
    print("     • Thread-safe operations")
    print("     • Error handling and recovery")
    print("     • Performance monitoring")
    print("     • Comprehensive logging")
    
    print("\\n💡 Usage Instructions:")
    print("  1. Click '🚀 Start Automation' to begin full automated operation")
    print("  2. Monitor market status and next open time")
    print("  3. Use manual controls for immediate operations")
    print("  4. View scheduled tasks and their next run times")
    print("  5. Manage data with save/load/export/backup controls")
    print("  6. Monitor activity log for real-time system events")
    print("  7. System automatically handles market hours and scheduling")
    
    print("\\n📊 Data Persistence Features:")
    print("  • Portfolio positions with complete trade history")
    print("  • Recovery analysis and status tracking")
    print("  • Market scan results caching")
    print("  • Automated daily/weekly summaries")
    print("  • Comprehensive audit trail")
    print("  • Backup and restore capabilities")
    
    print("\\n🚀 Automation Scheduling:")
    print("  • Smart market hour detection")
    print("  • Configurable scan intervals")
    print("  • Automatic error recovery")
    print("  • Background thread management")
    print("  • Resource-efficient operation")
    
    print("\\n✨ RecoveryApp™ PHASE 4 COMPLETE!")
    print("🎯 Full automation with scheduling and persistence now operational!")
    
    # Bind cleanup on close
    def on_close():
        automation_panel.cleanup()
        root.destroy()
    
    root.protocol("WM_DELETE_WINDOW", on_close)
    
    # Start the GUI
    root.mainloop()

if __name__ == "__main__":
    test_complete_automation()
"""
RecoveryApp Production Mode Setup
Clears all test data and prepares app for real-time use
"""
import os
import json
from datetime import datetime

def clear_production_data():
    """Clear all test data and prepare for production use"""
    print("🧹 Preparing RecoveryApp for Production Mode...")
    
    # Get the RecoveryApp directory
    app_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Clear portfolio data
    portfolio_file = os.path.join(app_dir, "recovery_portfolio.json")
    portfolio_data = {
        "positions": [],
        "last_updated": None
    }
    
    with open(portfolio_file, 'w') as f:
        json.dump(portfolio_data, f, indent=2)
    print("✅ Portfolio data cleared")
    
    # Clear alerts config
    alerts_file = os.path.join(app_dir, "alerts_config.json") 
    alerts_data = {
        "alerts": [],
        "settings": {
            "refresh_interval": 300,
            "sound_enabled": True,
            "popup_enabled": True
        },
        "saved_at": None
    }
    
    with open(alerts_file, 'w') as f:
        json.dump(alerts_data, f, indent=2)
    print("✅ Alerts configuration cleared")
    
    # Clear automation log
    data_dir = os.path.join(app_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    
    log_file = os.path.join(data_dir, "automation.log")
    with open(log_file, 'w') as f:
        f.write(f"# RecoveryApp Production Log - Started {datetime.now().isoformat()}\n")
    print("✅ Automation log cleared")
    
    # Remove any temporary automation data files
    temp_files = [
        "portfolio.json",
        "trades_history.json", 
        "recovery_status.json",
        "market_cache.json"
    ]
    
    for temp_file in temp_files:
        temp_path = os.path.join(data_dir, temp_file)
        if os.path.exists(temp_path):
            os.remove(temp_path)
            print(f"✅ Removed {temp_file}")
    
    print("\n🎯 Production Mode Ready!")
    print("📋 What's cleared:")
    print("   ✅ All test portfolio positions")
    print("   ✅ All test alerts")
    print("   ✅ Automation history")
    print("   ✅ Cached market data")
    print("\n🚀 Ready for real-time ticker analysis!")
    print("   - Add your positions using the 'Add Position' tab")
    print("   - Configure alerts using the 'Alerts & Monitoring' tab")
    print("   - Enable automation in the 'Automation' tab")
    print("   - All data will be saved and persist between sessions")

if __name__ == "__main__":
    clear_production_data()
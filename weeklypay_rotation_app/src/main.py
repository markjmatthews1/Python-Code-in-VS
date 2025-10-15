"""
Main application entry point for WeeklyPay™ Rotation App
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
sys.path.append(str(Path(__file__).parent))

from config import GUI_SETTINGS, load_etf_config
from gui_interface import WeeklyPayGUI

def main():
    """Main application entry point"""
    print("Starting WeeklyPay™ Rotation App...")
    
    # Load configuration
    etf_config = load_etf_config()
    if etf_config is None:
        print("Failed to load ETF configuration. Exiting.")
        return
    
    print(f"Loaded configuration for {len(etf_config['tracked_etfs'])} ETFs")
    
    # Start GUI application
    try:
        app = WeeklyPayGUI(etf_config)
        app.run()
    except Exception as e:
        print(f"Error starting application: {e}")
        return

if __name__ == "__main__":
    main()
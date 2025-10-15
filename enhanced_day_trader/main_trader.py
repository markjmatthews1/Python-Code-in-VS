#!/usr/bin/env python3
"""
Enhanced Day Trader - Main Application
=====================================

Complete day trading system with:
- Real-time signal generation using Schwab API
- Paper trading with full trade tracking
- Beautiful colorful display with Arial 12+ fonts
- Risk management and position sizing
- Performance analytics

Author: GitHub Copilot
Date: October 15, 2025
"""

import asyncio
import logging
import threading
import time
from datetime import datetime
import sys
import os
import subprocess
import webbrowser

# Add the enhanced_day_trader directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from live_signals import trade_signal_generator
from core.paper_trader import paper_trader
from ui.trade_display import create_trade_display

# Set up logging with UTF-8 encoding
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_day_trader.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Configure console handler to use UTF-8
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

logger = logging.getLogger(__name__)

class EnhancedDayTrader:
    """
    Main application controller for the Enhanced Day Trader
    """
    
    def __init__(self):
        self.running = False
        self.signal_thread = None
        self.display_window = None
        self.web_dashboard_process = None
        self.web_dashboard_port = 8051
        
    def start_web_dashboard(self):
        """Start the web dashboard in a separate process"""
        try:
            logger.info("Starting web dashboard on port " + str(self.web_dashboard_port))
            
            # Start dashboard.py in a separate process
            dashboard_script = os.path.join(os.path.dirname(__file__), "dashboard.py")
            self.web_dashboard_process = subprocess.Popen(
                [sys.executable, dashboard_script],
                cwd=os.path.dirname(__file__),
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Give it a moment to start
            time.sleep(2)
            
            logger.info(f"Web dashboard started at http://localhost:{self.web_dashboard_port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start web dashboard: {e}")
            return False
    
    def open_web_dashboard(self):
        """Open the web dashboard in default browser"""
        try:
            url = f"http://localhost:{self.web_dashboard_port}"
            webbrowser.open(url)
            logger.info(f"Opened web dashboard: {url}")
        except Exception as e:
            logger.error(f"Failed to open web dashboard: {e}")
        
    def start_signal_monitoring(self):
        """Start the signal monitoring thread"""
        self.running = True
        self.signal_thread = threading.Thread(target=self.signal_loop, daemon=True)
        self.signal_thread.start()
        logger.info("Signal monitoring started")
    
    def signal_loop(self):
        """Main signal monitoring loop"""
        while self.running:
            try:
                # Run signal scan in async context
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                signals = loop.run_until_complete(trade_signal_generator.scan_for_signals())
                
                if signals:
                    logger.info(f"Found {len(signals)} signals")
                    for signal in signals:
                        print(trade_signal_generator.format_signal_for_display(signal))
                else:
                    logger.info("No signals found in current scan")
                
                loop.close()
                
                # Update paper trader performance
                summary = paper_trader.get_performance_summary()
                logger.info(f"Current Balance: ${summary['current_balance']:,.2f} | "
                          f"P&L: {summary['total_pnl']:+,.2f} | "
                          f"Active Trades: {summary['active_positions']}")
                
                # Wait before next scan
                time.sleep(60)  # Scan every minute
                
            except Exception as e:
                logger.error(f"Error in signal loop: {e}")
                time.sleep(30)  # Wait 30 seconds on error
    
    def start_display(self):
        """Start the colorful trade display"""
        try:
            logger.info("Starting trade display interface...")
            
            # Start web dashboard first
            web_success = self.start_web_dashboard()
            
            # Create the GUI display with web dashboard integration
            self.display_window = create_trade_display()
            
            # Add web dashboard button to the display
            if hasattr(self.display_window, 'add_web_button'):
                self.display_window.add_web_button(self.open_web_dashboard)
            
            # Start signal monitoring before showing display
            self.start_signal_monitoring()
            
            # Show the display (this will block until window is closed)
            self.display_window.show()
            
        except Exception as e:
            logger.error(f"Error starting display: {e}")
            return False
        
        return True
    
    def stop(self):
        """Stop the application"""
        logger.info("Stopping Enhanced Day Trader...")
        self.running = False
        
        if self.signal_thread and self.signal_thread.is_alive():
            self.signal_thread.join(timeout=5)
        
        # Stop web dashboard process
        if self.web_dashboard_process:
            try:
                self.web_dashboard_process.terminate()
                self.web_dashboard_process.wait(timeout=5)
                logger.info("Web dashboard stopped")
            except Exception as e:
                logger.warning(f"Error stopping web dashboard: {e}")
        
        # Save final paper trading state
        paper_trader.save_trades()
        
        logger.info("Application stopped successfully")

def print_startup_banner():
    """Print a colorful startup banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║              🚀 ENHANCED DAY TRADER v2.0 🚀                 ║
    ║                                                              ║
    ║    Real-time Signals • Paper Trading • Risk Management      ║
    ║       Schwab API • Dual Interface (GUI + Web)               ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📊 Sector ETF Watchlist: 25 securities
    🔗 Market Data: Schwab API with live quotes
    💰 Account Size: $10,000 paper trading
    ⚡ Risk Management: 0.5% per trade, 50% min signal strength
    🎨 Native GUI: Arial 12+ fonts with colorful interface
    🌐 Web Dashboard: http://localhost:8051
    
    Starting dual interface system...
    """
    print(banner)

def main():
    """Main application entry point"""
    print_startup_banner()
    
    try:
        # Initialize the application
        app = EnhancedDayTrader()
        
        # Load existing paper trading data
        paper_trader.load_trades()
        
        logger.info("Enhanced Day Trader initialized successfully")
        
        # Print current performance
        summary = paper_trader.get_performance_summary()
        print(f"\nCurrent Portfolio Status:")
        print(f"   Balance: ${summary['current_balance']:,.2f}")
        print(f"   Total P&L: {summary['total_pnl']:+,.2f} ({summary['total_return_percent']:+.1f}%)")
        print(f"   Win Rate: {summary['win_rate']:.1f}%")
        print(f"   Active Positions: {summary['active_positions']}")
        print(f"   Total Trades: {summary['total_trades']}\n")
        
        # Start the main application with display
        success = app.start_display()
        
        if not success:
            logger.error("Failed to start application")
            return 1
            
    except KeyboardInterrupt:
        logger.info("Application interrupted by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        return 1
    finally:
        if 'app' in locals():
            app.stop()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
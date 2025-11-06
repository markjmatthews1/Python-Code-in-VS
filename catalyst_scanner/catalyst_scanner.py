"""
Catalyst Scanner - Investment Catalyst Tracking Application

Main entry point for the Catalyst Scanner application that provides
real-time investment catalyst tracking with accessible GUI design.

Features:
- Morning Brief: Daily catalyst summary
- Impact Ranking: Events ranked by portfolio impact  
- Earnings Calendar: Upcoming earnings for holdings
- Opportunity Scanner: Catalyst-driven entry points
- Schwab News Feed: Real-time news with sentiment analysis
- E*TRADE Analyst Ratings: Rating changes and price targets

Author: Investment Catalyst Team
Date: September 29, 2025
Version: 1.0 (Phase 1)
"""

import tkinter as tk
import sys
import os
from tkinter import messagebox
import logging

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

try:
    from utils.logger import initialize_logging, log_startup, log_shutdown, get_logger
    from utils.error_handler import CatalystErrorHandler, get_error_handler, handle_error, ErrorContext
    from gui.main_window import CatalystScannerMainWindow
    # Try to import Phase 4 live dashboard with graceful fallback
    try:
        from gui.live_dashboard_panel import integrate_live_dashboard
    except ImportError as phase4_error:
        print(f"Phase 4 Live Dashboard not available: {phase4_error}")
        integrate_live_dashboard = None
    
except ImportError as e:
    print(f"Import error: {e}")
    print("Please ensure all required modules are available.")
    sys.exit(1)


class CatalystScannerApp:
    """Main application class for Catalyst Scanner"""
    
    def __init__(self):
        """Initialize the Catalyst Scanner application"""
        # Initialize logging first
        self.logger_manager = initialize_logging(
            log_dir="logs", 
            app_name="catalyst_scanner", 
            debug=True
        )
        self.logger = get_logger()
        
        # Initialize error handler
        self.error_handler = get_error_handler()
        
        # Initialize GUI
        self.root = None
        self.main_window = None
        self.live_dashboard = None  # Phase 4: Live Dashboard
        
        # Application state
        self.running = False
        
        self.logger.info("Catalyst Scanner application initialized")
    
    def startup(self):
        """Start the application"""
        try:
            with ErrorContext("Application startup", "Failed to start Catalyst Scanner", critical=True):
                # Log startup
                log_startup(version="1.0", phase="Phase 1 Development")
                
                # Initialize Tkinter
                self.root = tk.Tk()
                self.root.title("Catalyst Scanner v1.0 - Investment Intelligence")
                
                # Set window properties for accessibility
                self.root.geometry("1200x800")
                self.root.minsize(800, 600)
                
                # Set window icon (if available)
                try:
                    # This would set an icon if we had one
                    # self.root.iconbitmap("assets/catalyst_icon.ico")
                    pass
                except Exception:
                    pass  # Icon not critical
                
                # Create main window
                self.main_window = CatalystScannerMainWindow(self.root, self)
                
                # Initialize Phase 4 Live Dashboard (but don't show yet)
                if integrate_live_dashboard:
                    try:
                        self.live_dashboard = integrate_live_dashboard(
                            self.root, 
                            self.main_window.portfolio_loader
                        )
                        self.logger.info("Phase 4 Live Dashboard initialized successfully")
                    except Exception as e:
                        self.logger.warning(f"Phase 4 Live Dashboard initialization failed: {e}")
                        self.live_dashboard = None
                else:
                    self.logger.info("Phase 4 Live Dashboard not available")
                    self.live_dashboard = None
                
                # Set up cleanup on close
                self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
                
                # Handle keyboard shortcuts
                self.setup_keyboard_shortcuts()
                
                self.running = True
                self.logger.info("Catalyst Scanner startup complete")
                
                # Show initial status
                self.main_window.update_status("Application started - Ready for portfolio data")
                
                return True
                
        except Exception as e:
            handle_error(e, "Application startup", "Failed to initialize Catalyst Scanner", critical=True)
            return False
    
    def run(self):
        """Run the main application loop"""
        if not self.running:
            self.logger.error("Cannot run - application not properly started")
            return
        
        try:
            with ErrorContext("Main application loop", "Application error occurred"):
                self.logger.info("Starting main application loop")
                
                # Start the Tkinter main loop
                self.root.mainloop()
                
        except Exception as e:
            handle_error(e, "Main application loop", "Application error - restarting may help")
        finally:
            self.shutdown()
    
    def shutdown(self):
        """Shutdown the application cleanly"""
        try:
            self.logger.info("Shutting down Catalyst Scanner")
            
            # Cleanup Phase 4 Live Dashboard
            if self.live_dashboard:
                try:
                    self.live_dashboard.cleanup()
                    self.logger.info("Live Dashboard cleaned up successfully")
                except Exception as e:
                    self.logger.warning(f"Error cleaning up Live Dashboard: {e}")
            
            if self.main_window:
                # Save any application state here if needed
                pass
            
            self.running = False
            log_shutdown()
            
        except Exception as e:
            print(f"Error during shutdown: {e}")
    
    def on_closing(self):
        """Handle window close event"""
        try:
            # Ask for confirmation
            result = messagebox.askyesno(
                "Exit Catalyst Scanner", 
                "Are you sure you want to exit Catalyst Scanner?",
                icon='question'
            )
            
            if result:
                self.logger.info("User initiated shutdown")
                self.root.destroy()
            
        except Exception as e:
            handle_error(e, "Application close")
            self.root.destroy()
    
    def setup_keyboard_shortcuts(self):
        """Setup keyboard shortcuts"""
        try:
            # F5 - Refresh data
            self.root.bind('<F5>', lambda e: self.refresh_data())
            
            # F11 - Toggle fullscreen
            self.root.bind('<F11>', lambda e: self.toggle_fullscreen())
            
            # Ctrl+Q - Quit
            self.root.bind('<Control-q>', lambda e: self.on_closing())
            
            # Ctrl+R - Refresh
            self.root.bind('<Control-r>', lambda e: self.refresh_data())
            
            self.logger.debug("Keyboard shortcuts configured")
            
        except Exception as e:
            handle_error(e, "Keyboard shortcuts setup")
    
    def refresh_data(self):
        """Refresh application data"""
        try:
            if self.main_window:
                self.main_window.refresh_data()
        except Exception as e:
            handle_error(e, "Data refresh")
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode"""
        try:
            if self.main_window:
                self.main_window.toggle_fullscreen()
        except Exception as e:
            handle_error(e, "Fullscreen toggle")
    
    def show_live_dashboard(self):
        """Show Phase 4 Live Dashboard in new window"""
        try:
            if not self.live_dashboard:
                messagebox.showwarning(
                    "Live Dashboard Unavailable",
                    "Live Dashboard is not available. This may be due to missing dependencies or initialization errors.\n\n"
                    "Please check the logs for more details."
                )
                return
            
            # Create new window for live dashboard
            dashboard_window = tk.Toplevel(self.root)
            dashboard_window.title("Catalyst Scanner - Live Dashboard")
            dashboard_window.geometry("1400x900")
            dashboard_window.minsize(1000, 700)
            
            # Set window icon (same as main window)
            try:
                # This would set an icon if we had one
                pass
            except Exception:
                pass
            
            # Re-initialize dashboard in new window
            from gui.live_dashboard_panel import LiveDashboardPanel
            live_panel = LiveDashboardPanel(
                dashboard_window, 
                self.main_window.portfolio_loader if self.main_window else None
            )
            
            # Set up cleanup when dashboard window is closed
            def on_dashboard_close():
                try:
                    live_panel.cleanup()
                    dashboard_window.destroy()
                except Exception as e:
                    self.logger.error(f"Error closing live dashboard: {e}")
                    dashboard_window.destroy()
            
            dashboard_window.protocol("WM_DELETE_WINDOW", on_dashboard_close)
            
            self.logger.info("Live Dashboard window opened")
            
        except Exception as e:
            handle_error(e, "Live Dashboard", "Failed to open Live Dashboard")
            messagebox.showerror(
                "Error", 
                f"Failed to open Live Dashboard: {e}\n\nPlease check the logs for more details."
            )
    
    def get_status(self):
        """Get application status"""
        return {
            "running": self.running,
            "version": "1.0",
            "phase": "Phase 1 Development",
            "error_count": self.error_handler.error_count if self.error_handler else 0
        }


def main():
    """Main entry point"""
    try:
        # Print startup banner
        print("="*60)
        print("🔍 CATALYST SCANNER v1.0")
        print("Investment Catalyst Tracking Application")
        print("Phase 1 Development - September 29, 2025")
        print("="*60)
        
        # Create and start application
        app = CatalystScannerApp()
        
        if app.startup():
            print("Catalyst Scanner started successfully!")
            print("Check the logs/ directory for detailed logging.")
            app.run()
        else:
            print("Failed to start Catalyst Scanner. Check logs for details.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nCatalyst Scanner interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Fatal error starting Catalyst Scanner: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
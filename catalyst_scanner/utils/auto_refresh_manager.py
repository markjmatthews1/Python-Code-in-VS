"""
Auto Refresh Manager
Handles automatic data refresh and alert timing
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Callable, Optional
import json
import os


class AutoRefreshManager:
    """
    Manages automatic refresh cycles and timing configurations
    """
    
    def __init__(self, settings_file: str = "config/auto_refresh_settings.json"):
        """Initialize the auto refresh manager"""
        self.logger = logging.getLogger(__name__)
        self.settings_file = settings_file
        self.refresh_thread = None
        self.stop_flag = threading.Event()
        self.refresh_callbacks = []
        
        # Default settings
        self.default_settings = {
            'auto_refresh_enabled': True,
            'refresh_interval_minutes': 120,  # 2 hours default
            'market_hours_only': True,
            'weekend_refresh': False,
            'extended_hours_refresh': False,
            'last_refresh_time': None
        }
        
        # Load settings
        self.settings = self.load_settings()
        
        # Market hours (Eastern Time)
        self.market_open_hour = 9
        self.market_open_minute = 30
        self.market_close_hour = 16
        self.market_close_minute = 0
        
    def load_settings(self) -> Dict:
        """Load refresh settings from file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    return settings
            else:
                # Create default settings file
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading refresh settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict = None) -> bool:
        """Save refresh settings to file"""
        try:
            settings_to_save = settings or self.settings
            
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
            
            self.logger.info(f"Auto refresh settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving refresh settings: {e}")
            return False
    
    def update_setting(self, key: str, value) -> bool:
        """Update a specific setting"""
        try:
            if key in self.default_settings:
                self.settings[key] = value
                self.save_settings()
                
                # Restart refresh thread if interval changed
                if key == 'refresh_interval_minutes' and self.is_running():
                    self.restart_refresh_cycle()
                
                self.logger.info(f"Updated refresh setting {key} = {value}")
                return True
            else:
                self.logger.warning(f"Unknown refresh setting: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating refresh setting {key}: {e}")
            return False
    
    def get_setting(self, key: str, default=None):
        """Get a specific setting value"""
        return self.settings.get(key, default)
    
    def add_refresh_callback(self, callback: Callable):
        """Add a callback function to be called on refresh"""
        if callback not in self.refresh_callbacks:
            self.refresh_callbacks.append(callback)
            self.logger.info(f"Added refresh callback: {callback.__name__}")
    
    def remove_refresh_callback(self, callback: Callable):
        """Remove a refresh callback"""
        if callback in self.refresh_callbacks:
            self.refresh_callbacks.remove(callback)
            self.logger.info(f"Removed refresh callback: {callback.__name__}")
    
    def is_market_hours(self) -> bool:
        """Check if current time is during market hours"""
        try:
            now = datetime.now()
            
            # Check if weekend
            if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
                return False
            
            # Check if within market hours (9:30 AM - 4:00 PM ET)
            market_open = now.replace(hour=self.market_open_hour, minute=self.market_open_minute, second=0, microsecond=0)
            market_close = now.replace(hour=self.market_close_hour, minute=self.market_close_minute, second=0, microsecond=0)
            
            return market_open <= now <= market_close
            
        except Exception as e:
            self.logger.error(f"Error checking market hours: {e}")
            return True  # Default to allowing refresh
    
    def should_refresh_now(self) -> bool:
        """Determine if refresh should happen now based on settings"""
        try:
            if not self.settings.get('auto_refresh_enabled', True):
                return False
            
            # Check market hours restriction
            if self.settings.get('market_hours_only', True) and not self.is_market_hours():
                return False
            
            # Check weekend restriction
            now = datetime.now()
            if now.weekday() >= 5 and not self.settings.get('weekend_refresh', False):
                return False
            
            # Check if enough time has passed since last refresh
            last_refresh = self.settings.get('last_refresh_time')
            if last_refresh:
                try:
                    last_time = datetime.fromisoformat(last_refresh)
                    interval_minutes = self.settings.get('refresh_interval_minutes', 120)
                    next_refresh = last_time + timedelta(minutes=interval_minutes)
                    
                    if now < next_refresh:
                        return False
                except:
                    pass  # If parsing fails, allow refresh
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking refresh conditions: {e}")
            return False
    
    def execute_refresh(self):
        """Execute refresh callbacks and update last refresh time"""
        try:
            self.logger.info("Executing automatic refresh...")
            
            # Execute all refresh callbacks
            for callback in self.refresh_callbacks:
                try:
                    callback()
                    self.logger.debug(f"Executed refresh callback: {callback.__name__}")
                except Exception as e:
                    self.logger.error(f"Error in refresh callback {callback.__name__}: {e}")
            
            # Update last refresh time
            self.settings['last_refresh_time'] = datetime.now().isoformat()
            self.save_settings()
            
            self.logger.info("Automatic refresh completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error during automatic refresh: {e}")
    
    def refresh_worker(self):
        """Background worker thread for automatic refresh"""
        try:
            self.logger.info("Auto refresh worker started")
            
            while not self.stop_flag.is_set():
                try:
                    # Check every minute if refresh is needed
                    if self.should_refresh_now():
                        self.execute_refresh()
                    
                    # Wait 60 seconds before next check
                    if self.stop_flag.wait(60):  # Returns True if stop flag is set
                        break
                        
                except Exception as e:
                    self.logger.error(f"Error in refresh worker loop: {e}")
                    # Continue running even if there's an error
                    time.sleep(60)
            
            self.logger.info("Auto refresh worker stopped")
            
        except Exception as e:
            self.logger.error(f"Critical error in refresh worker: {e}")
    
    def start_auto_refresh(self):
        """Start the automatic refresh cycle"""
        try:
            if self.refresh_thread and self.refresh_thread.is_alive():
                self.logger.warning("Auto refresh already running")
                return False
            
            self.stop_flag.clear()
            self.refresh_thread = threading.Thread(target=self.refresh_worker, daemon=True)
            self.refresh_thread.start()
            
            interval_minutes = self.settings.get('refresh_interval_minutes', 120)
            self.logger.info(f"Auto refresh started with {interval_minutes} minute interval")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting auto refresh: {e}")
            return False
    
    def stop_auto_refresh(self):
        """Stop the automatic refresh cycle"""
        try:
            if self.refresh_thread and self.refresh_thread.is_alive():
                self.stop_flag.set()
                self.refresh_thread.join(timeout=5.0)
                self.logger.info("Auto refresh stopped")
                return True
            else:
                self.logger.info("Auto refresh was not running")
                return True
                
        except Exception as e:
            self.logger.error(f"Error stopping auto refresh: {e}")
            return False
    
    def restart_refresh_cycle(self):
        """Restart the refresh cycle with new settings"""
        try:
            self.stop_auto_refresh()
            time.sleep(1)  # Brief pause
            self.start_auto_refresh()
            self.logger.info("Auto refresh cycle restarted with new settings")
            
        except Exception as e:
            self.logger.error(f"Error restarting refresh cycle: {e}")
    
    def is_running(self) -> bool:
        """Check if auto refresh is currently running"""
        return self.refresh_thread and self.refresh_thread.is_alive()
    
    def get_status(self) -> Dict:
        """Get current auto refresh status"""
        try:
            last_refresh = self.settings.get('last_refresh_time')
            last_refresh_formatted = "Never"
            next_refresh_formatted = "Unknown"
            
            if last_refresh:
                try:
                    last_time = datetime.fromisoformat(last_refresh)
                    last_refresh_formatted = last_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    interval_minutes = self.settings.get('refresh_interval_minutes', 120)
                    next_time = last_time + timedelta(minutes=interval_minutes)
                    next_refresh_formatted = next_time.strftime("%Y-%m-%d %H:%M:%S")
                except:
                    pass
            
            return {
                'enabled': self.settings.get('auto_refresh_enabled', True),
                'running': self.is_running(),
                'interval_minutes': self.settings.get('refresh_interval_minutes', 120),
                'market_hours_only': self.settings.get('market_hours_only', True),
                'last_refresh': last_refresh_formatted,
                'next_refresh': next_refresh_formatted,
                'is_market_hours': self.is_market_hours()
            }
            
        except Exception as e:
            self.logger.error(f"Error getting refresh status: {e}")
            return {'error': str(e)}
    
    def manual_refresh(self):
        """Trigger a manual refresh immediately"""
        try:
            self.logger.info("Manual refresh triggered")
            self.execute_refresh()
            return True
            
        except Exception as e:
            self.logger.error(f"Error during manual refresh: {e}")
            return False


if __name__ == "__main__":
    # Test the auto refresh manager
    def test_callback():
        print(f"Refresh callback executed at {datetime.now()}")
    
    manager = AutoRefreshManager()
    manager.add_refresh_callback(test_callback)
    
    print("Auto Refresh Manager Test")
    print(f"Current settings: {manager.settings}")
    print(f"Status: {manager.get_status()}")
    print(f"Should refresh now: {manager.should_refresh_now()}")
    print(f"Is market hours: {manager.is_market_hours()}")
    
    # Test manual refresh
    print("\nTesting manual refresh...")
    manager.manual_refresh()
    
    print(f"\nUpdated status: {manager.get_status()}")
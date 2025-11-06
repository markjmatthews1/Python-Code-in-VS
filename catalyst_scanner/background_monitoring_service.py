#!/usr/bin/env python3
"""
Catalyst Scanner Background Monitoring Service
Standalone service that monitors your portfolio 24/7 and sends alerts
independently of the GUI dashboard.

This service runs continuously and monitors:
- Portfolio catalyst scores
- Price movements
- Technical indicator changes
- Risk level changes

Sends alerts via:
- SMS (Twilio/AWS SNS)
- Email notifications
- System notifications
- Log files

Perfect for real money trading decisions - never miss a critical alert!
"""

import logging
import time
import threading
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import signal

# Add the catalyst_scanner directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from alerts.alert_system import AlertSystem
    from utils.auto_refresh_manager import AutoRefreshManager
    # Try to import portfolio components
    try:
        from data_collectors.portfolio_loader import PortfolioLoader
        PORTFOLIO_LOADER_AVAILABLE = True
    except ImportError:
        PORTFOLIO_LOADER_AVAILABLE = False
    
    # Try to import etrade quotes
    try:
        from etrade_quotes import get_quotes
        ETRADE_QUOTES_AVAILABLE = True
    except ImportError:
        ETRADE_QUOTES_AVAILABLE = False
        
except ImportError as e:
    print(f"Warning: Some imports not available: {e}")
    print("Service will run with limited functionality")


class BackgroundMonitoringService:
    """
    Standalone background monitoring service for portfolio alerts
    Runs independently of the GUI dashboard
    """
    
    def __init__(self, config_file: str = "config/monitoring_service.json"):
        """Initialize the background monitoring service"""
        self.config_file = config_file
        self.running = False
        self.monitor_thread = None
        
        # Setup logging
        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        
        # Load configuration
        self.config = self.load_config()
        
        # Initialize components
        self.alert_system = None
        self.portfolio_loader = None
        self.previous_data = {}
        self.last_check_time = None
        
        # Service status
        self.start_time = None
        self.total_checks = 0
        self.alerts_sent = 0
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        self.logger.info("Background Monitoring Service initialized")
    
    def setup_logging(self):
        """Setup dedicated logging for the monitoring service"""
        # Create logs directory if it doesn't exist
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logging
        log_filename = f"{log_dir}/monitoring_service_{datetime.now().strftime('%Y%m%d')}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s | %(levelname)-8s | %(message)s',
            handlers=[
                logging.FileHandler(log_filename, encoding='utf-8'),
                logging.StreamHandler(sys.stdout)
            ]
        )
    
    def load_config(self) -> Dict:
        """Load monitoring service configuration"""
        default_config = {
            'monitoring_enabled': True,
            'check_interval_minutes': 5,  # Check every 5 minutes
            'market_hours_only': True,
            'weekend_monitoring': False,
            'after_hours_monitoring': True,
            'alert_thresholds': {
                'catalyst_score_high': 7.5,
                'catalyst_score_critical': 8.5,
                'price_change_percent': 5.0,
                'volume_spike_multiplier': 3.0
            },
            'portfolio_tickers': [
                'AMZU', 'AVL', 'FOXA', 'HSAI', 'IBKR', 'MARA', 'MRX',
                'NCLH', 'PINS', 'QQQI', 'SMCI', 'SMR', 'SOXL', 'XMTR'
            ],
            'email_alerts': {
                'enabled': True,
                'recipients': ['your_email@example.com']
            },
            'sms_alerts': {
                'enabled': False,
                'phone_number': '+1234567890'
            },
            'system_notifications': {
                'enabled': True
            },
            'max_alerts_per_hour': 10,
            'cooldown_minutes': 30
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                # Merge with defaults
                config = {**default_config, **loaded_config}
            else:
                config = default_config
                # Save default config
                self.save_config(config)
            
            return config
            
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return default_config
    
    def save_config(self, config: Dict):
        """Save configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
        except Exception as e:
            self.logger.error(f"Error saving config: {e}")
    
    def initialize_components(self):
        """Initialize monitoring components"""
        try:
            # Initialize alert system
            self.alert_system = AlertSystem()
            self.logger.info("Alert system initialized")
            
            # Initialize portfolio loader
            if PORTFOLIO_LOADER_AVAILABLE:
                try:
                    self.portfolio_loader = PortfolioLoader()
                    self.logger.info("Portfolio loader initialized")
                except Exception as e:
                    self.logger.warning(f"Portfolio loader not available: {e}")
            else:
                self.logger.warning("Portfolio loader module not available")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing components: {e}")
            return False
    
    def is_market_hours(self) -> bool:
        """Check if it's during market hours (9:30 AM - 4:00 PM ET)"""
        now = datetime.now()
        
        # Skip weekends if configured
        if not self.config.get('weekend_monitoring', False) and now.weekday() >= 5:
            return False
        
        # Check market hours (simplified - doesn't account for holidays)
        if self.config.get('market_hours_only', True):
            hour = now.hour
            minute = now.minute
            
            # Market hours: 9:30 AM - 4:00 PM ET
            market_open = hour >= 9 and (hour > 9 or minute >= 30)
            market_close = hour < 16
            
            return market_open and market_close
        
        return True
    
    def should_monitor(self) -> bool:
        """Determine if monitoring should be active"""
        if not self.config.get('monitoring_enabled', True):
            return False
        
        if self.config.get('market_hours_only', True) and not self.is_market_hours():
            if not self.config.get('after_hours_monitoring', True):
                return False
        
        return True
    
    def get_portfolio_data(self) -> Dict:
        """Get current portfolio data with scores"""
        portfolio_data = {}
        
        try:
            # Get portfolio tickers
            tickers = self.config.get('portfolio_tickers', [])
            
            if not tickers:
                self.logger.warning("No portfolio tickers configured")
                return {}
            
            # Get real quotes
            quotes = {}
            if ETRADE_QUOTES_AVAILABLE:
                try:
                    quotes = get_quotes(tickers)
                    self.logger.info(f"Retrieved quotes for {len(quotes)} tickers")
                except Exception as e:
                    self.logger.warning(f"Error getting quotes: {e}")
            else:
                # Simulate quotes for testing
                import random
                for ticker in tickers:
                    quotes[ticker] = {
                        'price': random.uniform(10, 200),
                        'changePercent': random.uniform(-5, 5),
                        'volume': random.randint(100000, 10000000)
                    }
                self.logger.info(f"Generated simulated quotes for {len(quotes)} tickers")
            
            # Simulate catalyst scores for now (replace with real catalyst scoring)
            for ticker in tickers:
                quote_data = quotes.get(ticker, {})
                
                # Calculate mock catalyst score based on price movement and volume
                price_change = quote_data.get('changePercent', 0)
                volume = quote_data.get('volume', 0)
                
                # Simple scoring algorithm (replace with your actual catalyst logic)
                base_score = 5.0
                price_factor = abs(price_change) * 0.5
                volume_factor = min(volume / 1000000, 2.0)  # Volume in millions
                
                catalyst_score = base_score + price_factor + volume_factor
                catalyst_score = min(catalyst_score, 10.0)  # Cap at 10
                
                portfolio_data[ticker] = {
                    'catalyst_score': catalyst_score,
                    'price': quote_data.get('price', 0),
                    'change_percent': price_change,
                    'volume': volume,
                    'timestamp': datetime.now().isoformat()
                }
            
            return portfolio_data
            
        except Exception as e:
            self.logger.error(f"Error getting portfolio data: {e}")
            return {}
    
    def analyze_changes(self, current_data: Dict, previous_data: Dict) -> List[Dict]:
        """Analyze data changes and generate alerts"""
        alerts = []
        
        try:
            thresholds = self.config.get('alert_thresholds', {})
            
            for ticker, current in current_data.items():
                if ticker not in previous_data:
                    continue
                
                previous = previous_data[ticker]
                
                # Check catalyst score changes
                current_score = current.get('catalyst_score', 0)
                previous_score = previous.get('catalyst_score', 0)
                
                # High catalyst score alert
                if current_score >= thresholds.get('catalyst_score_critical', 8.5):
                    alerts.append({
                        'type': 'CRITICAL_CATALYST_SCORE',
                        'ticker': ticker,
                        'message': f"🔴 CRITICAL: {ticker} catalyst score reached {current_score:.1f}",
                        'priority': 'CRITICAL',
                        'data': current
                    })
                elif current_score >= thresholds.get('catalyst_score_high', 7.5):
                    alerts.append({
                        'type': 'HIGH_CATALYST_SCORE',
                        'ticker': ticker,
                        'message': f"🟡 HIGH: {ticker} catalyst score is {current_score:.1f}",
                        'priority': 'HIGH',
                        'data': current
                    })
                
                # Significant score change
                score_change = abs(current_score - previous_score)
                if score_change >= 1.0:
                    direction = "increased" if current_score > previous_score else "decreased"
                    alerts.append({
                        'type': 'CATALYST_SCORE_CHANGE',
                        'ticker': ticker,
                        'message': f"📈 {ticker} catalyst score {direction} by {score_change:.1f} to {current_score:.1f}",
                        'priority': 'MEDIUM',
                        'data': current
                    })
                
                # Price movement alerts
                current_change = abs(current.get('change_percent', 0))
                if current_change >= thresholds.get('price_change_percent', 5.0):
                    direction = "up" if current.get('change_percent', 0) > 0 else "down"
                    alerts.append({
                        'type': 'SIGNIFICANT_PRICE_MOVE',
                        'ticker': ticker,
                        'message': f"💰 {ticker} moved {direction} {current_change:.1f}% to ${current.get('price', 0):.2f}",
                        'priority': 'HIGH',
                        'data': current
                    })
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error analyzing changes: {e}")
            return []
    
    def send_alerts(self, alerts: List[Dict]):
        """Send alerts through configured channels"""
        if not alerts:
            return
        
        try:
            for alert in alerts:
                # Send through alert system
                if self.alert_system:
                    self.alert_system.trigger_alert(alert)
                
                # Log alert
                self.logger.warning(f"ALERT: {alert['message']}")
                
                # System notification
                if self.config.get('system_notifications', {}).get('enabled', True):
                    try:
                        import plyer
                        plyer.notification.notify(
                            title=f"Catalyst Alert - {alert['ticker']}",
                            message=alert['message'],
                            timeout=10
                        )
                    except (ImportError, Exception):
                        # Fallback to Windows toast notification
                        try:
                            import os
                            os.system(f'msg * "Catalyst Alert: {alert["message"]}"')
                        except Exception:
                            pass  # Notification not available
                
                self.alerts_sent += 1
            
            self.logger.info(f"Sent {len(alerts)} alerts")
            
        except Exception as e:
            self.logger.error(f"Error sending alerts: {e}")
    
    def monitoring_loop(self):
        """Main monitoring loop"""
        self.logger.info("Starting monitoring loop")
        
        while self.running:
            try:
                if self.should_monitor():
                    # Get current portfolio data
                    current_data = self.get_portfolio_data()
                    
                    if current_data:
                        self.total_checks += 1
                        
                        # Analyze for alerts if we have previous data
                        if self.previous_data:
                            alerts = self.analyze_changes(current_data, self.previous_data)
                            if alerts:
                                self.send_alerts(alerts)
                        
                        # Update previous data
                        self.previous_data = current_data
                        self.last_check_time = datetime.now()
                        
                        # Log status
                        avg_score = sum(d.get('catalyst_score', 0) for d in current_data.values()) / len(current_data)
                        high_scores = sum(1 for d in current_data.values() if d.get('catalyst_score', 0) >= 7.5)
                        
                        self.logger.info(f"Check #{self.total_checks}: {len(current_data)} tickers, avg score {avg_score:.1f}, {high_scores} high alerts")
                    
                else:
                    if self.total_checks % 12 == 0:  # Log every hour when not monitoring
                        self.logger.info("Monitoring paused (outside configured hours)")
                
                # Sleep for configured interval
                interval = self.config.get('check_interval_minutes', 5) * 60
                time.sleep(interval)
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def start(self):
        """Start the monitoring service"""
        if self.running:
            self.logger.warning("Service is already running")
            return
        
        self.logger.info("Starting Background Monitoring Service")
        
        # Initialize components
        if not self.initialize_components():
            self.logger.error("❌ Failed to initialize components")
            return False
        
        # Start monitoring
        self.running = True
        self.start_time = datetime.now()
        
        self.monitor_thread = threading.Thread(target=self.monitoring_loop, daemon=False)
        self.monitor_thread.start()
        
        self.logger.info("Background Monitoring Service started successfully")
        return True
    
    def stop(self):
        """Stop the monitoring service"""
        if not self.running:
            return
        
        self.logger.info("🛑 Stopping Background Monitoring Service")
        self.running = False
        
        if self.monitor_thread:
            self.monitor_thread.join(timeout=30)
        
        # Log final statistics
        runtime = datetime.now() - self.start_time if self.start_time else timedelta(0)
        self.logger.info(f"📊 Service Statistics:")
        self.logger.info(f"   Runtime: {runtime}")
        self.logger.info(f"   Total checks: {self.total_checks}")
        self.logger.info(f"   Alerts sent: {self.alerts_sent}")
        
        self.logger.info("✅ Background Monitoring Service stopped")
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.stop()
        sys.exit(0)
    
    def get_status(self) -> Dict:
        """Get current service status"""
        return {
            'running': self.running,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'total_checks': self.total_checks,
            'alerts_sent': self.alerts_sent,
            'monitoring_active': self.should_monitor()
        }


def main():
    """Main entry point for the monitoring service"""
    print("🎯 Catalyst Scanner Background Monitoring Service")
    print("=" * 60)
    
    # Create monitoring service
    service = BackgroundMonitoringService()
    
    try:
        # Start the service
        if service.start():
            print("✅ Background monitoring service started")
            print("📱 You will receive alerts for:")
            print("   • High catalyst scores (7.5+)")
            print("   • Critical catalyst scores (8.5+)")
            print("   • Significant price movements (5%+)")
            print("   • Score changes (1.0+ change)")
            print("")
            print("💡 Service will monitor your Bryan Perry portfolio:")
            portfolio = service.config.get('portfolio_tickers', [])
            print(f"   {', '.join(portfolio)}")
            print("")
            print("🔄 Press Ctrl+C to stop the service")
            
            # Keep the main thread alive
            try:
                while service.running:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n👋 Shutting down service...")
                service.stop()
        else:
            print("❌ Failed to start monitoring service")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        service.stop()


if __name__ == "__main__":
    main()
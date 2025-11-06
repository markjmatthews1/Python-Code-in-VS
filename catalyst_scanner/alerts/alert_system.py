"""
Alert System
Handles visual, audio, and SMS alerts for ticker changes
"""

import logging
import threading
import time
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Callable
import tkinter as tk
from tkinter import messagebox
import winsound  # For Windows audio alerts

# Import SMS service
try:
    from alerts.sms_service import SMSService
    SMS_SERVICE_AVAILABLE = True
except ImportError:
    SMS_SERVICE_AVAILABLE = False

# Import Email service
try:
    from alerts.email_service_fixed import EmailService
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False


class AlertSystem:
    """
    Comprehensive alert system for ticker setup changes
    Handles visual popups, audio alerts, and SMS notifications
    """
    
    def __init__(self, settings_file: str = "config/alert_settings.json"):
        """Initialize the alert system"""
        self.logger = logging.getLogger(__name__)
        self.settings_file = settings_file
        
        # Alert tracking
        self.previous_states = {}
        self.active_alerts = []
        self.alert_callbacks = []
        
        # Default alert settings
        self.default_settings = {
            'visual_alerts_enabled': True,
            'audio_alerts_enabled': True,
            'sms_alerts_enabled': False,
            'popup_duration_seconds': 10,
            'audio_alert_sound': 'SystemAsterisk',  # Windows system sound
            'alert_on_rsi_extreme': True,
            'alert_on_signal_change': True,
            'alert_on_momentum_change': True,
            'alert_on_opportunity_score_change': True,
            'rsi_extreme_threshold': 25,  # Alert when RSI < 25 or > 75
            'opportunity_score_threshold': 7.0,  # Alert when score >= 7.0
            'sms_phone_number': '',
            'sms_service_enabled': False,  # Start disabled
            'sms_provider': 'mock',  # Options: twilio, aws_sns, mock
            'sms_test_mode': True,
            'sms_daily_limit': 50,
            'sms_rate_limit_minutes': 5,
            'cooldown_minutes': 30,  # Minimum time between alerts for same ticker
            # Twilio credentials
            'twilio_account_sid': '',
            'twilio_auth_token': '',
            'twilio_phone_number': '',
            # AWS SNS credentials
            'aws_access_key_id': '',
            'aws_secret_access_key': '',
            'aws_region': 'us-east-1'
        }
        
        # Load settings
        self.settings = self.load_settings()
        
        # Alert history for cooldown
        self.alert_history = {}
        
        # Initialize SMS service
        self.sms_service = None
        if SMS_SERVICE_AVAILABLE:
            try:
                self.sms_service = SMSService()
                self.logger.info("SMS service initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing SMS service: {e}")
        else:
            self.logger.warning("SMS service not available - install twilio for SMS functionality")
        
        # Initialize Email service
        self.email_service = None
        if EMAIL_SERVICE_AVAILABLE:
            try:
                self.email_service = EmailService()
                self.logger.info("Email service initialized successfully")
            except Exception as e:
                self.logger.error(f"Error initializing Email service: {e}")
        else:
            self.logger.warning("Email service not available")
        
    def load_settings(self) -> Dict:
        """Load alert settings from file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded_settings = json.load(f)
                    # Merge with defaults
                    settings = self.default_settings.copy()
                    settings.update(loaded_settings)
                    return settings
            else:
                self.save_settings(self.default_settings)
                return self.default_settings.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading alert settings: {e}")
            return self.default_settings.copy()
    
    def save_settings(self, settings: Dict = None) -> bool:
        """Save alert settings to file"""
        try:
            settings_to_save = settings or self.settings
            
            os.makedirs(os.path.dirname(self.settings_file), exist_ok=True)
            
            with open(self.settings_file, 'w') as f:
                json.dump(settings_to_save, f, indent=2)
            
            self.logger.info(f"Alert settings saved to {self.settings_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving alert settings: {e}")
            return False
    
    def update_setting(self, key: str, value) -> bool:
        """Update a specific alert setting"""
        try:
            if key in self.default_settings:
                self.settings[key] = value
                self.save_settings()
                self.logger.info(f"Updated alert setting {key} = {value}")
                return True
            else:
                self.logger.warning(f"Unknown alert setting: {key}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating alert setting {key}: {e}")
            return False
    
    def get_setting(self, key: str, default=None):
        """Get a specific alert setting"""
        return self.settings.get(key, default)
    
    def add_alert_callback(self, callback: Callable):
        """Add a callback for custom alert handling"""
        if callback not in self.alert_callbacks:
            self.alert_callbacks.append(callback)
    
    def trigger_alert(self, alert: Dict):
        """
        Public method to manually trigger an alert
        
        Args:
            alert: Dictionary containing alert information with keys:
                - ticker: Stock ticker symbol
                - type: Alert type (e.g., 'RSI_EXTREME', 'SIGNAL_CHANGE')
                - message: Alert message
                - data: Additional alert data
                - timestamp: Alert timestamp
        """
        try:
            self._process_alert(alert)
            self.logger.info(f"Alert triggered manually: {alert.get('ticker', 'Unknown')} - {alert.get('type', 'Unknown')}")
        except Exception as e:
            self.logger.error(f"Error triggering manual alert: {e}")
    
    def check_for_alerts(self, current_data: Dict):
        """
        Check current data against previous state and trigger alerts
        
        Args:
            current_data: Dictionary with ticker data
                Format: {
                    'ticker': {
                        'rsi': float,
                        'signal': str,
                        'momentum': dict,
                        'opportunity_score': float
                    }
                }
        """
        try:
            alerts_triggered = []
            
            for ticker, data in current_data.items():
                # Check if we're in cooldown for this ticker
                if self._is_in_cooldown(ticker):
                    continue
                
                # Get previous state
                prev_data = self.previous_states.get(ticker, {})
                
                # Check for RSI extreme alerts
                if self.settings.get('alert_on_rsi_extreme', True):
                    alert = self._check_rsi_extreme(ticker, data, prev_data)
                    if alert:
                        alerts_triggered.append(alert)
                
                # Check for signal changes
                if self.settings.get('alert_on_signal_change', True):
                    alert = self._check_signal_change(ticker, data, prev_data)
                    if alert:
                        alerts_triggered.append(alert)
                
                # Check for momentum changes
                if self.settings.get('alert_on_momentum_change', True):
                    alert = self._check_momentum_change(ticker, data, prev_data)
                    if alert:
                        alerts_triggered.append(alert)
                
                # Check for opportunity score changes
                if self.settings.get('alert_on_opportunity_score_change', True):
                    alert = self._check_opportunity_score(ticker, data, prev_data)
                    if alert:
                        alerts_triggered.append(alert)
            
            # Process triggered alerts
            for alert in alerts_triggered:
                self._process_alert(alert)
            
            # Update previous states
            self.previous_states = current_data.copy()
            
            return alerts_triggered
            
        except Exception as e:
            self.logger.error(f"Error checking for alerts: {e}")
            return []
    
    def _check_rsi_extreme(self, ticker: str, current: Dict, previous: Dict) -> Optional[Dict]:
        """Check for RSI extreme conditions"""
        try:
            current_rsi = self._extract_rsi(current)
            previous_rsi = self._extract_rsi(previous)
            
            if current_rsi is None:
                return None
            
            threshold = self.settings.get('rsi_extreme_threshold', 25)
            
            # Check for new extreme conditions
            if current_rsi <= threshold and (previous_rsi is None or previous_rsi > threshold):
                return {
                    'type': 'rsi_extreme_oversold',
                    'ticker': ticker,
                    'message': f'{ticker} RSI extreme oversold: {current_rsi:.1f}',
                    'priority': 'HIGH',
                    'current_value': current_rsi,
                    'previous_value': previous_rsi
                }
            
            elif current_rsi >= (100 - threshold) and (previous_rsi is None or previous_rsi < (100 - threshold)):
                return {
                    'type': 'rsi_extreme_overbought',
                    'ticker': ticker,
                    'message': f'{ticker} RSI extreme overbought: {current_rsi:.1f}',
                    'priority': 'HIGH',
                    'current_value': current_rsi,
                    'previous_value': previous_rsi
                }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error checking RSI extreme for {ticker}: {e}")
            return None
    
    def _check_signal_change(self, ticker: str, current: Dict, previous: Dict) -> Optional[Dict]:
        """Check for technical signal changes"""
        try:
            current_signal = current.get('signal', 'Neutral')
            previous_signal = previous.get('signal', 'Neutral')
            
            # Alert on significant signal changes
            significant_changes = [
                ('Neutral', 'Buy'),
                ('Neutral', 'Strong Buy'),
                ('Sell', 'Buy'),
                ('Sell', 'Strong Buy'),
                ('Buy', 'Strong Buy'),
                ('Strong Buy', 'Sell'),
                ('Buy', 'Sell')
            ]
            
            if (previous_signal, current_signal) in significant_changes:
                priority = 'HIGH' if 'Strong' in current_signal else 'MEDIUM'
                return {
                    'type': 'signal_change',
                    'ticker': ticker,
                    'message': f'{ticker} signal changed: {previous_signal} → {current_signal}',
                    'priority': priority,
                    'current_value': current_signal,
                    'previous_value': previous_signal
                }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error checking signal change for {ticker}: {e}")
            return None
    
    def _check_momentum_change(self, ticker: str, current: Dict, previous: Dict) -> Optional[Dict]:
        """Check for significant momentum changes"""
        try:
            current_momentum = current.get('momentum', {})
            previous_momentum = previous.get('momentum', {})
            
            current_5d = current_momentum.get('5_day', 0)
            previous_5d = previous_momentum.get('5_day', 0)
            
            if isinstance(current_5d, (int, float)) and isinstance(previous_5d, (int, float)):
                # Alert on significant momentum shifts (>3% change)
                momentum_change = abs(current_5d - previous_5d)
                
                if momentum_change >= 3.0:
                    direction = "increased" if current_5d > previous_5d else "decreased"
                    priority = 'HIGH' if momentum_change >= 5.0 else 'MEDIUM'
                    
                    return {
                        'type': 'momentum_change',
                        'ticker': ticker,
                        'message': f'{ticker} momentum {direction}: {previous_5d:.1f}% → {current_5d:.1f}%',
                        'priority': priority,
                        'current_value': current_5d,
                        'previous_value': previous_5d
                    }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error checking momentum change for {ticker}: {e}")
            return None
    
    def _check_opportunity_score(self, ticker: str, current: Dict, previous: Dict) -> Optional[Dict]:
        """Check for opportunity score changes"""
        try:
            current_score = current.get('opportunity_score', 0)
            previous_score = previous.get('opportunity_score', 0)
            threshold = self.settings.get('opportunity_score_threshold', 7.0)
            
            # Alert when crossing high-opportunity threshold
            if (isinstance(current_score, (int, float)) and 
                isinstance(previous_score, (int, float))):
                
                if current_score >= threshold and previous_score < threshold:
                    return {
                        'type': 'opportunity_high',
                        'ticker': ticker,
                        'message': f'{ticker} high opportunity detected: Score {current_score:.1f}/10',
                        'priority': 'HIGH',
                        'current_value': current_score,
                        'previous_value': previous_score
                    }
            
            return None
            
        except Exception as e:
            self.logger.debug(f"Error checking opportunity score for {ticker}: {e}")
            return None
    
    def _extract_rsi(self, data: Dict) -> Optional[float]:
        """Extract RSI value from data dictionary"""
        try:
            rsi_data = data.get('rsi', {})
            if isinstance(rsi_data, dict):
                return rsi_data.get('rsi')
            elif isinstance(rsi_data, (int, float)):
                return rsi_data
            return None
        except:
            return None
    
    def _is_in_cooldown(self, ticker: str) -> bool:
        """Check if ticker is in cooldown period"""
        try:
            cooldown_minutes = self.settings.get('cooldown_minutes', 30)
            last_alert_time = self.alert_history.get(ticker)
            
            if last_alert_time:
                time_diff = (datetime.now() - last_alert_time).total_seconds() / 60
                return time_diff < cooldown_minutes
            
            return False
            
        except Exception as e:
            self.logger.debug(f"Error checking cooldown for {ticker}: {e}")
            return False
    
    def _process_alert(self, alert: Dict):
        """Process and display an alert"""
        try:
            ticker = alert['ticker']
            
            # Update alert history
            self.alert_history[ticker] = datetime.now()
            
            # Add to active alerts
            alert['timestamp'] = datetime.now().isoformat()
            self.active_alerts.append(alert)
            
            # Trigger visual alert
            if self.settings.get('visual_alerts_enabled', True):
                self._show_visual_alert(alert)
            
            # Trigger audio alert
            if self.settings.get('audio_alerts_enabled', True):
                self._play_audio_alert(alert)
            
            # Trigger SMS alert
            if self.settings.get('sms_alerts_enabled', False):
                self._send_sms_alert(alert)
            
            # Trigger Email alert
            if self.email_service and self.email_service.config.get('enabled', False):
                self._send_email_alert(alert)
            
            # Call custom callbacks
            for callback in self.alert_callbacks:
                try:
                    callback(alert)
                except Exception as e:
                    self.logger.error(f"Error in alert callback: {e}")
            
            self.logger.info(f"Alert processed: {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"Error processing alert: {e}")
    
    def _show_visual_alert(self, alert: Dict):
        """Show visual popup alert"""
        try:
            # Run in separate thread to avoid blocking
            def show_popup():
                try:
                    title = f"Catalyst Alert - {alert['priority']}"
                    message = alert['message']
                    
                    # Create alert window
                    alert_window = tk.Toplevel()
                    alert_window.title(title)
                    alert_window.geometry("400x200")
                    alert_window.configure(bg='#2b2b2b')
                    
                    # Make it stay on top
                    alert_window.attributes('-topmost', True)
                    
                    # Priority color
                    color = '#ff4444' if alert['priority'] == 'HIGH' else '#ffaa00'
                    
                    # Alert content
                    tk.Label(alert_window, text=title, 
                            font=('Arial', 14, 'bold'), 
                            fg=color, bg='#2b2b2b').pack(pady=10)
                    
                    tk.Label(alert_window, text=message, 
                            font=('Arial', 12), 
                            fg='white', bg='#2b2b2b', 
                            wraplength=350).pack(pady=10)
                    
                    # Timestamp
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    tk.Label(alert_window, text=f"Time: {timestamp}", 
                            font=('Arial', 10), 
                            fg='#aaaaaa', bg='#2b2b2b').pack(pady=5)
                    
                    # Close button
                    tk.Button(alert_window, text="Acknowledge", 
                             command=alert_window.destroy,
                             bg=color, fg='white', 
                             font=('Arial', 10, 'bold')).pack(pady=10)
                    
                    # Auto-close after duration
                    duration = self.settings.get('popup_duration_seconds', 10) * 1000
                    alert_window.after(duration, alert_window.destroy)
                    
                except Exception as e:
                    self.logger.error(f"Error showing visual alert: {e}")
            
            # Run in thread
            threading.Thread(target=show_popup, daemon=True).start()
            
        except Exception as e:
            self.logger.error(f"Error creating visual alert thread: {e}")
    
    def _play_audio_alert(self, alert: Dict):
        """Play audio alert sound"""
        try:
            sound_name = self.settings.get('audio_alert_sound', 'SystemAsterisk')
            
            # Use different sounds for different priorities
            if alert['priority'] == 'HIGH':
                sound = winsound.MB_ICONEXCLAMATION
            else:
                sound = winsound.MB_ICONASTERISK
            
            # Play system sound
            winsound.MessageBeep(sound)
            
        except Exception as e:
            self.logger.error(f"Error playing audio alert: {e}")
    
    def _send_sms_alert(self, alert: Dict):
        """Send SMS alert using SMS service"""
        try:
            # Check if SMS alerts are enabled
            if not self.settings.get('sms_alerts_enabled', False):
                return
            
            # Check if SMS service is available
            if not self.sms_service:
                self.logger.warning("SMS service not available for alert")
                return
            
            phone_number = self.settings.get('sms_phone_number', '')
            if not phone_number:
                self.logger.warning("No phone number configured for SMS alerts")
                return
            
            # Create SMS message
            ticker = alert.get('ticker', 'Unknown')
            alert_type = alert.get('type', 'Alert')
            timestamp = datetime.now().strftime('%H:%M')
            
            # Format message based on alert type
            if alert_type == 'RSI_EXTREME':
                rsi_value = alert.get('data', {}).get('rsi', 'N/A')
                message = f"{ticker} RSI extreme: {rsi_value} at {timestamp}"
            elif alert_type == 'SIGNAL_CHANGE':
                old_signal = alert.get('data', {}).get('old_signal', 'N/A')
                new_signal = alert.get('data', {}).get('new_signal', 'N/A')
                message = f"{ticker} signal: {old_signal}→{new_signal} at {timestamp}"
            elif alert_type == 'MOMENTUM_CHANGE':
                momentum = alert.get('data', {}).get('momentum', 'N/A')
                message = f"{ticker} momentum change: {momentum} at {timestamp}"
            elif alert_type == 'OPPORTUNITY_SCORE':
                score = alert.get('data', {}).get('score', 'N/A')
                message = f"{ticker} opportunity score: {score} at {timestamp}"
            else:
                message = f"{ticker}: {alert.get('message', 'Alert')} at {timestamp}"
            
            # Send SMS
            result = self.sms_service.send_sms(phone_number, message, priority='normal')
            
            if result.get('success'):
                self.logger.info(f"SMS alert sent successfully: {result.get('message_id')}")
                # Store SMS result in alert for tracking
                alert['sms_result'] = result
            else:
                self.logger.error(f"Failed to send SMS alert: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error sending SMS alert: {e}")
    
    def _send_email_alert(self, alert: Dict):
        """Send email alert using email service"""
        try:
            # Check if email alerts are enabled
            if not self.settings.get('email_alerts_enabled', False):
                return
            
            # Check if email service is available
            if not self.email_service:
                self.logger.warning("Email service not available for alert")
                return
            
            recipient_email = self.settings.get('email_recipient', '')
            if not recipient_email:
                self.logger.warning("No recipient email configured for email alerts")
                return
            
            # Create email content
            ticker = alert.get('ticker', 'Unknown')
            alert_type = alert.get('type', 'Alert')
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # Format subject and message based on alert type
            if alert_type == 'RSI_EXTREME':
                rsi_value = alert.get('data', {}).get('rsi', 'N/A')
                subject = f"Catalyst Alert: {ticker} RSI Extreme"
                message = f"{ticker} RSI extreme level detected: {rsi_value}"
            elif alert_type == 'SIGNAL_CHANGE':
                old_signal = alert.get('data', {}).get('old_signal', 'N/A')
                new_signal = alert.get('data', {}).get('new_signal', 'N/A')
                subject = f"Catalyst Alert: {ticker} Signal Change"
                message = f"{ticker} signal change: {old_signal} → {new_signal}"
            elif alert_type == 'MOMENTUM_CHANGE':
                momentum = alert.get('data', {}).get('momentum', 'N/A')
                subject = f"Catalyst Alert: {ticker} Momentum Change"
                message = f"{ticker} momentum change detected: {momentum}"
            elif alert_type == 'OPPORTUNITY_SCORE':
                score = alert.get('data', {}).get('score', 'N/A')
                subject = f"Catalyst Alert: {ticker} Opportunity Score"
                message = f"{ticker} opportunity score: {score}"
            else:
                subject = f"Catalyst Alert: {ticker}"
                message = alert.get('message', 'Alert triggered')
            
            # Send email using the enhanced email service
            result = self.email_service.send_catalyst_alert(
                ticker=ticker,
                alert_type=alert_type,
                message=message,
                data=alert.get('data', {}),
                timestamp=timestamp
            )
            
            if result.get('success'):
                self.logger.info(f"Email alert sent successfully: {result.get('message_id', 'No ID')}")
                # Store email result in alert for tracking
                alert['email_result'] = result
            else:
                self.logger.error(f"Failed to send email alert: {result.get('error')}")
                
        except Exception as e:
            self.logger.error(f"Error sending email alert: {e}")
    
    def get_active_alerts(self, limit: int = 10) -> List[Dict]:
        """Get recent active alerts"""
        return self.active_alerts[-limit:] if self.active_alerts else []
    
    def clear_alerts(self):
        """Clear all active alerts"""
        self.active_alerts.clear()
        self.logger.info("All alerts cleared")
    
    def get_sms_service_status(self) -> Dict:
        """Get SMS service status and configuration"""
        if not self.sms_service:
            return {"available": False, "error": "SMS service not initialized"}
        
        try:
            status = self.sms_service.get_provider_status()
            status["phone_number"] = self.settings.get('sms_phone_number', '')
            status["sms_alerts_enabled"] = self.settings.get('sms_alerts_enabled', False)
            return status
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def test_sms_service(self) -> Dict:
        """Test SMS service connection"""
        if not self.sms_service:
            return {"success": False, "error": "SMS service not available"}
        
        try:
            return self.sms_service.test_connection()
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_email_service_status(self) -> Dict:
        """Get email service status and configuration"""
        if not self.email_service:
            return {"available": False, "error": "Email service not initialized"}
        
        try:
            status = self.email_service.get_service_status()
            status["recipient_email"] = self.settings.get('email_recipient', '')
            status["email_alerts_enabled"] = self.settings.get('email_alerts_enabled', False)
            return status
        except Exception as e:
            return {"available": False, "error": str(e)}
    
    def test_email_service(self) -> Dict:
        """Test email service connection"""
        if not self.email_service:
            return {"success": False, "error": "Email service not available"}
        
        try:
            recipient = self.settings.get('email_recipient', '')
            if not recipient:
                return {"success": False, "error": "No recipient email configured"}
            
            return self.email_service.send_test_email(recipient)
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def send_test_sms(self) -> Dict:
        """Send a test SMS message"""
        try:
            phone_number = self.settings.get('sms_phone_number', '')
            if not phone_number:
                return {"success": False, "error": "No phone number configured"}
            
            if not self.sms_service:
                return {"success": False, "error": "SMS service not available"}
            
            test_message = f"Test message from Catalyst Scanner at {datetime.now().strftime('%H:%M:%S')}"
            result = self.sms_service.send_sms(phone_number, test_message, priority='normal')
            
            if result.get('success'):
                self.logger.info("Test SMS sent successfully")
            else:
                self.logger.error(f"Test SMS failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error sending test SMS: {e}")
            return {"success": False, "error": str(e)}
    
    def update_sms_credentials(self):
        """Update SMS service with current credentials from settings"""
        try:
            if not self.sms_service:
                return False
                
            provider = self.settings.get('sms_provider', 'mock')
            
            if provider == 'twilio':
                credentials = {
                    'account_sid': self.settings.get('twilio_account_sid', ''),
                    'auth_token': self.settings.get('twilio_auth_token', ''),
                    'from_number': self.settings.get('twilio_phone_number', '')
                }
                return self.sms_service.update_credentials('twilio', credentials)
                
            elif provider == 'aws_sns':
                credentials = {
                    'access_key_id': self.settings.get('aws_access_key_id', ''),
                    'secret_access_key': self.settings.get('aws_secret_access_key', ''),
                    'region': self.settings.get('aws_region', 'us-east-1')
                }
                return self.sms_service.update_credentials('aws_sns', credentials)
                
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating SMS credentials: {e}")
            return False

    def update_email_credentials(self):
        """Update Email service with current credentials from settings"""
        if not self.email_service:
            self.logger.warning("Email service not available for credential update")
            return False
        
        try:
            # Prepare email credentials from settings
            credentials = {
                'email_provider': self.settings.get('email_provider', 'gmail'),
                'email_username': self.settings.get('email_username', ''),
                'email_password': self.settings.get('email_password', ''),
                'email_recipient': self.settings.get('email_recipient', ''),
                'email_alerts_enabled': self.settings.get('email_alerts_enabled', False)
            }
            
            # Update email service
            result = self.email_service.update_credentials(credentials)
            
            if result:
                self.logger.info("Email credentials updated successfully")
                return True
            else:
                self.logger.error("Failed to update email credentials")
                return False
                
        except Exception as e:
            self.logger.error(f"Error updating email credentials: {e}")
            return False

    def get_alert_summary(self) -> Dict:
        """Get summary of alert system status"""
        try:
            return {
                'total_alerts_today': len(self.active_alerts),
                'high_priority_alerts': len([a for a in self.active_alerts if a.get('priority') == 'HIGH']),
                'visual_enabled': self.settings.get('visual_alerts_enabled', True),
                'audio_enabled': self.settings.get('audio_alerts_enabled', True),
                'sms_enabled': self.settings.get('sms_alerts_enabled', False),
                'cooldown_minutes': self.settings.get('cooldown_minutes', 30),
                'last_alert': self.active_alerts[-1]['timestamp'] if self.active_alerts else None
            }
        except Exception as e:
            self.logger.error(f"Error getting alert summary: {e}")
            return {'error': str(e)}


if __name__ == "__main__":
    # Test the alert system
    alert_system = AlertSystem()
    
    # Test data
    test_data = {
        'SMCI': {
            'rsi': {'rsi': 22.5},
            'signal': 'Strong Buy',
            'momentum': {'5_day': 5.2},
            'opportunity_score': 8.5
        }
    }
    
    print("Alert System Test")
    print(f"Settings: {alert_system.settings}")
    
    # Check for alerts
    alerts = alert_system.check_for_alerts(test_data)
    print(f"Alerts triggered: {len(alerts)}")
    
    for alert in alerts:
        print(f"  - {alert['message']} ({alert['priority']})")
    
    print(f"Alert summary: {alert_system.get_alert_summary()}")
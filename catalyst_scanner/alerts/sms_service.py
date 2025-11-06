"""
SMS Service Module for Catalyst Scanner
Provides SMS alert functionality using multiple providers (Twilio, AWS SNS, etc.)
"""

import logging
import json
import os
from typing import Dict, Optional, List
from datetime import datetime

try:
    from twilio.rest import Client as TwilioClient
    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False

try:
    import boto3
    AWS_AVAILABLE = True
except ImportError:
    AWS_AVAILABLE = False


class SMSService:
    """
    SMS service for sending text message alerts
    Supports multiple providers: Twilio, AWS SNS, and mock testing
    """
    
    def __init__(self, config_file: str = "config/sms_config.json"):
        """Initialize SMS service"""
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        self.config = self.load_config()
        
        # Initialize providers
        self.twilio_client = None
        self.aws_sns_client = None
        self.mock_mode = False
        
        self._initialize_providers()
    
    def load_config(self) -> Dict:
        """Load SMS configuration from file"""
        try:
            # Ensure config directory exists
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                self.logger.info(f"SMS config loaded from {self.config_file}")
                return config
            else:
                # Create default config
                default_config = {
                    "provider": "mock",  # Options: twilio, aws_sns, mock
                    "enabled": True,  # Enable by default for mock testing
                    "twilio": {
                        "account_sid": "",
                        "auth_token": "",
                        "from_number": "",
                        "enabled": False
                    },
                    "aws_sns": {
                        "region": "us-east-1",
                        "access_key_id": "",
                        "secret_access_key": "",
                        "enabled": False
                    },
                    "settings": {
                        "max_daily_messages": 50,
                        "rate_limit_minutes": 5,
                        "message_prefix": "Catalyst Alert: ",
                        "test_mode": True
                    }
                }
                
                self.save_config(default_config)
                return default_config
                
        except Exception as e:
            self.logger.error(f"Error loading SMS config: {e}")
            return {}
    
    def save_config(self, config: Dict) -> bool:
        """Save SMS configuration to file"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=4)
            self.config = config
            self.logger.info(f"SMS config saved to {self.config_file}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving SMS config: {e}")
            return False
    
    def _initialize_providers(self):
        """Initialize SMS providers based on configuration"""
        try:
            provider = self.config.get('provider', 'mock').lower()
            
            if provider == 'twilio' and TWILIO_AVAILABLE:
                self._init_twilio()
            elif provider == 'aws_sns' and AWS_AVAILABLE:
                self._init_aws_sns()
            else:
                self.mock_mode = True
                self.logger.info("SMS service running in mock mode")
                
        except Exception as e:
            self.logger.error(f"Error initializing SMS providers: {e}")
            self.mock_mode = True
    
    def _init_twilio(self):
        """Initialize Twilio SMS client"""
        try:
            twilio_config = self.config.get('twilio', {})
            account_sid = twilio_config.get('account_sid')
            auth_token = twilio_config.get('auth_token')
            
            if account_sid and auth_token:
                self.twilio_client = TwilioClient(account_sid, auth_token)
                self.mock_mode = False
                self.logger.info("Twilio SMS client initialized successfully")
            else:
                self.logger.warning("Twilio credentials not configured, using mock mode")
                self.mock_mode = True
                
        except Exception as e:
            self.logger.error(f"Error initializing Twilio: {e}")
            self.mock_mode = True
    
    def _init_aws_sns(self):
        """Initialize AWS SNS client"""
        try:
            aws_config = self.config.get('aws_sns', {})
            region = aws_config.get('region', 'us-east-1')
            access_key = aws_config.get('access_key_id')
            secret_key = aws_config.get('secret_access_key')
            
            if access_key and secret_key:
                self.aws_sns_client = boto3.client(
                    'sns',
                    region_name=region,
                    aws_access_key_id=access_key,
                    aws_secret_access_key=secret_key
                )
                self.mock_mode = False
                self.logger.info("AWS SNS client initialized successfully")
            else:
                self.logger.warning("AWS SNS credentials not configured, using mock mode")
                self.mock_mode = True
                
        except Exception as e:
            self.logger.error(f"Error initializing AWS SNS: {e}")
            self.mock_mode = True
    
    def send_sms(self, phone_number: str, message: str, priority: str = "normal") -> Dict:
        """
        Send SMS message
        
        Args:
            phone_number: Recipient phone number (format: +1234567890)
            message: Message content
            priority: Message priority (low, normal, high)
            
        Returns:
            Dict with success status and details
        """
        try:
            if not self.config.get('enabled', False):
                return {"success": False, "error": "SMS service is disabled"}
            
            if not phone_number or not message:
                return {"success": False, "error": "Phone number and message are required"}
            
            # Format phone number
            formatted_number = self._format_phone_number(phone_number)
            if not formatted_number:
                return {"success": False, "error": "Invalid phone number format"}
            
            # Add message prefix
            prefix = self.config.get('settings', {}).get('message_prefix', 'Catalyst Alert: ')
            full_message = f"{prefix}{message}"
            
            # Truncate message if too long (SMS limit is 160 chars)
            if len(full_message) > 160:
                full_message = full_message[:157] + "..."
            
            # Send via configured provider
            provider = self.config.get('provider', 'mock').lower()
            
            if provider == 'twilio' and self.twilio_client:
                return self._send_via_twilio(formatted_number, full_message)
            elif provider == 'aws_sns' and self.aws_sns_client:
                return self._send_via_aws_sns(formatted_number, full_message)
            else:
                return self._send_mock(formatted_number, full_message)
                
        except Exception as e:
            self.logger.error(f"Error sending SMS: {e}")
            return {"success": False, "error": str(e)}
    
    def _send_via_twilio(self, phone_number: str, message: str) -> Dict:
        """Send SMS via Twilio"""
        try:
            twilio_config = self.config.get('twilio', {})
            from_number = twilio_config.get('from_number')
            
            if not from_number:
                return {"success": False, "error": "Twilio from_number not configured"}
            
            message_obj = self.twilio_client.messages.create(
                body=message,
                from_=from_number,
                to=phone_number
            )
            
            self.logger.info(f"SMS sent via Twilio to {phone_number}, SID: {message_obj.sid}")
            return {
                "success": True,
                "provider": "twilio",
                "message_id": message_obj.sid,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Twilio SMS error: {e}")
            return {"success": False, "error": f"Twilio error: {str(e)}"}
    
    def _send_via_aws_sns(self, phone_number: str, message: str) -> Dict:
        """Send SMS via AWS SNS"""
        try:
            response = self.aws_sns_client.publish(
                PhoneNumber=phone_number,
                Message=message
            )
            
            message_id = response.get('MessageId')
            self.logger.info(f"SMS sent via AWS SNS to {phone_number}, MessageId: {message_id}")
            return {
                "success": True,
                "provider": "aws_sns",
                "message_id": message_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"AWS SNS SMS error: {e}")
            return {"success": False, "error": f"AWS SNS error: {str(e)}"}
    
    def _send_mock(self, phone_number: str, message: str) -> Dict:
        """Send mock SMS (for testing)"""
        self.logger.info(f"MOCK SMS to {phone_number}: {message}")
        return {
            "success": True,
            "provider": "mock",
            "message_id": f"mock_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat()
        }
    
    def _format_phone_number(self, phone_number: str) -> Optional[str]:
        """Format phone number to international format"""
        try:
            # Remove all non-digit characters
            digits = ''.join(filter(str.isdigit, phone_number))
            
            # Add country code if missing (assuming US +1)
            if len(digits) == 10:
                digits = '1' + digits
            elif len(digits) == 11 and digits.startswith('1'):
                pass  # Already has country code
            else:
                return None  # Invalid length
            
            return f"+{digits}"
            
        except Exception:
            return None
    
    def test_connection(self) -> Dict:
        """Test SMS service connection"""
        try:
            provider = self.config.get('provider', 'mock').lower()
            
            if provider == 'twilio' and self.twilio_client:
                # Test Twilio connection
                account = self.twilio_client.api.accounts(self.twilio_client.username).fetch()
                return {
                    "success": True,
                    "provider": "twilio",
                    "status": account.status,
                    "message": "Twilio connection successful"
                }
            elif provider == 'aws_sns' and self.aws_sns_client:
                # Test AWS SNS connection
                response = self.aws_sns_client.list_subscriptions_by_topic(
                    TopicArn='arn:aws:sns:us-east-1:123456789012:test'  # This will fail but test auth
                )
                return {
                    "success": True,
                    "provider": "aws_sns",
                    "message": "AWS SNS connection successful"
                }
            else:
                return {
                    "success": True,
                    "provider": "mock",
                    "message": "Mock SMS service ready"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Connection test failed: {str(e)}"
            }
    
    def get_provider_status(self) -> Dict:
        """Get status of available SMS providers"""
        return {
            "twilio_available": TWILIO_AVAILABLE,
            "aws_available": AWS_AVAILABLE,
            "current_provider": self.config.get('provider', 'mock'),
            "enabled": self.config.get('enabled', False),
            "mock_mode": self.mock_mode
        }
    
    def update_credentials(self, provider: str, credentials: dict):
        """Update SMS provider credentials and reinitialize"""
        try:
            if provider == 'twilio':
                self.config['twilio'] = {
                    'account_sid': credentials.get('account_sid', ''),
                    'auth_token': credentials.get('auth_token', ''),
                    'from_number': credentials.get('from_number', ''),
                    'enabled': bool(credentials.get('account_sid') and credentials.get('auth_token'))
                }
                # Update main provider and enabled status if Twilio credentials are valid
                if credentials.get('account_sid') and credentials.get('auth_token'):
                    self.config['provider'] = 'twilio'
                    self.config['enabled'] = True
                    
            elif provider == 'aws_sns':
                self.config['aws_sns'] = {
                    'region': credentials.get('region', 'us-east-1'),
                    'access_key_id': credentials.get('access_key_id', ''),
                    'secret_access_key': credentials.get('secret_access_key', ''),
                    'enabled': bool(credentials.get('access_key_id') and credentials.get('secret_access_key'))
                }
                # Update main provider and enabled status if AWS credentials are valid
                if credentials.get('access_key_id') and credentials.get('secret_access_key'):
                    self.config['provider'] = 'aws_sns'
                    self.config['enabled'] = True
            
            # Save updated configuration
            self.save_config(self.config)
            
            # Reinitialize providers
            self._initialize_providers()
            
            self.logger.info(f"Updated {provider} credentials and reinitialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating {provider} credentials: {e}")
            return False

    def update_provider_config(self, provider: str, config: Dict) -> bool:
        """Update provider-specific configuration"""
        try:
            if provider.lower() in ['twilio', 'aws_sns']:
                self.config[provider.lower()] = config
                self.config['provider'] = provider.lower()
                self.save_config(self.config)
                self._initialize_providers()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Error updating provider config: {e}")
            return False


# Convenience function for creating SMS service instance
def create_sms_service() -> SMSService:
    """Create and return SMS service instance"""
    return SMSService()
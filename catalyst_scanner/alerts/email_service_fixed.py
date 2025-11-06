"""
Email Alert Service for Catalyst Scanner
========================================
Provides professional email notifications for catalyst events and alerts.
"""

import smtplib
import ssl
import logging
from datetime import datetime
from typing import Dict, List, Optional
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import os


class EmailService:
    """
    Professional email service for Catalyst Scanner alerts
    Supports Gmail, Outlook, Yahoo, and custom SMTP servers
    """
    
    def __init__(self, config_file: str = "config/email_config.json"):
        self.logger = logging.getLogger(__name__)
        self.config_file = config_file
        
        # Default email settings
        self.default_config = {
            'enabled': False,
            'provider': 'gmail',  # gmail, outlook, yahoo, custom
            'smtp_server': '',
            'smtp_port': 587,
            'use_tls': True,
            'sender_email': '',
            'sender_password': '',  # App password for Gmail
            'sender_name': 'Catalyst Scanner',
            'recipient_email': '',
            'subject_prefix': '[Catalyst Alert]',
            'daily_limit': 100,
            'rate_limit_minutes': 2,
            'test_mode': True,  # Start in test mode
            'html_emails': True
        }
        
        # Provider-specific SMTP settings
        self.smtp_providers = {
            'gmail': {
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'use_tls': True
            },
            'outlook': {
                'smtp_server': 'smtp-mail.outlook.com', 
                'smtp_port': 587,
                'use_tls': True
            },
            'yahoo': {
                'smtp_server': 'smtp.mail.yahoo.com',
                'smtp_port': 587,
                'use_tls': True
            }
        }
        
        # Load configuration
        self.config = self.load_config()
        
        # Rate limiting
        self.last_email_time = {}
        self.daily_email_count = 0
        self.daily_reset_date = datetime.now().date()
        self.last_sent_time = None
        
    def load_config(self) -> Dict:
        """Load email configuration"""
        try:
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    loaded_config = json.load(f)
                    config = self.default_config.copy()
                    config.update(loaded_config)
                    
                    # Auto-configure SMTP settings based on provider
                    if config['provider'] in self.smtp_providers:
                        provider_settings = self.smtp_providers[config['provider']]
                        config.update(provider_settings)
                    
                    return config
            else:
                # Create default config file
                self.save_config(self.default_config)
                return self.default_config.copy()
                
        except Exception as e:
            self.logger.error(f"Error loading email config: {e}")
            return self.default_config.copy()
    
    def save_config(self, config: Dict = None):
        """Save email configuration"""
        try:
            config_to_save = config or self.config
            os.makedirs(os.path.dirname(self.config_file), exist_ok=True)
            
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Error saving email config: {e}")
    
    def update_credentials(self, credentials: Dict) -> bool:
        """Update email credentials and configuration"""
        try:
            # Update configuration with new credentials
            if 'email_provider' in credentials:
                self.config['provider'] = credentials['email_provider']
            if 'email_username' in credentials:
                self.config['sender_email'] = credentials['email_username']
            if 'email_password' in credentials:
                self.config['sender_password'] = credentials['email_password']
            if 'email_recipient' in credentials:
                self.config['recipient_email'] = credentials['email_recipient']
            if 'email_alerts_enabled' in credentials:
                self.config['enabled'] = credentials['email_alerts_enabled']
            
            # Auto-configure SMTP settings based on provider
            if self.config['provider'] in self.smtp_providers:
                provider_settings = self.smtp_providers[self.config['provider']]
                self.config.update(provider_settings)
            
            # Save updated configuration
            self.save_config()
            
            self.logger.info(f"Email credentials updated for provider: {self.config['provider']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating email credentials: {e}")
            return False
    
    def test_connection(self) -> tuple:
        """Test email server connection"""
        try:
            if not self.config['enabled']:
                return False, "Email service is disabled"
            
            if not self.config['sender_email'] or not self.config['sender_password']:
                return False, "Email credentials not configured"
            
            # Create SMTP connection
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            
            if self.config['use_tls']:
                context = ssl.create_default_context()
                server.starttls(context=context)
            
            # Login
            server.login(self.config['sender_email'], self.config['sender_password'])
            server.quit()
            
            self.logger.info("Email connection test successful")
            return True, "Connection successful"
            
        except Exception as e:
            error_msg = f"Email connection failed: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def send_catalyst_alert(self, 
                          ticker: str, 
                          catalyst_type: str,
                          impact_score: float,
                          details: Dict,
                          urgency: str = "normal") -> bool:
        """Send a catalyst alert email"""
        
        if not self._should_send_email(f"catalyst_{ticker}_{catalyst_type}"):
            return False
        
        # Create email content
        subject = self._create_catalyst_subject(ticker, catalyst_type, impact_score, urgency)
        body_html, body_text = self._create_catalyst_body(ticker, catalyst_type, impact_score, details, urgency)
        
        return self._send_email(subject, body_html, body_text)
    
    def send_test_email(self, recipient: str = None) -> Dict:
        """Send a test email to verify configuration
        
        Args:
            recipient: Optional recipient email address. If not provided, uses configured recipient.
            
        Returns:
            Dict with success status and message/error details
        """
        
        try:
            if recipient:
                # Temporarily override recipient for test
                original_recipient = self.config.get('recipient')
                self.config['recipient'] = recipient
            
            subject = f"{self.config['subject_prefix']} Test Email"
            
            body_html = f"""
            <html>
            <body>
                <h2>🧪 Catalyst Scanner Test Email</h2>
                <p>This is a test email from your Catalyst Scanner application.</p>
                <p><strong>Sent:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Provider:</strong> {self.config['provider']}</p>
                <p><strong>SMTP Server:</strong> {self.config['smtp_server']}:{self.config['smtp_port']}</p>
                <p>If you received this email, your email alerts are working correctly!</p>
                <hr>
                <p><small>Catalyst Scanner - Investment Intelligence System</small></p>
            </body>
            </html>
            """
            
            body_text = f"""
CATALYST SCANNER TEST EMAIL

This is a test email from your Catalyst Scanner application.

Sent: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Provider: {self.config['provider']}
SMTP Server: {self.config['smtp_server']}:{self.config['smtp_port']}

If you received this email, your email alerts are working correctly!

Catalyst Scanner - Investment Intelligence System
            """
            
            result = self._send_email(subject, body_html, body_text)
            
            if recipient and 'original_recipient' in locals():
                # Restore original recipient
                if original_recipient:
                    self.config['recipient'] = original_recipient
                else:
                    self.config.pop('recipient', None)
            
            if result:
                return {"success": True, "message": "Test email sent successfully"}
            else:
                return {"success": False, "error": "Failed to send test email"}
                
        except Exception as e:
            self.logger.error(f"Error sending test email: {e}")
            return {"success": False, "error": str(e)}
    
    def get_service_status(self) -> Dict:
        """Get the current status of the email service
        
        Returns:
            Dict with service status information
        """
        try:
            status = {
                "available": True,
                "provider": self.config.get('provider', 'unknown'),
                "smtp_server": self.config.get('smtp_server', 'unknown'),
                "smtp_port": self.config.get('smtp_port', 'unknown'),
                "enabled": self.config.get('enabled', False),
                "recipient": self.config.get('recipient', ''),
                "daily_sent": self.daily_email_count,
                "daily_limit": self.config.get('daily_limit', 50),
                "last_sent": self.last_sent_time.strftime('%Y-%m-%d %H:%M:%S') if self.last_sent_time else 'Never',
                "test_mode": self.config.get('test_mode', False)
            }
            
            # Check if configuration is valid
            required_fields = ['username', 'password', 'recipient']
            missing_fields = [field for field in required_fields if not self.config.get(field)]
            
            if missing_fields:
                status["configuration_warning"] = f"Missing required fields: {', '.join(missing_fields)}"
            
            return status
            
        except Exception as e:
            self.logger.error(f"Error getting service status: {e}")
            return {
                "available": False,
                "error": str(e)
            }
    
    def _should_send_email(self, alert_type: str) -> bool:
        """Check if email should be sent based on rate limits"""
        
        if not self.config['enabled']:
            return False
        
        # Check daily limit
        current_date = datetime.now().date()
        if current_date != self.daily_reset_date:
            self.daily_email_count = 0
            self.daily_reset_date = current_date
        
        if self.daily_email_count >= self.config['daily_limit']:
            self.logger.warning("Daily email limit reached")
            return False
        
        # Check rate limit
        now = datetime.now()
        last_time = self.last_email_time.get(alert_type)
        
        if last_time:
            time_diff = (now - last_time).total_seconds() / 60  # minutes
            if time_diff < self.config['rate_limit_minutes']:
                self.logger.debug(f"Rate limit active for {alert_type}")
                return False
        
        return True
    
    def _create_catalyst_subject(self, ticker: str, catalyst_type: str, impact_score: float, urgency: str) -> str:
        """Create catalyst alert email subject"""
        
        urgency_prefix = {
            'low': '📊',
            'normal': '⚠️',
            'high': '🚨',
            'critical': '🔴'
        }.get(urgency, '⚠️')
        
        return f"{self.config['subject_prefix']} {urgency_prefix} {ticker} {catalyst_type.title()} Alert (Impact: {impact_score:.1f}/10)"
    
    def _create_catalyst_body(self, ticker: str, catalyst_type: str, impact_score: float, details: Dict, urgency: str) -> tuple:
        """Create catalyst alert email body (HTML and text versions)"""
        
        # Impact color coding
        if impact_score >= 8:
            impact_color = "#dc3545"  # Red
            impact_level = "HIGH IMPACT"
        elif impact_score >= 6:
            impact_color = "#fd7e14"  # Orange
            impact_level = "MEDIUM IMPACT"
        elif impact_score >= 4:
            impact_color = "#ffc107"  # Yellow
            impact_level = "LOW-MEDIUM IMPACT"
        else:
            impact_color = "#28a745"  # Green
            impact_level = "LOW IMPACT"
        
        # Create HTML version
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .alert-box {{ background-color: {impact_color}; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>🎯 Catalyst Scanner Alert</h1>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
            
            <div class="alert-box">
                <h2>{ticker} - {catalyst_type.title()} Alert</h2>
                <p><strong>Impact Level:</strong> {impact_level} ({impact_score:.1f}/10)</p>
                <p><strong>Urgency:</strong> {urgency.upper()}</p>
            </div>
            
            <div class="details">
                <h3>📋 Catalyst Details</h3>
                <p><strong>Event:</strong> {details.get('event', 'Not specified')}</p>
                <p><strong>Description:</strong> {details.get('description', 'No details available')}</p>
                <p><strong>Expected Date:</strong> {details.get('date', 'TBD')}</p>
                <p><strong>Source:</strong> {details.get('source', 'Internal Analysis')}</p>
            </div>
            
            <div class="footer">
                <p><strong>📱 Next Steps:</strong></p>
                <ul>
                    <li>Review your position in {ticker}</li>
                    <li>Consider the catalyst timing and your investment strategy</li>
                    <li>Monitor for additional developments</li>
                    <li>Check technical analysis for entry/exit signals</li>
                </ul>
                
                <hr>
                <p><small>This alert was generated by Catalyst Scanner - Your Investment Intelligence System</small></p>
            </div>
        </body>
        </html>
        """
        
        # Create text version
        body_text = f"""
CATALYST SCANNER ALERT
======================

{ticker} - {catalyst_type.title()} Alert
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Impact Level: {impact_level} ({impact_score:.1f}/10)
Urgency: {urgency.upper()}

CATALYST DETAILS:
================
Event: {details.get('event', 'Not specified')}
Description: {details.get('description', 'No details available')}
Expected Date: {details.get('date', 'TBD')}
Source: {details.get('source', 'Internal Analysis')}

NEXT STEPS:
===========
• Review your position in {ticker}
• Consider the catalyst timing and your investment strategy  
• Monitor for additional developments
• Check technical analysis for entry/exit signals

---
This alert was generated by Catalyst Scanner - Your Investment Intelligence System
        """
        
        return body_html, body_text
    
    def _send_email(self, subject: str, body_html: str, body_text: str) -> bool:
        """Send email with both HTML and text versions"""
        
        try:
            if self.config['test_mode']:
                self.logger.info(f"TEST MODE: Would send email with subject: {subject}")
                print(f"📧 TEST MODE EMAIL: {subject}")
                print(f"📧 To: {self.config['recipient_email']}")
                print(f"📧 Body preview: {body_text[:200]}...")
                return True
            
            # Validate configuration
            if not self.config['recipient_email']:
                self.logger.error("No recipient email configured")
                return False
            
            # Create message
            msg = MIMEMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = subject
            
            # Create text and HTML parts
            part1 = MIMEText(body_text, 'plain')
            part2 = MIMEText(body_html, 'html')
            
            # Add parts to message
            msg.attach(part1)
            if self.config['html_emails']:
                msg.attach(part2)
            
            # Create SMTP connection and send
            server = smtplib.SMTP(self.config['smtp_server'], self.config['smtp_port'])
            
            if self.config['use_tls']:
                context = ssl.create_default_context()
                server.starttls(context=context)
            
            server.login(self.config['sender_email'], self.config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(self.config['sender_email'], self.config['recipient_email'], text)
            server.quit()
            
            # Update tracking
            self.daily_email_count += 1
            alert_type = "general"
            if "catalyst" in subject.lower():
                alert_type = "catalyst"
            elif "summary" in subject.lower():
                alert_type = "summary"
            
            self.last_email_time[alert_type] = datetime.now()
            
            self.logger.info(f"Email sent successfully: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False
    
    def get_setup_instructions(self) -> Dict[str, str]:
        """Get setup instructions for different email providers"""
        
        return {
            'gmail': """
Gmail Setup Instructions:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
   - Use this password, not your regular Gmail password
3. Use your full Gmail address as sender_email
4. Use the generated app password as sender_password
            """,
            
            'outlook': """
Outlook/Hotmail Setup Instructions:
1. Enable 2-factor authentication (recommended)
2. Use your full email address as sender_email
3. Use your regular password or app password
4. If using 2FA, generate an app password in security settings
            """,
            
            'yahoo': """
Yahoo Setup Instructions:
1. Enable 2-factor authentication
2. Generate an App Password:
   - Go to Account Security
   - Generate and manage app passwords
   - Create password for "Mail"
3. Use your full Yahoo email as sender_email
4. Use the generated app password as sender_password
            """
        }


# Test the email service
if __name__ == "__main__":
    print("🧪 Testing Email Service...")
    
    # Initialize email service
    email_service = EmailService()
    
    # Print current config
    print(f"📧 Email enabled: {email_service.config['enabled']}")
    print(f"📧 Test mode: {email_service.config['test_mode']}")
    print(f"📧 Provider: {email_service.config['provider']}")
    
    # Test connection if enabled
    if email_service.config['enabled']:
        success, message = email_service.test_connection()
        print(f"🔗 Connection test: {success} - {message}")
        
        if success:
            # Send test email
            test_result = email_service.send_test_email()
            print(f"📧 Test email sent: {test_result}")
    else:
        print("📧 Email service disabled - configure in email_config.json to test")
        
        # Show sample catalyst alert in test mode
        sample_details = {
            'event': 'Earnings Release',
            'description': 'Q3 2025 earnings after market close',
            'date': '2025-10-15',
            'source': 'Yahoo Finance'
        }
        
        result = email_service.send_catalyst_alert(
            ticker="AAPL",
            catalyst_type="earnings",
            impact_score=8.5,
            details=sample_details,
            urgency="high"
        )
        print(f"📧 Sample catalyst alert: {result}")
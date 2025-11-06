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
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
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
            'test_mode': False,
            'html_emails': True,
            'include_logo': False
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
        
    def load_config(self) -> Dict:
        """Load email configuration"""
        try:
            # Ensure config directory exists
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
    
    def test_connection(self) -> bool:
        """Test email server connection"""
        try:
            if not self.config['enabled']:
                return False, "Email service is disabled"
            
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
        """
        Send a catalyst alert email
        
        Args:
            ticker: Stock ticker symbol
            catalyst_type: Type of catalyst (earnings, news, technical, etc.)
            impact_score: Impact score 1-10
            details: Additional catalyst details
            urgency: Alert urgency (low, normal, high, critical)
        """
        
        if not self._should_send_email(f"catalyst_{ticker}_{catalyst_type}"):
            return False
        
        # Create email content
        subject = self._create_catalyst_subject(ticker, catalyst_type, impact_score, urgency)
        body_html, body_text = self._create_catalyst_body(ticker, catalyst_type, impact_score, details, urgency)
        
        return self._send_email(subject, body_html, body_text)
    
    def send_portfolio_summary(self, 
                             portfolio_alerts: List[Dict],
                             market_status: Dict,
                             next_catalysts: List[Dict]) -> bool:
        """Send daily portfolio summary email"""
        
        if not self._should_send_email("daily_summary"):
            return False
        
        subject = f"{self.config['subject_prefix']} Daily Portfolio Summary - {datetime.now().strftime('%Y-%m-%d')}"
        body_html, body_text = self._create_summary_body(portfolio_alerts, market_status, next_catalysts)
        
        return self._send_email(subject, body_html, body_text)
    
    def send_test_email(self) -> bool:
        """Send a test email to verify configuration"""
        
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
        
        return self._send_email(subject, body_html, body_text)
    
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
        
        # HTML version
        body_html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; }}
                .alert-box {{ background-color: {impact_color}; color: white; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                .details {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }}
                table {{ width: 100%; border-collapse: collapse; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #f2f2f2; }}
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
                <table>
        """
        
        # Add details to HTML table
        for key, value in details.items():
            if value:  # Only show non-empty values
                body_html += f"<tr><th>{key.replace('_', ' ').title()}</th><td>{value}</td></tr>"
        
        body_html += \"\"\"
                </table>
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
                <p><small>To modify alert settings, open the Catalyst Scanner application and go to Settings → Email Alerts</small></p>
            </div>
        </body>
        </html>
        \"\"\"
        
        # Text version
        body_text = f\"\"\"
CATALYST SCANNER ALERT
======================

{ticker} - {catalyst_type.title()} Alert
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Impact Level: {impact_level} ({impact_score:.1f}/10)
Urgency: {urgency.upper()}

CATALYST DETAILS:
================
\"\"\"
        
        # Add details to text version
        for key, value in details.items():
            if value:
                body_text += f"{key.replace('_', ' ').title()}: {value}\\n"
        
        body_text += f\"\"\"

NEXT STEPS:
===========
• Review your position in {ticker}
• Consider the catalyst timing and your investment strategy  
• Monitor for additional developments
• Check technical analysis for entry/exit signals

---
This alert was generated by Catalyst Scanner - Your Investment Intelligence System
To modify alert settings, open the Catalyst Scanner application and go to Settings → Email Alerts
\"\"\"
        
        return body_html, body_text
    
    def _create_summary_body(self, portfolio_alerts: List[Dict], market_status: Dict, next_catalysts: List[Dict]) -> tuple:
        """Create daily summary email body"""
        
        # HTML version with comprehensive styling
        body_html = f\"\"\"
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; border-radius: 5px; }}
                .section {{ margin: 20px 0; padding: 15px; border-radius: 5px; background-color: #f8f9fa; }}
                .alert-high {{ background-color: #dc3545; color: white; padding: 10px; border-radius: 3px; }}
                .alert-medium {{ background-color: #fd7e14; color: white; padding: 10px; border-radius: 3px; }}
                .alert-low {{ background-color: #ffc107; color: black; padding: 10px; border-radius: 3px; }}
                table {{ width: 100%; border-collapse: collapse; margin: 10px 0; }}
                th, td {{ padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }}
                th {{ background-color: #e9ecef; }}
                .footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ccc; color: #666; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>📊 Daily Portfolio Summary</h1>
                <p>{datetime.now().strftime('%A, %B %d, %Y')}</p>
            </div>
            
            <div class="section">
                <h2>📈 Market Status</h2>
                <p><strong>Market State:</strong> {market_status.get('state', 'Unknown')}</p>
                <p><strong>VIX Level:</strong> {market_status.get('vix', 'N/A')}</p>
                <p><strong>Market Sentiment:</strong> {market_status.get('sentiment', 'Neutral')}</p>
            </div>
            
            <div class="section">
                <h2>🚨 Active Portfolio Alerts ({len(portfolio_alerts)})</h2>
        \"\"\"
        
        if portfolio_alerts:
            body_html += "<table><tr><th>Ticker</th><th>Alert Type</th><th>Impact</th><th>Details</th></tr>"
            for alert in portfolio_alerts[:10]:  # Limit to top 10
                impact_class = "alert-high" if alert.get('impact_score', 0) >= 7 else "alert-medium" if alert.get('impact_score', 0) >= 5 else "alert-low"
                body_html += f\"\"\"
                <tr>
                    <td><strong>{alert.get('ticker', 'N/A')}</strong></td>
                    <td>{alert.get('type', 'N/A')}</td>
                    <td><span class="{impact_class}">{alert.get('impact_score', 0):.1f}/10</span></td>
                    <td>{alert.get('summary', 'No details')}</td>
                </tr>
                \"\"\"
            body_html += "</table>"
        else:
            body_html += "<p>No active alerts for your portfolio holdings.</p>"
        
        body_html += \"\"\"
            </div>
            
            <div class="section">
                <h2>📅 Upcoming Catalysts (Next 7 Days)</h2>
        \"\"\"
        
        if next_catalysts:
            body_html += "<table><tr><th>Date</th><th>Ticker</th><th>Event</th><th>Expected Impact</th></tr>"
            for catalyst in next_catalysts[:15]:  # Limit to next 15
                body_html += f\"\"\"
                <tr>
                    <td>{catalyst.get('date', 'TBD')}</td>
                    <td><strong>{catalyst.get('ticker', 'N/A')}</strong></td>
                    <td>{catalyst.get('event', 'N/A')}</td>
                    <td>{catalyst.get('expected_impact', 'Unknown')}</td>
                </tr>
                \"\"\"
            body_html += "</table>"
        else:
            body_html += "<p>No upcoming catalysts detected for your portfolio.</p>"
        
        body_html += \"\"\"
            </div>
            
            <div class="footer">
                <p><strong>📱 Action Items:</strong></p>
                <ul>
                    <li>Review high-impact alerts and consider position adjustments</li>
                    <li>Prepare for upcoming catalyst events</li>
                    <li>Monitor technical analysis for optimal entry/exit timing</li>
                </ul>
                
                <hr>
                <p><small>Generated by Catalyst Scanner at {datetime.now().strftime('%H:%M:%S')}</small></p>
            </div>
        </body>
        </html>
        \"\"\"
        
        # Text version
        body_text = f\"\"\"
DAILY PORTFOLIO SUMMARY
=======================
{datetime.now().strftime('%A, %B %d, %Y')}

MARKET STATUS:
=============
Market State: {market_status.get('state', 'Unknown')}
VIX Level: {market_status.get('vix', 'N/A')}
Market Sentiment: {market_status.get('sentiment', 'Neutral')}

ACTIVE PORTFOLIO ALERTS ({len(portfolio_alerts)}):
===============================================
\"\"\"
        
        if portfolio_alerts:
            for alert in portfolio_alerts[:10]:
                body_text += f"• {alert.get('ticker', 'N/A')} - {alert.get('type', 'N/A')} (Impact: {alert.get('impact_score', 0):.1f}/10)\\n"
                body_text += f"  {alert.get('summary', 'No details')}\\n\\n"
        else:
            body_text += "No active alerts for your portfolio holdings.\\n"
        
        body_text += f\"\"\"
UPCOMING CATALYSTS (Next 7 Days):
=================================
\"\"\"
        
        if next_catalysts:
            for catalyst in next_catalysts[:15]:
                body_text += f"• {catalyst.get('date', 'TBD')} - {catalyst.get('ticker', 'N/A')}: {catalyst.get('event', 'N/A')}\\n"
        else:
            body_text += "No upcoming catalysts detected for your portfolio.\\n"
        
        body_text += f\"\"\"

ACTION ITEMS:
============
• Review high-impact alerts and consider position adjustments
• Prepare for upcoming catalyst events  
• Monitor technical analysis for optimal entry/exit timing

---
Generated by Catalyst Scanner at {datetime.now().strftime('%H:%M:%S')}
\"\"\"
        
        return body_html, body_text
    
    def _send_email(self, subject: str, body_html: str, body_text: str) -> bool:
        """Send email with both HTML and text versions"""
        
        try:
            if self.config['test_mode']:
                self.logger.info(f"TEST MODE: Would send email with subject: {subject}")
                return True
            
            # Create message
            msg = MimeMultipart('alternative')
            msg['From'] = f"{self.config['sender_name']} <{self.config['sender_email']}>"
            msg['To'] = self.config['recipient_email']
            msg['Subject'] = subject
            
            # Create text and HTML parts
            part1 = MimeText(body_text, 'plain')
            part2 = MimeText(body_html, 'html')
            
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
            'gmail': \"\"\"
Gmail Setup Instructions:
1. Enable 2-factor authentication on your Google account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → App passwords
   - Generate password for "Mail"
   - Use this password, not your regular Gmail password
3. Use your full Gmail address as sender_email
4. Use the generated app password as sender_password
            \"\"\",
            
            'outlook': \"\"\"
Outlook/Hotmail Setup Instructions:
1. Enable 2-factor authentication (recommended)
2. Use your full email address as sender_email
3. Use your regular password or app password
4. If using 2FA, generate an app password in security settings
            \"\"\",
            
            'yahoo': \"\"\"
Yahoo Setup Instructions:
1. Enable 2-factor authentication
2. Generate an App Password:
   - Go to Account Security
   - Generate and manage app passwords
   - Create password for "Mail"
3. Use your full Yahoo email as sender_email
4. Use the generated app password as sender_password
            \"\"\"
        }


# Example usage and testing
if __name__ == "__main__":
    # Initialize email service
    email_service = EmailService()
    
    # Test connection
    success, message = email_service.test_connection()
    print(f"Connection test: {success} - {message}")
    
    # Send test email
    if success:
        test_result = email_service.send_test_email()
        print(f"Test email sent: {test_result}")
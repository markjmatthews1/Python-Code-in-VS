#!/usr/bin/env python3
"""
Status checker for the Background Monitoring Service
Quick tool to test components and configuration
"""

import sys
import os
import json
from datetime import datetime

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def check_service_status():
    """Check service components and configuration"""
    print("Background Monitoring Service Status Check")
    print("=" * 60)
    
    # Check configuration
    config_file = "config/monitoring_service.json"
    if os.path.exists(config_file):
        print("✅ Configuration file found")
        try:
            with open(config_file, 'r') as f:
                config = json.load(f)
            print(f"   • Monitoring enabled: {config.get('monitoring_enabled', False)}")
            print(f"   • Check interval: {config.get('check_interval_minutes', 5)} minutes")
            print(f"   • Portfolio tickers: {len(config.get('portfolio_tickers', []))}")
        except Exception as e:
            print(f"❌ Error reading config: {e}")
    else:
        print("⚠️ Configuration file not found")
    
    print("")
    
    # Check imports
    print("Component Availability:")
    
    # Alert system
    try:
        from alerts.alert_system import AlertSystem
        print("✅ Alert system available")
    except ImportError as e:
        print(f"❌ Alert system not available: {e}")
    
    # Auto refresh manager
    try:
        from utils.auto_refresh_manager import AutoRefreshManager
        print("✅ Auto refresh manager available")
    except ImportError as e:
        print(f"❌ Auto refresh manager not available: {e}")
    
    # E*TRADE quotes
    try:
        from etrade_quotes import get_quotes
        print("✅ E*TRADE quotes available")
    except ImportError:
        print("⚠️ E*TRADE quotes not available (will use simulated data)")
    
    # Portfolio loader
    try:
        from data_collectors.portfolio_loader import PortfolioLoader
        print("✅ Portfolio loader available")
    except ImportError:
        print("⚠️ Portfolio loader not available")
    
    # System notifications
    try:
        import plyer
        print("✅ System notifications (plyer) available")
    except ImportError:
        print("⚠️ System notifications not available (will use fallback)")
    
    print("")
    
    # Test service creation
    print("Testing Service Creation:")
    try:
        from background_monitoring_service import BackgroundMonitoringService
        service = BackgroundMonitoringService()
        print("✅ Background monitoring service created successfully")
        
        # Test component initialization
        if service.initialize_components():
            print("✅ Service components initialized")
        else:
            print("⚠️ Some service components failed to initialize")
        
        # Show configuration
        print(f"\nCurrent Configuration:")
        print(f"   • Portfolio: {', '.join(service.config.get('portfolio_tickers', []))}")
        print(f"   • Check interval: {service.config.get('check_interval_minutes')} minutes")
        print(f"   • Market hours only: {service.config.get('market_hours_only')}")
        print(f"   • Email alerts: {service.config.get('email_alerts', {}).get('enabled', False)}")
        print(f"   • SMS alerts: {service.config.get('sms_alerts', {}).get('enabled', False)}")
        
    except Exception as e:
        print(f"❌ Error creating service: {e}")
        import traceback
        traceback.print_exc()
    
    print("")
    print("Service Status: Ready to run")
    print("To start monitoring: python start_monitoring.py")

if __name__ == "__main__":
    check_service_status()
#!/usr/bin/env python3
"""
Quick launcher for the Background Monitoring Service
Runs the service with proper error handling and logging
"""

import sys
import os
import time

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

try:
    from background_monitoring_service import BackgroundMonitoringService
    
    print("🎯 Catalyst Scanner Background Monitoring Launcher")
    print("=" * 60)
    
    # Create and start service
    service = BackgroundMonitoringService()
    
    print("📋 Service Configuration:")
    print(f"   • Check interval: {service.config.get('check_interval_minutes', 5)} minutes")
    print(f"   • Portfolio tickers: {len(service.config.get('portfolio_tickers', []))} tickers")
    print(f"   • Market hours only: {service.config.get('market_hours_only', True)}")
    print(f"   • Weekend monitoring: {service.config.get('weekend_monitoring', False)}")
    print("")
    
    # Start monitoring
    if service.start():
        print("✅ Background monitoring service started successfully!")
        print("")
        print("🔔 Alert Types:")
        print("   • High catalyst scores (7.5+)")
        print("   • Critical catalyst scores (8.5+)")
        print("   • Significant price movements (5%+)")
        print("   • Catalyst score changes (1.0+)")
        print("")
        print("📱 Notifications will be sent via:")
        if service.config.get('email_alerts', {}).get('enabled', False):
            print("   • Email alerts")
        if service.config.get('sms_alerts', {}).get('enabled', False):
            print("   • SMS alerts")
        if service.config.get('system_notifications', {}).get('enabled', True):
            print("   • System notifications")
        print("   • Log files")
        print("")
        print("🔄 Service is now monitoring your portfolio...")
        print("   Press Ctrl+C to stop")
        
        try:
            # Keep running
            while service.running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 Stopping service...")
            service.stop()
            print("✅ Service stopped successfully")
    else:
        print("❌ Failed to start service")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please ensure all required modules are available")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
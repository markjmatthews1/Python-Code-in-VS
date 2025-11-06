#!/usr/bin/env python3
"""
Quick Service Manager for Background Monitoring
Simple interface to start, stop, and check service status
"""

import os
import sys
import time
import subprocess
import json

def check_service_running():
    """Check if service is already running"""
    try:
        # Check for running Python processes with background_monitoring
        if os.name == 'nt':  # Windows
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                   capture_output=True, text=True)
            return 'python.exe' in result.stdout
        else:  # Unix/Linux
            result = subprocess.run(['pgrep', '-f', 'background_monitoring'], 
                                   capture_output=True, text=True)
            return bool(result.stdout.strip())
    except:
        return False

def start_service():
    """Start the background monitoring service"""
    print("Starting Background Monitoring Service...")
    
    # Check dependencies first
    print("   Checking dependencies...")
    missing_deps = []
    
    # Check for key modules
    try:
        import threading
        import signal
        import json
        import logging
    except ImportError as e:
        missing_deps.append(str(e))
    
    if missing_deps:
        print("❌ Missing dependencies:")
        for dep in missing_deps:
            print(f"   • {dep}")
        return False
    
    # Start service
    try:
        if os.name == 'nt':  # Windows
            # Run in new window
            subprocess.Popen(['python', 'start_monitoring.py'], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE)
        else:  # Unix/Linux
            subprocess.Popen(['python', 'start_monitoring.py'])
        
        print("✅ Service started successfully!")
        print("💡 Check logs in: monitoring_service.log")
        return True
        
    except Exception as e:
        print(f"❌ Failed to start service: {e}")
        return False

def stop_service():
    """Stop the background monitoring service"""
    print("Stopping Background Monitoring Service...")
    
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                          capture_output=True)
        else:  # Unix/Linux
            subprocess.run(['pkill', '-f', 'background_monitoring'], 
                          capture_output=True)
        
        print("✅ Service stopped")
        return True
        
    except Exception as e:
        print(f"❌ Failed to stop service: {e}")
        return False

def show_status():
    """Show service status and logs"""
    print("Background Monitoring Service Status")
    print("=" * 50)
    
    # Check if running
    if check_service_running():
        print("✅ Service Status: RUNNING")
    else:
        print("❌ Service Status: STOPPED")
    
    # Show configuration
    if os.path.exists("config/monitoring_service.json"):
        try:
            with open("config/monitoring_service.json", 'r') as f:
                config = json.load(f)
            print(f"\n📋 Portfolio: {len(config.get('portfolio_tickers', []))} tickers")
            print(f"   Check interval: {config.get('check_interval_minutes')} minutes")
        except:
            print("\n⚠️ Could not read configuration")
    
    # Show recent logs
    if os.path.exists("monitoring_service.log"):
        print("\n📝 Recent log entries:")
        try:
            with open("monitoring_service.log", 'r') as f:
                lines = f.readlines()
                for line in lines[-5:]:  # Last 5 lines
                    print(f"   {line.strip()}")
        except:
            print("   Could not read log file")

def main():
    """Main service manager interface"""
    print("Background Monitoring Service Manager")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Start Service")
        print("2. Stop Service") 
        print("3. Show Status")
        print("4. Check Configuration")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            start_service()
        elif choice == '2':
            stop_service()
        elif choice == '3':
            show_status()
        elif choice == '4':
            os.system('python check_service_status.py')
        elif choice == '5':
            print("Goodbye!")
            break
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
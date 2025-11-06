#!/usr/bin/env python3
"""
Quick Monitor Status Checker
Check if background monitoring service is running
"""

import subprocess
import os

def check_monitor_status():
    """Check if monitoring service is running"""
    print("🔍 Checking Background Monitoring Service Status...")
    print("=" * 60)
    
    try:
        if os.name == 'nt':  # Windows
            result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                                   capture_output=True, text=True)
            
            python_processes = result.stdout.count('python.exe')
            
            if python_processes > 0:
                print(f"✅ MONITORING STATUS: ACTIVE")
                print(f"   📊 Found {python_processes} Python process(es) running")
                print(f"   🎯 Background monitoring likely active")
                print(f"   💡 Check for console window with monitoring service")
            else:
                print(f"❌ MONITORING STATUS: STOPPED")
                print(f"   🔍 No Python processes found")
                print(f"   💡 Start monitoring via GUI 🎯 MONITOR button")
                
        else:  # Unix/Linux
            result = subprocess.run(['pgrep', '-f', 'background_monitoring'], 
                                   capture_output=True, text=True)
            if result.stdout.strip():
                print("✅ MONITORING STATUS: ACTIVE")
            else:
                print("❌ MONITORING STATUS: STOPPED")
    
    except Exception as e:
        print(f"⚠️ Error checking status: {e}")
    
    print("\n💡 Quick Actions:")
    print("   • To start: Use GUI 🎯 MONITOR button → 🚀 Start Service")
    print("   • To stop: Use GUI 🎯 MONITOR button → 🛑 Stop Service")
    print("   • Check logs: Look for monitoring_service.log")

if __name__ == "__main__":
    check_monitor_status()
    input("\nPress Enter to exit...")
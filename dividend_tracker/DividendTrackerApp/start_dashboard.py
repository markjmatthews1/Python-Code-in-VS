#!/usr/bin/env python3
"""
Simple script to start the dividend dashboard properly
"""

import subprocess
import sys
import os
import time

def start_dashboard():
    """Start the dividend dashboard"""
    print("🚀 Starting Dividend Dashboard...")
    
    # Change to the correct directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    print("📁 Current directory:", os.getcwd())
    print("🌐 Dashboard will be available at: http://127.0.0.1:8051")
    print("💡 Press Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Start the dashboard
        subprocess.run([sys.executable, "simple_dividend_dashboard.py"], check=True)
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error starting dashboard: {e}")

if __name__ == "__main__":
    start_dashboard()

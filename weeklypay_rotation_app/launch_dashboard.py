"""
Launch script for WeeklyPay™ Rotation Dashboard
Easy startup for the Streamlit GUI
"""

import subprocess
import sys
import os
from pathlib import Path

def launch_dashboard():
    """Launch the Streamlit dashboard"""
    
    print("🚀 LAUNCHING WEEKLYPAY™ ROTATION DASHBOARD")
    print("="*50)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    dashboard_file = current_dir / "streamlit_dashboard.py"
    
    if not dashboard_file.exists():
        print("❌ Error: streamlit_dashboard.py not found!")
        return
    
    print("📈 Starting Streamlit server...")
    print("🌐 Dashboard will open in your web browser")
    print("🔄 Real-time data updates every 5 minutes")
    print("⏹️  Press Ctrl+C to stop the server")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(dashboard_file),
            "--server.port", "8501",
            "--server.address", "localhost",
            "--theme.base", "light",
            "--theme.primaryColor", "#1f77b4",
            "--theme.backgroundColor", "#ffffff",
            "--theme.secondaryBackgroundColor", "#f0f2f6"
        ])
    
    except KeyboardInterrupt:
        print("\n✅ Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")
        print("\n💡 Troubleshooting:")
        print("   1. Ensure Streamlit is installed: pip install streamlit")
        print("   2. Check if port 8501 is available")
        print("   3. Try running manually: streamlit run streamlit_dashboard.py")

if __name__ == "__main__":
    launch_dashboard()
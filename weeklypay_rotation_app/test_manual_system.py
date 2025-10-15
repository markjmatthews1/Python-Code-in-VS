"""
Quick Test Launcher for WeeklyPay Manual Data Entry System
"""

import sys
import os
import subprocess
from datetime import datetime

def test_manual_gui():
    """Test the manual data entry GUI"""
    print("🚀 Testing Manual Data Entry GUI...")
    try:
        script_path = "manual_data_entry_gui.py"
        if os.path.exists(script_path):
            subprocess.run([sys.executable, script_path])
            print("✅ GUI test completed")
        else:
            print("❌ GUI script not found")
    except Exception as e:
        print(f"❌ GUI test failed: {e}")

def test_comprehensive_calendar():
    """Test the comprehensive earnings calendar"""
    print("\n📅 Testing Comprehensive Earnings Calendar...")
    try:
        from comprehensive_earnings_calendar import WeeklyPayEarningsCalendar
        
        calendar_system = WeeklyPayEarningsCalendar()
        calendar, sources = calendar_system.get_comprehensive_earnings_calendar(prompt_for_manual=False)
        
        print(f"✅ Calendar loaded with {len(calendar)} ETFs")
        
        # Show current data
        current_time = datetime.now()
        for etf, date in calendar.items():
            days_away = (date - current_time).days
            source = sources.get(etf, 'unknown')
            print(f"   {etf}: {date.strftime('%Y-%m-%d')} ({days_away} days) - {source}")
        
        # Test HOOW specifically
        hoow_days = (calendar['HOOW'] - current_time).days
        print(f"\n🎯 HOOW verification: {hoow_days} days (should be ~28-29)")
        
    except Exception as e:
        print(f"❌ Calendar test failed: {e}")

def launch_enhanced_dashboard():
    """Launch the enhanced dashboard"""
    print("\n🌐 Launching Enhanced Dashboard...")
    try:
        import subprocess
        
        print("Starting Streamlit dashboard on port 8504...")
        print("Dashboard will open at: http://localhost:8504")
        
        # Launch in background
        subprocess.Popen([
            sys.executable, "-m", "streamlit", "run", 
            "enhanced_dashboard.py", "--server.port", "8504"
        ])
        
        print("✅ Dashboard launched! Check your browser.")
        
    except Exception as e:
        print(f"❌ Dashboard launch failed: {e}")

def show_manual_data():
    """Show current manual data entries"""
    print("\n📋 Current Manual Data Entries:")
    try:
        import json
        
        manual_data_file = "manual_earnings_data.json"
        if os.path.exists(manual_data_file):
            with open(manual_data_file, 'r') as f:
                manual_data = json.load(f)
            
            if manual_data:
                for etf, data in manual_data.items():
                    entry_date = data.get('earnings_date', 'Unknown')
                    entry_time = data.get('entry_timestamp', 'Unknown')
                    print(f"   {etf}: {entry_date} (entered: {entry_time})")
            else:
                print("   No manual entries found")
        else:
            print("   No manual data file exists")
            
    except Exception as e:
        print(f"❌ Error reading manual data: {e}")

def main():
    """Main test menu"""
    print("=" * 60)
    print("🔧 WeeklyPay™ Manual Data Entry System - Test Launcher")
    print("=" * 60)
    
    while True:
        print("\nSelect a test option:")
        print("1. 🎨 Test Manual Data Entry GUI")
        print("2. 📅 Test Comprehensive Calendar")
        print("3. 🌐 Launch Enhanced Dashboard")
        print("4. 📋 Show Current Manual Data")
        print("5. 🧪 Run All Tests")
        print("0. ❌ Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == "1":
            test_manual_gui()
        elif choice == "2":
            test_comprehensive_calendar()
        elif choice == "3":
            launch_enhanced_dashboard()
        elif choice == "4":
            show_manual_data()
        elif choice == "5":
            print("\n🧪 Running All Tests...")
            show_manual_data()
            test_comprehensive_calendar()
            print("\n🎨 Opening GUI...")
            test_manual_gui()
            print("\n🌐 Launching Dashboard...")
            launch_enhanced_dashboard()
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("❌ Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
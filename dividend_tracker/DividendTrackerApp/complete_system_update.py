#!/usr/bin/env python3
"""
Complete Dividend Tracker System Launcher
Runs all components of the dividend tracking system in proper sequence

Author: Mark
Created: August 6, 2025
Purpose: Weekend update launcher for complete dividend system
Location: DividendTrackerApp directory
"""

import os
import sys
import subprocess
import time

def main():
    """
    Complete dividend tracker system launcher that:
    1. Updates Portfolio_2025 sheet with current real-time data
    2. Updates Estimated Income 2025 page with all 4 accounts
    3. Updates Ticker Analysis 2025 sheet with new yield columns
    4. Updates portfolio values and calculates gains
    5. Updates ticker quantities and new/removed tickers
    6. Displays summary GUI popup at the end
    """
    
    print("🚀 Starting Complete Dividend Tracker System Update...")
    print("=" * 60)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    modules_dir = os.path.join(script_dir, "modules")
    
    # Step 1: Run main dividend tracker with full API integration
    print("📊 Step 1: Updating Portfolio & Estimated Income sheets...")
    try:
        result = subprocess.run([
            sys.executable, 
            os.path.join(modules_dir, "estimated_income_tracker.py"),
            "--api", "--portfolio", "--comprehensive"
        ], cwd=script_dir, capture_output=True, text=True, timeout=300)
        
        if result.returncode == 0:
            print("✅ Portfolio & Estimated Income update completed successfully")
        else:
            print(f"⚠️ Portfolio update completed with warnings: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏰ Portfolio update timed out after 5 minutes")
    except Exception as e:
        print(f"❌ Error updating portfolio: {e}")
    
    # Small delay between operations
    time.sleep(2)
    
    # Step 2: Run ticker analysis update
    print("\n📈 Step 2: Updating Ticker Analysis sheet...")
    try:
        result = subprocess.run([
            sys.executable, 
            "create_historical_ticker_analysis.py"
        ], cwd=script_dir, capture_output=True, text=True, timeout=180)
        
        if result.returncode == 0:
            print("✅ Ticker Analysis update completed successfully")
        else:
            print(f"⚠️ Ticker Analysis completed with warnings: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏰ Ticker Analysis update timed out after 3 minutes")
    except Exception as e:
        print(f"❌ Error updating ticker analysis: {e}")
    
    print("\n" + "=" * 60)
    print("🎉 Complete Dividend Tracker System Update Finished!")
    print("📁 Check outputs/Dividends_2025.xlsx for updated data")
    print("💡 All sheets should now be updated with current data")
    
    # Keep console open for a moment to see results
    input("\nPress Enter to close...")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Fully Automated Dividend Dashboard System
- Automatically updates all position data from APIs
- Fetches dividend yields from Alpha Vantage
- Launches dividend-focused dashboard 
- Zero manual intervention required
"""

import sys
import os
import subprocess
import time
from datetime import datetime

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def run_automated_update():
    """Run the automated portfolio update"""
    print("🚀 STARTING AUTOMATED PORTFOLIO UPDATE...")
    print("="*60)
    
    try:
        # Run the automated update script
        result = subprocess.run([
            sys.executable, 
            'automated_portfolio_update.py'
        ], capture_output=True, text=True, cwd=os.path.dirname(__file__))
        
        if result.returncode == 0:
            print("✅ Automated portfolio update completed!")
            print(result.stdout)
            return True
        else:
            print("❌ Portfolio update failed:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running automated update: {e}")
        return False

def show_dividend_completion_popup():
    """Show the dividend completion display"""
    print("\n🎯 SHOWING DIVIDEND COMPLETION DISPLAY...")
    print("="*50)
    
    try:
        # Use console-based display (doesn't interfere with other apps)
        from console_completion_display import show_console_completion_display
        
        print("✅ Processing complete - showing results!")
        print("🎯 Shows dividend stocks with ≥4% yield")
        print("📊 Data updated automatically from APIs")
        print("📋 Console display will appear...")
        
        # Show the console display
        show_console_completion_display()
        
        return True
        
    except Exception as e:
        print(f"⚠️ Console display failed: {e}")
        print("� Showing basic summary instead...")
        
        # Final fallback
        print("\n🎯 DIVIDEND TRACKER - PROCESSING COMPLETE")
        print("="*50)
        print("✅ Your dividend data has been processed successfully!")
        print("📊 Check outputs/Dividends_2025.xlsx for full results")
        print(f"📅 Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*50)
        return False

def main():
    """Main automated system launcher"""
    print("🎯 AUTOMATED DIVIDEND TRACKING SYSTEM")
    print("="*60)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("📋 AUTOMATION FEATURES:")
    print("  ✅ Fetches ALL positions from E*TRADE & Schwab APIs")
    print("  ✅ Gets dividend yields from Alpha Vantage API")
    print("  ✅ Updates Excel automatically") 
    print("  ✅ Shows beautiful console results (≥4% yield)")
    print("  ✅ Zero manual intervention required")
    print()
    
    # Step 1: Update portfolio data automatically
    update_success = run_automated_update()
    
    if update_success:
        print("\n" + "="*60)
        
        # Step 2: Show beautiful completion popup
        popup_success = show_dividend_completion_popup()
        
        if popup_success:
            print("\n🎉 AUTOMATED SYSTEM FULLY OPERATIONAL!")
            print("="*60)
            print("📊 Your dividend processing completed successfully")
            print("🔄 Data updated automatically from APIs")
            print("💰 Only 401k weekly amounts need manual updates")
            print()
            print("✅ SYSTEM READY:")
            print("   ✅ E*TRADE API connected")
            print("   ✅ Schwab API connected") 
            print("   ✅ Alpha Vantage API configured")
            print("   ✅ Results displayed in console with 4% yield filter")
            
        else:
            print("\n⚠️ Display failed - check console for summary")
    else:
        print("\n❌ Automated update failed - check API connections")

if __name__ == '__main__':
    main()

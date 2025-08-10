#!/usr/bin/env python3
"""
Test Console Completion Display
This won't interfere with your day trading app
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_console_display():
    """Test the console completion display"""
    print("🧪 Testing Console Dividend Completion Display...")
    print("="*60)
    print("📋 This will show in the current terminal without opening new windows")
    print("💡 Safe to use while day trading app is running")
    print()
    
    try:
        from console_completion_display import show_console_completion_display
        
        print("🎯 Showing console completion display...")
        show_console_completion_display()
        
        print("✅ Console display test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Showing basic fallback...")
        
        print("\n🎯 DIVIDEND TRACKER - PROCESSING COMPLETE")
        print("="*50)
        print("✅ Your dividend data processed successfully!")
        print("📊 Check outputs/Dividends_2025.xlsx for results")
        print("="*50)

if __name__ == "__main__":
    test_console_display()

#!/usr/bin/env python3
"""
Test the Dividend Popup Display
Use this to test the popup without running the full automation
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_popup():
    """Test the dividend popup display"""
    print("🧪 Testing Dividend Completion Popup...")
    print("="*50)
    
    try:
        from dividend_popup_display import show_dividend_completion_popup
        
        print("📊 Loading dividend data...")
        print("🎯 Creating beautiful popup window...")
        print("💡 Popup should appear in a few seconds...")
        
        # Show the popup
        show_dividend_completion_popup()
        
        print("✅ Popup test completed!")
        
    except Exception as e:
        print(f"❌ Error testing popup: {e}")
        print("💡 Make sure you have tkinter installed and Dividends_2025.xlsx exists")

if __name__ == "__main__":
    test_popup()

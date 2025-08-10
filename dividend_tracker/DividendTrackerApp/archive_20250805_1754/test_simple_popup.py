#!/usr/bin/env python3
"""
Test the Simple Popup Display
Quick test for the lightweight popup version
"""

import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(__file__))

def test_simple_popup():
    """Test the simple dividend popup display"""
    print("🧪 Testing Simple Dividend Completion Popup...")
    print("="*50)
    
    try:
        from simple_popup_display import show_simple_completion_popup
        
        print("📊 Creating simple popup window...")
        print("💡 Popup should appear in a few seconds...")
        
        # Show the simple popup
        show_simple_completion_popup()
        
        print("✅ Simple popup test completed!")
        
    except Exception as e:
        print(f"❌ Error testing simple popup: {e}")
        print("💡 Make sure you have tkinter installed")

if __name__ == "__main__":
    test_simple_popup()

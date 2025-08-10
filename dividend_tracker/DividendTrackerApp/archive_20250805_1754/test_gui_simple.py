#!/usr/bin/env python3
"""Simple GUI test for 401k popup"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.gui_prompts import ColorfulK401Prompt

print("🧪 Testing standalone GUI popup...")

try:
    popup = ColorfulK401Prompt()
    result = popup.show_popup()
    
    if result is not None:
        print(f"✅ Success! Got value: ${result:,.2f}")
    else:
        print("❌ User cancelled or no value entered")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Test completed.")

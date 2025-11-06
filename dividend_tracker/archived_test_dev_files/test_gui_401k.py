#!/usr/bin/env python3
"""
Test GUI 401K Input Directly
"""

import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from gui_prompts import get_k401_value

def main():
    print("Testing GUI 401K Input")
    print("=" * 30)
    
    print("💰 Calling get_k401_value()...")
    result = get_k401_value()
    
    print(f"\n📊 RESULT:")
    print(f"Type: {type(result)}")
    print(f"Value: {result}")
    
    if result is not None:
        print(f"Formatted: ${result:,.2f}")
    else:
        print("Result is None (user cancelled)")

if __name__ == "__main__":
    main()

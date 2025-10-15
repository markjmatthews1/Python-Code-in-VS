#!/usr/bin/env python3
"""
Quick fix for color references in enhanced strategy panel
"""

def fix_color_references():
    file_path = 'c:/Users/mjmat/Python Code in VS/RecoveryApp/gui/enhanced_strategy_panel.py'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Fix color references
    content = content.replace("UIConfig.COLORS['text_primary']", "UIConfig.COLORS['text_light']")
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed all text_primary color references")

if __name__ == "__main__":
    fix_color_references()
#!/usr/bin/env python3
"""
Test to debug Complete System Update historical yield integration
"""

import os
import subprocess
import sys

def test_complete_system_integration():
    """Test if the Complete System Update is properly calling the historical yield updater"""
    
    print("🧪 TESTING COMPLETE SYSTEM UPDATE INTEGRATION")
    print("="*50)
    
    # Check which files exist
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    files_to_check = [
        "proper_excel_updater.py",
        "corrected_enhanced_historical_yield_updater.py",
        "enhanced_cache_historical_yield_updater.py", 
        "cache_historical_yield_updater.py"
    ]
    
    print("\n📁 CHECKING FILES:")
    for filename in files_to_check:
        filepath = os.path.join(script_dir, filename)
        exists = "✅" if os.path.exists(filepath) else "❌"
        print(f"  {exists} {filename}")
    
    # Test if proper_excel_updater can find the corrected updater
    print("\n🔍 TESTING FILE DISCOVERY:")
    corrected_updater = os.path.join(script_dir, "corrected_enhanced_historical_yield_updater.py")
    
    if os.path.exists(corrected_updater):
        print(f"  ✅ Corrected updater found: {corrected_updater}")
        
        # Test running it directly
        print("\n🚀 TESTING DIRECT EXECUTION:")
        try:
            result = subprocess.run([sys.executable, corrected_updater], 
                                  capture_output=True, text=True, cwd=script_dir, timeout=30)
            
            if result.returncode == 0:
                print("  ✅ Direct execution successful")
                print("  📊 Output preview:")
                lines = result.stdout.split('\n')
                for line in lines[:10]:  # Show first 10 lines
                    if line.strip():
                        print(f"    {line}")
                if len(lines) > 10:
                    print(f"    ... ({len(lines)-10} more lines)")
            else:
                print("  ❌ Direct execution failed")
                print(f"  Error: {result.stderr}")
                
        except Exception as e:
            print(f"  ❌ Exception during execution: {e}")
    else:
        print(f"  ❌ Corrected updater not found!")
    
    # Check the proper_excel_updater method
    print("\n📖 CHECKING PROPER_EXCEL_UPDATER METHOD:")
    try:
        with open(os.path.join(script_dir, "proper_excel_updater.py"), 'r') as f:
            content = f.read()
            
        if "update_historical_yield_sheet" in content:
            print("  ✅ update_historical_yield_sheet method found")
            
            if "corrected_enhanced_historical_yield_updater" in content:
                print("  ✅ References corrected updater")
            else:
                print("  ❌ Does not reference corrected updater")
        else:
            print("  ❌ update_historical_yield_sheet method not found")
            
    except Exception as e:
        print(f"  ❌ Error checking proper_excel_updater: {e}")

if __name__ == "__main__":
    test_complete_system_integration()
#!/usr/bin/env python3
"""
Test script to diagnose update issues
"""

import os
import sys
import traceback
import subprocess
from datetime import datetime

def test_update():
    print("Testing dividend update components...")
    print(f"Current directory: {os.getcwd()}")
    print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
    
    # Test 1: Check if Update_dividend_sheet.py exists
    update_script = os.path.join("modules", "Update_dividend_sheet.py")
    print(f"\nTesting: {update_script}")
    print(f"Exists: {os.path.exists(update_script)}")
    
    if os.path.exists(update_script):
        try:
            print("Running Update_dividend_sheet.py...")
            result = subprocess.run([
                sys.executable, update_script
            ], capture_output=True, text=True, timeout=30)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT: {result.stdout[:500]}...")
            if result.stderr:
                print(f"STDERR: {result.stderr[:500]}...")
                
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
    
    # Test 2: Check if historic yield updater exists
    historic_script = "update_etrade_historic_yield.py"
    print(f"\nTesting: {historic_script}")
    print(f"Exists: {os.path.exists(historic_script)}")
    
    if os.path.exists(historic_script):
        try:
            print("Running update_etrade_historic_yield.py...")
            result = subprocess.run([
                sys.executable, historic_script
            ], capture_output=True, text=True, timeout=30)
            
            print(f"Return code: {result.returncode}")
            print(f"STDOUT: {result.stdout[:200]}...")
            if result.stderr:
                print(f"STDERR: {result.stderr[:200]}...")
                
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    test_update()

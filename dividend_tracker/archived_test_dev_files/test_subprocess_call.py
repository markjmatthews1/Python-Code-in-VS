#!/usr/bin/env python3

import subprocess
import sys
import os

def test_subprocess_call():
    """Test calling the final updater via subprocess like the main app does"""
    print("TESTING SUBPROCESS CALL TO FINAL UPDATER")
    print("=" * 50)
    
    script_path = "final_historical_yield_updater.py"
    
    if not os.path.exists(script_path):
        print(f"ERROR: Script not found: {script_path}")
        return False
    
    print("Running final updater via subprocess...")
    
    try:
        result = subprocess.run([sys.executable, script_path], 
                              capture_output=True, text=True, 
                              cwd=os.getcwd())
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT:")
        print(result.stdout)
        
        if result.stderr:
            print(f"STDERR:")
            print(result.stderr)
        
        if result.returncode == 0:
            print("SUCCESS: Subprocess call worked!")
            return True
        else:
            print("ERROR: Subprocess call failed")
            return False
            
    except Exception as e:
        print(f"ERROR: Exception during subprocess call: {e}")
        return False

if __name__ == "__main__":
    test_subprocess_call()
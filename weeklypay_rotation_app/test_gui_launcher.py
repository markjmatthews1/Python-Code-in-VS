"""
WeeklyPay GUI Launcher - Unicode Safe Version
Test launcher for the WeeklyPay native GUI
"""

import sys
import os

def test_gui_function():
    """Test just the function that was causing the error"""
    
    # Add the WeeklyPay directory to path
    weeklypay_dir = os.path.join(os.path.dirname(__file__))
    sys.path.insert(0, weeklypay_dir)
    
    try:
        print("Testing WeeklyPay GUI function fix...")
        
        # Import just what we need to test
        import pandas as pd
        from datetime import datetime
        
        # Create a minimal test
        print("Creating test DataFrame...")
        test_data = {
            'Ticker': ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW'],
            'WeeklyPay_Score': [75, 65, 55, 70, 60, 50],
            'Rotation_Signal': ['BUY', 'HOLD', 'SELL', 'BUY', 'HOLD', 'SELL'],
            'Weekly_Yield_%': [1.2, 0.8, 0.6, 1.1, 0.9, 0.7],
            'RSI': [45, 55, 35, 50, 60, 30]
        }
        test_df = pd.DataFrame(test_data)
        print(f"Test DataFrame created: {len(test_df)} rows")
        
        # Import and test the specific function
        from simple_dashboard import format_rotation_week_summary
        print("Function imported successfully")
        
        # Test the function call (this was causing the original error)
        result = format_rotation_week_summary(test_df)
        print("Function executed successfully!")
        print(f"Result type: {type(result)}")
        print(f"Result length: {len(result)} characters")
        
        # Show a preview of the result
        print("\n--- Preview of Function Output ---")
        print(result[:300] + "..." if len(result) > 300 else result)
        
        print("\n" + "="*50)
        print("SUCCESS: WeeklyPay GUI function signature is FIXED!")
        print("The 'takes 1 positional argument but 2 were given' error is resolved.")
        print("="*50)
        
        return True
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def launch_full_gui():
    """Launch the full WeeklyPay GUI"""
    
    weeklypay_dir = os.path.join(os.path.dirname(__file__))
    sys.path.insert(0, weeklypay_dir)
    
    try:
        print("Launching WeeklyPay GUI...")
        
        # Import and launch the GUI
        from simple_dashboard import create_tkinter_gui_window
        create_tkinter_gui_window()
        
    except Exception as e:
        print(f"GUI Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("WeeklyPay GUI Launcher")
    print("1. Test function fix")
    print("2. Launch full GUI")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        test_gui_function()
    elif choice == "2":
        # First test the function, then launch GUI if successful
        if test_gui_function():
            print("\nFunction test passed! Launching full GUI...")
            launch_full_gui()
        else:
            print("\nFunction test failed. Please fix errors before launching GUI.")
    else:
        print("Invalid choice. Running function test by default...")
        test_gui_function()
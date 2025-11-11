"""
Simple GUI launch test - no unicode
"""

import sys
import traceback

print("="*80)
print("WeeklyPay GUI Launch Test")
print("="*80)

try:
    print("\nImporting simple_dashboard...")
    import simple_dashboard
    print("SUCCESS - Module imported")
    
    print("\nGenerating test data...")
    df = simple_dashboard.generate_etf_data()
    print(f"SUCCESS - Generated {len(df)} tickers")
    print(f"Tickers: {', '.join(df['Ticker'].tolist())}")
    
    print("\nCreating GUI window...")
    root = simple_dashboard.create_tkinter_gui_window()
    
    if root:
        print("SUCCESS - GUI window created!")
        print(f"Window title: {root.title()}")
        print("\nDestroying test window...")
        root.destroy()
        print("\n" + "="*80)
        print("ALL TESTS PASSED - GUI SHOULD WORK!")
        print("="*80)
    else:
        print("ERROR - create_tkinter_gui_window() returned None")
        sys.exit(1)
        
except Exception as e:
    print(f"\nERROR: {e}")
    print("\nFull traceback:")
    traceback.print_exc()
    sys.exit(1)

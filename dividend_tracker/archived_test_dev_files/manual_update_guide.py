#!/usr/bin/env python3
"""
Manual step-by-step update guide
"""

print("""
=== MANUAL DIVIDEND TRACKER UPDATE GUIDE ===

Since the automation isn't working, let's update manually:

STEP 1: Update Portfolio Values & Estimated Income
------------------------------------------------------
1. Open file explorer to: c:\\Users\\mjmat\\Python Code in VS\\dividend_tracker\\DividendTrackerApp\\modules
2. Double-click: estimated_income_tracker.py
3. This should open and prompt for 401K value
4. Enter your current 401K value when prompted

STEP 2: Update Historic Yields
------------------------------------------------------
1. In same folder, double-click: update_etrade_historic_yield.py  
2. This should update the historic yield sheet

STEP 3: Check Results
------------------------------------------------------
1. Open: outputs\\Dividends_2025.xlsx
2. Check if sheets have today's date (08/31/2025)
3. Verify data looks current

If this doesn't work, we'll need to debug the core scripts.
""")

input("Press Enter after reading...")

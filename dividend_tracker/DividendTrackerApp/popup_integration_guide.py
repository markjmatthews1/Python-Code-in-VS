#!/usr/bin/env python3
"""
Quick Integration Guide for Dividend Popup

Add this code to the end of ANY dividend tracker script to show the popup:

```python
# At the end of your processing script, add:
try:
    from dividend_popup_display import show_dividend_completion_popup
    print("🎯 Processing complete - showing results popup!")
    show_dividend_completion_popup()
except Exception as e:
    print(f"⚠️ Could not show popup: {e}")
    print("📊 Check outputs/Dividends_2025.xlsx for results")
```

INTEGRATION EXAMPLES:
====================

1. FOR estimated_income_tracker.py:
   Add the popup code after the final Excel save

2. FOR any weekly processing script:
   Add the popup code after data processing completes

3. FOR manual runs:
   Just run test_popup.py to see results

The popup will automatically:
✅ Load data from outputs/Dividends_2025.xlsx
✅ Filter for dividend stocks ≥4% yield
✅ Show beautiful summary with account breakdown
✅ Display top positions in scrollable table
✅ Provide links to open full Excel report

REQUIREMENTS:
=============
- tkinter (included with Python)
- pandas (for data processing)
- outputs/Dividends_2025.xlsx (your main Excel file)

The popup is completely self-contained and will work with your existing
dividend tracker infrastructure without any modifications needed!
"""

def show_integration_examples():
    """Show integration examples"""
    print("🎯 DIVIDEND POPUP INTEGRATION GUIDE")
    print("="*60)
    print(__doc__)

if __name__ == "__main__":
    show_integration_examples()

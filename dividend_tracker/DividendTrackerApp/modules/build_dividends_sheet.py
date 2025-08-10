r"""
Module: build_dividends_sheet.py
Author: Mark
Created: July 20, 2025
Purpose: Build complete E*TRADE dividend Excel workbook
Location: C:\Python_Projects\DividendTrackerApp\modules\build_dividends_sheet.py
"""

import os
from openpyxl import Workbook
from modules import dividend_loader, excel_generator, summary_builder, estimated_income_tracker

# ------------------------- Configuration -------------------------
INPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data")
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "outputs")
TARGET_FILE = os.path.join(OUTPUT_PATH, "Dividends_2025.xlsx")

def process_etrade_files():
    """Process all E*TRADE dividend files and build Excel workbook"""
    wb = Workbook()
    wb.remove(wb.active)

    for filename in os.listdir(INPUT_PATH):
        # Skip estimate files - they're handled separately
        if "estimates" in filename.lower():
            print(f"📊 Skipping estimate file (handled separately): {filename}")
            continue
            
        if filename.endswith(".xlsx") and "etrade" in filename.lower():
            print(f"📄 Processing dividend file: {filename}")
            
            df = dividend_loader.load_dividend_file(filename)
            
            if "ira" in filename.lower():
                sheet_name = "ETRADE IRA Dividends 2025"
                df["Account Type"] = "ETRADE IRA"
            elif "taxable" in filename.lower():
                sheet_name = "ETRADE Taxable Dividends 2025" 
                df["Account Type"] = "ETRADE Taxable"
            else:
                print(f"⚠️ Unknown account type in file: {filename}")
                continue

            excel_generator.write_to_workbook(wb, sheet_name, df)

    wb.save(TARGET_FILE)
    print(f"✅ E*TRADE workbook saved: {TARGET_FILE}")

    # Add Totals 2025 sheet with summary tables
    try:
        summary_builder.build_totals_sheet()
        print("📊 Summary sheet integrated via summary_builder.")
    except Exception as e:
        print(f"❌ Error running summary_builder: {e}")

    # Add estimated income tracking
    try:
        estimated_income_tracker.build_estimated_income_tracker()
        print("📈 Estimated income tracker integrated.")
    except Exception as e:
        print(f"❌ Error running estimated income tracker: {e}")

if __name__ == "__main__":
    if not os.path.exists(OUTPUT_PATH):
        os.makedirs(OUTPUT_PATH)
    process_etrade_files()
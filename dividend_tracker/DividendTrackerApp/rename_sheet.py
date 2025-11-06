#!/usr/bin/env python3
"""
Rename Sheet to "Accounts dividend historical yield"
===================================================
"""

import openpyxl
import os

def rename_sheet():
    """Rename the sheet to the new name"""
    
    excel_path = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp\outputs\Dividends_2025.xlsx"
    
    try:
        workbook = openpyxl.load_workbook(excel_path)
        
        # Find and rename the sheet
        if "Etrade IRA historic yield" in workbook.sheetnames:
            sheet = workbook["Etrade IRA historic yield"]
            sheet.title = "Accounts dividend historical yield"
            print(f"✅ Renamed sheet to: 'Accounts dividend historical yield'")
        else:
            print(f"❌ Could not find original sheet name")
            return
        
        # Save the changes
        workbook.save(excel_path)
        workbook.close()
        
        print(f"💾 File saved with new sheet name")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    rename_sheet()

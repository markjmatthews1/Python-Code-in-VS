#!/usr/bin/env python3
"""
Clear existing E*TRADE Taxable data and re-fetch complete data from API
"""

import pandas as pd
from datetime import datetime

def clear_and_refetch_etrade_taxable():
    """Remove existing E*TRADE Taxable data and re-add from API"""
    
    print("🔄 Clearing existing E*TRADE Taxable data and re-fetching from API...")
    
    try:
        # Read existing dividends data
        dividends_excel = 'outputs/Dividends_2025.xlsx'
        existing_df = pd.read_excel(dividends_excel)
        print(f"📊 Current data: {len(existing_df)} rows")
        
        # Remove existing E*TRADE Taxable rows
        filtered_df = existing_df[existing_df['Account'] != 'E*TRADE Taxable']
        print(f"📊 After removing E*TRADE Taxable: {len(filtered_df)} rows")
        
        # Create backup with current data
        backup_file = f'outputs/Dividends_2025_backup_before_refresh_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        existing_df.to_excel(backup_file, index=False)
        print(f"📁 Backup saved: {backup_file}")
        
        # Save cleaned data (without E*TRADE Taxable)
        filtered_df.to_excel(dividends_excel, index=False)
        print(f"✅ Cleared existing E*TRADE Taxable data")
        print(f"📋 Remaining accounts: {filtered_df['Account'].value_counts()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = clear_and_refetch_etrade_taxable()
    if success:
        print("\n✅ Ready to re-fetch complete E*TRADE Taxable data from API")
    else:
        print("\n❌ Failed to clear existing data")

#!/usr/bin/env python3
"""
Update Dividends_2025.xlsx with E*TRADE Taxable account data
"""

import pandas as pd
import os
from datetime import datetime

def update_dividends_excel_with_etrade_taxable():
    """Add E*TRADE Taxable data to the Dividends_2025.xlsx file"""
    
    print("🔄 Updating Dividends_2025.xlsx with E*TRADE Taxable data...")
    
    # File paths
    dividends_excel = 'outputs/Dividends_2025.xlsx'
    etrade_taxable_file = r'c:\Users\mjmat\Python Code in VS\Etrade_Individual_Brokerage_data.xlsx'
    
    try:
        # Read existing dividends data
        existing_df = pd.read_excel(dividends_excel)
        print(f"📊 Current data: {len(existing_df)} rows")
        print(f"📋 Current accounts: {existing_df['Account'].value_counts()}")
        
        # Read E*TRADE Taxable data
        if os.path.exists(etrade_taxable_file):
            etrade_taxable_df = pd.read_excel(etrade_taxable_file)
            print(f"📊 E*TRADE Taxable data: {len(etrade_taxable_df)} rows")
            
            # Filter for dividend stocks only (avoid growth stocks)
            dividend_tickers = ['PDI', 'OFS', 'ABR', 'ACP', 'NHS', 'QDTE', 'AGNC', 'QYLD', 'JEPI', 'JEPQ', 'DIVO', 'SCHD', 'VYM', 'SPHD', 'RYLD', 'SVOL']
            
            if 'Ticker' in etrade_taxable_df.columns:
                dividend_positions = etrade_taxable_df[etrade_taxable_df['Ticker'].isin(dividend_tickers)].copy()
                print(f"🎯 Found {len(dividend_positions)} dividend positions in E*TRADE Taxable")
                
                # Add account column
                dividend_positions['Account'] = 'E*TRADE Taxable'
                
                # Make sure we have the same columns as existing data
                for col in existing_df.columns:
                    if col not in dividend_positions.columns:
                        if col in ['08-02-2025', '07-28-2025', '07-19-2025']:  # Yield columns
                            dividend_positions[col] = 0.0  # Will need to calculate actual yields
                        else:
                            dividend_positions[col] = ''
                
                # Reorder columns to match existing data
                dividend_positions = dividend_positions[existing_df.columns]
                
                # Append to existing data
                updated_df = pd.concat([existing_df, dividend_positions], ignore_index=True)
                
                # Save updated file
                backup_file = f'outputs/Dividends_2025_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
                existing_df.to_excel(backup_file, index=False)
                print(f"📁 Backup saved: {backup_file}")
                
                updated_df.to_excel(dividends_excel, index=False)
                print(f"✅ Updated {dividends_excel} with E*TRADE Taxable data")
                print(f"📊 New total: {len(updated_df)} rows")
                print(f"📋 Updated accounts: {updated_df['Account'].value_counts()}")
                
                return True
            else:
                print("❌ No 'Ticker' column found in E*TRADE Taxable data")
                return False
        else:
            print(f"❌ E*TRADE Taxable file not found: {etrade_taxable_file}")
            return False
            
    except Exception as e:
        print(f"❌ Error updating Excel file: {e}")
        return False

if __name__ == '__main__':
    success = update_dividends_excel_with_etrade_taxable()
    if success:
        print("🎉 Successfully updated Dividends_2025.xlsx with E*TRADE Taxable data!")
    else:
        print("❌ Failed to update Excel file")

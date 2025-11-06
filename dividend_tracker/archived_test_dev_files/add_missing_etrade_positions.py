#!/usr/bin/env python3
"""
Add missing E*TRADE Taxable positions to Dividends_2025.xlsx
"""

import pandas as pd
from datetime import datetime

def add_missing_etrade_taxable_positions():
    """Add the missing MORT, BITO, ARI, and EIC positions"""
    
    print("🔄 Adding missing E*TRADE Taxable positions...")
    
    # Missing positions with actual data from the screenshot
    missing_positions = [
        {
            'Account': 'E*TRADE Taxable',
            'Ticker': 'MORT', 
            'Qty #': 90,
            'Price Paid $': 11.25,
            'Last Price $': 10.67,
            'Current Value $': 960.30,
            'Original Value $': 1012.50,  # 90 * 11.25
            'Total Gain %': -5.16,
            '08-02-2025': 12.56,  # Current dividend yield from screenshot
            '07-28-2025': 12.56,
            '07-19-2025': 12.56,
            'Beginning Dividend Yield': 12.56
        },
        {
            'Account': 'E*TRADE Taxable',
            'Ticker': 'BITO', 
            'Qty #': 200,
            'Price Paid $': 23.35,
            'Last Price $': 20.79,
            'Current Value $': 4158.00,
            'Original Value $': 4670.00,  # 200 * 23.35
            'Total Gain %': -10.96,
            '08-02-2025': 53.41,  # Current dividend yield from screenshot
            '07-28-2025': 53.41,
            '07-19-2025': 53.41,
            'Beginning Dividend Yield': 53.41
        },
        {
            'Account': 'E*TRADE Taxable',
            'Ticker': 'ARI', 
            'Qty #': 472,
            'Price Paid $': 10.1571,
            'Last Price $': 9.91,
            'Current Value $': 4677.52,
            'Original Value $': 4794.15,  # 472 * 10.1571
            'Total Gain %': -2.43,
            '08-02-2025': 10.22,  # Current dividend yield from screenshot
            '07-28-2025': 10.22,
            '07-19-2025': 10.22,
            'Beginning Dividend Yield': 10.22
        },
        {
            'Account': 'E*TRADE Taxable',
            'Ticker': 'EIC', 
            'Qty #': 300,
            'Price Paid $': 15.50,
            'Last Price $': 12.71,
            'Current Value $': 3813.00,
            'Original Value $': 4650.00,  # 300 * 15.50
            'Total Gain %': -18.00,
            '08-02-2025': 12.26,  # Current dividend yield from screenshot
            '07-28-2025': 12.26,
            '07-19-2025': 12.26,
            'Beginning Dividend Yield': 12.26
        }
    ]
    
    try:
        # Read existing dividends data
        dividends_excel = 'outputs/Dividends_2025.xlsx'
        existing_df = pd.read_excel(dividends_excel)
        print(f"📊 Current data: {len(existing_df)} rows")
        
        # Check if these positions already exist
        existing_etrade_taxable = existing_df[existing_df['Account'] == 'E*TRADE Taxable']
        existing_tickers = set(existing_etrade_taxable['Ticker'].values)
        
        new_positions = []
        for pos in missing_positions:
            if pos['Ticker'] not in existing_tickers:
                new_positions.append(pos)
                print(f"   ✅ Adding missing position: {pos['Ticker']}")
            else:
                print(f"   ℹ️ Position already exists: {pos['Ticker']}")
        
        if not new_positions:
            print("ℹ️ All positions already exist in Excel file")
            return True
        
        # Convert new positions to DataFrame
        new_df = pd.DataFrame(new_positions)
        
        # Add missing columns to match existing structure
        for col in existing_df.columns:
            if col not in new_df.columns:
                new_df[col] = ''  # Default empty value
        
        # Reorder columns to match existing data
        new_df = new_df[existing_df.columns]
        
        # Append to existing data
        updated_df = pd.concat([existing_df, new_df], ignore_index=True)
        
        # Create backup
        backup_file = f'outputs/Dividends_2025_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        existing_df.to_excel(backup_file, index=False)
        print(f"📁 Backup saved: {backup_file}")
        
        # Save updated file
        updated_df.to_excel(dividends_excel, index=False)
        print(f"✅ Added {len(new_positions)} missing E*TRADE Taxable positions")
        print(f"📊 New total: {len(updated_df)} rows")
        
        # Show updated E*TRADE Taxable positions
        updated_etrade_taxable = updated_df[updated_df['Account'] == 'E*TRADE Taxable']
        print(f"📋 E*TRADE Taxable now has {len(updated_etrade_taxable)} positions:")
        for _, row in updated_etrade_taxable.iterrows():
            print(f"   {row['Ticker']}: {row['Qty #']} shares")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = add_missing_etrade_taxable_positions()
    if success:
        print("\n🎉 Successfully added missing E*TRADE Taxable positions!")
        print("🔄 Refresh the dividend dashboard to see the complete E*TRADE Taxable data")
    else:
        print("\n❌ Failed to add missing positions")

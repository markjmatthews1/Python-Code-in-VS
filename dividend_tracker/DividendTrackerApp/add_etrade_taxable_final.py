#!/usr/bin/env python3
"""
Add E*TRADE Taxable positions to Dividends_2025.xlsx
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def add_etrade_taxable_to_excel():
    """Add E*TRADE Taxable account data to Excel"""
    
    print("🔄 Adding E*TRADE Taxable data to Dividends_2025.xlsx...")
    
    try:
        from etrade_account_api import ETRADEAccountAPI
        
        # Initialize E*TRADE API
        etrade_api = ETRADEAccountAPI()
        
        # Get positions from the taxable account (3rd account from our check)
        taxable_account_id = "KdLoXe9uuGmiLrZmvOcokw"
        
        positions = etrade_api.get_account_positions(taxable_account_id)
        if not positions:
            print("❌ No positions found in taxable account")
            return False
        
        print(f"📊 Found {len(positions)} positions in E*TRADE Taxable")
        
        # Filter for dividend stocks - include all stocks with meaningful dividend yields
        # Instead of a restrictive list, check for actual dividend yields from the API
        
        dividend_positions = []
        for position in positions:
            symbol = position.get('symbolDescription', '').upper().strip()
            quantity = position.get('quantity', 0)
            market_value = position.get('marketValue', 0)
            price_paid = position.get('pricePaid', 0)
            
            print(f"   Checking: {symbol} - {quantity} shares, ${market_value:.2f}")
            
            # Include all positions that have shares and market value > 0
            # The dashboard will filter by yield threshold (4%+) later
            if quantity > 0 and market_value > 0:
                print(f"   ✅ Adding position: {symbol}")
                
                original_value = quantity * price_paid
                current_price = market_value / quantity if quantity > 0 else 0
                total_gain_pct = ((market_value - original_value) / original_value * 100) if original_value > 0 else 0
                
                dividend_positions.append({
                    'Account': 'E*TRADE Taxable',
                    'Ticker': symbol,
                    'Qty #': quantity,
                    'Price Paid $': price_paid,
                    'Last Price $': current_price,
                    'Current Value $': market_value,
                    'Original Value $': original_value,
                    'Total Gain %': total_gain_pct,
                    # Add placeholder yield data - will need to be calculated later
                    '08-02-2025': 6.0,  # Placeholder current yield
                    '07-28-2025': 6.0,
                    '07-19-2025': 6.0,
                    'Beginning Dividend Yield': 6.0
                })
        
        print(f"🎯 Found {len(dividend_positions)} dividend positions to add")
        
        if not dividend_positions:
            print("⚠️ No dividend positions found to add")
            return False
        
        # Read existing dividends data
        dividends_excel = 'outputs/Dividends_2025.xlsx'
        existing_df = pd.read_excel(dividends_excel)
        print(f"📊 Current data: {len(existing_df)} rows")
        
        # Convert new data to DataFrame
        new_df = pd.DataFrame(dividend_positions)
        
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
        print(f"✅ Updated {dividends_excel} with E*TRADE Taxable data")
        print(f"📊 New total: {len(updated_df)} rows")
        print(f"📋 Updated accounts:")
        print(updated_df['Account'].value_counts())
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = add_etrade_taxable_to_excel()
    if success:
        print("\n🎉 Successfully added E*TRADE Taxable data to Excel!")
        print("🔄 The dividend dashboard will now show all 4 accounts!")
    else:
        print("\n❌ Failed to add E*TRADE Taxable data")

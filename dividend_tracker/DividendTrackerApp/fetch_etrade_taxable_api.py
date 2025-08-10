#!/usr/bin/env python3
"""
Fetch E*TRADE Taxable account data via API and add to Dividends_2025.xlsx
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def fetch_etrade_taxable_and_update_excel():
    """Fetch E*TRADE Taxable account data and add to Excel"""
    
    print("🔄 Fetching E*TRADE Taxable account data via API...")
    
    try:
        from etrade_account_api import ETRADEAccountAPI
        
        # Initialize E*TRADE API
        api = ETRADEAccountAPI()
        
        # Get all accounts
        accounts = api.get_account_list()
        if not accounts:
            print("❌ Failed to get E*TRADE accounts")
            return False
        
        print(f"📊 Found {len(accounts)} E*TRADE accounts")
        
        # Find the Individual Brokerage (Taxable) account
        taxable_account = None
        for account in accounts:
            account_type = account.get('accountDesc', '').lower()
            if 'individual' in account_type or 'brokerage' in account_type:
                taxable_account = account
                break
        
        if not taxable_account:
            print("❌ No E*TRADE Individual/Taxable account found")
            return False
        
        account_key = taxable_account.get('accountIdKey')
        print(f"✅ Found E*TRADE Taxable account: {account_key}")
        
        # Get positions for this account
        positions = api.get_account_positions(account_key)
        if not positions:
            print("❌ Failed to get positions for taxable account")
            return False
        
        print(f"📊 Found {len(positions)} positions in E*TRADE Taxable account")
        
        # Filter for dividend stocks only
        dividend_tickers = ['PDI', 'OFS', 'ABR', 'ACP', 'NHS', 'QDTE', 'AGNC', 'QYLD', 'JEPI', 'JEPQ', 'DIVO', 'SCHD', 'VYM', 'SPHD', 'RYLD', 'SVOL']
        
        taxable_dividend_positions = []
        for position in positions:
            symbol = position.get('symbol', '').upper()
            if symbol in dividend_tickers:
                taxable_dividend_positions.append({
                    'Account': 'E*TRADE Taxable',
                    'Ticker': symbol,
                    'Qty #': position.get('quantity', 0),
                    'Price Paid $': position.get('costPerShare', 0),
                    'Last Price $': position.get('lastPrice', 0),
                    'Current Value $': position.get('marketValue', 0),
                    'Original Value $': position.get('totalCost', 0),
                    'Total Gain %': 0,  # Calculate if needed
                    'Pay Date': '',
                    'Payment cycle': '',
                    'Rate per share': 0,
                    'Original Payment amount': 0,
                    'New Payment amount': 0,
                    'Beginning Dividend Yield': 0,  # Will need to calculate
                })
        
        print(f"🎯 Found {len(taxable_dividend_positions)} dividend positions in E*TRADE Taxable")
        
        if taxable_dividend_positions:
            # Read existing Excel data
            dividends_excel = 'outputs/Dividends_2025.xlsx'
            existing_df = pd.read_excel(dividends_excel)
            
            # Create backup
            backup_file = f'outputs/Dividends_2025_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
            existing_df.to_excel(backup_file, index=False)
            print(f"📁 Backup saved: {backup_file}")
            
            # Add new taxable positions
            new_positions_df = pd.DataFrame(taxable_dividend_positions)
            
            # Make sure we have all the same columns
            for col in existing_df.columns:
                if col not in new_positions_df.columns:
                    new_positions_df[col] = 0.0 if '2025' in col else ''
            
            # Reorder columns to match existing data
            new_positions_df = new_positions_df[existing_df.columns]
            
            # Combine data
            updated_df = pd.concat([existing_df, new_positions_df], ignore_index=True)
            
            # Save updated file
            updated_df.to_excel(dividends_excel, index=False)
            print(f"✅ Updated {dividends_excel} with {len(taxable_dividend_positions)} E*TRADE Taxable positions")
            print(f"📊 New total: {len(updated_df)} rows")
            print(f"📋 Updated accounts: {updated_df['Account'].value_counts()}")
            
            return True
        else:
            print("⚠️ No dividend positions found in E*TRADE Taxable account")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure E*TRADE API modules are available")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == '__main__':
    success = fetch_etrade_taxable_and_update_excel()
    if success:
        print("🎉 Successfully added E*TRADE Taxable data to Excel!")
        print("🔄 The dividend dashboard will now show all 4 accounts")
    else:
        print("❌ Failed to add E*TRADE Taxable data")

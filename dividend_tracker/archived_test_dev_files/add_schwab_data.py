#!/usr/bin/env python3
"""
Add Schwab data to complete all 4 accounts
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

print("🚀 Adding Schwab data to complete 4-account setup...")
print("="*60)

try:
    from schwab_api_integrated import SchwabAPI
    
    # Initialize Schwab API
    schwab_api = SchwabAPI()
    print("✅ Schwab API initialized")
    
    # Get account numbers
    accounts = schwab_api.get_account_numbers()
    print(f"📊 Found {len(accounts)} Schwab accounts: {accounts}")
    
    all_schwab_positions = []
    
    for account_num in accounts:
        print(f"\n📂 Processing Schwab account: {account_num}")
        
        # Get positions for this account
        positions = schwab_api.get_account_positions(account_num)
        print(f"   📊 Found {len(positions)} positions")
        
        for position in positions:
            try:
                # Extract position data
                instrument = position.get('instrument', {})
                symbol = instrument.get('symbol', '').strip().upper()
                quantity = position.get('longQuantity', 0)
                market_value = position.get('marketValue', 0)
                
                if symbol and quantity > 0:
                    # Determine account type (IRA vs Individual)
                    account_type = "Schwab IRA" if "IRA" in str(account_num) else "Schwab Individual"
                    
                    position_data = {
                        'Ticker': symbol,
                        'Account': account_type,
                        'Shares': float(quantity),
                        'Market_Value': float(market_value),
                        'Current_Price': float(market_value) / float(quantity) if quantity > 0 else 0,
                        'Yield': 0.00,  # Will be updated with real dividend data
                        'Annual_Dividend': 0.00,  # Will be calculated
                        'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                    }
                    
                    all_schwab_positions.append(position_data)
                    print(f"     ✅ {symbol}: {quantity} shares (${market_value:,.2f})")
                    
            except Exception as e:
                print(f"     ⚠️ Error processing position: {e}")
                continue
    
    print(f"\n📈 Schwab Summary:")
    print(f"   • Total Schwab positions: {len(all_schwab_positions)}")
    
    # Group by account type
    schwab_ira = [p for p in all_schwab_positions if p['Account'] == 'Schwab IRA']
    schwab_individual = [p for p in all_schwab_positions if p['Account'] == 'Schwab Individual']
    
    print(f"   • Schwab IRA: {len(schwab_ira)} positions")
    print(f"   • Schwab Individual: {len(schwab_individual)} positions")
    
    # Update the Excel file with Schwab data
    if all_schwab_positions:
        print(f"\n📊 Adding Schwab data to Excel file...")
        
        # Read existing data
        dividends_file = os.path.join('outputs', 'Dividends_2025.xlsx')
        
        # Read existing ticker analysis
        existing_df = pd.read_excel(dividends_file, sheet_name='Ticker Analysis 2025 Updated')
        print(f"   📋 Existing data: {len(existing_df)} rows")
        
        # Add Schwab data
        schwab_df = pd.DataFrame(all_schwab_positions)
        
        # Combine data
        combined_df = pd.concat([existing_df, schwab_df], ignore_index=True)
        
        # Sort by account then by ticker
        combined_df = combined_df.sort_values(['Account', 'Ticker'])
        
        print(f"   📊 Combined data: {len(combined_df)} rows")
        print(f"   🎯 Account breakdown:")
        account_counts = combined_df['Account'].value_counts()
        for account, count in account_counts.items():
            print(f"       • {account}: {count} positions")
        
        # Save updated file
        with pd.ExcelWriter(dividends_file, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
            combined_df.to_excel(writer, sheet_name='All 4 Accounts Complete', index=False)
        
        print(f"✅ Updated Excel file with complete 4-account data!")
        print(f"📁 File: {dividends_file}")
        print(f"📋 Sheet: 'All 4 Accounts Complete'")
        
    else:
        print("⚠️ No Schwab positions found")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n🏁 Schwab data addition complete!")

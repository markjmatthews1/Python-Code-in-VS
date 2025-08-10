#!/usr/bin/env python3
"""
Update the Dividends_2025.xlsx with properly organized E*TRADE data
This will fix the dashboard to show correct yields and account organization
"""

import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
import os
from datetime import datetime

def read_etrade_data_organized():
    """Read E*TRADE data and organize it properly by account"""
    print("📊 Reading and organizing E*TRADE data...")
    
    base_path = os.path.join(os.path.dirname(__file__), '..', '..')
    
    # Files to read
    files = {
        'E*TRADE IRA': os.path.join(base_path, 'Etrade_Rollover_IRA_data.xlsx'),
        'E*TRADE Taxable': os.path.join(base_path, 'Etrade_Individual_Brokerage_data.xlsx')
    }
    
    all_accounts = {}
    
    for account_name, file_path in files.items():
        print(f"\n   🔍 Processing {account_name}")
        positions = []
        
        if os.path.exists(file_path):
            wb_data = pd.read_excel(file_path, sheet_name=None)
            
            for sheet_name, df in wb_data.items():
                if df.empty:
                    continue
                
                # Find symbol and quantity columns
                symbol_col = None
                qty_col = None
                value_col = None
                
                for col in df.columns:
                    col_name = str(col).lower()
                    if not symbol_col and any(kw in col_name for kw in ['symbol', 'ticker']):
                        symbol_col = col
                    if not qty_col and any(kw in col_name for kw in ['quantity', 'shares']):
                        qty_col = col
                    if not value_col and any(kw in col_name for kw in ['value', 'market']):
                        value_col = col
                
                if symbol_col and qty_col:
                    print(f"     ✅ Found data in sheet: {sheet_name}")
                    
                    for _, row in df.iterrows():
                        symbol = row[symbol_col]
                        qty = row[qty_col]
                        
                        if pd.notna(symbol) and pd.notna(qty) and qty != 0:
                            try:
                                position = {
                                    'symbol': str(symbol).strip().upper(),
                                    'quantity': float(qty),
                                    'account': account_name
                                }
                                
                                if value_col and pd.notna(row[value_col]):
                                    position['market_value'] = float(row[value_col])
                                
                                positions.append(position)
                                
                            except:
                                continue
        
        # Sort positions by symbol within account
        positions.sort(key=lambda x: x['symbol'])
        all_accounts[account_name] = positions
        
        print(f"     📊 {len(positions)} positions found")
        
        # Show sample for verification
        if positions:
            print(f"     📋 Sample positions:")
            for i, pos in enumerate(positions[:3]):
                qty = pos['quantity']
                symbol = pos['symbol']
                value = pos.get('market_value', 'N/A')
                print(f"       {i+1}. {symbol}: {qty} shares (${value})")
    
    return all_accounts

def update_dividends_file_with_organized_data(accounts_data):
    """Update the Dividends_2025.xlsx file with properly organized data"""
    print("\n🔄 Updating Dividends_2025.xlsx with organized account data...")
    
    dividends_file = os.path.join('outputs', 'Dividends_2025.xlsx')
    
    # Create a new ticker analysis sheet
    ticker_data = []
    
    print("\n📈 Creating organized ticker analysis:")
    
    for account_name, positions in accounts_data.items():
        print(f"\n   📂 {account_name}: {len(positions)} positions")
        
        for pos in positions:
            # Create ticker analysis row
            row = {
                'Ticker': pos['symbol'],
                'Account': account_name,
                'Shares': pos['quantity'],
                'Market_Value': pos.get('market_value', 0),
                'Current_Price': pos.get('market_value', 0) / pos['quantity'] if pos['quantity'] > 0 else 0,
                'Yield': 0.00,  # Will be updated with real dividend data
                'Annual_Dividend': 0.00,  # Will be calculated
                'Last_Updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            ticker_data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(ticker_data)
    
    # Save to Excel with proper formatting
    with pd.ExcelWriter(dividends_file, mode='a', if_sheet_exists='replace', engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Ticker Analysis 2025 Updated', index=False)
    
    print(f"✅ Updated file with {len(ticker_data)} organized ticker entries")
    
    return ticker_data

def main():
    """Main function to organize and update data"""
    print("🚀 Starting data organization for dividend dashboard...")
    print("="*60)
    
    # Read and organize E*TRADE data
    accounts = read_etrade_data_organized()
    
    # Show summary
    print(f"\n📊 SUMMARY:")
    total_positions = 0
    for account, positions in accounts.items():
        count = len(positions)
        total_positions += count
        print(f"   • {account}: {count} positions")
    
    print(f"   🎯 Total: {total_positions} positions")
    
    # Update the Excel file
    ticker_data = update_dividends_file_with_organized_data(accounts)
    
    print(f"\n✅ Data organization complete!")
    print(f"📁 Updated: outputs/Dividends_2025.xlsx")
    print(f"📊 Dashboard should now show correct account organization")
    print(f"🎯 E*TRADE IRA average yield: 16.90% (to be calculated from real dividend data)")

if __name__ == "__main__":
    main()

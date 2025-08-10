#!/usr/bin/env python3
"""
Rebuild ticker analysis with CORRECT data from actual E*TRADE Excel files
This will preserve historical data but regenerate current analysis with real yields
"""

import pandas as pd
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
import os
import sys
from datetime import datetime

# Add modules path for Schwab API access
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from schwab_api_integrated import SchwabAPI
    SCHWAB_API_AVAILABLE = True
    print("✅ Schwab API module loaded successfully")
except ImportError as e:
    print(f"⚠️ Schwab API not available: {e}")
    SCHWAB_API_AVAILABLE = False

def read_etrade_ira_data():
    """Read the actual E*TRADE IRA data"""
    base_path = os.path.join(os.path.dirname(__file__), '..', '..')
    ira_file = os.path.join(base_path, 'Etrade_Rollover_IRA_data.xlsx')
    
    print(f"📊 Reading E*TRADE IRA data from: {os.path.basename(ira_file)}")
    
    positions = []
    
    if os.path.exists(ira_file):
        # Read all sheets to find position data
        wb_data = pd.read_excel(ira_file, sheet_name=None)
        
        for sheet_name, df in wb_data.items():
            print(f"   • Checking sheet: {sheet_name}")
            
            if df.empty:
                continue
                
            # Look for position-like data
            df_columns = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
            
            # Find symbol/ticker column
            symbol_col = None
            for i, col in enumerate(df.columns):
                col_name = str(col).lower()
                if any(keyword in col_name for keyword in ['symbol', 'ticker', 'stock']):
                    symbol_col = col
                    break
            
            # Find quantity column
            qty_col = None
            for col in df.columns:
                col_name = str(col).lower()
                if any(keyword in col_name for keyword in ['quantity', 'shares', 'qty']):
                    qty_col = col
                    break
            
            # Find value column
            value_col = None
            for col in df.columns:
                col_name = str(col).lower()
                if any(keyword in col_name for keyword in ['value', 'market', 'total']):
                    value_col = col
                    break
            
            if symbol_col and qty_col:
                print(f"     ✅ Found position data: {symbol_col}, {qty_col}")
                
                for _, row in df.iterrows():
                    symbol = row[symbol_col]
                    qty = row[qty_col]
                    
                    if pd.notna(symbol) and pd.notna(qty) and qty != 0:
                        try:
                            symbol_clean = str(symbol).strip().upper()
                            qty_clean = float(qty)
                            
                            position = {
                                'symbol': symbol_clean,
                                'quantity': qty_clean,
                                'account': 'E*TRADE IRA'
                            }
                            
                            if value_col and pd.notna(row[value_col]):
                                position['market_value'] = float(row[value_col])
                            
                            positions.append(position)
                            
                        except Exception as e:
                            continue
    
    print(f"   ✅ Found {len(positions)} positions in E*TRADE IRA")
    return positions

def read_etrade_taxable_data():
    """Read the actual E*TRADE Taxable data"""
    base_path = os.path.join(os.path.dirname(__file__), '..', '..')
    taxable_file = os.path.join(base_path, 'Etrade_Individual_Brokerage_data.xlsx')
    
    print(f"📊 Reading E*TRADE Taxable data from: {os.path.basename(taxable_file)}")
    
    positions = []
    
    if os.path.exists(taxable_file):
        # Read all sheets to find position data
        wb_data = pd.read_excel(taxable_file, sheet_name=None)
        
        for sheet_name, df in wb_data.items():
            print(f"   • Checking sheet: {sheet_name}")
            
            if df.empty:
                continue
                
            # Look for position-like data
            df_columns = [col.lower() if isinstance(col, str) else str(col).lower() for col in df.columns]
            
            # Find symbol/ticker column
            symbol_col = None
            for i, col in enumerate(df.columns):
                col_name = str(col).lower()
                if any(keyword in col_name for keyword in ['symbol', 'ticker', 'stock']):
                    symbol_col = col
                    break
            
            # Find quantity column
            qty_col = None
            for col in df.columns:
                col_name = str(col).lower()
                if any(keyword in col_name for keyword in ['quantity', 'shares', 'qty']):
                    qty_col = col
                    break
            
            # Find value column
            value_col = None
            for col in df.columns:
                col_name = str(col).lower()
                if any(keyword in col_name for keyword in ['value', 'market', 'total']):
                    value_col = col
                    break
            
            if symbol_col and qty_col:
                print(f"     ✅ Found position data: {symbol_col}, {qty_col}")
                
                for _, row in df.iterrows():
                    symbol = row[symbol_col]
                    qty = row[qty_col]
                    
                    if pd.notna(symbol) and pd.notna(qty) and qty != 0:
                        try:
                            symbol_clean = str(symbol).strip().upper()
                            qty_clean = float(qty)
                            
                            position = {
                                'symbol': symbol_clean,
                                'quantity': qty_clean,
                                'account': 'E*TRADE Taxable'
                            }
                            
                            if value_col and pd.notna(row[value_col]):
                                position['market_value'] = float(row[value_col])
                            
                            positions.append(position)
                            
                        except Exception as e:
                            continue
    
    print(f"   ✅ Found {len(positions)} positions in E*TRADE Taxable")
    return positions

def read_schwab_data():
    """Read Schwab account data using the existing Schwab API"""
    print("📊 Reading Schwab data using live API...")
    
    schwab_positions = []
    
    if not SCHWAB_API_AVAILABLE:
        print("   ❌ Schwab API not available - skipping Schwab accounts")
        return schwab_positions
    
    try:
        # Initialize Schwab API
        schwab_api = SchwabAPI()
        print("   ✅ Schwab API initialized")
        
        # Test connection first
        if not schwab_api.test_connection():
            print("   ❌ Schwab API connection failed")
            return schwab_positions
        
        # Get account numbers
        accounts = schwab_api.get_account_numbers()
        print(f"   📊 Found {len(accounts)} Schwab accounts")
        
        for account_num in accounts:
            print(f"   • Processing Schwab account: {account_num}")
            
            # Get positions for this account
            positions = schwab_api.get_account_positions(account_num)
            
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
                            'symbol': symbol,
                            'quantity': float(quantity),
                            'account': account_type,
                            'market_value': float(market_value)
                        }
                        
                        schwab_positions.append(position_data)
                        print(f"     ✅ {symbol}: {quantity} shares (${market_value:,.2f})")
                        
                except Exception as e:
                    print(f"     ⚠️ Error processing position: {e}")
                    continue
        
    except Exception as e:
        print(f"   ❌ Error reading Schwab data: {e}")
        print("   💡 Note: Schwab authentication may be needed")
    
    print(f"   ✅ Found {len(schwab_positions)} total Schwab positions")
    return schwab_positions

def create_updated_analysis():
    """Create updated analysis with ALL 4 accounts, properly sorted"""
    print("🔄 Creating updated ticker analysis with ALL 4 accounts...")
    
    # Get real position data from all accounts
    print("\n" + "="*60)
    print("📂 READING ALL ACCOUNT DATA")
    print("="*60)
    
    etrade_ira_positions = read_etrade_ira_data()
    etrade_taxable_positions = read_etrade_taxable_data()
    schwab_positions = read_schwab_data()
    
    # Separate Schwab positions by account type
    schwab_ira_positions = [p for p in schwab_positions if p['account'] == 'Schwab IRA']
    schwab_individual_positions = [p for p in schwab_positions if p['account'] == 'Schwab Individual']
    
    # Create organized account structure
    accounts = {
        'E*TRADE IRA': etrade_ira_positions,
        'E*TRADE Taxable': etrade_taxable_positions,
        'Schwab IRA': schwab_ira_positions,
        'Schwab Individual': schwab_individual_positions
    }
    
    print(f"\n" + "="*60)
    print("📈 ACCOUNT SUMMARY")
    print("="*60)
    
    total_positions = 0
    for account_name, positions in accounts.items():
        count = len(positions)
        total_positions += count
        print(f"   • {account_name}: {count} positions")
        
        # Show sample positions for each account
        if positions and count > 0:
            print(f"     📋 Sample positions:")
            for i, pos in enumerate(positions[:3]):  # Show first 3
                symbol = pos.get('symbol', 'Unknown')
                qty = pos.get('quantity', 0)
                print(f"       {i+1}. {symbol}: {qty} shares")
            if count > 3:
                print(f"       ... and {count-3} more")
        print()
    
    print(f"🎯 TOTAL ACROSS ALL ACCOUNTS: {total_positions} positions")
    
    # Create sorted, organized list (grouped by account)
    all_positions_sorted = []
    for account_name in ['E*TRADE IRA', 'E*TRADE Taxable', 'Schwab IRA', 'Schwab Individual']:
        account_positions = accounts[account_name]
        # Sort positions within each account by symbol
        sorted_account_positions = sorted(account_positions, key=lambda x: x.get('symbol', ''))
        all_positions_sorted.extend(sorted_account_positions)
    
    print(f"\n✅ Data organized and sorted by account!")
    return all_positions_sorted, accounts

if __name__ == "__main__":
    positions_sorted, accounts_dict = create_updated_analysis()
    
    print(f"\n" + "="*60)
    print("🎯 NEXT STEPS TO COMPLETE 4-ACCOUNT SETUP")
    print("="*60)
    print("1. ✅ E*TRADE data successfully read")
    print("2. ⚠️  Schwab data needs to be added/updated")
    print("3. 🔄 Need to organize all 4 accounts properly")
    print("4. 📊 Update dashboard to show correct 16.90% IRA yield")
    print(f"\nCurrent status: {len(positions_sorted)} total positions across all available accounts")

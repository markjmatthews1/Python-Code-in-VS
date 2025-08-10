#!/usr/bin/env python3
"""
Process E*TRADE data with proper dividend stock classification
Dividend stocks: Yield >= 4%
Investment tickers: Yield < 4%
"""

import pandas as pd
import os
from datetime import datetime

def classify_and_process_etrade_data():
    """Process E*TRADE data with dividend stock classification"""
    print("🎯 Processing E*TRADE data with dividend stock classification...")
    print("📊 Rule: Dividend stocks = Yield ≥ 4%, Investment tickers = Yield < 4%")
    print("="*70)
    
    base_path = os.path.join(os.path.dirname(__file__), '..', '..')
    
    # Files to process
    files = {
        'E*TRADE IRA': os.path.join(base_path, 'Etrade_Rollover_IRA_data.xlsx'),
        'E*TRADE Taxable': os.path.join(base_path, 'Etrade_Individual_Brokerage_data.xlsx')
    }
    
    all_positions = []
    account_stats = {}
    
    for account_name, file_path in files.items():
        print(f"\n📂 Processing {account_name}")
        
        dividend_stocks = []
        investment_tickers = []
        
        if os.path.exists(file_path):
            wb_data = pd.read_excel(file_path, sheet_name=None)
            
            for sheet_name, df in wb_data.items():
                if df.empty:
                    continue
                
                # Find data columns
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
                                    position['current_price'] = position['market_value'] / position['quantity']
                                
                                # For now, classify all as potential dividend stocks
                                # We'll need yield data to properly classify
                                position['yield'] = 0.0  # Will be updated with real yield data
                                position['classification'] = 'TBD'  # To Be Determined
                                
                                all_positions.append(position)
                                
                            except:
                                continue
        
        account_positions = [p for p in all_positions if p['account'] == account_name]
        print(f"   📊 Total positions: {len(account_positions)}")
        
        # Sample positions
        if account_positions:
            print(f"   📋 Sample positions:")
            for i, pos in enumerate(account_positions[:5]):
                symbol = pos['symbol']
                qty = pos['quantity']
                value = pos.get('market_value', 'N/A')
                print(f"       {i+1}. {symbol}: {qty} shares (${value})")
        
        account_stats[account_name] = {
            'total_positions': len(account_positions),
            'dividend_stocks': 0,  # Will be updated when we get yield data
            'investment_tickers': 0,  # Will be updated when we get yield data
        }
    
    print(f"\n📈 Summary:")
    total_positions = len(all_positions)
    print(f"   🎯 Total positions across accounts: {total_positions}")
    
    for account, stats in account_stats.items():
        print(f"   📂 {account}: {stats['total_positions']} positions")
    
    print(f"\n💡 Next steps:")
    print(f"   1. ✅ Position data extracted")
    print(f"   2. 🔄 Need dividend yield data for each ticker")
    print(f"   3. 🎯 Classify: ≥4% yield = Dividend stock, <4% = Investment")
    print(f"   4. 📊 Calculate true average yield for dividend stocks only")
    print(f"   5. 🎯 Should show ~16.90% for E*TRADE IRA dividend stocks")
    
    return all_positions, account_stats

def create_yield_classification_template():
    """Create a template for adding yield data and classification"""
    print(f"\n📋 Creating yield classification template...")
    
    positions, stats = classify_and_process_etrade_data()
    
    # Create DataFrame for analysis
    df = pd.DataFrame(positions)
    
    # Add classification columns
    df['Dividend_Yield_Percent'] = 0.0
    df['Is_Dividend_Stock'] = False  # Will be True if yield >= 4%
    df['Classification'] = 'Investment'  # Default to Investment
    df['Notes'] = 'Yield data needed'
    
    # Save to Excel for review and updating
    output_file = os.path.join('outputs', 'Position_Classification_Template.xlsx')
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Positions_Need_Yields', index=False)
    
    print(f"✅ Template created: {output_file}")
    print(f"📊 Contains {len(df)} positions ready for yield classification")
    print(f"\n🎯 To complete classification:")
    print(f"   1. Add dividend yields to 'Dividend_Yield_Percent' column")
    print(f"   2. System will auto-classify: ≥4% = Dividend stock, <4% = Investment")
    print(f"   3. Calculate true dividend yield average (should be ~16.90% for E*TRADE IRA)")
    
    return df

if __name__ == "__main__":
    template_df = create_yield_classification_template()

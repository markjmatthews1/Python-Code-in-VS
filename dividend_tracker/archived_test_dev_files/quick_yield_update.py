#!/usr/bin/env python3
"""
Quick update dividend yields based on E*TRADE screenshot data
"""

import pandas as pd
from datetime import datetime

# Dividend yields from your E*TRADE Individual Brokerage screenshot
etrade_yields = {
    'ABR': 10.71,
    'ACP': 15.60, 
    'AGNC': 15.19,
    'ARI': 10.22,
    'BITO': 53.41,
    'EIC': 12.26,
    'MORT': 12.56,
    'OFS': 16.39,
    'PDI': 13.77,
    'QDTE': 8.24,
    'QYLD': 12.52,
    'RYLD': 13.10
}

def quick_yield_update():
    print("🔄 Quick dividend yield update...")
    
    try:
        df = pd.read_excel('outputs/Dividends_2025.xlsx')
        print(f"📊 Processing {len(df)} positions")
        
        # Backup
        backup = f'outputs/Dividends_2025_backup_quick_yield_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
        df.to_excel(backup, index=False)
        
        # Update yields
        for index, row in df.iterrows():
            ticker = str(row['Ticker']).upper().strip()
            if ticker in etrade_yields:
                yield_val = etrade_yields[ticker]
                df.at[index, '08-02-2025'] = yield_val
                df.at[index, '07-28-2025'] = yield_val
                df.at[index, '07-19-2025'] = yield_val
                df.at[index, 'Beginning Dividend Yield'] = yield_val
                print(f"Updated {ticker}: {yield_val}%")
        
        # Save
        df.to_excel('outputs/Dividends_2025.xlsx', index=False)
        print("✅ Yield data updated!")
        
        # Show dividend stocks
        dividend_stocks = df[pd.to_numeric(df['08-02-2025'], errors='coerce') >= 4.0]
        print(f"🎯 {len(dividend_stocks)} stocks with ≥4% yield")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == '__main__':
    quick_yield_update()

import pandas as pd
import sys

try:
    # Load the Excel file and see what sheets exist
    xl_file = pd.ExcelFile('outputs/Dividends_2025.xlsx')
    print('📊 Available sheets in Dividends_2025.xlsx:')
    for sheet in xl_file.sheet_names:
        print(f'  • {sheet}')
    
    # Check if Portfolio Values 2025 sheet exists
    if 'Portfolio Values 2025' in xl_file.sheet_names:
        print('\n📈 Loading Portfolio Values 2025 sheet...')
        df = pd.read_excel('outputs/Dividends_2025.xlsx', sheet_name='Portfolio Values 2025')
        print(f'Shape: {df.shape}')
        print('\nColumns:', list(df.columns))
        print('\nFirst few rows:')
        print(df.head())
        
        # Show last few rows to see latest data
        print('\nLast few rows:')
        print(df.tail())
    else:
        print('\n❌ Portfolio Values 2025 sheet not found')
        
except Exception as e:
    print(f'❌ Error: {e}')
    import traceback
    traceback.print_exc()

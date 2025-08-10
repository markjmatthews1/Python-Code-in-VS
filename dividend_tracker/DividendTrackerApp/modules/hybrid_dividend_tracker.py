r"""
Module: hybrid_dividend_tracker.py
Author: Mark
Created: July 26, 2025
Purpose: Hybrid approach - API positions + Excel dividend estimates
Location: C:\Python_Projects\DividendTrackerApp\modules\hybrid_dividend_tracker.py
"""

import pandas as pd
from datetime import datetime
from modules.etrade_account_api import ETRADEAccountAPI
from modules.estimated_income_tracker import load_estimate_files

def get_hybrid_dividend_data():
    """
    Hybrid approach: Get positions from API and dividend estimates from Excel
    Cross-reference to ensure accuracy
    """
    print("🔄 Using hybrid approach: API positions + Excel dividend estimates")
    
    # Get current positions from API
    try:
        api = ETRADEAccountAPI()
        api_account_data = api.get_dividend_estimates()
        print("✅ Successfully retrieved API position data")
    except Exception as e:
        print(f"❌ Error getting API data: {e}")
        print("📄 Falling back to Excel-only data")
        return load_estimate_files(use_api=False)
    
    # Get dividend estimates from Excel files
    try:
        excel_account_data = load_estimate_files(use_api=False)
        print("✅ Successfully loaded Excel dividend estimates")
    except Exception as e:
        print(f"❌ Error loading Excel data: {e}")
        return api_account_data
    
    # Cross-reference and merge the data
    merged_data = {}
    
    for account_type in excel_account_data.keys():
        print(f"🔄 Processing {account_type}...")
        
        excel_df = excel_account_data[account_type]
        
        # Get API positions for this account if available
        api_positions = []
        if account_type in api_account_data:
            api_df = api_account_data[account_type]
            api_positions = api_df['Symbol'].tolist() if 'Symbol' in api_df.columns else []
        
        # Create a comparison report
        excel_symbols = set(excel_df['Symbol'].tolist())
        api_symbols = set(api_positions)
        
        print(f"  📊 Excel symbols: {len(excel_symbols)}")
        print(f"  📊 API symbols: {len(api_symbols)}")
        
        # Find differences
        only_in_excel = excel_symbols - api_symbols
        only_in_api = api_symbols - excel_symbols
        common_symbols = excel_symbols & api_symbols
        
        print(f"  📊 Excel symbols: {len(excel_symbols)}")
        print(f"  📊 API symbols: {len(api_symbols)}")
        print(f"  ✅ Common symbols: {len(common_symbols)}")
        
        if only_in_excel:
            print(f"  🔴 SOLD POSITIONS ({len(only_in_excel)}): {sorted(list(only_in_excel))}")
            # Calculate lost dividend income from sold positions
            sold_df = excel_df[excel_df['Symbol'].isin(only_in_excel)]
            lost_income = sold_df['Est. Income $'].sum()
            print(f"     💰 Lost dividend income: ${lost_income:.2f}")
            
        if only_in_api:
            print(f"  🟢 NEW PURCHASES ({len(only_in_api)}): {sorted(list(only_in_api))}")
            print(f"     ⚠️ These new positions need dividend estimates added to Excel files")
            
        validation_rate = len(common_symbols) / len(excel_symbols) * 100 if excel_symbols else 0
        print(f"  📈 Portfolio validation rate: {validation_rate:.1f}%")
        
        # Use Excel data (which has dividend estimates) as the primary source
        # but add validation flags and remove sold positions
        excel_df_copy = excel_df.copy()
        
        # Add validation flags
        excel_df_copy['API_Validated'] = excel_df_copy['Symbol'].isin(api_symbols)
        excel_df_copy['Data_Source'] = 'Excel_with_API_validation'
        
        # Mark positions that have been sold
        excel_df_copy['Position_Status'] = excel_df_copy['Symbol'].apply(
            lambda x: 'SOLD - REMOVE FROM ESTIMATES' if x in only_in_excel else 'ACTIVE'
        )
        
        # Filter out sold positions for accurate current estimates
        active_positions = excel_df_copy[excel_df_copy['Position_Status'] == 'ACTIVE'].copy()
        
        # Create summary of changes
        if only_in_excel or only_in_api:
            print(f"\n📊 PORTFOLIO CHANGES DETECTED for {account_type}:")
            
            if only_in_excel:
                sold_income = excel_df_copy[excel_df_copy['Position_Status'] != 'ACTIVE']['Est. Income $'].sum()
                print(f"  🔴 REMOVED from estimates: ${sold_income:.2f} (sold positions)")
                
            if only_in_api:
                print(f"  🟢 NEW positions need dividend research: {list(only_in_api)}")
                print(f"     💡 Tip: Add these to your Excel files for complete tracking")
        
        merged_data[account_type] = active_positions  # Use only active positions
    
    return merged_data

if __name__ == "__main__":
    # Test the hybrid approach
    data = get_hybrid_dividend_data()
    
    for account_type, df in data.items():
        print(f"\n📊 {account_type} Summary:")
        print(f"  Total positions: {len(df)}")
        if 'API_Validated' in df.columns:
            validated_count = df['API_Validated'].sum()
            print(f"  API validated: {validated_count}")
            print(f"  Validation rate: {validated_count/len(df)*100:.1f}%")
        if 'Est. Income $' in df.columns:
            total_income = df['Est. Income $'].sum()
            print(f"  Total estimated income: ${total_income:.2f}")

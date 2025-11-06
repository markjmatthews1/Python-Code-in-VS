import openpyxl
import json
from datetime import datetime

def examine_portfolio_summary():
    """Debug Portfolio Summary sheet values vs cache data"""
    print("PORTFOLIO SUMMARY DEBUG")
    print("=" * 40)
    
    # Check Excel sheet values
    print("\n1. CURRENT EXCEL VALUES:")
    try:
        wb = openpyxl.load_workbook('outputs/Dividends_2025.xlsx')
        ws = wb['Portfolio Summary']
        
        # Look for key account values in the sheet
        for row in range(1, 30):
            row_values = []
            has_content = False
            for col in range(1, 6):
                cell_value = ws.cell(row=row, column=col).value
                if cell_value is not None:
                    row_values.append(str(cell_value))
                    has_content = True
                else:
                    row_values.append("")
            
            if has_content and any(keyword in ' '.join(row_values).upper() for keyword in 
                                  ['ETRADE', 'SCHWAB', '401K', 'TOTAL', 'PORTFOLIO', 'IRA', 'TAXABLE']):
                print(f"  Row {row}: {' | '.join(row_values)}")
        
        wb.close()
        
    except Exception as e:
        print(f"  ERROR reading Excel: {e}")
    
    # Check cache data
    print("\n2. CACHE DATA VALUES:")
    try:
        with open('portfolio_data_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        timestamp = cache_data.get('timestamp', 'Unknown')
        print(f"  Cache timestamp: {timestamp}")
        
        portfolio_values = cache_data.get('portfolio_values', {})
        print("  Portfolio Values from cache:")
        for account, value in portfolio_values.items():
            print(f"    {account}: ${value:,.2f}")
        
        # Calculate totals
        positions_data = cache_data.get('positions', {})
        calculated_totals = {}
        for account, positions in positions_data.items():
            total = sum(pos.get('market_value', 0) for pos in positions)
            calculated_totals[account] = total
            print(f"  {account} (calculated): ${total:,.2f}")
            
    except Exception as e:
        print(f"  ERROR reading cache: {e}")
    
    # Test portfolio summary updater calculation
    print("\n3. PORTFOLIO SUMMARY UPDATER TEST:")
    try:
        from portfolio_summary_updater import PortfolioSummaryUpdater
        
        updater = PortfolioSummaryUpdater()
        cache_data = updater.load_cache_data()
        
        if cache_data:
            values = updater.get_portfolio_values(cache_data)
            print("  Calculated values from updater:")
            for key, value in values.items():
                print(f"    {key}: ${value:,.2f}")
        else:
            print("  ERROR: Could not load cache data")
            
    except Exception as e:
        print(f"  ERROR testing updater: {e}")

if __name__ == "__main__":
    examine_portfolio_summary()
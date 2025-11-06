import os
import sys
import json
from datetime import datetime

# Add modules to path  
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_portfolio_data():
    """Check what portfolio_data_collector returns"""
    try:
        from portfolio_data_collector import PortfolioDataCollector
        
        collector = PortfolioDataCollector()
        k401_value = 128693.17
        
        print("TESTING PORTFOLIO DATA COLLECTOR")
        print("=" * 50)
        
        # Get fresh data like the main updater does
        fresh_data = collector.collect_all_data_with_fallback(k401_value)
        
        if fresh_data:
            print("FRESH DATA KEYS:")
            for key in fresh_data.keys():
                print(f"  {key}: {type(fresh_data[key])}")
                
            print(f"\nTOTALS:")
            totals = fresh_data.get('totals', {})
            for key, value in totals.items():
                print(f"  {key}: {value}")
                
            print(f"\nPORTFOLIO VALUES:")
            portfolio_values = fresh_data.get('portfolio_values', {})
            total_portfolio = 0
            for account, value in portfolio_values.items():
                print(f"  {account}: ${value:,.2f}")
                total_portfolio += value
                
            print(f"\nCALCULATION CHECK:")
            print(f"  Sum of portfolio_values: ${total_portfolio:,.2f}")
            print(f"  401k value: ${k401_value:,.2f}")
            print(f"  Expected total: ${total_portfolio + k401_value:,.2f}")
            print(f"  Totals['total_portfolio']: ${totals.get('total_portfolio', 0):,.2f}")
            
        else:
            print("ERROR: No fresh data returned")
            
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_portfolio_data()
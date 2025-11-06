import os
import sys
from datetime import datetime

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_401k_handling():
    """Test 401k value handling in isolation"""
    
    # Simulate the 401k value you entered
    k401_value = 128693.17
    
    # Simulate portfolio values from API
    portfolio_values = {
        'E*TRADE IRA': 289870.9963,
        'E*TRADE Taxable': 65093.35,
        'Schwab IRA': 51929.91,
        'Schwab Individual': 2660.97
    }
    
    print("401K VALUE TEST")
    print("=" * 50)
    print(f"401k value entered: ${k401_value:,.2f}")
    print(f"Portfolio sum: ${sum(portfolio_values.values()):,.2f}")
    print(f"Expected total: ${sum(portfolio_values.values()) + k401_value:,.2f}")
    
    # Test account mapping
    account_mapping = {
        'E*TRADE IRA': portfolio_values.get('E*TRADE IRA', 0),
        'E*TRADE Taxable': portfolio_values.get('E*TRADE Taxable', 0),
        'Schwab IRA': portfolio_values.get('Schwab IRA', 0),
        'Schwab Individual': portfolio_values.get('Schwab Individual', 0),
        '401k Retirement (Manual)': k401_value  # Match exact Excel label
    }
    
    print("\nACCOUNT MAPPING:")
    for account, value in account_mapping.items():
        print(f"  {account}: ${value:,.2f}")
    
    # Test the matching logic
    test_keys = [
        'E*TRADE IRA',
        'E*TRADE Taxable', 
        'Schwab IRA',
        'Schwab Individual',
        '401k Retirement (Manual)',
        'TOTAL PORTFOLIO'
    ]
    
    print("\nMATCHING LOGIC TEST:")
    for account_key in test_keys:
        value = None
        match_reason = ""
        
        if account_key in account_mapping:
            value = account_mapping[account_key]
            match_reason = "Exact match"
        elif 'total' in account_key.lower():
            value = sum(portfolio_values.values()) + k401_value
            match_reason = f"Total calculation ({sum(portfolio_values.values()):,.2f} + {k401_value:,.2f})"
        elif any(partial in account_key for partial in ['E*TRADE', 'Etrade', 'Schwab']):
            for map_key, map_value in account_mapping.items():
                if map_key.replace('*', '') in account_key or map_key in account_key:
                    value = map_value
                    match_reason = f"Partial match to '{map_key}'"
                    break
        elif '401k' in account_key.lower() or '401' in account_key:
            value = k401_value
            match_reason = "401k match"
        
        if value is not None:
            print(f"  '{account_key}': ${value:,.2f} ({match_reason})")
        else:
            print(f"  '{account_key}': NO MATCH FOUND")

if __name__ == "__main__":
    test_401k_handling()
import os
import sys
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.styles.numbers import FORMAT_CURRENCY_USD_SIMPLE
from datetime import datetime

def test_total_fix():
    """Test the fixed total calculation"""
    
    # Simulate the correct data structure (with 401K already included)
    portfolio_values = {
        'E*TRADE IRA': 289870.9963,
        'E*TRADE Taxable': 65093.35,
        'Schwab Individual': 2660.97,
        'Schwab IRA': 51929.91,
        '401K': 128693.17
    }
    
    k401_value = 128693.17
    
    print("TOTAL CALCULATION TEST")
    print("=" * 50)
    print("Portfolio Values (with 401K already included):")
    for account, value in portfolio_values.items():
        print(f"  {account}: ${value:,.2f}")
        
    print(f"\nOLD CALCULATION (WRONG):")
    old_total = sum(portfolio_values.values()) + k401_value
    print(f"  sum(portfolio_values) + k401_value = ${sum(portfolio_values.values()):,.2f} + ${k401_value:,.2f} = ${old_total:,.2f}")
    print("  ❌ This double-counts the 401K!")
    
    print(f"\nNEW CALCULATION (CORRECT):")
    new_total = sum(portfolio_values.values())
    print(f"  sum(portfolio_values) = ${new_total:,.2f}")
    print("  ✅ 401K already included, no double-counting!")
    
    print(f"\nCOMPARISON:")
    print(f"  Old (wrong) total: ${old_total:,.2f}")
    print(f"  New (correct) total: ${new_total:,.2f}")
    print(f"  Difference: ${old_total - new_total:,.2f}")

if __name__ == "__main__":
    test_total_fix()
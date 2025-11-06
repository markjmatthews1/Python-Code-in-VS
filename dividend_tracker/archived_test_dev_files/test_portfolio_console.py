#!/usr/bin/env python3
"""
Test Portfolio Update with Console Input for 401K
"""

import sys
import os

# Add modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

from enhanced_portfolio_updater import EnhancedPortfolioUpdater

def main():
    print("Portfolio Update Console Test")
    print("=" * 40)
    
    updater = EnhancedPortfolioUpdater()
    
    # Get 401K value from console input
    k401_value = input("Enter your 401K value: $").strip()
    try:
        k401_value = float(k401_value.replace(',', ''))
        print(f"You entered: ${k401_value:,.2f}")
    except ValueError:
        print("Invalid input, using 0")
        k401_value = 0.0
    
    print("\n" + "=" * 50)
    print("PORTFOLIO UPDATE TEST")
    print("=" * 50)
    
    # Test the portfolio update with real values
    success = updater.update_portfolio_values_enhanced(k401_value)
    
    if success:
        print(f"\n✅ Portfolio update successful!")
        print(f"401K value used: ${k401_value:,.2f}")
    else:
        print(f"\n❌ Portfolio update failed")

if __name__ == "__main__":
    main()

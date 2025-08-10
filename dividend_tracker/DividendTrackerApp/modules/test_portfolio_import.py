#!/usr/bin/env python3
"""
Test import of portfolio history manager
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    from portfolio_history_manager import PortfolioHistoryManager
    print("✅ PortfolioHistoryManager imported successfully")
    
    # Test creation
    manager = PortfolioHistoryManager()
    print("✅ PortfolioHistoryManager created successfully")
    
    # Test getting summary
    summary = manager.get_portfolio_summary_for_week()
    if summary:
        print("✅ Portfolio summary retrieved:")
        for account, value in summary.items():
            print(f"  {account}: ${value:,.2f}")
    else:
        print("⚠️ No portfolio summary found")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

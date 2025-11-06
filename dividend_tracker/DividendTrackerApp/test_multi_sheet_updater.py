#!/usr/bin/env python3
"""
Quick test of the new multi-sheet updater
"""

import sys
import os

# Add path
sys.path.append(os.path.dirname(__file__))

from multi_sheet_historical_yield_updater import MultiSheetHistoricalYieldUpdater

if __name__ == "__main__":
    print("🧪 TESTING MULTI-SHEET HISTORICAL YIELD UPDATER")
    print("=" * 70)
    print()
    
    updater = MultiSheetHistoricalYieldUpdater()
    success = updater.run_update()
    
    if success:
        print("\n✅ TEST PASSED - Multi-sheet updater working correctly!")
    else:
        print("\n❌ TEST FAILED - Check errors above")

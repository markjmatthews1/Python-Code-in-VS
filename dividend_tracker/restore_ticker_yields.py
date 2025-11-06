#!/usr/bin/env python3
"""
Restore Ticker Yields to Consolidated Cache
==========================================

This script restores the ticker yield data from the backup to the consolidated cache.
The consolidated cache was missing the ticker_yields data, causing the system to fail.
"""

import json
import os

def restore_ticker_yields():
    """Restore ticker yields to consolidated cache from backup"""
    
    # File paths
    backup_file = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\cache_backups\ticker_yields_backup_20250906_150907.json"
    consolidated_cache = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp\portfolio_data_cache.json"
    
    print("🔧 RESTORING TICKER YIELDS TO CONSOLIDATED CACHE")
    print("=" * 60)
    
    # Load backup data
    if not os.path.exists(backup_file):
        print(f"❌ Backup file not found: {backup_file}")
        return False
    
    with open(backup_file, 'r') as f:
        backup_data = json.load(f)
    
    ticker_yields = backup_data.get('tickers', {})
    print(f"📊 Loaded {len(ticker_yields)} tickers from backup")
    
    # Load consolidated cache
    if not os.path.exists(consolidated_cache):
        print(f"❌ Consolidated cache not found: {consolidated_cache}")
        return False
    
    with open(consolidated_cache, 'r') as f:
        cache_data = json.load(f)
    
    print(f"📊 Current consolidated cache has {len(cache_data.get('ticker_yields', {}))} ticker yields")
    
    # Update ticker yields section
    cache_data['ticker_yields'] = ticker_yields
    
    # Save updated cache
    with open(consolidated_cache, 'w') as f:
        json.dump(cache_data, f, indent=2)
    
    print(f"✅ Updated consolidated cache with {len(ticker_yields)} ticker yields")
    
    # Verify the update
    with open(consolidated_cache, 'r') as f:
        updated_data = json.load(f)
    
    updated_yields = updated_data.get('ticker_yields', {})
    dividend_count = len([t for t in updated_yields.values() if t.get('has_dividend', False)])
    
    print(f"🔍 Verification: {len(updated_yields)} tickers ({dividend_count} with dividends)")
    return True

if __name__ == "__main__":
    success = restore_ticker_yields()
    if success:
        print("\n🎉 Ticker yields successfully restored to consolidated cache!")
        print("✅ The dividend tracker system should now work properly")
    else:
        print("\n❌ Failed to restore ticker yields")

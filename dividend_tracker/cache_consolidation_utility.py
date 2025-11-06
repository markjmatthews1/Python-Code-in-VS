#!/usr/bin/env python3
"""
Cache Consolidation Utility
============================

This script helps consolidate the dual cache system by:
1. Verifying that portfolio_data_cache.json has all ticker yield data
2. Providing safe backup and migration tools
3. Testing that all systems work with consolidated cache
4. Safely removing legacy ticker_yields.json file

Usage:
    python cache_consolidation_utility.py --verify
    python cache_consolidation_utility.py --migrate  
    python cache_consolidation_utility.py --cleanup

"""

import json
import os
import shutil
from datetime import datetime
import sys

class CacheConsolidator:
    def __init__(self):
        self.main_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.dirname(self.main_dir)
        
        # Cache file paths
        self.legacy_cache = os.path.join(self.parent_dir, "ticker_yields.json")
        self.consolidated_cache = os.path.join(self.main_dir, "DividendTrackerApp", "portfolio_data_cache.json")
        
        # Backup directory
        self.backup_dir = os.path.join(self.main_dir, "cache_backups")
        os.makedirs(self.backup_dir, exist_ok=True)
        
    def verify_cache_data(self):
        """Verify that consolidated cache has all the data from legacy cache"""
        print("🔍 CACHE VERIFICATION")
        print("=" * 50)
        
        # Load legacy cache
        legacy_data = {}
        if os.path.exists(self.legacy_cache):
            with open(self.legacy_cache, 'r') as f:
                legacy_file = json.load(f)
                legacy_data = legacy_file.get('tickers', {})
            print(f"📊 Legacy cache: {len(legacy_data)} tickers")
        else:
            print("⚠️ Legacy ticker_yields.json not found")
            return True
        
        # Load consolidated cache
        consolidated_data = {}
        if os.path.exists(self.consolidated_cache):
            with open(self.consolidated_cache, 'r') as f:
                consolidated_file = json.load(f)
                consolidated_data = consolidated_file.get('ticker_yields', {})
            print(f"📊 Consolidated cache: {len(consolidated_data)} tickers")
        else:
            print("❌ Consolidated portfolio_data_cache.json not found")
            return False
        
        # Compare data
        missing_tickers = []
        data_mismatches = []
        
        for ticker, legacy_info in legacy_data.items():
            if ticker not in consolidated_data:
                missing_tickers.append(ticker)
            else:
                # Compare key fields
                consolidated_info = consolidated_data[ticker]
                for key in ['yield', 'dividend_amount', 'annual_dividend', 'has_dividend']:
                    if legacy_info.get(key) != consolidated_info.get(key):
                        data_mismatches.append(f"{ticker}.{key}: {legacy_info.get(key)} != {consolidated_info.get(key)}")
        
        # Results
        print(f"\n📋 VERIFICATION RESULTS:")
        if missing_tickers:
            print(f"❌ Missing tickers in consolidated cache: {missing_tickers}")
        if data_mismatches:
            print(f"⚠️ Data mismatches found:")
            for mismatch in data_mismatches[:5]:  # Show first 5
                print(f"   • {mismatch}")
        
        if not missing_tickers and not data_mismatches:
            print("✅ All ticker data matches! Consolidation is safe.")
            return True
        else:
            print(f"⚠️ Found {len(missing_tickers)} missing tickers and {len(data_mismatches)} mismatches")
            return False
    
    def backup_legacy_cache(self):
        """Create backup of legacy cache before deletion"""
        if not os.path.exists(self.legacy_cache):
            print("⚠️ No legacy cache file to backup")
            return True
            
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.backup_dir, f"ticker_yields_backup_{timestamp}.json")
        
        try:
            shutil.copy2(self.legacy_cache, backup_file)
            print(f"✅ Legacy cache backed up to: {backup_file}")
            return True
        except Exception as e:
            print(f"❌ Backup failed: {e}")
            return False
    
    def test_updated_system(self):
        """Test that updated system can load ticker yields"""
        print("\n🧪 TESTING UPDATED SYSTEM")
        print("=" * 50)
        
        # Test portfolio_data_collector
        try:
            sys.path.append(os.path.join(self.main_dir, "DividendTrackerApp"))
            from portfolio_data_collector import PortfolioDataCollector
            
            collector = PortfolioDataCollector()
            ticker_yields = collector.load_ticker_yields()
            
            if ticker_yields:
                print(f"✅ PortfolioDataCollector: Loaded {len(ticker_yields)} tickers")
            else:
                print("❌ PortfolioDataCollector: No ticker yields loaded")
                
        except Exception as e:
            print(f"❌ PortfolioDataCollector test failed: {e}")
        
        # Test enhanced_portfolio_updater
        try:
            from enhanced_portfolio_updater_with_schwab import EnhancedPortfolioUpdater
            
            # Constructor takes no arguments
            updater = EnhancedPortfolioUpdater()
            ticker_yields = updater.load_ticker_yields()
            
            if ticker_yields:
                print(f"✅ EnhancedPortfolioUpdater: Loaded {len(ticker_yields)} tickers")
            else:
                print("❌ EnhancedPortfolioUpdater: No ticker yields loaded")
                
        except Exception as e:
            print(f"❌ EnhancedPortfolioUpdater test failed: {e}")
    
    def safe_cleanup(self):
        """Safely remove legacy cache file after verification"""
        print("\n🗑️ SAFE CLEANUP")
        print("=" * 50)
        
        # Final verification
        if not self.verify_cache_data():
            print("❌ Verification failed. Aborting cleanup for safety.")
            return False
        
        # Backup first
        if not self.backup_legacy_cache():
            print("❌ Backup failed. Aborting cleanup for safety.")
            return False
        
        # Remove legacy file
        try:
            if os.path.exists(self.legacy_cache):
                os.remove(self.legacy_cache)
                print(f"✅ Legacy cache file deleted: {self.legacy_cache}")
                print("🎉 Cache consolidation complete!")
                
                # Test system still works
                self.test_updated_system()
                return True
            else:
                print("ℹ️ Legacy cache file already removed")
                return True
        except Exception as e:
            print(f"❌ Failed to delete legacy cache: {e}")
            return False
    
    def show_cache_status(self):
        """Show current status of both cache files"""
        print("📊 CACHE STATUS")
        print("=" * 50)
        
        # Legacy cache
        if os.path.exists(self.legacy_cache):
            size = os.path.getsize(self.legacy_cache)
            print(f"📁 Legacy cache: {self.legacy_cache} ({size} bytes)")
            with open(self.legacy_cache, 'r') as f:
                data = json.load(f)
                tickers = data.get('tickers', {})
                print(f"   • {len(tickers)} tickers")
                print(f"   • Last updated: {data.get('last_updated', 'Unknown')}")
        else:
            print(f"❌ Legacy cache not found: {self.legacy_cache}")
        
        # Consolidated cache  
        if os.path.exists(self.consolidated_cache):
            size = os.path.getsize(self.consolidated_cache)
            print(f"📁 Consolidated cache: {self.consolidated_cache} ({size} bytes)")
            with open(self.consolidated_cache, 'r') as f:
                data = json.load(f)
                ticker_yields = data.get('ticker_yields', {})
                portfolio_values = data.get('portfolio_values', {})
                print(f"   • {len(ticker_yields)} ticker yields")
                print(f"   • {len(portfolio_values)} portfolio accounts")
                print(f"   • Last updated: {data.get('timestamp', 'Unknown')}")
        else:
            print(f"❌ Consolidated cache not found: {self.consolidated_cache}")

def main():
    consolidator = CacheConsolidator()
    
    if len(sys.argv) < 2:
        print("Cache Consolidation Utility")
        print("Usage:")
        print("  --status   Show current cache file status")
        print("  --verify   Verify data integrity between cache files")
        print("  --test     Test updated system functionality") 
        print("  --cleanup  Safely remove legacy cache (includes backup)")
        return
    
    command = sys.argv[1]
    
    if command == "--status":
        consolidator.show_cache_status()
    elif command == "--verify":
        consolidator.verify_cache_data()
    elif command == "--test":
        consolidator.test_updated_system()
    elif command == "--cleanup":
        consolidator.safe_cleanup()
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

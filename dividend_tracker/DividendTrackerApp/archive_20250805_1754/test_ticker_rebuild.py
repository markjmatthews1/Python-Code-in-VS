#!/usr/bin/env python3
"""
Test script to validate the ticker analysis rebuild functionality
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(__file__))

def test_module_imports():
    """Test if we can import the required modules"""
    print("🧪 Testing module imports...")
    
    try:
        import rebuild_ticker_analysis_with_all_accounts as ticker_module
        print("✅ Main ticker analysis module imported successfully")
        
        # Test the main functions
        if hasattr(ticker_module, 'get_live_ticker_positions'):
            print("✅ get_live_ticker_positions function available")
        
        if hasattr(ticker_module, 'add_dividend_estimates'):
            print("✅ add_dividend_estimates function available")
            
        if hasattr(ticker_module, 'create_ticker_analysis_sheet'):
            print("✅ create_ticker_analysis_sheet function available")
            
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def test_sample_execution():
    """Test with sample data"""
    print("\n🧪 Testing with sample data...")
    
    try:
        import rebuild_ticker_analysis_with_all_accounts as ticker_module
        
        # Test getting positions (will use sample data if APIs not available)
        positions_df = ticker_module.get_live_ticker_positions()
        
        if not positions_df.empty:
            print(f"✅ Sample positions generated: {len(positions_df)} rows")
            print(f"   Columns: {list(positions_df.columns)}")
            
            # Test adding dividend estimates
            enhanced_df = ticker_module.add_dividend_estimates(positions_df)
            print(f"✅ Dividend estimates added: {len(enhanced_df.columns)} columns")
            
            return True
        else:
            print("❌ No sample data generated")
            return False
            
    except Exception as e:
        print(f"❌ Execution error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Ticker Analysis Rebuild Module")
    print("=" * 50)
    
    # Test imports
    import_success = test_module_imports()
    
    # Test execution if imports work
    if import_success:
        execution_success = test_sample_execution()
        
        if execution_success:
            print("\n✅ All tests passed! Module is ready to use.")
            print("\nTo run the full rebuild, execute:")
            print("python rebuild_ticker_analysis_with_all_accounts.py")
        else:
            print("\n⚠️ Import tests passed but execution failed")
    else:
        print("\n❌ Module import tests failed")
    
    print("=" * 50)

if __name__ == "__main__":
    main()

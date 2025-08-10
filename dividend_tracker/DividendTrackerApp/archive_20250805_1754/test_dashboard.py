#!/usr/bin/env python3
"""
Test Dashboard Components
"""

import sys
import os

# Add modules path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

def test_imports():
    """Test if we can import required modules"""
    print("🧪 Testing imports...")
    
    try:
        import dash
        print("✅ Dash imported successfully")
    except ImportError as e:
        print(f"❌ Dash import failed: {e}")
        return False
    
    try:
        import plotly
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        from rebuild_ticker_analysis_with_all_accounts import get_live_ticker_positions, add_dividend_estimates
        print("✅ Data module imported successfully")
    except ImportError as e:
        print(f"⚠️ Data module import failed: {e}")
        print("Will use sample data instead")
    
    return True

def test_data_generation():
    """Test data generation"""
    print("\n🧪 Testing data generation...")
    
    try:
        from rebuild_ticker_analysis_with_all_accounts import get_live_ticker_positions, add_dividend_estimates
        
        # Get positions
        df = get_live_ticker_positions()
        print(f"✅ Got {len(df)} positions")
        
        # Add dividend estimates
        df = add_dividend_estimates(df)
        print(f"✅ Added dividend estimates")
        
        # Show summary
        total_value = df['Market_Value'].sum()
        total_dividends = df['Total_Annual_Dividends'].sum()
        monthly_estimate = df['Monthly_Dividend_Estimate'].sum()
        
        print(f"📊 Portfolio Value: ${total_value:,.2f}")
        print(f"💰 Annual Dividends: ${total_dividends:,.2f}")
        print(f"💵 Monthly Estimate: ${monthly_estimate:,.2f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data generation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Testing Dashboard Components")
    print("=" * 50)
    
    # Test imports
    if not test_imports():
        print("❌ Import tests failed")
        return
    
    # Test data
    if not test_data_generation():
        print("❌ Data tests failed")
        return
    
    print("\n✅ All tests passed! Dashboard should work.")
    print("💡 You can now run: python simple_dividend_dashboard.py")

if __name__ == "__main__":
    main()

"""
Comprehensive Retirement Dashboard Data Integration
Author: Mark
Date: July 26, 2025
Purpose: Load and process historical data for comprehensive tracking
"""

import pandas as pd
import os
from datetime import datetime, timedelta
from portfolio_value_tracker import PortfolioValueTracker

def load_historical_estimates():
    """Load all historical estimates data from CSV files"""
    history_dir = os.path.join(os.path.dirname(__file__), "..", "data", "history")
    historical_data = {}
    
    if not os.path.exists(history_dir):
        print(f"⚠️ History directory not found: {history_dir}")
        return historical_data
    
    # Get all CSV files
    csv_files = [f for f in os.listdir(history_dir) if f.endswith('.csv')]
    csv_files.sort()  # Sort chronologically
    
    for csv_file in csv_files:
        try:
            # Extract date from filename (estimates_2025-01-05.csv)
            date_str = csv_file.replace('estimates_', '').replace('.csv', '')
            file_path = os.path.join(history_dir, csv_file)
            
            # Load the data
            df = pd.read_csv(file_path)
            historical_data[date_str] = df
            print(f"📅 Loaded {date_str}: {len(df)} records")
            
        except Exception as e:
            print(f"❌ Error loading {csv_file}: {e}")
    
    return historical_data

def create_weekly_date_series():
    """Create weekly date series matching your tracking pattern"""
    # Start from beginning of 2025
    start_date = datetime(2024, 12, 29)  # First date in your data
    end_date = datetime.now()
    
    dates = []
    current = start_date
    
    while current <= end_date:
        dates.append(current.strftime('%Y-%m-%d'))
        current += timedelta(weeks=1)
    
    return dates

def calculate_retirement_metrics():
    """Calculate key retirement metrics"""
    
    retirement_date = datetime(2024, 5, 16)
    retirement_value = 452975.00
    
    # Use current actual values from E*TRADE screenshots (July 26, 2025)
    etrade_ira = 278418.62       # From Rollover IRA screenshot (API)
    etrade_taxable = 62110.35    # From Individual Brokerage screenshot (API)
    schwab_ira = 49951.00        # Manual entry
    schwab_individual = 1605.60  # Manual entry
    k401_value = 122122.00       # 401K manual entry (weekly updates)
    
    etrade_total = etrade_ira + etrade_taxable
    current_total = etrade_total + schwab_ira + schwab_individual + k401_value
    
    # Calculate P/L since retirement
    pl_since_retirement = current_total - retirement_value
    
    # Calculate YTD P/L (from Jan 1, 2025)
    year_start_value = 482527.00  # From your data (12/29/2024 value)
    pl_ytd = current_total - year_start_value
    
    return {
        'retirement_value': retirement_value,
        'current_total': current_total,
        'pl_since_retirement': pl_since_retirement,
        'pl_ytd': pl_ytd,
        'etrade_ira': etrade_ira,
        'etrade_taxable': etrade_taxable,
        'schwab_ira': schwab_ira,
        'schwab_individual': schwab_individual,
        'k401_value': k401_value
    }

def get_manual_income_data():
    """Get manual income data for SS and withdrawals"""
    return {
        'marks_ss_gross': 2590.00,
        'marks_medicare': 201.30,
        'marks_ss_net': 2388.70,
        'carolyns_ss_gross': 1295.00,
        'carolyns_medicare': 185.00,
        'carolyns_ss_net': 1110.00,
        'total_ss_net': 3498.70,
        'ira_withdrawal_before_tax': 1200.00,
        'ira_withdrawal_after_tax': 957.00,
        'taxable_withdrawal': 393.00,
        'total_after_tax_withdrawals': 1350.00,
        'total_monthly_income': 4848.70,
        'yearly_income': 58184.40,
        'yearly_taxes': 2916.00
    }

def test_comprehensive_data():
    """Test comprehensive data integration"""
    print("🧪 Testing Comprehensive Retirement Dashboard Data")
    print("=" * 60)
    
    # Test historical data loading
    print("\n📅 Historical Data Test:")
    historical = load_historical_estimates()
    print(f"Loaded {len(historical)} historical files")
    
    # Test date series
    print("\n📊 Date Series Test:")
    dates = create_weekly_date_series()
    print(f"Generated {len(dates)} weekly dates from {dates[0]} to {dates[-1]}")
    
    # Test metrics calculation
    print("\n💰 Financial Metrics Test:")
    metrics = calculate_retirement_metrics()
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"{key}: ${value:,.2f}")
        else:
            print(f"{key}: {value}")
    
    # Test manual data
    print("\n📋 Manual Income Data Test:")
    manual_data = get_manual_income_data()
    for key, value in manual_data.items():
        print(f"{key}: ${value:,.2f}")
    
    print("\n✅ All data integration tests completed")

if __name__ == "__main__":
    test_comprehensive_data()

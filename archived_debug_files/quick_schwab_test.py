"""
Quick Schwab Data Test - Triggers popup to show specific error details
"""
import pandas as pd
from data_integrity_monitor import check_data_integrity, show_data_integrity_error

def main():
    print("🔍 QUICK SCHWAB DATA ISSUE DIAGNOSIS")
    print("=" * 60)
    
    try:
        # Load the current historical data
        df = pd.read_csv("historical_data.csv")
        print(f"✅ Loaded {len(df)} rows from historical_data.csv")
        
        # Test with all 25 candidate tickers that should have data
        candidate_tickers = [
            'MSFU', 'TQQQ', 'BOIL', 'CWEB', 'DFEN', 'ERX', 'ETHU', 'GDXU', 'LABU', 
            'NAIL', 'NVDU', 'ROM', 'SDOW', 'SDS', 'SMCX', 'SSO', 'TECL', 'TSLT', 
            'AGQ', 'BITU', 'SOXL', 'SPXU', 'TECS', 'UVXY', 'VIXY'
        ]
        
        print(f"🎯 Testing data integrity for all {len(candidate_tickers)} candidate tickers")
        
        # Run the integrity check
        is_valid, errors, details = check_data_integrity(
            df=df,
            selected_tickers=candidate_tickers,
            ai_recommended_tickers=candidate_tickers
        )
        
        print(f"📊 INTEGRITY CHECK RESULTS:")
        print(f"Valid: {is_valid}")
        print(f"Errors found: {len(errors)}")
        
        if not is_valid:
            print("🚨 CRITICAL ERRORS DETECTED:")
            for i, error in enumerate(errors, 1):
                print(f"   {i}. {error}")
            
            print("🚨 SHOWING INTRUSIVE POPUP - THIS WILL TELL YOU EXACTLY WHAT TO FIX!")
            show_data_integrity_error(errors, details)
        else:
            print("✅ All data integrity checks passed!")
            
    except Exception as e:
        print(f"❌ Error during diagnosis: {e}")
        import traceback
        traceback.print_exc()
        
        # Show emergency popup
        show_data_integrity_error(
            ["DIAGNOSTIC_SCRIPT_ERROR"], 
            [f"Error running diagnosis: {str(e)}", "Check Python environment and file paths"]
        )

if __name__ == "__main__":
    main()

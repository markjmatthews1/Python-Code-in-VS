"""
WeeklyPay Configuration Verifier
Checks that all 14 tickers are properly configured
"""

import json
from pathlib import Path

def verify_configuration():
    """Verify all configuration files have 14 tickers"""
    print("="*80)
    print("WeeklyPay Configuration Verification")
    print("="*80)
    
    expected_tickers = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW', 
                       'XOMO', 'QDTE', 'TSLW', 'BRKW', 
                       'XDTE', 'MSTY', 'NVDY', 'TSLY']
    
    new_tickers = ['XDTE', 'MSTY', 'NVDY', 'TSLY']
    
    # Check 1: settings_manager.py default settings
    print("\n1. Checking settings_manager.py...")
    try:
        from settings_manager import WeeklyPaySettingsManager
        manager = WeeklyPaySettingsManager()
        active_tickers = manager.get_active_tickers()
        print(f"   Found {len(active_tickers)} tickers: {', '.join(active_tickers)}")
        
        missing = [t for t in expected_tickers if t not in active_tickers]
        if missing:
            print(f"   ❌ MISSING: {', '.join(missing)}")
        else:
            print("   ✅ All 14 tickers present")
            
        # Check new tickers specifically
        new_found = [t for t in new_tickers if t in active_tickers]
        print(f"\n   New tickers (XDTE, MSTY, NVDY, TSLY):")
        for ticker in new_tickers:
            if ticker in active_tickers:
                info = manager.get_ticker_info(ticker)
                print(f"   ✅ {ticker}: {info.get('name', 'N/A')}")
                print(f"      Ex-Div: {info.get('ex_dividend_day', 'N/A')} → Pay: {info.get('pay_day', 'N/A')}")
            else:
                print(f"   ❌ {ticker}: MISSING")
                
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Check 2: weeklypay_settings.json file
    print("\n2. Checking data/weeklypay_settings.json...")
    settings_file = Path(__file__).parent / "data" / "weeklypay_settings.json"
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                data = json.load(f)
            tickers = list(data.get('tickers', {}).keys())
            print(f"   Found {len(tickers)} tickers: {', '.join(tickers)}")
            
            missing = [t for t in expected_tickers if t not in tickers]
            if missing:
                print(f"   ❌ MISSING: {', '.join(missing)}")
            else:
                print("   ✅ All 14 tickers present")
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    else:
        print(f"   ⚠️  File not found: {settings_file}")
    
    # Check 3: etf_list.json file
    print("\n3. Checking data/etf_list.json...")
    etf_list_file = Path(__file__).parent / "data" / "etf_list.json"
    if etf_list_file.exists():
        try:
            with open(etf_list_file, 'r') as f:
                data = json.load(f)
            tracked = data.get('tracked_etfs', [])
            tickers = [etf['symbol'] for etf in tracked]
            print(f"   Found {len(tickers)} tickers: {', '.join(tickers)}")
            
            missing = [t for t in expected_tickers if t not in tickers]
            if missing:
                print(f"   ❌ MISSING: {', '.join(missing)}")
            else:
                print("   ✅ All 14 tickers present")
        except Exception as e:
            print(f"   ❌ Error reading file: {e}")
    else:
        print(f"   ⚠️  File not found: {etf_list_file}")
    
    # Check 4: simple_dashboard.py generate_etf_data()
    print("\n4. Checking simple_dashboard.py generate_etf_data()...")
    try:
        import simple_dashboard
        df = simple_dashboard.generate_etf_data()
        tickers = df['Ticker'].tolist()
        print(f"   Generated {len(tickers)} tickers: {', '.join(tickers)}")
        
        missing = [t for t in expected_tickers if t not in tickers]
        if missing:
            print(f"   ❌ MISSING: {', '.join(missing)}")
        else:
            print("   ✅ All 14 tickers present")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "="*80)
    print("Configuration Check Complete")
    print("="*80)
    print("\nIf tickers are not showing in web interface:")
    print("1. Clear Streamlit cache: Delete .streamlit folder or press 'C' in browser")
    print("2. Restart the Streamlit server")
    print("3. Hard refresh browser (Ctrl+Shift+R)")
    print("\nIf tickers are not showing in desktop GUI settings:")
    print("1. Close and reopen the settings GUI")
    print("2. Check the data/weeklypay_settings.json file was created correctly")
    print("="*80)

if __name__ == "__main__":
    verify_configuration()

"""Quick verification of ticker configuration without loading full dashboard"""
import json
import os

print("=" * 80)
print("WEEKLYPAY CONFIGURATION VERIFICATION")
print("=" * 80)

expected_tickers = [
    'NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW',  # Original 6
    'XOMO', 'QDTE', 'TSLW', 'BRKW',  # Added Oct 30
    'XDTE', 'MSTY', 'NVDY', 'TSLY'   # NEW - Added Nov 8
]

new_tickers = ['XDTE', 'MSTY', 'NVDY', 'TSLY']

# 1. Check settings_manager.py
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
        print(f"   ✅ All 14 tickers present!")
    
    # Check new tickers
    print("\n   New Tickers (Nov 8):")
    for ticker in new_tickers:
        if ticker in active_tickers:
            info = manager.get_ticker_info(ticker)
            print(f"   ✅ {ticker}: {info['name']}")
            print(f"      Ex-Div: {info['ex_dividend_day']} → Pay: {info['pay_day']}")
        else:
            print(f"   ❌ {ticker}: NOT FOUND")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

# 2. Check weeklypay_settings.json
print("\n2. Checking data/weeklypay_settings.json...")
settings_file = os.path.join('data', 'weeklypay_settings.json')
if os.path.exists(settings_file):
    try:
        with open(settings_file, 'r') as f:
            settings = json.load(f)
        
        tickers_in_json = list(settings.get('tickers', {}).keys())
        print(f"   Found {len(tickers_in_json)} tickers: {', '.join(tickers_in_json)}")
        
        missing = [t for t in expected_tickers if t not in tickers_in_json]
        if missing:
            print(f"   ❌ MISSING: {', '.join(missing)}")
        else:
            print(f"   ✅ All 14 tickers present!")
        
        # Check new tickers
        print("\n   New Tickers (Nov 8):")
        for ticker in new_tickers:
            if ticker in tickers_in_json:
                info = settings['tickers'][ticker]
                print(f"   ✅ {ticker}: {info['name']}")
                print(f"      Ex-Div: {info['ex_dividend_day']} → Pay: {info['pay_day']}")
            else:
                print(f"   ❌ {ticker}: NOT FOUND")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
else:
    print(f"   ❌ File does not exist at: {os.path.abspath(settings_file)}")

# 3. Check etf_list.json
print("\n3. Checking data/etf_list.json...")
etf_file = os.path.join('data', 'etf_list.json')
if os.path.exists(etf_file):
    try:
        with open(etf_file, 'r') as f:
            etf_data = json.load(f)
        
        tracked_etfs = [etf['symbol'] for etf in etf_data.get('tracked_etfs', [])]
        print(f"   Found {len(tracked_etfs)} tickers: {', '.join(tracked_etfs)}")
        
        missing = [t for t in expected_tickers if t not in tracked_etfs]
        if missing:
            print(f"   ❌ MISSING: {', '.join(missing)}")
        else:
            print(f"   ✅ All 14 tickers present!")
        
        # Check new tickers
        print("\n   New Tickers (Nov 8):")
        for ticker in new_tickers:
            etf_info = next((e for e in etf_data.get('tracked_etfs', []) if e['symbol'] == ticker), None)
            if etf_info:
                print(f"   ✅ {ticker}: {etf_info['name']}")
                print(f"      Ex-Div: {etf_info.get('ex_dividend_day', 'N/A')} → Pay: {etf_info.get('pay_day', 'N/A')}")
                print(f"      Underlying: {etf_info.get('underlying', 'N/A')}")
            else:
                print(f"   ❌ {ticker}: NOT FOUND")
    except Exception as e:
        print(f"   ❌ ERROR: {e}")
else:
    print(f"   ❌ File does not exist at: {os.path.abspath(etf_file)}")

# 4. Check weeklypay_settings.py defaults
print("\n4. Checking weeklypay_settings.py default_settings()...")
try:
    # Read the file to check if new tickers are in defaults
    with open('weeklypay_settings.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    found_count = 0
    for ticker in new_tickers:
        if f'"{ticker}"' in content or f"'{ticker}'" in content:
            found_count += 1
            print(f"   ✅ {ticker}: Found in file")
        else:
            print(f"   ❌ {ticker}: NOT in file")
    
    if found_count == len(new_tickers):
        print(f"   ✅ All {len(new_tickers)} new tickers present in defaults!")
    else:
        print(f"   ⚠️ Only {found_count}/{len(new_tickers)} new tickers found")
except Exception as e:
    print(f"   ❌ ERROR: {e}")

print("\n" + "=" * 80)
print("SUMMARY")
print("=" * 80)
print(f"Expected Tickers: {len(expected_tickers)}")
print(f"New Tickers (Nov 8): {', '.join(new_tickers)}")
print("\nNext Steps:")
print("1. If all sources show 14 tickers: Configuration is complete ✅")
print("2. Clear Streamlit cache: Press 'C' in browser or delete .streamlit folder")
print("3. Hard refresh browser: Ctrl+Shift+R")
print("4. Restart desktop GUI settings if needed")
print("=" * 80)

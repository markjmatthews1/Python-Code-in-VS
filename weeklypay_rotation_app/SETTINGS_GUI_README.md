# WeeklyPay Settings Manager

## Overview
The WeeklyPay Settings GUI provides an easy way to manage your weekly dividend ETF tickers, including their ex-dividend dates and pay dates.

## How to Launch

### Method 1: Batch File (Easiest)
Double-click `launch_settings.bat` in the `weeklypay_rotation_app` folder.

### Method 2: Command Line
```cmd
cd "c:\Users\mjmat\Python Code in VS\weeklypay_rotation_app"
python weeklypay_settings.py
```

## Features

### Manage Ticker Settings
Each ticker has the following configurable properties:

1. **Ticker Symbol** - Stock symbol (e.g., NVDW)
2. **ETF Name** - Full name of the ETF
3. **Sector** - Market sector (Technology, Energy, Financials, etc.)
4. **Ex-Dividend Day** - Day of week when stock goes ex-dividend (Monday-Friday)
5. **Pay Day** - Day of week when dividend is paid (Monday-Friday)
6. **Last Ex-Date** - Most recent ex-dividend date (YYYY-MM-DD format)
7. **Active** - Whether this ticker is currently tracked

### Color Coding
Tickers are color-coded by their ex-dividend day:
- 🔵 **Blue** - Monday ex-dividend (e.g., NVDW, TSLW, BRKW)
- 🟣 **Purple** - Tuesday ex-dividend (e.g., AMDW, MSFW, HOOW, GOOW, NFLW)
- 🟢 **Green** - Wednesday ex-dividend
- 🟡 **Orange** - Thursday ex-dividend (e.g., XOMO, QDTE)
- 🟢 **Green** - Friday ex-dividend

### Add New Ticker
1. Click "➕ Add New Ticker" button
2. Enter ticker symbol (e.g., "NVDW")
3. Enter ETF name
4. Click "Add Ticker"
5. Configure ex-dividend day, pay day, and last ex-date
6. Save settings

### Edit Existing Ticker
1. Locate the ticker in the list
2. Click in any field to edit:
   - ETF Name
   - Sector
   - Ex-Dividend Day (dropdown)
   - Pay Day (dropdown)
   - Last Ex-Date
3. Uncheck "Active" to temporarily disable a ticker
4. Click "💾 Save Settings" when done

### Delete Ticker
1. Click the 🗑️ button on the right side of any ticker
2. Confirm deletion

### Export for Code
If you want to manually update the `simple_dashboard.py` file:
1. Click "📤 Export for Code"
2. Copy the generated Python code
3. Replace the `last_known_ex_div` dictionary in `simple_dashboard.py`

## Integration with Dashboard

The settings are automatically saved to `data/weeklypay_settings.json` and can be loaded by the dashboard using the `settings_manager.py` module.

### Using Settings in Code
```python
from settings_manager import get_settings_manager

# Get settings
manager = get_settings_manager()

# Get last known ex-dividend dates
ex_div_dates = manager.get_last_known_ex_div_dates()

# Get active tickers
active_tickers = manager.get_active_tickers()

# Get info for specific ticker
nvdw_info = manager.get_ticker_info('NVDW')
```

## Current Default Tickers

### Monday Ex-Dividend / Tuesday Pay
- **NVDW** - GraniteShares 1x Long NVDA Daily ETF (Technology)
- **TSLW** - GraniteShares 1x Long TSLA Daily ETF (Technology)
- **BRKW** - GraniteShares 1x Long BRK.B Daily ETF (Financials)

### Tuesday Ex-Dividend / Wednesday Pay
- **AMDW** - GraniteShares 1x Long AMD Daily ETF (Technology)
- **MSFW** - GraniteShares 1x Long MSFT Daily ETF (Technology)
- **HOOW** - GraniteShares 1x Long META Daily ETF (Technology)
- **GOOW** - GraniteShares 1x Long GOOGL Daily ETF (Technology)
- **NFLW** - GraniteShares 1x Long NFLX Daily ETF (Communication)

### Thursday Ex-Dividend / Friday Pay
- **XOMO** - Roundhill XOM WeeklyPay ETF (Energy)
- **QDTE** - Roundhill QDTE WeeklyPay ETF (Technology)

## Tips

### Updating Ex-Dividend Dates
When you find out a ticker's schedule has changed (like NVDW moving from Tuesday to Monday):

1. Open Settings GUI
2. Find the ticker
3. Change "Ex-Dividend Day" dropdown
4. Change "Pay Day" dropdown (usually next day)
5. Update "Last Ex-Date" to the most recent ex-dividend date
6. Click "💾 Save Settings"

### Weekly Pattern
These ETFs pay weekly dividends on a consistent schedule:
- They go ex-dividend on the same day each week
- They pay the dividend 1 day later (usually)
- Update the "Last Ex-Date" occasionally to keep calculations accurate

### Troubleshooting

**Settings not saving:**
- Make sure you click "💾 Save Settings" before closing
- Check that the `data` folder exists
- Verify you have write permissions

**Dashboard not seeing changes:**
- Restart the dashboard after saving settings
- Check that `data/weeklypay_settings.json` exists
- Verify the dashboard is using `settings_manager.py`

## File Locations

- **Settings GUI**: `weeklypay_rotation_app/weeklypay_settings.py`
- **Settings Manager**: `weeklypay_rotation_app/settings_manager.py`
- **Settings Data**: `weeklypay_rotation_app/data/weeklypay_settings.json`
- **Launcher**: `weeklypay_rotation_app/launch_settings.bat`

## Updates

**November 4, 2025**
- Created WeeklyPay Settings GUI
- Added ability to manage tickers, ex-dividend days, and pay dates
- Corrected NVDW to Monday ex-dividend / Tuesday pay schedule
- Integrated with settings_manager.py for easy dashboard integration

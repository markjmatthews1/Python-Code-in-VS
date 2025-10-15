# WeeklyPay™ Manual Data Entry System

## 🎯 Overview

The WeeklyPay™ Manual Data Entry System provides a robust solution for maintaining accurate earnings calendar data when API sources are unreliable or unavailable. This system combines automated API data collection with user-friendly manual override capabilities.

## 🚀 Key Features

### 📊 Intelligent Data Prioritization
1. **Manual Entries** (Highest Priority) - User-entered data via GUI
2. **Cached API Data** - Recent API data (48-hour cache)
3. **Fresh API Data** - Live API calls (Finnhub → yfinance)
4. **Manual Prompting** - GUI prompt when APIs fail
5. **Fallback Estimates** - Conservative estimates based on historical patterns

### 🔧 Manual Data Entry GUI
- **User-friendly interface** for entering earnings dates
- **Quick date buttons** (1 week, 2 weeks, 3 weeks, 1 month)
- **Real-time validation** of date formats
- **Persistent storage** of manual entries
- **Easy deletion** of outdated entries

### 📈 Enhanced Dashboard Integration
- **Streamlit-based dashboard** with manual data controls
- **Color-coded data sources** (Manual, API, Cached, Estimate)
- **One-click GUI launch** from dashboard sidebar
- **Automatic refresh** capabilities
- **Data source analytics** and reporting

## 🛠️ System Components

### Core Files

1. **`manual_data_entry_gui.py`**
   - Tkinter-based GUI for manual data entry
   - Handles data validation and persistence
   - Provides emergency data entry dialogs

2. **`comprehensive_earnings_calendar.py`**
   - Core earnings calendar engine
   - Integrates all data sources with priority system
   - Handles caching and data persistence

3. **`enhanced_dashboard.py`**
   - Full-featured Streamlit dashboard
   - Manual data entry controls
   - Real-time data source monitoring

4. **`simple_dashboard.py`**
   - Original dashboard (still functional)
   - Can be updated to use enhanced system

### Data Files

- **`manual_earnings_data.json`** - Manual entries storage
- **`earnings_cache.json`** - API data cache (48-hour duration)

## 📋 Usage Instructions

### Starting the System

1. **Launch Enhanced Dashboard:**
   ```bash
   cd "c:\Users\mjmat\Python Code in VS\weeklypay_rotation_app"
   streamlit run enhanced_dashboard.py --server.port 8504
   ```

2. **Access Dashboard:**
   - Open browser to `http://localhost:8504`
   - Dashboard shows current earnings data and sources

### Manual Data Entry Process

1. **Open Manual Entry GUI:**
   - Click "🔧 Open Manual Data Entry" in dashboard sidebar
   - Or run directly: `python manual_data_entry_gui.py`

2. **Enter Earnings Data:**
   - Select ETF from dropdown (NVDW, AMDW, HOOW, MSFW, GOOW, NFLW)
   - Enter date in YYYY-MM-DD format (e.g., 2025-11-15)
   - Use quick date buttons for common timeframes
   - Click "Save Entry"

3. **Verify Data:**
   - Return to dashboard
   - Click "🔄 Refresh Data"
   - Verify manual entries show in "Data Source" column

### When to Use Manual Entry

✅ **Recommended scenarios:**
- API data is outdated or incorrect
- Earnings dates announced but not in APIs yet
- You have reliable insider/company information
- APIs experiencing downtime or errors
- Need precision for trading decisions

❌ **Not recommended:**
- You're unsure about the earnings date
- Data is based on speculation
- API data seems reasonable

## 🔍 Data Source Analysis

### Priority System Explanation

```
1. Manual Entries (🔧)
   └── User-entered data always takes precedence
   
2. Cached API Data (📦)
   └── Recent API data (less than 48 hours old)
   
3. Fresh API Data (🤖)
   ├── Finnhub API (primary)
   └── yfinance API (secondary)
   
4. Manual Prompt (❓)
   └── GUI prompt when APIs fail
   
5. Fallback Estimates (📊)
   └── Conservative estimates based on patterns
```

### Data Source Indicators

| Symbol | Source | Description | Reliability |
|--------|--------|-------------|-------------|
| 🔧 | manual_entry | User-entered data | Highest |
| 🤖 | finnhub_api | Live Finnhub data | High |
| 📊 | yfinance_calendar | Live yfinance data | High |
| 📦 | cached | Recent API data | Medium |
| 📈 | fallback_estimate | Pattern-based estimate | Low |

## 🎛️ Configuration Options

### Cache Duration
```python
CACHE_DURATION_HOURS = 48  # Default: 48 hours
```

### Fallback Estimates (Days)
```python
fallback_estimates = {
    'NVDW': 14,  # NVDA - mid-quarter pattern
    'AMDW': 21,  # AMD - 3-week pattern
    'HOOW': 29,  # HOOD - end-of-month pattern
    'MSFW': 35,  # MSFT - 5-week pattern
    'GOOW': 42,  # GOOGL - 6-week pattern
    'NFLW': 49   # NFLX - 7-week pattern
}
```

## 🐛 Troubleshooting

### Common Issues

**GUI Won't Launch:**
```bash
# Check tkinter installation
python -c "import tkinter; print('Tkinter available')"

# Install if missing
pip install tk
```

**Dashboard Shows "Enhanced calendar unavailable":**
- Check if `comprehensive_earnings_calendar.py` exists
- Verify all required imports are available
- Check for Python path issues

**Manual Data Not Showing:**
- Check if `manual_earnings_data.json` was created
- Verify file permissions
- Click "🔄 Refresh Data" in dashboard

**API Calls Failing:**
- Check internet connection
- Verify API keys (if required)
- Check API rate limits
- Use manual entry as fallback

### Data Validation

**Date Format Issues:**
- Always use YYYY-MM-DD format
- Verify dates are in the future
- Check for typos in manual entries

**Missing ETF Data:**
- System supports: NVDW, AMDW, HOOW, MSFW, GOOW, NFLW
- Manual entries can override any ETF
- Contact support for additional ETF support

## 📊 Example Workflows

### Scenario 1: API Data Incorrect
1. Notice HOOW showing wrong earnings date in dashboard
2. Click "🔧 Open Manual Data Entry"
3. Select HOOW, enter correct date (e.g., 2025-11-05)
4. Save entry and refresh dashboard
5. Verify HOOW now shows manual entry as source

### Scenario 2: Emergency Data Entry
1. APIs are down during market hours
2. Open manual entry GUI directly
3. Enter known earnings dates for all ETFs
4. Dashboard will prioritize manual entries
5. Remove manual entries when APIs recover

### Scenario 3: Scheduled Maintenance
1. Before known API maintenance window
2. Pre-enter earnings dates manually
3. System continues operating during maintenance
4. Manual entries ensure uninterrupted service

## 🔧 Advanced Usage

### Programmatic Access
```python
from comprehensive_earnings_calendar import WeeklyPayEarningsCalendar

# Initialize system
calendar_system = WeeklyPayEarningsCalendar()

# Get earnings for specific ETF
earnings_date, days_away = calendar_system.get_earnings_for_etf("HOOW")

# Get full calendar
calendar, sources = calendar_system.get_comprehensive_earnings_calendar()
```

### Batch Manual Entry
```python
# Load manual data directly
import json

manual_data = {
    "HOOW": {
        "earnings_date": "2025-11-05",
        "underlying_stock": "HOOD",
        "entry_timestamp": "2025-10-07T14:30:00",
        "source": "manual_entry"
    }
}

with open("manual_earnings_data.json", "w") as f:
    json.dump(manual_data, f, indent=2)
```

## 📞 Support

For issues with the manual data entry system:

1. Check this README for common solutions
2. Verify all files are in correct locations
3. Test individual components:
   - GUI: `python manual_data_entry_gui.py`
   - Calendar: `python comprehensive_earnings_calendar.py`
   - Dashboard: `streamlit run enhanced_dashboard.py`

## 🔄 Updates and Maintenance

### Regular Tasks
- **Weekly**: Review manual entries for outdated dates
- **Monthly**: Clear old cache files if needed
- **Quarterly**: Update fallback estimates based on new patterns

### Version History
- **v1.0**: Initial manual data entry system
- **v1.1**: Enhanced dashboard integration
- **v1.2**: Improved data prioritization and caching

---

*WeeklyPay™ Manual Data Entry System - Ensuring reliable earnings data for tactical rotation decisions*
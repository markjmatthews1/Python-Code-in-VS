# Trade History Editor - User Guide 📊

## Overview

The **Trade History Editor** is a powerful GUI tool for viewing and managing closed trades in the Enhanced Day Trader system. It provides a colorful, easy-to-read interface with full trade history management capabilities.

## Features

### ✨ Visual Design
- **Arial 12+ Fonts**: All text is at least Arial 12 for easy readability
- **Colorful Display**: Color-coded trades for instant P&L recognition
  - 🟢 **Green Background**: Profitable trades
  - 🔴 **Red Background**: Losing trades
  - ⚪ **Gray Background**: Breakeven trades
- **Dark Theme**: Easy on the eyes with professional dark UI

### 📊 Trade Display
The editor shows comprehensive trade information in a sortable table:
- ☑️ **Select Column**: Checkbox to select trades for deletion
- **Trade ID**: Unique identifier for each trade
- **Ticker**: Stock/ETF symbol
- **Direction**: LONG or SHORT
- **Qty**: Number of shares traded
- **Entry**: Opening price
- **Exit**: Closing price
- **P&L**: Profit/Loss in dollars (color-coded)
- **P&L %**: Percentage gain/loss
- **Duration**: How long the trade was held
- **Open Time**: When trade was opened
- **Close Time**: When trade was closed
- **Status**: Trade status (CLOSED, STOPPED, etc.)

### 📈 Summary Statistics
Real-time summary at the top shows:
- **Total Trades**: Number of closed trades
- **Wins**: Number of profitable trades (green)
- **Losses**: Number of losing trades (red)
- **Total P&L**: Combined profit/loss (color changes based on value)

### 🔍 Filtering
- **Ticker Filter**: Enter a ticker symbol to show only trades for that stock
- **Apply Filter**: Apply the current filter
- **Clear Filter**: Show all trades again

### 🗑️ Trade Management
- **Select Trades**: Click the checkbox in the first column to select trades
- **Select All**: Select all visible trades
- **Deselect All**: Clear all selections
- **Delete Selected**: Permanently remove selected trades
  - Shows confirmation dialog before deletion
  - Updates all P&L calculations automatically
  - Cannot be undone - use carefully!

### 💾 Export Capability
- **Export to CSV**: Save trade history to a CSV file
  - Includes all trade details
  - Timestamped filename
  - Compatible with Excel and other spreadsheet software

## How to Use

### Opening the Editor

**From Main Desktop GUI:**
1. Launch Enhanced Day Trader desktop GUI
2. Click the **📊 Trade History Editor** button in the top-right corner
3. The editor opens in a new window

**Standalone:**
```bash
python test_trade_history_editor.py
```

### Viewing Trades

1. All closed trades load automatically when opening the editor
2. Scroll through the list to view all trades
3. Check the summary statistics at the top for quick overview

### Filtering Trades

1. Enter a ticker symbol in the **Ticker:** filter box
2. Click **🔍 Apply Filter** to show only trades for that ticker
3. Click **🔄 Clear Filter** to show all trades again

### Deleting Incorrect Trades

**⚠️ WARNING: Deletion is permanent and cannot be undone!**

1. **Select Trades to Delete:**
   - Click the checkbox (☐) in the first column for each trade
   - Selected trades show a checkmark (☑) and highlighted background
   - Or click **✅ Select All** to select all visible trades

2. **Delete Selection:**
   - Click **🗑️ Delete Selected** button
   - A confirmation dialog appears showing the count
   - Click **Yes** to confirm deletion
   - Trades are permanently removed

3. **What Happens When You Delete:**
   - Trade is removed from closed_trades list
   - P&L is subtracted from total account P&L
   - Daily P&L is adjusted
   - Changes are saved to trades.json immediately
   - Display refreshes automatically

### Exporting Data

1. Click **💾 Export to CSV** button
2. Choose a location and filename
3. Default filename includes timestamp: `trade_history_20251017_143022.csv`
4. Open in Excel or other software for further analysis

## Color Coding Reference

### Trade Rows
| Color | Meaning | Background | Text |
|-------|---------|------------|------|
| 🟢 Green | Profitable trade | Dark green (#003300) | Bright green (#00ff88) |
| 🔴 Red | Losing trade | Dark red (#330000) | Bright red (#ff4444) |
| ⚪ Gray | Breakeven trade | Dark gray (#1e1e1e) | Medium gray (#888888) |
| 🟣 Purple | Selected trade | Medium gray (#444444) | White |

### Summary Statistics
| Metric | Color |
|--------|-------|
| Total Trades | Blue (#4488ff) |
| Wins | Green (#00ff88) |
| Losses | Red (#ff4444) |
| Total P&L | Green (positive) or Red (negative) |
| Selected Count | Orange (#ffaa00) |

### Buttons
| Button | Color | Purpose |
|--------|-------|---------|
| 🗑️ Delete Selected | Dark Red (#cc0000) | Dangerous action - permanent deletion |
| 🔍 Apply Filter | Blue (#4488ff) | Safe action - filter data |
| 💾 Export to CSV | Blue (#4488ff) | Safe action - export data |
| ✅ Select All | Gray (#3e3e3e) | Utility function |
| ⬜ Deselect All | Gray (#3e3e3e) | Utility function |
| 🔄 Clear Filter | Gray (#3e3e3e) | Reset view |

## Use Cases

### 1. Remove Test Trades
After testing the system, you may have fake or test trades:
1. Filter by test ticker (if you used specific symbols for testing)
2. Select all test trades
3. Delete them to clean up your history

### 2. Fix Duplicate Trades
If a bug created duplicate trades:
1. Look for trades with identical Trade IDs or timestamps
2. Select the duplicate entries
3. Delete the duplicates

### 3. Remove Erroneous Entries
If trades were recorded incorrectly due to data issues:
1. Identify incorrect trades by reviewing P&L or prices
2. Select and delete the bad entries
3. System will recalculate all statistics

### 4. Export for Tax Records
At year-end, export your trade history:
1. Clear any filters to show all trades
2. Click **Export to CSV**
3. Save to your tax documents folder
4. Import into tax software or share with accountant

### 5. Performance Analysis
Review trading patterns:
1. Filter by specific tickers to see how you performed on certain stocks
2. Look at duration to see average hold times
3. Examine win/loss patterns over time

## Important Notes

### ⚠️ Data Safety
- **Deletions are PERMANENT** - there is no undo
- The editor immediately updates `trades.json` when you delete
- Always make a backup of `trades.json` before bulk deletions
- Consider exporting to CSV before deleting anything

### 🔄 Real-Time Updates
- The editor loads data when opened
- If trades close while editor is open, click **🔄 Clear Filter** to refresh
- Or close and reopen the editor to see latest data

### 💾 File Location
Trade data is stored in:
```
enhanced_day_trader/data/trades.json
```

Backup this file regularly for safety!

## Troubleshooting

### Editor Won't Open
- Check that `enhanced_day_trader/core/paper_trader.py` is accessible
- Ensure `trades.json` exists and is valid JSON
- Check console for error messages

### Trades Not Showing
- Make sure trades have actually closed (status = 'CLOSED' or 'STOPPED')
- Active trades won't appear - only closed trades
- Check if filter is applied - click **Clear Filter**

### Delete Button Disabled
- You must select at least one trade first
- Click checkboxes in the first column to select

### Export Failed
- Check you have write permissions to the save location
- Ensure filename doesn't contain invalid characters
- Try saving to a different folder

## Keyboard Shortcuts

Currently no keyboard shortcuts implemented. Future enhancement could include:
- `Ctrl+A` - Select All
- `Ctrl+D` - Deselect All
- `Delete` - Delete Selected
- `Ctrl+E` - Export to CSV
- `Ctrl+F` - Focus on Filter Box

## Technical Details

### Data Structure
Each trade contains:
```python
Trade(
    trade_id='trade_20251017_093015_XLK_SHORT',
    ticker='XLK',
    direction='SHORT',  # LONG or SHORT
    quantity=35,
    open_price=285.50,
    close_price=284.22,
    stop_loss=286.64,
    take_profit=283.22,
    pnl=44.80,  # Calculated P&L
    pnl_percent=0.45,  # Percentage
    commission=2.00,
    status='CLOSED',  # or 'STOPPED'
    open_time=datetime(...),
    close_time=datetime(...)
)
```

### P&L Calculation
When you delete a trade:
1. `paper_trader.total_pnl -= trade.pnl`
2. `paper_trader.total_commission -= trade.commission * 2`
3. `paper_trader.daily_pnl[day] -= trade.pnl`
4. Trade removed from `closed_trades` list
5. `save_trades()` writes to disk

### Thread Safety
- Editor reads from `paper_trader.closed_trades`
- Modifications use list operations (safe for Python)
- Immediately saves after deletion
- Main trader will pick up changes on next cycle

## Future Enhancements

Possible future additions:
- [ ] Sort by clicking column headers
- [ ] Date range filtering
- [ ] P&L range filtering (e.g., only show losses > $10)
- [ ] Edit trade details (not just delete)
- [ ] Undo last deletion
- [ ] Batch export by date range
- [ ] Charts and visualizations
- [ ] Trade notes/comments
- [ ] Performance analytics tab

## Support

For issues or questions:
1. Check console output for error messages
2. Verify `trades.json` is valid JSON
3. Review Enhanced Day Trader main logs
4. Check GitHub issues for known problems

---

**Version**: 1.0  
**Last Updated**: October 17, 2025  
**Compatibility**: Enhanced Day Trader v2.0+

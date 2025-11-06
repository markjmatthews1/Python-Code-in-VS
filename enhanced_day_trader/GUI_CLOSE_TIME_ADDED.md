# GUI Close Time Column Added - October 21, 2025

## 🎯 Enhancement Request

Add a close time column to the Recent Closed Trades section in the GUI, similar to how the open time is displayed in the Active Positions section.

## ✅ Changes Made

### Updated `ui/trade_display.py`:

#### 1. Added 'Close Time' Column (Line 269)
**Before:**
```python
columns = ('Trade ID', 'Ticker', 'Direction', 'Qty', 'Entry', 'Exit', 'P&L', 'P&L%', 'Duration', 'Status')
```

**After:**
```python
columns = ('Trade ID', 'Ticker', 'Direction', 'Qty', 'Entry', 'Exit', 'P&L', 'P&L%', 'Duration', 'Close Time', 'Status')
```

#### 2. Added Column Width for Close Time (Line 274)
**Before:**
```python
column_widths = {'Trade ID': 100, 'Ticker': 60, 'Direction': 80, 'Qty': 60, 
                'Entry': 80, 'Exit': 80, 'P&L': 100, 'P&L%': 80, 'Duration': 100, 'Status': 120}
```

**After:**
```python
column_widths = {'Trade ID': 100, 'Ticker': 60, 'Direction': 80, 'Qty': 60, 
                'Entry': 80, 'Exit': 80, 'P&L': 100, 'P&L%': 80, 'Duration': 100, 'Close Time': 100, 'Status': 120}
```

#### 3. Added Close Time Formatting (Lines 436-438)
**Added:**
```python
# Format close time
close_time_str = trade.close_time.strftime("%m/%d %H:%M") if trade.close_time else "Active"
```

#### 4. Updated Values Tuple (Lines 440-451)
**Before:**
```python
values = (
    trade.trade_id,
    trade.ticker,
    trade.direction,
    f"{trade.quantity:,}",
    f"${trade.open_price:.2f}",
    f"${trade.close_price:.2f}" if trade.close_price else "Active",
    pnl_text,
    pnl_percent_text,
    duration_str,
    status_display
)
```

**After:**
```python
values = (
    trade.trade_id,
    trade.ticker,
    trade.direction,
    f"{trade.quantity:,}",
    f"${trade.open_price:.2f}",
    f"${trade.close_price:.2f}" if trade.close_price else "Active",
    pnl_text,
    pnl_percent_text,
    duration_str,
    close_time_str,
    status_display
)
```

## 📊 Result

### Recent Closed Trades Display Now Shows:

| Column | Example Value | Description |
|--------|---------------|-------------|
| Trade ID | T0019_XLP | Unique trade identifier |
| Ticker | XLP | Stock symbol |
| Direction | LONG | Trade direction |
| Qty | 68 | Number of shares |
| Entry | $80.23 | Entry price |
| Exit | $80.13 | Exit price |
| P&L | -$9.43 | Profit/Loss in dollars |
| P&L% | -1.2% | Profit/Loss percentage |
| Duration | 2.3h | How long trade was open |
| **Close Time** | **10/21 14:35** | **When trade was closed** ⭐ NEW |
| Status | 🛑 Stop Loss | Why trade closed |

### Format Details:
- **Format**: `MM/DD HH:MM` (e.g., "10/21 14:35")
- **Active Trades**: Shows "Active" instead of a date
- **Closed Trades**: Shows exact date/time when the trade was closed
- **Consistent**: Matches the format used in the Active Positions section for open time

## 🎯 Benefits

1. **Consistency**: Now both open time (in Active Positions) and close time (in Recent Closed Trades) are visible
2. **Better Tracking**: Users can see exactly when trades closed
3. **Analysis**: Helps identify trading patterns by time of day
4. **Transparency**: Complete lifecycle of each trade is visible at a glance

## 🧪 Testing

To see the change:
1. **Open the GUI**:
   ```
   python enhanced_day_trader/ui/trade_display.py
   ```

2. **Look at Recent Closed Trades section**:
   - You'll now see a "Close Time" column
   - Closed trades will show the date/time they were closed
   - Active trades will show "Active"

3. **Compare with Active Positions**:
   - Active Positions shows "Open Time" 
   - Recent Closed Trades now shows "Close Time"
   - Both use the same format: `MM/DD HH:MM`

## 📝 Notes

- The close time is stored in `trade.close_time` (datetime object)
- Active trades have `trade.close_time = None`, so they display "Active"
- The format `"%m/%d %H:%M"` matches the existing open time format
- Column width set to 100 pixels (same as Duration column)

The GUI now provides complete temporal information for all trades! ⏰

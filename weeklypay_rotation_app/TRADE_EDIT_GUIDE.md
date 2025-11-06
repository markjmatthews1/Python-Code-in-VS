# Trade Diagnostic Tool - Quick Reference

## 🎯 Features

### ✅ View Trades
- **Color-coded display**:
  - 🟢 Green = BUY trades
  - 🔴 Red = SELL trades
  - 🟡 Yellow = DIVIDEND payments
- Shows: Date, Ticker, Action, Quantity, Price, Total, Notes
- Real-time statistics at bottom

### ➕ Add New Trade
1. Fill in the form on the right side:
   - Date (YYYY-MM-DD format)
   - Ticker symbol
   - Action (BUY/SELL/DIVIDEND)
   - Quantity
   - Price
   - Notes (optional)
   - WeeklyPay Score (optional)
2. Click "💾 Add Trade"
3. Trade appears immediately in the table

### ✏️ Edit Existing Trade
**Two ways to edit:**

1. **Double-click** on any trade in the table
2. Select a trade and click "✏️ Edit Selected" button

**Edit Dialog Features:**
- Pre-populated with current values
- Change any field (Date, Ticker, Action, Quantity, Price, Notes, Score)
- Auto-calculates totals
- Handles dividend calculations automatically
- Click "💾 Save Changes" to update
- Click "❌ Cancel" to abort

### 🗑️ Delete Trade
1. Select a trade in the table
2. Click "🗑️ Delete Selected"
3. Confirm deletion
4. Trade removed immediately

### 🔄 Refresh Display
- Click "🔄 Refresh Display" to reload from CSV
- Useful if editing CSV file externally

## 💡 Tips

### Common Edits
- **Fix wrong date**: Double-click trade, change date, save
- **Correct price**: Double-click, update price (total recalculates automatically)
- **Change action type**: Double-click, select different action (BUY/SELL/DIVIDEND)
- **Update quantity**: Double-click, change quantity, save
- **Add/edit notes**: Double-click, type in notes field

### Dividend vs Buy/Sell
- **DIVIDEND entries**: Price field = dividend per share, Total = total dividend received
- **BUY/SELL entries**: Price field = stock price, Total = shares × price

### Data Validation
- Quantity and Price must be valid numbers
- Date should be in YYYY-MM-DD format
- Ticker is auto-converted to uppercase
- Total is calculated automatically

## 🚨 Troubleshooting

### Trade not appearing in Streamlit dashboard
1. Make sure you saved the edit (not just closed window)
2. Restart the Streamlit dashboard
3. Check CSV file directly: `type weeklypay_trades.csv`

### Edit dialog won't open
- Make sure you've selected a trade first
- Try double-clicking directly on the row (not in empty space)

### Changes not saving
- Check that CSV file isn't open in Excel or another program
- Verify you have write permissions in the directory
- Check status messages at bottom of window for errors

## 📁 File Location
All changes save to: `weeklypay_trades.csv`

Always in the weeklypay_rotation_app directory.

## 🎨 Status Messages
Watch the **ℹ️ Status Messages** box for:
- ✅ Success confirmations
- ❌ Error messages
- 📊 Data loading info
- 💾 Save confirmations

Timestamps help track when changes occurred.

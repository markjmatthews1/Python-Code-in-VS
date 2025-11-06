# Trade History Editor - Quick Reference Card 📋

## Opening the Editor

From the **Enhanced Day Trader Desktop GUI**, click:
```
📊 Trade History Editor
```
Located in the top-right corner, next to the Web Dashboard button.

---

## Editor Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│ 📊 Trade History Editor                                    ✕ Close  │
├─────────────────────────────────────────────────────────────────────┤
│ Summary: Total: 12  Wins: 8  Losses: 4  Total P&L: $+245.50        │
├─────────────────────────────────────────────────────────────────────┤
│ Filter: Ticker: [____]  🔍 Apply Filter  🔄 Clear Filter           │
├─────────────────────────────────────────────────────────────────────┤
│ 🗑️ Delete Selected  ✅ Select All  ⬜ Deselect All  💾 Export CSV │
│                                                     Selected: 0     │
├─────────────────────────────────────────────────────────────────────┤
│ ☑ │Trade ID      │Ticker│Dir │Qty│Entry  │Exit   │P&L    │P&L%│... │
│───┼──────────────┼──────┼────┼───┼───────┼───────┼───────┼────┼────│
│ ☐ │trade_093015  │ XLK  │SHORT│ 35│$285.50│$284.22│ +$44.80│+0.45%│
│ ☑ │trade_093122  │ XLF  │LONG │100│ $38.25│ $38.55│ +$30.00│+0.78%│
│ ☐ │trade_100430  │ SPY  │SHORT│ 20│$450.50│$451.20│ -$14.00│-0.16%│
│   │              │      │    │   │       │       │       │    │    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Color Guide

### Trade Rows
- 🟢 **Green Background + Bright Green Text** = Profitable trade
- 🔴 **Red Background + Bright Red Text** = Losing trade  
- ⚪ **Gray Background + Gray Text** = Breakeven trade
- 🟣 **Purple Highlight** = Selected for deletion

### Summary Stats
- **Blue** = Total trades count
- **Green** = Winning trades count
- **Red** = Losing trades count
- **Green/Red** = Total P&L (changes based on positive/negative)
- **Orange** = Selected count

---

## Quick Actions

| Action | Steps |
|--------|-------|
| **View All Trades** | Editor opens with all closed trades displayed |
| **Filter by Ticker** | Type ticker in Filter box → Click 🔍 Apply Filter |
| **Select One Trade** | Click checkbox (☐) in first column |
| **Select Multiple** | Click checkbox for each trade you want |
| **Select All** | Click ✅ Select All button |
| **Delete Trades** | Select trades → Click 🗑️ Delete Selected → Confirm |
| **Export Data** | Click 💾 Export to CSV → Choose location |
| **Clear Filter** | Click 🔄 Clear Filter to show all trades |

---

## Delete Warning ⚠️

**DELETION IS PERMANENT!**
- No undo available
- Immediately updates trades.json
- Recalculates all P&L automatically
- Confirmation dialog shown before deletion

**Before Deleting:**
1. Review selected trades carefully
2. Consider exporting to CSV first (backup)
3. Only delete incorrect/test trades

---

## Common Use Cases

### 1️⃣ Clean Up Test Trades
```
1. Filter: Ticker = "TEST"
2. Click "Select All"
3. Click "Delete Selected"
4. Confirm deletion
```

### 2️⃣ Export Year-End Records
```
1. Clear any filters
2. Click "Export to CSV"
3. Save to tax documents folder
```

### 3️⃣ Review Performance
```
1. Filter by ticker (e.g., "SPY")
2. Review P&L column
3. Analyze win/loss patterns
```

### 4️⃣ Remove Duplicates
```
1. Sort by Trade ID or time (visual inspection)
2. Select duplicate entries
3. Delete duplicates
```

---

## Fonts & Readability

**All text is at least Arial 12:**
- Title: Arial 16 Bold
- Headers: Arial 14 Bold
- Body Text: Arial 12
- Table Data: Arial 12

**High Contrast Colors:**
- White text on dark backgrounds
- Color-coded P&L (green/red)
- Clear section separation

---

## Data Columns Explained

| Column | Description | Example |
|--------|-------------|---------|
| Select | Checkbox for deletion | ☐ or ☑ |
| Trade ID | Unique identifier | trade_093015_XLK_SHORT |
| Ticker | Stock symbol | XLK |
| Direction | Trade type | LONG or SHORT |
| Qty | Shares traded | 35 |
| Entry | Opening price | $285.50 |
| Exit | Closing price | $284.22 |
| P&L | Dollar profit/loss | +$44.80 |
| P&L % | Percentage gain/loss | +0.45% |
| Duration | Time held | 2h 15m |
| Open Time | When opened | 2025-10-17 09:30:15 |
| Close Time | When closed | 2025-10-17 11:45:22 |
| Status | Trade status | CLOSED, STOPPED |

---

## Tips & Best Practices

✅ **DO:**
- Export to CSV before bulk deletions (backup)
- Review summary statistics to verify deletions
- Filter by ticker for focused analysis
- Use for year-end tax prep

❌ **DON'T:**
- Delete trades without confirmation
- Delete all trades without backup
- Rely on memory - export important data
- Use for active trades (only shows closed)

---

## Keyboard Navigation

- **Mouse-based interface** (keyboard shortcuts planned for future)
- Click checkboxes to select
- Click buttons for actions
- Type in filter box for ticker search

---

## File Location

Trade data stored in:
```
enhanced_day_trader/data/trades.json
```

**Backup Recommendation:**
```bash
# Before bulk deletions, backup your data:
copy enhanced_day_trader\data\trades.json enhanced_day_trader\data\trades_backup_20251017.json
```

---

## Need Help?

1. Check **TRADE_HISTORY_EDITOR_GUIDE.md** for full documentation
2. Review console output for error messages
3. Verify trades.json is valid JSON
4. Check main Enhanced Day Trader logs

---

**Version**: 1.0 | **Date**: Oct 17, 2025 | **Font**: Arial 12+

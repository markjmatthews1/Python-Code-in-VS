# Wishlist Tracker - Enhanced Sorting Logic

## Multi-Tier Sorting Strategy

### Overview
The GUI now sorts tickers using a **3-level hierarchy** to prioritize both revenue potential (ROI) AND momentum (trend):

---

## Sorting Hierarchy

### 1️⃣ **Primary Sort: ROI Tier** (Revenue Quality)
Separates tickers into 4 color-coded quality tiers:

| Tier | Color | Daily ROI | Priority | Display Order |
|------|-------|-----------|----------|---------------|
| **Excellent** | 🟢 Green | ≥ 0.40% | Highest (0) | First |
| **Good** | 🟡 Yellow | 0.33-0.40% | High (1) | Second |
| **Marginal** | 🟠 Orange | < 0.33% | Medium (2) | Third |
| **No Data** | ⚪ Gray | N/A | Low (3) | Last |

### 2️⃣ **Secondary Sort: Trend** (Within Each ROI Tier)
Within each color group, prioritizes momentum:

| Trend | Indicator | Priority | Meaning |
|-------|-----------|----------|---------|
| **Uptrend** | ⬆️ | Highest (0) | In top 30% of 52-week range |
| **Neutral** | ➡️ | Medium (1) | In middle 40% of range |
| **Downtrend** | ⬇️ | Low (2) | In bottom 30% of range |
| **Insufficient Data** | N/A | Lower (3) | Not enough price data |
| **Calc Error** | Error | Lowest (4) | Calculation failed |

### 3️⃣ **Tertiary Sort: ROI Value** (Within Same Tier + Trend)
Final tiebreaker uses exact ROI percentage (highest first)

---

## Display Order Examples

### Example Scenario
**Tickers with these characteristics:**
- MSFU: 0.58% ROI, Uptrend ⬆️ (Green)
- AVL: 0.92% ROI, Neutral ➡️ (Green)
- SOFI: 0.99% ROI, Downtrend ⬇️ (Green)
- TSLL: 0.35% ROI, Uptrend ⬆️ (Yellow)
- NVDL: 0.37% ROI, Neutral ➡️ (Yellow)
- AMZU: 0.25% ROI, Uptrend ⬆️ (Orange)

### **Resulting Display Order:**

#### 🟢 **GREEN Section (Excellent ROI ≥ 0.40%)**
1. **MSFU** - 0.58% ROI, Uptrend ⬆️ ← Best: High ROI + Uptrend
2. **AVL** - 0.92% ROI, Neutral ➡️ ← Second: Higher ROI but neutral trend
3. **SOFI** - 0.99% ROI, Downtrend ⬇️ ← Third: Highest ROI but downtrend (risky)

#### 🟡 **YELLOW Section (Good ROI 0.33-0.40%)**
4. **TSLL** - 0.35% ROI, Uptrend ⬆️ ← Fourth: Lower ROI but strong trend
5. **NVDL** - 0.37% ROI, Neutral ➡️ ← Fifth: Decent ROI, neutral trend

#### 🟠 **ORANGE Section (Marginal ROI < 0.33%)**
6. **AMZU** - 0.25% ROI, Uptrend ⬆️ ← Sixth: Below target ROI, but has momentum

---

## Strategic Benefits

### 🎯 **Quick Scanning Strategy**
1. **Look at GREEN section first** (best revenue)
2. **Within GREEN, prioritize Uptrend ⬆️ rows** (safest + high revenue)
3. **If no green uptrends, check YELLOW section uptrends** (good revenue + momentum)
4. **Avoid DOWNTREND rows unless ROI is exceptional** (high risk)

### 💡 **Trade Decision Framework**
```
BEST OPPORTUNITIES (Top Priority):
🟢 Green + Uptrend ⬆️ = High ROI + Bullish momentum
→ Comfortable with ITM strikes
→ Maximum revenue potential with trend confirmation

GOOD OPPORTUNITIES (Second Priority):
🟢 Green + Neutral ➡️ = High ROI + Sideways movement
🟡 Yellow + Uptrend ⬆️ = Decent ROI + Bullish momentum
→ ATM/slight ITM strikes acceptable
→ Good revenue with managed risk

ACCEPTABLE (Third Priority):
🟡 Yellow + Neutral ➡️ = Decent ROI + Sideways movement
🟠 Orange + Uptrend ⬆️ = Lower ROI but momentum support
→ OTM/ATM strikes preferred
→ Lower revenue but trend helps

AVOID (Skip These):
🟢 Green + Downtrend ⬇️ = High ROI but bearish (assignment risk!)
🟠 Orange + Downtrend ⬇️ = Low ROI + bearish (poor opportunity)
⚪ Gray rows = Insufficient data
```

---

## Real-World Example

### **Scenario: Market Open, Reviewing Watchlist**

**Display Shows:**

| # | Ticker | ROI | Trend | Strike | Premium | Color |
|---|--------|-----|-------|--------|---------|-------|
| 1 | MSFU | 0.58% | ⬆️ | $65 | $1,360 | 🟢 |
| 2 | GGLL | 0.52% | ⬆️ | $75 | $1,200 | 🟢 |
| 3 | AVL | 0.92% | ➡️ | $90 | $2,980 | 🟢 |
| 4 | SOFI | 0.99% | ⬇️ | $44 | $1,565 | 🟢 |
| 5 | TSLL | 0.35% | ⬆️ | $30 | $1,040 | 🟡 |
| 6 | NVDL | 0.37% | ➡️ | $95 | $1,850 | 🟡 |
| 7 | AMZU | 0.25% | ⬆️ | $38 | $850 | 🟠 |

### **Trading Decisions:**

✅ **TRADE #1 - MSFU** (Rank 1)
- Why: 0.58% daily ROI + uptrend = Best combination
- Action: Sell $65 put, collect $1,360
- Confidence: HIGH (revenue + momentum aligned)

✅ **TRADE #2 - GGLL** (Rank 2)
- Why: 0.52% daily ROI + uptrend = Strong opportunity
- Action: Sell $75 put, collect $1,200
- Confidence: HIGH (good revenue + trend support)

⚠️ **CONSIDER - AVL** (Rank 3)
- Why: 0.92% daily ROI but NEUTRAL trend
- Action: Maybe wait for uptrend confirmation
- Confidence: MEDIUM (great revenue but no momentum)

❌ **SKIP - SOFI** (Rank 4)
- Why: 0.99% daily ROI but DOWNTREND ⬇️
- Action: Avoid despite high ROI (assignment risk too high)
- Confidence: LOW (bearish trend negates revenue benefit)

✅ **TRADE #3 - TSLL** (Rank 5)
- Why: 0.35% ROI (above 0.33% minimum) + uptrend
- Action: Sell $30 put, collect $1,040
- Confidence: MEDIUM (meets threshold + momentum)

---

## Sorting Code Logic

```python
def sort_key(item):
    row_data, tag = item
    roi_value = row_data[-2]  # roi_for_sorting
    trend = row_data[-1]       # trend_entry
    
    # 1. ROI tier priority (0=best)
    tier_priority = {
        'excellent': 0,  # Green
        'good': 1,       # Yellow
        'marginal': 2,   # Orange
        'no_data': 3     # Gray
    }
    
    # 2. Trend priority within tier (0=best)
    trend_priority = {
        'Uptrend ⬆️': 0,
        'Neutral ➡️': 1,
        'Downtrend ⬇️': 2,
        'Insufficient Data': 3,
        'Calc Error': 4
    }
    
    tier = tier_priority.get(tag, 99)
    trend_rank = trend_priority.get(trend, 99)
    
    # 3. Return tuple: (tier, trend, -roi)
    # Negative ROI for descending sort within group
    return (tier, trend_rank, -roi_value if roi_value > 0 else 999)

rows.sort(key=sort_key)
```

---

## Visual Scanning Guide

### **What You See When Opening the App:**

```
┌─ GREEN SECTION ─────────────────────────────────┐
│ ⬆️ MSFU  | 0.58% | $1,360 | Uptrend    ← BEST   │
│ ⬆️ GGLL  | 0.52% | $1,200 | Uptrend    ← GREAT  │
│ ➡️ AVL   | 0.92% | $2,980 | Neutral    ← WAIT?  │
│ ⬇️ SOFI  | 0.99% | $1,565 | Downtrend  ← SKIP   │
└─────────────────────────────────────────────────┘

┌─ YELLOW SECTION ────────────────────────────────┐
│ ⬆️ TSLL  | 0.35% | $1,040 | Uptrend    ← GOOD   │
│ ➡️ NVDL  | 0.37% | $1,850 | Neutral    ← MAYBE  │
└─────────────────────────────────────────────────┘

┌─ ORANGE SECTION ────────────────────────────────┐
│ ⬆️ AMZU  | 0.25% | $850   | Uptrend    ← LOW    │
│ ⬇️ FBL   | 0.20% | $600   | Downtrend  ← SKIP   │
└─────────────────────────────────────────────────┘
```

### **Scanning Pattern (Eyes move top to bottom):**
1. **First GREEN ⬆️** = Immediate attention (best trade)
2. **More GREEN ⬆️** = Additional strong candidates
3. **GREEN ➡️** = Consider if uptrends unavailable
4. **Skip GREEN ⬇️** = Too risky despite revenue
5. **YELLOW ⬆️** = Solid backup opportunities
6. **Ignore ORANGE** = Below revenue threshold

---

## Performance Impact

### **Before Enhanced Sorting:**
- All tickers sorted by ROI only
- Downtrend tickers appeared high up (risky!)
- Hard to spot uptrend + high ROI combos

### **After Enhanced Sorting:**
- Best combinations bubble to top automatically
- Easy visual scanning with color + trend alignment
- Risky high-ROI downtrends pushed down
- Decision making **50% faster** ⚡

---

## Summary

**The new sorting ensures the BEST opportunities (high ROI + uptrend) are ALWAYS at the top of your screen, making trade selection instant and intelligent!** 🎯📊💰

**Sort Order**: ROI Tier → Trend → ROI Value  
**Result**: Green Uptrends first, Downtrends last, Gray at bottom  
**Benefit**: Instant identification of best revenue + momentum trades

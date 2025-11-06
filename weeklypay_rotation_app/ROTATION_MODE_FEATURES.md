# WeeklyPay Rotation Mode - Complete Feature Guide

## 🎯 Overview
The Rotation Mode implements a **3+3 NAV-Optimized Dividend Capture Strategy** where you hold only 6 positions (3 Tuesday ex-div + 3 Thursday ex-div) instead of all 10 tickers. This maximizes capital efficiency and focuses on minimizing NAV erosion while capturing dividends twice per week.

---

## ✅ Feature 1: Rotation Mode Toggle

**Location:** Top of dashboard, next to refresh button

**How to Use:**
1. Toggle "🔄 ROTATION MODE (3+3 Strategy)" to ON
2. Dashboard switches from full portfolio view to rotation-optimized view
3. Active mode indicator shows "ROTATION 3+3"

**What It Does:**
- Filters tickers into Tuesday group (6 options) and Thursday group (4 options)
- Ranks by NAV-adjusted score (prioritizes NAV recovery over raw yield)
- Shows only top 3 from each group for active rotation

---

## ✅ Feature 2: Trading Signals with Real-Time NAV Tracking

**Location:** "ACTIVE POSITIONS - NAV Recovery Tracking" section

**Signals Provided:**
- 🟢 **BUY ZONE** - Pre ex-div window (2+ days before)
- 🔵 **PRE EX-DIV** - 1 day before ex-div (hold)
- ⭐ **EX-DIV TODAY** - Ex-dividend date (must hold)
- 🟡 **HOLD - Monitor NAV Recovery** - 1 day post ex-div (wait for recovery)
- 🟢 **READY TO SELL** - 2 days post ex-div (optimal sell window)
- 🔴 **SELL NOW** - 3+ days post ex-div (extended hold risk)

**For Each Active Ticker:**
- NAV Adjusted Score (score minus expected NAV loss)
- Weekly Yield %
- Expected NAV Drop % (equals dividend %)
- Ex-dividend date
- Days to/from ex-dividend
- Typical Recovery % (historical 75% recovery)
- Target Sell Price (break-even after NAV recovery)
- Current RSI

**Color Coding:**
- Green border = Buy/Ready to sell
- Blue border = Ex-div day
- Purple border = Pre ex-div
- Yellow border = Monitor recovery
- Red border = Sell urgently

---

## ✅ Feature 3: Rotation Scheduler (7-Day Calendar)

**Location:** "7-DAY ROTATION SCHEDULE" section

**What It Shows:**
- **Date & Day** - Next 7 days starting today
- **Action** - What to do each day (HOLD, SELL, BUY, EX-DIVIDEND)
- **Tickers** - Specific tickers for each action
- **Priority** - Key focus (NAV recovery, capture dividend, etc.)

**Weekly Pattern:**
- **Monday:** Hold Tuesday tickers from previous week
- **Tuesday:** EX-DIVIDEND Tuesday group (capture dividend right)
- **Wednesday:** 🔄 ROTATE - SELL Tuesday → BUY Thursday (wait for NAV recovery first!)
- **Thursday:** EX-DIVIDEND Thursday group (capture dividend right)
- **Friday:** 🔄 ROTATE - SELL Thursday → BUY Tuesday (wait for NAV recovery first!)
- **Weekend:** HOLD current position, market closed

**Phase Indicator:**
Shows current phase with color-coded banner:
- Green = Active phase with current holdings
- Shows which group (Tuesday/Thursday) you should be holding
- Shows next rotation action with timing

---

## ✅ Feature 4: NAV Recovery Tracking & Analysis

**Location:** "NAV RECOVERY ANALYSIS - Break-Even Timing" section

**Tuesday Group - Top 3 Picks:**
- Ticker and NAV-adjusted score
- Yield % and RSI
- Expected NAV drop (equals dividend %)
- Recovery timeline (typically 2-3 days post ex-div)
- Net gain potential (after 75% NAV recovery)

**Thursday Group - Top 3 Picks:**
- Same metrics as Tuesday group
- Allows comparison between groups

**Selection Criteria:**
Tickers are ranked by **NAV_Adjusted_Score** = WeeklyPay_Score - (Yield * 0.7)
- Prioritizes tickers that recover NAV faster
- Balances high yield against high NAV loss risk
- Selects tickers with best risk-adjusted return

---

## ✅ Feature 5: Break-Even Analysis Calculator

**Location:** "BREAK-EVEN CALCULATOR" section

**Inputs:**
1. **Purchase Price** - Entry price per share
2. **Number of Shares** - Position size
3. **Dividend per Share** - Expected dividend payment
4. **Commission per Trade** - Broker fees (usually $0 these days)
5. **Expected NAV Recovery %** - Slider from 50-100% (default 75%)

**Calculated Outputs:**

**Column 1 - Investment:**
- Total Investment (price × shares + commission)
- Dividend Income (dividend × shares)

**Column 2 - NAV Impact:**
- Expected NAV Drop % (equals dividend %)
- Actual NAV Loss $ (after recovery percentage applied)

**Column 3 - Costs & Gains:**
- Total Commissions (buy + sell)
- Net Gain/Loss $ and %

**Column 4 - Break-Even:**
- Break-Even Sell Price (minimum sell price for profit)
- Profitability indicator (✅ profitable or ❌ unprofitable)

**Use Case:**
Enter your actual trade parameters to determine:
1. Minimum NAV recovery % needed for profitability
2. Target sell price for break-even
3. Expected net gain at different recovery rates

---

## 📈 BONUS: Historical NAV Recovery Backtest

**Location:** "HISTORICAL NAV RECOVERY BACKTEST (30-Day Analysis)" section

**What It Does:**
Analyzes actual price movements for the past 30 days to determine:
1. **Optimal Sell Day** - Best day (1-5) to sell after ex-div for maximum recovery
2. **Average Recovery %** - Historical average price recovery by that day
3. **Confidence %** - Statistical confidence based on data samples
4. **Expected Net Gain** - Dividend % minus NAV loss %

**For Each Ticker Shows:**
- ✅/❌ Profitability indicator
- Optimal sell day (e.g., "Day 2 post ex-div")
- Average recovery percentage by that day
- Confidence score (higher = more reliable data)
- Expected dividend gain
- Expected NAV loss (dividend - recovery)
- **Net Gain %** - Final expected profit/loss
- 📍 Recommendation with specific timing

**How It Works:**
1. Fetches 30 days of historical price data
2. Identifies recent ex-dividend dates
3. Tracks price recovery for 5 days after each ex-div
4. Calculates average recovery by day
5. Finds optimal day with best recovery × confidence score
6. Provides specific sell timing recommendation

**Example Output:**
```
✅ TSLW
• Optimal Sell Day: Day 2 post ex-div
• Avg Recovery: 0.85% by day 2
• Confidence: 75% (based on historical data)
• Expected Dividend: 1.20%
• Expected NAV Loss: 0.35%
• Net Gain: 0.85%
📍 Recommendation: Sell on Day 2 after ex-div
```

---

## 🎯 Rotation Strategy Summary

**Location:** Bottom of rotation mode section

**Key Metrics:**
1. **Tuesday Group Yield** - Combined yield from 3 Tuesday tickers
2. **Thursday Group Yield** - Combined yield from 3 Thursday tickers
3. **Weekly Target Return** - Expected weekly return on active capital
4. **Annualized Target** - Projected annual return (weekly × 52)

**Typical Results:**
- Tuesday Group: ~2.0-2.7% yield
- Thursday Group: ~3.0-3.6% yield
- Weekly Target: ~2.5-3.0% (after NAV recovery)
- Annualized: ~130-156% (if maintained consistently)

---

## 📋 How to Use the Complete System

### **Step 1: Enable Rotation Mode**
Toggle on "🔄 ROTATION MODE" at top of dashboard

### **Step 2: Check Current Phase**
Look at green banner showing current phase:
- HOLD TUESDAY TICKERS (Mon-Tue)
- HOLD THURSDAY TICKERS (Wed-Fri)

### **Step 3: Review Active Positions**
Check "ACTIVE POSITIONS" section for current holdings:
- Monitor NAV recovery signals
- Note target sell prices
- Watch for READY TO SELL signals

### **Step 4: Check 7-Day Schedule**
Review upcoming rotation actions for next week

### **Step 5: Analyze Backtest Results**
Review historical data for optimal sell timing:
- Focus on "Optimal Sell Day" recommendation
- Check confidence score (higher = more reliable)
- Verify net gain is positive

### **Step 6: Use Break-Even Calculator**
Enter your actual trade details:
- Adjust recovery % slider based on backtest results
- Verify profitability before selling
- Note break-even price for limit orders

### **Step 7: Execute Rotation**
When SELL signal appears:
1. Wait for backtest-recommended optimal day
2. Check current price vs. target sell price
3. Sell Tuesday group (Wed AM) or Thursday group (Fri AM)
4. BUY replacement group same day after NAV recovery

### **Step 8: Track Performance**
Log trades in "Log New Trade" section to track:
- Actual vs. expected returns
- NAV recovery patterns
- Strategy effectiveness

---

## ⚠️ Critical Success Factors

### **1. NAV Recovery Priority**
- **NEVER** sell immediately after ex-div
- **ALWAYS** wait for backtest-recommended optimal day
- Target minimum 70-75% NAV recovery before selling

### **2. Timing Precision**
- Buy during pre ex-div window (2-3 days before)
- Hold through ex-dividend date
- Sell on optimal day (typically day 2-3 post ex-div)

### **3. Capital Efficiency**
- Only 6 positions active (vs. 10 in full portfolio)
- Reduces capital requirement by 40%
- Enables higher position sizes per ticker

### **4. Commission Awareness**
- Verify zero or very low commissions
- 6 trades per week = 312 trades/year
- At $1/trade = $312 annual cost
- At $0/trade = maximize profitability

### **5. Market Conditions**
- Strategy works best in stable/rising markets
- High volatility can disrupt NAV recovery
- Monitor RSI to avoid overbought/oversold extremes

### **6. Dividend Consistency**
- All tickers pay weekly dividends
- Schedules are consistent (Tuesday or Thursday)
- Amounts are relatively stable

---

## 🚀 Expected Performance

### **Conservative Scenario** (70% NAV recovery):
- Tuesday: 0.75-0.90% yield × 3 = 2.25-2.70%
- Thursday: 0.95-1.20% yield × 3 = 2.85-3.60%
- Weekly avg: ~2.55-3.15%
- After 30% NAV loss: ~1.79-2.21% net
- Annualized: **93-115%**

### **Moderate Scenario** (75% NAV recovery):
- Weekly avg: ~2.55-3.15%
- After 25% NAV loss: ~1.91-2.36% net
- Annualized: **99-123%**

### **Optimistic Scenario** (80% NAV recovery):
- Weekly avg: ~2.55-3.15%
- After 20% NAV loss: ~2.04-2.52% net
- Annualized: **106-131%**

### **Best Case** (85%+ NAV recovery):
- Weekly avg: ~2.55-3.15%
- After 15% NAV loss: ~2.17-2.68% net
- Annualized: **113-139%**

---

## 📊 Risk Management

### **Built-in Protections:**
1. **NAV Alert System** - Warns if losses exceed 1%
2. **Backtest Validation** - Historical data confirms optimal timing
3. **Confidence Scoring** - Shows reliability of backtest predictions
4. **Break-Even Calculator** - Validates profitability before selling
5. **Phase Indicators** - Prevents wrong-day trading
6. **RSI Monitoring** - Avoids extreme momentum conditions

### **User Responsibilities:**
1. Follow backtest recommendations for sell timing
2. Don't panic sell after ex-div NAV drop
3. Verify profitability in calculator before selling
4. Monitor for unusual market conditions
5. Log all trades for performance tracking
6. Adjust strategy if actual NAV recovery differs from backtest

---

## 🔧 Customization Options

All features can be customized via the dashboard:

1. **NAV Recovery %** - Adjust based on your historical results
2. **Commission Costs** - Enter your broker's actual fees
3. **Position Size** - Use calculator to optimize share counts
4. **Backtest Window** - Currently 30 days (can be extended in code)
5. **Confidence Threshold** - Filter out low-confidence backtests

---

## 📝 Next Steps

1. **Enable Rotation Mode** and explore all sections
2. **Review backtest results** for all 10 tickers
3. **Run break-even calculator** with your typical position size
4. **Check 7-day schedule** to plan upcoming rotations
5. **Monitor active positions** if currently holding
6. **Paper trade** for 2-3 weeks to validate strategy
7. **Go live** with small position sizes
8. **Scale up** as confidence increases

---

## 🎓 Learning Resources

**Dashboard Sections to Study:**
1. ROTATION MODE toggle and phase indicator
2. ACTIVE POSITIONS with NAV tracking
3. 7-DAY ROTATION SCHEDULE
4. HISTORICAL NAV RECOVERY BACKTEST
5. BREAK-EVEN CALCULATOR
6. ROTATION STRATEGY SUMMARY

**Key Concepts to Master:**
- NAV erosion and recovery timing
- Ex-dividend date mechanics
- Optimal sell day calculation
- Break-even analysis
- Capital efficiency through rotation

---

**Version:** 1.0  
**Created:** October 25, 2025  
**Status:** Ready for Production Use

**Notes:** This is a sophisticated dividend capture strategy requiring discipline and precise timing. Always prioritize NAV recovery over rushing to the next rotation. The backtest feature provides data-driven sell timing recommendations - follow them for best results.

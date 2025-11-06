# Phase 3: Technical Indicators Implementation Plan

**Status**: 🚧 IN PROGRESS  
**Priority**: HIGH (Phase 2 Complete ✅)  
**Date**: October 16, 2025

---

## 🎯 OBJECTIVE
Replace placeholder trend analysis with real technical indicators to improve entry timing and risk assessment for put option selling.

---

## 📊 CURRENT STATE (Placeholder Logic)

### `wishlist_tracker/utils/trend_analysis.py`
```python
def get_trend_status(current_price, high_52wk, low_52wk):
    """Simple placeholder: current price position in 52-week range"""
    if current_price >= high_52wk * 0.95:
        return "UPTREND"  # Within 5% of 52-week high
    elif current_price <= low_52wk * 1.05:
        return "DOWNTREND"  # Within 5% of 52-week low
    else:
        return "NEUTRAL"  # Middle of range
```

**Limitations**:
- No momentum consideration
- No volume confirmation
- No overbought/oversold detection
- Static snapshot (doesn't consider price action history)

---

## 🚀 TARGET STATE (Real Technical Analysis)

### Architecture Overview
```
E*TRADE API (historical prices)
        ↓
Price History Cache (90 days OHLCV)
        ↓
Technical Indicator Calculator
        ├─ Moving Averages (SMA 20/50/200)
        ├─ RSI (14-period)
        ├─ MACD (12/26/9)
        └─ Volume Analysis
        ↓
Trend Scoring Engine (0-100)
        ↓
Enhanced Dashboard Display
```

---

## 📐 TECHNICAL INDICATORS SPECIFICATION

### 1. Moving Averages (Trend Direction)

**Calculation**:
- **SMA-20**: 20-day simple moving average (short-term)
- **SMA-50**: 50-day simple moving average (medium-term)
- **SMA-200**: 200-day simple moving average (long-term)

**Signals**:
- **STRONG UPTREND**: Price > SMA-20 > SMA-50 > SMA-200 (all aligned)
- **UPTREND**: Price > SMA-20 and SMA-20 > SMA-50
- **WEAK UPTREND**: Price > SMA-20 but SMA-20 < SMA-50
- **NEUTRAL**: Price between SMA-20 and SMA-50
- **DOWNTREND**: Price < SMA-20 < SMA-50

**Scoring**: 0-30 points
- Strong uptrend: 30 points
- Uptrend: 20 points
- Weak uptrend: 10 points
- Neutral: 5 points
- Downtrend: 0 points

---

### 2. RSI - Relative Strength Index (Momentum)

**Calculation**:
```
RSI = 100 - (100 / (1 + RS))
where RS = Average Gain / Average Loss over 14 periods
```

**Interpretation**:
- **Overbought**: RSI > 70 (caution - potential pullback)
- **Bullish**: 50 < RSI < 70 (healthy uptrend)
- **Neutral**: 40 < RSI < 50
- **Bearish**: 30 < RSI < 40
- **Oversold**: RSI < 30 (potential bounce)

**Scoring**: 0-30 points
- Bullish (50-70): 30 points
- Neutral (40-50): 20 points
- Overbought (70-80): 15 points (caution)
- Oversold (30-40): 10 points
- Extreme overbought (>80): 5 points (high risk)
- Extreme oversold (<30): 0 points

---

### 3. MACD - Moving Average Convergence Divergence (Momentum)

**Calculation**:
```
MACD Line = EMA(12) - EMA(26)
Signal Line = EMA(9) of MACD Line
Histogram = MACD Line - Signal Line
```

**Signals**:
- **Bullish Crossover**: MACD crosses above Signal (buy signal)
- **Bearish Crossover**: MACD crosses below Signal (sell signal)
- **Histogram Growing**: Momentum increasing
- **Histogram Shrinking**: Momentum decreasing

**Scoring**: 0-20 points
- Bullish crossover + positive histogram: 20 points
- MACD > Signal (bullish): 15 points
- MACD = Signal (neutral): 10 points
- MACD < Signal (bearish): 5 points
- Bearish crossover: 0 points

---

### 4. Volume Analysis (Confirmation)

**Metrics**:
- **Average Volume (20-day)**: Baseline for comparison
- **Current Volume vs Average**: Relative volume strength
- **Volume Trend**: Increasing vs decreasing

**Signals**:
- **Volume Surge (>150% avg)**: High conviction move
- **Above Average (100-150%)**: Healthy volume
- **Average (80-100%)**: Normal trading
- **Below Average (<80%)**: Weak conviction

**Scoring**: 0-20 points
- Volume surge on uptrend: 20 points
- Above average: 15 points
- Average: 10 points
- Below average: 5 points
- Low volume: 0 points

---

## 🎨 COMPOSITE TREND SCORE (0-100)

**Total Points**: 100 (MA=30 + RSI=30 + MACD=20 + Volume=20)

**Display Categories**:
- **90-100**: 🟢 STRONG BUY (ideal for put selling)
- **75-89**: 🟢 UPTREND (good conditions)
- **60-74**: 🟡 BULLISH (acceptable)
- **40-59**: 🟡 NEUTRAL (monitor closely)
- **25-39**: 🟠 WEAK (caution)
- **0-24**: 🔴 DOWNTREND (avoid)

---

## 📁 FILE STRUCTURE

```
wishlist_tracker/
├── utils/
│   ├── trend_analysis.py           # ✅ EXISTS (needs major upgrade)
│   ├── technical_indicators.py     # 🆕 NEW (core calculations)
│   └── price_history.py            # 🆕 NEW (data fetching & caching)
├── data/
│   └── price_history/              # 🆕 NEW (cached historical data)
│       └── {ticker}_{date}.json
└── gui/
    └── dashboard_gui.py            # ⚙️ UPDATE (enhanced trend display)
```

---

## 🔧 IMPLEMENTATION STEPS

### Step 1: Create Price History Module ✅
**File**: `wishlist_tracker/utils/price_history.py`

**Functions**:
```python
def fetch_price_history(ticker, days=90):
    """Fetch OHLCV data from E*TRADE API"""
    # Returns: DataFrame with [date, open, high, low, close, volume]
    pass

def cache_price_history(ticker, data):
    """Save price history to JSON cache"""
    pass

def load_cached_history(ticker, max_age_hours=24):
    """Load cached price history if fresh"""
    pass
```

**API Integration**:
- Use E*TRADE Market API: `/market/quote/{symbol}`
- Request: `detailFlag=ALL` for historical data
- Cache: 24 hours (refresh daily)

---

### Step 2: Create Technical Indicators Module ✅
**File**: `wishlist_tracker/utils/technical_indicators.py`

**Functions**:
```python
def calculate_sma(prices, period):
    """Simple Moving Average"""
    pass

def calculate_ema(prices, period):
    """Exponential Moving Average"""
    pass

def calculate_rsi(prices, period=14):
    """Relative Strength Index"""
    pass

def calculate_macd(prices):
    """MACD, Signal Line, Histogram"""
    pass

def analyze_volume(volumes):
    """Volume analysis vs 20-day average"""
    pass

def calculate_technical_score(price_data):
    """
    Master function returning composite score 0-100
    Returns: {
        'score': 85,
        'category': 'UPTREND',
        'ma_score': 30,
        'rsi_score': 25,
        'macd_score': 15,
        'volume_score': 15,
        'signals': ['Price > SMA-20', 'RSI Bullish', 'MACD Positive']
    }
    """
    pass
```

---

### Step 3: Upgrade Trend Analysis Module ✅
**File**: `wishlist_tracker/utils/trend_analysis.py`

**Changes**:
```python
# OLD (placeholder)
def get_trend_status(current_price, high_52wk, low_52wk):
    return "UPTREND" / "NEUTRAL" / "DOWNTREND"

# NEW (technical indicators)
def get_trend_analysis(ticker, current_price):
    """
    Enhanced trend analysis using technical indicators
    Returns: {
        'status': 'UPTREND',        # Category
        'score': 85,                 # 0-100 composite
        'ma_alignment': 'BULLISH',   # MA positioning
        'rsi': 62.5,                 # Current RSI
        'macd_signal': 'BULLISH',    # MACD vs Signal
        'volume_trend': 'STRONG',    # Volume analysis
        'confidence': 'HIGH'         # Overall confidence
    }
    """
    # 1. Load/fetch price history
    # 2. Calculate technical indicators
    # 3. Score each component
    # 4. Return composite analysis
    pass
```

---

### Step 4: Update Dashboard GUI ✅
**File**: `wishlist_tracker/gui/dashboard_gui.py`

**Current "Trend" Column**:
- Shows: "Uptrend" / "Neutral" / "Downtrend"
- Width: 120px

**Enhanced "Trend" Column**:
- Shows: "🟢 85 UPTREND" (emoji + score + category)
- Width: 140px (need more space for score)
- Tooltip: Hover shows breakdown (MA: 30, RSI: 25, MACD: 15, Vol: 15)

**Color Coding**:
- 🟢 Green: Score 75-100 (STRONG BUY / UPTREND)
- 🟡 Yellow: Score 40-74 (BULLISH / NEUTRAL)
- 🟠 Orange: Score 25-39 (WEAK)
- 🔴 Red: Score 0-24 (DOWNTREND)

---

### Step 5: Integration Testing ✅
**Test Cases**:

1. **Strong Uptrend Stock** (NVDA-type)
   - Expected: Score 85-100, all indicators aligned
   - Verify: MA alignment, RSI 50-70, MACD positive, volume strong

2. **Neutral Stock** (Sideways range)
   - Expected: Score 40-60, mixed signals
   - Verify: Price near MA-50, RSI 40-60, MACD flat

3. **Downtrend Stock** (Declining)
   - Expected: Score 0-25, negative indicators
   - Verify: Price < all MAs, RSI <40, MACD negative

4. **Overbought Stock** (Parabolic move)
   - Expected: Score 60-75 (not 90+), RSI >70 warning
   - Verify: RSI penalty applied, caution flagged

---

## 📊 PERFORMANCE CONSIDERATIONS

### Data Requirements
- **90 days of OHLCV data** per ticker (minimum for 200-day SMA requires historical data)
- **API Calls**: 1 per ticker per day (cached 24 hours)
- **Storage**: ~5KB per ticker JSON file
- **23 tickers × 5KB = 115KB total** (negligible)

### Calculation Speed
- **Technical indicators**: ~10-20ms per ticker (Python loops)
- **Total dashboard load**: 23 tickers × 20ms = **~460ms overhead**
- **Acceptable**: <1 second total (current load time ~3-5 seconds)

### Optimization Options
1. **Pre-calculate on cache load** (calculate once when fetching history)
2. **Parallel processing** (calculate all tickers simultaneously)
3. **NumPy vectorization** (faster array operations)

---

## 🎯 SUCCESS METRICS

### Technical Validation
- [ ] All 4 indicators calculate correctly
- [ ] Scores match manual verification
- [ ] Cache system working (no redundant API calls)
- [ ] Dashboard displays enhanced trend data

### Business Validation
- [ ] Identify overbought conditions (avoid bad entries)
- [ ] Confirm strong trends (confidence in put selling)
- [ ] Spot trend reversals early (exit signals)
- [ ] Improve win rate by 10-15% vs placeholder trend

---

## 🚀 ROLLOUT PLAN

### Week 1: Core Infrastructure ✅
- Day 1: Create `price_history.py` with E*TRADE integration
- Day 2: Implement caching system
- Day 3: Test data fetching for all 23 tickers

### Week 2: Indicator Calculations ✅
- Day 1: Implement MA calculations (SMA, EMA)
- Day 2: Implement RSI calculation
- Day 3: Implement MACD calculation
- Day 4: Implement volume analysis

### Week 3: Scoring & Integration ✅
- Day 1: Build composite scoring engine
- Day 2: Upgrade `trend_analysis.py`
- Day 3: Update dashboard GUI
- Day 4: Integration testing

### Week 4: Testing & Refinement ✅
- Day 1-2: Test with live market data
- Day 3: Tune scoring weights if needed
- Day 4: User feedback & adjustments

---

## 🔧 DEPENDENCIES

### Python Libraries (Already Available)
- `pandas`: DataFrame operations ✅
- `numpy`: Fast array calculations ✅
- `requests`: API calls ✅
- `json`: Caching ✅

### E*TRADE API Endpoints
- `/market/quote/{symbol}`: Current price + indicators
- Historical data might require separate endpoint or third-party (yfinance as fallback)

---

## 📝 NOTES & CONSIDERATIONS

### API Limitations
- **E*TRADE**: May not provide full 90-day history in quote endpoint
- **Fallback**: Use `yfinance` library for historical data (free, reliable)
- **Hybrid approach**: E*TRADE for current price, yfinance for history

### Indicator Tuning
- **Default periods** (14 RSI, 20/50/200 MA) are industry standard
- **User feedback** after 1-2 weeks will guide weight adjustments
- **Example**: If RSI overbought warnings too sensitive, reduce RSI weight from 30 to 25

### Future Enhancements (Phase 4+)
- **Bollinger Bands**: Volatility analysis
- **ATR**: Average True Range for position sizing
- **Fibonacci Retracements**: Support/resistance levels
- **Chart Visualization**: Matplotlib plots in separate window

---

## ✅ PHASE 3 COMPLETION CRITERIA

- [ ] Price history fetching working (E*TRADE or yfinance)
- [ ] All 4 indicators calculating correctly
- [ ] Composite scoring (0-100) implemented
- [ ] Dashboard showing enhanced trend scores
- [ ] Caching system operational (24hr refresh)
- [ ] Testing complete with 3+ validation cases
- [ ] User testing feedback positive
- [ ] Documentation updated

---

## 🎯 READY TO START?

**First Command**: 
```bash
python -m pip install yfinance  # If not already installed (fallback for historical data)
```

**First File to Create**:
`wishlist_tracker/utils/price_history.py`

Let me know when you're ready and I'll start implementing! 🚀

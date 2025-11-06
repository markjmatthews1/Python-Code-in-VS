# Wishlist Tracker - Enhanced Put Selection Strategy

**Status**: ✅ INTEGRATED (October 17, 2025)

## Overview

The Wishlist Tracker has been upgraded with an **enhanced put selection algorithm** that prioritizes **cost basis quality** and **capital efficiency** over raw premium dollars.

## What Changed

### Before (ROI-Only Strategy)
- Sorted options by **daily ROI** (highest first)
- Could recommend deep ITM puts with high assignment risk
- Example: 1x $85 put @ $40.70 (cost basis $44.30 - underwater!)
- Focused only on premium income

### After (Enhanced Multi-Factor Strategy)
- **Weighted scoring system** balancing 5 factors:
  1. **Cost Basis (30%)**: Lower entry price if assigned
  2. **Premium Dollars (25%)**: Income per contract
  3. **Time Efficiency (20%)**: Premium per day
  4. **Safety Cushion (15%)**: Downside protection %
  5. **Liquidity (10%)**: Ease of execution
- Considers **trend direction** for strike selection
- Example: 2x $42 put @ $5.20 (cost basis $36.80, 15.4% cushion) ✅

## Scoring Formula

```python
# Component Scores (0-100 each)

Cost Basis Score (30% weight):
  - 20%+ below current price → 100 points (Excellent)
  - 15-20% below → 85 points
  - 10-15% below → 70 points
  - 5-10% below → 50 points
  - 0-5% below → 25 points
  - Above current price → 0 points (Underwater - avoid!)

Premium Score (25% weight):
  - $6.00+ premium → 100 points (Excellent)
  - $5.00-6.00 → 85 points
  - $4.00-5.00 → 70 points
  - $3.00-4.00 → 55 points
  - $2.00-3.00 → 40 points (Minimum acceptable)
  - < $2.00 → 0 points (Filtered out)

Time Efficiency Score (20% weight):
  - $0.30+/day → 100 points (Excellent time value)
  - $0.20-0.30/day → 80 points
  - $0.15-0.20/day → 60 points
  - $0.10-0.15/day → 40 points
  - < $0.10/day → 20 points (Poor time value)

Safety Cushion Score (15% weight):
  - 20%+ cushion → 100 points (Very safe)
  - 15-20% cushion → 80 points
  - 10-15% cushion → 60 points
  - 5-10% cushion → 40 points
  - 0-5% cushion → 20 points
  - Negative cushion → 0 points (Underwater)

Liquidity Score (10% weight):
  - Already calculated (0-100 from spread, OI, volume, bid size)

Final Score = Weighted Sum × Trend Multiplier
```

## Trend Adjustment

The system adjusts strike preferences based on stock trend:

**Strong Uptrend** (e.g., "100 Strong Buy"):
- Can use strikes closer to current price (95-100%)
- Rewards near-ATM puts (1.10x multiplier)
- Stock likely to stay elevated

**Neutral/Sideways**:
- Sweet spot: 85-95% of current price
- Balanced risk/reward (1.00x multiplier)

**Downtrend**:
- Needs wider cushion (75-90% of current)
- Rewards safer strikes (1.05x multiplier)
- More conservative approach

**Strong Downtrend**:
- Very conservative (70-85% of current)
- Rewards very safe strikes (1.10x multiplier)
- Avoid assignment risk

## Real-World Example: SMR

**Current Price**: $43.50  
**Trend**: Strong Uptrend (100 Strong Buy)

### Old Recommendation (48.4/100 score)
```
1x $85 strike @ $40.70 premium
Capital Required: $8,500
Cost Basis: $44.30/share (UNDERWATER by 1.8%!)
Cushion: -$80
Premium/Day: $1.94
```

**Problems**:
- ❌ Cost basis above current price
- ❌ Immediate underwater if assigned
- ❌ Deep ITM = high assignment risk
- ❌ Poor capital efficiency

### New Recommendation (90.5/100 score)
```
2x $42 strike @ $5.20 premium
Capital Required: $8,400
Cost Basis: $36.80/share (15.4% cushion)
Cushion: +$670 per contract
Premium/Day: $0.25 per contract
```

**Advantages**:
- ✅ Cost basis 15.4% below current price
- ✅ Happy to own stock at this price
- ✅ Better time efficiency (11/7 vs longer expirations)
- ✅ Same capital, much better protection

**Score Improvement**: +42.0 points!

## Time Value Comparison

The system now compares premium efficiency across different expirations:

```
11/7 Expiration (21 days):
  2x $42 @ $5.20 = $1,040 total premium
  Premium/Day: $0.50 total ($0.25 per contract)
  
11/21 Expiration (35 days):
  2x $42 @ $6.00 = $1,200 total premium
  Premium/Day: $0.34 total ($0.17 per contract)
  
Insight: 11/7 is 44% more time-efficient!
  - Collect $1,040 in 21 days
  - Then roll or open new puts
  - vs. tying up capital 14 extra days for only $160 more
```

## Files Modified

1. **`wishlist_tracker/utils/enhanced_put_strategy.py`** (NEW)
   - Core scoring algorithms
   - Multi-contract strategy generator
   - Formatting utilities

2. **`wishlist_tracker/utils/option_chain.py`** (MODIFIED)
   - Added import for enhanced_put_strategy
   - Modified `fetch_put_option_chain()` function
   - Changed sorting from daily_roi to enhanced_score
   - Added new fields to candidate dictionaries

## New Data Fields

Options returned by `fetch_put_option_chain()` now include:

```python
{
    # ... existing fields ...
    
    # Enhanced scoring fields:
    'enhanced_score': 90.5,           # Overall quality score (0-100)
    'cost_basis_score': 85.0,         # Cost basis component (0-100)
    'premium_score': 85.0,            # Premium component (0-100)
    'time_score': 80.0,               # Time efficiency component (0-100)
    'cushion_score': 80.0,            # Safety cushion component (0-100)
    'cushion_percent': 15.4,          # Downside protection percentage
    'premium_per_day': 0.25,          # Premium dollars per day
    'premium_yield': 12.4,            # Premium as % of strike
    'strike_vs_current': 96.6,        # Strike as % of current price
}
```

## Testing

Run the test suite to verify scoring:

```bash
# Basic scoring test
python test_wishlist_integration.py

# Full SMR example with multiple strategies
python test_smr_strategy.py
```

Expected output:
- ✅ Good puts score 90-100/100
- ❌ Bad puts score <60/100
- 🎯 SMR 2x $42 @ $5.20 ranks #1

## Usage

The enhanced scoring is **automatically integrated**. No code changes needed in:
- GUI (`wishlist_tracker/gui/app.py`)
- Main application logic
- Display formatting

The system will now:
1. Fetch option chains as before
2. Apply enhanced scoring to each option
3. Return top 3 by enhanced_score (not daily_roi)
4. Display better recommendations automatically

## Configuration

To adjust scoring weights, edit `enhanced_put_strategy.py`:

```python
# In score_put_strategy() function:

weighted_score = (
    cost_basis_score * 0.30 +      # Adjust these weights
    premium_score * 0.25 +          # to match your preferences
    time_score * 0.20 +
    cushion_score * 0.15 +
    liquidity_normalized * 0.10
)
```

## Benefits

1. **Safer Assignments**: Prioritizes strikes you'd be happy to own
2. **Capital Efficiency**: Compares multiple contract strategies
3. **Time Awareness**: Values shorter, more efficient expirations
4. **Trend Aware**: Adjusts strike selection based on stock direction
5. **Balanced Approach**: Doesn't just chase highest premium

## Next Steps (Optional Enhancements)

- [ ] Integrate real analyst ratings for trend_direction
- [ ] Add user-configurable scoring weights
- [ ] Show side-by-side strategy comparisons in GUI
- [ ] Add "multiple contracts" view (1x, 2x, 3x strategies)
- [ ] Expand expiration range to 7-90 days (currently 30-60)

## Summary

The Wishlist Tracker now recommends puts that:
- ✅ Give you a **good cost basis** if assigned
- ✅ Provide **solid premium income**
- ✅ Use capital **efficiently** (multiple contracts at lower strikes)
- ✅ Match the **stock's trend** direction
- ✅ Have good **liquidity** for easy fills

**Result**: Better puts, safer assignments, more efficient capital usage! 🎯

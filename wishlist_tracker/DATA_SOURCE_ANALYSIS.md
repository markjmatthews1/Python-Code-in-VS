# Wishlist Tracker - Put Option Data Source Analysis

## 📊 Data Source: **E*TRADE API**

### API Endpoint
```
Base URL: https://api.etrade.com/v1/market/optionchains
Method: GET
Authentication: OAuth 1.0
```

### Current Data Flow

#### 1. **Entry Point** (`dashboard_gui.py`)
```python
from wishlist_tracker.utils.option_chain import fetch_put_option_chain

# Called during data refresh:
puts = fetch_put_option_chain(inst.symbol, float(inst.current_price or 0))
```

#### 2. **Main Fetching Logic** (`utils/option_chain.py`)
```python
def fetch_put_option_chain(ticker, current_price):
    """Fetch put options for 2 months, find best negative premium with probability analysis"""
```

**Process:**
1. Gets E*TRADE session with OAuth tokens
2. Calculates 2 target expiration dates (3rd Friday rule)
3. Fetches option chains for each expiration
4. Parses XML response for put option data
5. Filters and scores options
6. Returns top 3 candidates

### 🔍 Current Filtering Logic

#### **Strike Price Filter**
```python
# Only options within ±$10 of current price
if abs(strike - current_price) <= 10.0 and bid > 0:
```

#### **Negative Premium Filter**
```python
net_cost_basis = strike - bid
negative_premium = current_price - net_cost_basis

# Only include if it's a true negative premium (profitable if assigned)
if negative_premium > 0:
```

#### **Expiration Filter**
- **Current month**: Used if >5 trading days remain until 3rd Friday
- **Next month**: Always included
- **Month after next**: Included if current month skipped
- **Result**: Always checking exactly 2 expiration dates

### 📈 Scoring System

#### **Combined Score Calculation**
```python
combined_score = (premium_income * 0.6) + (negative_premium * 0.4)
```

**Components:**
1. **Premium Income (60% weight)**: The actual cash you receive
2. **Negative Premium (40% weight)**: Protection/profit if assigned

#### **Additional Metrics Calculated**
```python
# Expected value (probability-weighted)
expected_value = (premium_income * probability) + (negative_premium * (1 - probability))

# Premium yield (annualized percentage)
premium_yield = (premium_income / strike) * 100
```

### 🎯 Probability Model

```python
def calculate_probability_above_strike(current_price, strike_price, days_to_expiry):
```

**Factors:**
1. **Price Buffer** (Distance from current to strike)
   - 15%+ buffer → 85% probability
   - 10-15% buffer → 75% probability
   - 5-10% buffer → 65% probability
   - 2-5% buffer → 55% probability
   - At/near money → 50% probability
   - In the money → 30% probability

2. **Time Adjustment**
   - >45 days → -10% (more risk)
   - 30-45 days → -5%
   - 14-30 days → no adjustment
   - <14 days → +5% (safer)

### 🔴 Current Issues / Limitations

#### **1. No Bid-Ask Spread Filter**
- **Problem**: Some options show unrealistic bids with wide spreads
- **Example**: Bid=$10, Ask=$15 (50% spread = likely no real market)
- **Impact**: Misleading premiums that may not be executable

#### **2. No Volume/Open Interest Filter**
- **Problem**: Low liquidity options included
- **Result**: May not be able to execute at displayed prices

#### **3. No Premium-to-Strike Ratio Cap**
- **Problem**: Extremely high premiums (>50% of strike) likely wishful thinking
- **Example**: $20 strike with $15 premium = 75% premium/strike ratio
- **Reality**: Usually indicates deep ITM or data error

#### **4. No Implied Volatility Check**
- **Problem**: High IV options may look attractive but carry extreme risk
- **Missing**: Volatility context for premium evaluation

#### **5. Simple Probability Model**
- **Current**: Rule-based estimates
- **Better**: Could use Black-Scholes or historical volatility

### 📝 What Data We're Getting

From E*TRADE API XML Response:
```xml
<OptionPair>
  <Put>
    <displaySymbol>NVDL 251219P00095000</displaySymbol>
    <strikePrice>95.0</strikePrice>
    <bid>17.20</bid>
    <ask>17.50</ask>
  </Put>
</OptionPair>
```

**Available but NOT Currently Used:**
- Volume
- Open Interest  
- Implied Volatility
- Greeks (Delta, Gamma, Theta, Vega)
- Last trade price/time

### 💡 Recommended Filter Additions

#### **1. Bid-Ask Spread Filter**
```python
# Only include options with reasonable spreads
spread = ask - bid
spread_percentage = (spread / bid) * 100
if spread_percentage <= 20:  # Max 20% spread
    # Include option
```

#### **2. Premium-to-Strike Ratio Cap**
```python
# Flag unrealistic premiums
premium_ratio = (bid / strike) * 100
if premium_ratio <= 40:  # Max 40% of strike
    # Include option
```

#### **3. Minimum Liquidity Check**
```python
# Require some market activity (if available from API)
if volume > 10 or open_interest > 50:
    # Include option
```

#### **4. Maximum Distance from Current Price**
```python
# Already have ±$10 filter, could make it percentage-based
price_distance_pct = abs(strike - current_price) / current_price
if price_distance_pct <= 0.15:  # Within 15% of current
    # Include option
```

### 🎯 Next Steps

1. **Identify problematic examples** - Which specific tickers showing unrealistic premiums?
2. **Add spread filter** - Eliminate wide bid-ask spreads
3. **Add premium ratio cap** - Flag suspicious high premiums
4. **Enhance data display** - Show spread, volume, open interest in GUI
5. **Improve probability model** - Use more sophisticated calculations

---

**Date Created:** October 16, 2025
**Current Version:** Wishlist Tracker v2.1
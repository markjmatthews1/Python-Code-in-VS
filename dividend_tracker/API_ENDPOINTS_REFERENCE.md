# API ENDPOINTS QUICK REFERENCE
## Critical endpoints for E*TRADE and Schwab integration

---

## 🏦 **E*TRADE API ENDPOINTS**

### **Authentication:**
- Uses `etrade_auth.py` OAuth1 system
- Tokens stored automatically, refresh as needed

### **Account List:**
```
GET https://api.etrade.com/v1/accounts/list.json
```

### **Positions (CRITICAL):**
```
GET https://api.etrade.com/v1/accounts/{accountId}/portfolio.json
```
**Key Response Fields:**
- `AccountPortfolio.Position[].Product.symbol`
- `AccountPortfolio.Position[].quantity` 
- `AccountPortfolio.Position[].marketValue`

### **Dividend/Yield Data (CRITICAL):**
```
GET https://api.etrade.com/v1/market/quote/{symbol}.json
```
**Key Response Fields:**
- `QuoteResponse.QuoteData[0].All.yield` (dividend yield %)
- `QuoteResponse.QuoteData[0].All.dividend` (weekly/period amount)
- `QuoteResponse.QuoteData[0].All.declaredDividend` (declared amount)
- `QuoteResponse.QuoteData[0].All.lastTrade` (current price)

**⚠️ SPECIAL CASE - QDTE (Weekly Payer):**
- Use `dividend` or `declaredDividend` field = $0.286/week
- Annual = $0.286 × 52 = $14.872/year
- Yield = ($14.872 ÷ price) × 100

---

## 🏦 **SCHWAB API ENDPOINTS**

### **Authentication:**
- Uses `Schwab_auth.py` OAuth2 system  
- Call `get_valid_access_token()` for auto-refresh
- Tokens in `tokens.json` (main directory)

### **Accounts + Positions (RECOMMENDED):**
```
GET https://api.schwabapi.com/trader/v1/accounts?fields=positions
```
**Key Response Fields:**
- `[].securitiesAccount.accountNumber`
- `[].securitiesAccount.positions[].instrument.symbol`
- `[].securitiesAccount.positions[].longQuantity` ⚠️ (NOT quantity)
- `[].securitiesAccount.positions[].marketValue`

### **Account Balances:**
```
GET https://api.schwabapi.com/trader/v1/accounts
```
**Balance Logic:**
- Account `91562183` (IRA): Use `initialBalances.equity`
- Account `74501314` (Individual): Use `currentBalances.equity`

---

## 🔧 **TROUBLESHOOTING**

### **E*TRADE 401 Error:**
```bash
cd "c:\Users\mjmat\Python Code in VS"
python etrade_auth.py
```

### **Schwab 401 Error:**
- Schwab_auth handles auto-refresh
- If persistent, may need re-authentication

### **Missing Positions:**
- E*TRADE: Check account type mapping
- Schwab: Ensure `?fields=positions` parameter
- Schwab: Use `longQuantity` not `quantity`

### **Wrong QDTE Yield:**
- Must use `dividend`/`declaredDividend` fields
- Calculate: weekly × 52 weeks
- NOT the `yield` field (shows 9.88% vs actual 42.74%)

---

**Quick Access Files:**
- Main Collector: `dividend_tracker/DividendTrackerApp/portfolio_data_collector.py`
- E*TRADE API: `dividend_tracker/DividendTrackerApp/modules/etrade_account_api.py`  
- Schwab Auth: `Schwab_auth.py` (main directory)
- Integration Test: `dividend_tracker/DividendTrackerApp/test_dual_broker_integration.py`

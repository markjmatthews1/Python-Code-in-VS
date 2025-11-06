"""
Configuration settings for the trading application
"""

# ====== AI Trading Settings ======
AI_PROB_THRESHOLD = 0.55        # Lower from 0.6 to 0.55 for more trades
AI_VOLATILITY_THRESHOLD = 0.015  # 1.5% instead of 0.5% for ETFs
AI_TARGET_PERCENT = 0.02         # 2% target
AI_STOP_PERCENT = 0.01          # 1% stop loss

# Volatility settings by asset type (OPTIMIZED for current market conditions - Oct 2025)
# Lowered 75% from previous values to match observed intraday volatility
VOLATILITY_THRESHOLDS = {
    "leveraged_etf": 0.0005,    # 0.05% for 3x leveraged ETFs (was 0.2%, reduced 75%)
    "regular_etf": 0.0003,      # 0.03% for regular ETFs (was 0.1%, reduced 70%)  
    "individual_stock": 0.0008, # 0.08% for individual stocks (was 0.3%, reduced 73%)
    "crypto_etf": 0.001,        # 0.1% for crypto ETFs (was 0.5%, reduced 80%)
    "default": 0.0005           # 0.05% default (was 0.2%, reduced 75%)
}

# Define which tickers are leveraged ETFs
LEVERAGED_ETFS = ["TQQQ", "TECL", "MSTX", "BITU", "ETHU", "NVDU", "LABU", 
                  "GDXU", "NUGT", "SMCX", "JNUG", "NAIL", "DFEN", "ERX", 
                  "SDOW", "BOIL", "MSFU", "TSLT", "SSO", "SDS", "AGQ"]

def get_volatility_threshold(ticker):
    """Get appropriate volatility threshold based on ticker type"""
    ticker = ticker.upper()
    
    if ticker in LEVERAGED_ETFS:
        return VOLATILITY_THRESHOLDS["leveraged_etf"]
    elif ticker.endswith("ETH") or ticker.endswith("BTC") or ticker in ["BITU", "ETHU"]:
        return VOLATILITY_THRESHOLDS["crypto_etf"] 
    elif ticker == "AMD":  # Individual stock in your list
        return VOLATILITY_THRESHOLDS["individual_stock"]
    else:
        return VOLATILITY_THRESHOLDS["default"]
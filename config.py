"""
Configuration settings for the trading application
"""

# ====== AI Trading Settings ======
AI_PROB_THRESHOLD = 0.55        # Lower from 0.6 to 0.55 for more trades
AI_VOLATILITY_THRESHOLD = 0.015  # 1.5% instead of 0.5% for ETFs
AI_TARGET_PERCENT = 0.02         # 2% target
AI_STOP_PERCENT = 0.01          # 1% stop loss

# Volatility settings by asset type (LOWERED for intraday trading)
VOLATILITY_THRESHOLDS = {
    "leveraged_etf": 0.002,     # 0.2% for 3x leveraged ETFs (was 1.5%)
    "regular_etf": 0.001,       # 0.1% for regular ETFs (was 0.8%)  
    "individual_stock": 0.003,  # 0.3% for individual stocks (was 1.2%)
    "crypto_etf": 0.005,        # 0.5% for crypto ETFs (was 2.0%)
    "default": 0.002            # 0.2% default (was 1.0%)
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
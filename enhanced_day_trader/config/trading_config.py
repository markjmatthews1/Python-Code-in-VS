#!/usr/bin/env python3
"""
Enhanced Day Trader Configuration
=================================

Configuration settings for the enhanced day trading system.
Separate from original app to avoid conflicts.

Author: GitHub Copilot
Date: September 26, 2025
"""

# ====== ENHANCED RISK MANAGEMENT SETTINGS ======

# NEW: Optimized Risk/Reward Ratios
ENHANCED_TARGET_PCT = 0.008      # 0.8% profit target (vs old 2.0%)
ENHANCED_STOP_PCT = 0.004        # 0.4% stop loss (vs old 1.0%)
RISK_REWARD_RATIO = 2.0          # 2:1 favorable ratio (vs old 1:2)

# Position Sizing
MAX_RISK_PER_TRADE = 0.01        # 1% of account per trade
MAX_DAILY_RISK = 0.05            # 5% of account per day max
MAX_POSITION_PCT = 0.25          # 25% of account max position size
MAX_SINGLE_STOCK_PCT = 0.10      # 10% max in single stock

# ====== ENHANCED FEATURE SELECTION ======

# Reduced feature set to prevent overfitting
ESSENTIAL_FEATURES = [
    # Price action (most predictive)
    'close',
    'returns',
    'volume',
    
    # Key technical indicators  
    'rsi_14',
    'macd',
    'macd_signal',
    
    # Market context
    'volume_ratio',      # Current vs average volume
    'time_of_day',       # Hour of day patterns
    'bb_position',       # Bollinger Band position
    'atr_pct'           # Volatility measure
]

# Features to EXCLUDE (caused overfitting in original)
EXCLUDED_FEATURES = [
    'sma_5', 'sma_20', 'ema_5', 'ema_20',  # Redundant with close/returns
    'bb_upper', 'bb_lower',                # Use bb_position instead  
    'vol_sma_20',                          # Use volume_ratio instead
    'news_sentiment_mean', 'news_count',   # Too noisy for day trading
    'whale_trade_count', 'whale_volume',   # Delayed data
    'congress_trade_count_30d',            # Too slow for day trading
    'inst_trade_count_30d'                 # Too slow for day trading
]

# ====== TIME-BASED FILTERS ======

# Optimal trading hours (avoid volatility at open/close)
OPTIMAL_TRADING_HOURS = [
    (10.0, 11.5),   # 10:00 AM - 11:30 AM
    (13.5, 15.5)    # 1:30 PM - 3:30 PM
]

# Avoid these times (too volatile or low volume)
AVOID_TRADING_HOURS = [
    (9.5, 10.0),    # Market open chaos
    (11.5, 13.5),   # Lunch time low volume  
    (15.5, 16.0)    # Market close unpredictability
]

# ====== ENSEMBLE SIGNAL REQUIREMENTS ======

# Require multiple confirmations before trade entry
MIN_SIGNAL_CONFIRMATIONS = 2

# Signal types and weights
SIGNAL_TYPES = {
    'ai_prediction': 1.0,        # ML model prediction
    'technical_alignment': 1.0,   # Technical indicators aligned
    'volume_confirmation': 1.0,   # Above-average volume
    'time_filter': 0.5,          # Optimal time of day
    'volatility_check': 0.5      # Appropriate volatility
}

# ====== MACHINE LEARNING SETTINGS ======

# Model parameters
MODEL_CONFIG = {
    'algorithm': 'RandomForestClassifier',
    'n_estimators': 100,          # Reduced from potentially higher
    'max_depth': 8,               # Prevent overfitting
    'min_samples_split': 10,      # Prevent overfitting  
    'min_samples_leaf': 5,        # Prevent overfitting
    'max_features': 'sqrt',       # Feature subsampling
    'class_weight': 'balanced',   # Handle class imbalance
    'random_state': 42
}

# Training parameters
TRAINING_CONFIG = {
    'test_size': 0.2,
    'validation_size': 0.2, 
    'cross_validation_folds': 5,
    'feature_importance_threshold': 0.01,  # Remove low-importance features
    'max_lookahead_bars': 20,              # Reduced from 30 for day trading
    'min_training_samples': 1000
}

# ====== DATA MANAGEMENT ======

# File paths (separate from original app)
DATA_CONFIG = {
    'historical_data': 'enhanced_historical_data.csv',
    'minute_data': 'enhanced_minute_data.csv', 
    'trade_log': 'enhanced_trade_log.csv',
    'performance_log': 'enhanced_performance.csv',
    'model_file': 'enhanced_model.pkl',
    'predictions_log': 'enhanced_predictions.csv'
}

# Cache settings
CACHE_CONFIG = {
    'news_cache': 'enhanced_news_cache.json',
    'whale_cache': 'enhanced_whale_cache.json',
    'market_data_cache': 'enhanced_market_cache.json',
    'cache_expiry_hours': 1  # Shorter cache for day trading
}

# ====== DASHBOARD SETTINGS ======

# Separate port from original app to avoid conflicts
DASHBOARD_CONFIG = {
    'port': 8051,                    # Original uses 8050
    'host': '127.0.0.1',
    'debug': False,
    'auto_refresh_seconds': 30,
    'max_chart_points': 100
}

# ====== ALERT SETTINGS ======

ALERT_CONFIG = {
    'enable_audio': True,
    'enable_desktop': True, 
    'min_signal_strength': 0.7,     # Higher threshold
    'max_alerts_per_hour': 10,      # Rate limiting
    'alert_cooldown_minutes': 15    # Prevent spam
}

# ====== VALIDATION THRESHOLDS ======

# Performance validation requirements before live trading
VALIDATION_THRESHOLDS = {
    'min_backtest_win_rate': 0.55,     # 55% minimum in backtesting
    'min_paper_trade_days': 30,        # 30 days paper trading
    'min_paper_trade_win_rate': 0.50,  # 50% minimum in paper trading
    'max_drawdown_limit': 0.10,        # 10% max drawdown
    'min_trades_for_validation': 100    # Minimum trade sample size
}

# ====== LOGGING AND MONITORING ======

LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'enhanced_trader.log',
    'max_file_size': 10485760,  # 10MB
    'backup_count': 5
}

def get_config_summary():
    """Return a summary of key configuration differences"""
    return {
        'system_type': 'Enhanced Day Trader v2.0',
        'risk_reward_ratio': f"{RISK_REWARD_RATIO}:1",
        'target_profit': f"{ENHANCED_TARGET_PCT*100:.1f}%", 
        'stop_loss': f"{ENHANCED_STOP_PCT*100:.1f}%",
        'features_count': len(ESSENTIAL_FEATURES),
        'excluded_count': len(EXCLUDED_FEATURES),
        'trading_hours': len(OPTIMAL_TRADING_HOURS),
        'dashboard_port': DASHBOARD_CONFIG['port'],
        'min_confirmations': MIN_SIGNAL_CONFIRMATIONS,
        'breakeven_win_rate': f"{ENHANCED_STOP_PCT/(ENHANCED_TARGET_PCT+ENHANCED_STOP_PCT)*100:.0f}%"
    }

if __name__ == "__main__":
    print("Enhanced Day Trader Configuration")
    print("=" * 40)
    
    summary = get_config_summary()
    for key, value in summary.items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print(f"\nKey Improvements vs Original:")
    print(f"- Better risk/reward: 2:1 vs 1:2")
    print(f"- Fewer features: {len(ESSENTIAL_FEATURES)} vs 30+")
    print(f"- Time filters: {len(OPTIMAL_TRADING_HOURS)} optimal windows")
    print(f"- Separate port: {DASHBOARD_CONFIG['port']} vs 8050")
    print(f"- Win rate needed: {ENHANCED_STOP_PCT/(ENHANCED_TARGET_PCT+ENHANCED_STOP_PCT)*100:.0f}% vs 67%")
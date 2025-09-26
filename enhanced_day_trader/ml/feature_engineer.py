#!/usr/bin/env python3
"""
Enhanced Feature Selection and Engineering Module
=================================================

Handles reduced feature set to prevent overfitting that plagued the original system.
Focus on the most predictive indicators for day trading.

Key Improvements:
- Reduced from 30+ features to 10 essential features
- Eliminates redundant and noisy signals  
- Time-based feature engineering for intraday patterns
- Volume-based confirmations

Author: GitHub Copilot
Date: September 26, 2025
"""

import pandas as pd
import numpy as np
import talib
from datetime import datetime
import logging

# Import our configuration
from ..config.trading_config import ESSENTIAL_FEATURES, EXCLUDED_FEATURES

logger = logging.getLogger(__name__)

class EnhancedFeatureEngineer:
    """
    Feature engineering focused on quality over quantity.
    Addresses the overfitting problem in the original system.
    """
    
    def __init__(self):
        self.feature_history = {}
        self.volume_lookback = 20  # Days for volume average
        
    def engineer_essential_features(self, df):
        """
        Create only the essential features that provide real predictive value.
        Dramatically reduced from original feature set.
        """
        logger.info(f"Engineering {len(ESSENTIAL_FEATURES)} essential features")
        
        # Ensure we have required columns
        if not all(col in df.columns for col in ['open', 'high', 'low', 'close', 'volume']):
            raise ValueError("Missing required OHLCV columns")
        
        # Make copy to avoid modifying original
        result_df = df.copy()
        
        # ====== PRICE ACTION FEATURES (Most Predictive) ======
        
        # Returns (most important feature)
        result_df['returns'] = result_df['close'].pct_change()
        
        # Volume ratio (current vs 20-period average)
        result_df['volume_sma_20'] = result_df['volume'].rolling(20).mean()
        result_df['volume_ratio'] = result_df['volume'] / result_df['volume_sma_20']
        result_df.drop('volume_sma_20', axis=1, inplace=True)  # Drop intermediate
        
        # ====== KEY TECHNICAL INDICATORS ======
        
        # RSI (14-period standard)
        result_df['rsi_14'] = talib.RSI(result_df['close'].values, timeperiod=14)
        
        # MACD (12,26,9 standard)
        macd, macd_signal, macd_hist = talib.MACD(
            result_df['close'].values,
            fastperiod=12,
            slowperiod=26, 
            signalperiod=9
        )
        result_df['macd'] = macd
        result_df['macd_signal'] = macd_signal
        
        # ====== MARKET CONTEXT FEATURES ======
        
        # Time of day (hour as decimal)
        if 'timestamp' in result_df.columns:
            result_df['datetime'] = pd.to_datetime(result_df['timestamp'])
            result_df['time_of_day'] = (
                result_df['datetime'].dt.hour + 
                result_df['datetime'].dt.minute / 60.0
            )
        else:
            # Use index if timestamp not available
            result_df['time_of_day'] = pd.to_datetime(result_df.index).hour
            
        # Bollinger Band position (0-1 normalized)
        bb_upper, bb_middle, bb_lower = talib.BBANDS(
            result_df['close'].values,
            timeperiod=20,
            nbdevup=2,
            nbdevdn=2
        )
        result_df['bb_position'] = (
            (result_df['close'] - bb_lower) / (bb_upper - bb_lower)
        ).clip(0, 1)  # Clip to 0-1 range
        
        # ATR as percentage of close (volatility measure)
        atr = talib.ATR(
            result_df['high'].values,
            result_df['low'].values, 
            result_df['close'].values,
            timeperiod=14
        )
        result_df['atr_pct'] = atr / result_df['close']
        
        # ====== FEATURE VALIDATION ======
        
        # Ensure all essential features are present
        missing_features = [f for f in ESSENTIAL_FEATURES if f not in result_df.columns]
        if missing_features:
            logger.warning(f"Missing essential features: {missing_features}")
            
        # Log feature creation success
        created_features = [f for f in ESSENTIAL_FEATURES if f in result_df.columns]
        logger.info(f"Successfully created {len(created_features)} essential features")
        
        return result_df
        
    def validate_feature_quality(self, df):
        """
        Validate that features have good quality and predictive potential.
        Check for common issues that caused problems in original system.
        """
        quality_report = {
            'total_features': len([f for f in ESSENTIAL_FEATURES if f in df.columns]),
            'issues': [],
            'warnings': []
        }
        
        for feature in ESSENTIAL_FEATURES:
            if feature not in df.columns:
                quality_report['issues'].append(f"Missing feature: {feature}")
                continue
                
            feature_data = df[feature]
            
            # Check for excessive NaN values
            nan_pct = feature_data.isna().sum() / len(feature_data)
            if nan_pct > 0.1:  # More than 10% NaN
                quality_report['warnings'].append(f"{feature}: {nan_pct:.1%} NaN values")
                
            # Check for constant values (no variance)
            if feature_data.std() == 0:
                quality_report['issues'].append(f"{feature}: Constant values (no variance)")
                
            # Check for extreme outliers (beyond 5 standard deviations)
            if feature_data.std() > 0:
                z_scores = np.abs((feature_data - feature_data.mean()) / feature_data.std())
                extreme_outliers = (z_scores > 5).sum()
                if extreme_outliers > len(feature_data) * 0.01:  # More than 1%
                    quality_report['warnings'].append(
                        f"{feature}: {extreme_outliers} extreme outliers"
                    )
        
        # Overall quality score
        issues_score = len(quality_report['issues']) * -2  # -2 per issue
        warnings_score = len(quality_report['warnings']) * -0.5  # -0.5 per warning
        quality_report['quality_score'] = max(0, 10 + issues_score + warnings_score)
        
        logger.info(f"Feature quality score: {quality_report['quality_score']:.1f}/10")
        
        return quality_report
        
    def remove_excluded_features(self, df):
        """
        Remove features that caused overfitting in the original system.
        These were identified as noisy or redundant.
        """
        removed_features = []
        
        for feature in EXCLUDED_FEATURES:
            if feature in df.columns:
                df.drop(feature, axis=1, inplace=True)
                removed_features.append(feature)
        
        if removed_features:
            logger.info(f"Removed {len(removed_features)} excluded features: {removed_features}")
            
        return df
        
    def get_feature_importance_baseline(self):
        """
        Return expected feature importance rankings based on day trading research.
        Used to validate that our reduced feature set focuses on the right signals.
        """
        importance_ranking = {
            # Price action (highest importance)
            'returns': 0.20,        # Price momentum
            'close': 0.15,          # Current price level
            'volume_ratio': 0.12,   # Volume confirmation
            
            # Technical indicators (medium importance)
            'rsi_14': 0.10,         # Momentum oscillator
            'macd': 0.08,           # Trend following
            'macd_signal': 0.08,    # Trend confirmation
            'atr_pct': 0.07,        # Volatility measure
            
            # Market context (lower but important)
            'time_of_day': 0.06,    # Intraday patterns
            'bb_position': 0.05,    # Overbought/oversold
            'volume': 0.04          # Raw volume
        }
        
        # Normalize to sum to 1.0
        total = sum(importance_ranking.values()) 
        normalized_importance = {k: v/total for k, v in importance_ranking.items()}
        
        return normalized_importance
        
    def create_feature_report(self, df):
        """
        Generate a comprehensive report on feature engineering results.
        """
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_rows': len(df),
            'feature_summary': {}
        }
        
        for feature in ESSENTIAL_FEATURES:
            if feature in df.columns:
                feature_data = df[feature]
                report['feature_summary'][feature] = {
                    'mean': float(feature_data.mean()) if pd.notna(feature_data.mean()) else None,
                    'std': float(feature_data.std()) if pd.notna(feature_data.std()) else None,
                    'min': float(feature_data.min()) if pd.notna(feature_data.min()) else None,
                    'max': float(feature_data.max()) if pd.notna(feature_data.max()) else None,
                    'nan_count': int(feature_data.isna().sum()),
                    'nan_pct': float(feature_data.isna().sum() / len(feature_data))
                }
        
        # Calculate improvement metrics vs original system
        original_feature_count = 30  # Estimated from original system
        current_feature_count = len([f for f in ESSENTIAL_FEATURES if f in df.columns])
        
        report['improvements'] = {
            'feature_reduction': f"{original_feature_count} → {current_feature_count}",
            'reduction_pct': f"{(1 - current_feature_count/original_feature_count)*100:.0f}%",
            'focus': "Quality over quantity - removed noisy/redundant features"
        }
        
        return report

def test_feature_engineering():
    """Test the enhanced feature engineering with sample data"""
    
    # Create sample OHLCV data
    dates = pd.date_range('2025-01-01', periods=100, freq='1min')
    np.random.seed(42)
    
    sample_data = pd.DataFrame({
        'timestamp': dates,
        'open': 100 + np.cumsum(np.random.randn(100) * 0.01),
        'high': 0,  # Will be filled
        'low': 0,   # Will be filled  
        'close': 0, # Will be filled
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # Create realistic OHLC from open
    for i in range(len(sample_data)):
        base = sample_data.loc[i, 'open']
        change = np.random.randn() * 0.005  # 0.5% typical change
        sample_data.loc[i, 'close'] = base * (1 + change)
        sample_data.loc[i, 'high'] = max(base, sample_data.loc[i, 'close']) * (1 + abs(np.random.randn()) * 0.002)
        sample_data.loc[i, 'low'] = min(base, sample_data.loc[i, 'close']) * (1 - abs(np.random.randn()) * 0.002)
    
    # Test feature engineering
    engineer = EnhancedFeatureEngineer()
    enhanced_data = engineer.engineer_essential_features(sample_data)
    quality_report = engineer.validate_feature_quality(enhanced_data)
    feature_report = engineer.create_feature_report(enhanced_data)
    
    print("Enhanced Feature Engineering Test Results")
    print("=" * 50)
    print(f"Original columns: {len(sample_data.columns)}")
    print(f"Enhanced columns: {len(enhanced_data.columns)}")
    print(f"Essential features created: {quality_report['total_features']}")
    print(f"Quality score: {quality_report['quality_score']:.1f}/10")
    
    if quality_report['issues']:
        print(f"Issues: {quality_report['issues']}")
    if quality_report['warnings']:
        print(f"Warnings: {quality_report['warnings']}")
    
    print("\nKey Features:")
    for feature in ESSENTIAL_FEATURES:
        if feature in enhanced_data.columns:
            data = enhanced_data[feature].dropna()
            if len(data) > 0:
                print(f"  {feature}: {data.mean():.4f} ± {data.std():.4f}")

if __name__ == "__main__":
    test_feature_engineering()
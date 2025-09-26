#!/usr/bin/env python3
"""
Enhanced Day Trading System Integration
=======================================

Integrates all enhanced components to create the improved trading system.
Targets 60-70% win rate vs original 24% by addressing core issues.

Key Integrations:
- Enhanced risk management (2:1 vs 1:2 ratio)
- Reduced feature set (10 vs 30+ features)
- Time-based filtering
- Ensemble signal confirmation
- Improved model training

Author: GitHub Copilot
Date: September 26, 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import asyncio
import logging
from typing import Dict, List, Optional, Tuple
import json
import os

# Import enhanced components
from .core.risk_manager import EnhancedRiskManager
from .core.time_filter import TimeBasedFilter
from .core.ensemble_signals import EnsembleSignalGenerator
from .ml.feature_engineer import EnhancedFeatureEngineer
from .ml.enhanced_trainer import EnhancedModelTrainer
from .auth.auth_manager import EnhancedAuthManager
from .config.trading_config import *

logger = logging.getLogger(__name__)

class EnhancedDayTradingSystem:
    """
    Complete enhanced day trading system.
    Addresses the 24% win rate issue through systematic improvements.
    """
    
    def __init__(self, config_override: Optional[Dict] = None):
        """
        Initialize the enhanced trading system.
        
        Args:
            config_override: Optional configuration overrides
        """
        # Apply config overrides
        if config_override:
            self._apply_config_override(config_override)
            
        # Initialize core components
        self.risk_manager = EnhancedRiskManager()
        self.time_filter = TimeBasedFilter()
        self.signal_generator = EnsembleSignalGenerator()
        self.feature_engineer = EnhancedFeatureEngineer()
        self.model_trainer = EnhancedModelTrainer()
        self.auth_manager = EnhancedAuthManager()
        
        # System state
        self.is_running = False
        self.current_positions = {}
        self.daily_stats = {
            'trades_taken': 0,
            'trades_won': 0,
            'daily_pnl': 0.0,
            'max_risk_used': 0.0
        }
        self.system_performance = {
            'total_trades': 0,
            'total_wins': 0,
            'total_pnl': 0.0,
            'win_rate': 0.0,
            'avg_win': 0.0,
            'avg_loss': 0.0,
            'profit_factor': 0.0
        }
        
        logger.info("Enhanced Day Trading System initialized")
        
    def _apply_config_override(self, config: Dict):
        """Apply configuration overrides"""
        # Update global config variables if needed
        for key, value in config.items():
            if hasattr(ENHANCED_TARGET_PCT, key):
                setattr(ENHANCED_TARGET_PCT, key, value)
                
    async def initialize_system(self) -> bool:
        """
        Initialize all system components and connections.
        
        Returns:
            bool: Success status
        """
        try:
            logger.info("Initializing enhanced trading system...")
            
            # Initialize authentication
            if not await self.auth_manager.initialize_auth():
                logger.error("Failed to initialize authentication")
                return False
                
            # Load or train ML model
            model_path = DATA_CONFIG['model_file']
            if os.path.exists(model_path):
                logger.info("Loading existing enhanced model...")
                if not self.model_trainer.load_model(model_path):
                    logger.warning("Failed to load model, will need training")
            else:
                logger.info("No existing model found, will need training")
                
            # Initialize risk manager with account info
            account_info = await self.auth_manager.get_account_info()
            if account_info:
                self.risk_manager.update_account_balance(
                    account_info.get('total_value', 100000)
                )
                
            logger.info("Enhanced trading system initialization complete")
            return True
            
        except Exception as e:
            logger.error(f"System initialization failed: {e}")
            return False
            
    async def process_market_data(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """
        Process market data through the enhanced pipeline.
        
        Args:
            symbol: Trading symbol
            market_data: Raw market data
            
        Returns:
            Optional[Dict]: Trading decision or None
        """
        try:
            current_time = datetime.now()
            
            # Step 1: Feature Engineering (reduced set)
            feature_data = self._prepare_features_from_market_data(market_data, symbol)
            if not feature_data:
                return None
                
            # Step 2: ML Model Prediction
            ml_signal = self._get_ml_prediction(feature_data)
            if not ml_signal:
                return None
                
            # Step 3: Prepare ensemble data
            ensemble_data = {
                'symbol': symbol,
                'ai_prediction': ml_signal.get('prediction', 0),
                'ai_confidence': ml_signal.get('confidence', 0),
                **feature_data  # Include all features for ensemble
            }
            
            # Step 4: Generate ensemble signal
            ensemble_result = self.signal_generator.generate_full_ensemble_signal(
                ensemble_data, current_time
            )
            
            # Step 5: Apply time filter
            if not ensemble_result.get('meets_threshold', False):
                logger.debug(f"Signal for {symbol} filtered out (insufficient confirmations)")
                return None
                
            # Step 6: Risk management check
            position_size = self.risk_manager.calculate_position_size(
                market_data.get('close', 0),
                ENHANCED_STOP_PCT
            )
            
            if position_size == 0:
                logger.debug(f"Position size for {symbol} is zero (risk limits)")
                return None
                
            # Step 7: Final trading decision
            trading_decision = {
                'symbol': symbol,
                'action': ensemble_result['direction'],
                'signal_strength': ensemble_result['signal_strength'],
                'confidence': ensemble_result['confidence'],
                'position_size': position_size,
                'entry_price': market_data.get('close', 0),
                'stop_loss': market_data.get('close', 0) * (1 - ENHANCED_STOP_PCT),
                'take_profit': market_data.get('close', 0) * (1 + ENHANCED_TARGET_PCT),
                'timestamp': current_time,
                'ensemble_components': ensemble_result['components'],
                'risk_reward_ratio': ENHANCED_TARGET_PCT / ENHANCED_STOP_PCT
            }
            
            logger.info(f"Trading decision: {symbol} {ensemble_result['direction']} "
                       f"(strength: {ensemble_result['signal_strength']:.2f})")
            
            return trading_decision
            
        except Exception as e:
            logger.error(f"Error processing market data for {symbol}: {e}")
            return None
            
    def _prepare_features_from_market_data(self, market_data: Dict, symbol: str) -> Optional[Dict]:
        """
        Prepare features from raw market data.
        
        Args:
            market_data: Raw market data
            symbol: Trading symbol
            
        Returns:
            Optional[Dict]: Prepared features or None if insufficient data
        """
        try:
            # Convert to DataFrame if needed
            if not isinstance(market_data, pd.DataFrame):
                # Assume it's current bar data, need historical context
                # This would typically fetch recent bars for indicators
                return self._get_historical_features(symbol, market_data)
            
            # Use feature engineer to process
            enhanced_data = self.feature_engineer.engineer_essential_features(market_data)
            
            # Return latest row as dict
            if len(enhanced_data) > 0:
                latest_features = enhanced_data.iloc[-1].to_dict()
                return latest_features
            
            return None
            
        except Exception as e:
            logger.error(f"Feature preparation failed for {symbol}: {e}")
            return None
            
    def _get_historical_features(self, symbol: str, current_data: Dict) -> Optional[Dict]:
        """
        Get historical data and calculate features for current bar.
        
        Args:
            symbol: Trading symbol
            current_data: Current bar data
            
        Returns:
            Optional[Dict]: Features with current values
        """
        # This would typically fetch recent historical data
        # For now, create mock features based on current data
        try:
            features = {
                'close': current_data.get('close', 0),
                'returns': current_data.get('returns', 0),
                'volume': current_data.get('volume', 0),
                'volume_ratio': current_data.get('volume_ratio', 1.0),
                'rsi_14': current_data.get('rsi_14', 50),
                'macd': current_data.get('macd', 0),
                'macd_signal': current_data.get('macd_signal', 0),
                'time_of_day': datetime.now().hour + datetime.now().minute / 60.0,
                'bb_position': current_data.get('bb_position', 0.5),
                'atr_pct': current_data.get('atr_pct', 0.01)
            }
            
            return features
            
        except Exception as e:
            logger.error(f"Historical feature calculation failed: {e}")
            return None
            
    def _get_ml_prediction(self, feature_data: Dict) -> Optional[Dict]:
        """
        Get ML model prediction.
        
        Args:
            feature_data: Prepared features
            
        Returns:
            Optional[Dict]: Prediction result or None
        """
        try:
            if self.model_trainer.model is None:
                logger.warning("ML model not available")
                return {'prediction': 0, 'confidence': 0}
                
            # Convert to DataFrame
            feature_df = pd.DataFrame([feature_data])
            
            # Make prediction
            prediction_result = self.model_trainer.predict(feature_df)
            
            # Convert to signal format
            prediction = prediction_result['predictions'][0]
            confidence = prediction_result['confidence'][0]
            
            # Convert to buy/sell signal (-1 to 1 range)
            signal_strength = (prediction * 2 - 1) if prediction == 1 else -0.5
            
            return {
                'prediction': signal_strength,
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"ML prediction failed: {e}")
            return None
            
    async def execute_trade(self, trading_decision: Dict) -> bool:
        """
        Execute a trading decision.
        
        Args:
            trading_decision: Trading decision from process_market_data
            
        Returns:
            bool: Success status
        """
        try:
            symbol = trading_decision['symbol']
            action = trading_decision['action']
            
            if action == 'hold':
                return True  # No action needed
                
            # Check risk limits before execution
            if not self.risk_manager.can_take_new_position(
                trading_decision['position_size'] * trading_decision['entry_price']
            ):
                logger.warning(f"Risk limits prevent new position in {symbol}")
                return False
                
            # Execute through auth manager
            order_result = await self.auth_manager.place_order(
                symbol=symbol,
                side='buy' if action == 'buy' else 'sell',
                quantity=trading_decision['position_size'],
                price=trading_decision['entry_price'],
                order_type='market'
            )
            
            if order_result.get('success', False):
                # Update position tracking
                self.current_positions[symbol] = {
                    'side': action,
                    'quantity': trading_decision['position_size'],
                    'entry_price': trading_decision['entry_price'],
                    'stop_loss': trading_decision['stop_loss'],
                    'take_profit': trading_decision['take_profit'],
                    'timestamp': trading_decision['timestamp']
                }
                
                # Update daily stats
                self.daily_stats['trades_taken'] += 1
                
                logger.info(f"Trade executed: {action} {trading_decision['position_size']} {symbol} @ {trading_decision['entry_price']}")
                return True
            else:
                logger.error(f"Trade execution failed for {symbol}: {order_result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Trade execution error: {e}")
            return False
            
    async def monitor_positions(self):
        """Monitor open positions for exit conditions"""
        try:
            for symbol, position in list(self.current_positions.items()):
                # Get current price
                current_data = await self.auth_manager.get_quote(symbol)
                if not current_data:
                    continue
                    
                current_price = current_data.get('last_price', 0)
                if current_price == 0:
                    continue
                    
                # Check exit conditions
                should_exit = False
                exit_reason = ""
                
                if position['side'] == 'buy':
                    if current_price >= position['take_profit']:
                        should_exit = True
                        exit_reason = "take_profit"
                    elif current_price <= position['stop_loss']:
                        should_exit = True
                        exit_reason = "stop_loss"
                else:  # sell position
                    if current_price <= position['take_profit']:
                        should_exit = True
                        exit_reason = "take_profit"
                    elif current_price >= position['stop_loss']:
                        should_exit = True
                        exit_reason = "stop_loss"
                        
                if should_exit:
                    await self._close_position(symbol, position, current_price, exit_reason)
                    
        except Exception as e:
            logger.error(f"Position monitoring error: {e}")
            
    async def _close_position(self, symbol: str, position: Dict, exit_price: float, reason: str):
        """Close a position and update statistics"""
        try:
            # Execute close order
            close_side = 'sell' if position['side'] == 'buy' else 'buy'
            order_result = await self.auth_manager.place_order(
                symbol=symbol,
                side=close_side,
                quantity=position['quantity'],
                price=exit_price,
                order_type='market'
            )
            
            if order_result.get('success', False):
                # Calculate P&L
                if position['side'] == 'buy':
                    pnl = (exit_price - position['entry_price']) * position['quantity']
                else:
                    pnl = (position['entry_price'] - exit_price) * position['quantity']
                    
                # Update statistics
                self.daily_stats['daily_pnl'] += pnl
                self.system_performance['total_pnl'] += pnl
                self.system_performance['total_trades'] += 1
                
                if pnl > 0:
                    self.daily_stats['trades_won'] += 1
                    self.system_performance['total_wins'] += 1
                    
                # Update win rate
                self.system_performance['win_rate'] = (
                    self.system_performance['total_wins'] / 
                    self.system_performance['total_trades']
                )
                
                # Remove from current positions
                del self.current_positions[symbol]
                
                logger.info(f"Position closed: {symbol} @ {exit_price} ({reason}) P&L: ${pnl:.2f}")
                
            else:
                logger.error(f"Failed to close position for {symbol}")
                
        except Exception as e:
            logger.error(f"Error closing position for {symbol}: {e}")
            
    def get_system_performance(self) -> Dict:
        """Get current system performance metrics"""
        return {
            'daily_stats': self.daily_stats.copy(),
            'system_performance': self.system_performance.copy(),
            'current_positions': len(self.current_positions),
            'risk_utilization': self.risk_manager.get_current_risk_utilization(),
            'win_rate': f"{self.system_performance['win_rate']:.1%}",
            'total_trades': self.system_performance['total_trades'],
            'daily_pnl': f"${self.daily_stats['daily_pnl']:.2f}",
            'total_pnl': f"${self.system_performance['total_pnl']:.2f}",
            'improvement_vs_original': {
                'original_win_rate': '24%',
                'current_win_rate': f"{self.system_performance['win_rate']:.1%}",
                'target_win_rate': '60-70%',
                'risk_reward_improvement': f"2:1 vs original 1:2"
            }
        }
        
    async def start_system(self):
        """Start the enhanced trading system"""
        if self.is_running:
            logger.warning("System already running")
            return
            
        if not await self.initialize_system():
            logger.error("Failed to initialize system")
            return
            
        self.is_running = True
        logger.info("Enhanced Day Trading System started")
        
        # Main system loop would go here
        # For now, just indicate system is ready
        
    def stop_system(self):
        """Stop the enhanced trading system"""
        self.is_running = False
        logger.info("Enhanced Day Trading System stopped")
        
    def get_system_status(self) -> Dict:
        """Get current system status"""
        return {
            'is_running': self.is_running,
            'components_status': {
                'risk_manager': 'active',
                'time_filter': 'active',
                'signal_generator': 'active',
                'feature_engineer': 'active',
                'model_trainer': 'loaded' if self.model_trainer.model else 'not_loaded',
                'auth_manager': 'connected' if self.auth_manager.is_authenticated else 'disconnected'
            },
            'system_improvements': {
                'risk_reward_ratio': f"{ENHANCED_TARGET_PCT/ENHANCED_STOP_PCT:.1f}:1",
                'feature_count': len(ESSENTIAL_FEATURES),
                'min_confirmations': MIN_SIGNAL_CONFIRMATIONS,
                'optimal_trading_hours': len(OPTIMAL_TRADING_HOURS)
            },
            'performance': self.get_system_performance()
        }

async def main():
    """Main function to demonstrate the enhanced system"""
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create and initialize enhanced system
    enhanced_system = EnhancedDayTradingSystem()
    
    print("Enhanced Day Trading System")
    print("=" * 50)
    print("Key Improvements vs Original System:")
    print("- Risk/Reward: 2:1 vs 1:2 (needs 33% win rate vs 67%)")
    print("- Features: 10 essential vs 30+ (prevents overfitting)")
    print("- Time filters: Avoids volatile open/close periods")
    print("- Ensemble signals: Requires multiple confirmations")
    print("- Target: 60-70% win rate vs original 24%")
    print()
    
    # Start system
    await enhanced_system.start_system()
    
    # Show system status
    status = enhanced_system.get_system_status()
    print("System Status:")
    print(f"Running: {status['is_running']}")
    print(f"Model Status: {status['components_status']['model_trainer']}")
    print(f"Risk/Reward Ratio: {status['system_improvements']['risk_reward_ratio']}")
    print(f"Essential Features: {status['system_improvements']['feature_count']}")
    
    # Test with sample market data
    sample_market_data = {
        'close': 150.50,
        'volume': 5000,
        'returns': 0.01,
        'rsi_14': 35,
        'macd': 0.5,
        'macd_signal': 0.3,
        'bb_position': 0.2,
        'atr_pct': 0.012,
        'volume_ratio': 1.8
    }
    
    print("\nTesting with sample market data...")
    decision = await enhanced_system.process_market_data('AAPL', sample_market_data)
    
    if decision:
        print(f"Trading Decision: {decision['action']} {decision['symbol']}")
        print(f"Signal Strength: {decision['signal_strength']:.2f}")
        print(f"Confidence: {decision['confidence']:.2f}")
        print(f"Risk/Reward: {decision['risk_reward_ratio']:.1f}:1")
    else:
        print("No trading decision generated (filtered out)")

if __name__ == "__main__":
    asyncio.run(main())
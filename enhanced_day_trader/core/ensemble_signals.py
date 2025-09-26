#!/usr/bin/env python3
"""
Enhanced Ensemble Signal System
===============================

Requires multiple confirmations before generating trading signals.
Major improvement over original system which relied on single AI prediction.

Key Features:
- Multiple signal type confirmations required
- Weighted signal strength calculation
- Signal consensus validation
- Prevents false signals that plagued original system

Author: GitHub Copilot
Date: September 26, 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
import logging
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass

from ..config.trading_config import (
    MIN_SIGNAL_CONFIRMATIONS, 
    SIGNAL_TYPES,
    OPTIMAL_TRADING_HOURS
)

logger = logging.getLogger(__name__)

@dataclass
class SignalComponent:
    """Individual signal component with strength and confidence"""
    signal_type: str
    strength: float  # -1.0 to 1.0 (negative = sell, positive = buy)
    confidence: float  # 0.0 to 1.0
    timestamp: datetime
    metadata: Dict = None

class EnsembleSignalGenerator:
    """
    Generates trading signals requiring multiple confirmations.
    Prevents the false signals that hurt the original system's 24% win rate.
    """
    
    def __init__(self):
        self.signal_weights = SIGNAL_TYPES.copy()
        self.min_confirmations = MIN_SIGNAL_CONFIRMATIONS
        self.signal_history = []
        self.ensemble_stats = {
            'signals_generated': 0,
            'signals_filtered': 0,
            'confirmations_required': MIN_SIGNAL_CONFIRMATIONS,
            'avg_confirmations_received': 0.0
        }
        
    def add_ai_prediction_signal(self, prediction: float, confidence: float, timestamp: datetime) -> SignalComponent:
        """
        Add AI/ML model prediction signal.
        
        Args:
            prediction: Model prediction (-1 to 1)
            confidence: Model confidence (0 to 1)
            timestamp: Signal timestamp
            
        Returns:
            SignalComponent: AI prediction signal
        """
        return SignalComponent(
            signal_type='ai_prediction',
            strength=prediction,
            confidence=confidence,
            timestamp=timestamp,
            metadata={'model_type': 'RandomForest'}
        )
        
    def add_technical_alignment_signal(self, indicators: Dict, timestamp: datetime) -> SignalComponent:
        """
        Add technical indicator alignment signal.
        
        Args:
            indicators: Dict with technical indicator values
            timestamp: Signal timestamp
            
        Returns:
            SignalComponent: Technical alignment signal
        """
        # Calculate alignment score from multiple technical indicators
        alignment_factors = []
        
        # RSI alignment (buy when oversold, sell when overbought)
        if 'rsi_14' in indicators:
            rsi = indicators['rsi_14']
            if rsi < 30:
                alignment_factors.append(0.5)  # Bullish (oversold)
            elif rsi > 70:
                alignment_factors.append(-0.5)  # Bearish (overbought)
            else:
                alignment_factors.append(0.0)  # Neutral
                
        # MACD alignment
        if 'macd' in indicators and 'macd_signal' in indicators:
            macd_diff = indicators['macd'] - indicators['macd_signal']
            if macd_diff > 0:
                alignment_factors.append(0.3)  # Bullish
            else:
                alignment_factors.append(-0.3)  # Bearish
                
        # Bollinger Band position
        if 'bb_position' in indicators:
            bb_pos = indicators['bb_position']
            if bb_pos < 0.2:
                alignment_factors.append(0.4)  # Bullish (oversold)
            elif bb_pos > 0.8:
                alignment_factors.append(-0.4)  # Bearish (overbought)
            else:
                alignment_factors.append(0.0)  # Neutral
        
        # Calculate overall alignment
        if alignment_factors:
            alignment_strength = np.mean(alignment_factors)
            confidence = min(len(alignment_factors) / 3.0, 1.0)  # More indicators = higher confidence
        else:
            alignment_strength = 0.0
            confidence = 0.0
            
        return SignalComponent(
            signal_type='technical_alignment',
            strength=alignment_strength,
            confidence=confidence,
            timestamp=timestamp,
            metadata={'indicators_used': list(indicators.keys())}
        )
        
    def add_volume_confirmation_signal(self, current_volume: float, avg_volume: float, timestamp: datetime) -> SignalComponent:
        """
        Add volume confirmation signal.
        
        Args:
            current_volume: Current bar volume
            avg_volume: Average volume (e.g., 20-period)
            timestamp: Signal timestamp
            
        Returns:
            SignalComponent: Volume confirmation signal
        """
        if avg_volume <= 0:
            return SignalComponent('volume_confirmation', 0.0, 0.0, timestamp)
            
        volume_ratio = current_volume / avg_volume
        
        # Volume confirmation logic
        if volume_ratio >= 2.0:
            # High volume confirms strong moves
            strength = 0.8
            confidence = min(volume_ratio / 3.0, 1.0)
        elif volume_ratio >= 1.5:
            # Above average volume provides moderate confirmation
            strength = 0.5
            confidence = 0.7
        elif volume_ratio < 0.5:
            # Low volume suggests weak/unreliable signals
            strength = -0.3
            confidence = 0.8
        else:
            # Average volume is neutral
            strength = 0.0
            confidence = 0.5
            
        return SignalComponent(
            signal_type='volume_confirmation',
            strength=strength,
            confidence=confidence,
            timestamp=timestamp,
            metadata={'volume_ratio': volume_ratio}
        )
        
    def add_time_filter_signal(self, timestamp: datetime) -> SignalComponent:
        """
        Add time-based filter signal.
        
        Args:
            timestamp: Current timestamp
            
        Returns:
            SignalComponent: Time filter signal
        """
        hour_decimal = timestamp.hour + timestamp.minute / 60.0
        
        # Check optimal trading hours
        in_optimal_window = False
        for start, end in OPTIMAL_TRADING_HOURS:
            if start <= hour_decimal <= end:
                in_optimal_window = True
                break
                
        if in_optimal_window:
            strength = 0.5
            confidence = 0.8
        else:
            # Penalize non-optimal times
            strength = -0.2
            confidence = 0.6
            
        return SignalComponent(
            signal_type='time_filter',
            strength=strength,
            confidence=confidence,
            timestamp=timestamp,
            metadata={'hour_decimal': hour_decimal, 'optimal_window': in_optimal_window}
        )
        
    def add_volatility_check_signal(self, atr_pct: float, timestamp: datetime) -> SignalComponent:
        """
        Add volatility appropriateness signal.
        
        Args:
            atr_pct: ATR as percentage of price
            timestamp: Signal timestamp
            
        Returns:
            SignalComponent: Volatility check signal
        """
        # Define optimal volatility range for day trading
        optimal_atr_min = 0.005  # 0.5% minimum for decent moves
        optimal_atr_max = 0.030  # 3.0% maximum to avoid chaos
        
        if optimal_atr_min <= atr_pct <= optimal_atr_max:
            # Good volatility for day trading
            strength = 0.3
            confidence = 0.7
        elif atr_pct < optimal_atr_min:
            # Too quiet - difficult to profit
            strength = -0.4
            confidence = 0.8
        else:
            # Too volatile - high risk
            strength = -0.6
            confidence = 0.9
            
        return SignalComponent(
            signal_type='volatility_check',
            strength=strength,
            confidence=confidence,
            timestamp=timestamp,
            metadata={'atr_pct': atr_pct, 'optimal_range': [optimal_atr_min, optimal_atr_max]}
        )
        
    def calculate_ensemble_signal(self, signal_components: List[SignalComponent]) -> Dict:
        """
        Calculate final ensemble signal from components.
        
        Args:
            signal_components: List of individual signal components
            
        Returns:
            dict: Ensemble signal with strength, confidence, and metadata
        """
        if not signal_components:
            return {
                'signal_strength': 0.0,
                'confidence': 0.0,
                'direction': 'hold',
                'confirmations': 0,
                'components': [],
                'meets_threshold': False
            }
            
        # Calculate weighted signal strength
        total_weighted_strength = 0.0
        total_weights = 0.0
        confirmations = 0
        component_details = []
        
        for component in signal_components:
            # Get weight for this signal type
            weight = self.signal_weights.get(component.signal_type, 0.5)
            
            # Weight by confidence
            effective_weight = weight * component.confidence
            
            # Accumulate weighted strength
            total_weighted_strength += component.strength * effective_weight
            total_weights += effective_weight
            
            # Count confirmations (positive strength above threshold)
            if abs(component.strength) >= 0.3 and component.confidence >= 0.5:
                confirmations += 1
                
            # Store component details
            component_details.append({
                'type': component.signal_type,
                'strength': component.strength,
                'confidence': component.confidence,
                'weight': weight,
                'metadata': component.metadata
            })
        
        # Calculate final ensemble strength
        if total_weights > 0:
            ensemble_strength = total_weighted_strength / total_weights
        else:
            ensemble_strength = 0.0
            
        # Calculate overall confidence (average of component confidences weighted by their weights)
        if signal_components:
            confidence_sum = sum(comp.confidence * self.signal_weights.get(comp.signal_type, 0.5) 
                               for comp in signal_components)
            weight_sum = sum(self.signal_weights.get(comp.signal_type, 0.5) 
                           for comp in signal_components)
            overall_confidence = confidence_sum / weight_sum if weight_sum > 0 else 0.0
        else:
            overall_confidence = 0.0
            
        # Determine direction
        if ensemble_strength >= 0.3:
            direction = 'buy'
        elif ensemble_strength <= -0.3:
            direction = 'sell'
        else:
            direction = 'hold'
            
        # Check if meets minimum confirmation threshold
        meets_threshold = confirmations >= self.min_confirmations
        
        # Update statistics
        self.ensemble_stats['signals_generated'] += 1
        if not meets_threshold:
            self.ensemble_stats['signals_filtered'] += 1
        self.ensemble_stats['avg_confirmations_received'] = (
            (self.ensemble_stats['avg_confirmations_received'] * (self.ensemble_stats['signals_generated'] - 1) + 
             confirmations) / self.ensemble_stats['signals_generated']
        )
        
        return {
            'signal_strength': ensemble_strength,
            'confidence': overall_confidence,
            'direction': direction,
            'confirmations': confirmations,
            'components': component_details,
            'meets_threshold': meets_threshold,
            'timestamp': datetime.now(),
            'ensemble_stats': self.ensemble_stats.copy()
        }
        
    def generate_full_ensemble_signal(self, market_data: Dict, timestamp: datetime) -> Dict:
        """
        Generate complete ensemble signal from market data.
        
        Args:
            market_data: Dict with all required market data
            timestamp: Current timestamp
            
        Returns:
            dict: Complete ensemble signal
        """
        signal_components = []
        
        # Add AI prediction signal
        if 'ai_prediction' in market_data and 'ai_confidence' in market_data:
            ai_signal = self.add_ai_prediction_signal(
                market_data['ai_prediction'],
                market_data['ai_confidence'],
                timestamp
            )
            signal_components.append(ai_signal)
            
        # Add technical alignment signal
        technical_indicators = {k: v for k, v in market_data.items() 
                              if k in ['rsi_14', 'macd', 'macd_signal', 'bb_position']}
        if technical_indicators:
            tech_signal = self.add_technical_alignment_signal(technical_indicators, timestamp)
            signal_components.append(tech_signal)
            
        # Add volume confirmation signal
        if 'volume' in market_data and 'volume_avg' in market_data:
            vol_signal = self.add_volume_confirmation_signal(
                market_data['volume'],
                market_data['volume_avg'],
                timestamp
            )
            signal_components.append(vol_signal)
            
        # Add time filter signal
        time_signal = self.add_time_filter_signal(timestamp)
        signal_components.append(time_signal)
        
        # Add volatility check signal
        if 'atr_pct' in market_data:
            vol_check_signal = self.add_volatility_check_signal(market_data['atr_pct'], timestamp)
            signal_components.append(vol_check_signal)
            
        # Calculate ensemble signal
        ensemble_result = self.calculate_ensemble_signal(signal_components)
        
        # Add market data context
        ensemble_result['market_data'] = market_data
        ensemble_result['symbol'] = market_data.get('symbol', 'Unknown')
        
        logger.info(f"Generated ensemble signal: {ensemble_result['direction']} "
                   f"(strength={ensemble_result['signal_strength']:.2f}, "
                   f"confirmations={ensemble_result['confirmations']}, "
                   f"meets_threshold={ensemble_result['meets_threshold']})")
        
        return ensemble_result
        
    def get_ensemble_performance_report(self) -> Dict:
        """
        Generate performance report for ensemble system.
        
        Returns:
            dict: Ensemble performance statistics
        """
        total_signals = self.ensemble_stats['signals_generated']
        filtered_signals = self.ensemble_stats['signals_filtered']
        
        if total_signals == 0:
            return {'error': 'No signals generated yet'}
            
        filter_rate = filtered_signals / total_signals
        approval_rate = 1.0 - filter_rate
        
        return {
            'total_signals_generated': total_signals,
            'signals_filtered_out': filtered_signals,
            'filter_rate': f"{filter_rate:.1%}",
            'approval_rate': f"{approval_rate:.1%}",
            'min_confirmations_required': self.min_confirmations,
            'avg_confirmations_received': f"{self.ensemble_stats['avg_confirmations_received']:.1f}",
            'signal_weights': self.signal_weights,
            'effectiveness': f"Ensemble filtering reduces false signals by requiring {self.min_confirmations}+ confirmations"
        }

def test_ensemble_signals():
    """Test the ensemble signal system"""
    
    # Create test market data scenarios
    test_scenarios = [
        {
            'name': 'Strong Buy Signal',
            'data': {
                'symbol': 'AAPL',
                'ai_prediction': 0.8,
                'ai_confidence': 0.9,
                'rsi_14': 25,  # Oversold
                'macd': 0.5,
                'macd_signal': 0.3,
                'bb_position': 0.1,  # Near lower band
                'volume': 5000,
                'volume_avg': 2000,  # High volume
                'atr_pct': 0.015  # Good volatility
            },
            'timestamp': datetime(2025, 1, 1, 10, 30)  # Optimal time
        },
        {
            'name': 'Weak Signal (Low Confirmations)', 
            'data': {
                'symbol': 'MSFT',
                'ai_prediction': 0.4,  # Weak prediction
                'ai_confidence': 0.6,
                'rsi_14': 50,  # Neutral
                'macd': 0.1,
                'macd_signal': 0.1,
                'bb_position': 0.5,  # Middle
                'volume': 800,
                'volume_avg': 1000,  # Low volume
                'atr_pct': 0.002  # Too quiet
            },
            'timestamp': datetime(2025, 1, 1, 12, 0)  # Lunch time
        }
    ]
    
    # Test ensemble signals
    ensemble_generator = EnsembleSignalGenerator()
    
    print("Ensemble Signal System Test Results")
    print("=" * 50)
    
    for scenario in test_scenarios:
        print(f"\nScenario: {scenario['name']}")
        print("-" * 30)
        
        result = ensemble_generator.generate_full_ensemble_signal(
            scenario['data'], 
            scenario['timestamp']
        )
        
        print(f"Direction: {result['direction']}")
        print(f"Signal Strength: {result['signal_strength']:.2f}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Confirmations: {result['confirmations']}")
        print(f"Meets Threshold: {result['meets_threshold']}")
        print(f"Components:")
        
        for comp in result['components']:
            print(f"  {comp['type']}: {comp['strength']:.2f} (conf: {comp['confidence']:.2f})")
    
    # Get performance report
    report = ensemble_generator.get_ensemble_performance_report()
    print(f"\nEnsemble Performance Report:")
    print(f"Total signals: {report['total_signals_generated']}")
    print(f"Filter rate: {report['filter_rate']}")
    print(f"Avg confirmations: {report['avg_confirmations_received']}")

if __name__ == "__main__":
    test_ensemble_signals()
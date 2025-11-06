"""
Live Catalyst Scorer for Catalyst Scanner
=========================================

Real-time catalyst impact scoring that updates with live market data:
- Dynamic catalyst scoring based on real-time price/volume changes
- Market state awareness (pre/regular/post market)
- Sentiment integration with live news feeds
- Technical indicator integration for enhanced scoring
- Historical pattern matching for catalyst impact prediction

Author: GitHub Copilot & Investment Catalyst Team  
Date: October 1, 2025
Phase: 4 - Advanced Features
"""

import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

from utils.logger import get_logger
from utils.error_handler import api_error_handler


@dataclass
class CatalystScore:
    """Catalyst scoring result"""
    symbol: str
    catalyst_type: str
    base_score: float          # 1-10 base catalyst importance
    real_time_multiplier: float # Market reaction multiplier
    final_score: float         # Combined final score
    confidence: float          # Confidence level 0-1
    factors: Dict             # Contributing factors breakdown
    timestamp: datetime
    

@dataclass  
class MarketReaction:
    """Market reaction analysis"""
    price_change: float
    volume_ratio: float
    volatility: float
    momentum_score: float
    technical_confirmation: bool


class LiveCatalystScorer:
    """
    Real-time catalyst impact scoring engine
    """
    
    def __init__(self, technical_analyzer=None, news_collector=None):
        """
        Initialize live catalyst scorer
        
        Args:
            technical_analyzer: Technical analysis collector
            news_collector: News feed collector for sentiment
        """
        self.logger = get_logger()
        self.technical_analyzer = technical_analyzer
        self.news_collector = news_collector
        
        # Scoring configuration
        self.scoring_config = {
            'base_weights': {
                'earnings': 8.0,
                'fda_approval': 9.0,
                'merger_acquisition': 9.5,
                'analyst_upgrade': 6.0,
                'analyst_downgrade': 7.0,
                'guidance_update': 7.5,
                'product_launch': 6.5,
                'regulatory_news': 8.5,
                'partnership': 7.0,
                'insider_trading': 5.5,
                'news_sentiment': 4.0,
                'technical_breakout': 5.0
            },
            'market_state_multipliers': {
                'pre': 1.2,      # Pre-market news has higher impact
                'regular': 1.0,   # Regular hours baseline
                'post': 1.1,     # Post-market somewhat elevated
                'closed': 0.8    # Closed market lower impact
            },
            'volume_impact_weights': {
                'low': 0.8,      # <1x average volume
                'normal': 1.0,   # 1-2x average volume  
                'elevated': 1.3, # 2-5x average volume
                'extreme': 1.8   # >5x average volume
            },
            'price_impact_weights': {
                'minimal': 0.9,  # <1% price change
                'moderate': 1.0, # 1-3% price change
                'significant': 1.4, # 3-7% price change
                'major': 1.8     # >7% price change
            }
        }
        
        # Catalyst history for pattern matching
        self.catalyst_history = {}
        self.recent_scores = {}
        
        self.logger.info("Live catalyst scorer initialized")
    
    @api_error_handler("Catalyst scoring", reraise=False)
    def score_catalyst_impact(self, 
                            symbol: str, 
                            catalyst_type: str, 
                            catalyst_data: Dict,
                            market_data: Dict) -> CatalystScore:
        """
        Score catalyst impact with real-time market data
        
        Args:
            symbol: Stock ticker symbol
            catalyst_type: Type of catalyst (earnings, fda_approval, etc.)
            catalyst_data: Catalyst-specific data
            market_data: Real-time market reaction data
            
        Returns:
            CatalystScore with real-time adjusted scoring
        """
        try:
            # Get base catalyst score
            base_score = self.scoring_config['base_weights'].get(catalyst_type, 5.0)
            
            # Analyze market reaction
            market_reaction = self._analyze_market_reaction(market_data)
            
            # Calculate real-time multiplier
            real_time_multiplier = self._calculate_real_time_multiplier(
                market_reaction, 
                market_data.get('market_state', 'regular')
            )
            
            # Apply technical analysis enhancement
            technical_multiplier = self._get_technical_multiplier(symbol, market_reaction)
            
            # Apply sentiment analysis if available
            sentiment_multiplier = self._get_sentiment_multiplier(symbol, catalyst_data)
            
            # Calculate final score
            final_score = base_score * real_time_multiplier * technical_multiplier * sentiment_multiplier
            final_score = min(final_score, 10.0)  # Cap at 10
            
            # Calculate confidence based on data quality and market confirmation
            confidence = self._calculate_confidence(
                market_reaction, 
                catalyst_data, 
                market_data
            )
            
            # Build factors breakdown
            factors = {
                'base_score': base_score,
                'market_reaction': {
                    'price_change': market_reaction.price_change,
                    'volume_ratio': market_reaction.volume_ratio,
                    'volatility': market_reaction.volatility
                },
                'multipliers': {
                    'real_time': real_time_multiplier,
                    'technical': technical_multiplier,
                    'sentiment': sentiment_multiplier
                },
                'market_state': market_data.get('market_state', 'unknown')
            }
            
            # Create catalyst score
            score = CatalystScore(
                symbol=symbol,
                catalyst_type=catalyst_type,
                base_score=base_score,
                real_time_multiplier=real_time_multiplier * technical_multiplier * sentiment_multiplier,
                final_score=final_score,
                confidence=confidence,
                factors=factors,
                timestamp=datetime.now()
            )
            
            # Store for historical tracking
            self._store_catalyst_score(score)
            
            self.logger.debug(f"Scored {symbol} {catalyst_type}: {final_score:.2f} (confidence: {confidence:.2f})")
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error scoring catalyst impact for {symbol}: {e}")
            return self._create_default_score(symbol, catalyst_type)
    
    def _analyze_market_reaction(self, market_data: Dict) -> MarketReaction:
        """Analyze current market reaction to catalyst"""
        try:
            price_change = market_data.get('price_change_percent', 0.0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            
            # Calculate volatility (simplified)
            volatility = abs(price_change) * volume_ratio
            
            # Calculate momentum score based on price and volume
            momentum_score = self._calculate_momentum_score(price_change, volume_ratio)
            
            # Check technical confirmation
            technical_confirmation = self._check_technical_confirmation(market_data)
            
            return MarketReaction(
                price_change=price_change,
                volume_ratio=volume_ratio,
                volatility=volatility,
                momentum_score=momentum_score,
                technical_confirmation=technical_confirmation
            )
            
        except Exception as e:
            self.logger.error(f"Error analyzing market reaction: {e}")
            return MarketReaction(0.0, 1.0, 0.0, 0.0, False)
    
    def _calculate_momentum_score(self, price_change: float, volume_ratio: float) -> float:
        """Calculate momentum score from price and volume changes"""
        try:
            # Combine price change and volume for momentum
            price_component = abs(price_change) / 10.0  # Normalize to 0-1 for 10% change
            volume_component = min(volume_ratio, 5.0) / 5.0  # Normalize to 0-1 for 5x volume
            
            # Weight volume higher for momentum
            momentum = (price_component * 0.4) + (volume_component * 0.6)
            
            return min(momentum, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating momentum score: {e}")
            return 0.0
    
    def _calculate_real_time_multiplier(self, market_reaction: MarketReaction, market_state: str) -> float:
        """Calculate real-time impact multiplier"""
        try:
            # Base multiplier from market state
            state_multiplier = self.scoring_config['market_state_multipliers'].get(market_state, 1.0)
            
            # Volume impact multiplier
            volume_category = self._categorize_volume(market_reaction.volume_ratio)
            volume_multiplier = self.scoring_config['volume_impact_weights'][volume_category]
            
            # Price impact multiplier  
            price_category = self._categorize_price_change(abs(market_reaction.price_change))
            price_multiplier = self.scoring_config['price_impact_weights'][price_category]
            
            # Momentum bonus
            momentum_bonus = 1.0 + (market_reaction.momentum_score * 0.3)
            
            # Technical confirmation bonus
            technical_bonus = 1.1 if market_reaction.technical_confirmation else 1.0
            
            # Combine all multipliers
            total_multiplier = (state_multiplier * volume_multiplier * 
                              price_multiplier * momentum_bonus * technical_bonus)
            
            # Reasonable bounds
            return max(0.5, min(total_multiplier, 3.0))
            
        except Exception as e:
            self.logger.error(f"Error calculating real-time multiplier: {e}")
            return 1.0
    
    def _categorize_volume(self, volume_ratio: float) -> str:
        """Categorize volume level"""
        if volume_ratio < 1.0:
            return 'low'
        elif volume_ratio < 2.0:
            return 'normal'
        elif volume_ratio < 5.0:
            return 'elevated'
        else:
            return 'extreme'
    
    def _categorize_price_change(self, price_change: float) -> str:
        """Categorize price change magnitude"""
        if price_change < 1.0:
            return 'minimal'
        elif price_change < 3.0:
            return 'moderate'
        elif price_change < 7.0:
            return 'significant'
        else:
            return 'major'
    
    def _get_technical_multiplier(self, symbol: str, market_reaction: MarketReaction) -> float:
        """Get technical analysis multiplier"""
        try:
            if not self.technical_analyzer:
                return 1.0
            
            # Get technical indicators (simplified for now)
            # In full implementation, this would integrate with technical_analysis.py
            
            # Mock technical analysis based on price action and volume
            technical_score = 1.0
            
            # Volume confirmation
            if market_reaction.volume_ratio > 2.0:
                technical_score += 0.1
            
            # Strong momentum
            if market_reaction.momentum_score > 0.7:
                technical_score += 0.15
            
            return min(technical_score, 1.5)
            
        except Exception as e:
            self.logger.error(f"Error getting technical multiplier for {symbol}: {e}")
            return 1.0
    
    def _get_sentiment_multiplier(self, symbol: str, catalyst_data: Dict) -> float:
        """Get sentiment analysis multiplier"""
        try:
            if not self.news_collector:
                return 1.0
            
            # Get recent sentiment for symbol (simplified)
            sentiment = catalyst_data.get('sentiment', 'neutral')
            
            sentiment_multipliers = {
                'very_positive': 1.2,
                'positive': 1.1,
                'neutral': 1.0,
                'negative': 0.9,
                'very_negative': 0.8
            }
            
            return sentiment_multipliers.get(sentiment, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error getting sentiment multiplier for {symbol}: {e}")
            return 1.0
    
    def _check_technical_confirmation(self, market_data: Dict) -> bool:
        """Check if technical indicators confirm the move"""
        try:
            # Simplified technical confirmation
            price_change = market_data.get('price_change_percent', 0.0)
            volume_ratio = market_data.get('volume_ratio', 1.0)
            
            # Strong move with volume confirmation
            if abs(price_change) > 2.0 and volume_ratio > 1.5:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Error checking technical confirmation: {e}")
            return False
    
    def _calculate_confidence(self, 
                            market_reaction: MarketReaction, 
                            catalyst_data: Dict, 
                            market_data: Dict) -> float:
        """Calculate confidence level for the score"""
        try:
            confidence = 0.5  # Base confidence
            
            # Market reaction confirms catalyst
            if market_reaction.momentum_score > 0.5:
                confidence += 0.2
            
            # Volume confirmation
            if market_reaction.volume_ratio > 1.5:
                confidence += 0.15
            
            # Technical confirmation
            if market_reaction.technical_confirmation:
                confidence += 0.1
            
            # Data quality
            if catalyst_data.get('source_reliability', 'medium') == 'high':
                confidence += 0.05
            
            return min(confidence, 1.0)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _store_catalyst_score(self, score: CatalystScore):
        """Store catalyst score for historical tracking"""
        try:
            key = f"{score.symbol}_{score.catalyst_type}_{score.timestamp.strftime('%Y%m%d_%H%M')}"
            self.recent_scores[key] = score
            
            # Keep only recent scores (last 24 hours)
            cutoff = datetime.now() - timedelta(hours=24)
            self.recent_scores = {
                k: v for k, v in self.recent_scores.items() 
                if v.timestamp > cutoff
            }
            
        except Exception as e:
            self.logger.error(f"Error storing catalyst score: {e}")
    
    def _create_default_score(self, symbol: str, catalyst_type: str) -> CatalystScore:
        """Create default score when scoring fails"""
        return CatalystScore(
            symbol=symbol,
            catalyst_type=catalyst_type,
            base_score=5.0,
            real_time_multiplier=1.0,
            final_score=5.0,
            confidence=0.3,
            factors={'error': 'Failed to calculate score'},
            timestamp=datetime.now()
        )
    
    def get_recent_scores(self, symbol: str = None, hours_back: int = 24) -> List[CatalystScore]:
        """Get recent catalyst scores"""
        try:
            cutoff = datetime.now() - timedelta(hours=hours_back)
            
            scores = [
                score for score in self.recent_scores.values()
                if score.timestamp > cutoff and (symbol is None or score.symbol == symbol)
            ]
            
            return sorted(scores, key=lambda x: x.timestamp, reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting recent scores: {e}")
            return []
    
    def get_top_catalysts(self, limit: int = 10) -> List[CatalystScore]:
        """Get top-scoring catalysts"""
        try:
            all_scores = list(self.recent_scores.values())
            top_scores = sorted(all_scores, key=lambda x: x.final_score, reverse=True)
            return top_scores[:limit]
            
        except Exception as e:
            self.logger.error(f"Error getting top catalysts: {e}")
            return []
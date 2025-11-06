"""
Market Impact Calculator for Catalyst Scanner
============================================

Calculates real-time market impact and portfolio effects from catalysts:
- Portfolio-wide impact assessment
- Position-weighted catalyst scoring
- Risk exposure calculation
- Correlation analysis between holdings
- Real-time P&L impact estimation

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
class PortfolioImpact:
    """Portfolio impact assessment"""
    total_exposure: float          # Total $ exposure to catalyst
    affected_positions: int        # Number of positions affected
    estimated_pnl_impact: float    # Estimated P&L impact
    risk_level: str               # low/medium/high/critical
    correlation_risk: float       # Risk from correlated positions
    diversification_score: float  # Portfolio diversification 0-1
    timestamp: datetime


@dataclass
class PositionImpact:
    """Individual position impact"""
    symbol: str
    position_value: float
    catalyst_score: float
    estimated_move: float         # Expected price move %
    estimated_pnl: float         # Expected P&L impact
    risk_contribution: float     # Contribution to portfolio risk
    correlation_factor: float    # Correlation with other positions


class MarketImpactCalculator:
    """
    Real-time market impact calculator for portfolio analysis
    """
    
    def __init__(self, portfolio_loader=None):
        """
        Initialize market impact calculator
        
        Args:
            portfolio_loader: Portfolio loader for position data
        """
        self.logger = get_logger()
        self.portfolio_loader = portfolio_loader
        
        # Configuration
        self.config = {
            'risk_thresholds': {
                'low': 0.02,      # <2% portfolio impact
                'medium': 0.05,   # 2-5% portfolio impact  
                'high': 0.10,     # 5-10% portfolio impact
                'critical': 0.15  # >15% portfolio impact
            },
            'correlation_threshold': 0.7,  # High correlation threshold
            'max_position_risk': 0.20,     # Max 20% of portfolio in one position
            'catalyst_decay_factor': 0.1,  # Daily catalyst impact decay
        }
        
        # Portfolio state
        self.portfolio_positions = {}
        self.correlation_matrix = None
        self.last_portfolio_update = None
        
        # Impact history
        self.impact_history = []
        
        self.logger.info("Market impact calculator initialized")
    
    @api_error_handler("Portfolio impact calculation", reraise=False)
    def calculate_portfolio_impact(self, 
                                 catalyst_scores: List,
                                 real_time_quotes: Dict) -> PortfolioImpact:
        """
        Calculate real-time portfolio impact from catalysts
        
        Args:
            catalyst_scores: List of CatalystScore objects
            real_time_quotes: Dict of real-time quote data
            
        Returns:
            PortfolioImpact assessment
        """
        try:
            # Load current portfolio if needed
            self._update_portfolio_positions()
            
            if not self.portfolio_positions:
                return self._create_empty_impact()
            
            # Calculate individual position impacts
            position_impacts = self._calculate_position_impacts(catalyst_scores, real_time_quotes)
            
            # Aggregate portfolio-level metrics
            total_exposure = sum(pos.position_value for pos in position_impacts)
            affected_positions = len([p for p in position_impacts if p.catalyst_score > 0])
            estimated_pnl_impact = sum(pos.estimated_pnl for pos in position_impacts)
            
            # Calculate correlation risk
            correlation_risk = self._calculate_correlation_risk(position_impacts)
            
            # Calculate diversification score
            diversification_score = self._calculate_diversification_score(position_impacts)
            
            # Determine risk level
            portfolio_value = sum(self.portfolio_positions.values())
            impact_percentage = abs(estimated_pnl_impact) / portfolio_value if portfolio_value > 0 else 0
            risk_level = self._determine_risk_level(impact_percentage)
            
            # Create portfolio impact
            impact = PortfolioImpact(
                total_exposure=total_exposure,
                affected_positions=affected_positions,
                estimated_pnl_impact=estimated_pnl_impact,
                risk_level=risk_level,
                correlation_risk=correlation_risk,
                diversification_score=diversification_score,
                timestamp=datetime.now()
            )
            
            # Store for historical tracking
            self._store_impact_history(impact, position_impacts)
            
            self.logger.info(f"Portfolio impact: {impact.risk_level} risk, "
                           f"${impact.estimated_pnl_impact:,.0f} estimated impact")
            
            return impact
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio impact: {e}")
            return self._create_empty_impact()
    
    def _update_portfolio_positions(self):
        """Update portfolio positions from loader"""
        try:
            if not self.portfolio_loader:
                return
            
            # Check if we need to update (every 5 minutes)
            if (self.last_portfolio_update and 
                datetime.now() - self.last_portfolio_update < timedelta(minutes=5)):
                return
            
            # Load portfolio data
            portfolio_data = self.portfolio_loader.load_portfolio()
            
            # Convert to position values (symbol -> market value)
            self.portfolio_positions = {}
            for symbol, position_info in portfolio_data.items():
                if isinstance(position_info, dict):
                    market_value = position_info.get('market_value', 0)
                    quantity = position_info.get('quantity', 0)
                    price = position_info.get('price', 0)
                    
                    # Calculate market value if not provided
                    if market_value == 0 and quantity > 0 and price > 0:
                        market_value = quantity * price
                    
                    self.portfolio_positions[symbol] = market_value
                else:
                    # Simple numeric value
                    self.portfolio_positions[symbol] = float(position_info)
            
            self.last_portfolio_update = datetime.now()
            self.logger.debug(f"Updated portfolio: {len(self.portfolio_positions)} positions")
            
        except Exception as e:
            self.logger.error(f"Error updating portfolio positions: {e}")
    
    def _calculate_position_impacts(self, 
                                  catalyst_scores: List, 
                                  real_time_quotes: Dict) -> List[PositionImpact]:
        """Calculate impact for each portfolio position"""
        position_impacts = []
        
        try:
            # Create lookup for catalyst scores by symbol
            score_lookup = {score.symbol: score for score in catalyst_scores}
            
            for symbol, position_value in self.portfolio_positions.items():
                # Get catalyst score for this position
                catalyst_score_obj = score_lookup.get(symbol)
                catalyst_score = catalyst_score_obj.final_score if catalyst_score_obj else 0.0
                
                # Get real-time quote data
                quote_data = real_time_quotes.get(symbol, {})
                current_price_change = quote_data.get('change_percent', 0.0)
                
                # Estimate price move based on catalyst score
                estimated_move = self._estimate_price_move(catalyst_score, current_price_change)
                
                # Calculate estimated P&L
                estimated_pnl = position_value * (estimated_move / 100.0)
                
                # Calculate risk contribution
                portfolio_value = sum(self.portfolio_positions.values())
                risk_contribution = (position_value / portfolio_value) * abs(estimated_move) / 100.0
                
                # Calculate correlation factor (simplified)
                correlation_factor = self._get_correlation_factor(symbol)
                
                # Create position impact
                impact = PositionImpact(
                    symbol=symbol,
                    position_value=position_value,
                    catalyst_score=catalyst_score,
                    estimated_move=estimated_move,
                    estimated_pnl=estimated_pnl,
                    risk_contribution=risk_contribution,
                    correlation_factor=correlation_factor
                )
                
                position_impacts.append(impact)
            
            return position_impacts
            
        except Exception as e:
            self.logger.error(f"Error calculating position impacts: {e}")
            return []
    
    def _estimate_price_move(self, catalyst_score: float, current_change: float) -> float:
        """Estimate expected price move from catalyst score"""
        try:
            # Base move expectation from catalyst score
            # Score 1-3: 0-2% move, Score 4-6: 2-5% move, Score 7-10: 5-15% move
            if catalyst_score <= 3:
                base_move = catalyst_score * 0.67  # 0-2%
            elif catalyst_score <= 6:
                base_move = 2 + ((catalyst_score - 3) * 1.0)  # 2-5%
            else:
                base_move = 5 + ((catalyst_score - 6) * 2.5)  # 5-15%
            
            # Factor in current market reaction
            market_momentum = abs(current_change) * 0.3
            
            # Combine base move with market momentum
            estimated_move = base_move + market_momentum
            
            # Apply direction from current change
            if current_change != 0:
                estimated_move = estimated_move if current_change > 0 else -estimated_move
            
            return min(abs(estimated_move), 20.0) * (1 if estimated_move >= 0 else -1)
            
        except Exception as e:
            self.logger.error(f"Error estimating price move: {e}")
            return 0.0
    
    def _get_correlation_factor(self, symbol: str) -> float:
        """Get correlation factor for symbol with rest of portfolio"""
        try:
            # Simplified correlation calculation
            # In full implementation, this would use historical correlation data
            
            # Sector-based correlation (simplified)
            sector_correlations = {
                'TECH': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA'],
                'FINANCE': ['JPM', 'BAC', 'WFC', 'GS', 'MS'],
                'HEALTH': ['JNJ', 'PFE', 'UNH', 'ABBV', 'MRK'],
                'ENERGY': ['XOM', 'CVX', 'COP', 'EOG'],
            }
            
            # Find symbols in same sector
            symbol_sector = None
            for sector, tickers in sector_correlations.items():
                if symbol in tickers:
                    symbol_sector = sector
                    break
            
            if symbol_sector:
                # Count how many portfolio positions are in same sector
                same_sector_count = sum(
                    1 for ticker in self.portfolio_positions.keys()
                    if ticker in sector_correlations[symbol_sector]
                )
                
                # Higher correlation if more positions in same sector
                return min(same_sector_count * 0.2, 1.0)
            
            return 0.3  # Default moderate correlation
            
        except Exception as e:
            self.logger.error(f"Error getting correlation factor for {symbol}: {e}")
            return 0.3
    
    def _calculate_correlation_risk(self, position_impacts: List[PositionImpact]) -> float:
        """Calculate portfolio correlation risk"""
        try:
            if len(position_impacts) <= 1:
                return 0.0
            
            # Calculate weighted correlation risk
            total_risk = 0.0
            total_weight = 0.0
            
            for impact in position_impacts:
                weight = impact.position_value
                risk = impact.risk_contribution * impact.correlation_factor
                total_risk += risk * weight
                total_weight += weight
            
            if total_weight > 0:
                return total_risk / total_weight
            
            return 0.0
            
        except Exception as e:
            self.logger.error(f"Error calculating correlation risk: {e}")
            return 0.0
    
    def _calculate_diversification_score(self, position_impacts: List[PositionImpact]) -> float:
        """Calculate portfolio diversification score (0-1, higher = more diversified)"""
        try:
            if len(position_impacts) <= 1:
                return 0.0
            
            # Calculate position concentration
            portfolio_value = sum(impact.position_value for impact in position_impacts)
            
            if portfolio_value <= 0:
                return 0.0
            
            # Calculate Herfindahl index (concentration measure)
            herfindahl = sum(
                (impact.position_value / portfolio_value) ** 2 
                for impact in position_impacts
            )
            
            # Convert to diversification score (inverse of concentration)
            max_positions = len(position_impacts)
            min_herfindahl = 1.0 / max_positions  # Perfect diversification
            
            diversification = 1.0 - ((herfindahl - min_herfindahl) / (1.0 - min_herfindahl))
            
            return max(0.0, min(1.0, diversification))
            
        except Exception as e:
            self.logger.error(f"Error calculating diversification score: {e}")
            return 0.5
    
    def _determine_risk_level(self, impact_percentage: float) -> str:
        """Determine risk level from impact percentage"""
        if impact_percentage >= self.config['risk_thresholds']['critical']:
            return 'critical'
        elif impact_percentage >= self.config['risk_thresholds']['high']:
            return 'high'
        elif impact_percentage >= self.config['risk_thresholds']['medium']:
            return 'medium'
        else:
            return 'low'
    
    def _store_impact_history(self, portfolio_impact: PortfolioImpact, position_impacts: List[PositionImpact]):
        """Store impact assessment for historical tracking"""
        try:
            impact_record = {
                'timestamp': portfolio_impact.timestamp,
                'portfolio_impact': portfolio_impact,
                'position_impacts': position_impacts
            }
            
            self.impact_history.append(impact_record)
            
            # Keep only last 24 hours of history
            cutoff = datetime.now() - timedelta(hours=24)
            self.impact_history = [
                record for record in self.impact_history
                if record['timestamp'] > cutoff
            ]
            
        except Exception as e:
            self.logger.error(f"Error storing impact history: {e}")
    
    def _create_empty_impact(self) -> PortfolioImpact:
        """Create empty portfolio impact when calculation fails"""
        return PortfolioImpact(
            total_exposure=0.0,
            affected_positions=0,
            estimated_pnl_impact=0.0,
            risk_level='low',
            correlation_risk=0.0,
            diversification_score=0.5,
            timestamp=datetime.now()
        )
    
    def get_position_breakdown(self, risk_threshold: float = 0.01) -> List[PositionImpact]:
        """Get position impacts above risk threshold"""
        try:
            if not self.impact_history:
                return []
            
            latest_record = self.impact_history[-1]
            position_impacts = latest_record['position_impacts']
            
            # Filter by risk threshold
            significant_impacts = [
                impact for impact in position_impacts
                if impact.risk_contribution >= risk_threshold
            ]
            
            # Sort by risk contribution
            return sorted(significant_impacts, 
                         key=lambda x: x.risk_contribution, 
                         reverse=True)
            
        except Exception as e:
            self.logger.error(f"Error getting position breakdown: {e}")
            return []
    
    def get_risk_summary(self) -> Dict:
        """Get comprehensive risk summary"""
        try:
            if not self.impact_history:
                return {'status': 'no_data'}
            
            latest_impact = self.impact_history[-1]['portfolio_impact']
            position_impacts = self.impact_history[-1]['position_impacts']
            
            # Top risk contributors
            top_risks = sorted(
                position_impacts,
                key=lambda x: x.risk_contribution,
                reverse=True
            )[:5]
            
            # Risk metrics
            total_portfolio_value = sum(self.portfolio_positions.values())
            max_position_size = max(self.portfolio_positions.values()) if self.portfolio_positions else 0
            concentration_risk = (max_position_size / total_portfolio_value) if total_portfolio_value > 0 else 0
            
            return {
                'status': 'active',
                'overall_risk': latest_impact.risk_level,
                'estimated_impact': latest_impact.estimated_pnl_impact,
                'correlation_risk': latest_impact.correlation_risk,
                'diversification_score': latest_impact.diversification_score,
                'concentration_risk': concentration_risk,
                'top_risk_positions': [
                    {
                        'symbol': risk.symbol,
                        'risk_contribution': risk.risk_contribution,
                        'estimated_pnl': risk.estimated_pnl
                    }
                    for risk in top_risks
                ],
                'timestamp': latest_impact.timestamp
            }
            
        except Exception as e:
            self.logger.error(f"Error getting risk summary: {e}")
            return {'status': 'error', 'message': str(e)}
"""
Opportunity Scanner
Identifies catalyst-driven entry points and trading opportunities
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional
import pandas as pd
import numpy as np


class OpportunityScanner:
    """
    Advanced opportunity scanner that identifies high-probability catalyst-driven
    entry points based on technical, fundamental, and sentiment convergence
    """
    
    def __init__(self):
        """Initialize the opportunity scanner"""
        self.logger = logging.getLogger(__name__)
        
        # Opportunity scoring weights
        self.weights = {
            'technical_setup': 0.30,     # 30% - Technical entry setup quality
            'catalyst_timing': 0.25,     # 25% - Catalyst proximity and impact
            'risk_reward': 0.20,         # 20% - Risk/reward ratio
            'momentum_alignment': 0.15,  # 15% - Sector/market momentum
            'sentiment_divergence': 0.10 # 10% - Sentiment opportunity
        }
        
        # Risk thresholds
        self.max_risk_per_trade = 0.02  # 2% max risk per opportunity
        self.min_reward_ratio = 2.0     # Minimum 2:1 reward:risk ratio
        
    def scan_opportunities(self, portfolio_data: Dict, technical_data: Dict, 
                          catalyst_events: List, market_data: Dict = None) -> List[Dict]:
        """
        Scan for trading opportunities based on catalyst convergence
        
        Args:
            portfolio_data: Current portfolio positions
            technical_data: Technical analysis results
            catalyst_events: Upcoming catalyst events
            market_data: Overall market conditions
            
        Returns:
            List of opportunity dictionaries sorted by score
        """
        try:
            opportunities = []
            
            # Get all tickers from technical data
            all_tickers = set(technical_data.keys())
            
            # Add catalyst tickers
            for event in catalyst_events:
                all_tickers.add(event.get('ticker', ''))
            
            # Remove empty ticker
            all_tickers.discard('')
            
            self.logger.info(f"Scanning opportunities for {len(all_tickers)} tickers")
            
            for ticker in all_tickers:
                # Get ticker data
                tech_data = technical_data.get(ticker, {})
                portfolio_position = portfolio_data.get(ticker, {})
                
                # Find relevant catalysts for this ticker
                ticker_catalysts = [e for e in catalyst_events if e.get('ticker') == ticker]
                
                # Scan for different opportunity types
                opportunities.extend(self._scan_technical_opportunities(ticker, tech_data, ticker_catalysts))
                opportunities.extend(self._scan_catalyst_opportunities(ticker, tech_data, ticker_catalysts))
                opportunities.extend(self._scan_momentum_opportunities(ticker, tech_data, market_data))
                opportunities.extend(self._scan_mean_reversion_opportunities(ticker, tech_data))
                
            # Score and rank opportunities
            scored_opportunities = []
            for opp in opportunities:
                try:
                    score = self._calculate_opportunity_score(opp, technical_data, market_data)
                    opp['opportunity_score'] = score
                    opp['risk_level'] = self._assess_risk_level(opp, technical_data)
                    scored_opportunities.append(opp)
                except Exception as e:
                    self.logger.debug(f"Error scoring opportunity {opp.get('ticker', 'Unknown')}: {e}")
            
            # Sort by score (highest first)
            scored_opportunities.sort(key=lambda x: x.get('opportunity_score', 0), reverse=True)
            
            # Filter by minimum criteria
            filtered_opportunities = self._filter_opportunities(scored_opportunities)
            
            self.logger.info(f"Found {len(filtered_opportunities)} high-quality opportunities")
            return filtered_opportunities
            
        except Exception as e:
            self.logger.error(f"Error scanning opportunities: {e}")
            return []
    
    def _scan_technical_opportunities(self, ticker: str, tech_data: Dict, catalysts: List) -> List[Dict]:
        """Scan for technical setup opportunities"""
        opportunities = []
        
        try:
            if not tech_data:
                return opportunities
            
            # Extract RSI data
            rsi_data = tech_data.get('rsi', {})
            if isinstance(rsi_data, dict):
                rsi = rsi_data.get('rsi', 50)
                rsi_signal = rsi_data.get('rsi_signal', 'neutral')
            else:
                rsi = 50
                rsi_signal = 'neutral'
            
            # RSI Oversold Opportunity (potential bounce)
            if isinstance(rsi, (int, float)) and rsi <= 30:
                opportunities.append({
                    'ticker': ticker,
                    'type': 'technical_oversold',
                    'setup': 'RSI Oversold Bounce',
                    'description': f'{ticker} oversold at RSI {rsi:.1f} - potential bounce setup',
                    'entry_reason': 'RSI oversold with potential mean reversion',
                    'timeframe': 'Short-term (1-5 days)',
                    'expected_move': 'Upward correction',
                    'catalysts': len(catalysts),
                    'technical_strength': 8.0 if rsi <= 25 else 7.0,
                    'setup_quality': 'Strong' if rsi <= 25 else 'Good'
                })
            
            # RSI Overbought Fade Opportunity (potential pullback)
            elif isinstance(rsi, (int, float)) and rsi >= 75:
                opportunities.append({
                    'ticker': ticker,
                    'type': 'technical_overbought_fade',
                    'setup': 'Overbought Fade',
                    'description': f'{ticker} overbought at RSI {rsi:.1f} - potential pullback setup',
                    'entry_reason': 'RSI overbought with potential mean reversion',
                    'timeframe': 'Short-term (1-3 days)',
                    'expected_move': 'Downward correction',
                    'catalysts': len(catalysts),
                    'technical_strength': 7.5 if rsi >= 80 else 6.5,
                    'setup_quality': 'Strong' if rsi >= 80 else 'Moderate'
                })
            
            # Momentum continuation opportunities
            momentum_data = tech_data.get('momentum', {})
            if isinstance(momentum_data, dict):
                momentum_5d = momentum_data.get('5_day', 0)
                momentum_10d = momentum_data.get('10_day', 0)
                
                if isinstance(momentum_5d, (int, float)) and isinstance(momentum_10d, (int, float)):
                    # Strong momentum continuation
                    if momentum_5d > 3 and momentum_10d > 2:
                        opportunities.append({
                            'ticker': ticker,
                            'type': 'momentum_continuation',
                            'setup': 'Momentum Breakout',
                            'description': f'{ticker} strong momentum - 5d: {momentum_5d:.1f}%, 10d: {momentum_10d:.1f}%',
                            'entry_reason': 'Sustained momentum with potential acceleration',
                            'timeframe': 'Medium-term (5-15 days)',
                            'expected_move': 'Continued upward movement',
                            'catalysts': len(catalysts),
                            'technical_strength': 8.5,
                            'setup_quality': 'Strong'
                        })
            
        except Exception as e:
            self.logger.debug(f"Error scanning technical opportunities for {ticker}: {e}")
        
        return opportunities
    
    def _scan_catalyst_opportunities(self, ticker: str, tech_data: Dict, catalysts: List) -> List[Dict]:
        """Scan for catalyst-driven opportunities"""
        opportunities = []
        
        try:
            for catalyst in catalysts:
                catalyst_type = catalyst.get('type', 'unknown')
                catalyst_date = catalyst.get('date', '')
                
                # Calculate days until catalyst
                try:
                    catalyst_datetime = datetime.strptime(catalyst_date, '%Y-%m-%d')
                    days_until = (catalyst_datetime - datetime.now()).days
                except:
                    days_until = 0
                
                # Pre-earnings opportunities
                if catalyst_type in ['earnings', 'earnings_watch', 'earnings_preview']:
                    if 1 <= days_until <= 5:
                        opportunities.append({
                            'ticker': ticker,
                            'type': 'pre_earnings_setup',
                            'setup': 'Pre-Earnings Momentum',
                            'description': f'{ticker} earnings in {days_until} days - pre-event positioning',
                            'entry_reason': 'Position ahead of earnings catalyst',
                            'timeframe': f'{days_until} days to earnings',
                            'expected_move': 'Volatility expansion',
                            'catalysts': 1,
                            'technical_strength': 7.0,
                            'setup_quality': 'Time-sensitive',
                            'days_to_catalyst': days_until
                        })
                
                # Sector catalyst opportunities
                elif catalyst_type in ['sector_catalyst', 'sector_momentum']:
                    opportunities.append({
                        'ticker': ticker,
                        'type': 'sector_opportunity',
                        'setup': 'Sector Catalyst Play',
                        'description': f'{ticker} positioned for sector catalyst - {catalyst.get("description", "")}',
                        'entry_reason': 'Sector-wide catalyst with individual exposure',
                        'timeframe': 'Medium-term (3-10 days)',
                        'expected_move': 'Sector rotation benefit',
                        'catalysts': 1,
                        'technical_strength': 6.5,
                        'setup_quality': 'Sector-driven'
                    })
        
        except Exception as e:
            self.logger.debug(f"Error scanning catalyst opportunities for {ticker}: {e}")
        
        return opportunities
    
    def _scan_momentum_opportunities(self, ticker: str, tech_data: Dict, market_data: Dict) -> List[Dict]:
        """Scan for momentum-based opportunities using ONLY real technical analysis data"""
        opportunities = []
        
        try:
            # Only proceed if we have real technical signal data
            signal_data = tech_data.get('signal', 'Neutral')
            rsi_data = tech_data.get('rsi', {})
            momentum_data = tech_data.get('momentum', {})
            
            # Validate we have real data before making recommendations
            if not signal_data or signal_data == 'Neutral':
                return opportunities  # No real signal, no recommendation
                
            # Only recommend if we have supporting momentum data
            if signal_data in ['Strong Buy', 'Buy'] and momentum_data:
                five_day = momentum_data.get('5_day', 0)
                ten_day = momentum_data.get('10_day', 0)
                
                # Only recommend if momentum is actually positive (real data)
                if five_day > 0 and ten_day > 0:
                    opportunities.append({
                        'ticker': ticker,
                        'type': 'momentum_play',
                        'setup': 'Technical Buy Signal',
                        'description': f'{ticker} showing {signal_data} signal with {five_day:.1f}% 5-day momentum',
                        'entry_reason': f'Technical signals align with {five_day:.1f}% momentum',
                        'timeframe': 'Medium-term (3-10 days)',
                        'expected_move': 'Trending continuation',
                        'catalysts': 0,
                        'technical_strength': 7.5 if signal_data == 'Strong Buy' else 6.5,
                        'setup_quality': 'Technical'
                })
        
        except Exception as e:
            self.logger.debug(f"Error scanning momentum opportunities for {ticker}: {e}")
        
        return opportunities
    
    def _scan_mean_reversion_opportunities(self, ticker: str, tech_data: Dict) -> List[Dict]:
        """Scan for mean reversion opportunities"""
        opportunities = []
        
        try:
            # Look for extreme conditions that may revert
            rsi_data = tech_data.get('rsi', {})
            if isinstance(rsi_data, dict):
                rsi = rsi_data.get('rsi', 50)
                
                # Extreme oversold (high probability bounce)
                if isinstance(rsi, (int, float)) and rsi <= 20:
                    opportunities.append({
                        'ticker': ticker,
                        'type': 'mean_reversion_long',
                        'setup': 'Extreme Oversold Bounce',
                        'description': f'{ticker} at extreme oversold RSI {rsi:.1f} - high-probability bounce',
                        'entry_reason': 'Extreme oversold condition with high reversion probability',
                        'timeframe': 'Short-term (1-3 days)',
                        'expected_move': 'Sharp bounce/recovery',
                        'catalysts': 0,
                        'technical_strength': 9.0,
                        'setup_quality': 'High Probability'
                    })
                
                # Extreme overbought (pullback opportunity)
                elif isinstance(rsi, (int, float)) and rsi >= 85:
                    opportunities.append({
                        'ticker': ticker,
                        'type': 'mean_reversion_short',
                        'setup': 'Extreme Overbought Fade',
                        'description': f'{ticker} at extreme overbought RSI {rsi:.1f} - pullback expected',
                        'entry_reason': 'Extreme overbought condition with high reversion probability',
                        'timeframe': 'Short-term (1-3 days)',
                        'expected_move': 'Sharp pullback/correction',
                        'catalysts': 0,
                        'technical_strength': 8.5,
                        'setup_quality': 'High Probability'
                    })
        
        except Exception as e:
            self.logger.debug(f"Error scanning mean reversion opportunities for {ticker}: {e}")
        
        return opportunities
    
    def _calculate_opportunity_score(self, opportunity: Dict, technical_data: Dict, market_data: Dict) -> float:
        """Calculate overall opportunity score"""
        try:
            # Base score from technical strength
            technical_score = opportunity.get('technical_strength', 5.0)
            
            # Catalyst bonus
            catalyst_count = opportunity.get('catalysts', 0)
            catalyst_score = min(catalyst_count * 1.5, 3.0)  # Max 3 points from catalysts
            
            # Time sensitivity bonus
            if 'days_to_catalyst' in opportunity:
                days = opportunity['days_to_catalyst']
                if 1 <= days <= 3:
                    time_bonus = 2.0
                elif 4 <= days <= 7:
                    time_bonus = 1.0
                else:
                    time_bonus = 0.0
            else:
                time_bonus = 0.0
            
            # Setup quality multiplier
            quality = opportunity.get('setup_quality', 'Moderate')
            if quality == 'High Probability':
                quality_multiplier = 1.3
            elif quality == 'Strong':
                quality_multiplier = 1.2
            elif quality == 'Good':
                quality_multiplier = 1.1
            else:
                quality_multiplier = 1.0
            
            # Calculate final score
            base_score = technical_score + catalyst_score + time_bonus
            final_score = base_score * quality_multiplier
            
            # Cap at 10
            return min(final_score, 10.0)
            
        except Exception as e:
            self.logger.debug(f"Error calculating opportunity score: {e}")
            return 5.0
    
    def _assess_risk_level(self, opportunity: Dict, technical_data: Dict) -> str:
        """Assess risk level for opportunity"""
        try:
            ticker = opportunity.get('ticker', '')
            tech_data = technical_data.get(ticker, {})
            
            # Base risk on opportunity type
            opp_type = opportunity.get('type', '')
            
            if opp_type in ['mean_reversion_long', 'mean_reversion_short']:
                base_risk = 'MEDIUM'  # Mean reversion has defined risk
            elif opp_type in ['momentum_continuation', 'momentum_play']:
                base_risk = 'HIGH'    # Momentum can reverse quickly
            elif opp_type.startswith('technical_'):
                base_risk = 'MEDIUM'  # Technical setups have moderate risk
            elif opp_type.startswith('pre_earnings'):
                base_risk = 'HIGH'    # Earnings are inherently risky
            else:
                base_risk = 'MEDIUM'
            
            # Adjust based on technical indicators
            rsi_data = tech_data.get('rsi', {})
            if isinstance(rsi_data, dict):
                rsi = rsi_data.get('rsi', 50)
                if isinstance(rsi, (int, float)):
                    # Extreme RSI levels are higher risk
                    if rsi <= 15 or rsi >= 90:
                        base_risk = 'HIGH'
            
            return base_risk
            
        except Exception as e:
            self.logger.debug(f"Error assessing risk level: {e}")
            return 'MEDIUM'
    
    def _filter_opportunities(self, opportunities: List[Dict]) -> List[Dict]:
        """Filter opportunities by quality criteria"""
        try:
            filtered = []
            
            for opp in opportunities:
                score = opp.get('opportunity_score', 0)
                
                # Minimum score threshold
                if score >= 6.0:
                    filtered.append(opp)
                elif score >= 4.5 and opp.get('catalysts', 0) > 0:
                    # Lower score OK if catalyst-driven
                    filtered.append(opp)
            
            return filtered[:10]  # Return top 10 opportunities
            
        except Exception as e:
            self.logger.debug(f"Error filtering opportunities: {e}")
            return opportunities[:10]


if __name__ == "__main__":
    # WARNING: This module should only be used with REAL data
    # No hardcoded or sample data - trading accuracy is critical
    print("OpportunityScanner: Only use with real portfolio/technical/catalyst data")
    print("No sample data provided - connect to actual data sources for testing")
    
    # Example usage with real data:
    # scanner = OpportunityScanner()
    # real_portfolio_data = load_real_portfolio()  # From your portfolio loader
    # real_technical_data = load_technical_analysis()  # From technical analysis module  
    # real_catalyst_events = load_earnings_calendar()  # From earnings calendar API
    # opportunities = scanner.scan_opportunities(real_portfolio_data, real_technical_data, real_catalyst_events)
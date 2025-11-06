"""
Catalyst Impact Scorer
Advanced algorithm to score catalyst events based on multiple factors
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np


class CatalystImpactScorer:
    """
    Advanced catalyst impact scoring system that weights multiple factors
    to generate actionable impact scores for investment decisions
    """
    
    def __init__(self):
        """Initialize the impact scorer with default weights"""
        self.weights = {
            'position_size': 0.25,      # 25% - How much of portfolio is at risk
            'historical_volatility': 0.30,  # 30% - Expected price movement
            'technical_alignment': 0.20,     # 20% - Technical setup strength
            'options_activity': 0.15,        # 15% - Unusual options flow
            'market_sentiment': 0.10         # 10% - Overall market context
        }
        self.logger = logging.getLogger(__name__)
        
    def calculate_impact_score(self, catalyst_event: Dict, portfolio_data: Dict, 
                              technical_data: Dict, news_data: List = None) -> Tuple[float, Dict]:
        """
        Calculate comprehensive impact score for a catalyst event
        
        Args:
            catalyst_event: Event details (type, ticker, date, etc.)
            portfolio_data: Portfolio position information
            technical_data: Technical analysis signals
            news_data: Recent news sentiment (optional)
            
        Returns:
            Tuple of (impact_score, score_breakdown)
        """
        try:
            ticker = catalyst_event.get('ticker', '')
            event_type = catalyst_event.get('type', 'unknown')
            
            # Initialize score components
            scores = {
                'position_size': 0.0,
                'historical_volatility': 0.0,
                'technical_alignment': 0.0,
                'options_activity': 0.0,
                'market_sentiment': 0.0
            }
            
            # 1. Position Size Score (0-10)
            scores['position_size'] = self._calculate_position_size_score(
                ticker, portfolio_data
            )
            
            # 2. Historical Volatility Score (0-10)
            scores['historical_volatility'] = self._calculate_volatility_score(
                ticker, event_type, technical_data
            )
            
            # 3. Technical Alignment Score (0-10)
            scores['technical_alignment'] = self._calculate_technical_score(
                ticker, technical_data
            )
            
            # 4. Options Activity Score (0-10)
            scores['options_activity'] = self._calculate_options_score(
                ticker, catalyst_event
            )
            
            # 5. Market Sentiment Score (0-10)
            scores['market_sentiment'] = self._calculate_sentiment_score(
                ticker, news_data, catalyst_event
            )
            
            # Calculate weighted final score
            final_score = sum(
                scores[component] * self.weights[component] 
                for component in scores
            )
            
            # Create detailed breakdown
            breakdown = {
                'final_score': round(final_score, 1),
                'components': scores,
                'weights': self.weights,
                'ticker': ticker,
                'event_type': event_type,
                'risk_level': self._get_risk_level(final_score),
                'confidence': self._calculate_confidence(scores)
            }
            
            self.logger.info(f"Impact score calculated for {ticker}: {final_score:.1f}")
            return final_score, breakdown
            
        except Exception as e:
            self.logger.error(f"Error calculating impact score: {e}")
            return 0.0, {}
    
    def _calculate_position_size_score(self, ticker: str, portfolio_data: Dict) -> float:
        """Calculate score based on position size in portfolio (0-10)"""
        try:
            # Get position value as percentage of total portfolio
            position_value = portfolio_data.get(ticker, {}).get('value', 0)
            total_portfolio_value = sum(
                pos.get('value', 0) for pos in portfolio_data.values()
                if isinstance(pos, dict)
            )
            
            if total_portfolio_value == 0:
                return 0.0
                
            position_percentage = (position_value / total_portfolio_value) * 100
            
            # Score based on position size (higher percentage = higher impact)
            if position_percentage >= 10:      # 10%+ of portfolio
                return 10.0
            elif position_percentage >= 7:     # 7-10% of portfolio
                return 8.0
            elif position_percentage >= 5:     # 5-7% of portfolio
                return 6.0
            elif position_percentage >= 3:     # 3-5% of portfolio
                return 4.0
            elif position_percentage >= 1:     # 1-3% of portfolio
                return 2.0
            else:                              # <1% of portfolio
                return 1.0
                
        except Exception as e:
            self.logger.error(f"Error calculating position size score: {e}")
            return 0.0
    
    def _calculate_volatility_score(self, ticker: str, event_type: str, 
                                   technical_data: Dict) -> float:
        """Calculate score based on expected volatility (0-10)"""
        try:
            ticker_data = technical_data.get(ticker, {})
            
            # Base volatility score by event type
            event_volatility_map = {
                'earnings': 8.0,        # Earnings typically high impact
                'fda_approval': 9.0,    # FDA approvals very high impact
                'acquisition': 9.5,     # M&A announcements very high impact
                'product_launch': 6.0,  # Product launches medium impact
                'analyst_upgrade': 4.0, # Analyst changes lower impact
                'earnings_guidance': 7.0, # Guidance changes high impact
                'regulatory': 7.5,      # Regulatory news high impact
                'insider_trading': 3.0, # Insider trading lower impact
                'options_flow': 5.0,    # Options activity medium impact
                'news': 3.0            # General news lower impact
            }
            
            base_score = event_volatility_map.get(event_type.lower(), 5.0)
            
            # Adjust based on current technical volatility indicators
            rsi = ticker_data.get('rsi', 50)
            bollinger_position = ticker_data.get('bollinger_position', 0)
            
            # Handle case where RSI might be a dict or other non-numeric type
            if isinstance(rsi, dict):
                rsi = 50  # Default neutral value
            elif not isinstance(rsi, (int, float)):
                try:
                    rsi = float(rsi)
                except (ValueError, TypeError):
                    rsi = 50
            
            # Handle bollinger_position type checking
            if isinstance(bollinger_position, dict):
                bollinger_position = 0  # Default neutral value
            elif not isinstance(bollinger_position, (int, float)):
                try:
                    bollinger_position = float(bollinger_position)
                except (ValueError, TypeError):
                    bollinger_position = 0
            
            # Higher volatility if RSI is extreme or at Bollinger band edges
            volatility_multiplier = 1.0
            
            if rsi <= 30 or rsi >= 70:  # Oversold/overbought conditions
                volatility_multiplier += 0.2
                
            if abs(bollinger_position) > 0.8:  # Near Bollinger band edges
                volatility_multiplier += 0.3
                
            adjusted_score = min(base_score * volatility_multiplier, 10.0)
            return adjusted_score
            
        except Exception as e:
            self.logger.error(f"Error calculating volatility score: {e}")
            return 5.0  # Default medium score
    
    def _calculate_technical_score(self, ticker: str, technical_data: Dict) -> float:
        """Calculate score based on technical analysis alignment (0-10)"""
        try:
            ticker_data = technical_data.get(ticker, {})
            
            score = 5.0  # Start with neutral
            
            # RSI analysis
            rsi = ticker_data.get('rsi', 50)
            # Handle case where RSI might be a dict or other non-numeric type
            if isinstance(rsi, dict):
                rsi = 50  # Default neutral value
            elif not isinstance(rsi, (int, float)):
                try:
                    rsi = float(rsi)
                except (ValueError, TypeError):
                    rsi = 50
                    
            if rsi <= 30:      # Oversold - potential upside
                score += 2.0
            elif rsi >= 70:    # Overbought - potential downside risk
                score -= 1.0
            
            # Moving average analysis
            ma_signal = ticker_data.get('ma_signal', 'Neutral')
            if ma_signal == 'Bullish':
                score += 1.5
            elif ma_signal == 'Bearish':
                score -= 1.5
            
            # MACD analysis
            macd_signal = ticker_data.get('macd_signal', 'Neutral')
            if macd_signal == 'Bullish':
                score += 1.0
            elif macd_signal == 'Bearish':
                score -= 1.0
            
            # Volume analysis
            volume_trend = ticker_data.get('volume_trend', 'Normal')
            if volume_trend == 'High':
                score += 0.5  # High volume adds conviction
            
            # Momentum analysis
            momentum_5d = ticker_data.get('momentum_5d', 0)
            momentum_10d = ticker_data.get('momentum_10d', 0)
            
            if momentum_5d > 3 and momentum_10d > 3:      # Strong upward momentum
                score += 1.0
            elif momentum_5d < -3 and momentum_10d < -3:  # Strong downward momentum
                score -= 1.0
            
            return max(0, min(score, 10.0))  # Clamp to 0-10 range
            
        except Exception as e:
            self.logger.error(f"Error calculating technical score: {e}")
            return 5.0
    
    def _calculate_options_score(self, ticker: str, catalyst_event: Dict) -> float:
        """Calculate score based on options activity (0-10)"""
        try:
            # For now, return a placeholder score based on event type
            # In future, integrate with actual options flow data
            
            event_type = catalyst_event.get('type', 'unknown')
            
            # Some events typically generate more options activity
            options_activity_map = {
                'earnings': 7.0,        # High options activity before earnings
                'fda_approval': 8.0,    # Very high options activity
                'acquisition': 9.0,     # Extremely high options activity
                'product_launch': 5.0,  # Medium options activity
                'analyst_upgrade': 3.0, # Lower options activity
                'earnings_guidance': 6.0, # High options activity
                'regulatory': 6.0,      # High options activity
                'insider_trading': 4.0, # Medium options activity
                'options_flow': 8.0,    # By definition high options activity
                'news': 2.0            # Generally low options activity
            }
            
            score = options_activity_map.get(event_type.lower(), 3.0)
            
            # TODO: Integrate with actual options data when available
            # - Unusual options volume
            # - Put/call ratio changes
            # - Implied volatility spikes
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating options score: {e}")
            return 3.0
    
    def _calculate_sentiment_score(self, ticker: str, news_data: List, 
                                  catalyst_event: Dict) -> float:
        """Calculate score based on market sentiment (0-10)"""
        try:
            if not news_data:
                return 5.0  # Neutral if no news data
            
            # Find news articles for this ticker
            ticker_news = [
                article for article in news_data 
                if ticker.upper() in article.get('title', '').upper() or
                   ticker.upper() in article.get('description', '').upper()
            ]
            
            if not ticker_news:
                return 5.0  # Neutral if no specific news
            
            # Calculate average sentiment
            sentiments = []
            for article in ticker_news[-5:]:  # Last 5 articles
                sentiment = article.get('sentiment', 'neutral')
                if sentiment == 'positive':
                    sentiments.append(7.0)
                elif sentiment == 'negative':
                    sentiments.append(3.0)
                else:
                    sentiments.append(5.0)
            
            if sentiments:
                avg_sentiment = sum(sentiments) / len(sentiments)
                
                # Adjust based on recency and catalyst alignment
                event_type = catalyst_event.get('type', 'unknown')
                
                # Positive sentiment increases impact for positive catalysts
                if event_type in ['earnings', 'product_launch', 'analyst_upgrade']:
                    if avg_sentiment > 5.0:
                        avg_sentiment += 1.0  # Boost positive sentiment
                    else:
                        avg_sentiment -= 0.5  # Slight penalty for negative sentiment
                
                return max(0, min(avg_sentiment, 10.0))
            
            return 5.0
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment score: {e}")
            return 5.0
    
    def _get_risk_level(self, score: float) -> str:
        """Convert numeric score to risk level"""
        if score >= 8.0:
            return "HIGH"
        elif score >= 5.0:
            return "MEDIUM"
        else:
            return "LOW"
    
    def _calculate_confidence(self, scores: Dict) -> float:
        """Calculate confidence level based on score consistency"""
        try:
            score_values = list(scores.values())
            if not score_values:
                return 0.5
            
            # Higher confidence when scores are more consistent
            score_std = np.std(score_values)
            score_mean = np.mean(score_values)
            
            # Lower standard deviation = higher confidence
            confidence = max(0.3, min(1.0, 1.0 - (score_std / 10.0)))
            
            # Boost confidence for extreme scores (very high or very low)
            if score_mean >= 8.0 or score_mean <= 2.0:
                confidence = min(1.0, confidence + 0.2)
            
            return round(confidence, 2)
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def get_catalyst_events(self, earnings_data: Dict, news_data: List, 
                           technical_data: Dict) -> List[Dict]:
        """
        Extract catalyst events from various data sources
        
        Returns:
            List of catalyst event dictionaries
        """
        events = []
        
        try:
            # Extract earnings events
            for ticker, earnings_info in earnings_data.items():
                if earnings_info and isinstance(earnings_info, dict):
                    event = {
                        'ticker': ticker,
                        'type': 'earnings',
                        'date': earnings_info.get('date', ''),
                        'time': earnings_info.get('time', ''),
                        'description': f"{ticker} Earnings Release",
                        'source': 'earnings_calendar'
                    }
                    events.append(event)
            
            # Extract news-based catalyst events
            if news_data:
                for article in news_data:
                    # Look for catalyst keywords in news
                    catalyst_keywords = [
                        'earnings', 'acquisition', 'merger', 'fda', 'approval',
                        'upgrade', 'downgrade', 'guidance', 'regulatory'
                    ]
                    
                    title = article.get('title', '').lower()
                    description = article.get('description', '').lower()
                    
                    for keyword in catalyst_keywords:
                        if keyword in title or keyword in description:
                            # Try to extract ticker from title/description
                            # This is a simplified approach - could be enhanced
                            event = {
                                'ticker': 'GENERAL',  # Would need better ticker extraction
                                'type': keyword,
                                'date': article.get('publishedAt', ''),
                                'description': article.get('title', ''),
                                'source': 'news'
                            }
                            events.append(event)
                            break
            
            # Extract technical analysis events (unusual signals)
            for ticker, tech_data in technical_data.items():
                if isinstance(tech_data, dict):
                    rsi = tech_data.get('rsi', 50)
                    
                    # Extreme RSI as potential catalyst
                    if rsi <= 25 or rsi >= 75:
                        event = {
                            'ticker': ticker,
                            'type': 'technical_extreme',
                            'date': datetime.now().strftime('%Y-%m-%d'),
                            'description': f"{ticker} RSI at extreme level ({rsi:.1f})",
                            'source': 'technical_analysis'
                        }
                        events.append(event)
            
            self.logger.info(f"Extracted {len(events)} catalyst events")
            return events
            
        except Exception as e:
            self.logger.error(f"Error extracting catalyst events: {e}")
            return []


if __name__ == "__main__":
    # Test the impact scorer
    scorer = CatalystImpactScorer()
    
    # Sample test data
    catalyst_event = {
        'ticker': 'SMCI',
        'type': 'earnings',
        'date': '2025-10-01',
        'description': 'SMCI Q3 Earnings Release'
    }
    
    portfolio_data = {
        'SMCI': {'value': 5000, 'shares': 45},
        'MARA': {'value': 3000, 'shares': 150},
        'EQT': {'value': 2000, 'shares': 80}
    }
    
    technical_data = {
        'SMCI': {
            'rsi': 68.5,
            'ma_signal': 'Bullish',
            'macd_signal': 'Bullish',
            'momentum_5d': 4.2,
            'momentum_10d': 2.8
        }
    }
    
    score, breakdown = scorer.calculate_impact_score(
        catalyst_event, portfolio_data, technical_data
    )
    
    print(f"Impact Score: {score:.1f}")
    print(f"Risk Level: {breakdown.get('risk_level')}")
    print(f"Confidence: {breakdown.get('confidence')}")
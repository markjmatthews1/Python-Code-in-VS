"""
Insights Generator
Converts catalyst impact scores into actionable investment recommendations
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
from .impact_scorer import CatalystImpactScorer


class InsightsGenerator:
    """
    Generates actionable investment insights from catalyst impact analysis
    """
    
    def __init__(self):
        """Initialize the insights generator"""
        self.impact_scorer = CatalystImpactScorer()
        self.logger = logging.getLogger(__name__)
        
        # Action templates for different scenarios
        self.action_templates = {
            'high_risk_earnings': "Consider reducing {ticker} position by {percentage}% before earnings (High Risk - Score: {score})",
            'opportunity_setup': "{ticker} showing {setup_type} setup pre-catalyst (Opportunity - Score: {score})",
            'watch_entry': "Monitor {ticker} for post-{event_type} {direction} entry (Watch - Score: {score})",
            'hold_position': "Hold {ticker} through {event_type} - technical setup favorable (Hold - Score: {score})",
            'risk_management': "Set stop-loss on {ticker} at {price_level} before {event_type} (Risk Management)",
            'volatility_play': "{ticker} high volatility expected - consider options strategy (Volatility - Score: {score})",
            'sector_rotation': "Sector rotation detected - {action} {sector} exposure (Sector Play)",
            'momentum_continuation': "{ticker} strong momentum likely to continue through {event_type} (Momentum - Score: {score})"
        }
    
    def generate_daily_insights(self, portfolio_data: Dict, earnings_data: Dict, 
                              news_data: List, technical_data: Dict) -> Dict:
        """
        Generate the daily morning brief insights
        
        Returns:
            Dictionary with top insights, scores, and recommendations
        """
        try:
            # Extract all catalyst events
            catalyst_events = self.impact_scorer.get_catalyst_events(
                earnings_data, news_data, technical_data
            )
            
            # Score all catalyst events
            scored_events = []
            for event in catalyst_events:
                if event['ticker'] in portfolio_data or event['ticker'] == 'GENERAL':
                    score, breakdown = self.impact_scorer.calculate_impact_score(
                        event, portfolio_data, technical_data, news_data
                    )
                    
                    event_with_score = {
                        **event,
                        'impact_score': score,
                        'score_breakdown': breakdown,
                        'confidence': breakdown.get('confidence', 0.5)
                    }
                    scored_events.append(event_with_score)
            
            # Sort by impact score (highest first)
            scored_events.sort(key=lambda x: x['impact_score'], reverse=True)
            
            # Generate top 3 actionable insights
            top_insights = self._generate_top_insights(scored_events, portfolio_data, technical_data)
            
            # Generate additional analysis
            portfolio_risk = self._calculate_portfolio_risk(scored_events, portfolio_data)
            market_context = self._analyze_market_context(technical_data, news_data)
            
            insights_summary = {
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'top_insights': top_insights,
                'total_catalysts': len(scored_events),
                'high_impact_count': len([e for e in scored_events if e['impact_score'] >= 7.0]),
                'portfolio_risk_level': portfolio_risk['level'],
                'portfolio_risk_score': portfolio_risk['score'],
                'market_context': market_context,
                'all_scored_events': scored_events[:10]  # Top 10 for detailed view
            }
            
            self.logger.info(f"Generated insights: {len(top_insights)} top actions, {len(scored_events)} total events")
            return insights_summary
            
        except Exception as e:
            self.logger.error(f"Error generating daily insights: {e}")
            return self._get_default_insights()
    
    def _generate_top_insights(self, scored_events: List[Dict], portfolio_data: Dict, 
                              technical_data: Dict) -> List[Dict]:
        """Generate top 3 actionable insights"""
        insights = []
        
        try:
            # Process top scoring events for portfolio holdings
            portfolio_events = [e for e in scored_events if e['ticker'] in portfolio_data]
            
            for event in portfolio_events[:5]:  # Check top 5 events
                ticker = event['ticker']
                score = event['impact_score']
                event_type = event['type']
                confidence = event['confidence']
                
                # Generate specific action based on score and context
                action = self._generate_specific_action(
                    event, portfolio_data, technical_data
                )
                
                if action:
                    insight = {
                        'action': action['message'],
                        'ticker': ticker,
                        'impact_score': score,
                        'confidence': confidence,
                        'event_type': event_type,
                        'priority': action['priority'],
                        'action_type': action['type'],
                        'reasoning': action['reasoning'],
                        'risk_level': event['score_breakdown'].get('risk_level', 'MEDIUM')
                    }
                    insights.append(insight)
                    
                    # Stop when we have 3 insights
                    if len(insights) >= 3:
                        break
            
            # If we don't have 3 insights yet, add some general market insights
            while len(insights) < 3:
                general_insight = self._generate_general_insight(
                    technical_data, len(insights)
                )
                if general_insight:
                    insights.append(general_insight)
                else:
                    break
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error generating top insights: {e}")
            return []
    
    def _generate_specific_action(self, event: Dict, portfolio_data: Dict, 
                                 technical_data: Dict) -> Dict:
        """Generate specific action recommendation for an event"""
        try:
            ticker = event['ticker']
            score = event['impact_score']
            event_type = event['type']
            
            # Get technical data for this ticker
            tech_data = technical_data.get(ticker, {})
            rsi = tech_data.get('rsi', 50)
            ma_signal = tech_data.get('ma_signal', 'Neutral')
            momentum_5d = tech_data.get('momentum_5d', 0)
            
            # Get position data
            position_data = portfolio_data.get(ticker, {})
            position_value = position_data.get('value', 0)
            
            # Determine action based on score and technical setup
            if score >= 8.0:  # High impact events
                if event_type == 'earnings':
                    if rsi >= 70:  # Overbought before earnings
                        return {
                            'message': f"Consider reducing {ticker} position by 25-30% before earnings (High Risk)",
                            'type': 'RISK_REDUCTION',
                            'priority': 'HIGH',
                            'reasoning': f"High impact earnings with overbought RSI ({rsi:.1f}) suggests downside risk"
                        }
                    elif rsi <= 30 and ma_signal == 'Bullish':  # Oversold with bullish setup
                        return {
                            'message': f"{ticker} oversold with bullish setup - hold through earnings (High Conviction)",
                            'type': 'HOLD_CONVICTION',
                            'priority': 'HIGH',
                            'reasoning': f"Oversold RSI ({rsi:.1f}) with bullish MA suggests upside potential"
                        }
                
                elif event_type in ['acquisition', 'fda_approval']:
                    return {
                        'message': f"{ticker} high-impact catalyst pending - consider volatility strategy",
                        'type': 'VOLATILITY_PLAY',
                        'priority': 'HIGH',
                        'reasoning': f"{event_type.title()} events often create significant price movement"
                    }
            
            elif 5.0 <= score < 8.0:  # Medium impact events
                if momentum_5d > 3 and ma_signal == 'Bullish':
                    return {
                        'message': f"{ticker} strong momentum into {event_type} - hold position (Momentum Play)",
                        'type': 'MOMENTUM_HOLD',
                        'priority': 'MEDIUM',
                        'reasoning': f"Strong 5-day momentum ({momentum_5d:.1f}%) with bullish setup"
                    }
                elif rsi >= 75:
                    return {
                        'message': f"Set stop-loss on {ticker} before {event_type} - technically extended",
                        'type': 'RISK_MANAGEMENT',
                        'priority': 'MEDIUM',
                        'reasoning': f"Extremely overbought RSI ({rsi:.1f}) suggests pullback risk"
                    }
            
            else:  # Lower impact events
                if rsi <= 25:
                    return {
                        'message': f"Monitor {ticker} for post-{event_type} bounce - oversold condition",
                        'type': 'WATCH_ENTRY',
                        'priority': 'LOW',
                        'reasoning': f"Extremely oversold RSI ({rsi:.1f}) suggests potential bounce"
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating specific action: {e}")
            return None
    
    def _generate_general_insight(self, technical_data: Dict, insight_index: int) -> Dict:
        """Generate general market insight when specific insights are limited"""
        try:
            # Analyze overall portfolio technical health
            rsi_values = []
            momentum_values = []
            bullish_signals = 0
            bearish_signals = 0
            
            for ticker, data in technical_data.items():
                if isinstance(data, dict):
                    rsi_values.append(data.get('rsi', 50))
                    momentum_values.append(data.get('momentum_5d', 0))
                    
                    ma_signal = data.get('ma_signal', 'Neutral')
                    if ma_signal == 'Bullish':
                        bullish_signals += 1
                    elif ma_signal == 'Bearish':
                        bearish_signals += 1
            
            if not rsi_values:
                return None
            
            avg_rsi = sum(rsi_values) / len(rsi_values)
            avg_momentum = sum(momentum_values) / len(momentum_values)
            total_signals = bullish_signals + bearish_signals
            
            # Generate insight based on overall market conditions
            if insight_index == 0 and avg_rsi >= 65:
                return {
                    'action': f"Portfolio showing overbought conditions (Avg RSI: {avg_rsi:.1f}) - consider profit taking",
                    'ticker': 'PORTFOLIO',
                    'impact_score': 6.0,
                    'confidence': 0.7,
                    'event_type': 'technical_analysis',
                    'priority': 'MEDIUM',
                    'action_type': 'PORTFOLIO_MANAGEMENT',
                    'reasoning': 'Overall portfolio technical indicators suggest elevated risk',
                    'risk_level': 'MEDIUM'
                }
            
            elif insight_index == 1 and avg_momentum > 2:
                return {
                    'action': f"Strong portfolio momentum ({avg_momentum:.1f}%) - let winners run with trailing stops",
                    'ticker': 'PORTFOLIO',
                    'impact_score': 5.5,
                    'confidence': 0.6,
                    'event_type': 'momentum_analysis',
                    'priority': 'MEDIUM',
                    'action_type': 'MOMENTUM_MANAGEMENT',
                    'reasoning': 'Positive momentum suggests continued strength with proper risk management',
                    'risk_level': 'LOW'
                }
            
            elif insight_index == 2 and total_signals > 0:
                signal_ratio = bullish_signals / total_signals if total_signals > 0 else 0.5
                if signal_ratio >= 0.7:
                    return {
                        'action': f"Broad bullish signals across portfolio ({bullish_signals}/{total_signals}) - stay positioned",
                        'ticker': 'PORTFOLIO',
                        'impact_score': 5.0,
                        'confidence': 0.6,
                        'event_type': 'market_analysis',
                        'priority': 'LOW',
                        'action_type': 'MARKET_POSITIONING',
                        'reasoning': 'Strong bullish signal consensus across holdings',
                        'risk_level': 'LOW'
                    }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error generating general insight: {e}")
            return None
    
    def _calculate_portfolio_risk(self, scored_events: List[Dict], portfolio_data: Dict) -> Dict:
        """Calculate overall portfolio risk from catalyst events"""
        try:
            if not scored_events:
                return {'level': 'LOW', 'score': 2.0, 'reasoning': 'No significant catalysts detected'}
            
            # Get events affecting portfolio holdings
            portfolio_events = [e for e in scored_events if e['ticker'] in portfolio_data]
            
            if not portfolio_events:
                return {'level': 'LOW', 'score': 3.0, 'reasoning': 'No catalysts affecting current holdings'}
            
            # Calculate weighted risk based on position sizes and impact scores
            total_portfolio_value = sum(
                pos.get('value', 0) for pos in portfolio_data.values()
                if isinstance(pos, dict)
            )
            
            weighted_risk = 0.0
            high_risk_positions = []
            
            for event in portfolio_events:
                ticker = event['ticker']
                impact_score = event['impact_score']
                position_value = portfolio_data.get(ticker, {}).get('value', 0)
                
                if total_portfolio_value > 0:
                    position_weight = position_value / total_portfolio_value
                    weighted_risk += impact_score * position_weight
                    
                    if impact_score >= 7.0:
                        high_risk_positions.append(ticker)
            
            # Determine risk level
            if weighted_risk >= 6.0:
                level = 'HIGH'
                reasoning = f"High-impact catalysts affecting {len(high_risk_positions)} positions"
            elif weighted_risk >= 4.0:
                level = 'MEDIUM'
                reasoning = f"Moderate catalyst exposure across portfolio"
            else:
                level = 'LOW'
                reasoning = f"Limited catalyst risk exposure"
            
            return {
                'level': level,
                'score': weighted_risk,
                'reasoning': reasoning,
                'high_risk_positions': high_risk_positions
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating portfolio risk: {e}")
            return {'level': 'UNKNOWN', 'score': 5.0, 'reasoning': 'Error in risk calculation'}
    
    def _analyze_market_context(self, technical_data: Dict, news_data: List) -> Dict:
        """Analyze broader market context"""
        try:
            # Analyze overall sentiment from news
            positive_sentiment = 0
            negative_sentiment = 0
            neutral_sentiment = 0
            
            if news_data:
                for article in news_data[-10:]:  # Last 10 articles
                    sentiment = article.get('sentiment', 'neutral')
                    if sentiment == 'positive':
                        positive_sentiment += 1
                    elif sentiment == 'negative':
                        negative_sentiment += 1
                    else:
                        neutral_sentiment += 1
            
            total_articles = positive_sentiment + negative_sentiment + neutral_sentiment
            
            # Determine market sentiment
            if total_articles > 0:
                positive_ratio = positive_sentiment / total_articles
                if positive_ratio >= 0.6:
                    market_sentiment = 'BULLISH'
                elif positive_ratio <= 0.3:
                    market_sentiment = 'BEARISH'
                else:
                    market_sentiment = 'NEUTRAL'
            else:
                market_sentiment = 'NEUTRAL'
            
            # Analyze technical breadth
            total_stocks = len(technical_data)
            bullish_count = 0
            bearish_count = 0
            
            for ticker, data in technical_data.items():
                if isinstance(data, dict):
                    ma_signal = data.get('ma_signal', 'Neutral')
                    if ma_signal == 'Bullish':
                        bullish_count += 1
                    elif ma_signal == 'Bearish':
                        bearish_count += 1
            
            technical_breadth = 'NEUTRAL'
            if total_stocks > 0:
                bullish_ratio = bullish_count / total_stocks
                if bullish_ratio >= 0.6:
                    technical_breadth = 'BULLISH'
                elif bullish_ratio <= 0.4:
                    technical_breadth = 'BEARISH'
            
            return {
                'market_sentiment': market_sentiment,
                'technical_breadth': technical_breadth,
                'sentiment_details': {
                    'positive': positive_sentiment,
                    'negative': negative_sentiment,
                    'neutral': neutral_sentiment
                },
                'technical_details': {
                    'bullish': bullish_count,
                    'bearish': bearish_count,
                    'total': total_stocks
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error analyzing market context: {e}")
            return {
                'market_sentiment': 'NEUTRAL',
                'technical_breadth': 'NEUTRAL',
                'sentiment_details': {},
                'technical_details': {}
            }
    
    def _get_default_insights(self) -> Dict:
        """Return default insights when generation fails"""
        return {
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'top_insights': [
                {
                    'action': 'System initializing - catalyst analysis will be available shortly',
                    'ticker': 'SYSTEM',
                    'impact_score': 0.0,
                    'confidence': 1.0,
                    'event_type': 'system',
                    'priority': 'INFO',
                    'action_type': 'SYSTEM_STATUS',
                    'reasoning': 'Application startup in progress',
                    'risk_level': 'LOW'
                }
            ],
            'total_catalysts': 0,
            'high_impact_count': 0,
            'portfolio_risk_level': 'UNKNOWN',
            'portfolio_risk_score': 0.0,
            'market_context': {
                'market_sentiment': 'NEUTRAL',
                'technical_breadth': 'NEUTRAL'
            },
            'all_scored_events': []
        }


if __name__ == "__main__":
    # Test the insights generator
    generator = InsightsGenerator()
    
if __name__ == "__main__":
    # WARNING: This module should only be used with REAL data
    # No hardcoded or sample data - trading accuracy is critical
    print("InsightsGenerator: Only use with real portfolio/earnings/technical data")
    print("No sample data provided - connect to actual data sources for testing")
    
    # Example usage with real data:
    # generator = InsightsGenerator()
    # real_portfolio_data = load_real_portfolio()  # From your portfolio loader
    # real_earnings_data = load_earnings_calendar()  # From earnings calendar API  
    # real_technical_data = load_technical_analysis()  # From technical analysis module
    # insights = generator.generate_insights(real_portfolio_data, real_earnings_data, real_technical_data)
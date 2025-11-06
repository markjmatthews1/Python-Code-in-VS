"""
Social Sentiment Analyzer - Phase 4.3
Advanced social media sentiment analysis for retail investor sentiment tracking
Monitors Reddit, Twitter/X, and other social platforms for investment sentiment
"""

import logging
import requests
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class SocialMention:
    """Data structure for social media mentions"""
    platform: str
    ticker: str
    content: str
    timestamp: datetime
    author: str
    sentiment_score: float  # -1 to 1
    engagement_score: float  # likes, upvotes, retweets etc
    influence_score: float  # author influence/followers
    confidence: float


@dataclass
class SentimentAnalysis:
    """Comprehensive social sentiment analysis results"""
    ticker: str
    timestamp: datetime
    overall_sentiment: float  # -1 to 1
    sentiment_trend: str  # 'IMPROVING', 'DECLINING', 'STABLE'
    mention_volume: int
    volume_trend: str  # 'INCREASING', 'DECREASING', 'STABLE'
    top_themes: List[str]
    platform_breakdown: Dict[str, Dict]
    influence_weighted_sentiment: float
    retail_sentiment_level: str  # 'EXTREMELY_BULLISH', 'BULLISH', 'NEUTRAL', 'BEARISH', 'EXTREMELY_BEARISH'
    confidence_score: float


class SocialSentimentAnalyzer:
    """
    Advanced social sentiment analysis for retail investor sentiment
    Tracks mentions across multiple platforms and analyzes sentiment trends
    """
    
    def __init__(self):
        """Initialize the social sentiment analyzer"""
        self.logger = logging.getLogger(__name__)
        
        # Platform configurations
        self.platforms = {
            'reddit': {
                'subreddits': ['wallstreetbets', 'stocks', 'investing', 'SecurityAnalysis', 'ValueInvesting'],
                'weight': 0.4  # Reddit has high influence on retail sentiment
            },
            'twitter': {
                'keywords': ['$', 'stock', 'bull', 'bear', 'calls', 'puts'],
                'weight': 0.3
            },
            'stocktwits': {
                'weight': 0.2
            },
            'discord': {
                'weight': 0.1
            }
        }
        
        # Sentiment keywords and patterns
        self.bullish_keywords = [
            'moon', 'rocket', 'bull', 'buy', 'calls', 'long', 'squeeze', 'diamond hands',
            'hodl', 'bullish', 'pump', 'breakout', 'rally', 'green', 'gains', 'tendies'
        ]
        
        self.bearish_keywords = [
            'bear', 'crash', 'dump', 'puts', 'short', 'sell', 'bearish', 'red', 'drill',
            'tank', 'collapse', 'bubble', 'overvalued', 'decline', 'drop', 'fall'
        ]
        
        # Data cache
        self.sentiment_cache = {}
        self.mention_cache = {}
        self.last_update = {}
        
        self.logger.info("Social Sentiment Analyzer initialized")
    
    def analyze_social_sentiment(self, ticker: str, hours_back: int = 24) -> SentimentAnalysis:
        """
        Comprehensive social sentiment analysis for a ticker
        
        Args:
            ticker: Stock symbol to analyze
            hours_back: Hours of historical data to analyze
            
        Returns:
            SentimentAnalysis object with comprehensive sentiment metrics
        """
        try:
            self.logger.debug(f"Starting social sentiment analysis for {ticker}")
            
            # Gather mentions from all platforms
            all_mentions = self._collect_social_mentions(ticker, hours_back)
            
            if not all_mentions:
                return self._get_default_analysis(ticker)
            
            # Calculate sentiment metrics
            overall_sentiment = self._calculate_overall_sentiment(all_mentions)
            sentiment_trend = self._analyze_sentiment_trend(ticker, all_mentions)
            
            # Volume analysis
            mention_volume = len(all_mentions)
            volume_trend = self._analyze_volume_trend(ticker, mention_volume)
            
            # Extract themes and topics
            top_themes = self._extract_top_themes(all_mentions)
            
            # Platform breakdown
            platform_breakdown = self._analyze_platform_breakdown(all_mentions)
            
            # Influence-weighted sentiment
            influence_weighted_sentiment = self._calculate_influence_weighted_sentiment(all_mentions)
            
            # Classify sentiment level
            retail_sentiment_level = self._classify_sentiment_level(influence_weighted_sentiment)
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(all_mentions, mention_volume)
            
            analysis = SentimentAnalysis(
                ticker=ticker,
                timestamp=datetime.now(),
                overall_sentiment=overall_sentiment,
                sentiment_trend=sentiment_trend,
                mention_volume=mention_volume,
                volume_trend=volume_trend,
                top_themes=top_themes,
                platform_breakdown=platform_breakdown,
                influence_weighted_sentiment=influence_weighted_sentiment,
                retail_sentiment_level=retail_sentiment_level,
                confidence_score=confidence_score
            )
            
            self.logger.info(f"Social sentiment analysis complete for {ticker}: {retail_sentiment_level} ({overall_sentiment:.2f})")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing social sentiment for {ticker}: {e}")
            return self._get_default_analysis(ticker)
    
    def _collect_social_mentions(self, ticker: str, hours_back: int) -> List[SocialMention]:
        """Collect mentions from all social platforms"""
        try:
            all_mentions = []
            
            # Reddit mentions
            reddit_mentions = self._fetch_reddit_mentions(ticker, hours_back)
            all_mentions.extend(reddit_mentions)
            
            # Twitter mentions  
            twitter_mentions = self._fetch_twitter_mentions(ticker, hours_back)
            all_mentions.extend(twitter_mentions)
            
            # StockTwits mentions
            stocktwits_mentions = self._fetch_stocktwits_mentions(ticker, hours_back)
            all_mentions.extend(stocktwits_mentions)
            
            return all_mentions
            
        except Exception as e:
            self.logger.error(f"Error collecting social mentions for {ticker}: {e}")
            return []
    
    def _fetch_reddit_mentions(self, ticker: str, hours_back: int) -> List[SocialMention]:
        """
        Fetch Reddit mentions (simulated for development)
        In production, would use Reddit API or web scraping
        """
        try:
            mentions = []
            
            # Simulate Reddit mentions with realistic data
            sample_posts = [
                {
                    'content': f"{ticker} looking strong! Could see a breakout soon. Diamond hands! 🚀",
                    'score': 150,
                    'author': 'DiamondHands2025',
                    'subreddit': 'wallstreetbets'
                },
                {
                    'content': f"Thinking about buying {ticker} calls for earnings. What do you think?",
                    'score': 45,
                    'author': 'OptionsTrader99',
                    'subreddit': 'stocks'
                },
                {
                    'content': f"{ticker} is overvalued IMO. Might short it.",
                    'score': 23,
                    'author': 'BearMarket2025',
                    'subreddit': 'investing'
                },
                {
                    'content': f"Just bought more {ticker}. This dip is a gift! 💎🙌",
                    'score': 89,
                    'author': 'HODLer4Life',
                    'subreddit': 'wallstreetbets'
                }
            ]
            
            for post in sample_posts:
                sentiment_score = self._analyze_text_sentiment(post['content'])
                
                mention = SocialMention(
                    platform='reddit',
                    ticker=ticker,
                    content=post['content'],
                    timestamp=datetime.now() - timedelta(hours=np.random.randint(1, hours_back)),
                    author=post['author'],
                    sentiment_score=sentiment_score,
                    engagement_score=post['score'],
                    influence_score=min(1.0, post['score'] / 100.0),  # Normalize to 0-1
                    confidence=0.8
                )
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            self.logger.error(f"Error fetching Reddit mentions for {ticker}: {e}")
            return []
    
    def _fetch_twitter_mentions(self, ticker: str, hours_back: int) -> List[SocialMention]:
        """
        Fetch Twitter mentions (simulated for development)
        In production, would use Twitter API v2
        """
        try:
            mentions = []
            
            # Simulate Twitter mentions
            sample_tweets = [
                {
                    'content': f"${ticker} bullish breakout pattern forming on the daily chart 📈",
                    'likes': 67,
                    'retweets': 12,
                    'author': 'TechAnalyst'
                },
                {
                    'content': f"${ticker} earnings coming up. Expecting a beat! 🚀",
                    'likes': 34,
                    'retweets': 8,
                    'author': 'EarningsTracker'
                },
                {
                    'content': f"Sold my ${ticker} position today. Taking profits.",
                    'likes': 15,
                    'retweets': 3,
                    'author': 'ProfitTaker'
                }
            ]
            
            for tweet in sample_tweets:
                sentiment_score = self._analyze_text_sentiment(tweet['content'])
                engagement = tweet['likes'] + tweet['retweets'] * 2  # Retweets weighted higher
                
                mention = SocialMention(
                    platform='twitter',
                    ticker=ticker,
                    content=tweet['content'],
                    timestamp=datetime.now() - timedelta(hours=np.random.randint(1, hours_back)),
                    author=tweet['author'],
                    sentiment_score=sentiment_score,
                    engagement_score=engagement,
                    influence_score=min(1.0, engagement / 50.0),
                    confidence=0.7
                )
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            self.logger.error(f"Error fetching Twitter mentions for {ticker}: {e}")
            return []
    
    def _fetch_stocktwits_mentions(self, ticker: str, hours_back: int) -> List[SocialMention]:
        """
        Fetch StockTwits mentions (simulated for development)
        In production, would use StockTwits API
        """
        try:
            mentions = []
            
            # Simulate StockTwits messages
            sample_messages = [
                {
                    'content': f"${ticker} looking ready for a move higher. Volume picking up.",
                    'likes': 25,
                    'author': 'SwingTrader2025'
                },
                {
                    'content': f"${ticker} rejected at resistance. Might see pullback.",
                    'likes': 18,
                    'author': 'ChartMaster'
                }
            ]
            
            for message in sample_messages:
                sentiment_score = self._analyze_text_sentiment(message['content'])
                
                mention = SocialMention(
                    platform='stocktwits',
                    ticker=ticker,
                    content=message['content'],
                    timestamp=datetime.now() - timedelta(hours=np.random.randint(1, hours_back)),
                    author=message['author'],
                    sentiment_score=sentiment_score,
                    engagement_score=message['likes'],
                    influence_score=min(1.0, message['likes'] / 30.0),
                    confidence=0.6
                )
                mentions.append(mention)
            
            return mentions
            
        except Exception as e:
            self.logger.error(f"Error fetching StockTwits mentions for {ticker}: {e}")
            return []
    
    def _analyze_text_sentiment(self, text: str) -> float:
        """
        Analyze sentiment of text content
        Returns sentiment score from -1 (very bearish) to 1 (very bullish)
        """
        try:
            text_lower = text.lower()
            sentiment_score = 0.0
            
            # Count bullish keywords
            bullish_count = sum(1 for keyword in self.bullish_keywords if keyword in text_lower)
            bearish_count = sum(1 for keyword in self.bearish_keywords if keyword in text_lower)
            
            # Basic sentiment calculation
            if bullish_count > 0 or bearish_count > 0:
                sentiment_score = (bullish_count - bearish_count) / (bullish_count + bearish_count)
            
            # Adjust for specific patterns
            if '🚀' in text or '📈' in text or 'moon' in text_lower:
                sentiment_score += 0.3
            
            if '📉' in text or 'crash' in text_lower or 'dump' in text_lower:
                sentiment_score -= 0.3
            
            # Normalize to -1 to 1 range
            sentiment_score = max(-1.0, min(1.0, sentiment_score))
            
            return sentiment_score
            
        except Exception as e:
            self.logger.error(f"Error analyzing text sentiment: {e}")
            return 0.0
    
    def _calculate_overall_sentiment(self, mentions: List[SocialMention]) -> float:
        """Calculate overall sentiment from all mentions"""
        try:
            if not mentions:
                return 0.0
            
            # Weight by platform and engagement
            weighted_sum = 0.0
            total_weight = 0.0
            
            for mention in mentions:
                platform_weight = self.platforms.get(mention.platform, {}).get('weight', 0.1)
                engagement_weight = min(2.0, mention.engagement_score / 50.0)  # Cap at 2x
                
                weight = platform_weight * engagement_weight * mention.confidence
                weighted_sum += mention.sentiment_score * weight
                total_weight += weight
            
            if total_weight == 0:
                return 0.0
            
            return weighted_sum / total_weight
            
        except Exception as e:
            self.logger.error(f"Error calculating overall sentiment: {e}")
            return 0.0
    
    def _analyze_sentiment_trend(self, ticker: str, mentions: List[SocialMention]) -> str:
        """Analyze sentiment trend over time"""
        try:
            if len(mentions) < 5:
                return 'STABLE'
            
            # Sort mentions by timestamp
            sorted_mentions = sorted(mentions, key=lambda x: x.timestamp)
            
            # Split into older and newer halves
            midpoint = len(sorted_mentions) // 2
            older_mentions = sorted_mentions[:midpoint]
            newer_mentions = sorted_mentions[midpoint:]
            
            older_sentiment = np.mean([m.sentiment_score for m in older_mentions])
            newer_sentiment = np.mean([m.sentiment_score for m in newer_mentions])
            
            difference = newer_sentiment - older_sentiment
            
            if difference > 0.2:
                return 'IMPROVING'
            elif difference < -0.2:
                return 'DECLINING'
            else:
                return 'STABLE'
                
        except Exception as e:
            self.logger.error(f"Error analyzing sentiment trend: {e}")
            return 'STABLE'
    
    def _analyze_volume_trend(self, ticker: str, current_volume: int) -> str:
        """Analyze mention volume trend"""
        try:
            # In production, would compare with historical data
            # For now, use simple heuristics
            
            if current_volume > 20:
                return 'INCREASING'
            elif current_volume < 5:
                return 'DECREASING'
            else:
                return 'STABLE'
                
        except Exception as e:
            self.logger.error(f"Error analyzing volume trend: {e}")
            return 'STABLE'
    
    def _extract_top_themes(self, mentions: List[SocialMention]) -> List[str]:
        """Extract top themes and topics from mentions"""
        try:
            theme_keywords = {}
            
            # Common financial themes
            themes = {
                'earnings': ['earnings', 'eps', 'revenue', 'guidance'],
                'options': ['calls', 'puts', 'options', 'strike'],
                'technical': ['breakout', 'support', 'resistance', 'chart'],
                'squeeze': ['squeeze', 'short interest', 'float'],
                'catalyst': ['catalyst', 'news', 'announcement'],
                'valuation': ['overvalued', 'undervalued', 'fair value', 'pe ratio']
            }
            
            for mention in mentions:
                content_lower = mention.content.lower()
                for theme, keywords in themes.items():
                    if any(keyword in content_lower for keyword in keywords):
                        theme_keywords[theme] = theme_keywords.get(theme, 0) + 1
            
            # Return top 3 themes
            sorted_themes = sorted(theme_keywords.items(), key=lambda x: x[1], reverse=True)
            return [theme for theme, count in sorted_themes[:3]]
            
        except Exception as e:
            self.logger.error(f"Error extracting themes: {e}")
            return []
    
    def _analyze_platform_breakdown(self, mentions: List[SocialMention]) -> Dict[str, Dict]:
        """Analyze sentiment breakdown by platform"""
        try:
            platform_data = {}
            
            for platform in self.platforms.keys():
                platform_mentions = [m for m in mentions if m.platform == platform]
                
                if platform_mentions:
                    avg_sentiment = np.mean([m.sentiment_score for m in platform_mentions])
                    total_engagement = sum(m.engagement_score for m in platform_mentions)
                    
                    platform_data[platform] = {
                        'mention_count': len(platform_mentions),
                        'avg_sentiment': avg_sentiment,
                        'total_engagement': total_engagement,
                        'sentiment_label': self._sentiment_to_label(avg_sentiment)
                    }
            
            return platform_data
            
        except Exception as e:
            self.logger.error(f"Error analyzing platform breakdown: {e}")
            return {}
    
    def _calculate_influence_weighted_sentiment(self, mentions: List[SocialMention]) -> float:
        """Calculate sentiment weighted by author influence"""
        try:
            if not mentions:
                return 0.0
            
            weighted_sum = sum(m.sentiment_score * m.influence_score for m in mentions)
            total_influence = sum(m.influence_score for m in mentions)
            
            if total_influence == 0:
                return 0.0
            
            return weighted_sum / total_influence
            
        except Exception as e:
            self.logger.error(f"Error calculating influence weighted sentiment: {e}")
            return 0.0
    
    def _classify_sentiment_level(self, sentiment_score: float) -> str:
        """Classify sentiment into discrete levels"""
        if sentiment_score >= 0.6:
            return 'EXTREMELY_BULLISH'
        elif sentiment_score >= 0.2:
            return 'BULLISH'
        elif sentiment_score >= -0.2:
            return 'NEUTRAL'
        elif sentiment_score >= -0.6:
            return 'BEARISH'
        else:
            return 'EXTREMELY_BEARISH'
    
    def _sentiment_to_label(self, sentiment: float) -> str:
        """Convert sentiment score to readable label"""
        if sentiment > 0.3:
            return 'BULLISH'
        elif sentiment < -0.3:
            return 'BEARISH'
        else:
            return 'NEUTRAL'
    
    def _calculate_confidence(self, mentions: List[SocialMention], volume: int) -> float:
        """Calculate confidence in sentiment analysis"""
        try:
            # Base confidence from volume
            volume_confidence = min(1.0, volume / 10.0)  # Full confidence with 10+ mentions
            
            # Platform diversity
            platforms_used = len(set(m.platform for m in mentions))
            diversity_confidence = min(1.0, platforms_used / 3.0)  # Full confidence with 3+ platforms
            
            # Average mention confidence
            if mentions:
                avg_mention_confidence = np.mean([m.confidence for m in mentions])
            else:
                avg_mention_confidence = 0.1
            
            overall_confidence = (volume_confidence * 0.4 + 
                                diversity_confidence * 0.3 + 
                                avg_mention_confidence * 0.3)
            
            return overall_confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_default_analysis(self, ticker: str) -> SentimentAnalysis:
        """Return default analysis when data is unavailable"""
        return SentimentAnalysis(
            ticker=ticker,
            timestamp=datetime.now(),
            overall_sentiment=0.0,
            sentiment_trend='STABLE',
            mention_volume=0,
            volume_trend='STABLE',
            top_themes=[],
            platform_breakdown={},
            influence_weighted_sentiment=0.0,
            retail_sentiment_level='NEUTRAL',
            confidence_score=0.1
        )
    
    def get_catalyst_sentiment_boost(self, ticker: str, catalyst_event: Dict) -> float:
        """
        Calculate sentiment boost for catalyst events
        Integrates with existing CatalystImpactScorer
        """
        try:
            analysis = self.analyze_social_sentiment(ticker)
            
            boost = 0.0
            event_type = catalyst_event.get('type', '')
            
            # High retail interest boosts catalyst impact
            if analysis.mention_volume > 15:  # High social volume
                boost += 1.0
            
            # Sentiment alignment with event type
            if event_type in ['earnings', 'acquisition']:
                if analysis.retail_sentiment_level in ['BULLISH', 'EXTREMELY_BULLISH']:
                    boost += analysis.overall_sentiment * 2.0
                elif analysis.retail_sentiment_level in ['BEARISH', 'EXTREMELY_BEARISH']:
                    boost += 0.5  # Contrarian indicator
            
            # Trending sentiment
            if analysis.sentiment_trend == 'IMPROVING':
                boost += 0.5
            elif analysis.volume_trend == 'INCREASING':
                boost += 0.3
            
            # Apply confidence weighting
            boost *= analysis.confidence_score
            
            return min(2.0, boost)  # Cap at +2.0 boost
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment boost for {ticker}: {e}")
            return 0.0


if __name__ == "__main__":
    # Test the social sentiment analyzer
    analyzer = SocialSentimentAnalyzer()
    
    test_tickers = ['SMCI', 'MARA', 'EQT']
    
    print("=" * 60)
    print("🔍 TESTING SOCIAL SENTIMENT ANALYZER - PHASE 4.3")
    print("=" * 60)
    
    for ticker in test_tickers:
        print(f"\n📱 Analyzing social sentiment for {ticker}:")
        print("-" * 40)
        
        analysis = analyzer.analyze_social_sentiment(ticker)
        
        print(f"📊 Overall Sentiment: {analysis.overall_sentiment:.2f}")
        print(f"🎯 Sentiment Level: {analysis.retail_sentiment_level}")
        print(f"📈 Sentiment Trend: {analysis.sentiment_trend}")
        print(f"💬 Mention Volume: {analysis.mention_volume}")
        print(f"📊 Volume Trend: {analysis.volume_trend}")
        print(f"🎪 Confidence: {analysis.confidence_score:.0%}")
        
        if analysis.top_themes:
            print(f"🏷️  Top Themes: {', '.join(analysis.top_themes)}")
        
        # Test catalyst boost
        test_catalyst = {'type': 'earnings', 'ticker': ticker}
        boost = analyzer.get_catalyst_sentiment_boost(ticker, test_catalyst)
        print(f"🚀 Catalyst Sentiment Boost: +{boost:.1f}")
    
    print(f"\n✅ Social Sentiment Analyzer testing complete!")
    print("🚀 Phase 4.3 ready for integration!")
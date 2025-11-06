"""
News Sentiment Analyzer for Catalyst Scanner

Advanced NLP sentiment analysis for news articles and analyst reports
to determine bullish, bearish, or neutral sentiment with confidence scoring.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import re
import logging
from typing import Dict, List, Tuple
from datetime import datetime
import json

from utils.logger import get_logger, PerformanceTimer


class SentimentAnalyzer:
    """Advanced sentiment analysis for financial news and analyst reports"""
    
    def __init__(self):
        """Initialize sentiment analyzer with financial dictionaries"""
        self.logger = get_logger()
        
        # Financial sentiment dictionaries
        self.bullish_keywords = {
            # Strong positive indicators
            "strong": ["breakout", "surge", "soar", "skyrocket", "boom", "rally", "bull run"],
            "performance": ["beat", "exceed", "outperform", "stellar", "record", "all-time high"],
            "growth": ["accelerating", "expanding", "scaling", "robust", "strong growth"],
            "analyst": ["upgrade", "buy rating", "price target increase", "overweight"],
            "financial": ["revenue growth", "margin expansion", "cash flow", "profitability"],
            "market": ["market leader", "dominant", "competitive advantage", "moat"],
            "innovation": ["breakthrough", "revolutionary", "game changer", "disruptive"],
            
            # Moderate positive indicators  
            "moderate": ["positive", "optimistic", "confident", "stable", "solid", "healthy"],
            "trends": ["uptrend", "momentum", "gaining", "improving", "recovery"],
            "prospects": ["promising", "favorable", "bright outlook", "potential"]
        }
        
        self.bearish_keywords = {
            # Strong negative indicators
            "strong": ["crash", "plunge", "collapse", "tumble", "nosedive", "freefall"],
            "performance": ["miss", "disappoint", "underperform", "weak", "declining"],
            "problems": ["crisis", "scandal", "investigation", "lawsuit", "bankruptcy"],
            "analyst": ["downgrade", "sell rating", "price target cut", "underweight"],
            "financial": ["loss", "debt", "cash burn", "margin compression", "writedown"],
            "market": ["competition", "market share loss", "disruption", "obsolete"],
            "risks": ["risk", "concern", "warning", "caution", "uncertainty"],
            
            # Moderate negative indicators
            "moderate": ["negative", "pessimistic", "cautious", "challenging", "headwinds"],
            "trends": ["downtrend", "declining", "falling", "deteriorating", "weakening"],
            "outlook": ["cloudy", "unclear", "uncertain", "volatile", "turbulent"]
        }
        
        self.neutral_keywords = {
            "maintenance": ["maintain", "hold", "neutral", "unchanged", "stable"],
            "mixed": ["mixed", "balanced", "sideways", "flat", "range-bound"],
            "waiting": ["pending", "awaiting", "watching", "monitoring", "evaluating"]
        }
        
        # Context modifiers that can flip sentiment
        self.sentiment_modifiers = {
            "negation": ["not", "no", "never", "without", "lack of", "absence of"],
            "conditional": ["if", "unless", "provided", "assuming", "depends on"],
            "temporal": ["was", "were", "historically", "previously", "in the past"]
        }
        
        # Industry-specific sentiment patterns
        self.industry_patterns = {
            "tech": {
                "positive": ["AI", "machine learning", "cloud", "digital transformation"],
                "negative": ["data breach", "privacy concerns", "regulation", "antitrust"]
            },
            "healthcare": {
                "positive": ["FDA approval", "clinical trial success", "breakthrough"],
                "negative": ["FDA rejection", "clinical trial failure", "side effects"]
            },
            "energy": {
                "positive": ["oil price rise", "production increase", "reserves"],
                "negative": ["oil price fall", "production cut", "ESG concerns"]
            }
        }
        
        self.logger.info("Sentiment Analyzer initialized with financial dictionaries")
    
    def analyze_sentiment(self, text: str, context: str = "general") -> Dict:
        """
        Comprehensive sentiment analysis with confidence scoring
        
        Args:
            text: Text to analyze (headline + content)
            context: Context for analysis (tech, healthcare, energy, etc.)
            
        Returns:
            Dict with sentiment, confidence, and detailed breakdown
        """
        try:
            with PerformanceTimer(f"Sentiment analysis - {len(text)} chars"):
                # Preprocess text
                processed_text = self._preprocess_text(text)
                
                # Calculate sentiment scores
                sentiment_scores = self._calculate_sentiment_scores(processed_text, context)
                
                # Apply context modifiers
                modified_scores = self._apply_context_modifiers(processed_text, sentiment_scores)
                
                # Determine final sentiment
                final_sentiment = self._determine_final_sentiment(modified_scores)
                
                # Calculate confidence
                confidence = self._calculate_confidence(modified_scores, processed_text)
                
                # Generate detailed breakdown
                breakdown = self._generate_sentiment_breakdown(processed_text, modified_scores)
                
                result = {
                    "sentiment": final_sentiment,
                    "confidence": confidence,
                    "scores": modified_scores,
                    "breakdown": breakdown,
                    "word_count": len(processed_text.split()),
                    "analysis_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                self.logger.debug(f"Sentiment analysis complete: {final_sentiment} ({confidence:.1f}% confidence)")
                return result
                
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {str(e)}")
            return {
                "sentiment": "neutral",
                "confidence": 0,
                "scores": {"bullish": 0, "bearish": 0, "neutral": 0},
                "breakdown": {"error": str(e)},
                "word_count": 0,
                "analysis_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    
    def analyze_batch_sentiment(self, articles: List[Dict]) -> List[Dict]:
        """Analyze sentiment for multiple articles"""
        results = []
        
        for article in articles:
            text = f"{article.get('headline', '')} {article.get('content', '')}"
            context = article.get('industry', 'general')
            
            sentiment_result = self.analyze_sentiment(text, context)
            
            # Add sentiment to article
            article_with_sentiment = article.copy()
            article_with_sentiment.update({
                "sentiment_analysis": sentiment_result,
                "sentiment": sentiment_result["sentiment"],
                "sentiment_confidence": sentiment_result["confidence"]
            })
            
            results.append(article_with_sentiment)
        
        return results
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for sentiment analysis"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Handle common financial abbreviations
        financial_abbrevs = {
            "eps": "earnings per share",
            "pe": "price to earnings",
            "roe": "return on equity",
            "ebitda": "earnings before interest tax depreciation amortization",
            "q1": "first quarter", "q2": "second quarter", 
            "q3": "third quarter", "q4": "fourth quarter",
            "yoy": "year over year", "qoq": "quarter over quarter"
        }
        
        for abbrev, full_form in financial_abbrevs.items():
            text = text.replace(abbrev, full_form)
        
        return text.strip()
    
    def _calculate_sentiment_scores(self, text: str, context: str) -> Dict:
        """Calculate base sentiment scores"""
        scores = {"bullish": 0, "bearish": 0, "neutral": 0}
        
        # Score bullish keywords
        for category, keywords in self.bullish_keywords.items():
            weight = 2.0 if category == "strong" else 1.0
            for keyword in keywords:
                count = text.count(keyword)
                scores["bullish"] += count * weight
        
        # Score bearish keywords
        for category, keywords in self.bearish_keywords.items():
            weight = 2.0 if category == "strong" else 1.0
            for keyword in keywords:
                count = text.count(keyword)
                scores["bearish"] += count * weight
        
        # Score neutral keywords
        for category, keywords in self.neutral_keywords.items():
            for keyword in keywords:
                count = text.count(keyword)
                scores["neutral"] += count
        
        # Add industry-specific scoring
        if context in self.industry_patterns:
            industry_data = self.industry_patterns[context]
            
            for keyword in industry_data.get("positive", []):
                if keyword in text:
                    scores["bullish"] += 1.5
            
            for keyword in industry_data.get("negative", []):
                if keyword in text:
                    scores["bearish"] += 1.5
        
        return scores
    
    def _apply_context_modifiers(self, text: str, scores: Dict) -> Dict:
        """Apply context modifiers that can change sentiment"""
        modified_scores = scores.copy()
        
        # Check for negation patterns
        negation_count = sum(text.count(neg) for neg in self.sentiment_modifiers["negation"])
        if negation_count > 0:
            # Swap bullish and bearish scores if strong negation detected
            if negation_count >= 2:
                modified_scores["bullish"], modified_scores["bearish"] = \
                    modified_scores["bearish"], modified_scores["bullish"]
        
        # Check for conditional language (reduces confidence)
        conditional_count = sum(text.count(cond) for cond in self.sentiment_modifiers["conditional"])
        if conditional_count > 0:
            # Reduce extreme scores
            modified_scores["bullish"] *= 0.8
            modified_scores["bearish"] *= 0.8
            modified_scores["neutral"] += conditional_count
        
        # Check for temporal references (past events less impactful)
        temporal_count = sum(text.count(temp) for temp in self.sentiment_modifiers["temporal"])
        if temporal_count > 0:
            modified_scores["bullish"] *= 0.7
            modified_scores["bearish"] *= 0.7
        
        return modified_scores
    
    def _determine_final_sentiment(self, scores: Dict) -> str:
        """Determine final sentiment based on scores"""
        total_score = sum(scores.values())
        
        if total_score == 0:
            return "neutral"
        
        # Calculate percentages
        bullish_pct = scores["bullish"] / total_score
        bearish_pct = scores["bearish"] / total_score
        neutral_pct = scores["neutral"] / total_score
        
        # Determine sentiment with threshold
        threshold = 0.4  # 40% threshold for clear sentiment
        
        if bullish_pct > threshold and bullish_pct > bearish_pct:
            return "bullish"
        elif bearish_pct > threshold and bearish_pct > bullish_pct:
            return "bearish"
        else:
            return "neutral"
    
    def _calculate_confidence(self, scores: Dict, text: str) -> float:
        """Calculate confidence score (0-100)"""
        total_score = sum(scores.values())
        
        if total_score == 0:
            return 0
        
        # Base confidence from score distribution
        max_score = max(scores.values())
        confidence = (max_score / total_score) * 100
        
        # Adjust for text length (longer text = higher confidence)
        word_count = len(text.split())
        length_modifier = min(word_count / 50, 1.2)  # Cap at 20% boost
        confidence *= length_modifier
        
        # Adjust for absolute score magnitude
        magnitude_modifier = min(total_score / 10, 1.3)  # Cap at 30% boost
        confidence *= magnitude_modifier
        
        return min(confidence, 100)
    
    def _generate_sentiment_breakdown(self, text: str, scores: Dict) -> Dict:
        """Generate detailed sentiment breakdown"""
        breakdown = {
            "raw_scores": scores,
            "dominant_sentiment": max(scores, key=scores.get),
            "sentiment_ratio": {},
            "key_phrases": self._extract_key_phrases(text),
            "modifier_flags": self._detect_modifiers(text)
        }
        
        # Calculate sentiment ratios
        total = sum(scores.values())
        if total > 0:
            breakdown["sentiment_ratio"] = {
                sentiment: round((score / total) * 100, 1)
                for sentiment, score in scores.items()
            }
        
        return breakdown
    
    def _extract_key_phrases(self, text: str) -> List[str]:
        """Extract key sentiment-driving phrases"""
        key_phrases = []
        
        # Find phrases around sentiment keywords
        all_keywords = []
        for category in self.bullish_keywords.values():
            all_keywords.extend(category)
        for category in self.bearish_keywords.values():
            all_keywords.extend(category)
        for category in self.neutral_keywords.values():
            all_keywords.extend(category)
        
        words = text.split()
        for i, word in enumerate(words):
            for keyword in all_keywords:
                if keyword in ' '.join(words[max(0, i-2):i+3]):
                    phrase = ' '.join(words[max(0, i-2):i+3])
                    if phrase not in key_phrases:
                        key_phrases.append(phrase)
        
        return key_phrases[:5]  # Return top 5 phrases
    
    def _detect_modifiers(self, text: str) -> Dict:
        """Detect context modifiers in text"""
        flags = {}
        
        for modifier_type, keywords in self.sentiment_modifiers.items():
            count = sum(text.count(keyword) for keyword in keywords)
            if count > 0:
                flags[modifier_type] = count
        
        return flags
    
    def get_sentiment_trend(self, articles: List[Dict], ticker: str) -> Dict:
        """Analyze sentiment trend for a ticker over time"""
        try:
            ticker_articles = [a for a in articles if a.get('ticker') == ticker]
            
            if not ticker_articles:
                return {"trend": "neutral", "trend_strength": 0, "article_count": 0}
            
            # Sort by timestamp
            sorted_articles = sorted(ticker_articles, 
                                   key=lambda x: x.get('timestamp', ''))
            
            # Analyze sentiment over time
            sentiment_timeline = []
            for article in sorted_articles:
                sentiment_val = {"bullish": 1, "neutral": 0, "bearish": -1}.get(
                    article.get('sentiment', 'neutral'), 0
                )
                confidence = article.get('sentiment_confidence', 50) / 100
                weighted_sentiment = sentiment_val * confidence
                sentiment_timeline.append(weighted_sentiment)
            
            # Calculate trend
            if len(sentiment_timeline) >= 2:
                recent_avg = sum(sentiment_timeline[-3:]) / min(3, len(sentiment_timeline))
                overall_avg = sum(sentiment_timeline) / len(sentiment_timeline)
                trend_direction = "improving" if recent_avg > overall_avg else "declining"
                trend_strength = abs(recent_avg - overall_avg) * 100
            else:
                trend_direction = "neutral"
                trend_strength = 0
            
            return {
                "ticker": ticker,
                "trend": trend_direction,
                "trend_strength": trend_strength,
                "article_count": len(ticker_articles),
                "latest_sentiment": sorted_articles[-1].get('sentiment', 'neutral') if sorted_articles else 'neutral',
                "sentiment_timeline": sentiment_timeline
            }
            
        except Exception as e:
            self.logger.error(f"Error calculating sentiment trend for {ticker}: {str(e)}")
            return {"trend": "neutral", "trend_strength": 0, "article_count": 0}
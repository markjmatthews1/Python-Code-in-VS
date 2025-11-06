"""
Financial News Feed Data Collector

Real-time financial news collection using News API with ticker tagging, 
sentiment analysis, and catalyst detection for investment decision making.

Note: Uses News API instead of Schwab API since Schwab doesn't provide news endpoints.

Author: Investment Catalyst Team  
Date: September 29, 2025
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

from utils.logger import get_logger, log_api_call, log_data_update, PerformanceTimer


class SchwabNewsFeedCollector:
    """Collect and process real-time financial news using News API"""
    
    def __init__(self, auth_manager):
        """Initialize with authentication manager"""
        self.auth_manager = auth_manager
        self.logger = get_logger()
        
        # News API configuration (more reliable than Schwab for news)
        self.news_api_key = "7fdd7fe392ff4a9b9e7940a32a055fdb"  # From your existing config
        self.base_url = "https://newsapi.org/v2"
        
        # Financial news sources (high quality sources for better catalyst detection)
        self.financial_sources = [
            'bloomberg', 'reuters', 'financial-times', 'the-wall-street-journal',
            'cnbc', 'marketwatch', 'business-insider', 'seeking-alpha',
            'yahoo-finance', 'benzinga', 'thestreet', 'investor-business-daily'
        ]
        
        # Catalyst detection keywords
        self.catalyst_keywords = {
            "earnings": ["earnings", "pre-announcement", "guidance", "revenue", "profit"],
            "regulatory": ["FDA", "approval", "regulatory", "compliance", "patent"],
            "corporate": ["merger", "acquisition", "buyout", "takeover", "M&A"],
            "product": ["launch", "release", "breakthrough", "innovation", "new product"],
            "financial": ["dividend", "buyback", "debt", "financing", "capital"],
            "analyst": ["upgrade", "downgrade", "price target", "rating", "recommendation"]
        }
        
        # Sentiment keywords
        self.sentiment_keywords = {
            "bullish": ["strong", "positive", "bullish", "optimistic", "growth", "beat", "exceed", "outperform"],
            "bearish": ["weak", "negative", "bearish", "pessimistic", "decline", "miss", "underperform", "concern"],
            "neutral": ["neutral", "stable", "maintain", "steady", "unchanged", "in-line"]
        }
        
        self.logger.info("Schwab News Feed Collector initialized")
    
    def get_news_for_ticker(self, ticker: str, hours_back: int = 24) -> List[Dict]:
        """Get news articles for specific ticker using News API"""
        try:
            with PerformanceTimer(f"News API fetch for {ticker}"):
                # Calculate time range
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=hours_back)
                
                # News API endpoint for everything (includes business news)
                endpoint = "/everything"
                
                # Search query for the ticker with financial terms
                search_query = f'"{ticker}" AND (stock OR shares OR trading OR earnings OR financial OR market OR investment)'
                
                params = {
                    'q': search_query,
                    'from': start_time.strftime('%Y-%m-%d'),
                    'to': end_time.strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 20,  # Limit results
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=30
                )
                
                elapsed_time = response.elapsed.total_seconds() if hasattr(response, 'elapsed') and response.elapsed else 0
                log_api_call("NewsAPI", f"everything/{ticker}", response.status_code, elapsed_time)
                
                if response.status_code == 200:
                    news_data = response.json()
                    articles = self._process_news_articles(news_data.get('articles', []), ticker)
                    log_data_update("news_articles", len(articles), f"NewsAPI-{ticker}")
                    return articles
                else:
                    self.logger.error(f"News API error for {ticker}: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching news for {ticker}: {str(e)}")
            return []
    
    def get_news_for_portfolio(self, tickers: List[str], hours_back: int = 24) -> List[Dict]:
        """Get news for entire portfolio of tickers using News API"""
        try:
            all_articles = []
            
            with PerformanceTimer(f"News API fetch for {len(tickers)} tickers"):
                # Calculate time range
                end_time = datetime.now()
                start_time = end_time - timedelta(hours=hours_back)
                
                # Create search query for all tickers
                ticker_queries = []
                for ticker in tickers[:10]:  # Limit to 10 tickers to avoid API limits
                    ticker_queries.append(f'"{ticker}"')
                
                # Combine ticker queries with financial terms
                search_query = f'({" OR ".join(ticker_queries)}) AND (stock OR shares OR trading OR earnings OR financial OR market)'
                
                endpoint = "/everything"
                params = {
                    'q': search_query,
                    'from': start_time.strftime('%Y-%m-%d'),
                    'to': end_time.strftime('%Y-%m-%d'),
                    'sortBy': 'publishedAt',
                    'language': 'en',
                    'pageSize': 50,  # Get more articles for portfolio
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=45
                )
                
                elapsed_time = response.elapsed.total_seconds() if hasattr(response, 'elapsed') and response.elapsed else 0
                log_api_call("NewsAPI", "portfolio-everything", response.status_code, elapsed_time)
                
                if response.status_code == 200:
                    news_data = response.json()
                    
                    # Process articles and match to tickers
                    for article in news_data.get('articles', []):
                        # Determine which ticker(s) this article relates to
                        article_tickers = self._extract_tickers_from_article(article, tickers)
                        
                        for ticker in article_tickers:
                            processed_article = self._process_single_article(article, ticker)
                            if processed_article:
                                all_articles.append(processed_article)
                    
                    log_data_update("portfolio_news", len(all_articles), "NewsAPI-Portfolio")
                    return sorted(all_articles, key=lambda x: x['timestamp'], reverse=True)
                else:
                    self.logger.error(f"News API portfolio error: {response.status_code} - {response.text}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching portfolio news: {str(e)}")
            return []
    
    def _process_news_articles(self, articles: List[Dict], ticker: str) -> List[Dict]:
        """Process raw news articles into standardized format"""
        processed_articles = []
        
        for article in articles:
            processed = self._process_single_article(article, ticker)
            if processed:
                processed_articles.append(processed)
        
        return processed_articles
    
    def _process_single_article(self, article: Dict, ticker: str) -> Optional[Dict]:
        """Process a single news article from News API"""
        try:
            # News API article structure
            headline = article.get('title', '')
            content = article.get('description', '') or article.get('content', '')
            
            # Skip if no meaningful content
            if not headline and not content:
                return None
            
            # Detect sentiment
            sentiment = self._analyze_sentiment(headline, content)
            
            # Detect catalyst type
            catalyst_type = self._detect_catalyst_type(headline, content)
            
            # Calculate impact score
            impact_score = self._calculate_impact_score(headline, content, sentiment, catalyst_type)
            
            # Check for volatility indicators
            volatility_overlay = self._check_volatility_indicators(headline, content)
            
            processed_article = {
                "ticker": ticker,
                "headline": headline,
                "summary": content[:500] if content else "",
                "sentiment": sentiment,
                "catalyst_type": catalyst_type,
                "impact_score": impact_score,
                "volatility_overlay": volatility_overlay,
                "timestamp": self._parse_timestamp(article.get('publishedAt')),
                "source": article.get('source', {}).get('name', 'Unknown') if isinstance(article.get('source'), dict) else str(article.get('source', 'Unknown')),
                "url": article.get('url', ''),
                "author": article.get('author', 'Unknown')
            }
            
            return processed_article
            
        except Exception as e:
            self.logger.error(f"Error processing article: {str(e)}")
            return None
    
    def _analyze_sentiment(self, headline: str, content: str) -> str:
        """Analyze sentiment of news article using keyword matching"""
        text = f"{headline} {content}".lower()
        
        bullish_score = sum(1 for keyword in self.sentiment_keywords["bullish"] if keyword in text)
        bearish_score = sum(1 for keyword in self.sentiment_keywords["bearish"] if keyword in text)
        neutral_score = sum(1 for keyword in self.sentiment_keywords["neutral"] if keyword in text)
        
        # Determine dominant sentiment
        max_score = max(bullish_score, bearish_score, neutral_score)
        
        if max_score == 0:
            return "neutral"
        elif bullish_score == max_score:
            return "bullish"
        elif bearish_score == max_score:
            return "bearish"
        else:
            return "neutral"
    
    def _detect_catalyst_type(self, headline: str, content: str) -> str:
        """Detect the type of catalyst from article content"""
        text = f"{headline} {content}".lower()
        
        catalyst_scores = {}
        for catalyst_type, keywords in self.catalyst_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                catalyst_scores[catalyst_type] = score
        
        if not catalyst_scores:
            return "general"
        
        # Return catalyst type with highest score
        return max(catalyst_scores, key=catalyst_scores.get)
    
    def _calculate_impact_score(self, headline: str, content: str, sentiment: str, catalyst_type: str) -> float:
        """Calculate potential impact score (1-10 scale)"""
        base_score = 5.0
        
        # Sentiment modifiers
        sentiment_modifiers = {"bullish": 1.5, "bearish": 1.5, "neutral": 1.0}
        base_score *= sentiment_modifiers.get(sentiment, 1.0)
        
        # Catalyst type modifiers
        catalyst_modifiers = {
            "earnings": 2.0,
            "regulatory": 1.8,
            "corporate": 1.9,
            "product": 1.6,
            "financial": 1.4,
            "analyst": 1.3,
            "general": 1.0
        }
        base_score *= catalyst_modifiers.get(catalyst_type, 1.0)
        
        # Headline urgency indicators
        text = f"{headline} {content}".lower()
        urgency_keywords = ["breaking", "urgent", "immediate", "alert", "major", "significant"]
        urgency_multiplier = 1 + (0.2 * sum(1 for keyword in urgency_keywords if keyword in text))
        base_score *= urgency_multiplier
        
        # Cap at 10.0
        return min(base_score, 10.0)
    
    def _check_volatility_indicators(self, headline: str, content: str) -> str:
        """Check for volatility indicators in the news"""
        text = f"{headline} {content}".lower()
        
        volatility_indicators = [
            "options activity", "unusual volume", "volatility spike", 
            "after hours", "pre-market", "halt", "suspension"
        ]
        
        detected_indicators = [indicator for indicator in volatility_indicators if indicator in text]
        
        if detected_indicators:
            return f"Volatility indicators: {', '.join(detected_indicators)}"
        else:
            return "Normal volatility expected"
    
    def _extract_tickers_from_article(self, article: Dict, portfolio_tickers: List[str]) -> List[str]:
        """Extract which portfolio tickers are mentioned in the article"""
        # Combine title and description for News API articles
        text = f"{article.get('title', '')} {article.get('description', '')}".upper()
        
        mentioned_tickers = []
        for ticker in portfolio_tickers:
            if ticker.upper() in text:
                mentioned_tickers.append(ticker)
        
        return mentioned_tickers if mentioned_tickers else ["GENERAL"]
    
    def _parse_timestamp(self, timestamp_str: str) -> str:
        """Parse timestamp from News API response"""
        try:
            if timestamp_str:
                # News API uses ISO format: 2025-09-29T12:34:56Z
                if 'T' in timestamp_str:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    dt = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                    return dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def get_trending_catalysts(self, hours_back: int = 4) -> List[Dict]:
        """Get trending catalyst news using News API business headlines"""
        try:
            with PerformanceTimer("NewsAPI trending catalysts"):
                endpoint = "/top-headlines"
                params = {
                    'category': 'business',
                    'country': 'us',
                    'pageSize': 20,
                    'apiKey': self.news_api_key
                }
                
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    params=params,
                    timeout=30
                )
                
                elapsed_time = response.elapsed.total_seconds() if hasattr(response, 'elapsed') and response.elapsed else 0
                log_api_call("NewsAPI", "top-headlines", response.status_code, elapsed_time)
                
                if response.status_code == 200:
                    trending_data = response.json()
                    articles = self._process_trending_articles(trending_data.get('articles', []))
                    log_data_update("trending_catalysts", len(articles), "NewsAPI-Trending")
                    return articles
                else:
                    self.logger.error(f"News API trending error: {response.status_code}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching trending catalysts: {str(e)}")
            return []
    
    def _process_trending_articles(self, articles: List[Dict]) -> List[Dict]:
        """Process trending articles with catalyst focus"""
        processed = []
        
        for article in articles:
            # Use "MARKET" as ticker for general trending news
            ticker = "MARKET"
            processed_article = self._process_single_article(article, ticker)
            
            if processed_article and processed_article['catalyst_type'] != 'general':
                processed.append(processed_article)
        
        # Sort by impact score
        return sorted(processed, key=lambda x: x['impact_score'], reverse=True)
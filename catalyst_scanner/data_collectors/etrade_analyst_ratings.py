"""
E*TRADE Analyst Ratings Data Collector

Collect analyst ratings, price targets, and rating changes from E*TRADE API
for catalyst detection and investment decision making.

Author: Investment Catalyst Team
Date: September 29, 2025
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from utils.logger import get_logger, log_api_call, log_data_update, PerformanceTimer


class ETradeAnalystRatingsCollector:
    """Collect and process analyst ratings from E*TRADE API"""
    
    def __init__(self, auth_manager):
        """Initialize with authentication manager"""
        self.auth_manager = auth_manager
        self.logger = get_logger()
        self.base_url = "https://api.etrade.com/v1"
        
        # Rating impact scoring weights
        self.rating_impact_weights = {
            "Strong Sell -> Sell": 2,
            "Strong Sell -> Hold": 4,
            "Strong Sell -> Buy": 7,
            "Strong Sell -> Strong Buy": 9,
            "Sell -> Hold": 3,
            "Sell -> Buy": 6,
            "Sell -> Strong Buy": 8,
            "Hold -> Buy": 6,
            "Hold -> Strong Buy": 8,
            "Buy -> Strong Buy": 4,
            "Buy -> Hold": -4,
            "Buy -> Sell": -6,
            "Strong Buy -> Buy": -3,
            "Strong Buy -> Hold": -6,
            "Strong Buy -> Sell": -8,
            "Hold -> Sell": -5,
            "Hold -> Strong Sell": -7
        }
        
        # Standard rating mappings
        self.rating_standardization = {
            "1": "Strong Buy", "Strong Buy": "Strong Buy", "Buy": "Buy",
            "2": "Buy", "Moderate Buy": "Buy", "Outperform": "Buy",
            "3": "Hold", "Hold": "Hold", "Neutral": "Hold", "Market Perform": "Hold",
            "4": "Sell", "Sell": "Sell", "Underperform": "Sell", "Weak Hold": "Sell",
            "5": "Strong Sell", "Strong Sell": "Strong Sell"
        }
        
        self.logger.info("E*TRADE Analyst Ratings Collector initialized")
    
    def get_analyst_ratings(self, ticker: str) -> Dict:
        """Get current analyst ratings for a ticker"""
        try:
            with PerformanceTimer(f"E*TRADE ratings fetch for {ticker}"):
                # Get authentication headers
                headers = self.auth_manager.get_headers()
                
                # API endpoint for analyst ratings
                endpoint = f"/market/productlookup/{ticker}/analystratings"
                
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    timeout=30
                )
                
                log_api_call("E*TRADE", endpoint, response.status_code,
                           getattr(response, 'elapsed', {}).get('total_seconds', 0))
                
                if response.status_code == 200:
                    ratings_data = response.json()
                    processed_ratings = self._process_ratings_data(ratings_data, ticker)
                    log_data_update("analyst_ratings", 1, f"E*TRADE-{ticker}")
                    return processed_ratings
                else:
                    self.logger.error(f"E*TRADE ratings API error: {response.status_code} - {response.text}")
                    return {}
                    
        except Exception as e:
            self.logger.error(f"Error fetching E*TRADE ratings for {ticker}: {str(e)}")
            return {}
    
    def get_rating_changes(self, ticker: str, days_back: int = 30) -> List[Dict]:
        """Get recent rating changes for a ticker"""
        try:
            with PerformanceTimer(f"E*TRADE rating changes for {ticker}"):
                headers = self.auth_manager.get_headers()
                
                # Calculate date range
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                
                endpoint = f"/market/productlookup/{ticker}/ratingchanges"
                params = {
                    'startDate': start_date.strftime('%Y-%m-%d'),
                    'endDate': end_date.strftime('%Y-%m-%d'),
                    'maxResults': 50
                }
                
                response = requests.get(
                    f"{self.base_url}{endpoint}",
                    headers=headers,
                    params=params,
                    timeout=30
                )
                
                log_api_call("E*TRADE", endpoint, response.status_code)
                
                if response.status_code == 200:
                    changes_data = response.json()
                    processed_changes = self._process_rating_changes(changes_data, ticker)
                    log_data_update("rating_changes", len(processed_changes), f"E*TRADE-{ticker}")
                    return processed_changes
                else:
                    self.logger.error(f"E*TRADE rating changes error: {response.status_code}")
                    return []
                    
        except Exception as e:
            self.logger.error(f"Error fetching rating changes for {ticker}: {str(e)}")
            return []
    
    def get_portfolio_ratings(self, tickers: List[str]) -> List[Dict]:
        """Get analyst ratings for entire portfolio"""
        try:
            all_ratings = []
            
            for ticker in tickers:
                ticker_ratings = self.get_analyst_ratings(ticker)
                if ticker_ratings:
                    all_ratings.append(ticker_ratings)
                    
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
            
            log_data_update("portfolio_ratings", len(all_ratings), "E*TRADE-Portfolio")
            return all_ratings
            
        except Exception as e:
            self.logger.error(f"Error fetching portfolio ratings: {str(e)}")
            return []
    
    def get_recent_upgrades_downgrades(self, tickers: List[str], days_back: int = 7) -> List[Dict]:
        """Get recent upgrades and downgrades across portfolio"""
        try:
            all_changes = []
            
            for ticker in tickers:
                changes = self.get_rating_changes(ticker, days_back)
                all_changes.extend(changes)
                
                # Small delay to avoid rate limiting
                import time
                time.sleep(0.5)
            
            # Sort by impact score and date
            sorted_changes = sorted(all_changes, 
                                  key=lambda x: (x['impact_score'], x['change_date']), 
                                  reverse=True)
            
            log_data_update("recent_changes", len(sorted_changes), "E*TRADE-Portfolio")
            return sorted_changes
            
        except Exception as e:
            self.logger.error(f"Error fetching recent upgrades/downgrades: {str(e)}")
            return []
    
    def _process_ratings_data(self, ratings_data: Dict, ticker: str) -> Dict:
        """Process raw ratings data into standardized format"""
        try:
            consensus = ratings_data.get('consensus', {})
            individual_ratings = ratings_data.get('ratings', [])
            
            # Calculate consensus metrics
            avg_rating = consensus.get('averageRating', 0)
            price_target = consensus.get('averagePriceTarget', 0)
            rating_distribution = consensus.get('ratingDistribution', {})
            
            # Get most recent individual rating
            latest_rating = None
            if individual_ratings:
                latest_rating = max(individual_ratings, 
                                  key=lambda x: datetime.strptime(x.get('date', '1900-01-01'), '%Y-%m-%d'))
            
            # Standardize the rating
            current_rating = self._standardize_rating(avg_rating)
            
            processed_data = {
                "ticker": ticker,
                "current_rating": current_rating,
                "consensus_rating": current_rating,
                "price_target": float(price_target) if price_target else 0,
                "rating_distribution": {
                    "strong_buy": rating_distribution.get('strongBuy', 0),
                    "buy": rating_distribution.get('buy', 0),
                    "hold": rating_distribution.get('hold', 0),
                    "sell": rating_distribution.get('sell', 0),
                    "strong_sell": rating_distribution.get('strongSell', 0)
                },
                "total_analysts": sum(rating_distribution.values()) if rating_distribution else 0,
                "latest_change": self._get_latest_change_info(latest_rating) if latest_rating else None,
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "source": "etrade_analyst_ratings"
            }
            
            return processed_data
            
        except Exception as e:
            self.logger.error(f"Error processing ratings data for {ticker}: {str(e)}")
            return {}
    
    def _process_rating_changes(self, changes_data: Dict, ticker: str) -> List[Dict]:
        """Process rating changes data"""
        try:
            changes = changes_data.get('ratingChanges', [])
            processed_changes = []
            
            for change in changes:
                # Extract change information
                old_rating = self._standardize_rating(change.get('previousRating', ''))
                new_rating = self._standardize_rating(change.get('newRating', ''))
                
                old_target = float(change.get('previousPriceTarget', 0)) if change.get('previousPriceTarget') else 0
                new_target = float(change.get('newPriceTarget', 0)) if change.get('newPriceTarget') else 0
                
                # Calculate impact score
                impact_score = self._calculate_rating_impact_score(old_rating, new_rating, old_target, new_target)
                
                # Determine change type
                change_type = self._determine_change_type(old_rating, new_rating)
                
                processed_change = {
                    "ticker": ticker,
                    "previous_rating": old_rating,
                    "current_rating": new_rating,
                    "previous_target": old_target,
                    "price_target": new_target,
                    "change_date": change.get('date', datetime.now().strftime('%Y-%m-%d')),
                    "analyst_firm": change.get('analystFirm', 'Unknown'),
                    "analyst_name": change.get('analystName', 'Unknown'),
                    "change_type": change_type,
                    "impact_score": impact_score,
                    "target_change_percent": self._calculate_target_change_percent(old_target, new_target),
                    "reasoning": change.get('reasoning', ''),
                    "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "source": "etrade_rating_changes"
                }
                
                processed_changes.append(processed_change)
            
            return processed_changes
            
        except Exception as e:
            self.logger.error(f"Error processing rating changes for {ticker}: {str(e)}")
            return []
    
    def _standardize_rating(self, rating) -> str:
        """Standardize rating to common format"""
        if isinstance(rating, (int, float)):
            # Numerical rating (1-5 scale)
            if rating <= 1.5:
                return "Strong Buy"
            elif rating <= 2.5:
                return "Buy"
            elif rating <= 3.5:
                return "Hold"
            elif rating <= 4.5:
                return "Sell"
            else:
                return "Strong Sell"
        
        # Text rating
        rating_str = str(rating).strip()
        return self.rating_standardization.get(rating_str, "Hold")
    
    def _calculate_rating_impact_score(self, old_rating: str, new_rating: str, 
                                     old_target: float, new_target: float) -> float:
        """Calculate impact score for rating change"""
        # Base score from rating change
        change_key = f"{old_rating} -> {new_rating}"
        base_score = self.rating_impact_weights.get(change_key, 0)
        
        # Adjust for price target change
        if old_target > 0 and new_target > 0:
            target_change_percent = ((new_target - old_target) / old_target) * 100
            target_modifier = abs(target_change_percent) / 10  # 10% change = 1 point
            base_score += target_modifier
        
        # Ensure score is between 0 and 10
        return max(0, min(abs(base_score), 10))
    
    def _determine_change_type(self, old_rating: str, new_rating: str) -> str:
        """Determine if change is upgrade, downgrade, or neutral"""
        rating_values = {
            "Strong Sell": 1, "Sell": 2, "Hold": 3, "Buy": 4, "Strong Buy": 5
        }
        
        old_value = rating_values.get(old_rating, 3)
        new_value = rating_values.get(new_rating, 3)
        
        if new_value > old_value:
            return "upgrade"
        elif new_value < old_value:
            return "downgrade"
        else:
            return "neutral"
    
    def _calculate_target_change_percent(self, old_target: float, new_target: float) -> float:
        """Calculate percentage change in price target"""
        if old_target <= 0 or new_target <= 0:
            return 0
        
        return ((new_target - old_target) / old_target) * 100
    
    def _get_latest_change_info(self, latest_rating: Dict) -> Dict:
        """Extract info from latest individual rating"""
        try:
            return {
                "firm": latest_rating.get('analystFirm', 'Unknown'),
                "rating": self._standardize_rating(latest_rating.get('rating', '')),
                "target": float(latest_rating.get('priceTarget', 0)) if latest_rating.get('priceTarget') else 0,
                "date": latest_rating.get('date', ''),
                "analyst": latest_rating.get('analystName', 'Unknown')
            }
        except Exception:
            return {}
    
    def get_price_target_analysis(self, ticker: str, current_price: float) -> Dict:
        """Analyze price targets vs current price"""
        try:
            ratings_data = self.get_analyst_ratings(ticker)
            
            if not ratings_data or not ratings_data.get('price_target'):
                return {}
            
            target_price = ratings_data['price_target']
            upside_percent = ((target_price - current_price) / current_price) * 100
            
            # Categorize upside potential
            if upside_percent > 20:
                upside_category = "High Upside"
            elif upside_percent > 10:
                upside_category = "Moderate Upside"
            elif upside_percent > -10:
                upside_category = "Fair Value"
            else:
                upside_category = "Overvalued"
            
            analysis = {
                "ticker": ticker,
                "current_price": current_price,
                "target_price": target_price,
                "upside_percent": upside_percent,
                "upside_category": upside_category,
                "consensus_rating": ratings_data.get('current_rating', 'Hold'),
                "analyst_count": ratings_data.get('total_analysts', 0),
                "analysis_date": datetime.now().strftime('%Y-%m-%d')
            }
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing price targets for {ticker}: {str(e)}")
            return {}
"""
Performance Tracker for Catalyst Scanner
=======================================

Tracks catalyst prediction accuracy and portfolio performance:
- Catalyst outcome tracking (hit/miss/partial)
- Performance attribution analysis
- Prediction accuracy metrics
- Portfolio performance correlation
- Machine learning model feedback

Author: GitHub Copilot & Investment Catalyst Team
Date: October 1, 2025
Phase: 4 - Advanced Features
"""

import json
import logging
import sqlite3
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path

from utils.logger import get_logger
from utils.error_handler import api_error_handler


@dataclass
class CatalystOutcome:
    """Catalyst prediction outcome tracking"""
    catalyst_id: str              # Unique catalyst identifier
    symbol: str                   # Stock symbol
    catalyst_type: str            # earnings, news, event, etc.
    predicted_score: float        # Original catalyst score (1-10)
    predicted_direction: str      # up/down/neutral
    predicted_magnitude: float    # Expected move percentage
    
    # Actual outcomes
    actual_price_move: float      # Actual price move percentage
    actual_volume_change: float   # Volume change vs average
    outcome_classification: str   # hit/miss/partial
    accuracy_score: float         # 0-1 accuracy rating
    
    # Timing
    prediction_time: datetime
    evaluation_time: datetime
    evaluation_period_hours: int  # Hours after catalyst to evaluate
    
    # Additional metrics
    market_condition: str         # bull/bear/sideways
    sector_performance: float     # Sector performance during period
    portfolio_impact: float       # Actual portfolio impact


@dataclass
class PerformanceMetrics:
    """Performance tracking metrics"""
    # Accuracy metrics
    overall_accuracy: float       # Overall prediction accuracy 0-1
    hit_rate: float              # Percentage of correct predictions
    false_positive_rate: float   # Percentage of false alarms
    
    # Performance metrics
    average_score_accuracy: float # How close scores are to reality
    direction_accuracy: float     # Accuracy of up/down predictions
    magnitude_accuracy: float     # Accuracy of move size predictions
    
    # Portfolio metrics
    attributed_performance: float # Performance attributed to catalysts
    total_portfolio_impact: float # Total impact on portfolio
    risk_adjusted_return: float   # Sharpe-like ratio for catalyst trades
    
    # Timing and reliability
    prediction_timeliness: float  # How early predictions are made
    consistency_score: float      # Consistency across time periods
    confidence_correlation: float # How well confidence predicts accuracy
    
    # Period information
    start_date: datetime
    end_date: datetime
    total_predictions: int
    evaluated_predictions: int


class PerformanceTracker:
    """
    Tracks catalyst prediction performance and provides feedback for model improvement
    """
    
    def __init__(self, db_path: str = "catalyst_performance.db"):
        """
        Initialize performance tracker
        
        Args:
            db_path: Path to SQLite database for performance data
        """
        self.logger = get_logger()
        self.db_path = Path(db_path)
        
        # Configuration
        self.config = {
            'evaluation_periods': [1, 4, 24, 72],  # Hours to evaluate outcomes
            'accuracy_thresholds': {
                'hit': 0.7,      # >70% accuracy = hit
                'partial': 0.3,  # 30-70% accuracy = partial
                'miss': 0.0      # <30% accuracy = miss
            },
            'direction_tolerance': 0.5,   # 0.5% tolerance for direction
            'magnitude_tolerance': 0.2,   # 20% tolerance for magnitude
            'min_volume_change': 1.5,     # Minimum volume change for validation
        }
        
        # Initialize database
        self._init_database()
        
        # Performance cache
        self.metrics_cache = {}
        self.last_metrics_update = None
        
        self.logger.info("Performance tracker initialized")
    
    def _init_database(self):
        """Initialize SQLite database for performance tracking"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Catalyst outcomes table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS catalyst_outcomes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        catalyst_id TEXT UNIQUE NOT NULL,
                        symbol TEXT NOT NULL,
                        catalyst_type TEXT NOT NULL,
                        predicted_score REAL NOT NULL,
                        predicted_direction TEXT NOT NULL,
                        predicted_magnitude REAL NOT NULL,
                        actual_price_move REAL,
                        actual_volume_change REAL,
                        outcome_classification TEXT,
                        accuracy_score REAL,
                        prediction_time TEXT NOT NULL,
                        evaluation_time TEXT,
                        evaluation_period_hours INTEGER,
                        market_condition TEXT,
                        sector_performance REAL,
                        portfolio_impact REAL,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Performance metrics table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        calculation_date TEXT NOT NULL,
                        period_start TEXT NOT NULL,
                        period_end TEXT NOT NULL,
                        overall_accuracy REAL,
                        hit_rate REAL,
                        false_positive_rate REAL,
                        average_score_accuracy REAL,
                        direction_accuracy REAL,
                        magnitude_accuracy REAL,
                        attributed_performance REAL,
                        total_portfolio_impact REAL,
                        risk_adjusted_return REAL,
                        prediction_timeliness REAL,
                        consistency_score REAL,
                        confidence_correlation REAL,
                        total_predictions INTEGER,
                        evaluated_predictions INTEGER,
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Model feedback table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS model_feedback (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        feedback_date TEXT NOT NULL,
                        model_version TEXT,
                        feature_importance TEXT,  -- JSON
                        accuracy_by_type TEXT,    -- JSON
                        recommended_adjustments TEXT,  -- JSON
                        confidence_calibration TEXT,  -- JSON
                        created_at TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                conn.commit()
                
            self.logger.info("Performance tracking database initialized")
            
        except Exception as e:
            self.logger.error(f"Error initializing database: {e}")
    
    @api_error_handler("Recording catalyst prediction", reraise=False)
    def record_catalyst_prediction(self, 
                                 catalyst_id: str,
                                 symbol: str,
                                 catalyst_type: str,
                                 predicted_score: float,
                                 predicted_direction: str,
                                 predicted_magnitude: float,
                                 market_condition: str = 'unknown') -> bool:
        """
        Record a catalyst prediction for later evaluation
        
        Args:
            catalyst_id: Unique identifier for this catalyst
            symbol: Stock symbol
            catalyst_type: Type of catalyst (earnings, news, etc.)
            predicted_score: Catalyst score 1-10
            predicted_direction: Expected direction (up/down/neutral)
            predicted_magnitude: Expected price move percentage
            market_condition: Current market condition
            
        Returns:
            True if recorded successfully
        """
        try:
            prediction_time = datetime.now()
            
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT OR REPLACE INTO catalyst_outcomes (
                        catalyst_id, symbol, catalyst_type, predicted_score,
                        predicted_direction, predicted_magnitude, prediction_time,
                        market_condition
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    catalyst_id, symbol, catalyst_type, predicted_score,
                    predicted_direction, predicted_magnitude, 
                    prediction_time.isoformat(), market_condition
                ))
                
                conn.commit()
            
            self.logger.info(f"Recorded prediction for {symbol}: {catalyst_type} "
                           f"score={predicted_score} direction={predicted_direction}")
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording catalyst prediction: {e}")
            return False
    
    @api_error_handler("Evaluating catalyst outcome", reraise=False)
    def evaluate_catalyst_outcome(self, 
                                catalyst_id: str,
                                actual_price_data: Dict,
                                evaluation_period_hours: int = 24,
                                portfolio_impact: float = 0.0) -> Optional[CatalystOutcome]:
        """
        Evaluate catalyst prediction outcome
        
        Args:
            catalyst_id: Catalyst identifier to evaluate
            actual_price_data: Actual price/volume data
            evaluation_period_hours: Hours after prediction to evaluate
            portfolio_impact: Actual portfolio impact
            
        Returns:
            CatalystOutcome object or None if evaluation fails
        """
        try:
            # Get original prediction
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM catalyst_outcomes 
                    WHERE catalyst_id = ? AND evaluation_time IS NULL
                ''', (catalyst_id,))
                
                row = cursor.fetchone()
                if not row:
                    self.logger.warning(f"No prediction found for catalyst {catalyst_id}")
                    return None
                
                # Parse row data
                columns = [desc[0] for desc in cursor.description]
                prediction_data = dict(zip(columns, row))
            
            # Extract actual outcomes
            actual_price_move = actual_price_data.get('price_change_percent', 0.0)
            actual_volume_change = actual_price_data.get('volume_change_ratio', 1.0)
            sector_performance = actual_price_data.get('sector_performance', 0.0)
            
            # Calculate accuracy metrics
            accuracy_score = self._calculate_accuracy_score(
                prediction_data, actual_price_move, actual_volume_change
            )
            
            # Classify outcome
            outcome_classification = self._classify_outcome(accuracy_score)
            
            # Create outcome object
            outcome = CatalystOutcome(
                catalyst_id=catalyst_id,
                symbol=prediction_data['symbol'],
                catalyst_type=prediction_data['catalyst_type'],
                predicted_score=prediction_data['predicted_score'],
                predicted_direction=prediction_data['predicted_direction'],
                predicted_magnitude=prediction_data['predicted_magnitude'],
                actual_price_move=actual_price_move,
                actual_volume_change=actual_volume_change,
                outcome_classification=outcome_classification,
                accuracy_score=accuracy_score,
                prediction_time=datetime.fromisoformat(prediction_data['prediction_time']),
                evaluation_time=datetime.now(),
                evaluation_period_hours=evaluation_period_hours,
                market_condition=prediction_data.get('market_condition', 'unknown'),
                sector_performance=sector_performance,
                portfolio_impact=portfolio_impact
            )
            
            # Update database with evaluation results
            self._update_outcome_evaluation(outcome)
            
            self.logger.info(f"Evaluated catalyst {catalyst_id}: {outcome_classification} "
                           f"(accuracy: {accuracy_score:.2f})")
            
            return outcome
            
        except Exception as e:
            self.logger.error(f"Error evaluating catalyst outcome: {e}")
            return None
    
    def _calculate_accuracy_score(self, 
                                prediction_data: Dict,
                                actual_price_move: float,
                                actual_volume_change: float) -> float:
        """Calculate comprehensive accuracy score for prediction"""
        try:
            predicted_direction = prediction_data['predicted_direction']
            predicted_magnitude = prediction_data['predicted_magnitude']
            predicted_score = prediction_data['predicted_score']
            
            # Direction accuracy (40% weight)
            direction_correct = False
            if predicted_direction == 'up' and actual_price_move > self.config['direction_tolerance']:
                direction_correct = True
            elif predicted_direction == 'down' and actual_price_move < -self.config['direction_tolerance']:
                direction_correct = True
            elif predicted_direction == 'neutral' and abs(actual_price_move) <= self.config['direction_tolerance']:
                direction_correct = True
            
            direction_score = 1.0 if direction_correct else 0.0
            
            # Magnitude accuracy (40% weight)
            if predicted_magnitude != 0:
                magnitude_error = abs(actual_price_move - predicted_magnitude) / abs(predicted_magnitude)
                magnitude_score = max(0.0, 1.0 - magnitude_error / self.config['magnitude_tolerance'])
            else:
                magnitude_score = 1.0 if abs(actual_price_move) < 1.0 else 0.0
            
            # Volume validation (20% weight)
            volume_valid = actual_volume_change >= self.config['min_volume_change']
            volume_score = 1.0 if volume_valid else 0.5  # Partial credit if no volume
            
            # Weighted average
            accuracy_score = (
                direction_score * 0.4 +
                magnitude_score * 0.4 +
                volume_score * 0.2
            )
            
            return min(1.0, max(0.0, accuracy_score))
            
        except Exception as e:
            self.logger.error(f"Error calculating accuracy score: {e}")
            return 0.0
    
    def _classify_outcome(self, accuracy_score: float) -> str:
        """Classify prediction outcome based on accuracy score"""
        if accuracy_score >= self.config['accuracy_thresholds']['hit']:
            return 'hit'
        elif accuracy_score >= self.config['accuracy_thresholds']['partial']:
            return 'partial'
        else:
            return 'miss'
    
    def _update_outcome_evaluation(self, outcome: CatalystOutcome):
        """Update database with evaluation results"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    UPDATE catalyst_outcomes SET
                        actual_price_move = ?,
                        actual_volume_change = ?,
                        outcome_classification = ?,
                        accuracy_score = ?,
                        evaluation_time = ?,
                        evaluation_period_hours = ?,
                        sector_performance = ?,
                        portfolio_impact = ?
                    WHERE catalyst_id = ?
                ''', (
                    outcome.actual_price_move,
                    outcome.actual_volume_change,
                    outcome.outcome_classification,
                    outcome.accuracy_score,
                    outcome.evaluation_time.isoformat(),
                    outcome.evaluation_period_hours,
                    outcome.sector_performance,
                    outcome.portfolio_impact,
                    outcome.catalyst_id
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error updating outcome evaluation: {e}")
    
    @api_error_handler("Calculating performance metrics", reraise=False)
    def calculate_performance_metrics(self, 
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> PerformanceMetrics:
        """
        Calculate comprehensive performance metrics
        
        Args:
            start_date: Start date for analysis (default: 30 days ago)
            end_date: End date for analysis (default: now)
            
        Returns:
            PerformanceMetrics object
        """
        try:
            # Set default date range
            if not end_date:
                end_date = datetime.now()
            if not start_date:
                start_date = end_date - timedelta(days=30)
            
            # Check cache
            cache_key = f"{start_date.date()}_{end_date.date()}"
            if (cache_key in self.metrics_cache and 
                self.last_metrics_update and
                datetime.now() - self.last_metrics_update < timedelta(hours=1)):
                return self.metrics_cache[cache_key]
            
            # Load evaluated outcomes from database
            outcomes = self._load_evaluated_outcomes(start_date, end_date)
            
            if not outcomes:
                return self._create_empty_metrics(start_date, end_date)
            
            # Calculate metrics
            metrics = self._compute_performance_metrics(outcomes, start_date, end_date)
            
            # Store in database
            self._store_performance_metrics(metrics)
            
            # Update cache
            self.metrics_cache[cache_key] = metrics
            self.last_metrics_update = datetime.now()
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error calculating performance metrics: {e}")
            return self._create_empty_metrics(start_date or datetime.now() - timedelta(days=30), 
                                           end_date or datetime.now())
    
    def _load_evaluated_outcomes(self, start_date: datetime, end_date: datetime) -> List[Dict]:
        """Load evaluated outcomes from database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM catalyst_outcomes 
                    WHERE evaluation_time IS NOT NULL
                    AND evaluation_time BETWEEN ? AND ?
                    ORDER BY evaluation_time
                ''', (start_date.isoformat(), end_date.isoformat()))
                
                columns = [desc[0] for desc in cursor.description]
                outcomes = [dict(zip(columns, row)) for row in cursor.fetchall()]
                
                return outcomes
                
        except Exception as e:
            self.logger.error(f"Error loading evaluated outcomes: {e}")
            return []
    
    def _compute_performance_metrics(self, 
                                   outcomes: List[Dict], 
                                   start_date: datetime, 
                                   end_date: datetime) -> PerformanceMetrics:
        """Compute performance metrics from outcomes data"""
        try:
            total_predictions = len(outcomes)
            
            if total_predictions == 0:
                return self._create_empty_metrics(start_date, end_date)
            
            # Basic accuracy metrics
            hits = len([o for o in outcomes if o['outcome_classification'] == 'hit'])
            partials = len([o for o in outcomes if o['outcome_classification'] == 'partial'])
            misses = len([o for o in outcomes if o['outcome_classification'] == 'miss'])
            
            hit_rate = hits / total_predictions
            overall_accuracy = sum(o['accuracy_score'] for o in outcomes) / total_predictions
            false_positive_rate = misses / total_predictions
            
            # Direction accuracy
            direction_correct = 0
            for outcome in outcomes:
                predicted_dir = outcome['predicted_direction']
                actual_move = outcome['actual_price_move'] or 0
                
                if ((predicted_dir == 'up' and actual_move > 0.5) or
                    (predicted_dir == 'down' and actual_move < -0.5) or
                    (predicted_dir == 'neutral' and abs(actual_move) <= 0.5)):
                    direction_correct += 1
            
            direction_accuracy = direction_correct / total_predictions
            
            # Magnitude accuracy
            magnitude_errors = []
            for outcome in outcomes:
                predicted_mag = outcome['predicted_magnitude'] or 0
                actual_move = outcome['actual_price_move'] or 0
                if predicted_mag != 0:
                    error = abs(actual_move - predicted_mag) / abs(predicted_mag)
                    magnitude_errors.append(min(error, 2.0))  # Cap at 200%
            
            magnitude_accuracy = 1.0 - (sum(magnitude_errors) / len(magnitude_errors)) if magnitude_errors else 0.5
            magnitude_accuracy = max(0.0, magnitude_accuracy)
            
            # Portfolio impact metrics
            portfolio_impacts = [o['portfolio_impact'] or 0 for o in outcomes]
            total_portfolio_impact = sum(portfolio_impacts)
            attributed_performance = total_portfolio_impact / len(portfolio_impacts) if portfolio_impacts else 0
            
            # Risk-adjusted return (simplified)
            positive_impacts = [p for p in portfolio_impacts if p > 0]
            negative_impacts = [p for p in portfolio_impacts if p < 0]
            
            avg_positive = sum(positive_impacts) / len(positive_impacts) if positive_impacts else 0
            avg_negative = abs(sum(negative_impacts) / len(negative_impacts)) if negative_impacts else 1
            
            risk_adjusted_return = avg_positive / avg_negative if avg_negative > 0 else 0
            
            # Timing and consistency
            prediction_times = [
                datetime.fromisoformat(o['prediction_time']) for o in outcomes
                if o['prediction_time']
            ]
            
            evaluation_times = [
                datetime.fromisoformat(o['evaluation_time']) for o in outcomes
                if o['evaluation_time']
            ]
            
            if prediction_times and evaluation_times:
                # Average time from prediction to evaluation
                time_deltas = [
                    (eval_time - pred_time).total_seconds() / 3600  # Hours
                    for pred_time, eval_time in zip(prediction_times, evaluation_times)
                ]
                prediction_timeliness = 1.0 / (1.0 + sum(time_deltas) / len(time_deltas) / 24)  # Normalize by day
            else:
                prediction_timeliness = 0.5
            
            # Consistency score (variance in accuracy)
            accuracy_scores = [o['accuracy_score'] for o in outcomes if o['accuracy_score'] is not None]
            if len(accuracy_scores) > 1:
                consistency_score = 1.0 - np.std(accuracy_scores) / np.mean(accuracy_scores)
                consistency_score = max(0.0, min(1.0, consistency_score))
            else:
                consistency_score = 0.5
            
            # Confidence correlation (how well catalyst scores predict accuracy)
            catalyst_scores = [o['predicted_score'] for o in outcomes]
            if len(catalyst_scores) > 1 and len(accuracy_scores) > 1:
                correlation = np.corrcoef(catalyst_scores, accuracy_scores)[0, 1]
                confidence_correlation = max(0.0, correlation) if not np.isnan(correlation) else 0.0
            else:
                confidence_correlation = 0.0
            
            return PerformanceMetrics(
                overall_accuracy=overall_accuracy,
                hit_rate=hit_rate,
                false_positive_rate=false_positive_rate,
                average_score_accuracy=overall_accuracy,  # Simplified
                direction_accuracy=direction_accuracy,
                magnitude_accuracy=magnitude_accuracy,
                attributed_performance=attributed_performance,
                total_portfolio_impact=total_portfolio_impact,
                risk_adjusted_return=risk_adjusted_return,
                prediction_timeliness=prediction_timeliness,
                consistency_score=consistency_score,
                confidence_correlation=confidence_correlation,
                start_date=start_date,
                end_date=end_date,
                total_predictions=total_predictions,
                evaluated_predictions=total_predictions
            )
            
        except Exception as e:
            self.logger.error(f"Error computing performance metrics: {e}")
            return self._create_empty_metrics(start_date, end_date)
    
    def _create_empty_metrics(self, start_date: datetime, end_date: datetime) -> PerformanceMetrics:
        """Create empty metrics when no data is available"""
        return PerformanceMetrics(
            overall_accuracy=0.0,
            hit_rate=0.0,
            false_positive_rate=0.0,
            average_score_accuracy=0.0,
            direction_accuracy=0.0,
            magnitude_accuracy=0.0,
            attributed_performance=0.0,
            total_portfolio_impact=0.0,
            risk_adjusted_return=0.0,
            prediction_timeliness=0.0,
            consistency_score=0.0,
            confidence_correlation=0.0,
            start_date=start_date,
            end_date=end_date,
            total_predictions=0,
            evaluated_predictions=0
        )
    
    def _store_performance_metrics(self, metrics: PerformanceMetrics):
        """Store performance metrics in database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO performance_metrics (
                        calculation_date, period_start, period_end,
                        overall_accuracy, hit_rate, false_positive_rate,
                        average_score_accuracy, direction_accuracy, magnitude_accuracy,
                        attributed_performance, total_portfolio_impact, risk_adjusted_return,
                        prediction_timeliness, consistency_score, confidence_correlation,
                        total_predictions, evaluated_predictions
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    datetime.now().isoformat(),
                    metrics.start_date.isoformat(),
                    metrics.end_date.isoformat(),
                    metrics.overall_accuracy,
                    metrics.hit_rate,
                    metrics.false_positive_rate,
                    metrics.average_score_accuracy,
                    metrics.direction_accuracy,
                    metrics.magnitude_accuracy,
                    metrics.attributed_performance,
                    metrics.total_portfolio_impact,
                    metrics.risk_adjusted_return,
                    metrics.prediction_timeliness,
                    metrics.consistency_score,
                    metrics.confidence_correlation,
                    metrics.total_predictions,
                    metrics.evaluated_predictions
                ))
                
                conn.commit()
                
        except Exception as e:
            self.logger.error(f"Error storing performance metrics: {e}")
    
    def get_performance_summary(self, days: int = 30) -> Dict:
        """Get human-readable performance summary"""
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            metrics = self.calculate_performance_metrics(start_date, end_date)
            
            return {
                'period': f"{days} days",
                'total_predictions': metrics.total_predictions,
                'overall_accuracy': f"{metrics.overall_accuracy:.1%}",
                'hit_rate': f"{metrics.hit_rate:.1%}",
                'direction_accuracy': f"{metrics.direction_accuracy:.1%}",
                'portfolio_impact': f"${metrics.total_portfolio_impact:,.0f}",
                'risk_adjusted_return': f"{metrics.risk_adjusted_return:.2f}",
                'consistency': f"{metrics.consistency_score:.1%}",
                'status': 'excellent' if metrics.overall_accuracy > 0.7 else
                         'good' if metrics.overall_accuracy > 0.5 else
                         'needs_improvement'
            }
            
        except Exception as e:
            self.logger.error(f"Error getting performance summary: {e}")
            return {'status': 'error', 'message': str(e)}
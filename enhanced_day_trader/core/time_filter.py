#!/usr/bin/env python3
"""
Enhanced Time-Based Signal Filtering System
===========================================

Implements time-based filters to avoid trading during unfavorable market conditions.
One of the key improvements over the original system which traded at all hours.

Key Features:
- Optimal trading hour windows (10-11:30 AM, 1:30-3:30 PM)  
- Avoids market open/close volatility and lunch time low volume
- Intraday pattern recognition
- Time-based signal strength adjustment

Author: GitHub Copilot
Date: September 26, 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime, time
import logging
from typing import Tuple, List, Dict, Optional

from ..config.trading_config import OPTIMAL_TRADING_HOURS, AVOID_TRADING_HOURS

logger = logging.getLogger(__name__)

class TimeBasedFilter:
    """
    Filters trading signals based on optimal time windows.
    Major improvement over original system that ignored time of day.
    """
    
    def __init__(self):
        self.optimal_hours = OPTIMAL_TRADING_HOURS
        self.avoid_hours = AVOID_TRADING_HOURS
        self.trading_stats = {
            'total_signals': 0,
            'time_filtered': 0,
            'optimal_window_signals': 0,
            'avoided_window_signals': 0
        }
        
    def is_optimal_trading_time(self, timestamp: datetime) -> bool:
        """
        Check if timestamp falls within optimal trading hours.
        
        Args:
            timestamp: DateTime to check
            
        Returns:
            bool: True if within optimal trading window
        """
        # Convert timestamp to decimal hour (e.g., 10:30 AM = 10.5)
        hour_decimal = timestamp.hour + timestamp.minute / 60.0
        
        # Check against optimal windows
        for start, end in self.optimal_hours:
            if start <= hour_decimal <= end:
                return True
                
        return False
        
    def should_avoid_trading(self, timestamp: datetime) -> bool:
        """
        Check if timestamp falls within hours to avoid trading.
        
        Args:
            timestamp: DateTime to check
            
        Returns:
            bool: True if should avoid trading at this time
        """
        hour_decimal = timestamp.hour + timestamp.minute / 60.0
        
        # Check against avoid windows  
        for start, end in self.avoid_hours:
            if start <= hour_decimal <= end:
                return True
                
        return False
        
    def get_time_signal_strength(self, timestamp: datetime) -> float:
        """
        Get time-based signal strength multiplier.
        
        Optimal times get full strength (1.0)
        Avoid times get zero strength (0.0)  
        Other times get reduced strength (0.5)
        
        Args:
            timestamp: DateTime to evaluate
            
        Returns:
            float: Signal strength multiplier (0.0 to 1.0)
        """
        if self.should_avoid_trading(timestamp):
            return 0.0
        elif self.is_optimal_trading_time(timestamp):
            return 1.0
        else:
            return 0.5  # Neutral time periods
            
    def filter_signals_by_time(self, signals_df: pd.DataFrame, timestamp_col: str = 'timestamp') -> pd.DataFrame:
        """
        Filter trading signals based on time windows.
        
        Args:
            signals_df: DataFrame with trading signals
            timestamp_col: Name of timestamp column
            
        Returns:
            pd.DataFrame: Filtered signals with time_filter_strength column
        """
        if timestamp_col not in signals_df.columns:
            logger.error(f"Timestamp column '{timestamp_col}' not found")
            return signals_df
            
        # Ensure timestamp column is datetime
        signals_df[timestamp_col] = pd.to_datetime(signals_df[timestamp_col])
        
        # Calculate time-based signal strength
        signals_df['time_filter_strength'] = signals_df[timestamp_col].apply(
            self.get_time_signal_strength
        )
        
        # Update statistics
        self.trading_stats['total_signals'] += len(signals_df)
        
        # Count signals in different time windows
        optimal_count = sum(signals_df[timestamp_col].apply(self.is_optimal_trading_time))
        avoid_count = sum(signals_df[timestamp_col].apply(self.should_avoid_trading))
        filtered_count = sum(signals_df['time_filter_strength'] == 0.0)
        
        self.trading_stats['optimal_window_signals'] += optimal_count
        self.trading_stats['avoided_window_signals'] += avoid_count
        self.trading_stats['time_filtered'] += filtered_count
        
        logger.info(f"Time filtering: {len(signals_df)} signals, {filtered_count} filtered out")
        
        return signals_df
        
    def analyze_intraday_patterns(self, trade_results_df: pd.DataFrame) -> Dict:
        """
        Analyze historical performance by time of day to validate time filters.
        
        Args:
            trade_results_df: Historical trade results with timestamp and pnl
            
        Returns:
            dict: Analysis of performance by time periods
        """
        if 'timestamp' not in trade_results_df.columns or 'pnl' not in trade_results_df.columns:
            logger.error("Required columns (timestamp, pnl) not found for pattern analysis")
            return {}
            
        # Ensure timestamp is datetime
        trade_results_df['timestamp'] = pd.to_datetime(trade_results_df['timestamp'])
        
        # Create hour_decimal column
        trade_results_df['hour_decimal'] = (
            trade_results_df['timestamp'].dt.hour + 
            trade_results_df['timestamp'].dt.minute / 60.0
        )
        
        # Analyze performance by hour
        hourly_stats = {}
        
        for hour in np.arange(9.5, 16.1, 0.5):  # 9:30 AM to 4:00 PM in 30-min blocks
            hour_mask = (
                (trade_results_df['hour_decimal'] >= hour) & 
                (trade_results_df['hour_decimal'] < hour + 0.5)
            )
            hour_trades = trade_results_df[hour_mask]
            
            if len(hour_trades) > 0:
                win_rate = (hour_trades['pnl'] > 0).mean()
                avg_pnl = hour_trades['pnl'].mean()
                trade_count = len(hour_trades)
                
                # Determine time classification
                time_classification = 'neutral'
                hour_time = datetime.strptime(f"{int(hour)}:{int((hour % 1) * 60)}", "%H:%M").time()
                
                if self.is_optimal_trading_time(datetime.combine(datetime.today(), hour_time)):
                    time_classification = 'optimal'
                elif self.should_avoid_trading(datetime.combine(datetime.today(), hour_time)):
                    time_classification = 'avoid'
                
                hourly_stats[f"{int(hour):02d}:{int((hour % 1) * 60):02d}"] = {
                    'win_rate': win_rate,
                    'avg_pnl': avg_pnl,
                    'trade_count': trade_count,
                    'classification': time_classification
                }
        
        # Calculate summary statistics
        optimal_trades = trade_results_df[
            trade_results_df['hour_decimal'].apply(
                lambda x: self.is_optimal_trading_time(
                    datetime.combine(datetime.today(), time(int(x), int((x % 1) * 60)))
                )
            )
        ]
        
        avoid_trades = trade_results_df[
            trade_results_df['hour_decimal'].apply(
                lambda x: self.should_avoid_trading(
                    datetime.combine(datetime.today(), time(int(x), int((x % 1) * 60)))
                )
            )
        ]
        
        analysis = {
            'hourly_breakdown': hourly_stats,
            'summary': {
                'optimal_window_win_rate': (optimal_trades['pnl'] > 0).mean() if len(optimal_trades) > 0 else 0,
                'avoid_window_win_rate': (avoid_trades['pnl'] > 0).mean() if len(avoid_trades) > 0 else 0,
                'optimal_window_avg_pnl': optimal_trades['pnl'].mean() if len(optimal_trades) > 0 else 0,
                'avoid_window_avg_pnl': avoid_trades['pnl'].mean() if len(avoid_trades) > 0 else 0,
                'optimal_trade_count': len(optimal_trades),
                'avoid_trade_count': len(avoid_trades),
                'filter_effectiveness': 0  # Will be calculated
            }
        }
        
        # Calculate filter effectiveness
        if len(avoid_trades) > 0 and len(optimal_trades) > 0:
            optimal_win_rate = analysis['summary']['optimal_window_win_rate']
            avoid_win_rate = analysis['summary']['avoid_window_win_rate']
            analysis['summary']['filter_effectiveness'] = optimal_win_rate - avoid_win_rate
        
        return analysis
        
    def get_optimal_entry_times(self, current_time: datetime) -> List[Tuple[datetime, datetime]]:
        """
        Get next optimal trading time windows from current time.
        
        Args:
            current_time: Current timestamp
            
        Returns:
            List of (start_time, end_time) tuples for next optimal windows
        """
        current_date = current_time.date()
        current_hour = current_time.hour + current_time.minute / 60.0
        
        upcoming_windows = []
        
        for start_hour, end_hour in self.optimal_hours:
            # Convert decimal hours to datetime
            start_dt = datetime.combine(
                current_date,
                time(int(start_hour), int((start_hour % 1) * 60))
            )
            end_dt = datetime.combine(
                current_date,
                time(int(end_hour), int((end_hour % 1) * 60))
            )
            
            # Only include future windows
            if start_hour > current_hour:
                upcoming_windows.append((start_dt, end_dt))
        
        return upcoming_windows
        
    def get_time_filter_report(self) -> Dict:
        """
        Generate report on time filtering performance.
        
        Returns:
            dict: Time filtering statistics and effectiveness
        """
        if self.trading_stats['total_signals'] == 0:
            return {'error': 'No signals processed yet'}
        
        filter_rate = (
            self.trading_stats['time_filtered'] / 
            self.trading_stats['total_signals']
        )
        
        optimal_rate = (
            self.trading_stats['optimal_window_signals'] / 
            self.trading_stats['total_signals']  
        )
        
        return {
            'total_signals_processed': self.trading_stats['total_signals'],
            'signals_filtered_out': self.trading_stats['time_filtered'],
            'filter_rate': f"{filter_rate:.1%}",
            'optimal_window_signals': self.trading_stats['optimal_window_signals'],
            'optimal_window_rate': f"{optimal_rate:.1%}",
            'avoid_window_signals': self.trading_stats['avoided_window_signals'],
            'trading_windows': {
                'optimal': [f"{s:.1f}-{e:.1f}" for s, e in self.optimal_hours],
                'avoid': [f"{s:.1f}-{e:.1f}" for s, e in self.avoid_hours]
            },
            'effectiveness': "Time filtering prevents trading during high-volatility periods"
        }

def test_time_filter():
    """Test the time-based filtering system"""
    
    # Create test data with various timestamps
    test_times = [
        datetime(2025, 1, 1, 9, 30),   # Market open - should avoid
        datetime(2025, 1, 1, 10, 15),  # Optimal window
        datetime(2025, 1, 1, 11, 45),  # Lunch time - should avoid  
        datetime(2025, 1, 1, 14, 0),   # Optimal window
        datetime(2025, 1, 1, 15, 45),  # Near close - should avoid
    ]
    
    # Create test signals DataFrame
    test_signals = pd.DataFrame({
        'timestamp': test_times,
        'signal_strength': [0.8, 0.7, 0.9, 0.6, 0.8],
        'symbol': ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    })
    
    # Test time filtering
    time_filter = TimeBasedFilter()
    filtered_signals = time_filter.filter_signals_by_time(test_signals)
    
    print("Time-Based Filter Test Results")
    print("=" * 40)
    
    for i, row in filtered_signals.iterrows():
        ts = row['timestamp']
        strength = row['time_filter_strength']
        is_optimal = time_filter.is_optimal_trading_time(ts)
        should_avoid = time_filter.should_avoid_trading(ts)
        
        print(f"{ts.strftime('%H:%M')}: strength={strength:.1f}, optimal={is_optimal}, avoid={should_avoid}")
    
    # Get report
    report = time_filter.get_time_filter_report()
    print(f"\nFilter Report:")
    print(f"Signals processed: {report['total_signals_processed']}")
    print(f"Filter rate: {report['filter_rate']}")
    print(f"Optimal window rate: {report['optimal_window_rate']}")

if __name__ == "__main__":
    test_time_filter()
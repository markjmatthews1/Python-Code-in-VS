# Technical Analysis Collector for Catalyst Scanner
#
# Provides real-time technical indicators, support/resistance levels,
# and momentum signals for portfolio tickers using multiple data sources.
#
# Author: Investment Catalyst Team
# Date: September 29, 2025

import requests
import json
import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed

from utils.logger import get_logger, log_api_call, log_data_update, PerformanceTimer
from utils.error_handler import api_error_handler, handle_error, APIError


class TechnicalAnalysisCollector:
    """
    Technical Analysis collector for real-time indicators and signals
    """
    
    def __init__(self, auth_manager=None):
        """
        Initialize technical analysis collector
        
        Args:
            auth_manager: Authentication manager (optional, mainly for Schwab data)
        """
        self.logger = get_logger()
        self.auth_manager = auth_manager
        self.technical_data = {}
        self.last_update = None
        
        # Technical indicator settings
        self.indicator_settings = {
            'sma_periods': [20, 50, 200],  # Simple Moving Averages
            'ema_periods': [12, 26],       # Exponential Moving Averages
            'rsi_period': 14,              # RSI period
            'macd_fast': 12,               # MACD fast EMA
            'macd_slow': 26,               # MACD slow EMA
            'macd_signal': 9,              # MACD signal line
            'bollinger_period': 20,        # Bollinger Bands period
            'bollinger_std': 2,            # Bollinger Bands standard deviation
            'volume_sma': 20,              # Volume moving average
        }
        
        # Signal thresholds
        self.signal_thresholds = {
            'rsi_oversold': 30,
            'rsi_overbought': 70,
            'volume_surge_multiplier': 2.0,  # 2x average volume
            'breakout_threshold': 0.02,       # 2% breakout
            'momentum_threshold': 0.05        # 5% momentum
        }
        
        self.logger.info("Technical Analysis Collector initialized")
    
    @api_error_handler("Technical Analysis", reraise=False)
    def analyze_portfolio_technicals(self, tickers: List[str], days_back: int = 60) -> Dict:
        """
        Analyze technical indicators for entire portfolio
        
        Args:
            tickers: List of ticker symbols
            days_back: Days of historical data to analyze
            
        Returns:
            Dict: Technical analysis results for all tickers
        """
        try:
            self.logger.info(f"Analyzing technical indicators for {len(tickers)} tickers")
            
            results = {}
            failed_tickers = []
            
            # Use thread pool for concurrent analysis
            with ThreadPoolExecutor(max_workers=5) as executor:
                # Submit all ticker analysis tasks
                future_to_ticker = {
                    executor.submit(self._analyze_single_ticker, ticker, days_back): ticker 
                    for ticker in tickers
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_ticker):
                    ticker = future_to_ticker[future]
                    try:
                        ticker_analysis = future.result(timeout=30)
                        if ticker_analysis:
                            results[ticker] = ticker_analysis
                            self.logger.debug(f"Technical analysis completed for {ticker}")
                        else:
                            failed_tickers.append(ticker)
                    except Exception as e:
                        self.logger.warning(f"Technical analysis failed for {ticker}: {e}")
                        failed_tickers.append(ticker)
            
            # Store results
            self.technical_data = results
            self.last_update = datetime.now()
            
            success_count = len(results)
            fail_count = len(failed_tickers)
            
            log_data_update("technical_analysis", success_count, 
                           f"Technical analysis: {success_count} success, {fail_count} failed")
            
            self.logger.info(f"Technical analysis completed: {success_count}/{len(tickers)} tickers analyzed")
            
            if failed_tickers:
                self.logger.warning(f"Failed tickers: {failed_tickers}")
            
            return results
            
        except Exception as e:
            handle_error(e, "Portfolio technical analysis", "Failed to analyze portfolio technicals")
            return {}
    
    def _analyze_single_ticker(self, ticker: str, days_back: int) -> Optional[Dict]:
        """
        Analyze technical indicators for a single ticker
        
        Args:
            ticker: Ticker symbol
            days_back: Days of historical data
            
        Returns:
            Dict: Technical analysis results
        """
        try:
            with PerformanceTimer(f"Technical analysis for {ticker}"):
                # Fetch historical data
                end_date = datetime.now()
                start_date = end_date - timedelta(days=days_back)
                
                # Use yfinance for reliable data
                stock = yf.Ticker(ticker)
                hist_data = stock.history(start=start_date.strftime('%Y-%m-%d'), 
                                        end=end_date.strftime('%Y-%m-%d'))
                
                if hist_data.empty:
                    self.logger.warning(f"No historical data available for {ticker}")
                    return None
                
                log_api_call("yfinance", f"history/{ticker}", 200, 0.5)  # Approximate timing
                
                # Calculate all technical indicators
                analysis = {
                    'ticker': ticker,
                    'last_update': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'data_points': len(hist_data),
                    'price_data': self._extract_price_data(hist_data),
                    'moving_averages': self._calculate_moving_averages(hist_data),
                    'rsi': self._calculate_rsi(hist_data),
                    'macd': self._calculate_macd(hist_data),
                    'bollinger_bands': self._calculate_bollinger_bands(hist_data),
                    'volume_analysis': self._analyze_volume(hist_data),
                    'support_resistance': self._find_support_resistance(hist_data),
                    'signals': self._generate_signals(hist_data),
                    'momentum': self._calculate_momentum(hist_data),
                    'trend_analysis': self._analyze_trend(hist_data)
                }
                
                return analysis
                
        except Exception as e:
            self.logger.error(f"Technical analysis failed for {ticker}: {e}")
            return None
    
    def _extract_price_data(self, hist_data: pd.DataFrame) -> Dict:
        """Extract current price data and basic statistics"""
        try:
            current_price = float(hist_data['Close'].iloc[-1])
            prev_close = float(hist_data['Close'].iloc[-2]) if len(hist_data) > 1 else current_price
            
            high_52w = float(hist_data['High'].max())
            low_52w = float(hist_data['Low'].min())
            
            return {
                'current_price': current_price,
                'previous_close': prev_close,
                'daily_change': current_price - prev_close,
                'daily_change_pct': ((current_price - prev_close) / prev_close) * 100,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'price_vs_52w_high': ((current_price - high_52w) / high_52w) * 100,
                'price_vs_52w_low': ((current_price - low_52w) / low_52w) * 100,
                'avg_volume': float(hist_data['Volume'].mean()),
                'current_volume': float(hist_data['Volume'].iloc[-1])
            }
        except Exception as e:
            self.logger.error(f"Price data extraction failed: {e}")
            return {}
    
    def _calculate_moving_averages(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate Simple and Exponential Moving Averages"""
        try:
            prices = hist_data['Close']
            mas = {}
            
            # Simple Moving Averages
            for period in self.indicator_settings['sma_periods']:
                if len(prices) >= period:
                    sma = prices.rolling(window=period).mean().iloc[-1]
                    mas[f'sma_{period}'] = float(sma)
                    
                    # Price position relative to SMA
                    current_price = prices.iloc[-1]
                    mas[f'price_vs_sma_{period}'] = ((current_price - sma) / sma) * 100
            
            # Exponential Moving Averages
            for period in self.indicator_settings['ema_periods']:
                if len(prices) >= period:
                    ema = prices.ewm(span=period).mean().iloc[-1]
                    mas[f'ema_{period}'] = float(ema)
                    
                    # Price position relative to EMA
                    current_price = prices.iloc[-1]
                    mas[f'price_vs_ema_{period}'] = ((current_price - ema) / ema) * 100
            
            return mas
            
        except Exception as e:
            self.logger.error(f"Moving averages calculation failed: {e}")
            return {}
    
    def _calculate_rsi(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate Relative Strength Index"""
        try:
            prices = hist_data['Close']
            period = self.indicator_settings['rsi_period']
            
            if len(prices) < period + 1:
                return {'rsi': None, 'rsi_signal': 'insufficient_data'}
            
            # Calculate price changes
            delta = prices.diff()
            
            # Separate gains and losses
            gains = delta.where(delta > 0, 0)
            losses = -delta.where(delta < 0, 0)
            
            # Calculate average gains and losses
            avg_gains = gains.rolling(window=period).mean()
            avg_losses = losses.rolling(window=period).mean()
            
            # Calculate RSI
            rs = avg_gains / avg_losses
            rsi = 100 - (100 / (1 + rs))
            
            current_rsi = float(rsi.iloc[-1])
            
            # Generate RSI signal
            if current_rsi <= self.signal_thresholds['rsi_oversold']:
                rsi_signal = 'oversold'
            elif current_rsi >= self.signal_thresholds['rsi_overbought']:
                rsi_signal = 'overbought'
            else:
                rsi_signal = 'neutral'
            
            return {
                'rsi': current_rsi,
                'rsi_signal': rsi_signal,
                'rsi_history': rsi.tail(5).tolist()  # Last 5 values for trend
            }
            
        except Exception as e:
            self.logger.error(f"RSI calculation failed: {e}")
            return {'rsi': None, 'rsi_signal': 'error'}
    
    def _calculate_macd(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        try:
            prices = hist_data['Close']
            fast_period = self.indicator_settings['macd_fast']
            slow_period = self.indicator_settings['macd_slow']
            signal_period = self.indicator_settings['macd_signal']
            
            if len(prices) < slow_period + signal_period:
                return {'macd': None, 'macd_signal': 'insufficient_data'}
            
            # Calculate EMAs
            ema_fast = prices.ewm(span=fast_period).mean()
            ema_slow = prices.ewm(span=slow_period).mean()
            
            # Calculate MACD line
            macd_line = ema_fast - ema_slow
            
            # Calculate signal line
            signal_line = macd_line.ewm(span=signal_period).mean()
            
            # Calculate histogram
            histogram = macd_line - signal_line
            
            # Current values
            current_macd = float(macd_line.iloc[-1])
            current_signal = float(signal_line.iloc[-1])
            current_histogram = float(histogram.iloc[-1])
            
            # Generate MACD signal
            if current_macd > current_signal and histogram.iloc[-2] < 0:
                macd_signal = 'bullish_crossover'
            elif current_macd < current_signal and histogram.iloc[-2] > 0:
                macd_signal = 'bearish_crossover'
            elif current_macd > current_signal:
                macd_signal = 'bullish'
            else:
                macd_signal = 'bearish'
            
            return {
                'macd_line': current_macd,
                'signal_line': current_signal,
                'histogram': current_histogram,
                'macd_signal': macd_signal
            }
            
        except Exception as e:
            self.logger.error(f"MACD calculation failed: {e}")
            return {'macd': None, 'macd_signal': 'error'}
    
    def _calculate_bollinger_bands(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate Bollinger Bands"""
        try:
            prices = hist_data['Close']
            period = self.indicator_settings['bollinger_period']
            std_dev = self.indicator_settings['bollinger_std']
            
            if len(prices) < period:
                return {'bollinger_signal': 'insufficient_data'}
            
            # Calculate middle band (SMA)
            middle_band = prices.rolling(window=period).mean()
            
            # Calculate standard deviation
            std = prices.rolling(window=period).std()
            
            # Calculate upper and lower bands
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            # Current values
            current_price = float(prices.iloc[-1])
            current_upper = float(upper_band.iloc[-1])
            current_middle = float(middle_band.iloc[-1])
            current_lower = float(lower_band.iloc[-1])
            
            # Calculate Bollinger Band position
            bb_position = (current_price - current_lower) / (current_upper - current_lower)
            
            # Generate Bollinger Band signal
            if current_price > current_upper:
                bb_signal = 'overbought'
            elif current_price < current_lower:
                bb_signal = 'oversold'
            elif bb_position > 0.8:
                bb_signal = 'approaching_overbought'
            elif bb_position < 0.2:
                bb_signal = 'approaching_oversold'
            else:
                bb_signal = 'neutral'
            
            return {
                'upper_band': current_upper,
                'middle_band': current_middle,
                'lower_band': current_lower,
                'bb_position': bb_position,
                'bollinger_signal': bb_signal,
                'band_width': current_upper - current_lower
            }
            
        except Exception as e:
            self.logger.error(f"Bollinger Bands calculation failed: {e}")
            return {'bollinger_signal': 'error'}
    
    def _analyze_volume(self, hist_data: pd.DataFrame) -> Dict:
        """Analyze volume patterns"""
        try:
            volume = hist_data['Volume']
            period = self.indicator_settings['volume_sma']
            
            if len(volume) < period:
                return {'volume_signal': 'insufficient_data'}
            
            # Calculate average volume
            avg_volume = volume.rolling(window=period).mean()
            current_volume = float(volume.iloc[-1])
            current_avg = float(avg_volume.iloc[-1])
            
            # Volume surge detection
            volume_ratio = current_volume / current_avg
            
            if volume_ratio >= self.signal_thresholds['volume_surge_multiplier']:
                volume_signal = 'surge'
            elif volume_ratio <= 0.5:
                volume_signal = 'low'
            else:
                volume_signal = 'normal'
            
            return {
                'current_volume': current_volume,
                'avg_volume': current_avg,
                'volume_ratio': volume_ratio,
                'volume_signal': volume_signal
            }
            
        except Exception as e:
            self.logger.error(f"Volume analysis failed: {e}")
            return {'volume_signal': 'error'}
    
    def _find_support_resistance(self, hist_data: pd.DataFrame) -> Dict:
        """Find support and resistance levels"""
        try:
            highs = hist_data['High']
            lows = hist_data['Low']
            closes = hist_data['Close']
            
            # Simple support/resistance based on recent highs and lows
            recent_data = hist_data.tail(20)  # Last 20 days
            
            resistance = float(recent_data['High'].max())
            support = float(recent_data['Low'].min())
            current_price = float(closes.iloc[-1])
            
            # Calculate distances to support/resistance
            resistance_distance = ((resistance - current_price) / current_price) * 100
            support_distance = ((current_price - support) / current_price) * 100
            
            return {
                'resistance': resistance,
                'support': support,
                'resistance_distance_pct': resistance_distance,
                'support_distance_pct': support_distance
            }
            
        except Exception as e:
            self.logger.error(f"Support/resistance calculation failed: {e}")
            return {}
    
    def _generate_signals(self, hist_data: pd.DataFrame) -> List[Dict]:
        """Generate trading signals based on technical indicators"""
        try:
            signals = []
            
            # Get current data
            current_price = float(hist_data['Close'].iloc[-1])
            current_volume = float(hist_data['Volume'].iloc[-1])
            
            # Calculate some basic indicators for signal generation
            if len(hist_data) >= 20:
                sma_20 = hist_data['Close'].rolling(window=20).mean().iloc[-1]
                
                # Price above/below SMA signal
                if current_price > sma_20 * 1.02:  # 2% above SMA
                    signals.append({
                        'type': 'bullish',
                        'signal': 'price_above_sma',
                        'strength': 'moderate',
                        'description': 'Price trading 2%+ above 20-day SMA'
                    })
                elif current_price < sma_20 * 0.98:  # 2% below SMA
                    signals.append({
                        'type': 'bearish',
                        'signal': 'price_below_sma',
                        'strength': 'moderate',
                        'description': 'Price trading 2%+ below 20-day SMA'
                    })
            
            # Volume surge signal
            if len(hist_data) >= 20:
                avg_volume = hist_data['Volume'].rolling(window=20).mean().iloc[-1]
                if current_volume > avg_volume * 2:
                    signals.append({
                        'type': 'neutral',
                        'signal': 'volume_surge',
                        'strength': 'strong',
                        'description': f'Volume surge: {current_volume/avg_volume:.1f}x average'
                    })
            
            return signals
            
        except Exception as e:
            self.logger.error(f"Signal generation failed: {e}")
            return []
    
    def _calculate_momentum(self, hist_data: pd.DataFrame) -> Dict:
        """Calculate momentum indicators"""
        try:
            prices = hist_data['Close']
            
            if len(prices) < 10:
                return {'momentum_signal': 'insufficient_data'}
            
            # Calculate price momentum (rate of change)
            momentum_5d = ((prices.iloc[-1] - prices.iloc[-6]) / prices.iloc[-6]) * 100 if len(prices) >= 6 else 0
            momentum_10d = ((prices.iloc[-1] - prices.iloc[-11]) / prices.iloc[-11]) * 100 if len(prices) >= 11 else 0
            
            # Determine momentum signal
            if momentum_5d > 5:  # 5% gain in 5 days
                momentum_signal = 'strong_bullish'
            elif momentum_5d > 2:
                momentum_signal = 'moderate_bullish'
            elif momentum_5d < -5:
                momentum_signal = 'strong_bearish'
            elif momentum_5d < -2:
                momentum_signal = 'moderate_bearish'
            else:
                momentum_signal = 'neutral'
            
            return {
                'momentum_5d': momentum_5d,
                'momentum_10d': momentum_10d,
                'momentum_signal': momentum_signal
            }
            
        except Exception as e:
            self.logger.error(f"Momentum calculation failed: {e}")
            return {'momentum_signal': 'error'}
    
    def _analyze_trend(self, hist_data: pd.DataFrame) -> Dict:
        """Analyze overall trend direction"""
        try:
            prices = hist_data['Close']
            
            if len(prices) < 20:
                return {'trend': 'insufficient_data'}
            
            # Calculate trend using linear regression
            x = np.arange(len(prices))
            coefficients = np.polyfit(x, prices, 1)
            slope = coefficients[0]
            
            # Normalize slope by price
            trend_strength = (slope / prices.mean()) * 100
            
            if trend_strength > 0.1:
                trend = 'uptrend'
            elif trend_strength < -0.1:
                trend = 'downtrend'
            else:
                trend = 'sideways'
            
            return {
                'trend': trend,
                'trend_strength': trend_strength,
                'slope': slope
            }
            
        except Exception as e:
            self.logger.error(f"Trend analysis failed: {e}")
            return {'trend': 'error'}
    
    def get_top_signals(self, max_signals: int = 10) -> List[Dict]:
        """Get top technical signals across portfolio"""
        try:
            all_signals = []
            
            for ticker, analysis in self.technical_data.items():
                if 'signals' in analysis:
                    for signal in analysis['signals']:
                        signal_copy = signal.copy()
                        signal_copy['ticker'] = ticker
                        signal_copy['timestamp'] = analysis['last_update']
                        all_signals.append(signal_copy)
            
            # Sort by signal strength and type
            strength_priority = {'strong': 3, 'moderate': 2, 'weak': 1}
            all_signals.sort(key=lambda x: strength_priority.get(x.get('strength', 'weak'), 1), reverse=True)
            
            return all_signals[:max_signals]
            
        except Exception as e:
            self.logger.error(f"Error getting top signals: {e}")
            return []
    
    def format_for_display(self, max_items: int = 5) -> List[Dict]:
        """Format technical analysis data for GUI display"""
        try:
            display_data = []
            
            for ticker, analysis in list(self.technical_data.items())[:max_items]:
                try:
                    price_data = analysis.get('price_data', {})
                    rsi_data = analysis.get('rsi', {})
                    signals = analysis.get('signals', [])
                    momentum_data = analysis.get('momentum', {})
                    
                    # Get primary signal
                    primary_signal = signals[0] if signals else {'type': 'neutral', 'signal': 'no_signal'}
                    
                    display_item = {
                        'ticker': ticker,
                        'current_price': price_data.get('current_price', 0),
                        'daily_change_pct': price_data.get('daily_change_pct', 0),
                        'rsi': rsi_data.get('rsi'),
                        'rsi_signal': rsi_data.get('rsi_signal', 'unknown'),
                        'primary_signal': primary_signal.get('signal', 'no_signal'),
                        'signal_type': primary_signal.get('type', 'neutral'),
                        'momentum': momentum_data,
                        'last_update': analysis.get('last_update', '')
                    }
                    
                    display_data.append(display_item)
                    
                except Exception as e:
                    self.logger.warning(f"Error formatting display data for {ticker}: {e}")
                    continue
            
            return display_data
            
        except Exception as e:
            self.logger.error(f"Error formatting technical data for display: {e}")
            return []


# Convenience function for quick access
def analyze_portfolio_technicals(tickers: List[str], auth_manager=None) -> TechnicalAnalysisCollector:
    """
    Quick function to analyze portfolio technical indicators
    
    Args:
        tickers: List of ticker symbols
        auth_manager: Optional authentication manager
        
    Returns:
        TechnicalAnalysisCollector: Collector with technical analysis data
    """
    collector = TechnicalAnalysisCollector(auth_manager)
    collector.analyze_portfolio_technicals(tickers)
    return collector


if __name__ == "__main__":
    # Test the technical analysis collector
    print("Testing Technical Analysis Collector...")
    
    # Test tickers
    test_tickers = ['AAPL', 'SMCI', 'MARA']
    
    collector = analyze_portfolio_technicals(test_tickers)
    
    # Display results
    display_data = collector.format_for_display(3)
    print(f"Technical analysis: {len(display_data)} tickers analyzed")
    
    for item in display_data:
        print(f"  {item['ticker']}: ${item['current_price']:.2f} ({item['daily_change_pct']:+.2f}%) RSI: {item['rsi']:.1f if item['rsi'] else 'N/A'}")
    
    # Show top signals
    top_signals = collector.get_top_signals(5)
    print(f"\nTop signals: {len(top_signals)} found")
    for signal in top_signals:
        print(f"  {signal['ticker']}: {signal['signal']} ({signal['type']}) - {signal['description']}")
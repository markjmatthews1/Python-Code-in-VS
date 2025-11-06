"""
Real-Time Data Stream Collector for Catalyst Scanner
===================================================

Provides live market data streaming for portfolio tickers with:
- Real-time price updates
- Volume analysis and unusual activity detection  
- Market hours detection
- Pre/post market catalyst tracking
- Live catalyst impact scoring

Author: GitHub Copilot & Investment Catalyst Team
Date: October 1, 2025
Phase: 4 - Advanced Features
"""

import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor

from utils.logger import get_logger
from utils.error_handler import api_error_handler


@dataclass
class RealTimeQuote:
    """Real-time quote data structure"""
    symbol: str
    price: float
    change: float
    change_percent: float
    volume: int
    avg_volume: int
    volume_ratio: float
    market_cap: float
    timestamp: datetime
    market_state: str  # 'pre', 'regular', 'post', 'closed'


@dataclass
class VolumeAlert:
    """Volume surge alert data structure"""
    symbol: str
    current_volume: int
    avg_volume: int
    volume_ratio: float
    price_change: float
    timestamp: datetime
    alert_level: str  # 'normal', 'elevated', 'extreme'


class RealTimeDataStream:
    """
    Real-time market data streaming for catalyst monitoring
    """
    
    def __init__(self, portfolio_loader=None, catalyst_scorer=None):
        """
        Initialize real-time data stream
        
        Args:
            portfolio_loader: Portfolio loader instance for ticker list
            catalyst_scorer: Live catalyst scorer for impact analysis
        """
        self.logger = get_logger()
        self.portfolio_loader = portfolio_loader
        self.catalyst_scorer = catalyst_scorer
        
        # Streaming state
        self.is_streaming = False
        self.stream_thread = None
        self.tickers = []
        self.current_quotes = {}
        self.historical_data = {}
        
        # Event callbacks
        self.quote_callbacks = []
        self.volume_alert_callbacks = []
        self.catalyst_update_callbacks = []
        
        # Configuration
        self.config = {
            'update_interval': 10,  # seconds between updates
            'volume_surge_threshold': 2.0,  # 2x average volume
            'extreme_volume_threshold': 5.0,  # 5x average volume
            'price_change_threshold': 0.02,  # 2% price change
            'max_concurrent_requests': 10,
            'market_hours_buffer': 30,  # minutes before/after market hours
        }
        
        # Market hours (Eastern Time)
        self.market_hours = {
            'pre_market_start': '04:00',
            'market_open': '09:30', 
            'market_close': '16:00',
            'post_market_end': '20:00'
        }
        
        self.logger.info("Real-time data stream initialized")
    
    def add_quote_callback(self, callback: Callable):
        """Add callback for real-time quote updates"""
        self.quote_callbacks.append(callback)
    
    def add_volume_alert_callback(self, callback: Callable):
        """Add callback for volume surge alerts"""
        self.volume_alert_callbacks.append(callback)
    
    def add_catalyst_update_callback(self, callback: Callable):
        """Add callback for catalyst impact updates"""
        self.catalyst_update_callbacks.append(callback)
    
    def load_portfolio_tickers(self) -> List[str]:
        """Load ticker list from portfolio"""
        try:
            if self.portfolio_loader:
                portfolio_data = self.portfolio_loader.load_portfolio()
                self.tickers = list(portfolio_data.keys())
                self.logger.info(f"Loaded {len(self.tickers)} tickers for streaming: {', '.join(self.tickers[:5])}...")
                return self.tickers
            else:
                self.logger.warning("No portfolio loader available")
                return []
        except Exception as e:
            self.logger.error(f"Error loading portfolio tickers: {e}")
            return []
    
    def get_market_state(self) -> str:
        """Determine current market state (pre/regular/post/closed)"""
        try:
            now = datetime.now()
            current_time = now.strftime('%H:%M')
            
            # Check if it's a weekday
            if now.weekday() >= 5:  # Saturday=5, Sunday=6
                return 'closed'
            
            # Check time periods
            if current_time < self.market_hours['pre_market_start']:
                return 'closed'
            elif current_time < self.market_hours['market_open']:
                return 'pre'
            elif current_time < self.market_hours['market_close']:
                return 'regular'
            elif current_time < self.market_hours['post_market_end']:
                return 'post'
            else:
                return 'closed'
                
        except Exception as e:
            self.logger.error(f"Error determining market state: {e}")
            return 'unknown'
    
    @api_error_handler("Real-time data fetch", reraise=False)
    def fetch_real_time_quotes(self, tickers: List[str]) -> Dict[str, RealTimeQuote]:
        """
        Fetch real-time quotes for multiple tickers
        
        Args:
            tickers: List of ticker symbols
            
        Returns:
            Dict mapping ticker to RealTimeQuote
        """
        quotes = {}
        market_state = self.get_market_state()
        
        try:
            # Use ThreadPoolExecutor for concurrent requests
            with ThreadPoolExecutor(max_workers=self.config['max_concurrent_requests']) as executor:
                # Submit all ticker requests
                future_to_ticker = {
                    executor.submit(self._fetch_single_ticker_quote, ticker, market_state): ticker 
                    for ticker in tickers
                }
                
                # Collect results
                for future in future_to_ticker:
                    ticker = future_to_ticker[future]
                    try:
                        quote = future.result(timeout=10)
                        if quote:
                            quotes[ticker] = quote
                    except Exception as e:
                        self.logger.error(f"Error fetching quote for {ticker}: {e}")
            
            self.logger.debug(f"Fetched quotes for {len(quotes)}/{len(tickers)} tickers")
            return quotes
            
        except Exception as e:
            self.logger.error(f"Error fetching real-time quotes: {e}")
            return {}
    
    def _fetch_single_ticker_quote(self, ticker: str, market_state: str) -> Optional[RealTimeQuote]:
        """Fetch real-time quote for a single ticker"""
        try:
            # Get ticker object
            stock = yf.Ticker(ticker)
            
            # Get current info
            info = stock.info
            
            # Get recent historical data for volume comparison
            hist = stock.history(period='5d', interval='1d')
            
            if hist.empty or not info:
                return None
            
            # Calculate average volume (last 5 days)
            avg_volume = hist['Volume'].mean()
            
            # Get current price and volume
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            previous_close = info.get('previousClose', info.get('regularMarketPreviousClose', current_price))
            current_volume = info.get('volume', info.get('regularMarketVolume', 0))
            
            # Calculate changes
            price_change = current_price - previous_close
            change_percent = (price_change / previous_close * 100) if previous_close > 0 else 0
            volume_ratio = (current_volume / avg_volume) if avg_volume > 0 else 1.0
            
            # Create quote object
            quote = RealTimeQuote(
                symbol=ticker,
                price=current_price,
                change=price_change,
                change_percent=change_percent,
                volume=current_volume,
                avg_volume=int(avg_volume),
                volume_ratio=volume_ratio,
                market_cap=info.get('marketCap', 0),
                timestamp=datetime.now(),
                market_state=market_state
            )
            
            return quote
            
        except Exception as e:
            self.logger.error(f"Error fetching quote for {ticker}: {e}")
            return None
    
    def analyze_volume_alerts(self, quotes: Dict[str, RealTimeQuote]) -> List[VolumeAlert]:
        """Analyze quotes for volume surge alerts"""
        alerts = []
        
        try:
            for ticker, quote in quotes.items():
                # Skip if no valid volume data
                if quote.volume <= 0 or quote.avg_volume <= 0:
                    continue
                
                # Determine alert level
                alert_level = 'normal'
                if quote.volume_ratio >= self.config['extreme_volume_threshold']:
                    alert_level = 'extreme'
                elif quote.volume_ratio >= self.config['volume_surge_threshold']:
                    alert_level = 'elevated'
                
                # Create alert if elevated or extreme
                if alert_level != 'normal':
                    alert = VolumeAlert(
                        symbol=ticker,
                        current_volume=quote.volume,
                        avg_volume=quote.avg_volume,
                        volume_ratio=quote.volume_ratio,
                        price_change=quote.change_percent,
                        timestamp=quote.timestamp,
                        alert_level=alert_level
                    )
                    alerts.append(alert)
            
            if alerts:
                self.logger.info(f"Generated {len(alerts)} volume alerts")
            
            return alerts
            
        except Exception as e:
            self.logger.error(f"Error analyzing volume alerts: {e}")
            return []
    
    def process_catalyst_updates(self, quotes: Dict[str, RealTimeQuote]):
        """Process quotes for catalyst impact updates"""
        try:
            if not self.catalyst_scorer:
                return
            
            # Find significant price/volume changes
            significant_changes = []
            
            for ticker, quote in quotes.items():
                # Check for significant price movement
                if abs(quote.change_percent) >= (self.config['price_change_threshold'] * 100):
                    significant_changes.append({
                        'ticker': ticker,
                        'price_change': quote.change_percent,
                        'volume_ratio': quote.volume_ratio,
                        'market_state': quote.market_state
                    })
            
            # Update catalyst scores for significant movers
            if significant_changes:
                self.logger.info(f"Processing catalyst updates for {len(significant_changes)} significant movers")
                
                # Trigger catalyst scoring updates
                for callback in self.catalyst_update_callbacks:
                    try:
                        callback(significant_changes)
                    except Exception as e:
                        self.logger.error(f"Error in catalyst update callback: {e}")
                        
        except Exception as e:
            self.logger.error(f"Error processing catalyst updates: {e}")
    
    def _stream_loop(self):
        """Main streaming loop"""
        self.logger.info("Starting real-time data stream")
        
        try:
            while self.is_streaming:
                # Fetch real-time quotes
                quotes = self.fetch_real_time_quotes(self.tickers)
                
                if quotes:
                    # Update current quotes
                    self.current_quotes.update(quotes)
                    
                    # Trigger quote callbacks
                    for callback in self.quote_callbacks:
                        try:
                            callback(quotes)
                        except Exception as e:
                            self.logger.error(f"Error in quote callback: {e}")
                    
                    # Analyze volume alerts
                    volume_alerts = self.analyze_volume_alerts(quotes)
                    if volume_alerts:
                        for callback in self.volume_alert_callbacks:
                            try:
                                callback(volume_alerts)
                            except Exception as e:
                                self.logger.error(f"Error in volume alert callback: {e}")
                    
                    # Process catalyst updates
                    self.process_catalyst_updates(quotes)
                
                # Wait for next update
                time.sleep(self.config['update_interval'])
                
        except Exception as e:
            self.logger.error(f"Error in streaming loop: {e}")
        finally:
            self.logger.info("Real-time data stream stopped")
    
    def start_streaming(self, tickers: List[str] = None):
        """Start real-time data streaming"""
        try:
            if self.is_streaming:
                self.logger.warning("Streaming already active")
                return
            
            # Load tickers if not provided
            if tickers:
                self.tickers = tickers
            else:
                self.tickers = self.load_portfolio_tickers()
            
            if not self.tickers:
                self.logger.error("No tickers available for streaming")
                return
            
            # Start streaming
            self.is_streaming = True
            self.stream_thread = threading.Thread(target=self._stream_loop, daemon=True)
            self.stream_thread.start()
            
            self.logger.info(f"Started real-time streaming for {len(self.tickers)} tickers")
            
        except Exception as e:
            self.logger.error(f"Error starting stream: {e}")
            self.is_streaming = False
    
    def stop_streaming(self):
        """Stop real-time data streaming"""
        try:
            if not self.is_streaming:
                return
            
            self.is_streaming = False
            
            if self.stream_thread and self.stream_thread.is_alive():
                self.stream_thread.join(timeout=5)
            
            self.logger.info("Real-time data streaming stopped")
            
        except Exception as e:
            self.logger.error(f"Error stopping stream: {e}")
    
    def get_current_quotes(self) -> Dict[str, RealTimeQuote]:
        """Get current real-time quotes"""
        return self.current_quotes.copy()
    
    def get_streaming_status(self) -> Dict:
        """Get streaming status information"""
        return {
            'is_streaming': self.is_streaming,
            'ticker_count': len(self.tickers),
            'quote_count': len(self.current_quotes),
            'market_state': self.get_market_state(),
            'last_update': max([q.timestamp for q in self.current_quotes.values()]) if self.current_quotes else None
        }
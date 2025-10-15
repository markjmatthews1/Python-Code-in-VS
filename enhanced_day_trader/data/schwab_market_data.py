#!/usr/bin/env python3
"""
Schwab Market Data Integration for Enhanced Day Trader
=====================================================

Real-time market data using existing Schwab API authentication system.
Replaces yfinance with Schwab streaming/1-minute data.

Uses existing tokens.json and Schwab_auth.py infrastructure.
"""

import sys
import os
import json
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import pytz
import time
import logging
from typing import Dict, List, Optional

# Add main directory to path for accessing existing auth
main_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, main_dir)

# Change working directory to main directory for token file access
original_cwd = os.getcwd()
os.chdir(main_dir)

# Import existing Schwab authentication
from Schwab_auth import get_valid_access_token, fetch_quote

logger = logging.getLogger(__name__)

class SchwabMarketDataProvider:
    """
    Real-time market data provider using existing Schwab API infrastructure
    """
    
    def __init__(self):
        self.base_url = "https://api.schwabapi.com"
        self.marketdata_url = f"{self.base_url}/marketdata/v1"
        self.cache = {}
        self.cache_timeout = 60  # 1 minute cache
        
        logger.info("🔗 Schwab Market Data Provider initialized")
        
    def get_headers(self):
        """Get authorization headers using existing token system"""
        try:
            access_token = get_valid_access_token()
            return {
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json"
            }
        except Exception as e:
            logger.error(f"Failed to get access token: {e}")
            raise
    
    def get_quote(self, symbol: str) -> Dict:
        """Get real-time quote using existing fetch_quote function"""
        try:
            quote_data = fetch_quote(symbol)
            if quote_data and symbol in quote_data:
                return quote_data[symbol]
            return {}
        except Exception as e:
            logger.error(f"Error getting quote for {symbol}: {e}")
            return {}
    
    def get_multiple_quotes(self, symbols: List[str]) -> Dict:
        """Get multiple quotes efficiently"""
        try:
            # Use existing auth system
            access_token = get_valid_access_token()
            headers = self.get_headers()
            
            # Join symbols for batch request
            symbol_str = ",".join(symbols)
            url = f"{self.marketdata_url}/quotes?symbols={symbol_str}"
            
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Batch quotes failed: {response.status_code} - {response.text}")
                return {}
                
        except Exception as e:
            logger.error(f"Error getting batch quotes: {e}")
            return {}
    
    def get_historical_data(self, symbol: str, period: str = '5d', interval: str = '1m') -> pd.DataFrame:
        """
        Get historical data for technical analysis
        
        Args:
            symbol: Ticker symbol
            period: Time period ('1d', '5d', '1mo', etc.)
            interval: Data interval ('1m', '5m', '15m', '1h', '1d')
        """
        try:
            # Convert period to days
            period_days = self._parse_period(period)
            
            # Convert interval to Schwab format
            freq_type, frequency = self._parse_interval(interval)
            
            # Calculate date range
            eastern = pytz.timezone("US/Eastern")
            end_time = datetime.now(eastern)
            start_time = end_time - timedelta(days=period_days)
            
            # Convert to milliseconds (Schwab API requirement)
            start_ms = int(start_time.timestamp() * 1000)
            end_ms = int(end_time.timestamp() * 1000)
            
            # Make API request
            params = {
                "symbol": symbol,
                "periodType": "day",
                "frequencyType": freq_type,
                "frequency": frequency,
                "startDate": start_ms,
                "endDate": end_ms,
                "needExtendedHoursData": "false"  # Regular hours only for cleaner signals
            }
            
            headers = self.get_headers()
            url = f"{self.marketdata_url}/pricehistory"
            
            response = requests.get(url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return self._format_historical_data(data, symbol)
            else:
                logger.error(f"Historical data failed for {symbol}: {response.status_code}")
                return pd.DataFrame()
                
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {e}")
            return pd.DataFrame()
    
    def _parse_period(self, period: str) -> int:
        """Convert period string to days"""
        period = period.lower()
        if period.endswith('d'):
            return int(period[:-1])
        elif period.endswith('mo'):
            return int(period[:-2]) * 30
        elif period.endswith('y'):
            return int(period[:-1]) * 365
        else:
            return 5  # Default 5 days
    
    def _parse_interval(self, interval: str) -> tuple:
        """Convert interval to Schwab frequency format"""
        interval = interval.lower()
        if interval.endswith('m'):
            minutes = int(interval[:-1])
            return "minute", minutes
        elif interval.endswith('h'):
            hours = int(interval[:-1])
            return "minute", hours * 60
        elif interval.endswith('d'):
            return "daily", 1
        else:
            return "minute", 1  # Default 1 minute
    
    def _format_historical_data(self, data: Dict, symbol: str) -> pd.DataFrame:
        """Format Schwab API response to pandas DataFrame"""
        try:
            if 'candles' not in data:
                logger.warning(f"No candles data for {symbol}")
                return pd.DataFrame()
            
            candles = data['candles']
            if not candles:
                logger.warning(f"Empty candles data for {symbol}")
                return pd.DataFrame()
            
            # Convert to DataFrame
            df = pd.DataFrame(candles)
            
            # Convert datetime from milliseconds
            df['datetime'] = pd.to_datetime(df['datetime'], unit='ms')
            df.set_index('datetime', inplace=True)
            
            # Rename columns to standard format
            df.rename(columns={
                'open': 'Open',
                'high': 'High', 
                'low': 'Low',
                'close': 'Close',
                'volume': 'Volume'
            }, inplace=True)
            
            # Ensure we have required columns
            required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
            for col in required_cols:
                if col not in df.columns:
                    logger.error(f"Missing required column {col} for {symbol}")
                    return pd.DataFrame()
            
            logger.info(f"✅ Got {len(df)} data points for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error formatting data for {symbol}: {e}")
            return pd.DataFrame()
    
    def get_market_data_for_signals(self, symbol: str, period='5d', interval='1m') -> pd.DataFrame:
        """
        Get market data formatted for signal generation
        Compatible with existing LiveTradeSignalGenerator interface
        """
        try:
            # Get historical data
            data = self.get_historical_data(symbol, period, interval)
            
            if data.empty:
                logger.warning(f"No historical data for {symbol}")
                return pd.DataFrame()
            
            # Calculate technical indicators (same as yfinance version)
            data['RSI'] = self._calculate_rsi(data['Close'], 14)
            data['MACD'], data['MACD_signal'] = self._calculate_macd(data['Close'])
            data['Volume_SMA'] = data['Volume'].rolling(window=20).mean()
            data['ATR'] = self._calculate_atr(data)
            
            return data
            
        except Exception as e:
            logger.error(f"Error getting market data for signals {symbol}: {e}")
            return pd.DataFrame()
    
    def _calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI using simple math"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN with neutral 50
    
    def _calculate_macd(self, prices: pd.Series) -> tuple:
        """Calculate MACD using exponential moving averages"""
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9).mean()
        return macd.fillna(0), macd_signal.fillna(0)
    
    def _calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=window).mean()
        return atr.fillna(data['Close'] * 0.02)  # Default to 2% of price

    def test_connection(self) -> bool:
        """Test connection to Schwab API"""
        try:
            quote = self.get_quote('SPY')
            return bool(quote)
        except:
            return False

# Global instance for easy import
schwab_data = SchwabMarketDataProvider()

if __name__ == "__main__":
    # Test the connection
    provider = SchwabMarketDataProvider()
    
    print("🔍 Testing Schwab Market Data Provider...")
    
    # Test connection
    if provider.test_connection():
        print("✅ Connection successful")
    else:
        print("❌ Connection failed")
        exit(1)
    
    # Test quote
    quote = provider.get_quote('XLK')
    if quote:
        print(f"✅ XLK Quote: ${quote.get('lastPrice', 'N/A')}")
    else:
        print("❌ Quote test failed")
    
    # Test historical data
    data = provider.get_market_data_for_signals('XLK', period='2d', interval='5m')
    if not data.empty:
        print(f"✅ Historical data: {len(data)} candles")
        print(f"   Latest RSI: {data['RSI'].iloc[-1]:.1f}")
        print(f"   Latest MACD: {data['MACD'].iloc[-1]:.4f}")
    else:
        print("❌ Historical data test failed")
    
    print("🎯 Schwab Market Data Provider ready!")
#!/usr/bin/env python3
"""
Live Trade Signal Generator
===========================

Generates real-time trade setups with entry, exit, and stop-loss levels.
Displays actual trading opportunities as they develop.
"""

import pandas as pd
import numpy as np
import asyncio
from datetime import datetime, timedelta
import logging
import json
from typing import Dict, List, Optional

# Import our Schwab market data provider
from data.schwab_market_data import schwab_data

# Import paper trading engine
from core.paper_trader import paper_trader, Trade

# Import enhanced risk manager
from core.risk_manager import enhanced_risk_manager

logger = logging.getLogger(__name__)

class LiveTradeSignalGenerator:
    """
    Generates real-time trade signals with specific entry/exit levels
    """
    
    def __init__(self, watchlist=None):
        # Sector ETF watchlist for sector rotation trading
        self.watchlist = watchlist or [
            # Core Technology Sectors
            'XLK',   # Technology Select Sector SPDR
            'FTEC',  # Fidelity MSCI Information Technology ETF
            'VGT',   # Vanguard Information Technology ETF
            
            # Financial Services
            'XLF',   # Financial Select Sector SPDR
            'KBE',   # SPDR S&P Bank ETF
            'KRE',   # SPDR S&P Regional Banking ETF
            
            # Healthcare & Biotech
            'XLV',   # Health Care Select Sector SPDR
            'IBB',   # iShares Biotechnology ETF
            'XBI',   # SPDR S&P Biotech ETF
            
            # Energy & Oil
            'XLE',   # Energy Select Sector SPDR
            'XOP',   # SPDR S&P Oil & Gas Exploration & Production ETF
            'OIH',   # VanEck Oil Services ETF
            
            # Consumer Sectors
            'XLY',   # Consumer Discretionary Select Sector SPDR
            'XLP',   # Consumer Staples Select Sector SPDR
            'XRT',   # SPDR S&P Retail ETF
            
            # Industrial & Materials
            'XLI',   # Industrial Select Sector SPDR
            'XLB',   # Materials Select Sector SPDR
            'XME',   # SPDR S&P Metals & Mining ETF
            
            # Real Estate & Utilities
            'XLRE',  # Real Estate Select Sector SPDR
            'VNQ',   # Vanguard Real Estate ETF
            'XLU',   # Utilities Select Sector SPDR
            
            # Communications
            'XLC',   # Communication Services Select Sector SPDR
            'IYZ'    # iShares U.S. Telecommunications ETF
        ]
        
        self.active_signals = []
        self.signal_history = []
        
        # Enhanced signal parameters - Made more sensitive for demo
        self.rsi_oversold = 45  # Was 30
        self.rsi_overbought = 55  # Was 70  
        self.volume_threshold = 1.2  # 120% of average volume (was 150%)
        self.min_signal_strength = 0.50  # Require 50% confidence minimum
        
        # Risk management parameters  
        self.target_pct = 0.008  # 0.8% target
        self.stop_pct = 0.004    # 0.4% stop (2:1 ratio)
        
    def get_market_data(self, symbol: str, period='5d', interval='1m') -> pd.DataFrame:
        """Get real-time market data using Schwab API"""
        try:
            # Use our Schwab market data provider
            data = schwab_data.get_market_data_for_signals(symbol, period, interval)
            
            if data.empty:
                logger.warning(f"No data retrieved for {symbol}")
                return pd.DataFrame()
                
            logger.info(f"✅ Got {len(data)} data points for {symbol} from Schwab API")
            return data
            
        except Exception as e:
            logger.error(f"Error getting Schwab data for {symbol}: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, prices: pd.Series, window: int = 14) -> pd.Series:
        """Calculate RSI using simple math"""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi.fillna(50)  # Fill NaN with neutral 50
    
    def calculate_macd(self, prices: pd.Series) -> tuple:
        """Calculate MACD using exponential moving averages"""
        ema12 = prices.ewm(span=12).mean()
        ema26 = prices.ewm(span=26).mean()
        macd = ema12 - ema26
        macd_signal = macd.ewm(span=9).mean()
        return macd.fillna(0), macd_signal.fillna(0)
    
    def calculate_atr(self, data: pd.DataFrame, window: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = np.abs(data['High'] - data['Close'].shift())
        low_close = np.abs(data['Low'] - data['Close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr = true_range.rolling(window=window).mean()
        return atr.fillna(data['Close'] * 0.02)  # Default to 2% of price
    
    def calculate_signal_strength(self, data: pd.DataFrame) -> float:
        """Calculate signal strength based on multiple factors"""
        if data.empty or len(data) < 20:
            return 0.0
            
        latest = data.iloc[-1]
        prev = data.iloc[-2]
        
        strength = 0.0
        debug_info = []
        
        # RSI component (25% weight)
        rsi_score = 0
        if latest['RSI'] < self.rsi_oversold:  # Oversold = bullish
            rsi_score = 0.25
            debug_info.append("RSI oversold: +0.25")
        elif latest['RSI'] > self.rsi_overbought:  # Overbought = bearish  
            rsi_score = 0.25
            debug_info.append("RSI overbought: +0.25")
        strength += rsi_score
            
        # MACD component (25% weight)
        macd_score = 0
        if latest['MACD'] > latest['MACD_signal'] and prev['MACD'] <= prev['MACD_signal']:
            macd_score = 0.25
            debug_info.append("MACD bullish cross: +0.25")
        elif latest['MACD'] < latest['MACD_signal'] and prev['MACD'] >= prev['MACD_signal']:
            macd_score = 0.25
            debug_info.append("MACD bearish cross: +0.25")
        strength += macd_score
            
        # Volume component (25% weight) - Fixed division by zero
        volume_score = 0
        volume_sma = latest['Volume_SMA']
        if volume_sma > 0:
            volume_ratio = latest['Volume'] / volume_sma
            if volume_ratio > self.volume_threshold:
                volume_score = 0.25
                debug_info.append(f"High volume ({volume_ratio:.2f}x): +0.25")
        else:
            # If no volume SMA data, give partial credit
            volume_score = 0.10
            debug_info.append("No volume data: +0.10")
        strength += volume_score
            
        # Price action component (25% weight)
        price_score = 0
        if len(data) >= 10:
            price_momentum = (latest['Close'] - data['Close'].iloc[-10]) / data['Close'].iloc[-10]
            if abs(price_momentum) > 0.02:  # 2% price movement
                price_score = 0.25
                debug_info.append(f"Price momentum ({price_momentum:.3f}): +0.25")
        strength += price_score
        
        # For demo purposes, let's add some base strength
        if strength == 0:
            strength = 0.15  # Minimum demo strength
            
        return min(strength, 1.0)
    
    def generate_trade_setup(self, symbol: str, data: pd.DataFrame) -> Optional[Dict]:
        """Generate complete trade setup with entry, exit, stop levels"""
        if data.empty:
            return None
            
        signal_strength = self.calculate_signal_strength(data)
        
        if signal_strength < self.min_signal_strength:
            return None
            
        latest = data.iloc[-1]
        current_price = latest['Close']
        atr = latest['ATR']
        
        # Determine direction - Made more flexible for demo
        rsi = latest['RSI']
        macd = latest['MACD']
        macd_signal = latest['MACD_signal']
        
        # Generate signals for demonstration
        if rsi < self.rsi_overbought and macd > macd_signal:
            direction = "BUY"
            entry_price = current_price
            stop_loss = entry_price * (1 - self.stop_pct)
            take_profit = entry_price * (1 + self.target_pct)
            
        elif rsi > self.rsi_oversold and macd < macd_signal:
            direction = "SELL"  
            entry_price = current_price
            stop_loss = entry_price * (1 + self.stop_pct)
            take_profit = entry_price * (1 - self.target_pct)
            
        else:
            # If no clear signal, create a neutral BUY signal for demo
            if signal_strength > 0.25:  # Very low threshold for demo
                direction = "BUY"
                entry_price = current_price
                stop_loss = entry_price * (1 - self.stop_pct)
                take_profit = entry_price * (1 + self.target_pct)
            else:
                return None
        
        # Calculate position size using EnhancedRiskManager
        from core.risk_manager import EnhancedRiskManager
        risk_manager = EnhancedRiskManager(10000)  # $10K account
        
        # Get proper position sizing with risk management
        position_calc = risk_manager.calculate_position_size(entry_price)
        position_size = position_calc['shares']
        risk_amount = position_calc['dollar_risk']
        
        if position_size == 0 or not position_calc['valid']:
            return None
            
        setup = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'direction': direction,
            'signal_strength': round(signal_strength, 3),
            'entry_price': round(entry_price, 2),
            'stop_loss': round(position_calc['stop_loss_price'], 2),
            'take_profit': round(position_calc['target_price'], 2),
            'position_size': position_size,
            'position_value': round(position_calc['position_value'], 2),
            'risk_amount': round(risk_amount, 2),
            'potential_profit': round((position_calc['target_price'] - entry_price) * position_size, 2),
            'potential_loss': round((entry_price - position_calc['stop_loss_price']) * position_size, 2),
            'risk_reward_ratio': position_calc['risk_reward_ratio'],
            'rsi': round(rsi, 1),
            'macd': round(macd, 4),
            'volume_ratio': round(latest['Volume'] / latest['Volume_SMA'], 2),
            'atr_pct': round(atr / current_price * 100, 2)
        }
        
        return setup
    
    async def scan_for_signals(self) -> List[Dict]:
        """Scan watchlist for trade setups"""
        signals = []
        
        for symbol in self.watchlist:
            try:
                logger.info(f"Scanning {symbol} for signals...")
                data = self.get_market_data(symbol)
                
                if not data.empty:
                    setup = self.generate_trade_setup(symbol, data)
                    if setup:
                        signals.append(setup)
                        logger.info(f"Signal found for {symbol}: {setup['direction']} at ${setup['entry_price']}")
                        
                        # Automatically open paper trade for good signals
                        if setup['signal_strength'] >= self.min_signal_strength:
                            try:
                                trade_signal = {
                                    'symbol': setup['symbol'],
                                    'direction': 'BUY' if setup['direction'] == 'LONG' else 'SELL',
                                    'entry_price': setup['entry_price'],
                                    'stop_loss': setup['stop_loss'],
                                    'take_profit': setup['take_profit'],
                                    'signal_strength': setup['signal_strength']
                                }
                                
                                trade_id = paper_trader.open_trade(trade_signal)
                                logger.info(f"🟢 Opened paper trade {trade_id} for {setup['symbol']}")
                                
                            except Exception as e:
                                logger.error(f"Error opening paper trade for {symbol}: {e}")
                        
            except Exception as e:
                logger.error(f"Error scanning {symbol}: {e}")
                continue
                
        self.active_signals = signals
        
        # Monitor existing paper trades for stop loss/take profit
        try:
            paper_trader.check_stop_loss_take_profit()
        except Exception as e:
            logger.error(f"Error checking stop loss/take profit: {e}")
            
        return signals
    
    def get_active_signals(self) -> List[Dict]:
        """Get current active trade signals"""
        return self.active_signals
    
    def format_signal_for_display(self, setup: Dict) -> str:
        """Format trade setup for console display"""
        return f"""
🎯 TRADE SETUP: {setup['symbol']} 
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Direction: {setup['direction']}
Entry: ${setup['entry_price']}
Stop Loss: ${setup['stop_loss']}
Take Profit: ${setup['take_profit']}
Position Size: {setup['position_size']} shares (${setup.get('position_value', 0):,.2f})
Risk/Reward: {setup['risk_reward_ratio']}:1
Signal Strength: {setup['signal_strength']}/1.0
Potential Profit: ${setup['potential_profit']}
Potential Loss: ${setup['potential_loss']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Time: {setup['timestamp'][:19]}
"""

# Create global instance
trade_signal_generator = LiveTradeSignalGenerator()

if __name__ == "__main__":
    import asyncio
    
    async def test_signals():
        generator = LiveTradeSignalGenerator()
        signals = await generator.scan_for_signals()
        
        if signals:
            for setup in signals:
                print(generator.format_signal_for_display(setup))
        else:
            print("No trade signals found at this time.")
            
    asyncio.run(test_signals())
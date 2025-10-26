#!/usr/bin/env python3
"""
Live Trade Signal Generator
===========================

Generates real-time trade setups with entry, exit, and stop-loss levels.
Displays actual trading opportunities as they develop.

Market Hours Awareness:
- Only opens new trades during regular market hours (9:30 AM - 3:55 PM ET)
- Closes all positions at 3:55 PM ET (before market close)
- No trading on weekends or holidays
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

# Import market hours checker
from utils.market_hours import should_open_new_trades, should_close_all_positions, get_market_status

logger = logging.getLogger(__name__)

class LiveTradeSignalGenerator:
    """
    Generates real-time trade signals with specific entry/exit levels
    """
    
    def __init__(self, watchlist=None):
        # Sector ETF watchlist for sector rotation trading
        # FIX #2: REMOVED LOSING TICKERS (0% win rate): XLK, FTEC, XLF, XLC
        # Keeping only profitable or neutral tickers based on analysis
        self.watchlist = watchlist or [
            # Technology - REMOVED XLK (0% win rate), REMOVED FTEC (0% win rate)
            'VGT',   # Vanguard Information Technology ETF
            
            # Financial Services - REMOVED XLF (0% win rate)
            'KBE',   # SPDR S&P Bank ETF
            'KRE',   # SPDR S&P Regional Banking ETF
            
            # Healthcare & Biotech - KEEP (good performance)
            'XLV',   # Health Care Select Sector SPDR (40% win rate, needs work)
            'IBB',   # iShares Biotechnology ETF (100% win rate! ✅)
            'XBI',   # SPDR S&P Biotech ETF (100% win rate! ✅)
            
            # Energy & Oil - KEEP (OIH is excellent!)
            'XLE',   # Energy Select Sector SPDR
            'XOP',   # SPDR S&P Oil & Gas Exploration & Production ETF
            'OIH',   # VanEck Oil Services ETF (75% win rate! ✅)
            
            # Consumer Sectors
            'XLY',   # Consumer Discretionary Select Sector SPDR
            'XLP',   # Consumer Staples Select Sector SPDR
            'XRT',   # SPDR S&P Retail ETF (100% win rate! ✅)
            
            # Industrial & Materials
            'XLI',   # Industrial Select Sector SPDR
            'XLB',   # Materials Select Sector SPDR
            'XME',   # SPDR S&P Metals & Mining ETF
            
            # Real Estate & Utilities
            'XLRE',  # Real Estate Select Sector SPDR
            'VNQ',   # Vanguard Real Estate ETF
            'XLU',   # Utilities Select Sector SPDR
            
            # Communications - REMOVED XLC (0% win rate)
            'IYZ'    # iShares U.S. Telecommunications ETF (100% win rate! ✅)
        ]
        
        self.active_signals = []
        self.signal_history = []
        
        # FIX #3: INCREASED SIGNAL THRESHOLD - Require higher quality signals
        # Enhanced signal parameters
        self.rsi_oversold = 45  # Was 30
        self.rsi_overbought = 55  # Was 70  
        self.volume_threshold = 1.5  # FIX #3b: Increased from 1.2 to 1.5 (150% of average)
        self.min_signal_strength = 0.65  # FIX #3: Increased from 0.50 - only high-confidence signals
        
        # Risk management parameters  
        self.target_pct = 0.008  # 0.8% target
        self.stop_pct = 0.004    # 0.4% stop (2:1 ratio) - Will be replaced by ATR-based stops
        
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
        
        # FIX #4: ADD TREND FILTER - Calculate 20-period SMA
        if 'SMA_20' not in data.columns:
            data['SMA_20'] = data['Close'].rolling(window=20).mean()
            
        signal_strength = self.calculate_signal_strength(data)
        
        if signal_strength < self.min_signal_strength:
            return None
            
        latest = data.iloc[-1]
        current_price = latest['Close']
        atr = latest['ATR']
        
        # FIX #4: TREND FILTER - Only LONG when price is above 20-period SMA
        sma_20 = latest['SMA_20']
        if pd.notna(sma_20) and current_price < sma_20:
            # Price below trend - skip this trade (avoid counter-trend)
            logger.debug(f"Skipping {symbol}: Price ${current_price:.2f} below SMA20 ${sma_20:.2f}")
            return None
        
        # FIX #5: TIME FILTER - Only trade morning hours (9:30 AM - 12:00 PM ET)
        # Afternoon trading has only 16.7% win rate vs 47.4% in morning
        from datetime import datetime
        current_time = datetime.now()
        current_hour = current_time.hour
        current_minute = current_time.minute
        
        # Skip if before 9:30 AM or after 12:00 PM
        if current_hour < 9 or (current_hour == 9 and current_minute < 30):
            logger.debug(f"Skipping {symbol}: Before market open (9:30 AM)")
            return None
        if current_hour >= 12:
            logger.debug(f"Skipping {symbol}: After 12:00 PM (afternoon trades have 16.7% win rate)")
            return None
        
        # Determine direction - Made more flexible for demo
        rsi = latest['RSI']
        macd = latest['MACD']
        macd_signal = latest['MACD_signal']
        
        # FIX #6: ATR-BASED STOP LOSSES - Use 2x ATR for stops (wider, more forgiving)
        # This prevents stops being hit on normal market noise
        atr_pct = (atr / current_price)  # ATR as percentage of price
        stop_distance_pct = max(atr_pct * 2.0, 0.006)  # At least 0.6%, or 2x ATR (whichever is larger)
        target_distance_pct = stop_distance_pct * 2.0  # Maintain 2:1 risk/reward
        
        # FIX #1: DISABLE SHORT TRADES - They have 25% win rate vs 54.5% for LONG
        # Only generate LONG (BUY) signals
        if rsi < self.rsi_overbought and macd > macd_signal:
            direction = "BUY"
            entry_price = current_price
            stop_loss = entry_price * (1 - stop_distance_pct)
            take_profit = entry_price * (1 + target_distance_pct)
            
        # DISABLED: SHORT signals removed due to poor performance
        # elif rsi > self.rsi_oversold and macd < macd_signal:
        #     direction = "SELL"  
        #     entry_price = current_price
        #     stop_loss = entry_price * (1 + self.stop_pct)
        #     take_profit = entry_price * (1 - self.target_pct)
            
        else:
            # If no clear BUY signal, create one for signals with decent strength
            if signal_strength > 0.25:  # Very low threshold for demo
                direction = "BUY"
                entry_price = current_price
                stop_loss = entry_price * (1 - stop_distance_pct)
                take_profit = entry_price * (1 + target_distance_pct)
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
        
        # FIX: Determine actual trade direction (paper_trader converts BUY->LONG, SELL->SHORT)
        # The paper_trader uses NORMAL logic: BUY->LONG, SELL->SHORT
        # Check if this is actually going to be a SHORT trade
        will_be_short_trade = (direction == "SELL")  # SELL signals become SHORT trades
        
        if will_be_short_trade:
            # For SHORT trades: Stop should be ABOVE entry, Take Profit BELOW entry
            actual_stop_loss = entry_price * (1 + risk_manager.default_stop_pct)
            actual_take_profit = entry_price * (1 - risk_manager.default_target_pct)
            potential_profit = (entry_price - actual_take_profit) * position_size
            potential_loss = (actual_stop_loss - entry_price) * position_size
        else:
            # For LONG trades (SELL signals): Use risk manager values as-is
            actual_stop_loss = position_calc['stop_loss_price']
            actual_take_profit = position_calc['target_price']
            potential_profit = (actual_take_profit - entry_price) * position_size
            potential_loss = (entry_price - actual_stop_loss) * position_size
            
        setup = {
            'timestamp': datetime.now().isoformat(),
            'symbol': symbol,
            'direction': direction,
            'signal_strength': round(signal_strength, 3),
            'entry_price': round(entry_price, 2),
            'stop_loss': round(actual_stop_loss, 2),
            'take_profit': round(actual_take_profit, 2),
            'position_size': position_size,
            'position_value': round(position_calc['position_value'], 2),
            'risk_amount': round(risk_amount, 2),
            'potential_profit': round(potential_profit, 2),
            'potential_loss': round(potential_loss, 2),
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
        
        # Check market hours status
        market_status = get_market_status()
        can_trade, trade_msg = should_open_new_trades()
        must_close, close_msg = should_close_all_positions()
        
        # Log market status
        logger.info(f"Market Status: {market_status['market_message']}")
        
        # Handle end-of-day position closing
        if must_close:
            active_count = len(paper_trader.active_trades)
            if active_count > 0:
                logger.warning(f"🔔 {close_msg} - Closing {active_count} open position(s)")
                
                # Close all active positions at market
                for trade_id, trade in list(paper_trader.active_trades.items()):
                    try:
                        # Get current price for this ticker
                        data = self.get_market_data(trade.ticker, period='1d', interval='1m')
                        if not data.empty:
                            current_price = data['Close'].iloc[-1]
                            paper_trader.close_trade(trade_id, current_price, "End of day - market closing")
                            logger.info(f"✅ Closed {trade.ticker} position at ${current_price:.2f}")
                        else:
                            # Use last known price if we can't get current
                            paper_trader.close_trade(trade_id, trade.entry_price, "End of day - using entry price")
                            logger.warning(f"⚠️ Closed {trade.ticker} at entry price (no current data)")
                    except Exception as e:
                        logger.error(f"Error closing {trade.ticker}: {e}")
                
                logger.info("🔒 All positions closed for end of day")
            else:
                logger.info(f"✅ {close_msg} - No open positions to close")
            
            # Don't scan for new signals when closing positions
            return signals
        
        # Check if we can open new trades
        if not can_trade:
            logger.info(f"⏸️ Not scanning for trades: {trade_msg}")
            return signals
        
        logger.info(f"✅ {trade_msg} - Scanning for trade opportunities")
        
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
                            # Check if we already have an active position in this ticker
                            has_active_position = any(
                                trade.ticker == symbol 
                                for trade in paper_trader.active_trades.values()
                            )
                            
                            if has_active_position:
                                logger.info(f"⏭️ Skipping {symbol} - already have active position")
                            else:
                                try:
                                    trade_signal = {
                                        'symbol': setup['symbol'],
                                        'direction': setup['direction'],  # Pass through as-is (BUY or SELL)
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
            if len(paper_trader.active_trades) > 0:
                logger.info(f"📊 Checking {len(paper_trader.active_trades)} active trades for stop/take triggers...")
                closed_trades = paper_trader.check_stop_loss_take_profit()
                if closed_trades:
                    logger.info(f"✅ Closed {len(closed_trades)} trades via stop/take profit")
                else:
                    logger.debug(f"✅ All {len(paper_trader.active_trades)} trades within stop/take ranges")
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
#!/usr/bin/env python3
"""
Paper Trading Engine for Enhanced Day Trader
===========================================

Comprehensive trade tracking system with real market data integration.
Tracks: ticker, open/close times, quantity, direction, prices, P&L.

Features:
- Real-time trade execution based on signals
- Detailed trade history with P&L tracking
- Daily and total performance metrics
- Colorful display with Arial 12+ font
- CSV export for analysis
- Web dashboard integration

Author: GitHub Copilot
Date: October 15, 2025
"""

import json
import csv
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from pathlib import Path
import logging

# Import our market data provider
from data.schwab_market_data import schwab_data
from core.risk_manager import EnhancedRiskManager

logger = logging.getLogger(__name__)

@dataclass
class Trade:
    """Individual trade record"""
    trade_id: str
    ticker: str
    direction: str  # 'LONG' or 'SHORT'
    quantity: int
    open_price: float
    open_time: datetime
    close_price: Optional[float] = None
    close_time: Optional[datetime] = None
    signal_strength: float = 0.0
    stop_loss: float = 0.0
    take_profit: float = 0.0
    status: str = 'OPEN'  # 'OPEN', 'CLOSED', 'STOPPED'
    pnl: float = 0.0
    pnl_percent: float = 0.0
    commission: float = 0.0
    
    def __post_init__(self):
        """Generate trade ID if not provided"""
        if not self.trade_id:
            self.trade_id = f"{self.ticker}_{self.open_time.strftime('%Y%m%d_%H%M%S')}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization"""
        return {
            'trade_id': self.trade_id,
            'ticker': self.ticker,
            'direction': self.direction,
            'quantity': self.quantity,
            'open_price': self.open_price,
            'open_time': self.open_time.isoformat(),
            'close_price': self.close_price,
            'close_time': self.close_time.isoformat() if self.close_time else None,
            'signal_strength': self.signal_strength,
            'stop_loss': self.stop_loss,
            'take_profit': self.take_profit,
            'status': self.status,
            'pnl': self.pnl,
            'pnl_percent': self.pnl_percent,
            'commission': self.commission
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Trade':
        """Create Trade from dictionary"""
        trade = cls(
            trade_id=data['trade_id'],
            ticker=data['ticker'],
            direction=data['direction'],
            quantity=data['quantity'],
            open_price=data['open_price'],
            open_time=datetime.fromisoformat(data['open_time']),
            close_price=data.get('close_price'),
            close_time=datetime.fromisoformat(data['close_time']) if data.get('close_time') else None,
            signal_strength=data.get('signal_strength', 0.0),
            stop_loss=data.get('stop_loss', 0.0),
            take_profit=data.get('take_profit', 0.0),
            status=data.get('status', 'OPEN'),
            pnl=data.get('pnl', 0.0),
            pnl_percent=data.get('pnl_percent', 0.0),
            commission=data.get('commission', 0.0)
        )
        return trade

class PaperTradingEngine:
    """
    Advanced paper trading engine with real market data
    """
    
    def __init__(self, initial_balance: float = 10000, data_file: str = "paper_trades.json"):
        self.initial_balance = initial_balance
        self.current_balance = initial_balance
        self.data_file = Path(data_file)
        
        # Trade tracking
        self.active_trades: Dict[str, Trade] = {}
        self.closed_trades: List[Trade] = []
        self.trade_counter = 0
        
        # Performance metrics
        self.daily_pnl = {}  # date -> pnl
        self.total_pnl = 0.0
        self.total_commission = 0.0
        
        # Trading parameters
        self.commission_per_trade = 0.65  # Schwab commission
        self.risk_manager = EnhancedRiskManager(initial_balance)
        
        # Load existing data
        self.load_trades()
        
        logger.info(f"📊 Paper Trading Engine initialized with ${initial_balance:,.2f}")
    
    def open_trade(self, signal: Dict) -> Optional[Trade]:
        """
        Open a new trade based on signal
        
        Args:
            signal: Trading signal with entry details
            
        Returns:
            Trade object if successful, None if failed
        """
        try:
            # Extract signal details
            ticker = signal['symbol']
            direction = 'LONG' if signal['direction'] == 'BUY' else 'SHORT'
            entry_price = signal['entry_price']
            stop_loss = signal['stop_loss']
            take_profit = signal['take_profit']
            signal_strength = signal.get('signal_strength', 0.0)
            
            # Calculate position size using risk manager
            position_calc = self.risk_manager.calculate_position_size(entry_price)
            quantity = position_calc['shares']
            
            if quantity <= 0 or not position_calc['valid']:
                logger.warning(f"❌ Invalid position size for {ticker}")
                return None
            
            # Check available balance
            position_value = quantity * entry_price + self.commission_per_trade
            if position_value > self.current_balance:
                logger.warning(f"❌ Insufficient balance for {ticker}: ${position_value:.2f} > ${self.current_balance:.2f}")
                return None
            
            # Create trade
            self.trade_counter += 1
            trade = Trade(
                trade_id=f"T{self.trade_counter:04d}_{ticker}",
                ticker=ticker,
                direction=direction,
                quantity=quantity,
                open_price=entry_price,
                open_time=datetime.now(),
                signal_strength=signal_strength,
                stop_loss=stop_loss,
                take_profit=take_profit,
                commission=self.commission_per_trade
            )
            
            # Update balance
            self.current_balance -= position_value
            
            # Add to active trades
            self.active_trades[trade.trade_id] = trade
            
            # Save data
            self.save_trades()
            
            logger.info(f"✅ Opened {direction} position: {quantity} shares {ticker} @ ${entry_price:.2f}")
            return trade
            
        except Exception as e:
            logger.error(f"Error opening trade: {e}")
            return None
    
    def close_trade(self, trade_id: str, close_price: float, reason: str = "MANUAL") -> Optional[Trade]:
        """
        Close an active trade
        
        Args:
            trade_id: ID of trade to close
            close_price: Current market price
            reason: Reason for closing (MANUAL, STOP_LOSS, TAKE_PROFIT, TIME)
            
        Returns:
            Closed trade object if successful
        """
        try:
            if trade_id not in self.active_trades:
                logger.warning(f"❌ Trade {trade_id} not found in active trades")
                return None
            
            trade = self.active_trades[trade_id]
            
            # Update trade details
            trade.close_price = close_price
            trade.close_time = datetime.now()
            trade.status = f"CLOSED_{reason}"
            
            # Calculate P&L
            if trade.direction == 'LONG':
                trade.pnl = (close_price - trade.open_price) * trade.quantity - (trade.commission * 2)
            else:  # SHORT
                trade.pnl = (trade.open_price - close_price) * trade.quantity - (trade.commission * 2)
            
            trade.pnl_percent = (trade.pnl / (trade.open_price * trade.quantity)) * 100
            
            # Update balance
            position_value = trade.quantity * close_price - self.commission_per_trade
            self.current_balance += position_value
            
            # Update total P&L
            self.total_pnl += trade.pnl
            self.total_commission += trade.commission * 2
            
            # Update daily P&L
            today = trade.close_time.date().isoformat()
            if today not in self.daily_pnl:
                self.daily_pnl[today] = 0.0
            self.daily_pnl[today] += trade.pnl
            
            # Move to closed trades
            self.closed_trades.append(trade)
            del self.active_trades[trade_id]
            
            # Save data
            self.save_trades()
            
            # Log result
            status_emoji = "💰" if trade.pnl > 0 else "📉" if trade.pnl < 0 else "➖"
            logger.info(f"{status_emoji} Closed {trade.direction}: {trade.quantity} {trade.ticker} @ ${close_price:.2f} | P&L: ${trade.pnl:.2f}")
            
            return trade
            
        except Exception as e:
            logger.error(f"Error closing trade: {e}")
            return None
    
    def check_stop_loss_take_profit(self) -> List[Trade]:
        """
        Check active trades for stop loss or take profit triggers
        
        Returns:
            List of trades that were closed
        """
        closed_trades = []
        
        for trade_id, trade in list(self.active_trades.items()):
            try:
                # Get current market price
                quote = schwab_data.get_quote(trade.ticker)
                if not quote:
                    continue
                
                current_price = quote.get('lastPrice', 0)
                if current_price <= 0:
                    continue
                
                # Check stop loss
                if trade.direction == 'LONG' and current_price <= trade.stop_loss:
                    closed_trade = self.close_trade(trade_id, current_price, "STOP_LOSS")
                    if closed_trade:
                        closed_trades.append(closed_trade)
                
                elif trade.direction == 'SHORT' and current_price >= trade.stop_loss:
                    closed_trade = self.close_trade(trade_id, current_price, "STOP_LOSS")
                    if closed_trade:
                        closed_trades.append(closed_trade)
                
                # Check take profit
                elif trade.direction == 'LONG' and current_price >= trade.take_profit:
                    closed_trade = self.close_trade(trade_id, current_price, "TAKE_PROFIT")
                    if closed_trade:
                        closed_trades.append(closed_trade)
                
                elif trade.direction == 'SHORT' and current_price <= trade.take_profit:
                    closed_trade = self.close_trade(trade_id, current_price, "TAKE_PROFIT")
                    if closed_trade:
                        closed_trades.append(closed_trade)
                        
            except Exception as e:
                logger.error(f"Error checking trade {trade_id}: {e}")
        
        return closed_trades
    
    def get_performance_summary(self) -> Dict:
        """Get comprehensive performance metrics"""
        total_trades = len(self.closed_trades)
        winning_trades = len([t for t in self.closed_trades if t.pnl > 0])
        losing_trades = len([t for t in self.closed_trades if t.pnl < 0])
        
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        avg_win = np.mean([t.pnl for t in self.closed_trades if t.pnl > 0]) if winning_trades > 0 else 0
        avg_loss = np.mean([t.pnl for t in self.closed_trades if t.pnl < 0]) if losing_trades > 0 else 0
        
        profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if avg_loss != 0 and losing_trades > 0 else float('inf')
        
        # Today's performance
        today = datetime.now().date().isoformat()
        today_pnl = self.daily_pnl.get(today, 0.0)
        
        # Portfolio performance
        total_return = ((self.current_balance + self.total_pnl) / self.initial_balance - 1) * 100
        
        return {
            'current_balance': self.current_balance,
            'initial_balance': self.initial_balance,
            'total_pnl': self.total_pnl,
            'total_return_percent': total_return,
            'today_pnl': today_pnl,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'total_commission': self.total_commission,
            'active_positions': len(self.active_trades)
        }
    
    def get_recent_trades(self, limit: int = 10) -> List[Trade]:
        """Get most recent closed trades"""
        return sorted(self.closed_trades, key=lambda t: t.close_time or datetime.min, reverse=True)[:limit]
    
    def save_trades(self):
        """Save trades to JSON file"""
        try:
            data = {
                'initial_balance': self.initial_balance,
                'current_balance': self.current_balance,
                'total_pnl': self.total_pnl,
                'total_commission': self.total_commission,
                'trade_counter': self.trade_counter,
                'daily_pnl': self.daily_pnl,
                'active_trades': [trade.to_dict() for trade in self.active_trades.values()],
                'closed_trades': [trade.to_dict() for trade in self.closed_trades],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving trades: {e}")
    
    def load_trades(self):
        """Load trades from JSON file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                
                self.current_balance = data.get('current_balance', self.initial_balance)
                self.total_pnl = data.get('total_pnl', 0.0)
                self.total_commission = data.get('total_commission', 0.0)
                self.trade_counter = data.get('trade_counter', 0)
                self.daily_pnl = data.get('daily_pnl', {})
                
                # Load active trades
                for trade_data in data.get('active_trades', []):
                    trade = Trade.from_dict(trade_data)
                    self.active_trades[trade.trade_id] = trade
                
                # Load closed trades
                for trade_data in data.get('closed_trades', []):
                    trade = Trade.from_dict(trade_data)
                    self.closed_trades.append(trade)
                
                logger.info(f"📂 Loaded {len(self.closed_trades)} closed trades, {len(self.active_trades)} active trades")
                
        except Exception as e:
            logger.error(f"Error loading trades: {e}")
    
    def export_to_csv(self, filename: str = None) -> str:
        """Export trade history to CSV"""
        if filename is None:
            filename = f"paper_trades_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        try:
            all_trades = self.closed_trades + list(self.active_trades.values())
            
            with open(filename, 'w', newline='') as csvfile:
                fieldnames = [
                    'trade_id', 'ticker', 'direction', 'quantity', 
                    'open_price', 'open_time', 'close_price', 'close_time',
                    'signal_strength', 'stop_loss', 'take_profit', 
                    'status', 'pnl', 'pnl_percent', 'commission'
                ]
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                for trade in all_trades:
                    writer.writerow(trade.to_dict())
            
            logger.info(f"📊 Exported {len(all_trades)} trades to {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return ""
    
    def reset_account(self):
        """Reset the paper trading account to initial state"""
        logger.info("🔄 Resetting paper trading account...")
        
        self.current_balance = self.initial_balance
        self.active_trades.clear()
        self.closed_trades.clear()
        self.trade_counter = 0
        self.daily_pnl.clear()
        self.total_pnl = 0.0
        self.total_commission = 0.0
        
        # Save the reset state
        self.save_trades()
        
        logger.info(f"✅ Account reset to ${self.initial_balance:,.2f}")

# Global paper trading engine instance
paper_trader = PaperTradingEngine()

if __name__ == "__main__":
    # Test the paper trading engine
    print("🧪 Testing Paper Trading Engine...")
    
    # Test signal
    test_signal = {
        'symbol': 'XLK',
        'direction': 'BUY',
        'entry_price': 285.50,
        'stop_loss': 284.36,
        'take_profit': 287.78,
        'signal_strength': 0.65
    }
    
    # Open test trade
    trade = paper_trader.open_trade(test_signal)
    if trade:
        print(f"✅ Test trade opened: {trade.trade_id}")
        
        # Get performance summary
        summary = paper_trader.get_performance_summary()
        print("\n📊 Performance Summary:")
        for key, value in summary.items():
            print(f"   {key}: {value}")
        
        # Export to CSV
        csv_file = paper_trader.export_to_csv()
        print(f"\n📂 Exported to: {csv_file}")
    else:
        print("❌ Failed to open test trade")
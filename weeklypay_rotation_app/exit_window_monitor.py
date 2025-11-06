"""
Exit Window Monitor for WeeklyPay Rotation Strategy
Tracks positions and alerts when NAV profit targets are reached
"""

import pandas as pd
import pytz
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import os


class ExitWindowMonitor:
    """Monitor positions and identify optimal exit windows based on NAV profit targets"""
    
    def __init__(self, trades_file: str = "weeklypay_trades.csv"):
        """
        Initialize the Exit Window Monitor
        
        Args:
            trades_file: Path to the CSV file containing trade history
        """
        self.trades_file = trades_file
        self.eastern = pytz.timezone('America/New_York')
        
        # Exit strategy thresholds
        self.thresholds = {
            'ideal': 0.30,      # $0.30+ NAV profit = IDEAL EXIT
            'good': 0.15,       # $0.15-0.29 NAV profit = GOOD EXIT
            'acceptable': 0.05, # $0.05-0.14 NAV profit = ACCEPTABLE
            'breakeven': 0.00,  # $0.00-0.04 NAV profit = BREAKEVEN
        }
        
        # Time-based exit rules (days held)
        self.holding_rules = {
            'early': 7,      # Days 1-7: Wait for ideal/good exit
            'normal': 14,    # Days 8-14: Accept acceptable/breakeven
            'extended': 21,  # Days 15-21: Consider taking small loss if needed
        }
    
    def get_current_time_et(self) -> datetime:
        """Get current time in Eastern Time"""
        return datetime.now(self.eastern)
    
    def load_current_positions(self) -> Dict[str, Dict]:
        """
        Load current positions from trades CSV
        
        Returns:
            Dictionary of ticker -> position data
        """
        positions = {}
        
        try:
            if not os.path.exists(self.trades_file):
                return positions
            
            trades_df = pd.read_csv(self.trades_file)
            if trades_df.empty:
                return positions
            
            trades_df['Date'] = pd.to_datetime(trades_df['Date'])
            
            # Calculate positions
            for ticker in trades_df['Ticker'].unique():
                ticker_trades = trades_df[trades_df['Ticker'] == ticker].copy()
                
                # Calculate current position
                buys = ticker_trades[ticker_trades['Action'] == 'BUY']
                sells = ticker_trades[ticker_trades['Action'] == 'SELL']
                dividends = ticker_trades[ticker_trades['Action'] == 'DIVIDEND']
                
                shares_bought = buys['Quantity'].sum() if not buys.empty else 0
                shares_sold = sells['Quantity'].sum() if not sells.empty else 0
                current_shares = shares_bought - shares_sold
                
                if current_shares > 0:
                    # Calculate average purchase price and date
                    total_cost = buys['Total'].sum()
                    avg_purchase_price = total_cost / shares_bought
                    
                    # Get most recent purchase date
                    most_recent_purchase = buys['Date'].max()
                    
                    # Localize to Eastern Time if needed
                    if most_recent_purchase.tzinfo is None:
                        most_recent_purchase = self.eastern.localize(most_recent_purchase)
                    
                    # Calculate dividends received
                    total_dividends = dividends['Total'].sum() if not dividends.empty else 0
                    dividends_received_count = len(dividends) if not dividends.empty else 0
                    
                    # Has dividend been received?
                    dividend_received = dividends_received_count > 0
                    
                    positions[ticker] = {
                        'shares': current_shares,
                        'avg_purchase_price': avg_purchase_price,
                        'purchase_date': most_recent_purchase,
                        'total_cost': total_cost,
                        'dividends_received': total_dividends,
                        'dividend_count': dividends_received_count,
                        'dividend_received': dividend_received,
                        'days_held': (self.get_current_time_et() - most_recent_purchase).days
                    }
        
        except Exception as e:
            print(f"Error loading positions: {e}")
        
        return positions
    
    def analyze_exit_window(
        self, 
        ticker: str, 
        current_price: float, 
        position_data: Dict
    ) -> Dict:
        """
        Analyze if current price presents a good exit window
        
        Args:
            ticker: Ticker symbol
            current_price: Current market price
            position_data: Position data from load_current_positions()
        
        Returns:
            Dictionary with exit analysis
        """
        purchase_price = position_data['avg_purchase_price']
        days_held = position_data['days_held']
        dividend_received = position_data['dividend_received']
        
        # Calculate NAV profit/loss
        nav_change = current_price - purchase_price
        nav_change_pct = (nav_change / purchase_price) * 100
        
        # Determine exit quality based on NAV profit
        if nav_change >= self.thresholds['ideal']:
            quality = 'IDEAL'
            quality_icon = '🟢'
            recommendation = 'SELL NOW'
        elif nav_change >= self.thresholds['good']:
            quality = 'GOOD'
            quality_icon = '🟢'
            recommendation = 'SELL NOW'
        elif nav_change >= self.thresholds['acceptable']:
            quality = 'ACCEPTABLE'
            quality_icon = '🟡'
            recommendation = 'CONSIDER SELLING'
        elif nav_change >= self.thresholds['breakeven']:
            quality = 'BREAKEVEN'
            quality_icon = '🟡'
            if days_held >= self.holding_rules['normal']:
                recommendation = 'SELL TO FREE CAPITAL'
            else:
                recommendation = 'HOLD FOR BETTER EXIT'
        else:
            quality = 'LOSS'
            quality_icon = '🔴'
            if days_held >= self.holding_rules['extended']:
                recommendation = 'CONSIDER EXITING IF SMALL LOSS'
            else:
                recommendation = 'HOLD - DO NOT SELL AT LOSS'
        
        # Adjust recommendation based on dividend status
        if not dividend_received:
            recommendation = 'HOLD - DIVIDEND NOT RECEIVED YET'
            quality_icon = '🔒'
        
        # Calculate suggested limit price (slightly above current for sells)
        if quality in ['IDEAL', 'GOOD']:
            # Aggressive - set limit at current price (take it now)
            suggested_limit = current_price
            limit_strategy = 'Market/Current Price'
        elif quality == 'ACCEPTABLE':
            # Set limit $0.05-0.10 above current
            suggested_limit = current_price + 0.05
            limit_strategy = 'Limit +$0.05 (wait for small bump)'
        else:
            # Set limit at purchase price or better
            suggested_limit = max(current_price + 0.10, purchase_price)
            limit_strategy = 'Limit at breakeven or better'
        
        return {
            'ticker': ticker,
            'quality': quality,
            'quality_icon': quality_icon,
            'recommendation': recommendation,
            'nav_change': nav_change,
            'nav_change_pct': nav_change_pct,
            'purchase_price': purchase_price,
            'current_price': current_price,
            'suggested_limit': suggested_limit,
            'limit_strategy': limit_strategy,
            'days_held': days_held,
            'dividend_received': dividend_received,
            'shares': position_data['shares'],
            'potential_profit': nav_change * position_data['shares'],
            'total_dividends': position_data['dividends_received']
        }
    
    def get_all_exit_windows(self, current_prices: Dict[str, float]) -> List[Dict]:
        """
        Analyze exit windows for all current positions
        
        Args:
            current_prices: Dictionary of ticker -> current price
        
        Returns:
            List of exit window analyses, sorted by quality
        """
        positions = self.load_current_positions()
        exit_windows = []
        
        for ticker, position_data in positions.items():
            if ticker in current_prices:
                analysis = self.analyze_exit_window(
                    ticker, 
                    current_prices[ticker], 
                    position_data
                )
                exit_windows.append(analysis)
        
        # Sort by quality (IDEAL first, LOSS last)
        quality_order = {'IDEAL': 0, 'GOOD': 1, 'ACCEPTABLE': 2, 'BREAKEVEN': 3, 'LOSS': 4}
        exit_windows.sort(key=lambda x: quality_order.get(x['quality'], 5))
        
        return exit_windows
    
    def generate_exit_alert(self, exit_windows: List[Dict]) -> Dict:
        """
        Generate alert message based on exit windows
        
        Args:
            exit_windows: List of exit window analyses
        
        Returns:
            Alert dictionary with urgency and message
        """
        if not exit_windows:
            return {
                'urgency': 'info',
                'message': '💼 No open positions to monitor',
                'exits': []
            }
        
        # Count exit qualities
        ideal_exits = [e for e in exit_windows if e['quality'] == 'IDEAL']
        good_exits = [e for e in exit_windows if e['quality'] == 'GOOD']
        acceptable_exits = [e for e in exit_windows if e['quality'] == 'ACCEPTABLE']
        loss_positions = [e for e in exit_windows if e['quality'] == 'LOSS']
        
        # Determine urgency
        if ideal_exits:
            urgency = 'critical'
            message = f"🎯 {len(ideal_exits)} IDEAL EXIT(S) AVAILABLE - TAKE PROFIT NOW!"
        elif good_exits:
            urgency = 'important'
            message = f"✅ {len(good_exits)} GOOD EXIT(S) AVAILABLE - SELL RECOMMENDED"
        elif acceptable_exits:
            urgency = 'moderate'
            message = f"🟡 {len(acceptable_exits)} ACCEPTABLE EXIT(S) - CONSIDER SELLING"
        elif loss_positions:
            urgency = 'low'
            message = f"🔴 {len(loss_positions)} position(s) underwater - HOLD for recovery"
        else:
            urgency = 'info'
            message = "📊 All positions at/near breakeven - Monitor for exit windows"
        
        return {
            'urgency': urgency,
            'message': message,
            'exits': exit_windows,
            'ideal_count': len(ideal_exits),
            'good_count': len(good_exits),
            'acceptable_count': len(acceptable_exits),
            'loss_count': len(loss_positions)
        }
    
    def get_intraday_timing_suggestion(self) -> Dict:
        """
        Suggest best time of day to sell based on typical market patterns
        
        Returns:
            Dictionary with timing suggestion
        """
        current_time = self.get_current_time_et()
        hour = current_time.hour
        minute = current_time.minute
        
        # Market hours: 9:30 AM - 4:00 PM ET
        if hour < 9 or (hour == 9 and minute < 30):
            return {
                'status': 'pre_market',
                'message': '🌅 Pre-Market: Wait for 9:30 AM open',
                'next_window': '10:30-11:00 AM ET (post-open recovery)',
                'color': 'gray'
            }
        elif hour == 9 or (hour == 10 and minute < 30):
            return {
                'status': 'morning_volatile',
                'message': '⚠️ Morning Volatility: Wait for 10:30 AM',
                'next_window': '10:30-11:00 AM ET (best morning window)',
                'color': 'orange'
            }
        elif (hour == 10 and minute >= 30) or (hour == 11 and minute < 30):
            return {
                'status': 'ideal_morning',
                'message': '✅ IDEAL MORNING WINDOW: Good time to sell',
                'next_window': 'Current (10:30-11:00 AM)',
                'color': 'green'
            }
        elif hour >= 11 and hour < 14:
            return {
                'status': 'midday_slow',
                'message': '🕐 Midday: Lower volume, wait for 2:00 PM',
                'next_window': '2:00-3:00 PM ET (pre-close buying)',
                'color': 'yellow'
            }
        elif hour == 14 or (hour == 15 and minute < 30):
            return {
                'status': 'ideal_afternoon',
                'message': '✅ IDEAL AFTERNOON WINDOW: Good time to sell',
                'next_window': 'Current (2:00-3:00 PM)',
                'color': 'green'
            }
        elif hour == 15 and minute >= 30:
            return {
                'status': 'power_hour',
                'message': '⚡ POWER HOUR: Last chance for good fills',
                'next_window': 'Current (3:30-4:00 PM)',
                'color': 'green'
            }
        else:
            return {
                'status': 'after_market',
                'message': '🌙 After Hours: Market closed',
                'next_window': 'Tomorrow 10:30-11:00 AM ET',
                'color': 'gray'
            }
    
    def format_exit_display(self, exit_analysis: Dict) -> str:
        """
        Format exit analysis for display
        
        Args:
            exit_analysis: Exit analysis dictionary
        
        Returns:
            Formatted string for display
        """
        lines = []
        lines.append(f"{exit_analysis['quality_icon']} {exit_analysis['ticker']} - {exit_analysis['quality']} EXIT")
        lines.append(f"   Purchase: ${exit_analysis['purchase_price']:.2f} → Current: ${exit_analysis['current_price']:.2f}")
        lines.append(f"   NAV Change: ${exit_analysis['nav_change']:+.2f} ({exit_analysis['nav_change_pct']:+.2f}%)")
        lines.append(f"   Days Held: {exit_analysis['days_held']} | Dividend: {'✓' if exit_analysis['dividend_received'] else '✗'}")
        lines.append(f"   💰 Potential Profit: ${exit_analysis['potential_profit']:+.2f}")
        lines.append(f"   📊 Recommendation: {exit_analysis['recommendation']}")
        lines.append(f"   🎯 Suggested Limit: ${exit_analysis['suggested_limit']:.2f} ({exit_analysis['limit_strategy']})")
        
        return "\n".join(lines)


def get_exit_window_monitor():
    """Convenience function to get ExitWindowMonitor instance"""
    return ExitWindowMonitor()


# For testing
if __name__ == "__main__":
    monitor = ExitWindowMonitor()
    
    # Test with sample prices
    test_prices = {
        'NVDW': 42.45,
        'XOMO': 28.80,
        'QDTE': 35.20
    }
    
    print("=" * 60)
    print("EXIT WINDOW MONITOR TEST")
    print("=" * 60)
    
    # Get current positions
    positions = monitor.load_current_positions()
    print(f"\n📊 Current Positions: {len(positions)}")
    for ticker, pos in positions.items():
        print(f"   {ticker}: {pos['shares']} shares @ ${pos['avg_purchase_price']:.2f}")
        print(f"   Held: {pos['days_held']} days | Dividend: {'✓' if pos['dividend_received'] else '✗'}")
    
    # Analyze exit windows
    print("\n" + "=" * 60)
    print("EXIT WINDOW ANALYSIS")
    print("=" * 60)
    
    exit_windows = monitor.get_all_exit_windows(test_prices)
    for exit_window in exit_windows:
        print(f"\n{monitor.format_exit_display(exit_window)}")
    
    # Generate alert
    print("\n" + "=" * 60)
    print("EXIT ALERT")
    print("=" * 60)
    
    alert = monitor.generate_exit_alert(exit_windows)
    print(f"\nUrgency: {alert['urgency'].upper()}")
    print(f"Message: {alert['message']}")
    
    # Timing suggestion
    print("\n" + "=" * 60)
    print("INTRADAY TIMING")
    print("=" * 60)
    
    timing = monitor.get_intraday_timing_suggestion()
    print(f"\nStatus: {timing['status']}")
    print(f"Message: {timing['message']}")
    print(f"Next Best Window: {timing['next_window']}")
    
    print("\n" + "=" * 60)
    print("✅ Test complete!")

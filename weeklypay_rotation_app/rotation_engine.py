"""
WeeklyPay Rotation Engine
Manages the weekly dividend rotation strategy with accurate timing and NAV protection
"""

from datetime import datetime, timedelta, time
import pytz
from typing import Dict, List, Tuple, Optional
from settings_manager import WeeklyPaySettingsManager

class RotationEngine:
    """Engine for managing weekly dividend rotation strategy"""
    
    def __init__(self):
        self.settings_manager = WeeklyPaySettingsManager()
        self.eastern = pytz.timezone('America/New_York')
        
        # Market hours (Eastern Time)
        self.market_open = time(9, 30)  # 9:30 AM ET
        self.market_close = time(16, 0)  # 4:00 PM ET
        self.safe_buy_deadline = time(15, 30)  # 3:30 PM ET (safer cutoff)
    
    def get_current_time_et(self) -> datetime:
        """Get current time in Eastern Time"""
        utc_now = datetime.now(pytz.utc)
        return utc_now.astimezone(self.eastern)
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        now_et = self.get_current_time_et()
        
        # Check if weekend
        if now_et.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check market hours
        current_time = now_et.time()
        return self.market_open <= current_time <= self.market_close
    
    def get_next_trading_day(self, from_date: datetime = None) -> datetime:
        """Get next trading day (skip weekends)"""
        if from_date is None:
            from_date = self.get_current_time_et()
        
        next_day = from_date + timedelta(days=1)
        
        # Skip weekends
        while next_day.weekday() >= 5:  # Saturday or Sunday
            next_day += timedelta(days=1)
        
        return next_day
    
    def get_previous_trading_day(self, from_date: datetime = None) -> datetime:
        """Get previous trading day (skip weekends)"""
        if from_date is None:
            from_date = self.get_current_time_et()
        
        prev_day = from_date - timedelta(days=1)
        
        # Skip weekends
        while prev_day.weekday() >= 5:  # Saturday or Sunday
            prev_day -= timedelta(days=1)
        
        return prev_day
    
    def calculate_next_ex_dividend_date(self, ticker: str) -> datetime:
        """
        Calculate next ex-dividend date for a ticker based on its schedule
        """
        ticker_info = self.settings_manager.get_ticker_info(ticker)
        if not ticker_info:
            return None
        
        ex_dividend_day = ticker_info.get('ex_dividend_day', 'Tuesday')
        last_ex_date_str = ticker_info.get('last_ex_date', '')
        
        try:
            last_ex_date = datetime.strptime(last_ex_date_str, '%Y-%m-%d')
            last_ex_date = self.eastern.localize(last_ex_date.replace(hour=9, minute=30))
        except:
            # Fallback to this week
            last_ex_date = self.get_current_time_et()
        
        # Calculate weeks passed since last ex-dividend
        current_time = self.get_current_time_et()
        days_since = (current_time - last_ex_date).days
        weeks_passed = days_since // 7
        
        # Calculate next ex-dividend date (weekly pattern)
        next_ex_date = last_ex_date + timedelta(days=(weeks_passed + 1) * 7)
        
        # If calculated date is in the past, add another week
        while next_ex_date < current_time:
            next_ex_date += timedelta(days=7)
        
        return next_ex_date
    
    def calculate_buy_deadline(self, ticker: str) -> Tuple[datetime, str]:
        """
        Calculate the absolute deadline to buy a ticker to capture the dividend
        
        Returns:
            (deadline_datetime, description)
        """
        next_ex_div = self.calculate_next_ex_dividend_date(ticker)
        if not next_ex_div:
            return None, "Unknown ex-dividend date"
        
        # Must buy the trading day BEFORE ex-dividend
        buy_day = self.get_previous_trading_day(next_ex_div)
        
        # Set deadline to market close (4:00 PM) or safe deadline (3:30 PM)
        buy_deadline = buy_day.replace(hour=15, minute=30, second=0, microsecond=0)
        
        # Format description
        current_time = self.get_current_time_et()
        time_until = buy_deadline - current_time
        
        if time_until.total_seconds() < 0:
            # Deadline passed
            description = f"Deadline passed (was {buy_deadline.strftime('%a %m/%d at %I:%M %p ET')})"
        elif time_until.days > 0:
            description = f"{buy_deadline.strftime('%A %m/%d')} by {buy_deadline.strftime('%I:%M %p ET')} ({time_until.days} days)"
        else:
            hours = int(time_until.total_seconds() // 3600)
            minutes = int((time_until.total_seconds() % 3600) // 60)
            
            # Check if deadline is actually today or tomorrow
            if buy_deadline.date() == current_time.date():
                day_text = "TODAY"
            else:
                day_text = buy_deadline.strftime('%A')  # e.g., "Friday"
            
            description = f"{day_text} by {buy_deadline.strftime('%I:%M %p ET')} ({hours}h {minutes}m remaining)"
        
        return buy_deadline, description
    
    def calculate_sell_eligibility(self, ticker: str, purchase_date: datetime, 
                                   purchase_price: float, current_price: float) -> Dict:
        """
        Determine if a ticker can be sold based on dividend receipt and NAV
        
        Returns dict with:
            - can_sell: bool
            - reason: str
            - nav_status: str ('profit', 'breakeven', 'loss')
            - nav_pct: float
            - dividend_status: str ('received', 'pending', 'today')
        """
        result = {
            'can_sell': False,
            'reason': '',
            'nav_status': 'unknown',
            'nav_pct': 0.0,
            'dividend_status': 'unknown',
            'days_held': 0
        }
        
        # Calculate NAV
        nav_pct = ((current_price - purchase_price) / purchase_price) * 100
        result['nav_pct'] = round(nav_pct, 2)
        
        if nav_pct > 0.1:
            result['nav_status'] = 'profit'
        elif nav_pct >= -0.1:
            result['nav_status'] = 'breakeven'
        else:
            result['nav_status'] = 'loss'
        
        # Calculate days held
        current_time = self.get_current_time_et()
        result['days_held'] = (current_time - purchase_date).days
        
        # Determine dividend status
        next_ex_div = self.calculate_next_ex_dividend_date(ticker)
        ticker_info = self.settings_manager.get_ticker_info(ticker)
        pay_day_offset = 1  # Usually pays 1 day after ex-dividend
        
        if next_ex_div:
            # Check if we've passed ex-dividend date
            if current_time.date() > next_ex_div.date():
                # Already went ex-dividend
                pay_date = next_ex_div + timedelta(days=pay_day_offset)
                if current_time.date() >= pay_date.date():
                    result['dividend_status'] = 'received'
                else:
                    result['dividend_status'] = 'pending'
            elif current_time.date() == next_ex_div.date():
                result['dividend_status'] = 'today'
            else:
                result['dividend_status'] = 'future'
        
        # Determine if can sell
        if result['nav_status'] == 'loss':
            result['can_sell'] = False
            result['reason'] = f"NAV at loss ({nav_pct:.2f}%) - hold until recovery"
        elif result['dividend_status'] in ['today', 'future']:
            result['can_sell'] = False
            result['reason'] = f"Must hold until ex-dividend on {next_ex_div.strftime('%a %m/%d')}"
        elif result['dividend_status'] == 'pending':
            result['can_sell'] = False
            result['reason'] = "Dividend pending payment - hold 1 more day"
        elif result['dividend_status'] == 'received':
            result['can_sell'] = True
            result['reason'] = f"✅ Dividend received, NAV at {nav_pct:+.2f}%"
        
        return result
    
    def find_next_rotation_targets(self) -> List[Dict]:
        """
        Find tickers eligible for the next rotation based on timing
        
        Returns ONLY the next available ex-date group (must buy day before ex-date)
        Logic: Shows next group where deadline hasn't passed yet
        Example: Monday 11am -> Show Wednesday group (must buy Tuesday)
                 Tuesday 4pm -> Too late for Wednesday, show Thursday group
        """
        current_time = self.get_current_time_et()
        current_day = current_time.strftime('%A')  # Monday, Tuesday, etc.
        
        all_tickers = self.settings_manager.get_all_tickers_info()
        all_targets = []
        
        # First, calculate all potential targets with their deadlines
        for ticker, info in all_tickers.items():
            # Calculate next ex-dividend date
            next_ex_div = self.calculate_next_ex_dividend_date(ticker)
            if not next_ex_div:
                continue
            
            # Calculate buy deadline (must purchase day before ex-date)
            buy_deadline, deadline_desc = self.calculate_buy_deadline(ticker)
            if not buy_deadline:
                continue
            
            # Only include if deadline hasn't passed
            if buy_deadline > current_time:
                days_until_deadline = (buy_deadline - current_time).days
                
                all_targets.append({
                    'ticker': ticker,
                    'name': info.get('name', ''),
                    'ex_dividend_day': info.get('ex_dividend_day', ''),
                    'pay_day': info.get('pay_day', ''),
                    'next_ex_div_date': next_ex_div,
                    'buy_deadline': buy_deadline,
                    'deadline_description': deadline_desc,
                    'days_until_deadline': days_until_deadline,
                    'hours_until_deadline': (buy_deadline - current_time).total_seconds() / 3600,
                    'is_urgent': days_until_deadline == 0,  # Today is the deadline
                })
        
        if not all_targets:
            return []
        
        # Sort by deadline (earliest first)
        all_targets.sort(key=lambda x: x['buy_deadline'])
        
        # Get the earliest ex-dividend date (next available group)
        earliest_ex_date = all_targets[0]['next_ex_div_date'].date()
        
        # Filter to only show tickers with this ex-dividend date
        # This ensures we only show ONE group at a time (the next available)
        next_group_targets = [
            t for t in all_targets 
            if t['next_ex_div_date'].date() == earliest_ex_date
        ]
        
        return next_group_targets
    
    def analyze_holdings(self, holdings: List[Dict]) -> Dict:
        """
        Analyze current holdings to determine rotation status
        
        Input holdings format:
        [
            {
                'ticker': 'NVDW',
                'purchase_date': datetime,
                'purchase_price': 42.20,
                'current_price': 42.50,
                'shares': 100
            },
            ...
        ]
        
        Returns categorized holdings:
        {
            'ready_to_sell': [...],    # At/past ex-date AND not in next rotation group
            'must_hold': [...],          # Waiting for ex-date OR NAV >= purchase AND in next rotation group
            'hold_for_nav': [...]        # NAV < purchase AND not in next rotation group
        }
        
        Logic:
        - Ready to Sell: Past ex-date, not in next rotation group (can sell to free capital)
        - Must Hold: Either waiting for ex-date OR in next rotation group (keep for upcoming dividend)
        - Hold for NAV: Below purchase price, not in next rotation group (wait for recovery)
        """
        categorized = {
            'ready_to_sell': [],
            'must_hold': [],
            'hold_for_nav': []
        }
        
        # Get next rotation targets to check if ticker is in upcoming group
        next_targets = self.find_next_rotation_targets()
        next_rotation_tickers = set(t['ticker'] for t in next_targets)
        
        current_time = self.get_current_time_et()
        
        for holding in holdings:
            ticker = holding['ticker']
            eligibility = self.calculate_sell_eligibility(
                ticker,
                holding['purchase_date'],
                holding['purchase_price'],
                holding['current_price']
            )
            
            # Add eligibility info to holding
            holding_with_status = {**holding, **eligibility}
            
            # Check if ticker is in next rotation group
            in_next_rotation = ticker in next_rotation_tickers
            
            # Calculate NAV
            nav_pct = ((holding['current_price'] - holding['purchase_price']) / holding['purchase_price']) * 100
            
            # Determine if this holding has passed through an ex-dividend cycle
            # Check if at least 7 days have passed since purchase (one weekly cycle)
            days_since_purchase = (current_time - holding['purchase_date']).days
            
            # Get next ex-dividend date
            next_ex_div = self.calculate_next_ex_dividend_date(ticker)
            
            # A holding has "passed ex-date" if:
            # 1. Held for at least 2 days (enough time to go ex-dividend)
            # 2. Next ex-div is in the future (meaning we already passed a previous one)
            # 3. Purchase date was before the most recent ex-div
            past_ex_date = False
            if next_ex_div and days_since_purchase >= 2:
                # If next ex-div is in the future, check if purchase was before last week's ex-div
                # For weekly payers, if we're 2+ days past purchase and next ex-div is future,
                # we likely already went through an ex-dividend cycle
                ticker_info = self.settings_manager.get_ticker_info(ticker)
                last_ex_date_str = ticker_info.get('last_ex_date', '')
                
                if last_ex_date_str:
                    try:
                        last_ex_date = datetime.strptime(last_ex_date_str, '%Y-%m-%d')
                        last_ex_date = self.eastern.localize(last_ex_date.replace(hour=9, minute=30))
                        
                        # If purchase was before or on the last known ex-date, we've passed it
                        if holding['purchase_date'].date() <= last_ex_date.date() and current_time.date() > last_ex_date.date():
                            past_ex_date = True
                    except:
                        pass
            
            # Categorization logic based on user requirements:
            # NOTE: A ticker can appear in MULTIPLE categories!
            
            # READY TO SELL: At/beyond ex-date AND not in next rotation group
            if past_ex_date and not in_next_rotation:
                ready_reason = f"✅ Past ex-date, not in next rotation (NAV {nav_pct:+.2f}%)"
                holding_ready = {**holding_with_status, 'reason': ready_reason}
                categorized['ready_to_sell'].append(holding_ready)
            
            # MUST HOLD: Waiting for ex-date OR in next rotation group OR below purchase price
            if in_next_rotation:
                if next_ex_div:
                    hold_reason = f"🎯 In next rotation group (ex-div {next_ex_div.strftime('%a %m/%d')})"
                else:
                    hold_reason = f"🎯 In next rotation group - Hold for upcoming dividend"
                holding_must_hold = {**holding_with_status, 'reason': hold_reason}
                categorized['must_hold'].append(holding_must_hold)
            elif not past_ex_date and next_ex_div:
                hold_reason = f"🔒 Waiting for ex-dividend on {next_ex_div.strftime('%a %m/%d')}"
                holding_must_hold = {**holding_with_status, 'reason': hold_reason}
                categorized['must_hold'].append(holding_must_hold)
            elif nav_pct < 0:
                hold_reason = f"📉 Below purchase price ({nav_pct:.2f}%) - Hold to recover"
                holding_must_hold = {**holding_with_status, 'reason': hold_reason}
                categorized['must_hold'].append(holding_must_hold)
            
            # HOLD FOR NAV: NAV < purchase price AND not in next rotation group
            if nav_pct < 0 and not in_next_rotation:
                nav_reason = f"📉 Below purchase price ({nav_pct:.2f}%) - Hold for NAV recovery"
                holding_nav = {**holding_with_status, 'reason': nav_reason}
                categorized['hold_for_nav'].append(holding_nav)
        
        return categorized
    
    def get_rotation_alert(self, holdings: List[Dict]) -> Dict:
        """
        Generate the main rotation alert message
        
        Returns:
        {
            'has_action': bool,
            'urgency': 'critical' | 'important' | 'info',
            'message': str,
            'actions': [
                {'type': 'sell', 'ticker': 'NVDW', 'details': ...},
                {'type': 'buy', 'ticker': 'MSFW', 'details': ...}
            ]
        }
        """
        current_time = self.get_current_time_et()
        current_day = current_time.strftime('%A')
        
        # Analyze holdings
        categorized = self.analyze_holdings(holdings)
        
        # Find next targets
        next_targets = self.find_next_rotation_targets()
        
        alert = {
            'current_time': current_time,
            'current_day': current_day,
            'has_action': False,
            'urgency': 'info',
            'message': '',
            'actions': []
        }
        
        # Check for urgent buy opportunities
        urgent_buys = [t for t in next_targets if t['is_urgent']]
        if urgent_buys:
            alert['has_action'] = True
            alert['urgency'] = 'critical'
            alert['message'] = f"⏰ URGENT: Buy deadline TODAY for {len(urgent_buys)} ticker(s)"
            for target in urgent_buys:
                alert['actions'].append({
                    'type': 'buy',
                    'ticker': target['ticker'],
                    'deadline': target['deadline_description'],
                    'ex_div_date': target['next_ex_div_date'].strftime('%a %m/%d')
                })
        
        # Check for ready-to-sell holdings (only those at or above purchase price)
        sellable_holdings = [h for h in categorized['ready_to_sell'] if h['nav_pct'] >= 0]
        if sellable_holdings:
            alert['has_action'] = True
            if alert['urgency'] == 'info':
                alert['urgency'] = 'important'
            sell_msg = f"✅ {len(sellable_holdings)} ticker(s) ready to sell"
            if alert['message']:
                alert['message'] += f" | {sell_msg}"
            else:
                alert['message'] = sell_msg
            
            for holding in sellable_holdings:
                alert['actions'].append({
                    'type': 'sell',
                    'ticker': holding['ticker'],
                    'nav_pct': holding['nav_pct'],
                    'reason': holding['reason']
                })
        
        # Check for must-hold tickers
        if categorized['must_hold']:
            hold_msg = f"🔒 {len(categorized['must_hold'])} ticker(s) must hold (pre-dividend)"
            if alert['message']:
                alert['message'] += f" | {hold_msg}"
            else:
                alert['message'] = hold_msg
        
        # If no actions, show next opportunity
        if not alert['has_action'] and next_targets:
            next_target = next_targets[0]
            alert['message'] = f"Next rotation: Buy {next_target['ticker']} by {next_target['deadline_description']}"
        
        return alert


# Convenience function
def get_rotation_engine():
    """Get a RotationEngine instance"""
    return RotationEngine()

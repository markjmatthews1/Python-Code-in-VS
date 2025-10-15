"""
Rotation Rules Engine for WeeklyPay™ ETFs
Implements the core logic for rotation decisions
"""

import datetime
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum

class RotationSignal(Enum):
    """Rotation signal types"""
    ROTATE_IN = "ROTATE_IN"
    ROTATE_OUT = "ROTATE_OUT"
    HOLD = "HOLD"

@dataclass
class MarketData:
    """Market data for rotation decisions"""
    symbol: str
    price: float
    rsi: float = 0.0
    sma_20: float = 0.0
    sma_50: float = 0.0
    volume: int = 0
    last_updated: str = ""

@dataclass
class EarningsEvent:
    """Earnings event data"""
    symbol: str
    earnings_date: str
    is_this_week: bool = False
    is_post_earnings: bool = False

@dataclass
class RotationDecision:
    """Rotation decision with reasoning"""
    symbol: str
    signal: RotationSignal
    confidence: float  # 0.0 to 1.0
    reasons: List[str]
    priority: int  # 1 = highest priority
    
class RotationRulesEngine:
    """Core engine for WeeklyPay™ rotation decisions"""
    
    def __init__(self, etf_tracker):
        self.etf_tracker = etf_tracker
        self.sector_rsi_high_threshold = 60
        self.sector_rsi_low_threshold = 40
        self.payout_threshold = 0.5  # 0.5% of NAV
        
        # Market data storage
        self.market_data: Dict[str, MarketData] = {}
        self.sector_data: Dict[str, MarketData] = {}
        self.earnings_calendar: List[EarningsEvent] = []
        
        print("🧠 Rotation Rules Engine initialized")
        print(f"   📊 RSI Thresholds: High={self.sector_rsi_high_threshold}, Low={self.sector_rsi_low_threshold}")
        print(f"   💰 Payout Threshold: {self.payout_threshold}%")
    
    def update_market_data(self, symbol: str, price: float, rsi: float = 0.0, 
                          sma_20: float = 0.0, sma_50: float = 0.0, volume: int = 0):
        """Update market data for a symbol"""
        self.market_data[symbol] = MarketData(
            symbol=symbol,
            price=price,
            rsi=rsi,
            sma_20=sma_20,
            sma_50=sma_50,
            volume=volume,
            last_updated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print(f"📊 Updated market data for {symbol}: ${price:.2f}, RSI={rsi:.1f}")
    
    def update_sector_data(self, sector_symbol: str, rsi: float, price: float = 0.0):
        """Update sector ETF data (SMH, XLC, XLK)"""
        self.sector_data[sector_symbol] = MarketData(
            symbol=sector_symbol,
            price=price,
            rsi=rsi,
            last_updated=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        print(f"🏭 Updated sector data for {sector_symbol}: RSI={rsi:.1f}")
    
    def add_earnings_event(self, underlying_symbol: str, earnings_date: str):
        """Add earnings event to calendar"""
        # Check if earnings is this week
        earnings_dt = datetime.datetime.strptime(earnings_date, "%Y-%m-%d")
        today = datetime.datetime.now()
        week_start = today - datetime.timedelta(days=today.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        
        is_this_week = week_start <= earnings_dt <= week_end
        is_post_earnings = earnings_dt < today
        
        event = EarningsEvent(
            symbol=underlying_symbol,
            earnings_date=earnings_date,
            is_this_week=is_this_week,
            is_post_earnings=is_post_earnings
        )
        
        self.earnings_calendar.append(event)
        status = "THIS WEEK" if is_this_week else "POST" if is_post_earnings else "FUTURE"
        print(f"📅 Added earnings for {underlying_symbol}: {earnings_date} ({status})")
    
    def integrate_weekly_payouts(self, weekly_payouts_tracker):
        """Integrate weekly payout data from WeeklyPayoutTracker"""
        if not weekly_payouts_tracker or not weekly_payouts_tracker.payout_data:
            return
        
        print("💰 Integrating weekly payout data...")
        
        for symbol, payout in weekly_payouts_tracker.payout_data.items():
            # Update ETF tracker with the latest payout data
            if self.etf_tracker.get_etf_metadata(symbol):
                self.etf_tracker.add_payout_data(
                    symbol, 
                    payout.pay_date, 
                    payout.dividend_amount
                )
                
                # Update current price and NAV
                current_price = payout.nav_price - 0.27  # Estimate
                self.etf_tracker.update_etf_price(symbol, current_price, payout.nav_price)
                
                print(f"💰 Updated {symbol}: ${payout.dividend_amount:.3f} ({payout.payout_percentage:.2f}% NAV)")
        
        print(f"✅ Integrated {len(weekly_payouts_tracker.payout_data)} weekly payouts")
    
    def evaluate_etf(self, etf_symbol: str) -> RotationDecision:
        """Evaluate a single ETF for rotation decision"""
        etf_metadata = self.etf_tracker.get_etf_metadata(etf_symbol)
        if not etf_metadata:
            return RotationDecision(etf_symbol, RotationSignal.HOLD, 0.0, ["ETF not found"], 999)
        
        reasons = []
        signal = RotationSignal.HOLD
        confidence = 0.5
        priority = 5
        
        underlying = etf_metadata.underlying_ticker
        
        # Rule 1: Earnings this week → ROTATE IN
        earnings_this_week = any(e.symbol == underlying and e.is_this_week 
                               for e in self.earnings_calendar)
        if earnings_this_week:
            signal = RotationSignal.ROTATE_IN
            confidence += 0.3
            priority = min(priority, 1)
            reasons.append(f"{underlying} has earnings this week")
        
        # Rule 2: Post-earnings → ROTATE OUT
        post_earnings = any(e.symbol == underlying and e.is_post_earnings 
                          for e in self.earnings_calendar)
        if post_earnings and not earnings_this_week:
            signal = RotationSignal.ROTATE_OUT
            confidence += 0.2
            priority = min(priority, 3)
            reasons.append(f"{underlying} is post-earnings")
        
        # Rule 3: Sector RSI > 60 → ROTATE IN
        sector_rsi = self.get_relevant_sector_rsi(etf_metadata.sector)
        if sector_rsi > self.sector_rsi_high_threshold:
            if signal != RotationSignal.ROTATE_OUT:
                signal = RotationSignal.ROTATE_IN
                confidence += 0.2
                priority = min(priority, 2)
            reasons.append(f"Sector RSI high: {sector_rsi:.1f}")
        
        # Rule 4: Sector RSI < 40 → ROTATE OUT
        elif sector_rsi < self.sector_rsi_low_threshold:
            signal = RotationSignal.ROTATE_OUT
            confidence += 0.2
            priority = min(priority, 4)
            reasons.append(f"Sector RSI low: {sector_rsi:.1f}")
        
        # Rule 5: Weekly payout > 0.5% NAV → ROTATE IN
        recent_payout_pct = self.etf_tracker.get_recent_payout_percentage(etf_symbol)
        if recent_payout_pct > self.payout_threshold:
            if signal != RotationSignal.ROTATE_OUT:
                signal = RotationSignal.ROTATE_IN
                confidence += 0.15
                priority = min(priority, 2)
            reasons.append(f"High payout: {recent_payout_pct:.2f}%")
        
        # Adjust confidence based on multiple factors
        confidence = min(confidence, 1.0)
        
        if not reasons:
            reasons.append("No significant signals detected")
        
        return RotationDecision(etf_symbol, signal, confidence, reasons, priority)
    
    def get_relevant_sector_rsi(self, sector: str) -> float:
        """Get RSI for the relevant sector ETF"""
        sector_mapping = {
            "Technology": "SMH",  # Semiconductor ETF for tech
            "Communication": "XLC"
        }
        
        sector_etf = sector_mapping.get(sector, "XLK")  # Default to XLK
        if sector_etf in self.sector_data:
            return self.sector_data[sector_etf].rsi
        return 50.0  # Neutral RSI if no data
    
    def generate_rotation_signals(self) -> Dict:
        """Generate rotation signals for all tracked ETFs"""
        current_week = datetime.datetime.now().strftime("Week of %b %d, %Y")
        
        decisions = []
        for etf_symbol in self.etf_tracker.get_etf_list():
            decision = self.evaluate_etf(etf_symbol)
            decisions.append(decision)
        
        # Sort by priority (lower number = higher priority)
        decisions.sort(key=lambda x: (x.priority, -x.confidence))
        
        # Separate into rotate in/out lists
        rotate_in = [d.symbol for d in decisions if d.signal == RotationSignal.ROTATE_IN]
        rotate_out = [d.symbol for d in decisions if d.signal == RotationSignal.ROTATE_OUT]
        hold = [d.symbol for d in decisions if d.signal == RotationSignal.HOLD]
        
        # Generate summary notes
        notes = []
        for decision in decisions[:3]:  # Top 3 priorities
            if decision.signal != RotationSignal.HOLD:
                note = f"{decision.symbol}: {'; '.join(decision.reasons[:2])}"
                notes.append(note)
        
        signal_output = {
            "week": current_week,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "rotate_in": rotate_in,
            "rotate_out": rotate_out, 
            "hold": hold,
            "notes": notes,
            "detailed_decisions": [
                {
                    "symbol": d.symbol,
                    "signal": d.signal.value,
                    "confidence": f"{d.confidence:.2f}",
                    "priority": d.priority,
                    "reasons": d.reasons
                }
                for d in decisions
            ]
        }
        
        return signal_output
    
    def generate_alert_format(self, weekly_payouts_tracker=None) -> Dict:
        """Generate alerts in the exact format requested by user"""
        # Generate standard rotation signals
        signals = self.generate_rotation_signals()
        
        # Get current week dates 
        today = datetime.datetime.now()
        week_start = today - datetime.timedelta(days=today.weekday())
        week_end = week_start + datetime.timedelta(days=4)  # Friday
        week_range = f"{week_start.strftime('%b %d')}–{week_end.strftime('%d')}"
        
        # Build comprehensive notes
        alert_notes = []
        
        # Add earnings notes
        for decision in signals['detailed_decisions']:
            symbol = decision['symbol']
            if decision['signal'] in ['ROTATE_IN', 'ROTATE_OUT']:
                for reason in decision['reasons']:
                    if 'earnings' in reason:
                        alert_notes.append(reason)
        
        # Add sector momentum notes
        sector_notes = []
        if hasattr(self, 'sector_data'):
            for sector_symbol, data in self.sector_data.items():
                if sector_symbol == "SMH":
                    sector_notes.append(f"SMH RSI = {data.rsi:.0f} ({'bullish' if data.rsi > 60 else 'bearish' if data.rsi < 40 else 'neutral'})")
                elif sector_symbol == "XLC":
                    sector_notes.append(f"XLC RSI = {data.rsi:.0f} ({'bullish' if data.rsi > 60 else 'bearish' if data.rsi < 40 else 'neutral'})")
        
        alert_notes.extend(sector_notes)
        
        # Add payout notes from weekly payouts tracker
        if weekly_payouts_tracker:
            highest_payouts = weekly_payouts_tracker.get_highest_payout_etfs(3)
            for symbol, payout_pct in highest_payouts:
                if payout_pct >= 0.8:  # Only show notable payouts
                    alert_notes.append(f"{symbol} payout = {payout_pct:.1f}% NAV")
        
        # Format final alert
        alert = {
            "week": week_range,
            "rotate_in": signals['rotate_in'],
            "rotate_out": signals['rotate_out'],
            "notes": alert_notes[:6]  # Limit to top 6 most important notes
        }
        
        return alert
    
    def display_rotation_signals(self, signals: Dict):
        """Display rotation signals in a formatted way"""
        print("\n" + "="*70)
        print("🎯 WEEKLYPAY™ ROTATION SIGNALS")
        print("="*70)
        print(f"📅 {signals['week']}")
        print(f"⏰ Generated: {signals['timestamp']}")
        
        # Rotate In signals (GREEN)
        if signals['rotate_in']:
            print(f"\n🟢 ROTATE IN:")
            for symbol in signals['rotate_in']:
                etf = self.etf_tracker.get_etf_metadata(symbol)
                underlying = etf.underlying_ticker if etf else "N/A"
                print(f"   📈 {symbol} ({underlying})")
        
        # Rotate Out signals (RED)
        if signals['rotate_out']:
            print(f"\n🔴 ROTATE OUT:")
            for symbol in signals['rotate_out']:
                etf = self.etf_tracker.get_etf_metadata(symbol)
                underlying = etf.underlying_ticker if etf else "N/A"
                print(f"   📉 {symbol} ({underlying})")
        
        # Hold signals (YELLOW)
        if signals['hold']:
            print(f"\n🟡 HOLD:")
            for symbol in signals['hold']:
                etf = self.etf_tracker.get_etf_metadata(symbol)
                underlying = etf.underlying_ticker if etf else "N/A"
                print(f"   ➡️  {symbol} ({underlying})")
        
        # Key notes
        if signals['notes']:
            print(f"\n📝 KEY INSIGHTS:")
            for note in signals['notes']:
                print(f"   • {note}")
        
        print("\n" + "="*70)

# Example usage and testing
if __name__ == "__main__":
    from etf_tracker import ETFTracker
    
    # Initialize components
    tracker = ETFTracker("../data/etf_list.json")
    engine = RotationRulesEngine(tracker)
    
    # Add sample market data
    engine.update_market_data("NVDA", 145.50, rsi=65.2)
    engine.update_market_data("AMD", 125.30, rsi=58.7)
    engine.update_market_data("META", 485.20, rsi=72.1)
    
    # Add sector data
    engine.update_sector_data("SMH", 64.5)  # High RSI - bullish tech
    engine.update_sector_data("XLC", 42.1)  # Low RSI
    
    # Add earnings events
    engine.add_earnings_event("AMD", "2025-10-08")  # This week
    engine.add_earnings_event("META", "2025-09-30") # Post-earnings
    
    # Update ETF prices and payouts
    tracker.update_etf_price("NVDW", 45.23, 45.50)
    tracker.update_etf_price("AMDW", 32.67, 32.80) 
    tracker.update_etf_price("HOOW", 67.89, 68.00)
    
    tracker.add_payout_data("NVDW", "2025-10-01", 0.28)  # 0.61% payout
    tracker.add_payout_data("AMDW", "2025-10-01", 0.15)  # 0.46% payout
    
    # Generate and display signals
    signals = engine.generate_rotation_signals()
    engine.display_rotation_signals(signals)
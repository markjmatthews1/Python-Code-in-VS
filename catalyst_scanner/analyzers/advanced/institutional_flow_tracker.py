"""
Institutional Flow Tracker - Phase 4.4
Advanced institutional activity monitoring for smart money flow analysis
Tracks 13F filings, insider trading, and block trades for institutional sentiment
"""

import logging
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class InstitutionalPosition:
    """Data structure for institutional position data"""
    institution_name: str
    ticker: str
    shares_held: int
    market_value: float
    percentage_of_portfolio: float
    change_from_previous: float  # Shares change
    change_percentage: float
    filing_date: datetime
    position_type: str  # 'NEW', 'INCREASED', 'DECREASED', 'SOLD_OUT'


@dataclass
class InsiderTrade:
    """Data structure for insider trading data"""
    ticker: str
    insider_name: str
    title: str
    transaction_date: datetime
    transaction_type: str  # 'BUY', 'SELL'
    shares: int
    price: float
    value: float
    ownership_type: str  # 'DIRECT', 'INDIRECT'


@dataclass
class BlockTrade:
    """Data structure for large block trades"""
    ticker: str
    timestamp: datetime
    volume: int
    price: float
    value: float
    trade_type: str  # 'BUY', 'SELL', 'NEUTRAL'
    size_category: str  # 'LARGE', 'VERY_LARGE', 'INSTITUTIONAL'


@dataclass
class InstitutionalAnalysis:
    """Comprehensive institutional flow analysis results"""
    ticker: str
    timestamp: datetime
    smart_money_sentiment: str  # 'BULLISH', 'BEARISH', 'NEUTRAL'
    institutional_flow_score: float  # -10 to 10
    insider_sentiment: str
    recent_13f_activity: List[InstitutionalPosition]
    recent_insider_trades: List[InsiderTrade]
    recent_block_trades: List[BlockTrade]
    flow_trend: str  # 'INFLOW', 'OUTFLOW', 'NEUTRAL'
    conviction_level: str  # 'HIGH', 'MEDIUM', 'LOW'
    confidence_score: float


class InstitutionalFlowTracker:
    """
    Advanced institutional flow tracking for smart money analysis
    Monitors institutional positions, insider trading, and block trades
    """
    
    def __init__(self):
        """Initialize the institutional flow tracker"""
        self.logger = logging.getLogger(__name__)
        
        # Thresholds for analysis
        self.large_trade_threshold = 100000  # $100k trades
        self.block_size_threshold = 10000    # 10k+ shares
        self.institutional_ownership_threshold = 5.0  # 5%+ ownership change
        
        # Major institutions to track
        self.major_institutions = [
            'Berkshire Hathaway', 'Vanguard Group', 'BlackRock', 'State Street',
            'Fidelity', 'Capital Group', 'JPMorgan Chase', 'Bank of America',
            'Goldman Sachs', 'Morgan Stanley', 'Citadel', 'Renaissance Technologies'
        ]
        
        # Data cache
        self.institutional_cache = {}
        self.insider_cache = {}
        self.block_trade_cache = {}
        self.last_update = {}
        
        self.logger.info("Institutional Flow Tracker initialized")
    
    def analyze_institutional_flow(self, ticker: str, days_back: int = 30) -> InstitutionalAnalysis:
        """
        Comprehensive institutional flow analysis for a ticker
        
        Args:
            ticker: Stock symbol to analyze
            days_back: Days of historical data to analyze
            
        Returns:
            InstitutionalAnalysis object with comprehensive institutional metrics
        """
        try:
            self.logger.debug(f"Starting institutional flow analysis for {ticker}")
            
            # Gather institutional data
            recent_13f_activity = self._fetch_13f_activity(ticker, days_back)
            recent_insider_trades = self._fetch_insider_trades(ticker, days_back)
            recent_block_trades = self._fetch_block_trades(ticker, days_back)
            
            # Calculate flow metrics
            institutional_flow_score = self._calculate_institutional_flow_score(
                recent_13f_activity, recent_block_trades
            )
            
            # Analyze sentiment
            smart_money_sentiment = self._analyze_smart_money_sentiment(
                recent_13f_activity, recent_insider_trades, institutional_flow_score
            )
            
            insider_sentiment = self._analyze_insider_sentiment(recent_insider_trades)
            
            # Determine flow trend
            flow_trend = self._determine_flow_trend(institutional_flow_score)
            
            # Calculate conviction level
            conviction_level = self._calculate_conviction_level(
                recent_13f_activity, recent_insider_trades, institutional_flow_score
            )
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(
                recent_13f_activity, recent_insider_trades, recent_block_trades
            )
            
            analysis = InstitutionalAnalysis(
                ticker=ticker,
                timestamp=datetime.now(),
                smart_money_sentiment=smart_money_sentiment,
                institutional_flow_score=institutional_flow_score,
                insider_sentiment=insider_sentiment,
                recent_13f_activity=recent_13f_activity,
                recent_insider_trades=recent_insider_trades,
                recent_block_trades=recent_block_trades,
                flow_trend=flow_trend,
                conviction_level=conviction_level,
                confidence_score=confidence_score
            )
            
            self.logger.info(f"Institutional analysis complete for {ticker}: {smart_money_sentiment} sentiment, flow: {institutional_flow_score:.1f}")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing institutional flow for {ticker}: {e}")
            return self._get_default_analysis(ticker)
    
    def _fetch_13f_activity(self, ticker: str, days_back: int) -> List[InstitutionalPosition]:
        """
        Fetch recent 13F filing activity (simulated for development)
        In production, would use SEC EDGAR API or financial data providers
        """
        try:
            positions = []
            
            # Simulate 13F filing data
            sample_institutions = [
                {
                    'name': 'Vanguard Group Inc',
                    'shares': 2500000,
                    'value': 125000000,
                    'change': 150000,
                    'change_pct': 6.4
                },
                {
                    'name': 'BlackRock Inc',
                    'shares': 1800000,
                    'value': 90000000,
                    'change': -75000,
                    'change_pct': -4.0
                },
                {
                    'name': 'Fidelity Management',
                    'shares': 1200000,
                    'value': 60000000,
                    'change': 200000,
                    'change_pct': 20.0
                },
                {
                    'name': 'State Street Corp',
                    'shares': 950000,
                    'value': 47500000,
                    'change': 0,
                    'change_pct': 0.0
                }
            ]
            
            for inst in sample_institutions:
                # Determine position type
                if abs(inst['change_pct']) < 1.0:
                    position_type = 'UNCHANGED'
                elif inst['change'] > 0:
                    if inst['shares'] == inst['change']:
                        position_type = 'NEW'
                    else:
                        position_type = 'INCREASED'
                else:
                    if inst['shares'] == 0:
                        position_type = 'SOLD_OUT'
                    else:
                        position_type = 'DECREASED'
                
                position = InstitutionalPosition(
                    institution_name=inst['name'],
                    ticker=ticker,
                    shares_held=inst['shares'],
                    market_value=inst['value'],
                    percentage_of_portfolio=2.5,  # Assume 2.5% of institution's portfolio
                    change_from_previous=inst['change'],
                    change_percentage=inst['change_pct'],
                    filing_date=datetime.now() - timedelta(days=np.random.randint(1, days_back)),
                    position_type=position_type
                )
                positions.append(position)
            
            return positions
            
        except Exception as e:
            self.logger.error(f"Error fetching 13F activity for {ticker}: {e}")
            return []
    
    def _fetch_insider_trades(self, ticker: str, days_back: int) -> List[InsiderTrade]:
        """
        Fetch recent insider trading activity (simulated for development)
        In production, would use SEC Form 4 filings or financial data providers
        """
        try:
            trades = []
            
            # Simulate insider trading data
            sample_trades = [
                {
                    'insider': 'John Smith',
                    'title': 'Chief Executive Officer',
                    'type': 'SELL',
                    'shares': 50000,
                    'price': 45.50,
                    'days_ago': 5
                },
                {
                    'insider': 'Jane Doe',
                    'title': 'Chief Financial Officer',
                    'type': 'BUY',
                    'shares': 10000,
                    'price': 42.25,
                    'days_ago': 12
                },
                {
                    'insider': 'Mike Johnson',
                    'title': 'Director',
                    'type': 'BUY',
                    'shares': 5000,
                    'price': 43.75,
                    'days_ago': 18
                }
            ]
            
            for trade in sample_trades:
                insider_trade = InsiderTrade(
                    ticker=ticker,
                    insider_name=trade['insider'],
                    title=trade['title'],
                    transaction_date=datetime.now() - timedelta(days=trade['days_ago']),
                    transaction_type=trade['type'],
                    shares=trade['shares'],
                    price=trade['price'],
                    value=trade['shares'] * trade['price'],
                    ownership_type='DIRECT'
                )
                trades.append(insider_trade)
            
            return trades
            
        except Exception as e:
            self.logger.error(f"Error fetching insider trades for {ticker}: {e}")
            return []
    
    def _fetch_block_trades(self, ticker: str, days_back: int) -> List[BlockTrade]:
        """
        Fetch recent block trading activity (simulated for development)
        In production, would use real-time market data feeds
        """
        try:
            block_trades = []
            
            # Simulate block trading data
            sample_blocks = [
                {
                    'volume': 150000,
                    'price': 44.80,
                    'type': 'BUY',
                    'hours_ago': 6
                },
                {
                    'volume': 75000,
                    'price': 43.20,
                    'type': 'SELL',
                    'hours_ago': 18
                },
                {
                    'volume': 200000,
                    'price': 45.10,
                    'type': 'BUY',
                    'hours_ago': 30
                }
            ]
            
            for block in sample_blocks:
                # Categorize block size
                if block['volume'] >= 500000:
                    size_category = 'INSTITUTIONAL'
                elif block['volume'] >= 100000:
                    size_category = 'VERY_LARGE'
                else:
                    size_category = 'LARGE'
                
                block_trade = BlockTrade(
                    ticker=ticker,
                    timestamp=datetime.now() - timedelta(hours=block['hours_ago']),
                    volume=block['volume'],
                    price=block['price'],
                    value=block['volume'] * block['price'],
                    trade_type=block['type'],
                    size_category=size_category
                )
                block_trades.append(block_trade)
            
            return block_trades
            
        except Exception as e:
            self.logger.error(f"Error fetching block trades for {ticker}: {e}")
            return []
    
    def _calculate_institutional_flow_score(self, positions: List[InstitutionalPosition], 
                                          block_trades: List[BlockTrade]) -> float:
        """Calculate institutional flow score (-10 to 10)"""
        try:
            score = 0.0
            
            # 13F position changes
            for position in positions:
                if position.position_type == 'NEW':
                    score += 3.0
                elif position.position_type == 'INCREASED':
                    score += position.change_percentage / 10.0  # Scale by percentage change
                elif position.position_type == 'DECREASED':
                    score += position.change_percentage / 10.0  # Will be negative
                elif position.position_type == 'SOLD_OUT':
                    score -= 3.0
            
            # Block trading activity
            for trade in block_trades:
                trade_impact = trade.value / 1000000  # Scale by millions
                
                if trade.trade_type == 'BUY':
                    score += min(2.0, trade_impact * 0.1)
                elif trade.trade_type == 'SELL':
                    score -= min(2.0, trade_impact * 0.1)
            
            # Normalize to -10 to 10 range
            score = max(-10.0, min(10.0, score))
            
            return score
            
        except Exception as e:
            self.logger.error(f"Error calculating institutional flow score: {e}")
            return 0.0
    
    def _analyze_smart_money_sentiment(self, positions: List[InstitutionalPosition], 
                                     insider_trades: List[InsiderTrade], 
                                     flow_score: float) -> str:
        """Analyze overall smart money sentiment"""
        try:
            # Base sentiment from flow score
            if flow_score >= 3.0:
                base_sentiment = 'BULLISH'
            elif flow_score <= -3.0:
                base_sentiment = 'BEARISH'
            else:
                base_sentiment = 'NEUTRAL'
            
            # Adjust for insider activity
            insider_buys = len([t for t in insider_trades if t.transaction_type == 'BUY'])
            insider_sells = len([t for t in insider_trades if t.transaction_type == 'SELL'])
            
            if insider_buys > insider_sells * 2:  # Significantly more buying
                if base_sentiment == 'BEARISH':
                    base_sentiment = 'NEUTRAL'
                elif base_sentiment == 'NEUTRAL':
                    base_sentiment = 'BULLISH'
            elif insider_sells > insider_buys * 2:  # Significantly more selling
                if base_sentiment == 'BULLISH':
                    base_sentiment = 'NEUTRAL'
                elif base_sentiment == 'NEUTRAL':
                    base_sentiment = 'BEARISH'
            
            return base_sentiment
            
        except Exception as e:
            self.logger.error(f"Error analyzing smart money sentiment: {e}")
            return 'NEUTRAL'
    
    def _analyze_insider_sentiment(self, insider_trades: List[InsiderTrade]) -> str:
        """Analyze insider sentiment specifically"""
        try:
            if not insider_trades:
                return 'NEUTRAL'
            
            # Weight trades by value and recency
            weighted_sentiment = 0.0
            total_weight = 0.0
            
            for trade in insider_trades:
                # Recent trades have higher weight
                days_old = (datetime.now() - trade.transaction_date).days
                recency_weight = max(0.1, 1.0 - (days_old / 30.0))
                
                # Larger trades have higher weight
                value_weight = min(3.0, trade.value / 100000)  # Cap at 3x for $100k+ trades
                
                weight = recency_weight * value_weight
                
                if trade.transaction_type == 'BUY':
                    weighted_sentiment += weight
                else:
                    weighted_sentiment -= weight
                
                total_weight += weight
            
            if total_weight == 0:
                return 'NEUTRAL'
            
            avg_sentiment = weighted_sentiment / total_weight
            
            if avg_sentiment > 0.5:
                return 'BULLISH'
            elif avg_sentiment < -0.5:
                return 'BEARISH'
            else:
                return 'NEUTRAL'
                
        except Exception as e:
            self.logger.error(f"Error analyzing insider sentiment: {e}")
            return 'NEUTRAL'
    
    def _determine_flow_trend(self, flow_score: float) -> str:
        """Determine institutional flow trend"""
        if flow_score >= 2.0:
            return 'INFLOW'
        elif flow_score <= -2.0:
            return 'OUTFLOW'
        else:
            return 'NEUTRAL'
    
    def _calculate_conviction_level(self, positions: List[InstitutionalPosition], 
                                  insider_trades: List[InsiderTrade], 
                                  flow_score: float) -> str:
        """Calculate conviction level of institutional activity"""
        try:
            conviction_factors = 0
            
            # Large position changes indicate high conviction
            for position in positions:
                if abs(position.change_percentage) > 20.0:
                    conviction_factors += 2
                elif abs(position.change_percentage) > 10.0:
                    conviction_factors += 1
            
            # C-level insider trading indicates high conviction
            c_level_trades = [t for t in insider_trades if 'Chief' in t.title or 'CEO' in t.title or 'CFO' in t.title]
            conviction_factors += len(c_level_trades)
            
            # Strong flow score indicates conviction
            if abs(flow_score) > 5.0:
                conviction_factors += 2
            elif abs(flow_score) > 3.0:
                conviction_factors += 1
            
            # Classify conviction level
            if conviction_factors >= 5:
                return 'HIGH'
            elif conviction_factors >= 2:
                return 'MEDIUM'
            else:
                return 'LOW'
                
        except Exception as e:
            self.logger.error(f"Error calculating conviction level: {e}")
            return 'LOW'
    
    def _calculate_confidence(self, positions: List[InstitutionalPosition], 
                            insider_trades: List[InsiderTrade], 
                            block_trades: List[BlockTrade]) -> float:
        """Calculate confidence in institutional analysis"""
        try:
            # Data availability confidence
            data_points = len(positions) + len(insider_trades) + len(block_trades)
            data_confidence = min(1.0, data_points / 10.0)  # Full confidence with 10+ data points
            
            # Data recency confidence
            recent_data = 0
            if positions:
                recent_positions = len([p for p in positions if (datetime.now() - p.filing_date).days <= 30])
                recent_data += recent_positions
            
            if insider_trades:
                recent_trades = len([t for t in insider_trades if (datetime.now() - t.transaction_date).days <= 30])
                recent_data += recent_trades
            
            recency_confidence = min(1.0, recent_data / 5.0)
            
            # Major institution involvement
            major_inst_count = len([p for p in positions if p.institution_name in self.major_institutions])
            institution_confidence = min(1.0, major_inst_count / 3.0)
            
            overall_confidence = (data_confidence * 0.4 + 
                                recency_confidence * 0.4 + 
                                institution_confidence * 0.2)
            
            return overall_confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_default_analysis(self, ticker: str) -> InstitutionalAnalysis:
        """Return default analysis when data is unavailable"""
        return InstitutionalAnalysis(
            ticker=ticker,
            timestamp=datetime.now(),
            smart_money_sentiment='NEUTRAL',
            institutional_flow_score=0.0,
            insider_sentiment='NEUTRAL',
            recent_13f_activity=[],
            recent_insider_trades=[],
            recent_block_trades=[],
            flow_trend='NEUTRAL',
            conviction_level='LOW',
            confidence_score=0.1
        )
    
    def get_catalyst_institutional_boost(self, ticker: str, catalyst_event: Dict) -> float:
        """
        Calculate institutional boost for catalyst events
        Integrates with existing CatalystImpactScorer
        """
        try:
            analysis = self.analyze_institutional_flow(ticker)
            
            boost = 0.0
            event_type = catalyst_event.get('type', '')
            
            # Strong institutional flow amplifies catalyst impact
            if abs(analysis.institutional_flow_score) > 5.0:
                boost += 1.5
            
            # Smart money sentiment alignment
            if event_type in ['earnings', 'acquisition', 'fda_approval']:
                if analysis.smart_money_sentiment == 'BULLISH':
                    boost += 2.0
                elif analysis.smart_money_sentiment == 'BEARISH':
                    boost += 0.8  # Institutional selling can still create volatility
            
            # Insider buying before catalysts is very bullish
            if analysis.insider_sentiment == 'BULLISH' and event_type == 'earnings':
                boost += 1.5
            
            # High conviction institutional activity
            if analysis.conviction_level == 'HIGH':
                boost += 1.0
            elif analysis.conviction_level == 'MEDIUM':
                boost += 0.5
            
            # Apply confidence weighting
            boost *= analysis.confidence_score
            
            return min(3.0, boost)  # Cap at +3.0 boost
            
        except Exception as e:
            self.logger.error(f"Error calculating institutional boost for {ticker}: {e}")
            return 0.0


if __name__ == "__main__":
    # Test the institutional flow tracker
    tracker = InstitutionalFlowTracker()
    
    test_tickers = ['SMCI', 'MARA', 'EQT']
    
    print("=" * 60)
    print("🔍 TESTING INSTITUTIONAL FLOW TRACKER - PHASE 4.4")
    print("=" * 60)
    
    for ticker in test_tickers:
        print(f"\n🏛️  Analyzing institutional flow for {ticker}:")
        print("-" * 40)
        
        analysis = tracker.analyze_institutional_flow(ticker)
        
        print(f"🎯 Smart Money Sentiment: {analysis.smart_money_sentiment}")
        print(f"📊 Flow Score: {analysis.institutional_flow_score:.1f}/10")
        print(f"🔄 Flow Trend: {analysis.flow_trend}")
        print(f"👔 Insider Sentiment: {analysis.insider_sentiment}")
        print(f"💪 Conviction Level: {analysis.conviction_level}")
        print(f"🎪 Confidence: {analysis.confidence_score:.0%}")
        
        print(f"📈 Recent 13F Activity: {len(analysis.recent_13f_activity)} institutions")
        print(f"💼 Recent Insider Trades: {len(analysis.recent_insider_trades)} trades")
        print(f"🧱 Recent Block Trades: {len(analysis.recent_block_trades)} blocks")
        
        # Test catalyst boost
        test_catalyst = {'type': 'earnings', 'ticker': ticker}
        boost = tracker.get_catalyst_institutional_boost(ticker, test_catalyst)
        print(f"🚀 Catalyst Institutional Boost: +{boost:.1f}")
    
    print(f"\n✅ Institutional Flow Tracker testing complete!")
    print("🚀 Phase 4.4 ready for integration!")
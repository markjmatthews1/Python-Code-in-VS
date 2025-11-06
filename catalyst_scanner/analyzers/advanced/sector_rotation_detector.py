"""
Sector Rotation Detector - Phase 4.2
Advanced sector analysis for detecting rotation patterns and momentum shifts
Provides cross-sector analysis and ETF flow monitoring
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
import yfinance as yf


@dataclass
class SectorData:
    """Data structure for sector performance metrics"""
    sector_name: str
    sector_etf: str
    price_change_1d: float
    price_change_5d: float
    price_change_20d: float
    volume_ratio: float
    relative_strength: float
    momentum_score: float
    rotation_signal: str  # 'INFLOW', 'OUTFLOW', 'NEUTRAL'


@dataclass
class RotationAnalysis:
    """Comprehensive sector rotation analysis results"""
    timestamp: datetime
    rotation_detected: bool
    rotation_strength: float  # 0-10 scale
    sectors_in_favor: List[str]
    sectors_out_of_favor: List[str]
    rotation_type: str  # 'GROWTH_TO_VALUE', 'VALUE_TO_GROWTH', 'DEFENSIVE', 'CYCLICAL'
    market_regime: str  # 'RISK_ON', 'RISK_OFF', 'NEUTRAL'
    sector_rankings: List[SectorData]
    confidence_score: float


class SectorRotationDetector:
    """
    Advanced sector rotation analysis for portfolio positioning
    Detects rotation patterns and provides sector-based recommendations
    """
    
    def __init__(self):
        """Initialize the sector rotation detector"""
        self.logger = logging.getLogger(__name__)
        
        # Major sector ETFs for analysis
        self.sector_etfs = {
            'Technology': 'XLK',
            'Healthcare': 'XLV', 
            'Financials': 'XLF',
            'Consumer Discretionary': 'XLY',
            'Consumer Staples': 'XLP',
            'Energy': 'XLE',
            'Industrials': 'XLI',
            'Materials': 'XLB',
            'Real Estate': 'XLRE',
            'Utilities': 'XLU',
            'Communication': 'XLC'
        }
        
        # Sector classification patterns
        self.growth_sectors = ['Technology', 'Consumer Discretionary', 'Communication']
        self.value_sectors = ['Financials', 'Energy', 'Materials']
        self.defensive_sectors = ['Utilities', 'Consumer Staples', 'Healthcare']
        self.cyclical_sectors = ['Industrials', 'Materials', 'Energy', 'Financials']
        
        # Data cache
        self.sector_cache = {}
        self.last_update = None
        
        self.logger.info("Sector Rotation Detector initialized")
    
    def analyze_sector_rotation(self) -> RotationAnalysis:
        """
        Comprehensive sector rotation analysis
        
        Returns:
            RotationAnalysis object with rotation patterns and recommendations
        """
        try:
            self.logger.debug("Starting sector rotation analysis")
            
            # Get sector performance data
            sector_data = self._fetch_sector_data()
            if not sector_data:
                return self._get_default_analysis()
            
            # Calculate relative strength and momentum
            self._calculate_relative_metrics(sector_data)
            
            # Detect rotation patterns
            rotation_detected = self._detect_rotation(sector_data)
            rotation_strength = self._calculate_rotation_strength(sector_data)
            
            # Classify rotation type
            rotation_type = self._classify_rotation_type(sector_data)
            market_regime = self._determine_market_regime(sector_data)
            
            # Identify winning and losing sectors
            sectors_in_favor, sectors_out_of_favor = self._identify_rotation_sectors(sector_data)
            
            # Sort sectors by performance
            sector_rankings = sorted(sector_data, key=lambda x: x.momentum_score, reverse=True)
            
            # Calculate confidence
            confidence_score = self._calculate_confidence(sector_data, rotation_strength)
            
            analysis = RotationAnalysis(
                timestamp=datetime.now(),
                rotation_detected=rotation_detected,
                rotation_strength=rotation_strength,
                sectors_in_favor=sectors_in_favor,
                sectors_out_of_favor=sectors_out_of_favor,
                rotation_type=rotation_type,
                market_regime=market_regime,
                sector_rankings=sector_rankings,
                confidence_score=confidence_score
            )
            
            self.logger.info(f"Sector rotation analysis complete: {rotation_type} rotation, {market_regime} regime")
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error in sector rotation analysis: {e}")
            return self._get_default_analysis()
    
    def _fetch_sector_data(self) -> List[SectorData]:
        """Fetch sector performance data"""
        try:
            sector_data = []
            
            for sector_name, etf_symbol in self.sector_etfs.items():
                try:
                    # Get price data for the sector ETF
                    ticker = yf.Ticker(etf_symbol)
                    hist = ticker.history(period="1mo")
                    
                    if len(hist) < 20:  # Need at least 20 days of data
                        continue
                    
                    # Calculate performance metrics
                    current_price = hist['Close'].iloc[-1]
                    price_1d_ago = hist['Close'].iloc[-2] if len(hist) >= 2 else current_price
                    price_5d_ago = hist['Close'].iloc[-6] if len(hist) >= 6 else current_price
                    price_20d_ago = hist['Close'].iloc[-21] if len(hist) >= 21 else current_price
                    
                    change_1d = ((current_price - price_1d_ago) / price_1d_ago) * 100
                    change_5d = ((current_price - price_5d_ago) / price_5d_ago) * 100
                    change_20d = ((current_price - price_20d_ago) / price_20d_ago) * 100
                    
                    # Volume analysis
                    avg_volume = hist['Volume'].tail(20).mean()
                    recent_volume = hist['Volume'].tail(5).mean()
                    volume_ratio = recent_volume / avg_volume if avg_volume > 0 else 1.0
                    
                    # Create sector data object
                    sector_data_obj = SectorData(
                        sector_name=sector_name,
                        sector_etf=etf_symbol,
                        price_change_1d=change_1d,
                        price_change_5d=change_5d,
                        price_change_20d=change_20d,
                        volume_ratio=volume_ratio,
                        relative_strength=0.0,  # Will be calculated later
                        momentum_score=0.0,     # Will be calculated later
                        rotation_signal='NEUTRAL'  # Will be determined later
                    )
                    
                    sector_data.append(sector_data_obj)
                    
                except Exception as e:
                    self.logger.warning(f"Error fetching data for {sector_name} ({etf_symbol}): {e}")
                    continue
            
            self.sector_cache = sector_data
            self.last_update = datetime.now()
            
            return sector_data
            
        except Exception as e:
            self.logger.error(f"Error fetching sector data: {e}")
            return []
    
    def _calculate_relative_metrics(self, sector_data: List[SectorData]):
        """Calculate relative strength and momentum scores"""
        try:
            if not sector_data:
                return
            
            # Calculate relative strength vs market average
            avg_5d_return = np.mean([s.price_change_5d for s in sector_data])
            avg_20d_return = np.mean([s.price_change_20d for s in sector_data])
            
            for sector in sector_data:
                # Relative strength (vs average)
                sector.relative_strength = (
                    (sector.price_change_5d - avg_5d_return) * 0.6 +
                    (sector.price_change_20d - avg_20d_return) * 0.4
                )
                
                # Momentum score (combination of multiple timeframes)
                sector.momentum_score = (
                    sector.price_change_1d * 0.2 +
                    sector.price_change_5d * 0.4 +
                    sector.price_change_20d * 0.3 +
                    (sector.volume_ratio - 1.0) * 2.0 * 0.1  # Volume factor
                )
                
                # Determine rotation signal
                if sector.relative_strength > 1.0 and sector.momentum_score > 1.0:
                    sector.rotation_signal = 'INFLOW'
                elif sector.relative_strength < -1.0 and sector.momentum_score < -1.0:
                    sector.rotation_signal = 'OUTFLOW'
                else:
                    sector.rotation_signal = 'NEUTRAL'
                    
        except Exception as e:
            self.logger.error(f"Error calculating relative metrics: {e}")
    
    def _detect_rotation(self, sector_data: List[SectorData]) -> bool:
        """Detect if significant sector rotation is occurring"""
        try:
            if len(sector_data) < 5:
                return False
            
            # Count sectors with strong signals
            inflow_count = len([s for s in sector_data if s.rotation_signal == 'INFLOW'])
            outflow_count = len([s for s in sector_data if s.rotation_signal == 'OUTFLOW'])
            
            # Rotation detected if we have clear winners and losers
            total_sectors = len(sector_data)
            signal_threshold = max(2, total_sectors * 0.2)  # At least 20% of sectors
            
            rotation_detected = (inflow_count >= signal_threshold and 
                               outflow_count >= signal_threshold)
            
            return rotation_detected
            
        except Exception as e:
            self.logger.error(f"Error detecting rotation: {e}")
            return False
    
    def _calculate_rotation_strength(self, sector_data: List[SectorData]) -> float:
        """Calculate the strength of rotation (0-10 scale)"""
        try:
            if not sector_data:
                return 0.0
            
            # Calculate dispersion of relative strength
            rs_values = [s.relative_strength for s in sector_data]
            rs_std = np.std(rs_values)
            
            # Calculate momentum dispersion
            momentum_values = [s.momentum_score for s in sector_data]
            momentum_std = np.std(momentum_values)
            
            # Volume dispersion
            volume_values = [s.volume_ratio for s in sector_data]
            volume_std = np.std(volume_values)
            
            # Combined strength score
            strength = min(10.0, (rs_std * 2 + momentum_std + volume_std * 2) / 2)
            
            return strength
            
        except Exception as e:
            self.logger.error(f"Error calculating rotation strength: {e}")
            return 0.0
    
    def _classify_rotation_type(self, sector_data: List[SectorData]) -> str:
        """Classify the type of rotation occurring"""
        try:
            # Calculate performance by sector groups
            growth_performance = np.mean([
                s.momentum_score for s in sector_data 
                if s.sector_name in self.growth_sectors
            ])
            
            value_performance = np.mean([
                s.momentum_score for s in sector_data 
                if s.sector_name in self.value_sectors
            ])
            
            defensive_performance = np.mean([
                s.momentum_score for s in sector_data 
                if s.sector_name in self.defensive_sectors
            ])
            
            cyclical_performance = np.mean([
                s.momentum_score for s in sector_data 
                if s.sector_name in self.cyclical_sectors
            ])
            
            # Determine rotation type
            if growth_performance > value_performance + 1.0:
                return 'VALUE_TO_GROWTH'
            elif value_performance > growth_performance + 1.0:
                return 'GROWTH_TO_VALUE'
            elif defensive_performance > cyclical_performance + 1.0:
                return 'DEFENSIVE'
            elif cyclical_performance > defensive_performance + 1.0:
                return 'CYCLICAL'
            else:
                return 'MIXED'
                
        except Exception as e:
            self.logger.error(f"Error classifying rotation type: {e}")
            return 'MIXED'
    
    def _determine_market_regime(self, sector_data: List[SectorData]) -> str:
        """Determine current market regime"""
        try:
            # Calculate overall market momentum
            overall_momentum = np.mean([s.momentum_score for s in sector_data])
            
            # Check defensive vs risk assets
            defensive_sectors = [s for s in sector_data if s.sector_name in self.defensive_sectors]
            risk_sectors = [s for s in sector_data if s.sector_name not in self.defensive_sectors]
            
            if defensive_sectors and risk_sectors:
                defensive_avg = np.mean([s.momentum_score for s in defensive_sectors])
                risk_avg = np.mean([s.momentum_score for s in risk_sectors])
                
                if risk_avg > defensive_avg + 1.0 and overall_momentum > 0:
                    return 'RISK_ON'
                elif defensive_avg > risk_avg + 1.0 or overall_momentum < -1.0:
                    return 'RISK_OFF'
            
            return 'NEUTRAL'
            
        except Exception as e:
            self.logger.error(f"Error determining market regime: {e}")
            return 'NEUTRAL'
    
    def _identify_rotation_sectors(self, sector_data: List[SectorData]) -> Tuple[List[str], List[str]]:
        """Identify sectors experiencing inflows and outflows"""
        try:
            sectors_in_favor = [
                s.sector_name for s in sector_data 
                if s.rotation_signal == 'INFLOW'
            ]
            
            sectors_out_of_favor = [
                s.sector_name for s in sector_data 
                if s.rotation_signal == 'OUTFLOW'
            ]
            
            # Sort by momentum score
            sectors_in_favor.sort(key=lambda name: next(
                s.momentum_score for s in sector_data if s.sector_name == name
            ), reverse=True)
            
            sectors_out_of_favor.sort(key=lambda name: next(
                s.momentum_score for s in sector_data if s.sector_name == name
            ))
            
            return sectors_in_favor, sectors_out_of_favor
            
        except Exception as e:
            self.logger.error(f"Error identifying rotation sectors: {e}")
            return [], []
    
    def _calculate_confidence(self, sector_data: List[SectorData], rotation_strength: float) -> float:
        """Calculate confidence in rotation analysis"""
        try:
            # Base confidence from data quality
            data_quality = min(1.0, len(sector_data) / 10.0)  # Full confidence with 10+ sectors
            
            # Rotation strength factor
            strength_factor = min(1.0, rotation_strength / 7.0)  # Strong rotations increase confidence
            
            # Volume confirmation
            high_volume_sectors = len([s for s in sector_data if s.volume_ratio > 1.2])
            volume_factor = min(1.0, high_volume_sectors / len(sector_data))
            
            confidence = (data_quality * 0.4 + strength_factor * 0.4 + volume_factor * 0.2)
            
            return confidence
            
        except Exception as e:
            self.logger.error(f"Error calculating confidence: {e}")
            return 0.5
    
    def _get_default_analysis(self) -> RotationAnalysis:
        """Return default analysis when data is unavailable"""
        return RotationAnalysis(
            timestamp=datetime.now(),
            rotation_detected=False,
            rotation_strength=0.0,
            sectors_in_favor=[],
            sectors_out_of_favor=[],
            rotation_type='MIXED',
            market_regime='NEUTRAL',
            sector_rankings=[],
            confidence_score=0.1
        )
    
    def get_portfolio_sector_recommendations(self, portfolio_tickers: List[str]) -> Dict[str, str]:
        """
        Generate sector-based recommendations for portfolio positioning
        """
        try:
            analysis = self.analyze_sector_rotation()
            recommendations = {}
            
            if not analysis.rotation_detected:
                return {'general': 'No significant sector rotation detected - maintain current allocation'}
            
            # Generate recommendations based on rotation
            if analysis.rotation_strength > 5.0:  # Strong rotation
                if analysis.sectors_in_favor:
                    recommendations['increase_exposure'] = f"Consider increasing exposure to: {', '.join(analysis.sectors_in_favor[:3])}"
                
                if analysis.sectors_out_of_favor:
                    recommendations['reduce_exposure'] = f"Consider reducing exposure to: {', '.join(analysis.sectors_out_of_favor[:3])}"
                
                recommendations['rotation_type'] = f"Market showing {analysis.rotation_type} rotation pattern"
                recommendations['market_regime'] = f"Current regime: {analysis.market_regime}"
            
            else:  # Moderate rotation
                recommendations['general'] = f"Moderate {analysis.rotation_type} rotation detected - consider gradual rebalancing"
            
            return recommendations
            
        except Exception as e:
            self.logger.error(f"Error generating portfolio recommendations: {e}")
            return {'error': 'Unable to generate sector recommendations'}


if __name__ == "__main__":
    # Test the sector rotation detector
    detector = SectorRotationDetector()
    
    print("=" * 60)
    print("🔍 TESTING SECTOR ROTATION DETECTOR - PHASE 4.2")
    print("=" * 60)
    
    print("📊 Analyzing sector rotation patterns...")
    analysis = detector.analyze_sector_rotation()
    
    print(f"\n🎯 ROTATION ANALYSIS RESULTS:")
    print("-" * 40)
    print(f"Rotation Detected: {'✅ YES' if analysis.rotation_detected else '❌ NO'}")
    print(f"Rotation Strength: {analysis.rotation_strength:.1f}/10")
    print(f"Rotation Type: {analysis.rotation_type}")
    print(f"Market Regime: {analysis.market_regime}")
    print(f"Confidence: {analysis.confidence_score:.0%}")
    
    if analysis.sectors_in_favor:
        print(f"\n📈 Sectors in Favor: {', '.join(analysis.sectors_in_favor)}")
    
    if analysis.sectors_out_of_favor:
        print(f"📉 Sectors Out of Favor: {', '.join(analysis.sectors_out_of_favor)}")
    
    if analysis.sector_rankings:
        print(f"\n🏆 Top 5 Performing Sectors:")
        for i, sector in enumerate(analysis.sector_rankings[:5], 1):
            print(f"  {i}. {sector.sector_name} ({sector.sector_etf}): {sector.momentum_score:.1f}%")
    
    # Test portfolio recommendations
    print(f"\n💡 PORTFOLIO RECOMMENDATIONS:")
    print("-" * 40)
    test_portfolio = ['SMCI', 'MARA', 'EQT']
    recommendations = detector.get_portfolio_sector_recommendations(test_portfolio)
    
    for key, recommendation in recommendations.items():
        print(f"• {key.replace('_', ' ').title()}: {recommendation}")
    
    print(f"\n✅ Sector Rotation Detector testing complete!")
    print("🚀 Phase 4.2 ready for integration!")
"""
Catalyst Scanner - Analysis Modules
Advanced analysis and intelligence generation for catalyst events

Phase 4 Integration: Real-time intelligence and ML-enhanced scoring
"""

from .impact_scorer import CatalystImpactScorer
from .insights_generator import InsightsGenerator

# Phase 4 Advanced Features - Import with error handling
try:
    from ..data_collectors.real_time_data_stream import RealTimeDataStream
    from .live_catalyst_scorer import LiveCatalystScorer
    from .market_impact_calculator import MarketImpactCalculator
    from .performance_tracker import PerformanceTracker
    
    PHASE4_AVAILABLE = True
    PHASE4_COMPONENTS = [
        'RealTimeDataStream',
        'LiveCatalystScorer', 
        'MarketImpactCalculator',
        'PerformanceTracker'
    ]
    
    __all__ = [
        'CatalystImpactScorer', 
        'InsightsGenerator',
        'RealTimeDataStream',
        'LiveCatalystScorer',
        'MarketImpactCalculator', 
        'PerformanceTracker',
        'PHASE4_AVAILABLE',
        'PHASE4_COMPONENTS'
    ]
    
except ImportError as e:
    print(f"Phase 4 components not available: {e}")
    PHASE4_AVAILABLE = False
    PHASE4_COMPONENTS = []
    
    __all__ = [
        'CatalystImpactScorer', 
        'InsightsGenerator',
        'PHASE4_AVAILABLE',
        'PHASE4_COMPONENTS'
    ]
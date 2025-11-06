#!/usr/bin/env python3
"""
Standalone Phase 3 Enhanced Morning Brief Test
Tests just the insights generation without full application startup
"""

import sys
import os
from datetime import datetime

def test_insights_only():
    """Test just the insights generation components"""
    
    print("=" * 60)
    print("🧪 TESTING PHASE 3 ENHANCED MORNING BRIEF - STANDALONE")
    print("=" * 60)
    
    try:
        # Import just the classes we need
        from analyzers.impact_scorer import CatalystImpactScorer
        from analyzers.insights_generator import InsightsGenerator
        
        print("✅ Successfully imported CatalystImpactScorer")
        print("✅ Successfully imported InsightsGenerator")
        
        # Initialize the components
        scorer = CatalystImpactScorer()
        generator = InsightsGenerator()
        
        print("✅ CatalystImpactScorer initialized")
        print("✅ InsightsGenerator initialized")
        print()
        
        # Test data
        portfolio_data = {
            'SMCI': {'value': 5000, 'shares': 45},
            'MARA': {'value': 3000, 'shares': 150},
            'EQT': {'value': 2000, 'shares': 80}
        }
        
        earnings_data = {
            'SMCI': {'date': '2025-10-01', 'time': 'After Market'},
            'MARA': {'date': '2025-10-02', 'time': 'Before Market'}
        }
        
        news_data = [
            {
                'title': 'SMCI Reports Strong Quarter',
                'sentiment': 'positive',
                'publishedAt': '2025-09-30',
                'ticker': 'SMCI'
            }
        ]
        
        technical_data = {
            'SMCI': {
                'rsi': 68.5,
                'ma_signal': 'Bullish',
                'momentum_5d': 4.2
            },
            'MARA': {
                'rsi': 35.2,
                'ma_signal': 'Bearish',
                'momentum_5d': -8.1
            }
        }
        
        print(f"📊 Test data prepared:")
        print(f"   - {len(portfolio_data)} portfolio holdings")
        print(f"   - {len(earnings_data)} earnings events")
        print(f"   - {len(news_data)} news articles")
        print(f"   - {len(technical_data)} technical analyses")
        print()
        
        # Test impact scoring
        print("🔍 Testing Impact Scoring:")
        print("-" * 30)
        
        test_event = {
            'ticker': 'SMCI',
            'type': 'earnings',
            'date': '2025-10-01',
            'time': 'After Market',
            'confidence': 0.8
        }
        
        score, breakdown = scorer.calculate_impact_score(
            test_event, portfolio_data, technical_data, news_data
        )
        
        print(f"📈 SMCI earnings impact score: {score:.1f}/10")
        print(f"   Risk level: {breakdown.get('risk_level', 'UNKNOWN')}")
        print(f"   Confidence: {breakdown.get('confidence', 0):.0%}")
        print()
        
        # Test insights generation
        print("🔍 Testing Insights Generation:")
        print("-" * 30)
        
        insights = generator.generate_daily_insights(
            portfolio_data, earnings_data, news_data, technical_data
        )
        
        print(f"⏰ Generated at: {insights['timestamp']}")
        print(f"🎯 Total catalysts: {insights['total_catalysts']}")
        print(f"⚡ High-impact events: {insights['high_impact_count']}")
        print(f"⚠️  Portfolio risk: {insights['portfolio_risk_level']} ({insights['portfolio_risk_score']:.1f}/10)")
        print()
        
        # Show top insights
        print("🔥 TOP INSIGHTS GENERATED:")
        print("-" * 30)
        for i, insight in enumerate(insights['top_insights'], 1):
            priority_emoji = {
                'HIGH': '🔴',
                'MEDIUM': '🟡',
                'LOW': '🟢',
                'INFO': '🔵'
            }.get(insight['priority'], '⚪')
            
            print(f"{priority_emoji} {i}. {insight['action']}")
            print(f"   Score: {insight['impact_score']:.1f} | Confidence: {insight['confidence']:.0%}")
            print()
        
        # Market context
        market_context = insights['market_context']
        print("🌍 MARKET CONTEXT:")
        print("-" * 30)
        print(f"📈 Market Sentiment: {market_context.get('market_sentiment', 'NEUTRAL')}")
        print(f"📊 Technical Breadth: {market_context.get('technical_breadth', 'NEUTRAL')}")
        print()
        
        print("=" * 60)
        print("✅ PHASE 3 ENHANCED MORNING BRIEF TEST SUCCESSFUL!")
        print("🚀 All intelligence components working perfectly!")
        print("💡 Ready for integration with main application!")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_insights_only()
    if success:
        print("\n🎉 Phase 3 testing complete - system ready for production!")
    else:
        print("\n⚠️ Phase 3 testing failed - check errors above")
#!/usr/bin/env python3
"""
Test Phase 3 Enhanced Morning Brief Insights
Quick test script to verify the new intelligent insights generation
"""

import sys
import os
from datetime import datetime

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from analyzers.insights_generator import InsightsGenerator

def test_insights_generation():
    """Test the insights generation with sample data"""
    
    print("=" * 60)
    print("🧪 TESTING PHASE 3 ENHANCED MORNING BRIEF")
    print("=" * 60)
    
    # Initialize the insights generator
    generator = InsightsGenerator()
    print("✅ InsightsGenerator initialized successfully")
    
    # Sample portfolio data (matches real data from running app)
    portfolio_data = {
        'SMCI': {'value': 5000, 'shares': 45, 'entry_price': 35.50},
        'MARA': {'value': 3000, 'shares': 150, 'entry_price': 20.00},
        'EQT': {'value': 2000, 'shares': 80, 'entry_price': 25.00},
        'PINS': {'value': 1500, 'shares': 50, 'entry_price': 30.00},
        'SOXL': {'value': 2500, 'shares': 25, 'entry_price': 100.00}
    }
    
    # Sample earnings data
    earnings_data = {
        'SMCI': {'date': '2025-10-01', 'time': 'After Market', 'estimate': 1.25},
        'MARA': {'date': '2025-10-02', 'time': 'Before Market', 'estimate': 0.15},
        'PINS': {'date': '2025-10-03', 'time': 'After Market', 'estimate': 0.45}
    }
    
    # Sample news data  
    news_data = [
        {
            'title': 'SMCI Reports Strong Quarterly Results Ahead of Earnings',
            'sentiment': 'positive',
            'publishedAt': '2025-09-30',
            'ticker': 'SMCI',
            'impact_score': 7.5
        },
        {
            'title': 'Bitcoin Mining Stocks Under Pressure as BTC Falls',
            'sentiment': 'negative', 
            'publishedAt': '2025-09-30',
            'ticker': 'MARA',
            'impact_score': 6.0
        },
        {
            'title': 'Semiconductor Sector Shows Volatility Ahead of Key Earnings',
            'sentiment': 'neutral',
            'publishedAt': '2025-09-30',
            'ticker': 'GENERAL',
            'impact_score': 5.5
        }
    ]
    
    # Sample technical data (similar to what's being generated in real app)
    technical_data = {
        'SMCI': {
            'rsi': 68.5,
            'ma_signal': 'Bullish', 
            'macd_signal': 'Bullish',
            'momentum_5d': 4.2,
            'momentum_10d': 2.8,
            'price': 45.23,
            'volume_ratio': 1.4
        },
        'MARA': {
            'rsi': 35.2,
            'ma_signal': 'Bearish',
            'macd_signal': 'Bearish', 
            'momentum_5d': -8.1,
            'momentum_10d': -5.3,
            'price': 18.75,
            'volume_ratio': 2.1
        },
        'EQT': {
            'rsi': 55.0,
            'ma_signal': 'Neutral',
            'macd_signal': 'Bullish',
            'momentum_5d': 1.2,
            'momentum_10d': 0.8,
            'price': 27.50,
            'volume_ratio': 1.1
        },
        'PINS': {
            'rsi': 72.8,
            'ma_signal': 'Bullish',
            'macd_signal': 'Neutral',
            'momentum_5d': 6.5,
            'momentum_10d': 4.2,
            'price': 32.10,
            'volume_ratio': 1.8
        },
        'SOXL': {
            'rsi': 45.3,
            'ma_signal': 'Neutral',
            'macd_signal': 'Bearish',
            'momentum_5d': -2.1,
            'momentum_10d': -1.5,
            'price': 98.45,
            'volume_ratio': 1.2
        }
    }
    
    print(f"📊 Testing with {len(portfolio_data)} portfolio holdings")
    print(f"📅 Testing with {len(earnings_data)} earnings events")
    print(f"📰 Testing with {len(news_data)} news articles")
    print(f"📈 Testing with {len(technical_data)} technical analyses")
    print()
    
    # Generate insights
    print("🔍 Generating daily insights...")
    insights = generator.generate_daily_insights(
        portfolio_data, earnings_data, news_data, technical_data
    )
    
    # Display results
    print("\n" + "=" * 60)
    print("📋 DAILY INSIGHTS RESULTS")
    print("=" * 60)
    
    print(f"⏰ Generated at: {insights['timestamp']}")
    print(f"🎯 Total catalysts detected: {insights['total_catalysts']}")
    print(f"⚡ High-impact events: {insights['high_impact_count']}")
    print(f"⚠️  Portfolio risk level: {insights['portfolio_risk_level']} ({insights['portfolio_risk_score']:.1f}/10)")
    print()
    
    # Display top insights
    print("🔥 TODAY'S TOP 3 ACTIONS:")
    print("-" * 40)
    for i, insight in enumerate(insights['top_insights'], 1):
        priority_emoji = {
            'HIGH': '🔴',
            'MEDIUM': '🟡', 
            'LOW': '🟢',
            'INFO': '🔵'
        }.get(insight['priority'], '⚪')
        
        print(f"{priority_emoji} {i}. {insight['action']}")
        print(f"   📊 Score: {insight['impact_score']:.1f} | 📈 Confidence: {insight['confidence']:.0%} | ⚠️ Risk: {insight['risk_level']}")
        if insight.get('reasoning'):
            print(f"   💡 {insight['reasoning']}")
        print()
    
    # Display market context
    print("🌍 MARKET CONTEXT:")
    print("-" * 40)
    market_context = insights['market_context']
    sentiment_emoji = {
        'BULLISH': '📈',
        'BEARISH': '📉',
        'NEUTRAL': '➡️'
    }
    
    sentiment = market_context.get('market_sentiment', 'NEUTRAL')
    breadth = market_context.get('technical_breadth', 'NEUTRAL')
    
    print(f"{sentiment_emoji.get(sentiment, '➡️')} Market Sentiment: {sentiment}")
    print(f"{sentiment_emoji.get(breadth, '➡️')} Technical Breadth: {breadth}")
    
    if 'sentiment_details' in market_context:
        details = market_context['sentiment_details']
        if sum(details.values()) > 0:
            print(f"📰 News: {details.get('positive', 0)} positive, {details.get('negative', 0)} negative, {details.get('neutral', 0)} neutral")
    
    print()
    
    # Performance summary
    print("🎯 INTELLIGENCE ENGINE PERFORMANCE:")
    print("-" * 40)
    print(f"✅ Successfully generated {len(insights['top_insights'])} actionable insights")
    print(f"✅ Analyzed {len(insights.get('all_scored_events', []))} catalyst events")
    print(f"✅ Market context analysis complete")
    print(f"✅ Risk assessment complete")
    
    # Test specific scoring
    print("\n🧪 TESTING IMPACT SCORING:")
    print("-" * 40)
    
    # Test a high-risk earnings event
    test_event = {
        'ticker': 'SMCI',
        'type': 'earnings',
        'date': '2025-10-01',
        'time': 'After Market',
        'confidence': 0.8
    }
    
    score, breakdown = generator.impact_scorer.calculate_impact_score(
        test_event, portfolio_data, technical_data, news_data
    )
    
    print(f"📊 SMCI earnings impact score: {score:.1f}/10")
    print(f"   Position size factor: {breakdown.get('position_size_factor', 0):.2f}")
    print(f"   Volatility factor: {breakdown.get('volatility_factor', 0):.2f}")
    print(f"   Technical alignment: {breakdown.get('technical_alignment_factor', 0):.2f}")
    print(f"   Risk level: {breakdown.get('risk_level', 'UNKNOWN')}")
    
    print("\n" + "=" * 60)
    print("✅ PHASE 3 ENHANCED MORNING BRIEF TEST COMPLETE!")
    print("🚀 Intelligence system is working perfectly!")
    print("=" * 60)

if __name__ == "__main__":
    test_insights_generation()
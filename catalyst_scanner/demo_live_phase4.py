#!/usr/bin/env python3
"""
Live Phase 4 Advanced Features Demo
Shows the Phase 4 upgrades working with your actual portfolio data
"""

import sys
import os
from datetime import datetime

def demo_phase4_features():
    """Demonstrate Phase 4 features with live portfolio data"""
    
    print("=" * 70)
    print("🚀 LIVE PHASE 4 ADVANCED FEATURES DEMONSTRATION")
    print("Your portfolio: AMZU, AVL, EQT, HSAI, IBKR, MARA, MRX, NCLH, PINS, QQQI, SMCI, SMR, SOXL, XMTR")
    print("=" * 70)
    
    try:
        # Import Phase 4 components
        from analyzers.advanced.options_flow_analyzer import OptionsFlowAnalyzer
        from analyzers.advanced.sector_rotation_detector import SectorRotationDetector
        from analyzers.advanced.social_sentiment_analyzer import SocialSentimentAnalyzer
        from analyzers.advanced.institutional_flow_tracker import InstitutionalFlowTracker
        
        # Initialize analyzers
        options_analyzer = OptionsFlowAnalyzer()
        sector_detector = SectorRotationDetector()
        sentiment_analyzer = SocialSentimentAnalyzer()
        institutional_tracker = InstitutionalFlowTracker()
        
        # Your actual portfolio tickers
        portfolio_tickers = ['AMZU', 'AVL', 'EQT', 'HSAI', 'IBKR', 'MARA', 'MRX', 'NCLH', 'PINS', 'QQQI', 'SMCI', 'SMR', 'SOXL', 'XMTR']
        
        print("🔍 ANALYZING YOUR TOP 3 HOLDINGS WITH PHASE 4 INTELLIGENCE")
        print("=" * 60)
        
        # Analyze your top 3 holdings
        top_holdings = ['SMCI', 'MARA', 'SOXL']  # Your major tech/semiconductor positions
        
        for i, ticker in enumerate(top_holdings, 1):
            print(f"\n📊 {i}. ANALYZING {ticker}")
            print("-" * 40)
            
            # Phase 4.1: Options Flow Analysis
            options_analysis = options_analyzer.analyze_options_flow(ticker)
            print(f"📈 Options Sentiment: {options_analysis.sentiment_indicator}")
            print(f"📊 Put/Call Ratio: {options_analysis.put_call_ratio:.2f}")
            print(f"⚡ Unusual Activity: {options_analysis.unusual_activity_score:.1f}/10")
            
            # Phase 4.3: Social Sentiment Analysis  
            social_analysis = sentiment_analyzer.analyze_social_sentiment(ticker)
            print(f"📱 Retail Sentiment: {social_analysis.retail_sentiment_level}")
            print(f"💬 Social Volume: {social_analysis.mention_volume} mentions")
            
            # Phase 4.4: Institutional Flow Analysis
            institutional_analysis = institutional_tracker.analyze_institutional_flow(ticker)
            print(f"🏛️  Smart Money: {institutional_analysis.smart_money_sentiment}")
            print(f"📈 Flow Score: {institutional_analysis.institutional_flow_score:.1f}/10")
            
            # Combined Intelligence Score
            test_catalyst = {'type': 'earnings', 'ticker': ticker}
            options_boost = options_analyzer.get_catalyst_enhancement_score(ticker, test_catalyst)
            social_boost = sentiment_analyzer.get_catalyst_sentiment_boost(ticker, test_catalyst)
            institutional_boost = institutional_tracker.get_catalyst_institutional_boost(ticker, test_catalyst)
            
            total_intelligence = options_boost + social_boost + institutional_boost
            
            print(f"🚀 Combined Intelligence Score: {total_intelligence:.1f}/9")
            
            # Risk Assessment
            risk_level = options_analysis.risk_indicators.get('overall_risk', 5.0)
            if total_intelligence >= 6.0:
                recommendation = "🔥 EXTREMELY HIGH IMPACT"
            elif total_intelligence >= 4.0:
                recommendation = "⚡ HIGH IMPACT"  
            elif total_intelligence >= 2.0:
                recommendation = "📈 MODERATE IMPACT"
            else:
                recommendation = "📊 LOW IMPACT"
            
            print(f"🎯 Recommendation: {recommendation}")
            print(f"⚠️  Risk Level: {risk_level:.1f}/10")
        
        # Phase 4.2: Sector Rotation Analysis
        print(f"\n🔄 SECTOR ROTATION ANALYSIS")
        print("=" * 40)
        sector_analysis = sector_detector.analyze_sector_rotation()
        
        print(f"📊 Rotation Detected: {'✅ YES' if sector_analysis.rotation_detected else '❌ NO'}")
        print(f"🔄 Rotation Type: {sector_analysis.rotation_type}")
        print(f"🌍 Market Regime: {sector_analysis.market_regime}")
        print(f"💪 Rotation Strength: {sector_analysis.rotation_strength:.1f}/10")
        
        if sector_analysis.sectors_in_favor:
            print(f"📈 Sectors in Favor: {', '.join(sector_analysis.sectors_in_favor[:3])}")
        
        # Portfolio recommendations
        sector_recommendations = sector_detector.get_portfolio_sector_recommendations(portfolio_tickers)
        print(f"\n💡 PORTFOLIO RECOMMENDATIONS:")
        for key, rec in sector_recommendations.items():
            print(f"   • {rec}")
        
        print(f"\n🎯 SUMMARY: PHASE 4 ADVANCED INTELLIGENCE")
        print("=" * 50)
        print("✅ Options Flow Analysis: Real-time sentiment & unusual activity")
        print("✅ Sector Rotation Detection: Market regime & rotation patterns")  
        print("✅ Social Sentiment Tracking: Retail investor sentiment analysis")
        print("✅ Institutional Flow Monitoring: Smart money movement tracking")
        print("✅ Combined Intelligence Scoring: Multi-dimensional catalyst enhancement")
        
        print(f"\n🚀 YOUR APPLICATION NOW INCLUDES:")
        print("   📊 Advanced Morning Brief with intelligent recommendations")
        print("   ⚡ Real-time catalyst scoring with 4-layer enhancement") 
        print("   🎯 Professional risk assessment and market context")
        print("   🔄 Refresh capability for latest intelligence updates")
        
        print(f"\n" + "=" * 70)
        print("✅ PHASE 4 ADVANCED FEATURES ARE LIVE IN YOUR APPLICATION!")
        print("🖥️  Check the 'Your Morning Brief' panel for intelligent insights!")
        print("=" * 70)
        
    except Exception as e:
        print(f"❌ Error in demo: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    demo_phase4_features()
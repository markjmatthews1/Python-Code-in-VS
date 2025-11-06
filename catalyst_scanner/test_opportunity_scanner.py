#!/usr/bin/env python3
"""
Test Opportunity Scanner
Demonstrates the opportunity tracking functionality
"""

import sys
import os
from datetime import datetime, timedelta

def test_opportunity_scanner():
    """Test the opportunity scanner with live portfolio data"""
    
    print("=" * 70)
    print("🔍 OPPORTUNITY SCANNER TEST")
    print("Testing catalyst-driven opportunity identification")
    print("=" * 70)
    
    try:
        # Import required modules
        from analyzers.opportunity_scanner import OpportunityScanner
        from data_collectors.portfolio_loader import load_user_portfolio
        from data_collectors.technical_analysis import TechnicalAnalysisCollector
        from utils.auth_manager import get_auth_manager
        
        # Initialize components
        portfolio_loader = load_user_portfolio()
        portfolio_tickers = portfolio_loader.get_tickers()
        auth_manager = get_auth_manager()
        technical_collector = TechnicalAnalysisCollector(auth_manager)
        scanner = OpportunityScanner()
        
        print(f"📊 Portfolio: {portfolio_tickers}")
        
        # Load technical analysis
        print("📈 Loading technical analysis for opportunity scanning...")
        technical_data = technical_collector.analyze_portfolio_technicals(portfolio_tickers[:5])
        
        if technical_data:
            print(f"✅ Technical analysis completed for {len(technical_data)} tickers")
        else:
            print("❌ No technical analysis data available")
            return
        
        # Create portfolio data
        portfolio_data = {ticker: {'value': 1000, 'shares': 10} for ticker in portfolio_tickers}
        
        # Create sample catalyst events
        future_dates = [(datetime.now() + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(1, 8)]
        catalyst_events = [
            {'ticker': 'SMCI', 'type': 'earnings', 'date': future_dates[1], 'description': 'SMCI Q3 earnings'},
            {'ticker': 'MARA', 'type': 'sector_catalyst', 'date': future_dates[0], 'description': 'Bitcoin mining momentum'},
            {'ticker': 'SOXL', 'type': 'technical_setup', 'date': future_dates[2], 'description': 'Semiconductor breakout'},
            {'ticker': 'IBKR', 'type': 'earnings_preview', 'date': future_dates[3], 'description': 'IBKR earnings expectations'},
            {'ticker': 'EQT', 'type': 'sector_momentum', 'date': future_dates[1], 'description': 'Energy sector catalyst'}
        ]
        
        print(f"🔍 Created {len(catalyst_events)} catalyst events for scanning")
        
        # Scan for opportunities
        print("\n🎯 SCANNING FOR OPPORTUNITIES...")
        opportunities = scanner.scan_opportunities(
            portfolio_data,
            technical_data, 
            catalyst_events
        )
        
        print(f"✅ Found {len(opportunities)} opportunities")
        
        if opportunities:
            print(f"\n🔍 OPPORTUNITY SCANNER RESULTS:")
            print("=" * 70)
            print(f"{'#':<3} {'Score':<6} {'Ticker':<6} {'Setup':<20} {'Risk':<6} {'Type'}")
            print("-" * 70)
            
            for i, opp in enumerate(opportunities, 1):
                score = opp.get('opportunity_score', 0)
                ticker = opp.get('ticker', 'N/A')
                setup = opp.get('setup', 'Unknown')[:18]
                risk = opp.get('risk_level', 'MED')
                opp_type = opp.get('type', 'unknown')
                
                score_icon = "🔥" if score >= 8.0 else "⚡" if score >= 6.5 else "📊"
                
                print(f"{i:<3} {score_icon}{score:<5.1f} {ticker:<6} {setup:<20} {risk:<6} {opp_type}")
            
            print(f"\n📋 DETAILED OPPORTUNITY ANALYSIS:")
            print("=" * 70)
            
            for i, opp in enumerate(opportunities[:3], 1):  # Show top 3 in detail
                print(f"\n{i}. {opp['ticker']} - {opp['setup']}")
                print(f"   Score: {opp['opportunity_score']:.1f}/10 | Risk: {opp['risk_level']}")
                print(f"   📝 {opp['description']}")
                print(f"   🎯 Entry: {opp['entry_reason']}")
                print(f"   ⏰ Timeframe: {opp['timeframe']}")
                print(f"   📈 Expected: {opp['expected_move']}")
                
                if opp.get('catalysts', 0) > 0:
                    print(f"   ⚡ Catalysts: {opp['catalysts']} active")
                
                setup_quality = opp.get('setup_quality', 'Unknown')
                print(f"   🏆 Quality: {setup_quality}")
            
            # Summary by opportunity type
            print(f"\n📊 OPPORTUNITY BREAKDOWN:")
            types = {}
            for opp in opportunities:
                opp_type = opp.get('type', 'unknown')
                types[opp_type] = types.get(opp_type, 0) + 1
            
            for opp_type, count in types.items():
                print(f"   • {opp_type.replace('_', ' ').title()}: {count}")
            
            # Risk summary
            risk_levels = {}
            for opp in opportunities:
                risk = opp.get('risk_level', 'MEDIUM')
                risk_levels[risk] = risk_levels.get(risk, 0) + 1
            
            print(f"\n⚠️  RISK DISTRIBUTION:")
            for risk, count in risk_levels.items():
                risk_icon = "🔥" if risk == 'HIGH' else "⚡" if risk == 'MEDIUM' else "✅"
                print(f"   {risk_icon} {risk}: {count} opportunities")
            
            print(f"\n🖥️  GUI OPPORTUNITY SCANNER PANEL WILL SHOW:")
            print("-" * 50)
            print("🔍 OPPORTUNITY SCANNER")
            print(f"🎯 Found {len(opportunities)} High-Quality Opportunities")
            print("")
            
            for opp in opportunities[:5]:  # Top 5 for GUI
                score = opp.get('opportunity_score', 0)
                risk = opp.get('risk_level', 'MED')
                score_icon = "🔥" if score >= 8.0 else "⚡" if score >= 6.5 else "📊"
                risk_color = "HIGH" if risk == 'HIGH' else "MED" if risk == 'MEDIUM' else "LOW"
                
                print(f"{score_icon} {score:.1f} {opp['ticker']} - {opp['setup']} [{risk_color} RISK]")
                print(f"    💡 {opp['description']}")
                print(f"    ⏰ {opp['timeframe']} | 🎯 {opp['entry_reason']}")
                print("")
        
        else:
            print("📊 No high-quality opportunities identified at this time")
            print("🔄 Continue monitoring for catalyst-driven setups")
        
        print(f"\n" + "=" * 70)
        print("✅ OPPORTUNITY SCANNER TEST COMPLETE")
        print("🔍 This is what your GUI Opportunity Scanner displays")
        print("🔄 It updates automatically when technical data refreshes")
        print("=" * 70)
        
        return opportunities
        
    except Exception as e:
        print(f"❌ Error testing opportunity scanner: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_opportunity_scanner()
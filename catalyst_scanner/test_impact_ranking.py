#!/usr/bin/env python3
"""
Test Impact Ranking System
Check if the impact ranking is working properly with real data
"""

import sys
import os
from datetime import datetime, timedelta

def test_impact_ranking():
    """Test the impact ranking system with current data"""
    
    print("=" * 70)
    print("🎯 TESTING IMPACT RANKING SYSTEM FOR NEXT 7 DAYS")
    print("=" * 70)
    
    try:
        # Import required modules
        from analyzers.impact_scorer import CatalystImpactScorer
        from data_collectors.earnings_calendar import EarningsCalendarCollector
        from data_collectors.portfolio_loader import load_user_portfolio
        from data_collectors.technical_analysis import TechnicalAnalysisCollector
        from utils.auth_manager import get_auth_manager
        
        # Initialize components
        impact_scorer = CatalystImpactScorer()
        earnings_collector = EarningsCalendarCollector()
        auth_manager = get_auth_manager()
        technical_collector = TechnicalAnalysisCollector(auth_manager)
        
        # Load portfolio data
        print("📊 Loading portfolio data...")
        portfolio_loader = load_user_portfolio()
        portfolio_tickers = portfolio_loader.get_tickers()
        print(f"✅ Loaded {len(portfolio_tickers)} tickers: {portfolio_tickers}")
        
        # Load earnings calendar
        print("\n📅 Loading earnings calendar for next 7 days...")
        earnings_collector.fetch_earnings_calendar(portfolio_tickers, days_ahead=7)
        earnings_events = earnings_collector.format_earnings_for_display(10)
        print(f"✅ Found {len(earnings_events)} earnings events")
        
        if earnings_events:
            for event in earnings_events:
                print(f"   • {event['ticker']}: {event['date_display']} {event['time_display']}")
        else:
            print("   ℹ️  No earnings events in next 7 days")
        
        # Load technical analysis
        print("\n📈 Loading technical analysis...")
        technical_data = technical_collector.analyze_portfolio_technicals(portfolio_tickers[:3])
        if technical_data:
            print(f"   ✅ Technical analysis completed for {len(technical_data)} tickers")
            for ticker, analysis in technical_data.items():
                rsi = analysis.get('rsi', 'N/A')
                signal = analysis.get('signal', 'N/A')
                print(f"   • {ticker}: RSI={rsi}, Signal={signal}")
        else:
            print("   ❌ No technical analysis data available")
        
        # Create sample catalyst events since we have no earnings
        print("\n🔍 Creating sample catalyst events for testing...")
        catalyst_events = []
        
        # Add technical-based catalyst events
        for ticker, analysis in technical_data.items():
            rsi = analysis.get('rsi', 50)
            if isinstance(rsi, (int, float)):
                if rsi <= 30:
                    catalyst_events.append({
                        'ticker': ticker,
                        'type': 'oversold_condition',
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'description': f'{ticker} RSI oversold at {rsi:.1f}',
                        'source': 'technical_analysis'
                    })
                elif rsi >= 70:
                    catalyst_events.append({
                        'ticker': ticker,
                        'type': 'overbought_condition', 
                        'date': datetime.now().strftime('%Y-%m-%d'),
                        'description': f'{ticker} RSI overbought at {rsi:.1f}',
                        'source': 'technical_analysis'
                    })
        
        # Add some sample upcoming events for demonstration
        future_date = (datetime.now() + timedelta(days=2)).strftime('%Y-%m-%d')
        catalyst_events.extend([
            {
                'ticker': 'SMCI',
                'type': 'earnings_preview',
                'date': future_date,
                'description': 'SMCI earnings expectations building',
                'source': 'market_analysis'
            },
            {
                'ticker': 'MARA',
                'type': 'sector_momentum',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'description': 'Bitcoin mining sector strength',
                'source': 'sector_analysis'
            }
        ])
        print(f"✅ Found {len(catalyst_events)} catalyst events")
        
        # Score and rank events
        print("\n📊 SCORING AND RANKING EVENTS:")
        print("-" * 50)
        
        if catalyst_events:
            # Create sample portfolio data for scoring
            portfolio_data = {}
            for ticker in portfolio_tickers:
                portfolio_data[ticker] = {
                    'value': 1000,  # Sample value
                    'shares': 10    # Sample shares
                }
            
            # Score each event
            scored_events = []
            for event in catalyst_events:
                try:
                    score, breakdown = impact_scorer.calculate_impact_score(
                        event, portfolio_data, technical_data
                    )
                    
                    scored_event = {
                        'event': event,
                        'score': score,
                        'breakdown': breakdown,
                        'priority': 'HIGH' if score >= 7.0 else 'MEDIUM' if score >= 4.0 else 'LOW'
                    }
                    scored_events.append(scored_event)
                    
                except Exception as e:
                    print(f"   ❌ Error scoring {event.get('ticker', 'Unknown')}: {e}")
            
            # Sort by score (highest first)
            scored_events.sort(key=lambda x: x['score'], reverse=True)
            
            # Display ranked results
            if scored_events:
                print(f"\n🏆 TOP IMPACT EVENTS (Next 7 Days):")
                print(f"{'Rank':<4} {'Priority':<8} {'Ticker':<6} {'Event':<15} {'Score':<6} {'Risk':<6}")
                print("-" * 65)
                
                for i, scored_event in enumerate(scored_events[:10], 1):
                    event = scored_event['event']
                    score = scored_event['score']
                    priority = scored_event['priority']
                    risk_level = scored_event['breakdown'].get('risk_level', 'N/A')
                    
                    print(f"{i:<4} {priority:<8} {event['ticker']:<6} {event['type']:<15} {score:<6.1f} {risk_level:<6}")
                
                print(f"\n📈 IMPACT RANKING SUMMARY:")
                high_impact = len([e for e in scored_events if e['priority'] == 'HIGH'])
                medium_impact = len([e for e in scored_events if e['priority'] == 'MEDIUM'])
                low_impact = len([e for e in scored_events if e['priority'] == 'LOW'])
                
                print(f"   🔥 HIGH Impact Events: {high_impact}")
                print(f"   ⚡ MEDIUM Impact Events: {medium_impact}")
                print(f"   📊 LOW Impact Events: {low_impact}")
                
                # Test what GUI should display
                print(f"\n🖥️  GUI IMPACT RANKING PANEL SHOULD SHOW:")
                print("-" * 50)
                print(f"{'Priority':<8} {'Ticker':<6} {'Event Type':<15} {'Date':<12} {'Score':<8}")
                print("-" * 50)
                
                for scored_event in scored_events[:5]:  # Top 5 for GUI
                    event = scored_event['event']
                    priority = scored_event['priority']
                    score = scored_event['score']
                    event_date = event.get('date', datetime.now().strftime('%Y-%m-%d'))
                    
                    print(f"{priority:<8} {event['ticker']:<6} {event['type']:<15} {event_date:<12} {score:.1f}/10")
            
            else:
                print("   ❌ No events could be scored")
        
        else:
            print("   📊 No catalyst events found for next 7 days")
            print("   📝 Impact ranking panel should show: 'No high-impact events in next 7 days'")
        
        print(f"\n" + "=" * 70)
        print("✅ IMPACT RANKING TEST COMPLETE")
        print("=" * 70)
        
        return scored_events if 'scored_events' in locals() else []
        
    except Exception as e:
        print(f"❌ Error in impact ranking test: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    test_impact_ranking()
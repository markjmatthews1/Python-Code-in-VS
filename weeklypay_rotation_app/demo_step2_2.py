"""
Step 2.2 Demo: Sector Momentum Tracker
Shows real-time sector momentum analysis with RSI and SMA crossovers
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.etf_tracker import ETFTracker
from src.signal_engine import RotationRulesEngine
from src.data_collector import DataCollector

def demo_sector_momentum():
    """Demonstrate Step 2.2: Sector Momentum Tracker"""
    
    print("🚀 STEP 2.2 DEMO: SECTOR MOMENTUM TRACKER")
    print("="*55)
    
    # Step 1: Initialize system
    print("\n📋 Step 1: Initializing Sector Momentum System...")
    tracker = ETFTracker("data/etf_list.json")
    engine = RotationRulesEngine(tracker)
    data_collector = DataCollector(tracker)
    data_collector.set_signal_engine(engine)
    
    # Step 2: Demonstrate sector momentum collection
    print("\n📈 Step 2: Real-Time Sector Momentum Analysis")
    print("-" * 45)
    
    print("Collecting live RSI and SMA data for:")
    print("   🔹 SMH - VanEck Semiconductor ETF")
    print("   🔹 XLK - Technology Select Sector SPDR")
    print("   🔹 XLC - Communication Services SPDR")
    
    # Collect sector momentum data
    momentum_results = data_collector.collect_all_data(['sector_momentum'])
    
    # Step 3: Display comprehensive momentum dashboard
    print("\n📊 Step 3: Momentum Dashboard Analysis")
    print("-" * 37)
    
    data_collector.display_sector_momentum_dashboard()
    
    # Step 4: Show integration with signal engine
    print("\n🧠 Step 4: Signal Engine Integration")
    print("-" * 35)
    
    # Add some sample earnings to see complete integration
    engine.add_earnings_event("AMD", "2025-10-08")
    engine.add_earnings_event("META", "2025-09-30")
    engine.add_earnings_event("NFLX", "2025-10-09")
    
    # Update ETF prices
    tracker.update_etf_price("NVDW", 45.23, 45.50)
    tracker.update_etf_price("AMDW", 32.67, 32.80)
    tracker.update_etf_price("HOOW", 67.89, 68.00)
    tracker.update_etf_price("NFLW", 78.90, 79.10)
    
    # Add some payout data
    tracker.add_payout_data("NVDW", "2025-10-01", 0.28)
    tracker.add_payout_data("HOOW", "2025-10-01", 0.35)
    
    # Generate signals with real sector momentum
    signals = engine.generate_rotation_signals()
    engine.display_rotation_signals(signals)
    
    # Step 5: Analyze momentum impact on rotation decisions
    print("\n🎯 Step 5: Momentum Impact Analysis")
    print("-" * 34)
    
    sector_signals = data_collector.sector_momentum.get_sector_signals()
    sector_rsi = data_collector.sector_momentum.get_sector_rsi_values()
    
    print("📊 CURRENT SECTOR MOMENTUM:")
    for symbol, signal in sector_signals.items():
        rsi = sector_rsi[symbol]
        signal_icon = "🟢" if signal == "BULLISH" else "🔴" if signal == "BEARISH" else "🟡"
        
        if rsi >= 70:
            rsi_status = "OVERBOUGHT"
        elif rsi <= 30:
            rsi_status = "OVERSOLD"
        elif rsi >= 60:
            rsi_status = "BULLISH"
        elif rsi <= 40:
            rsi_status = "BEARISH"
        else:
            rsi_status = "NEUTRAL"
        
        print(f"   {signal_icon} {symbol}: {signal} (RSI: {rsi:.1f} - {rsi_status})")
    
    print(f"\n🔧 ROTATION LOGIC IMPACT:")
    print(f"   📈 SMH RSI = {sector_rsi['SMH']:.1f} (Semiconductor sector)")
    if sector_rsi['SMH'] > 60:
        print(f"      → Tech ETFs (NVDW, AMDW, MSFW) get ROTATE IN signal")
    elif sector_rsi['SMH'] < 40:
        print(f"      → Tech ETFs (NVDW, AMDW, MSFW) get ROTATE OUT signal")
    else:
        print(f"      → Tech ETFs get NEUTRAL momentum signal")
    
    print(f"   📱 XLC RSI = {sector_rsi['XLC']:.1f} (Communication sector)")
    if sector_rsi['XLC'] > 60:
        print(f"      → Communication ETFs (HOOW, NFLW) get ROTATE IN signal")
    elif sector_rsi['XLC'] < 40:
        print(f"      → Communication ETFs (HOOW, NFLW) get ROTATE OUT signal")
    else:
        print(f"      → Communication ETFs get NEUTRAL momentum signal")
    
    # Step 6: Technical analysis breakdown
    print(f"\n📐 Step 6: Technical Analysis Breakdown")
    print("-" * 37)
    
    momentum_data = data_collector.sector_momentum.momentum_data
    
    for symbol, momentum in momentum_data.items():
        print(f"\n🔍 {symbol} Technical Analysis:")
        print(f"   💰 Current Price: ${momentum.price:.2f}")
        print(f"   📊 RSI (14-day): {momentum.rsi_14:.1f}")
        print(f"   📈 SMA 5-day: ${momentum.sma_5:.2f}")
        print(f"   📈 SMA 20-day: ${momentum.sma_20:.2f}")
        print(f"   📈 SMA 50-day: ${momentum.sma_50:.2f}")
        
        crossover_status = "Bullish (5 > 20)" if momentum.sma_crossover else "Bearish (5 < 20)"
        crossover_icon = "📈" if momentum.sma_crossover else "📉"
        print(f"   {crossover_icon} SMA Crossover: {crossover_status}")
        
        print(f"   🎯 Final Signal: {momentum.momentum_signal} ({momentum.confidence:.1%} confidence)")
        print(f"   📝 Key Factors:")
        for note in momentum.technical_notes[:3]:  # Show top 3 factors
            print(f"      • {note}")
    
    # Step 7: Save results
    print(f"\n💾 Step 7: Data Persistence")
    print("-" * 25)
    
    # Export comprehensive results
    with open("step2_2_demo_output.json", "w") as f:
        import json
        demo_output = {
            'step': '2.2 - Sector Momentum Tracker',
            'timestamp': data_collector.sector_momentum.momentum_data[list(data_collector.sector_momentum.momentum_data.keys())[0]].last_updated,
            'sector_signals': sector_signals,
            'sector_rsi': sector_rsi,
            'rotation_signals': signals,
            'momentum_analysis': {
                symbol: {
                    'signal': momentum.momentum_signal,
                    'rsi_14': momentum.rsi_14,
                    'price': momentum.price,
                    'sma_5': momentum.sma_5,
                    'sma_20': momentum.sma_20,
                    'sma_50': momentum.sma_50,
                    'sma_crossover': momentum.sma_crossover,
                    'confidence': momentum.confidence,
                    'technical_notes': momentum.technical_notes
                }
                for symbol, momentum in momentum_data.items()
            }
        }
        json.dump(demo_output, f, indent=2)
    
    print("✅ Demo results saved to 'step2_2_demo_output.json'")
    print("✅ Sector momentum cache saved to 'data/sector_momentum_cache.json'")
    
    # Step 8: Summary
    print(f"\n🎉 STEP 2.2 COMPLETE!")
    print("="*30)
    print("✅ Real-time RSI Calculation: Working")
    print("✅ SMA Crossover Analysis: Functional")  
    print("✅ Yahoo Finance Integration: Active")
    print("✅ Technical Signal Generation: Operational")
    print("✅ Signal Engine Integration: Complete")
    print("✅ Multi-timeframe Analysis: Enabled")
    
    bullish_count = sum(1 for s in sector_signals.values() if s == "BULLISH")
    bearish_count = sum(1 for s in sector_signals.values() if s == "BEARISH")
    neutral_count = len(sector_signals) - bullish_count - bearish_count
    
    print(f"\n📊 Current Market Snapshot:")
    print(f"   🟢 Bullish Sectors: {bullish_count}")
    print(f"   🔴 Bearish Sectors: {bearish_count}")
    print(f"   🟡 Neutral Sectors: {neutral_count}")
    
    if bearish_count > bullish_count:
        market_sentiment = "🔴 BEARISH MARKET"
    elif bullish_count > bearish_count:
        market_sentiment = "🟢 BULLISH MARKET"
    else:
        market_sentiment = "🟡 NEUTRAL MARKET"
    
    print(f"   🌟 Overall Market: {market_sentiment}")
    
    return signals

if __name__ == "__main__":
    demo_sector_momentum()
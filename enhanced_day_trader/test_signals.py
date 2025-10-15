#!/usr/bin/env python3
"""
Quick test of signal generation
"""

import asyncio
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.absolute()))

from live_signals import LiveTradeSignalGenerator

async def test_signals():
    generator = LiveTradeSignalGenerator()
    
    print("Testing signal generation...")
    
    # Test with sector ETFs individually
    for symbol in ['XLK', 'XLF', 'XLV', 'XLE']:
        print(f"\nTesting {symbol} (Sector ETF):")
        data = generator.get_market_data(symbol, period='5d', interval='5m')
        
        if not data.empty:
            print(f"✅ Got {len(data)} data points for {symbol}")
            print(f"Latest RSI: {data['RSI'].iloc[-1]:.1f}")
            print(f"Latest MACD: {data['MACD'].iloc[-1]:.4f}")
            print(f"Latest MACD Signal: {data['MACD_signal'].iloc[-1]:.4f}")
            print(f"Volume Ratio: {data['Volume'].iloc[-1] / data['Volume_SMA'].iloc[-1]:.2f}")
            
            # Calculate signal strength manually
            signal_strength = generator.calculate_signal_strength(data)
            print(f"Signal Strength: {signal_strength:.3f}")
            
            setup = generator.generate_trade_setup(symbol, data)
            if setup:
                print("🎯 SIGNAL FOUND!")
                print(generator.format_signal_for_display(setup))
            else:
                print("❌ No signal generated")
        else:
            print(f"❌ No data for {symbol}")

if __name__ == "__main__":
    asyncio.run(test_signals())
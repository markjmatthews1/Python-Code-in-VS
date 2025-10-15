#!/usr/bin/env python3
"""
Simple Console Trade Signal Display
===================================

Shows live trade signals directly in the console without web dashboard complications.
"""

import asyncio
from datetime import datetime
import sys
import os
from pathlib import Path

# Add current directory to Python path
sys.path.append(str(Path(__file__).parent.absolute()))

from live_signals import LiveTradeSignalGenerator

async def main():
    """Main function to display live trade signals"""
    print("🚀 Enhanced Day Trader v2.0 - Live Signal Scanner")
    print("=" * 60)
    print("Scanning for trade setups...")
    print("Press Ctrl+C to exit")
    print("=" * 60)
    
    signal_generator = LiveTradeSignalGenerator()
    
    while True:
        try:
            # Scan for signals
            signals = await signal_generator.scan_for_signals()
            
            if signals:
                print(f"\n📡 Found {len(signals)} active trade signals:")
                print("=" * 60)
                
                for signal in signals:
                    print(signal_generator.format_signal_for_display(signal))
                    
            else:
                current_time = datetime.now().strftime('%H:%M:%S')
                print(f"\n⏰ {current_time} - No signals found, continuing scan...")
                
            # Wait 60 seconds before next scan
            await asyncio.sleep(60)
            
        except KeyboardInterrupt:
            print("\n⏹️  Signal scanner stopped")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
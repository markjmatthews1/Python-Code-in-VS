"""
PINS Alert Strategy Analysis
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.strategy_engine import OptionChainAnalyzer

def analyze_pins_alerts():
    """Analyze viable alert strategies for PINS"""
    print("📈 PINS Alert Strategy Analysis")
    print("=" * 40)
    
    # Your position details
    cost_basis = 43.79
    target_recovery = 45.00
    qty = 200
    
    # Get current market data
    analyzer = OptionChainAnalyzer()
    current_price = analyzer.get_current_price('PINS')
    
    if current_price and current_price > 0:
        print(f"Current PINS Price: ${current_price:.2f}")
        print(f"Your Cost Basis: ${cost_basis:.2f}")
        print(f"Target Recovery: ${target_recovery:.2f}")
        
        # Calculate position metrics
        underwater_amount = (cost_basis - current_price) * qty
        underwater_pct = ((cost_basis - current_price) / current_price) * 100
        recovery_needed_pct = ((target_recovery - current_price) / current_price) * 100
        
        print(f"\n📊 Position Analysis:")
        print(f"Total Position Value: ${current_price * qty:,.2f}")
        print(f"Underwater Amount: ${underwater_amount:,.2f}")
        print(f"Underwater Percentage: {underwater_pct:.1f}%")
        print(f"Recovery Needed: {recovery_needed_pct:.1f}%")
        
        print(f"\n🎯 Recommended Alert Strategies:")
        
        # Strategy 1: Covered Call (if current price is reasonable)
        if current_price > cost_basis * 0.85:  # If not too far underwater
            print(f"\n1️⃣ COVERED CALL ALERT:")
            print(f"   Strategy: call_overlay")
            print(f"   Min Premium: $0.75 - $1.25")
            print(f"   Strike Distance: 5-8% (strikes around ${current_price * 1.05:.2f} - ${current_price * 1.08:.2f})")
            print(f"   Purpose: Generate income while holding")
            print(f"   Risk: Shares called away if price rises")
        
        # Strategy 2: Protective Put
        print(f"\n2️⃣ PROTECTIVE PUT ALERT:")
        print(f"   Strategy: put_overlay")
        print(f"   Min Premium: $1.00 - $2.00")
        print(f"   Strike Distance: 5-10% (strikes around ${current_price * 0.90:.2f} - ${current_price * 0.95:.2f})")
        print(f"   Purpose: Downside protection")
        print(f"   Best when: Expecting volatility or further decline")
        
        # Strategy 3: Synthetic Recovery (if significantly underwater)
        if underwater_pct > 10:
            print(f"\n3️⃣ SYNTHETIC RECOVERY ALERT:")
            print(f"   Strategy: synthetic_recovery")
            print(f"   Min Premium: $1.50 - $3.00")
            print(f"   Strike Distance: 15-20%")
            print(f"   Purpose: Complex recovery involving additional shares + calls")
            print(f"   Best when: Confident in long-term recovery")
        
        print(f"\n💡 RECOMMENDED STARTING ALERT:")
        if current_price > cost_basis * 0.90:
            print(f"   📞 COVERED CALL - Generate income while waiting for recovery")
            print(f"   Settings: call_overlay, min premium $1.00, 6% strike distance")
        else:
            print(f"   📉 PROTECTIVE PUT - Protect against further decline")
            print(f"   Settings: put_overlay, min premium $1.50, 8% strike distance")
            
    else:
        print("❌ Could not fetch current PINS price")
        print("💡 General PINS recommendations:")
        print("   - PINS is a social media/tech stock with higher volatility")
        print("   - Good candidate for covered calls during sideways movement")
        print("   - Consider protective puts if market outlook is uncertain")

if __name__ == "__main__":
    analyze_pins_alerts()
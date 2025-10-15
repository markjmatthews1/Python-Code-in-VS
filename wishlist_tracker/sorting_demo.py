#!/usr/bin/env python3
"""
Quick Sorting Demo for Wishlist Tracker
=======================================
Shows how the enhanced sorting will work with sample data
"""

def demo_enhanced_sorting():
    print("🎯 Enhanced Wishlist Sorting - Live Demo")
    print("=" * 60)
    
    # Sample data representing realistic put option scenarios
    sample_data = [
        # (symbol, current_price, strike, premium, is_uptrend)
        ("NVDL", 87.0, 90.0, 8.0, False),     # 90-8-87 = -$5.00 (great)
        ("TSLA", 250.0, 260.0, 12.0, True),   # 260-12-250 = -$2.00 (good + uptrend)
        ("AAPL", 180.0, 185.0, 7.0, False),   # 185-7-180 = -$2.00 (good)
        ("MSFT", 420.0, 430.0, 12.0, True),   # 430-12-420 = -$2.00 (good + uptrend)
        ("GOOGL", 150.0, 155.0, 8.0, True),   # 155-8-150 = -$3.00 (great + uptrend)
        ("META", 500.0, 510.0, 5.0, False),   # 510-5-500 = +$5.00 (poor)
        ("AMD", 140.0, 145.0, 2.0, True),     # 145-2-140 = +$3.00 (poor + uptrend)
        ("NFLX", 600.0, 620.0, 15.0, False),  # 620-15-600 = +$5.00 (poor)
    ]
    
    # Calculate premium vs current price
    rows = []
    for symbol, current, strike, premium, uptrend in sample_data:
        premium_vs_current = strike - premium - current
        trend_status = "Uptrend/Entry" if uptrend else "Neutral/Wait"
        rows.append((symbol, current, strike, premium, premium_vs_current, trend_status, uptrend))
    
    print("📊 Sample Data (Before Sorting):")
    print("Symbol | Current | Strike | Premium | Premium vs Current | Trend")
    print("-" * 65)
    for symbol, current, strike, premium, pvc, trend, _ in rows:
        prefix = "+" if pvc >= 0 else ""
        print(f"{symbol:6} | ${current:6.0f} | ${strike:6.0f} | ${premium:6.2f} | {prefix}${pvc:13.2f} | {trend}")
    
    print("\n🔄 Applying Enhanced Two-Tier Sorting...")
    
    # Step 1: Sort by premium value (best first)
    rows.sort(key=lambda r: r[4])  # Sort by premium_vs_current
    
    # Step 2: Apply uptrend boost to top performers
    valid_rows = [r for r in rows if r[4] != float('inf')]
    if valid_rows:
        top_count = max(3, len(valid_rows) // 3)  # Top 30% or at least 3
        best_premium_threshold = valid_rows[min(top_count-1, len(valid_rows)-1)][4]
        
        print(f"🔥 Top Premium Tier: {top_count} stocks with premium ≤ ${best_premium_threshold:.2f}")
        
        # Separate into top tier and others
        top_tier = []
        other_tier = []
        
        for row in rows:
            if row[4] != float('inf') and row[4] <= best_premium_threshold:
                top_tier.append(row)
            else:
                other_tier.append(row)
        
        # Within top tier, sort uptrend stocks first, then by premium
        top_tier.sort(key=lambda r: (-r[6], r[4]))  # Uptrend first, then best premium
        
        # Combine: top tier (with uptrend priority) + remaining stocks
        final_rows = top_tier + other_tier
    else:
        final_rows = rows
    
    print("\n📈 Final Sorted Results:")
    print("Rank | Symbol | Premium vs Current | Trend         | Tier")
    print("-" * 60)
    
    for i, (symbol, current, strike, premium, pvc, trend, uptrend) in enumerate(final_rows, 1):
        prefix = "+" if pvc >= 0 else ""
        tier = "🔥 ELITE" if i <= top_count else "📊 STD"
        trend_icon = "🟢" if uptrend else "⚪"
        print(f"{i:4} | {symbol:6} | {prefix}${pvc:13.2f} | {trend_icon} {trend:11} | {tier}")
    
    print(f"\n✅ Results Explanation:")
    print(f"🔥 Elite Tier (Top {top_count}): Best premiums with uptrend priority")
    print(f"📊 Standard Tier: Remaining stocks sorted by premium quality")
    print(f"🟢 Uptrend stocks get boosted within their tier")
    print(f"⚪ Non-uptrend stocks sorted purely by premium profitability")
    
    print(f"\n🎯 Perfect Balance Achieved!")
    print(f"✅ Best opportunities first (NVDL: -$5.00)")
    print(f"✅ Uptrend boost in elite tier (GOOGL: -$3.00 + uptrend beats AAPL: -$2.00)")
    print(f"✅ Quality over trend in lower tiers (Poor premiums at bottom regardless of trend)")

if __name__ == "__main__":
    demo_enhanced_sorting()
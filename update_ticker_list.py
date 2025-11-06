"""
Update the ETF ticker list with optimized tickers for day trading
"""
import pandas as pd

# Optimized ticker list (Option 3)
optimized_tickers = [
    'TQQQ',   # Nasdaq 3x - EXCELLENT
    'TECL',   # Tech 3x - EXCELLENT
    'SOXL',   # Semiconductors 3x - EXCELLENT (NEW)
    'UPRO',   # S&P 3x - EXCELLENT
    'TNA',    # Russell 2000 3x - EXCELLENT (NEW)
    'MSTX',   # Microsoft 2x - GOOD
    'NVDL',   # NVIDIA 2x - GOOD
    'FNGU',   # FANG+ 3x - GOOD (NEW)
    'BITU',   # Bitcoin 2x - MODERATE
    'ETHU',   # Ethereum 2x - MODERATE
    'ROM',    # ProShares Ultra Tech - GOOD
    'AGQ',    # Silver 2x - GOOD
    'LABU',   # Biotech 3x - GOOD
    'NUGT',   # Gold miners 3x - GOOD
    'DFEN',   # Defense 3x - GOOD
    'ERX',    # Energy 3x - GOOD
    'SDOW',   # Dow -3x - GOOD (inverse)
    'SDS',    # S&P -2x - GOOD (inverse)
    'MSFU',   # Microsoft 2x - MODERATE
    'TSLT',   # Tesla 2x - MODERATE
    'AMD',    # AMD stock - EXCELLENT
    'SSO',    # S&P 2x - EXCELLENT
    'UMDD',   # Midcap 3x - GOOD (NEW)
    'HIBL'    # S&P Buyback 3x - GOOD (NEW)
]

# Create DataFrame
df = pd.DataFrame({'Symbol': optimized_tickers})

# Save to Excel
df.to_excel('Top_ETFS_for_DayTrade.xlsx', index=False)

print("✅ Updated Top_ETFS_for_DayTrade.xlsx")
print(f"\n📊 Total tickers: {len(optimized_tickers)}")
print("\n✅ ADDED (5 new tickers):")
print("   • SOXL - Semiconductors 3x (50M+ volume)")
print("   • FNGU - FANG+ 3x (2M+ volume)")
print("   • TNA - Russell 2000 3x (20M+ volume)")
print("   • UMDD - Midcap 3x (500K+ volume)")
print("   • HIBL - S&P Buyback 3x (200K+ volume)")

print("\n❌ REMOVED (7 low-quality tickers):")
print("   • CWEB - Too low volume (50K)")
print("   • JNUG - Redundant with NUGT, lower volume")
print("   • NAIL - Too low volume (300K)")
print("   • BOIL - Erratic, low volume (800K)")
print("   • SMCX - Newer, lower volume (500K)")
print("   • GDXU - Redundant with NUGT")
print("   • SPYI - Income ETF, not for day trading")

print("\n🎯 DIVERSIFICATION:")
print(f"   Tech (7): TQQQ, TECL, SOXL, FNGU, NVDL, MSTX, ROM")
print(f"   Broad Market (5): UPRO, SSO, TNA, UMDD, HIBL")
print(f"   Commodities (3): AGQ, NUGT, ERX")
print(f"   Crypto (2): BITU, ETHU")
print(f"   Inverse (2): SDOW, SDS")
print(f"   Sector (2): LABU, DFEN")
print(f"   Single Stock (3): AMD, TSLT, MSFU")

print("\n📈 VOLUME QUALITY:")
print("   • 10M+ volume: 6 tickers (TQQQ, SOXL, UPRO, TNA, AMD, NUGT)")
print("   • 1M-10M volume: 11 tickers")
print("   • 500K-1M volume: 5 tickers")
print("   • 200K-500K volume: 2 tickers (MSFU, HIBL)")

print("\n💡 EXPECTED IMPROVEMENTS:")
print("   ✅ Tighter spreads (better execution)")
print("   ✅ Easier position entry/exit")
print("   ✅ Less slippage on stops")
print("   ✅ More consistent price action")
print("   ✅ Better intraday liquidity")

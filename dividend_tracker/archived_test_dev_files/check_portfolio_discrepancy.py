import json

# Load cache data
with open('portfolio_data_cache.json', 'r') as f:
    cache_data = json.load(f)

print("PORTFOLIO VALUES COMPARISON")
print("=" * 50)

# Check pre-calculated values from cache
portfolio_values = cache_data.get('portfolio_values', {})
print("1. PRE-CALCULATED VALUES FROM CACHE:")
total_precalc = 0
for account, value in portfolio_values.items():
    if account != '401K':
        total_precalc += value
    print(f"   {account}: ${value:,.2f}")

print(f"   Subtotal (excluding 401K): ${total_precalc:,.2f}")

# Check calculated values from positions
positions_data = cache_data.get('positions', {})
print("\n2. CALCULATED VALUES FROM POSITIONS:")
total_calc = 0
for account, positions in positions_data.items():
    account_total = sum(pos.get('market_value', 0) for pos in positions)
    total_calc += account_total
    print(f"   {account}: ${account_total:,.2f}")

print(f"   Subtotal from positions: ${total_calc:,.2f}")

print(f"\n3. DIFFERENCE:")
print(f"   Pre-calculated total: ${total_precalc:,.2f}")
print(f"   Positions total: ${total_calc:,.2f}")
print(f"   Difference: ${abs(total_precalc - total_calc):,.2f}")

if abs(total_precalc - total_calc) > 0.01:
    print("   ⚠️  SIGNIFICANT DIFFERENCE FOUND!")
    print("   Portfolio Summary updater should use portfolio_values, not positions!")
else:
    print("   ✅ Values match - no calculation issue")
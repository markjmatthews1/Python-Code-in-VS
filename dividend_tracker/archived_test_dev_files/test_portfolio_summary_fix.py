from portfolio_summary_updater import PortfolioSummaryUpdater

print("TESTING PORTFOLIO SUMMARY UPDATER")
print("=" * 40)

updater = PortfolioSummaryUpdater()
cache_data = updater.load_cache_data()

if cache_data:
    print("Cache loaded successfully!")
    print(f"Cache timestamp: {cache_data.get('timestamp', 'Unknown')}")
    
    values = updater.get_portfolio_values(cache_data)
    
    print("\nExpected values based on cache:")
    portfolio_values = cache_data.get('portfolio_values', {})
    for account, value in portfolio_values.items():
        print(f"  {account}: ${value:,.2f}")
    
    total_expected = sum(v for v in portfolio_values.values())
    print(f"  Total Expected: ${total_expected:,.2f}")
    
    print(f"\nCalculated total: ${values['total_portfolio']:,.2f}")
    print(f"Match: {'✅ YES' if abs(total_expected - values['total_portfolio']) < 0.01 else '❌ NO'}")
    
else:
    print("ERROR: Could not load cache data")
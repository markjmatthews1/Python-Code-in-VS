#!/usr/bin/env python3
from portfolio_data_collector import PortfolioDataCollector

print("Testing ticker yields collection...")
collector = PortfolioDataCollector()
ticker_yields = collector.collect_fresh_ticker_yields_from_etrade_ira()

print(f"Collected {len(ticker_yields)} ticker yields:")
for ticker, data in list(ticker_yields.items())[:5]:
    print(f"  {ticker}: Has dividend: {data.get('has_dividend', False)}, Yield: {data.get('yield', 0)}%")

if len(ticker_yields) > 5:
    print(f"  ... and {len(ticker_yields) - 5} more")

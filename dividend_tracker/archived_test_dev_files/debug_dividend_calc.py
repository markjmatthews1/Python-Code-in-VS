import json

def debug_dividend_calculations():
    """Debug why dividend estimates are showing $0.00"""
    
    try:
        with open('portfolio_data_cache.json', 'r') as f:
            cache_data = json.load(f)
        
        positions_data = cache_data.get('positions', {})
        yields_data = cache_data.get('yields', {})
        
        print("DIVIDEND CALCULATION DEBUG")
        print("=" * 35)
        
        print(f"Total yield symbols: {len(yields_data)}")
        print(f"Positions accounts: {list(positions_data.keys())}")
        
        # Check E*TRADE IRA positions and yields
        etrade_ira_positions = positions_data.get('etrade_ira', [])
        print(f"\nE*TRADE IRA positions: {len(etrade_ira_positions)}")
        
        total_dividend = 0
        for i, position in enumerate(etrade_ira_positions[:5]):  # Check first 5
            symbol = position.get('symbol', '').strip().upper()
            market_value = position.get('market_value', 0)
            yield_info = yields_data.get(symbol, {})
            current_yield = yield_info.get('yield', 0.0)
            has_dividend = yield_info.get('has_dividend', False)
            
            annual_dividend = market_value * (current_yield / 100.0)
            total_dividend += annual_dividend
            
            print(f"  {symbol}: MV=${market_value:.2f}, Yield={current_yield:.2f}%, Div={has_dividend}, Annual=${annual_dividend:.2f}")
        
        print(f"\nTotal from first 5: ${total_dividend:.2f}")
        
        # Check if any yields are actually > 0
        high_yields = {k: v for k, v in yields_data.items() if v.get('yield', 0) > 0}
        print(f"\nSymbols with yield > 0: {len(high_yields)}")
        
        for symbol, data in list(high_yields.items())[:10]:
            print(f"  {symbol}: {data.get('yield', 0):.2f}%")
            
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    debug_dividend_calculations()
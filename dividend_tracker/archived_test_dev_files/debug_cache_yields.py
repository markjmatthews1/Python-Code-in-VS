import json

def check_cache_yields():
    cache_file = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp\portfolio_data_cache.json"
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        yields_data = data.get('yields', {})
        print(f"Total symbols in yields cache: {len(yields_data)}")
        
        # Check first 10 yields
        count = 0
        dividend_count = 0
        high_yield_count = 0
        
        for symbol, info in yields_data.items():
            if count < 10:
                print(f"{symbol}: yield={info.get('yield', 0)}%, dividend={info.get('has_dividend', False)}")
                count += 1
            
            if info.get('has_dividend', False):
                dividend_count += 1
                if info.get('yield', 0) > 4.0:
                    high_yield_count += 1
        
        print(f"\nSummary:")
        print(f"- Total symbols: {len(yields_data)}")
        print(f"- Dividend paying: {dividend_count}")  
        print(f"- High yield (>4%): {high_yield_count}")
        
        # Show high yield examples
        print(f"\nHigh yield examples:")
        for symbol, info in yields_data.items():
            if info.get('yield', 0) > 4.0:
                print(f"  {symbol}: {info.get('yield', 0)}%")
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cache_yields()
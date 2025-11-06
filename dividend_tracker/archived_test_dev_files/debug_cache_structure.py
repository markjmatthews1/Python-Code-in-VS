import json

def check_cache_structure():
    cache_file = r"c:\Users\mjmat\Python Code in VS\dividend_tracker\DividendTrackerApp\portfolio_data_cache.json"
    
    try:
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        print("Cache structure:")
        for key in data.keys():
            if isinstance(data[key], dict):
                print(f"  {key}: {len(data[key])} items")
                if key == 'positions':
                    for account, positions in data[key].items():
                        print(f"    {account}: {len(positions)} positions")
            elif isinstance(data[key], list):
                print(f"  {key}: {len(data[key])} items")
            else:
                print(f"  {key}: {type(data[key])}")
                
        # Check if yields data exists under different key
        if 'yields' not in data:
            print("\n'yields' key not found! Available keys:", list(data.keys()))
            
        # Show sample position to see if it has yield data
        positions_data = data.get('positions', {})
        for account, positions in positions_data.items():
            if positions:
                print(f"\nSample position from {account}:")
                sample = positions[0]
                for key, value in sample.items():
                    print(f"  {key}: {value}")
                break
                
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_cache_structure()
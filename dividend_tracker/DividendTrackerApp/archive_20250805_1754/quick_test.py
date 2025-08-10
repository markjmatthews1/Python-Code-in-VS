import sys
sys.path.append('modules')
import requests

try:
    # First, test a direct API call to see if the key works
    print("Testing Alpha Vantage API key with direct call...")
    
    api_key = 'K83KWPBFXRE10DAD'
    url = f"https://www.alphavantage.co/query?function=OVERVIEW&symbol=ABR&apikey={api_key}"
    
    response = requests.get(url)
    print(f"API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("API Response Keys:", list(data.keys())[:10])  # Show first 10 keys
        
        # Check for specific dividend data
        if 'DividendYield' in data:
            print(f"Dividend Yield: {data['DividendYield']}")
        if 'DividendPerShare' in data:
            print(f"Dividend Per Share: {data['DividendPerShare']}")
        if 'Symbol' in data:
            print(f"Symbol: {data['Symbol']}")
        
        # Check for error messages
        if 'Error Message' in data:
            print(f"API Error: {data['Error Message']}")
        if 'Note' in data:
            print(f"API Note: {data['Note']}")
            
    else:
        print(f"HTTP Error: {response.status_code}")
        print("Response:", response.text[:200])
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

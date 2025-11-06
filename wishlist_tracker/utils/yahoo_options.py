"""
Yahoo Finance Option Data Fallback
Used during pre-market/after-hours when E*TRADE returns $0.00 bids
"""
import requests
from datetime import datetime, date


def fetch_yahoo_option_chain(ticker, target_expiry_dates):
    """
    Fetch option chain from Yahoo Finance as fallback
    
    Args:
        ticker: Stock symbol
        target_expiry_dates: List of datetime.date objects for desired expirations
        
    Returns:
        list: Option data in same format as E*TRADE parser
    """
    options = []
    
    try:
        # Yahoo Finance API endpoint
        url = f"https://query2.finance.yahoo.com/v7/finance/options/{ticker}"
        
        # Get available expiration dates
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            print(f"❌ Yahoo Finance API failed: {response.status_code}")
            return []
        
        data = response.json()
        
        if 'optionChain' not in data or 'result' not in data['optionChain']:
            print(f"❌ Yahoo Finance: No option chain data for {ticker}")
            return []
        
        result = data['optionChain']['result'][0]
        available_exp_timestamps = result.get('expirationDates', [])
        
        # Convert target dates to timestamps for matching
        target_timestamps = [int(datetime.combine(d, datetime.min.time()).timestamp()) for d in target_expiry_dates]
        
        # Fetch each target expiration
        for target_ts in target_timestamps:
            # Find closest available expiration
            closest_ts = min(available_exp_timestamps, key=lambda x: abs(x - target_ts))
            
            # Fetch options for this expiration
            exp_url = f"{url}?date={closest_ts}"
            exp_response = requests.get(exp_url, timeout=10)
            
            if exp_response.status_code == 200:
                exp_data = exp_response.json()
                exp_result = exp_data['optionChain']['result'][0]
                
                # Get put options
                puts = exp_result.get('options', [{}])[0].get('puts', [])
                
                for put in puts:
                    strike = put.get('strike')
                    bid = put.get('bid', 0)
                    ask = put.get('ask', 0)
                    
                    if strike and bid > 0:
                        options.append({
                            'symbol': put.get('contractSymbol', ''),
                            'strike': float(strike),
                            'bid': float(bid),
                            'ask': float(ask) if ask > 0 else float(bid * 1.1)
                        })
        
        print(f"✅ Yahoo Finance: Fetched {len(options)} puts for {ticker}")
        return options
        
    except Exception as e:
        print(f"❌ Yahoo Finance error: {e}")
        return []


# Test function
if __name__ == "__main__":
    from datetime import date, timedelta
    
    # Test with MSFU
    ticker = "MSFU"
    # Use November and December expirations
    target_dates = [date(2025, 11, 21), date(2025, 12, 19)]
    
    print(f"Testing Yahoo Finance fallback for {ticker}")
    print("="*80)
    
    options = fetch_yahoo_option_chain(ticker, target_dates)
    
    if options:
        print(f"\nFound {len(options)} options:")
        for opt in options[:10]:  # Show first 10
            print(f"  Strike: ${opt['strike']:.2f}, Bid: ${opt['bid']:.2f}, Ask: ${opt['ask']:.2f}")
    else:
        print("No options found")

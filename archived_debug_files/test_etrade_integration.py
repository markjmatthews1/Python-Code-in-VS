#!/usr/bin/env python3
"""Test script for E*TRADE integration with TradeTracker"""

def test_stock_price():
    """Test fetching a stock price"""
    try:
        from etrade_auth import get_etrade_session
        session, base_url = get_etrade_session()
        ticker = "AAPL"
        url = f"{base_url}/v1/market/quote/{ticker}.json"
        response = session.get(url)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            quote_data = data.get("QuoteResponse", {}).get("QuoteData", [])
            if quote_data and len(quote_data) > 0:
                all_data = quote_data[0].get("All", {})
                last_trade = all_data.get("lastTrade")
                print(f"AAPL last trade price: ${last_trade}")
                return True
        else:
            print(f"Error response: {response.text}")
    except Exception as e:
        print(f"Error fetching stock price: {e}")
        import traceback
        traceback.print_exc()
    return False

def test_option_chain():
    """Test fetching option chain data"""
    try:
        from etrade_auth import get_etrade_session
        
        session, base_url = get_etrade_session()
        ticker = "AAPL"
        
        # First, get available expiration dates
        exp_url = f"{base_url}/v1/market/optionexpiredate.json?symbol={ticker}"
        exp_response = session.get(exp_url)
        
        print(f"Option Expiration Dates Status Code: {exp_response.status_code}")
        if exp_response.status_code == 200:
            exp_data = exp_response.json()
            dates = exp_data.get("OptionExpireDateResponse", {}).get("ExpirationDate", [])
            if dates:
                # Use the first available expiration date
                exp_date = dates[0]
                day = exp_date.get("day")
                month = exp_date.get("month")
                year = exp_date.get("year")
                
                print(f"Using expiration date: {month}/{day}/{year}")
                
                url = f"{base_url}/v1/market/optionchains.json?symbol={ticker}&expiryDay={day:02d}&expiryMonth={month:02d}&expiryYear={year}&chainType=CALL"
                response = session.get(url)
                
                print(f"Option Chain Status Code: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    chain = data.get("OptionChainResponse", {})
                    option_pairs = chain.get("OptionPair", [])
                    print(f"Found {len(option_pairs)} option pairs")
                    if option_pairs:
                        first_option = option_pairs[0].get("Call", {})
                        strike = first_option.get("strikePrice")
                        last_price = first_option.get("lastPrice")
                        print(f"Example call option: Strike ${strike}, Last Price ${last_price}")
                        return True
                else:
                    print(f"Option chain error response: {response.text}")
            else:
                print("No expiration dates found")
        else:
            print(f"Expiration dates error response: {exp_response.text}")
    except Exception as e:
        print(f"Error fetching option chain: {e}")
        import traceback
        traceback.print_exc()
    return False

if __name__ == "__main__":
    print("Testing E*TRADE integration...")
    print("=" * 50)
    
    print("1. Testing stock price fetching...")
    if test_stock_price():
        print("✓ Stock price test passed")
    else:
        print("✗ Stock price test failed")
    
    print("\n2. Testing option chain fetching...")
    if test_option_chain():
        print("✓ Option chain test passed")
    else:
        print("✗ Option chain test failed")
    
    print("\nE*TRADE integration test complete.")

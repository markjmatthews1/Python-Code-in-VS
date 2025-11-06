#!/usr/bin/env python3
"""
Get SMR Oct 17 options (actual 3rd Friday monthly expiration)
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from etrade_auth import get_etrade_session
import xml.etree.ElementTree as ET

def main():
    print("Getting SMR Oct 17 '25 put options (3rd Friday monthly)...")
    print("=" * 70)
    
    # Initialize auth
    session, base_url = get_etrade_session()
    
    current_price = 38.20
    print(f"Current SMR price: ${current_price}")
    
    # Request Oct 17 options specifically (actual 3rd Friday)
    url = f"{base_url}/v1/market/optionchains"
    params = {
        'symbol': 'SMR',
        'chainType': 'PUT',
        'expiryDay': 17,
        'expiryMonth': 10,
        'expiryYear': 2025
    }
    
    response = session.get(url, params=params)
    
    if response.status_code != 200:
        print(f"API Error: {response.status_code}")
        print(f"Response: {response.text}")
        return
    
    # Parse XML response
    root = ET.fromstring(response.content)
    
    print(f"\nOct 17 '25 put options (3rd Friday - around $35-$42 strike):")
    print("=" * 70)
    
    option_count = 0
    negative_premium_count = 0
    
    for option_pair in root.findall('.//OptionPair'):
        put_element = option_pair.find('Put')
        if put_element is not None:
            display = put_element.find('displaySymbol').text
            strike = float(put_element.find('strikePrice').text)
            bid = float(put_element.find('bid').text)
            ask = float(put_element.find('ask').text)
            volume = int(put_element.find('volume').text)
            open_interest = int(put_element.find('openInterest').text)
            
            # Focus on relevant strikes
            if 35 <= strike <= 42:
                option_count += 1
                
                # Check for negative premium
                negative_premium = ""
                if bid > 0:
                    net_cost = strike - bid
                    if net_cost < current_price:
                        negative_premium = " *** NEGATIVE PREMIUM ***"
                        negative_premium_count += 1
                
                print(f"{display}")
                print(f"  Strike: ${strike}, Bid: ${bid}, Ask: ${ask}")
                print(f"  Volume: {volume}, Open Interest: {open_interest}")
                if bid > 0:
                    net_cost = strike - bid
                    print(f"  Net Cost: ${net_cost:.2f} (vs Current ${current_price}){negative_premium}")
                print()
    
    print(f"Summary:")
    print(f"  Total options in $35-$42 range: {option_count}")
    print(f"  Options with negative premiums: {negative_premium_count}")
    
    # Show the $38 put specifically
    print(f"\nLooking for $38 put specifically:")
    for option_pair in root.findall('.//OptionPair'):
        put_element = option_pair.find('Put')
        if put_element is not None:
            strike = float(put_element.find('strikePrice').text)
            if strike == 38.0:
                display = put_element.find('displaySymbol').text
                bid = float(put_element.find('bid').text)
                ask = float(put_element.find('ask').text)
                
                print(f"✅ Found: {display}")
                print(f"   Bid: ${bid} (Expected ~$2.25 from screenshot)")
                print(f"   Ask: ${ask}")
                
                if bid > 0:
                    net_cost = 38 - bid
                    print(f"   Net Cost: ${net_cost:.2f} (vs Current ${current_price})")
                    if net_cost < current_price:
                        print(f"   ✅ NEGATIVE PREMIUM CONFIRMED!")
                
                # Check if bid is close to expected $2.25
                if abs(bid - 2.25) < 0.50:
                    print(f"   ✅ BID MATCHES SCREENSHOT! ({bid} ≈ 2.25)")
                break

if __name__ == "__main__":
    main()
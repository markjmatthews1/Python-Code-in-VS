import os
import sys
from datetime import datetime, timedelta, date
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from etrade_auth import get_etrade_session


def get_target_expiration_dates():
    """Get both current and next month 3rd Friday dates based on trading days rule"""
    today = date.today()
    current_third_friday = get_third_friday(today.year, today.month)
    trading_days_left = calculate_trading_days(today, current_third_friday)
    
    print(f"DEBUG: {today} - Current month 3rd Friday: {current_third_friday} ({trading_days_left} trading days)")
    
    # Determine which months to use
    months_to_check = []
    
    if trading_days_left > 5:
        # Use current month
        months_to_check.append(current_third_friday)
        print(f"DEBUG: Using current month 3rd Friday: {current_third_friday}")
        
        # Add next month
        if today.month == 12:
            next_year = today.year + 1
            next_month = 1
        else:
            next_year = today.year
            next_month = today.month + 1
        next_third_friday = get_third_friday(next_year, next_month)
        months_to_check.append(next_third_friday)
        print(f"DEBUG: Also using next month 3rd Friday: {next_third_friday}")
    else:
        # Skip current month, use next month
        if today.month == 12:
            next_year = today.year + 1
            next_month = 1
        else:
            next_year = today.year
            next_month = today.month + 1
        next_third_friday = get_third_friday(next_year, next_month)
        months_to_check.append(next_third_friday)
        print(f"DEBUG: Skipping current month, using next month 3rd Friday: {next_third_friday}")
        
        # Add month after next
        if next_month == 12:
            next_next_year = next_year + 1
            next_next_month = 1
        else:
            next_next_year = next_year
            next_next_month = next_month + 1
        next_next_third_friday = get_third_friday(next_next_year, next_next_month)
        months_to_check.append(next_next_third_friday)
        print(f"DEBUG: Also using month after next 3rd Friday: {next_next_third_friday}")
    
    return months_to_check


def calculate_probability_above_strike(current_price, strike_price, days_to_expiry):
    """Simple probability estimate based on strike distance and time"""
    price_buffer = (current_price - strike_price) / current_price
    
    # Basic probability model - adjust as needed
    if price_buffer >= 0.15:  # 15%+ buffer
        base_prob = 0.85
    elif price_buffer >= 0.10:  # 10-15% buffer
        base_prob = 0.75
    elif price_buffer >= 0.05:  # 5-10% buffer
        base_prob = 0.65
    elif price_buffer >= 0.02:  # 2-5% buffer
        base_prob = 0.55
    elif price_buffer >= 0:     # At the money or slightly above
        base_prob = 0.50
    else:                       # In the money
        base_prob = 0.30
    
    # Adjust for time decay - longer time = higher risk
    if days_to_expiry > 45:
        time_adjustment = -0.10
    elif days_to_expiry > 30:
        time_adjustment = -0.05
    elif days_to_expiry > 14:
        time_adjustment = 0
    else:
        time_adjustment = 0.05
    
    final_prob = max(0.1, min(0.95, base_prob + time_adjustment))
    return final_prob


def fetch_put_option_chain(ticker, current_price):
    """Fetch put options for 2 months, find best negative premium with probability analysis"""
    session_result = get_etrade_session()
    if not session_result:
        print(f"Failed to get E*Trade session for {ticker}")
        return []
    
    session, base_url = session_result
    
    # Get target expiration dates (2 months)
    target_expiries = get_target_expiration_dates()
    print(f"DEBUG: {ticker} - Checking {len(target_expiries)} expiration dates")
    
    all_candidates = []
    
    for target_expiry in target_expiries:
        # Build option chain URL with specific expiration
        option_url = f"{base_url}/v1/market/optionchains"
        params = {
            'symbol': ticker,
            'chainType': 'PUT',
            'expiryDay': target_expiry.day,
            'expiryMonth': target_expiry.month,
            'expiryYear': target_expiry.year
        }
        
        try:
            print(f"DEBUG: {ticker} - Fetching options for {target_expiry}")
            response = session.get(option_url, params=params)
            
            if response.status_code == 200:
                options = parse_xml_option_pairs(response.text)
                print(f"DEBUG: {ticker} - Found {len(options)} put options for {target_expiry}")
                
                # Filter options within ±$10 of current price and calculate negative premiums
                days_to_expiry = (target_expiry - date.today()).days
                
                for opt in options:
                    strike = opt['strike']
                    bid = opt['bid']
                    
                    # Check if within ±$10 range
                    if abs(strike - current_price) <= 10.0 and bid > 0:
                        net_cost_basis = strike - bid
                        negative_premium = current_price - net_cost_basis
                        
                        # Only include if it's a true negative premium (profitable if assigned)
                        if negative_premium > 0:
                            probability = calculate_probability_above_strike(current_price, strike, days_to_expiry)
                            
                            candidate = {
                                'strike': strike,
                                'premium': bid,
                                'expiration': target_expiry.strftime('%m/%d'),
                                'net_cost_basis': net_cost_basis,
                                'negative_premium_amount': negative_premium,
                                'net_diff': negative_premium,  # GUI expects this field name
                                'probability_above_strike': probability,
                                'days_to_expiry': days_to_expiry,
                                'expiry_date': target_expiry
                            }
                            all_candidates.append(candidate)
                            
            else:
                print(f"ERROR: {ticker} - API request failed for {target_expiry}: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {ticker} - Exception fetching {target_expiry}: {e}")
    
    if not all_candidates:
        print(f"INFO: {ticker} - No negative premium opportunities found")
        return []
    
    # Calculate combined score: premium income + negative premium protection
    for candidate in all_candidates:
        premium_income = candidate['premium']
        negative_premium = candidate['negative_premium_amount']
        probability = candidate['probability_above_strike']
        
        # Expected value calculation:
        # (Premium if not assigned * probability) + (Negative premium value if assigned * (1-probability))
        expected_value = (premium_income * probability) + (negative_premium * (1 - probability))
        
        # Also consider pure premium income potential
        premium_yield = (premium_income / candidate['strike']) * 100  # Annualized percentage
        
        # Combined score favors high premium with decent protection
        combined_score = (premium_income * 0.6) + (negative_premium * 0.4)
        
        candidate['expected_value'] = expected_value
        candidate['premium_yield'] = premium_yield
        candidate['combined_score'] = combined_score
    
    # Sort by combined score (favoring premium income but with negative premium protection)
    all_candidates.sort(key=lambda x: x['combined_score'], reverse=True)
    
    # Return top 3 candidates
    best_candidates = all_candidates[:3]
    
    print(f"SUCCESS: {ticker} - Found {len(all_candidates)} negative premium options, returning top {len(best_candidates)}")
    for i, candidate in enumerate(best_candidates):
        print(f"  {i+1}: ${candidate['strike']} put @ ${candidate['premium']:.2f} -> Premium: ${candidate['premium']:.2f} | If assigned: ${candidate['net_cost_basis']:.2f} (${candidate['negative_premium_amount']:.2f} negative) | Score: {candidate['combined_score']:.2f}")
    
    return best_candidates


def get_third_friday(year, month):
    """Calculate the 3rd Friday of the given month and year"""
    first_day = date(year, month, 1)
    first_friday = first_day + timedelta(days=(4 - first_day.weekday()) % 7)
    third_friday = first_friday + timedelta(days=14)
    return third_friday


def calculate_trading_days(start_date, end_date):
    """Calculate trading days between start and end date (excludes weekends)"""
    if start_date >= end_date:
        return 0
    
    trading_days = 0
    current = start_date + timedelta(days=1)
    
    while current <= end_date:
        if current.weekday() < 5:  # Monday=0, Friday=4
            trading_days += 1
        current += timedelta(days=1)
    
    return trading_days


def parse_xml_option_pairs(xml_response):
    """Parse the XML response to extract option data"""
    options = []
    try:
        root = ET.fromstring(xml_response)
        
        # Find all OptionPair elements
        for option_pair in root.findall('.//OptionPair'):
            put_element = option_pair.find('Put')
            if put_element is not None:
                symbol = put_element.find('displaySymbol')
                bid = put_element.find('bid')
                ask = put_element.find('ask')
                strike = put_element.find('strikePrice')
                
                if all(elem is not None for elem in [symbol, bid, ask, strike]):
                    symbol_text = symbol.text
                    bid_value = float(bid.text) if bid.text and bid.text != '0' else 0.0
                    ask_value = float(ask.text) if ask.text and ask.text != '0' else 0.0
                    strike_value = float(strike.text)
                    
                    # Only include options with valid bids
                    if bid_value > 0:
                        options.append({
                            'symbol': symbol_text,
                            'strike': strike_value,
                            'bid': bid_value,
                            'ask': ask_value
                        })
                        
    except ET.ParseError as e:
        print(f"Error parsing XML response: {e}")
    except Exception as e:
        print(f"Error extracting option data: {e}")
    
    return options
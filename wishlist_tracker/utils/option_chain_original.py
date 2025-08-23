"""
E*TRADE Option Chain Utility for Wishlist Tracker
------------------------------------------------
Fetches and analyzes put option chains for a given ticker using E*TRADE API.
Selects the 'best' put (highest premium, $5–$10 above current price) and two alternatives.
"""
import os
import sys
from datetime import datetime, timedelta

# Ensure the parent directory is in sys.path for import
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from etrade_auth import get_etrade_session


def fetch_put_option_chain(symbol, current_price, price_buffer=5, num_results=3, max_days=70):
    session, base_url = get_etrade_session()

    # --- Direct AMD Sept 19, 2025 Put Chain Request ---
    if symbol.upper() == "AMD":
        year, month, day = 2025, 9, 19  # Standard monthly expiration
        strike_near = 180  # Center around $180
        num_strikes = 10   # Pull 10 strikes around that level
        url_exp = (
            f"{base_url}/v1/market/optionchains.json?"
            f"symbol={symbol}&chainType=PUT"
            f"&expiryYear={year}&expiryMonth={month:02d}&expiryDay={day:02d}"
            f"&strikePriceNear={strike_near}&noOfStrikes={num_strikes}"
        )
    else:
        url_exp = f"{base_url}/v1/market/optionchains.json?symbol={symbol}&chainType=PUT"

    resp = session.get(url_exp)
    data = resp.json()
    # Fix: parse OptionChainResponse > OptionPair > Put
    chain = data.get('OptionChainResponse', {})
    option_pairs = chain.get('OptionPair', [])
    if not option_pairs:
        import json
        print(f"DEBUG: Raw option chain response for {symbol}: {json.dumps(data, indent=2)}")
        return []
    puts = []
    today = datetime.now().date()
    def is_third_friday(date):
        # 3rd Friday: weekday() == 4 (Friday), and 15th <= day <= 21st
        return date.weekday() == 4 and 15 <= date.day <= 21

    # Collect all puts by expiration, include those with no bid/ask
    exp_map = {}
    all_puts_raw = []
    # DEBUG: Print the first option pair's raw Put data for inspection
    import json
    if option_pairs:
        print(f"DEBUG: First option pair for {symbol}: {json.dumps(option_pairs[0], indent=2)}")

    for pair in option_pairs:
        opt_data = pair.get('Put', {})
        if not opt_data:
            continue
        display_symbol = opt_data.get('displaySymbol', '')
        bid = opt_data.get('bid')
        ask = opt_data.get('ask')
        strike = opt_data.get('strikePrice')
        try:
            parts = display_symbol.split()
            if len(parts) >= 5:
                month = parts[1]
                day = int(parts[2])
                year = int('20' + parts[3].replace("'", ""))
                exp_date = datetime.strptime(f"{year}-{month}-{day}", "%Y-%b-%d").date()
            else:
                continue
        except Exception:
            continue
        days_to_exp = (exp_date - today).days
        if days_to_exp < 0 or days_to_exp > max_days:
            continue
        # Only include standard monthly expirations (3rd Friday)
        if not is_third_friday(exp_date):
            continue
        # Accept puts even if no bid/ask, use lastPrice as fallback
        if bid is not None and ask is not None and bid > 0 and ask > 0:
            premium = (bid + ask) / 2
        elif bid is not None and bid > 0:
            premium = bid
        elif ask is not None and ask > 0:
            premium = ask
        else:
            # Fallback to lastPrice if available and > 0
            last_price = opt_data.get('lastPrice')
            if last_price is not None and last_price > 0:
                premium = last_price
            else:
                premium = None
        open_interest = opt_data.get('openInterest', '')
        net = strike - (premium or 0) if strike is not None and premium is not None else None
        net_diff = current_price - net if net is not None and current_price is not None else None
        put = {
            'strike': strike,
            'premium': premium,
            'bid': bid,
            'ask': ask,
            'expiration': exp_date.strftime('%Y-%m-%d'),
            'open_interest': open_interest,
            'days_to_exp': days_to_exp,
            'net': net,
            'net_diff': net_diff
        }
        exp_map.setdefault(exp_date, []).append(put)
        all_puts_raw.append(put)

    # Only consider expirations with at least 14 days left
    min_days_to_exp = 14
    future_exps = sorted([d for d in exp_map if (d - today).days >= min_days_to_exp])
    # Use up to two expirations
    exps_to_consider = future_exps[:2]


    # --- Adaptive Strike Selection ---
    # Configurable parameters
    min_pct = 0.15  # 15% above current price
    max_pct = 0.40  # 40% above current price
    min_strikes = 6

    # 1. Try proportional range
    min_strike = current_price * (1 + min_pct)
    max_strike = current_price * (1 + max_pct)
    puts_in_range = [p for p in all_puts_raw if p['strike'] is not None and min_strike <= p['strike'] <= max_strike]

    # 2. If not enough, use all strikes above current price (for nearest expiry)
    if len(puts_in_range) < min_strikes:
        # Find nearest expiry with puts
        if exps_to_consider:
            nearest_exp = exps_to_consider[0]
            puts_in_range = [p for p in exp_map[nearest_exp] if p['strike'] is not None and p['strike'] > current_price]

    # 3. If still not enough, use all strikes for both months
    if len(puts_in_range) < min_strikes:
        puts_in_range = [p for p in all_puts_raw if p['strike'] is not None]

    # Pick best premium-per-day put (net < current price)
    best_put = None
    best_yield = float('-inf')
    for p in puts_in_range:
        if p['net'] is not None and p['net'] < current_price and p['days_to_exp'] > 0 and p['premium']:
            yield_per_day = p['premium'] / p['days_to_exp']
            if yield_per_day > best_yield:
                best_yield = yield_per_day
                best_put = p

    # If no best_put found, pick the closest strike to current price as fallback target
    if not best_put:
        # Try to pick the put with strike just above current price
        puts_sorted = sorted([p for p in puts_in_range if p['strike'] is not None], key=lambda p: abs(p['strike'] - current_price))
        if puts_sorted:
            best_put = puts_sorted[0]
        else:
            # If still nothing, try all puts
            puts_sorted = sorted([p for p in all_puts_raw if p['strike'] is not None], key=lambda p: abs(p['strike'] - current_price))
            if puts_sorted:
                best_put = puts_sorted[0]
            else:
                # No puts at all, return [None, None, None]
                return [None, None, None]




    # Find closest below and above strikes from ALL available strikes (all expirations), but only valid puts
    def is_valid_put(p):
        return (
            p['strike'] is not None and
            p['premium'] is not None and
            p['days_to_exp'] > 0
        )

    all_strikes_sorted = sorted(
        [p for p in all_puts_raw if p['strike'] is not None],
        key=lambda p: (p['strike'], p['days_to_exp'])
    )
    target_strike = best_put['strike']
    below = None
    above = None
    # Always show the next strike below and above the target, even if not tradable
    for p in reversed(all_strikes_sorted):
        if p['strike'] < target_strike:
            below = p
            break
    for p in all_strikes_sorted:
        if p['strike'] > target_strike:
            above = p
            break
    target = best_put
    # If there is only one put, below/above may be None, that's fine
    return [below, target, above]

    # Show only puts with net assignment cost ABOVE current price
    filtered = [p for p in puts if p['net'] is not None and p['net'] > current_price]
    filtered.sort(key=lambda x: x['net_diff'])

    if filtered:
        result = filtered[:num_results]
    else:
        puts.sort(key=lambda p: abs(p['net'] - current_price))
        result = puts[:num_results]

    for p in result:
        print(f"AMD Sep25 Put Strike: {p['strike']} | Bid: {p['bid']} | Ask: {p['ask']} | Mid: {p['premium']:.2f}")

    return result
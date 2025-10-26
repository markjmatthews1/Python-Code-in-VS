import os
import sys
from datetime import datetime, timedelta, date
import xml.etree.ElementTree as ET

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from etrade_auth import get_etrade_session
from wishlist_tracker.utils.market_hours import is_market_open, should_use_planning_mode
from wishlist_tracker.utils.option_cache import save_option_cache, load_option_cache
from wishlist_tracker.utils.enhanced_put_strategy import score_put_strategy, generate_multiple_contract_strategies
# PHASE 3: Removed old trend_analysis imports (get_trend_signal, is_uptrend) - no longer used


def calculate_liquidity_score(spread_pct, open_interest, daily_volume, bid_size):
    """
    Calculate composite liquidity score (0-100)
    
    Higher score = better liquidity = easier fills
    
    Components:
    - Spread (40 pts): Tighter spread = better execution
    - Open Interest (30 pts): More existing positions = more liquid
    - Daily Volume (20 pts): More active trading = easier fills
    - Bid Size (10 pts): Larger bid = deeper market
    
    Args:
        spread_pct: Bid-ask spread as percentage
        open_interest: Total open contracts for this strike
        daily_volume: Contracts traded today
        bid_size: Number of contracts at bid price
    
    Returns:
        int: Liquidity score (0-100)
    """
    score = 0
    
    # Spread component (40 points max) - Most important for execution
    if spread_pct < 10:
        score += 40  # Excellent spread
    elif spread_pct < 20:
        score += 25  # Good spread
    elif spread_pct < 30:
        score += 10  # Acceptable spread
    # else: 0 points for wide spread
    
    # Open Interest component (30 points max) - Indicates market liquidity
    if open_interest > 1000:
        score += 30  # Highly liquid
    elif open_interest > 500:
        score += 20  # Good liquidity
    elif open_interest > 100:
        score += 10  # Acceptable
    # else: 0 points for thin market
    
    # Daily Volume component (20 points max) - Shows today's activity
    if daily_volume > 500:
        score += 20  # Very active
    elif daily_volume > 200:
        score += 15  # Active
    elif daily_volume > 50:
        score += 5   # Some activity
    # else: 0 points for inactive
    
    # Bid Size component (10 points max) - Immediate fillability
    if bid_size >= 100:
        score += 10  # Deep market
    elif bid_size >= 50:
        score += 5   # Decent depth
    # else: 0 points for thin bid
    
    return score


def format_liquidity_display(score):
    """
    Format liquidity score with text indicator for display.
    
    Note: Scores below 40 are filtered out during option selection,
    so this function only handles the three viable liquidity tiers.
    
    Args:
        score: Liquidity score (0-100)
        
    Returns:
        Text indicator (HIGH/GOOD/FAIR)
    """
    if score >= 80:
        return "HIGH"  # Excellent - tight spreads, high volume/OI
    elif score >= 60:
        return "GOOD"  # Good - acceptable for most trades
    elif score >= 40:
        return "FAIR"  # Fair - watch for slippage, use limit orders
    else:
        # Should never reach here since we filter out <40
        return "POOR"  # Poor (filtered out)


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
    """Fetch put options for 2 months, find best negative premium with probability analysis
    
    Market-aware filtering:
    - During market hours: Stricter filters (requires valid bid/ask with reasonable spreads)
    - During closed hours (pre-market/after-hours/weekend): Planning mode
      * Shows options even without perfect negative premiums
      * Accepts any bid > 0 (ignores size since it's often 0 after hours)
      * Wider strike range for better planning
    """
    print(f"\n{'='*60}")
    print(f"🎯 fetch_put_option_chain({ticker}, current_price=${current_price})")
    print(f"{'='*60}")
    
    if not current_price or current_price <= 0:
        print(f"❌ {ticker} - Invalid current_price: {current_price}")
        return []
    
    session_result = get_etrade_session()
    if not session_result:
        print(f"❌ {ticker} - Failed to get E*Trade session")
        return []
    
    session, base_url = session_result
    
    # Check market status for filtering mode
    is_open, market_msg, market_state = is_market_open()
    planning_mode = should_use_planning_mode()
    
    # During closed hours, try to load cached data from previous session
    if planning_mode:
        cached_options, cache_age = load_option_cache(ticker)
        if cached_options and len(cached_options) > 0:
            print(f"💾 {ticker} - Using cached data from {cache_age:.1f} hours ago ({len(cached_options)} options)")
            # Return cached results directly (already scored and sorted)
            return cached_options
        else:
            print(f"🌙 {ticker} - No cache available, attempting live fetch (may return empty)")
    
    # Log market mode
    mode_str = "PLANNING MODE" if planning_mode else "LIVE MODE"
    print(f"📊 {mode_str}: {ticker} - Market {market_state}, using ROI-based filtering")
    
    # Get target expiration dates (implements 5 trading days rule)
    target_expiries = get_target_expiration_dates()
    print(f"DEBUG: {ticker} - Checking {len(target_expiries)} expiration dates")
    
    all_candidates = []  # All options passing ROI filter
    
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
                print(f"DEBUG: {ticker} - Parsed {len(options)} put options with bid>0 for {target_expiry}")
                
                # Filter options using ROI-based logic (Phase 1)
                days_to_expiry = (target_expiry - date.today()).days
                
                # Calculate minimum required ROI (0.33% per day)
                min_daily_roi = 0.33
                min_total_roi = min_daily_roi * days_to_expiry
                
                print(f"  📊 Days to expiry: {days_to_expiry}, Min ROI required: {min_total_roi:.1f}%")
                
                filtered_by_spread = 0
                filtered_by_roi = 0
                filtered_by_premium = 0
                filtered_by_liquidity = 0  # PHASE 2: Track liquidity rejections
                added_count = 0
                
                for opt in options:
                    strike = opt['strike']
                    bid = opt['bid']
                    ask = opt.get('ask', bid * 1.1)  # Default ask if missing
                    
                    # Hard Filter 1: Minimum absolute premium ($2.00/share = $200/contract)
                    if bid < 2.00:
                        filtered_by_premium += 1
                        continue
                    
                    # Hard Filter 2: Bid-ask spread quality
                    # During market hours: Reject if >30% (likely stale/bad data)
                    # During closed hours: Reject if >50% (more lenient for planning)
                    max_spread = 30 if is_open else 50
                    
                    if bid > 0 and ask > 0:
                        spread_pct = ((ask - bid) / bid) * 100
                        if spread_pct > max_spread:
                            filtered_by_spread += 1
                            continue
                    
                    # NEW: ROI-based filtering (NO strike distance limits!)
                    # Calculate daily ROI
                    total_roi = (bid / strike) * 100
                    daily_roi = total_roi / days_to_expiry
                    
                    # Hard Filter 3: Minimum ROI threshold
                    if daily_roi < min_daily_roi:
                        filtered_by_roi += 1
                        continue
                    
                    # Passed all filters - calculate additional metrics
                    net_cost_basis = strike - bid
                    negative_premium = current_price - net_cost_basis
                    
                    # Calculate quality flags
                    is_negative_premium = negative_premium > 0
                    premium_ratio = (bid / strike) * 100
                    is_reasonable = premium_ratio <= 40
                    
                    probability = calculate_probability_above_strike(current_price, strike, days_to_expiry)
                    
                    # PHASE 2: Calculate liquidity score
                    liquidity_score = calculate_liquidity_score(
                        spread_pct=spread_pct,
                        open_interest=opt.get('open_interest', 0),
                        daily_volume=opt.get('daily_volume', 0),
                        bid_size=opt.get('bid_size', 0)
                    )
                    
                    # Hard Filter 4: Minimum liquidity threshold (reject poor liquidity)
                    # If liquidity score < 40, option is not a viable trade candidate
                    if liquidity_score < 40:
                        filtered_by_liquidity += 1
                        continue
                    
                    liquidity_display = format_liquidity_display(liquidity_score)
                    
                    # ENHANCED: Use new scoring system for quality assessment
                    # Default to NEUTRAL trend (can be enhanced later with analyst ratings)
                    enhanced_score_data = score_put_strategy(
                        current_price=current_price,
                        strike=strike,
                        premium=bid,
                        days_to_expiry=days_to_expiry,
                        trend_direction="NEUTRAL",  # TODO: Integrate analyst ratings
                        liquidity_score=liquidity_score
                    )
                    
                    candidate = {
                        'strike': strike,
                        'premium': bid,
                        'expiration': target_expiry.strftime('%m/%d'),
                        'net_cost_basis': enhanced_score_data['cost_basis'],
                        'negative_premium_amount': enhanced_score_data['cushion_dollars'],
                        'net_diff': enhanced_score_data['cushion_dollars'],  # GUI expects this field name
                        'probability_above_strike': probability,
                        'days_to_expiry': days_to_expiry,
                        'expiry_date': target_expiry,
                        'is_negative_premium': enhanced_score_data['cushion_dollars'] > 0,
                        'premium_ratio': premium_ratio,
                        'is_reasonable': is_reasonable,
                        'spread_pct': spread_pct if bid > 0 else 0,
                        'is_planning_mode': planning_mode,
                        # NEW ROI metrics
                        'daily_roi': daily_roi,
                        'total_roi': total_roi,
                        'premium_dollars': bid * 100,  # Per contract
                        # PHASE 2: Liquidity metrics
                        'liquidity_score': liquidity_score,
                        'liquidity_display': liquidity_display,
                        'open_interest': opt.get('open_interest', 0),
                        'daily_volume': opt.get('daily_volume', 0),
                        'bid_size': opt.get('bid_size', 0),
                        'ask_size': opt.get('ask_size', 0),
                        # ENHANCED: New scoring metrics
                        'enhanced_score': enhanced_score_data['final_score'],
                        'cost_basis_score': enhanced_score_data['cost_basis_score'],
                        'premium_score': enhanced_score_data['premium_score'],
                        'time_score': enhanced_score_data['time_score'],
                        'cushion_score': enhanced_score_data['cushion_score'],
                        'cushion_percent': enhanced_score_data['cushion_percent'],
                        'premium_per_day': enhanced_score_data['premium_per_day'],
                        'premium_yield': enhanced_score_data['premium_yield'],
                        'strike_vs_current': enhanced_score_data['strike_vs_current'],
                    }
                    
                    all_candidates.append(candidate)
                    added_count += 1
                
                print(f"  🔍 Filter results: spread={filtered_by_spread}, roi={filtered_by_roi}, premium={filtered_by_premium}, liquidity={filtered_by_liquidity}, added={added_count}")
                            
            else:
                print(f"ERROR: {ticker} - API request failed for {target_expiry}: {response.status_code}")
                
        except Exception as e:
            print(f"ERROR: {ticker} - Exception fetching {target_expiry}: {e}")
    
    if not all_candidates:
        print(f"❌ {ticker} - NO OPTIONS FOUND after filtering")
        print(f"   (All options failed: premium<$2.00, ROI<{min_daily_roi:.2f}%/day, spread>{ max_spread}%, or liquidity<40)")
        return []
    
    print(f"✅ {ticker} - Found {len(all_candidates)} candidates passing ROI filter")
    
    # ENHANCED SCORING: Prioritize overall quality (cost basis + premium + time efficiency)
    # Sort by enhanced_score (highest first) - balances all factors
    all_candidates.sort(key=lambda x: x['enhanced_score'], reverse=True)
    
    # Return top 3 candidates by enhanced score
    best_candidates = all_candidates[:3]
    
    print(f"🎯 SUCCESS: {ticker} - Returning top {len(best_candidates)} by enhanced score:")
    for i, candidate in enumerate(best_candidates, 1):
        print(f"  {i}. ${candidate['strike']:.0f} @ ${candidate['premium']:.2f} ({candidate['expiration']}) → "
              f"Score: {candidate['enhanced_score']:.1f}/100 | Cost Basis: ${candidate['net_cost_basis']:.2f} | "
              f"Cushion: {candidate['cushion_percent']:.1f}% | Premium/Day: ${candidate['premium_per_day']:.2f}")
    
    # Cache the results if market is open (for use during next closed session)
    if is_open and best_candidates:
        save_option_cache(ticker, best_candidates)
    
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
    total_found = 0
    zero_bid_count = 0
    
    try:
        root = ET.fromstring(xml_response)
        
        # Find all OptionPair elements
        for option_pair in root.findall('.//OptionPair'):
            put_element = option_pair.find('Put')
            if put_element is not None:
                total_found += 1
                symbol = put_element.find('displaySymbol')
                bid = put_element.find('bid')
                ask = put_element.find('ask')
                strike = put_element.find('strikePrice')
                
                # PHASE 2: Extract liquidity metrics
                open_interest = put_element.find('openInterest')
                volume = put_element.find('volume')
                bid_size = put_element.find('bidSize')
                ask_size = put_element.find('askSize')
                
                if all(elem is not None for elem in [symbol, bid, ask, strike]):
                    symbol_text = symbol.text
                    bid_value = float(bid.text) if bid.text and bid.text != '0' else 0.0
                    ask_value = float(ask.text) if ask.text and ask.text != '0' else 0.0
                    strike_value = float(strike.text)
                    
                    # PHASE 2: Parse liquidity data with safe defaults
                    open_interest_value = int(open_interest.text) if open_interest is not None and open_interest.text else 0
                    volume_value = int(volume.text) if volume is not None and volume.text else 0
                    bid_size_value = int(bid_size.text) if bid_size is not None and bid_size.text else 0
                    ask_size_value = int(ask_size.text) if ask_size is not None and ask_size.text else 0
                    
                    # DEBUG: Log what we're seeing
                    if total_found <= 5:  # Log first 5 for debugging
                        print(f"  📊 Parse: Strike=${strike_value:.2f}, Bid=${bid_value:.2f}, Ask=${ask_value:.2f}, OI={open_interest_value}, Vol={volume_value}")
                    
                    # Only include options with valid bids
                    if bid_value > 0:
                        options.append({
                            'symbol': symbol_text,
                            'strike': strike_value,
                            'bid': bid_value,
                            'ask': ask_value,
                            # PHASE 2: Add liquidity metrics
                            'open_interest': open_interest_value,
                            'daily_volume': volume_value,
                            'bid_size': bid_size_value,
                            'ask_size': ask_size_value
                        })
                    else:
                        zero_bid_count += 1
        
        print(f"  ✅ Parsed: {total_found} total, {len(options)} with bid>0, {zero_bid_count} with bid=0")
                        
    except ET.ParseError as e:
        print(f"❌ Error parsing XML response: {e}")
    except Exception as e:
        print(f"❌ Error extracting option data: {e}")
    
    return options
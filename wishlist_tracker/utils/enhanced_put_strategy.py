"""
Enhanced Put Selection Strategy
================================

Implements capital-efficient put selling strategy that optimizes for:
1. Best cost basis if assigned (lowest entry price)
2. Maximum premium with minimum capital outlay
3. Strikes BELOW current price (safety first)
4. Premium per day efficiency (time value)
5. Directional bias (stock trend analysis)

Key Principles:
- Multiple contracts at lower strikes > 1 contract at high strike
- Target $2+ premium minimum, prefer $5-6+
- Avoid assignment traps (deep ITM puts)
- Consider stock trend for strike selection
"""

from datetime import date
from typing import List, Dict, Optional, Tuple


def calculate_cost_basis(strike: float, premium: float) -> float:
    """Calculate the effective cost basis if assigned"""
    return strike - premium


def calculate_downside_cushion(current_price: float, cost_basis: float) -> Tuple[float, float]:
    """
    Calculate downside protection cushion
    
    Returns:
        (cushion_dollars, cushion_percent)
    """
    cushion_dollars = current_price - cost_basis
    cushion_percent = (cushion_dollars / current_price) * 100 if current_price > 0 else 0
    return cushion_dollars, cushion_percent


def calculate_premium_per_day(premium: float, days_to_expiry: int) -> float:
    """Calculate daily premium value for time efficiency comparison"""
    return premium / days_to_expiry if days_to_expiry > 0 else 0


def score_put_strategy(
    current_price: float,
    strike: float,
    premium: float,
    days_to_expiry: int,
    trend_direction: str = "NEUTRAL",  # STRONG_UP, UP, NEUTRAL, DOWN, STRONG_DOWN
    liquidity_score: int = 50
) -> Dict:
    """
    Score a put selling opportunity based on multiple factors
    
    Scoring Components:
    - Cost Basis (30%): Lower = better (want cheap stock if assigned)
    - Premium Dollars (25%): Higher = better (more income)
    - Time Efficiency (20%): Higher premium/day = better
    - Safety Cushion (15%): Higher = better (more protection)
    - Liquidity (10%): Higher = better (easier fills)
    
    Returns:
        Dict with scores and metrics
    """
    
    # Calculate base metrics
    cost_basis = calculate_cost_basis(strike, premium)
    cushion_dollars, cushion_pct = calculate_downside_cushion(current_price, cost_basis)
    premium_per_day = calculate_premium_per_day(premium, days_to_expiry)
    premium_yield = (premium / strike) * 100
    
    # Scoring components (0-100 each)
    
    # 1. Cost Basis Score (30%) - Lower cost basis = higher score
    # Best if cost basis is 10-20% below current
    cost_basis_pct_below = ((current_price - cost_basis) / current_price) * 100
    if cost_basis_pct_below >= 20:
        cost_basis_score = 100  # Excellent
    elif cost_basis_pct_below >= 15:
        cost_basis_score = 85
    elif cost_basis_pct_below >= 10:
        cost_basis_score = 70
    elif cost_basis_pct_below >= 5:
        cost_basis_score = 50
    elif cost_basis_pct_below >= 0:
        cost_basis_score = 25
    else:
        cost_basis_score = 0  # Underwater - bad!
    
    # 2. Premium Dollars Score (25%) - Higher premium = higher score
    if premium >= 6.00:
        premium_score = 100  # Excellent ($600+/contract)
    elif premium >= 5.00:
        premium_score = 85
    elif premium >= 4.00:
        premium_score = 70
    elif premium >= 3.00:
        premium_score = 55
    elif premium >= 2.00:
        premium_score = 40  # Minimum acceptable
    else:
        premium_score = 0  # Below minimum
    
    # 3. Time Efficiency Score (20%) - Premium per day
    # Good daily premium: $0.15-0.30+
    if premium_per_day >= 0.30:
        time_score = 100  # Excellent time value
    elif premium_per_day >= 0.20:
        time_score = 80
    elif premium_per_day >= 0.15:
        time_score = 60
    elif premium_per_day >= 0.10:
        time_score = 40
    else:
        time_score = 20  # Poor time value
    
    # 4. Safety Cushion Score (15%) - Downside protection
    if cushion_pct >= 20:
        cushion_score = 100  # Very safe
    elif cushion_pct >= 15:
        cushion_score = 80
    elif cushion_pct >= 10:
        cushion_score = 60
    elif cushion_pct >= 5:
        cushion_score = 40
    elif cushion_pct >= 0:
        cushion_score = 20
    else:
        cushion_score = 0  # Underwater
    
    # 5. Liquidity Score (10%) - Already calculated, just normalize
    liquidity_normalized = liquidity_score  # 0-100
    
    # Trend Adjustment Factor (multiplier, not additive)
    # Adjust strike appropriateness based on trend
    strike_vs_current = strike / current_price
    
    if trend_direction == "STRONG_UP":
        # Can be more aggressive with higher strikes (closer to current)
        if 0.95 <= strike_vs_current <= 1.00:
            trend_multiplier = 1.10  # Reward near-ATM puts in uptrend
        elif 0.90 <= strike_vs_current < 0.95:
            trend_multiplier = 1.00
        else:
            trend_multiplier = 0.95  # Too far OTM might miss opportunity
    
    elif trend_direction == "UP":
        if 0.90 <= strike_vs_current <= 0.98:
            trend_multiplier = 1.05
        else:
            trend_multiplier = 1.00
    
    elif trend_direction in ["NEUTRAL", "SIDEWAYS"]:
        if 0.85 <= strike_vs_current <= 0.95:
            trend_multiplier = 1.00  # Sweet spot
        else:
            trend_multiplier = 0.95
    
    elif trend_direction == "DOWN":
        # Need wider cushion in downtrend
        if 0.75 <= strike_vs_current <= 0.90:
            trend_multiplier = 1.05  # Reward safer strikes
        elif 0.90 <= strike_vs_current <= 0.95:
            trend_multiplier = 1.00
        else:
            trend_multiplier = 0.90  # Too close to current in downtrend
    
    elif trend_direction == "STRONG_DOWN":
        # Very conservative in strong downtrend
        if 0.70 <= strike_vs_current <= 0.85:
            trend_multiplier = 1.10  # Reward very safe strikes
        elif 0.85 <= strike_vs_current <= 0.90:
            trend_multiplier = 1.00
        else:
            trend_multiplier = 0.85  # Risky in strong downtrend
    
    else:
        trend_multiplier = 1.00
    
    # Calculate weighted total score (before trend adjustment)
    weighted_score = (
        cost_basis_score * 0.30 +      # 30% weight
        premium_score * 0.25 +          # 25% weight
        time_score * 0.20 +             # 20% weight
        cushion_score * 0.15 +          # 15% weight
        liquidity_normalized * 0.10     # 10% weight
    )
    
    # Apply trend multiplier
    final_score = weighted_score * trend_multiplier
    
    return {
        'final_score': final_score,
        'cost_basis': cost_basis,
        'cost_basis_score': cost_basis_score,
        'premium_score': premium_score,
        'time_score': time_score,
        'cushion_score': cushion_score,
        'liquidity_score': liquidity_normalized,
        'trend_multiplier': trend_multiplier,
        'cushion_dollars': cushion_dollars,
        'cushion_percent': cushion_pct,
        'premium_per_day': premium_per_day,
        'premium_yield': premium_yield,
        'strike_vs_current': strike_vs_current * 100,  # As percentage
    }


def generate_multiple_contract_strategies(
    current_price: float,
    options: List[Dict],
    max_capital: float = 10000,
    trend_direction: str = "NEUTRAL"
) -> List[Dict]:
    """
    Generate strategies with multiple contracts at different strikes
    to compare capital efficiency
    
    For example, with $10k capital:
    - Option A: 1x $100 strike
    - Option B: 2x $50 strike  
    - Option C: 3x $33 strike
    
    Args:
        current_price: Current stock price
        options: List of option dictionaries from fetch_put_option_chain
        max_capital: Maximum capital to allocate (default $10k)
        trend_direction: Stock trend for scoring adjustment
    
    Returns:
        List of strategy dictionaries sorted by best score
    """
    
    strategies = []
    
    for opt in options:
        strike = opt['strike']
        premium = opt['premium']
        days_to_expiry = opt['days_to_expiry']
        liquidity = opt.get('liquidity_score', 50)
        
        # Skip if premium too low
        if premium < 2.00:
            continue
        
        # Calculate how many contracts we can sell with available capital
        capital_per_contract = strike * 100  # Each contract = 100 shares
        max_contracts = int(max_capital / capital_per_contract)
        
        if max_contracts == 0:
            continue  # Strike too high for our capital
        
        # Generate strategies for 1, 2, and 3 contracts (if possible)
        for num_contracts in range(1, min(max_contracts + 1, 4)):  # Max 3 contracts
            
            total_capital_required = capital_per_contract * num_contracts
            total_premium = premium * num_contracts * 100  # Premium per contract
            total_cost_basis = calculate_cost_basis(strike, premium) * num_contracts * 100
            
            # Score this strategy
            score_data = score_put_strategy(
                current_price=current_price,
                strike=strike,
                premium=premium,
                days_to_expiry=days_to_expiry,
                trend_direction=trend_direction,
                liquidity_score=liquidity
            )
            
            strategy = {
                'num_contracts': num_contracts,
                'strike': strike,
                'premium_per_contract': premium,
                'total_premium': total_premium,
                'capital_required': total_capital_required,
                'cost_basis_per_share': score_data['cost_basis'],
                'total_cost_if_assigned': total_cost_basis,
                'cushion_dollars': score_data['cushion_dollars'] * num_contracts * 100,
                'cushion_percent': score_data['cushion_percent'],
                'premium_per_day': score_data['premium_per_day'] * num_contracts,
                'days_to_expiry': days_to_expiry,
                'expiration': opt['expiration'],
                'score': score_data['final_score'],
                'score_breakdown': score_data,
                'liquidity_display': opt.get('liquidity_display', 'UNKNOWN'),
                'trend_direction': trend_direction,
            }
            
            strategies.append(strategy)
    
    # Sort by score (highest first)
    strategies.sort(key=lambda x: x['score'], reverse=True)
    
    return strategies


def format_strategy_comparison(
    ticker: str,
    current_price: float,
    strategies: List[Dict],
    top_n: int = 5
) -> str:
    """
    Format strategy comparison for display
    
    Returns formatted string showing top strategies
    """
    
    if not strategies:
        return f"No viable strategies found for {ticker}"
    
    output = []
    output.append(f"\n{'='*70}")
    output.append(f"PUT SELLING STRATEGIES: {ticker} @ ${current_price:.2f}")
    output.append(f"{'='*70}\n")
    
    for i, strategy in enumerate(strategies[:top_n], 1):
        rank_emoji = "🏆" if i == 1 else "✅" if i <= 3 else "📊"
        
        output.append(f"{rank_emoji} STRATEGY #{i} (Score: {strategy['score']:.1f}/100)")
        output.append(f"{'─'*70}")
        output.append(f"  Contracts:        {strategy['num_contracts']}x ${strategy['strike']:.0f} strike @ ${strategy['premium_per_contract']:.2f} premium")
        output.append(f"  Expiration:       {strategy['expiration']} ({strategy['days_to_expiry']} days)")
        output.append(f"  ")
        output.append(f"  💰 FINANCIALS:")
        output.append(f"     Capital Required:    ${strategy['capital_required']:,.0f}")
        output.append(f"     Total Premium:       ${strategy['total_premium']:,.0f}")
        output.append(f"     Premium/Day:         ${strategy['premium_per_day']:.2f}")
        output.append(f"  ")
        output.append(f"  📊 IF ASSIGNED:")
        output.append(f"     Cost Basis/Share:    ${strategy['cost_basis_per_share']:.2f}")
        output.append(f"     Total Cost:          ${strategy['total_cost_if_assigned']:,.0f}")
        output.append(f"     Cushion:             ${strategy['cushion_dollars']:,.0f} ({strategy['cushion_percent']:.1f}%)")
        output.append(f"  ")
        output.append(f"  🎯 QUALITY:")
        output.append(f"     Liquidity:           {strategy['liquidity_display']}")
        output.append(f"     Trend Match:         {strategy['trend_direction']}")
        output.append(f"")
    
    return "\n".join(output)

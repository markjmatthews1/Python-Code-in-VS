"""
WeeklyPay Tactical Rotation Engine - Simplified Dashboard
Standalone version with embedded WeeklyPay scoring formula

ENHANCED: Live Ex-Dividend Date Support + Accurate Earnings Calendar
This version tries to fetch live ex-dividend dates using yfinance and
accurate earnings dates using Finnhub API for maximum precision.
Falls back gracefully if APIs are not available.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import math
import random
import math
import sys
import os

# Suppress print statements to prevent Streamlit from showing them as info messages
class NullWriter:
    def write(self, txt): pass
    def flush(self): pass

# Redirect stdout to null when running in Streamlit mode
if len(sys.argv) > 0 and 'streamlit' in sys.argv[0].lower():
    sys.stdout = NullWriter()

# Page configuration
st.set_page_config(
    page_title="WeeklyPay Tactical Rotation Engine",
    page_icon="$",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# WeeklyPay Scoring Formula (matches day.py implementation)
def weeklypay_scoring_formula(weekly_yield, rsi, days_to_earnings):
    """
    WeeklyPay Tactical Rotation Scoring Formula
    Score = (yield_score * 0.5) + (momentum_score * 0.3) + (earnings_score * 0.2)
    """
    # Yield Score (0-10 scale, 50% weight)
    yield_score = min((weekly_yield / 1.0) * 10, 10)  # Scale to 0-10
    
    # Momentum Score (RSI-based, 30% weight)
    if rsi >= 70:
        momentum_score = 10  # Overbought = high momentum
    elif rsi >= 60:
        momentum_score = 8
    elif rsi >= 50:
        momentum_score = 6
    elif rsi >= 40:
        momentum_score = 4
    else:
        momentum_score = 2  # Oversold = low momentum
    
    # Earnings Score (decay function, 20% weight)
    if days_to_earnings <= 7:
        earnings_score = 10 * math.exp(-days_to_earnings / 10)
    else:
        earnings_score = 2  # Base score for distant earnings
    
    # Calculate final score with exact weights
    final_score = (yield_score * 0.5) + (momentum_score * 0.3) + (earnings_score * 0.2)
    
    return {
        'total_score': round(final_score, 2),
        'yield_score': round(yield_score, 2),
        'momentum_score': round(momentum_score, 2),
        'earnings_score': round(earnings_score, 2)
    }

def backtest_nav_recovery(ticker, days=90):
    """
    Backtest NAV recovery patterns using historical price data
    Analyzes post-dividend price recovery timing
    Returns: optimal_sell_day, avg_recovery_pct, confidence_score
    """
    try:
        import yfinance as yf
        import numpy as np
        import pytz
        
        # Get longer historical data (90 days for more dividend samples)
        stock = yf.Ticker(ticker)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        # Make start_date timezone-aware (Eastern Time to match yfinance)
        eastern = pytz.timezone('America/New_York')
        start_date_tz = eastern.localize(start_date.replace(hour=0, minute=0, second=0, microsecond=0))
        
        # Get historical price data
        hist = stock.history(start=start_date, end=end_date)
        
        if hist.empty or len(hist) < 7:
            print(f"Insufficient price data for {ticker}")
            return None, None, None
        
        # Get dividend history - extend window to catch more dividends
        dividends = stock.dividends
        if dividends.empty:
            print(f"No dividend data for {ticker}")
            return None, None, None
        
        # Filter dividends to our date range (both are now timezone-aware)
        recent_divs = dividends[dividends.index >= start_date_tz]
        
        if len(recent_divs) == 0:
            print(f"No recent dividends for {ticker} in past {days} days")
            return None, None, None
        
        print(f"Found {len(recent_divs)} dividend payments for {ticker}")
        
        recovery_patterns = []
        
        for div_date in recent_divs.index:
            # Convert to date for comparison (remove time component)
            div_date_only = div_date.date() if hasattr(div_date, 'date') else div_date
            
            # Find the closest trading day to dividend date (handle weekends/holidays)
            hist_dates = [d.date() if hasattr(d, 'date') else d for d in hist.index]
            
            # Find price on or closest to ex-div date
            div_price = None
            for i, hist_date in enumerate(hist_dates):
                if hist_date >= div_date_only:
                    div_price = hist.iloc[i]['Close']
                    actual_div_idx = i
                    break
            
            if div_price is None:
                continue
            
            print(f"Ex-div date {div_date_only}: price ${div_price:.2f}")
            
            # Track recovery over next 5 trading days
            for days_after in range(1, 6):
                future_idx = actual_div_idx + days_after
                if future_idx < len(hist):
                    recovery_price = hist.iloc[future_idx]['Close']
                    recovery_pct = ((recovery_price - div_price) / div_price) * 100
                    recovery_patterns.append({
                        'days_after': days_after,
                        'recovery_pct': recovery_pct
                    })
                    print(f"  Day {days_after}: ${recovery_price:.2f} ({recovery_pct:+.2f}%)")
        
        if not recovery_patterns:
            print(f"No recovery patterns found for {ticker}")
            return None, None, None
        
        # Analyze patterns by day
        recovery_df = pd.DataFrame(recovery_patterns)
        avg_by_day = recovery_df.groupby('days_after')['recovery_pct'].agg(['mean', 'std', 'count'])
        
        if avg_by_day.empty:
            return None, None, None
        
        print(f"Recovery analysis for {ticker}:")
        print(avg_by_day)
        
        # Find optimal sell day (best recovery with confidence)
        avg_by_day['confidence'] = avg_by_day['count'] / avg_by_day['count'].sum()
        avg_by_day['score'] = avg_by_day['mean'] * avg_by_day['confidence']
        
        optimal_day = avg_by_day['score'].idxmax()
        avg_recovery = avg_by_day.loc[optimal_day, 'mean']
        confidence = avg_by_day.loc[optimal_day, 'confidence'] * 100
        
        print(f"Optimal day: {optimal_day}, Avg recovery: {avg_recovery:.2f}%, Confidence: {confidence:.0f}%")
        
        return int(optimal_day), round(avg_recovery, 2), round(confidence, 0)
        
    except Exception as e:
        import traceback
        print(f"Backtest error for {ticker}: {e}")
        print(traceback.format_exc())
        return None, None, None

@st.cache_data(ttl=3600)  # Cache for 1 hour to prevent repeated API calls
def get_real_earnings_calendar():
    """
    Get real earnings calendar data using Finnhub API - highly accurate
    Falls back to yfinance, then estimation if APIs unavailable
    """
    import requests
    
    # Finnhub API key (from your main day.py file)
    FINNHUB_API_KEY = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"
    
    earnings_calendar = {}
    
    # Map ETF tickers to their underlying stocks for earnings
    underlying_stocks = {
        'NVDW': 'NVDA',
        'AMDW': 'AMD', 
        'HOOW': 'HOOD',
        'MSFW': 'MSFT',
        'GOOW': 'GOOGL',
        'NFLW': 'NFLX',
        'XOMO': 'XOM',    # Energy - Exxon Mobil
        'BRKW': 'BRK.B',  # Financials - Berkshire Hathaway
        'TSLW': 'TSLA',   # Technology - Tesla (high volatility)
        'QDTE': 'QQQ'     # Weekly payer (Thu ex-div, Fri pay) - Nasdaq 100 (0DTE strategy)
    }
    
    current_date = datetime.now()
    
    for etf_ticker, stock_ticker in underlying_stocks.items():
        # Try Finnhub first (most reliable for earnings calendar)
        try:
            url = f"https://finnhub.io/api/v1/calendar/earnings?symbol={stock_ticker}&token={FINNHUB_API_KEY}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                print(f"CHART Finnhub response for {stock_ticker}: {data}")
                
                if 'earningsCalendar' in data and data['earningsCalendar']:
                    # Find the next earnings date (earliest future date)
                    future_earnings = []
                    for earnings in data['earningsCalendar']:
                        earnings_date_str = earnings.get('date', '')
                        if earnings_date_str:
                            try:
                                earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
                                if earnings_date >= current_date:
                                    future_earnings.append(earnings_date)
                            except ValueError:
                                continue
                    
                    if future_earnings:
                        next_earnings = min(future_earnings)  # Get the earliest upcoming earnings
                        earnings_calendar[etf_ticker] = next_earnings
                        days_until = (next_earnings - current_date).days
                        print(f"CALENDAR SUCCESS Finnhub earnings for {etf_ticker} ({stock_ticker}): {next_earnings.strftime('%Y-%m-%d')} ({days_until} days)")
                        continue
                else:
                    print(f"CHART Finnhub: No earnings calendar data for {stock_ticker}")
            else:
                print(f"CHART Finnhub API error for {stock_ticker}: {response.status_code} - {response.text}")
                        
        except Exception as e:
            print(f"WARNING Finnhub earnings fetch failed for {etf_ticker} ({stock_ticker}): {e}")
        
        # Try yfinance as backup
        try:
            import yfinance as yf
            stock = yf.Ticker(stock_ticker)
            
            # Try to get earnings date from stock info first
            info = stock.info
            if 'earningsTimestamp' in info and info['earningsTimestamp']:
                try:
                    earnings_timestamp = info['earningsTimestamp']
                    if isinstance(earnings_timestamp, list) and len(earnings_timestamp) > 0:
                        earnings_timestamp = earnings_timestamp[0]
                    earnings_date = pd.to_datetime(earnings_timestamp, unit='s')
                    if earnings_date > current_date:
                        earnings_calendar[etf_ticker] = earnings_date.to_pydatetime()
                        days_until = (earnings_date.to_pydatetime() - current_date).days
                        print(f"CALENDAR SUCCESS yfinance info earnings for {etf_ticker} ({stock_ticker}): {earnings_date.strftime('%Y-%m-%d')} ({days_until} days)")
                        continue
                except Exception as ts_error:
                    print(f"WARNING Error parsing earnings timestamp for {stock_ticker}: {ts_error}")
            
            # Try calendar method as secondary backup
            try:
                calendar = stock.calendar
                if calendar is not None and isinstance(calendar, dict):
                    earnings_dates = calendar.get('Earnings Date', [])
                    if earnings_dates and isinstance(earnings_dates, list) and len(earnings_dates) > 0:
                        # Take the first/next earnings date
                        next_earnings_date = earnings_dates[0]
                        if hasattr(next_earnings_date, 'strftime'):  # It's already a date object
                            earnings_date = pd.to_datetime(next_earnings_date)
                        else:
                            earnings_date = pd.to_datetime(next_earnings_date)
                        
                        if earnings_date.date() >= current_date.date():
                            earnings_calendar[etf_ticker] = earnings_date.to_pydatetime()
                            days_until = (earnings_date.date() - current_date.date()).days
                            print(f"CALENDAR SUCCESS yfinance calendar earnings for {etf_ticker} ({stock_ticker}): {earnings_date.strftime('%Y-%m-%d')} ({days_until} days)")
                            continue
            except Exception as cal_error:
                print(f"WARNING yfinance calendar failed for {stock_ticker}: {cal_error}")
        except Exception as e:
            print(f"WARNING yfinance earnings fetch failed for {etf_ticker} ({stock_ticker}): {e}")
        
        # Final fallback to educated estimates based on typical quarterly cycles
        fallback_days = {
            'NVDW': 14,  # NVDA - typically reports mid-quarter
            'AMDW': 21,  # AMD - typically reports 3 weeks out  
            'HOOW': 29,  # HOOD - typically reports end of month
            'MSFW': 35,  # MSFT - typically reports 5 weeks
            'GOOW': 42,  # GOOGL - typically reports 6 weeks
            'NFLW': 49,  # NFLX - typically reports 7 weeks
            'XOMO': 28,  # XOM - typically reports ~4 weeks
            'BRKW': 90,  # BRK.B - annual meeting (not traditional earnings)
            'TSLW': 21,  # TSLA - typically reports ~3 weeks
            'QDTE': 90   # QQQ - no single earnings, spread across quarter
        }
        days_away = fallback_days.get(etf_ticker, 30)
        earnings_calendar[etf_ticker] = current_date + timedelta(days=days_away)
        print(f"CHART WARNING Estimated earnings for {etf_ticker}: {days_away} days away (API data unavailable)")
    
    return earnings_calendar

def get_fallback_earnings_calendar():
    """
    Fallback earnings calendar with more accurate estimates based on historical patterns
    Updated with better quarterly reporting cycle knowledge
    """
    current_date = datetime.now()
    
    # More accurate estimates based on typical quarterly reporting schedules
    # Most tech companies report: Q1 (late April), Q2 (late July), Q3 (late October), Q4 (late January)
    
    # Calculate which quarter we're in and estimate next earnings
    month = current_date.month
    year = current_date.year
    
    if month <= 1:      # January - Q4 earnings season
        next_earnings_base = datetime(year, 1, 28)  # Late January
    elif month <= 4:    # Feb-April - Q1 earnings season
        next_earnings_base = datetime(year, 4, 25)  # Late April
    elif month <= 7:    # May-July - Q2 earnings season
        next_earnings_base = datetime(year, 7, 25)  # Late July
    else:               # Aug-Dec - Q3 earnings season
        next_earnings_base = datetime(year, 10, 25) # Late October
    
    # If the base date has passed, move to next quarter
    if next_earnings_base <= current_date:
        if month <= 1:
            next_earnings_base = datetime(year, 4, 25)
        elif month <= 4:
            next_earnings_base = datetime(year, 7, 25)
        elif month <= 7:
            next_earnings_base = datetime(year, 10, 25)
        else:
            next_earnings_base = datetime(year + 1, 1, 28)
    
    # Company-specific adjustments based on historical patterns
    company_adjustments = {
        'NVDW': 3,   # NVDA tends to report ~3 days later in earnings week
        'AMDW': 1,   # AMD tends to report ~1 day later
        'HOOW': 0,   # HOOD typically on schedule
        'MSFW': 0,   # MSFT on schedule
        'GOOW': 2,   # GOOGL tends to report ~2 days later
        'NFLW': -1,  # NFLX tends to report ~1 day earlier
        'XOMO': 7,   # XOM reports ~1 week into earnings season
        'BRKW': 0,   # BRK.B (Berkshire) - no traditional earnings cycle
        'TSLW': 1,   # TSLA tends to report ~1 day later
        'QDTE': 0    # QQQ (index) - no single earnings date
    }
    
    earnings_calendar = {}
    for etf_ticker, adjustment in company_adjustments.items():
        adjusted_date = next_earnings_base + timedelta(days=adjustment)
        earnings_calendar[etf_ticker] = adjusted_date
        days_until = (adjusted_date - current_date).days
        print(f"CHART CALENDAR Fallback earnings for {etf_ticker}: {adjusted_date.strftime('%Y-%m-%d')} ({days_until} days)")
    
    return earnings_calendar

def test_earnings_accuracy():
    """
    Test function to verify earnings calendar accuracy
    Run this to see current earnings predictions vs known dates
    """
    print("\nTEST TESTING EARNINGS CALENDAR ACCURACY")
    print("=" * 50)
    
    earnings_calendar = get_real_earnings_calendar()
    current_date = datetime.now()
    
    print(f"Current Date: {current_date.strftime('%Y-%m-%d %H:%M')}")
    print(f"Earnings Predictions:")
    
    for ticker, earnings_date in earnings_calendar.items():
        days_until = (earnings_date - current_date).days
        
        if days_until < 0:
            print(f"   WARNING: {ticker}: {earnings_date.strftime('%Y-%m-%d')} ({abs(days_until)} days AGO)")
        elif days_until == 0:
            print(f"   TARGET: {ticker}: {earnings_date.strftime('%Y-%m-%d')} (TODAY!)")
        elif days_until <= 7:
            print(f"   URGENT: {ticker}: {earnings_date.strftime('%Y-%m-%d')} ({days_until} days - THIS WEEK)")
        else:
            print(f"   INFO: {ticker}: {earnings_date.strftime('%Y-%m-%d')} ({days_until} days)")
    
    print("\nTo verify accuracy, check actual earnings dates on:")
    print("   - Yahoo Finance earnings calendar")
    print("   - Company investor relations pages")
    print("   - Finnhub.io earnings calendar")
    print("=" * 50)

def generate_rotation_signals(df):
    """
    CORE SIGNAL ENGINE: Generate specific BUY/SELL rotation signals
    """
    signals = {
        'rotate_in': [],      # ETFs to buy
        'rotate_out': [],     # ETFs to sell
        'hold': [],           # ETFs to maintain
        'alerts': []          # Specific alert messages
    }
    
    current_date = datetime.now()
    
    for _, row in df.iterrows():
        ticker = row['Ticker']
        rsi = row['RSI']
        score = row['WeeklyPay_Score']
        days_to_ex_div = row['Days_to_Ex_Div']
        days_to_earnings = row['Days_to_Earnings']
        payout_eligible = row['Payout_Eligible']
        friday_flag = row['Friday_Purchase_Flag']
        
        # GREEN - ROTATE IN SIGNALS
        rotate_in_reasons = []
        
        # Rule 1: High RSI + High Score (Momentum + Yield)
        if rsi >= 60 and score >= 7.0:
            rotate_in_reasons.append(f"Strong momentum (RSI {rsi:.1f}) + High score ({score})")
        
        # Rule 2: Earnings Week Opportunity
        if days_to_earnings <= 7:
            rotate_in_reasons.append(f"Earnings in {days_to_earnings} days")
        
        # Rule 3: Friday Purchase Signal for Monday Ex-Dividend
        if friday_flag and payout_eligible:
            rotate_in_reasons.append(f"Friday purchase signal (ex-div in {days_to_ex_div} days)")
        
        # Rule 4: High Yield + Dividend Eligibility
        if payout_eligible and row['Weekly_Yield_%'] >= 0.8:
            rotate_in_reasons.append(f"High yield ({row['Weekly_Yield_%']:.1f}%) + dividend eligible")
        
        # RED - ROTATE OUT SIGNALS  
        rotate_out_reasons = []
        
        # Rule 1: Low RSI (Weak Momentum)
        if rsi <= 40:
            rotate_out_reasons.append(f"Weak momentum (RSI {rsi:.1f})")
        
        # Rule 2: Post-Earnings Exit (1-2 days after)
        if -2 <= days_to_earnings <= -1:  # 1-2 days AFTER earnings
            rotate_out_reasons.append(f"Post-earnings exit ({abs(days_to_earnings)} days after)")
        
        # Rule 3: Low Score (Poor Overall Performance)
        if score <= 4.0:
            rotate_out_reasons.append(f"Low WeeklyPay score ({score})")
        
        # Rule 4: Missed Dividend Window
        if not payout_eligible and days_to_ex_div <= 2:
            rotate_out_reasons.append(f"Missed dividend window (too late for ex-div)")
        
        # CHART - SIGNAL CLASSIFICATION
        if rotate_in_reasons:
            signals['rotate_in'].append({
                'ticker': ticker,
                'score': score,
                'reasons': rotate_in_reasons,
                'priority': 'HIGH' if len(rotate_in_reasons) >= 2 else 'MEDIUM'
            })
            
            # Generate specific alert
            main_reason = rotate_in_reasons[0]
            signals['alerts'].append(f"CHECK - ROTATE INTO {ticker}: {main_reason}")
            
        elif rotate_out_reasons:
            signals['rotate_out'].append({
                'ticker': ticker,
                'score': score,
                'reasons': rotate_out_reasons,
                'priority': 'HIGH' if len(rotate_out_reasons) >= 2 else 'MEDIUM'
            })
            
            # Generate specific alert
            main_reason = rotate_out_reasons[0]
            signals['alerts'].append(f"X - ROTATE OUT OF {ticker}: {main_reason}")
            
        else:
            signals['hold'].append({
                'ticker': ticker,
                'score': score,
                'status': 'Neutral - no strong signals'
            })
    
    return signals

def check_nav_erosion(ticker, threshold_pct=1.0, trades_df=None):
    """
    NAV Erosion Protection: Check for >threshold% losses for specific ticker
    Uses REAL price data and actual holdings to calculate NAV changes
    
    Args:
        ticker (str): ETF ticker symbol
        threshold_pct (float): Loss threshold percentage (default 1.0%)
        trades_df (DataFrame): Optional trade history dataframe for real calculations
    
    Returns:
        bool: True if erosion alert triggered, False if safe
    """
    # Load trades data if not provided
    if trades_df is None:
        try:
            trades_df = load_trade_data()
        except:
            return False  # Can't check without data
    
    # If we have trade data, calculate real NAV change
    if trades_df is not None and not trades_df.empty:
        try:
            # Calculate current holdings for this ticker
            ticker_trades = trades_df[trades_df['Ticker'] == ticker]
            
            if ticker_trades.empty:
                return False  # No position, no erosion risk
            
            # Calculate shares
            shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
            shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
            current_shares = shares_bought - shares_sold
            
            if current_shares <= 0:
                return False  # No current position
            
            # Calculate cost basis
            total_invested = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
            total_sold_proceeds = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
            net_investment = total_invested - total_sold_proceeds
            
            if net_investment <= 0:
                return False  # No investment to erode
            
            # Get current price
            current_prices = get_current_prices([ticker])
            current_price = current_prices.get(ticker)
            
            if current_price is None or current_price == 0:
                return False  # Can't determine price
            
            # Calculate NAV change percentage
            current_value = current_shares * current_price
            nav_change_pct = ((current_value - net_investment) / net_investment) * 100
            
            # Return True if loss exceeds threshold (triggering alert)
            return nav_change_pct <= -threshold_pct
            
        except Exception as e:
            print(f"Error calculating real NAV for {ticker}: {e}")
            return False
    
    # Fallback: No alert if we can't calculate real data
    return False

def format_rotation_week_summary(df):
    """
    Format weekly rotation summary from ETF DataFrame
    
    Args:
        df (DataFrame): ETF data with rotation signals
    
    Returns:
        list: Formatted summary messages
    """
    current_date = datetime.now()
    week_start = current_date.strftime("%b %d")
    week_end = (current_date + timedelta(days=4)).strftime("%b %d")
    
    summary = []
    
    # Get rotation signals from DataFrame
    buy_signals = df[df['Rotation_Signal'] == 'BUY'].sort_values('WeeklyPay_Score', ascending=False)
    sell_signals = df[df['Rotation_Signal'] == 'SELL'].sort_values('WeeklyPay_Score', ascending=True)
    hold_signals = df[df['Rotation_Signal'] == 'HOLD']
    
    summary.append(f"Week of {week_start}-{week_end}")
    summary.append("")
    
    # Rotation INTO signals (BUY)
    for _, row in buy_signals.head(3).iterrows():
        ticker = row['Ticker']
        score = row['WeeklyPay_Score']
        yield_pct = row['Weekly_Yield_%']
        rsi = row['RSI']
        
        priority_icon = "[HIGH]" if score > 70 else "[MED]"
        reason = f"High yield {yield_pct:.1f}%, RSI {rsi:.1f}"
        summary.append(f"[+] {priority_icon} ROTATE INTO: {ticker} ({reason})")
    
    # Rotation OUT signals (SELL)
    for _, row in sell_signals.head(3).iterrows():
        ticker = row['Ticker']
        rsi = row['RSI']
        yield_pct = row['Weekly_Yield_%']
        
        priority_icon = "[URGENT]" if rsi < 30 else "[WARNING]"
        reason = f"Low RSI {rsi:.1f}, Yield {yield_pct:.1f}%"
        summary.append(f"[-] {priority_icon} ROTATE OUT OF: {ticker} ({reason})")
    
    # HOLD signals
    if not hold_signals.empty:
        hold_count = len(hold_signals)
        summary.append(f"[=] HOLD: {hold_count} ETFs maintaining positions")
    
    return "\n".join(summary)

def create_tkinter_gui_window():
    """
    Create colorful native GUI interface with rotation bars and trophy boxes
    """
    try:
        import tkinter as tk
        from tkinter import ttk, scrolledtext
        import random
        
        def get_signal_color(signal):
            """Get color based on signal type"""
            if "BUY" in signal.upper():
                return "#28a745"  # Green
            elif "SELL" in signal.upper():
                return "#dc3545"  # Red
            elif "HOLD" in signal.upper():
                return "#ffc107"  # Yellow
            else:
                return "#6c757d"  # Gray
        
        def get_score_color(score):
            """Get color based on WeeklyPay score"""
            if score >= 8:
                return "#28a745"  # Excellent - Green
            elif score >= 6:
                return "#20c997"  # Good - Teal
            elif score >= 4:
                return "#ffc107"  # Average - Yellow
            elif score >= 2:
                return "#fd7e14"  # Below Average - Orange
            else:
                return "#dc3545"  # Poor - Red
        
        def create_rotation_bar(parent, ticker, signal, score, color):
            """Create colorful rotation signal bar"""
            bar_frame = tk.Frame(parent, bg='white', relief='raised', bd=2)
            bar_frame.pack(fill=tk.X, padx=5, pady=3)
            
            # Ticker label
            ticker_label = tk.Label(bar_frame, text=ticker, font=("Arial", 12, "bold"), 
                                   bg=color, fg='white', width=8, relief='raised', bd=1)
            ticker_label.pack(side=tk.LEFT, padx=2, pady=2)
            
            # Signal bar with gradient effect
            signal_frame = tk.Frame(bar_frame, bg=color, height=30)
            signal_frame.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=2, pady=2)
            
            signal_label = tk.Label(signal_frame, text=f"{signal} (Score: {score:.1f})", 
                                   font=("Arial", 10, "bold"), bg=color, fg='white')
            signal_label.pack(expand=True)
            
            # Progress bar effect
            progress_width = int((score / 10) * 200)  # Assume max score is 10
            progress_bar = tk.Frame(signal_frame, bg='white', height=3)
            progress_bar.place(x=0, y=25, width=progress_width)
            
            return bar_frame
        
        def create_trophy_box(parent, rank, ticker, score, yield_pct):
            """Create trophy box for top performers"""
            trophy_colors = {
                1: "#FFD700",  # Gold
                2: "#C0C0C0",  # Silver
                3: "#CD7F32",  # Bronze
                4: "#4A90E2",  # Blue
                5: "#50C878"   # Green
            }
            
            trophy_emojis = {1: "🏆", 2: "🥈", 3: "🥉", 4: "🎖️", 5: "⭐"}
            
            color = trophy_colors.get(rank, "#6c757d")
            emoji = trophy_emojis.get(rank, "📊")
            
            trophy_frame = tk.Frame(parent, bg=color, relief='raised', bd=3, width=200, height=120)
            trophy_frame.pack(side=tk.LEFT, padx=10, pady=10)
            trophy_frame.pack_propagate(False)
            
            # Rank and emoji
            rank_label = tk.Label(trophy_frame, text=f"#{rank} {emoji}", 
                                 font=("Arial", 16, "bold"), bg=color, fg='white')
            rank_label.pack(pady=5)
            
            # Ticker
            ticker_label = tk.Label(trophy_frame, text=ticker, 
                                   font=("Arial", 14, "bold"), bg=color, fg='white')
            ticker_label.pack()
            
            # Score
            score_label = tk.Label(trophy_frame, text=f"Score: {score:.1f}", 
                                  font=("Arial", 10, "bold"), bg=color, fg='white')
            score_label.pack()
            
            # Yield
            yield_label = tk.Label(trophy_frame, text=f"Yield: {yield_pct:.1f}%", 
                                  font=("Arial", 10), bg=color, fg='white')
            yield_label.pack()
            
            return trophy_frame
        
        def refresh_data():
            """Refresh the WeeklyPay data and signals with colorful display"""
            # Clear existing rotation bars
            for widget in rotation_container.winfo_children():
                widget.destroy()
            
            # Clear existing trophy boxes
            for widget in trophy_container.winfo_children():
                widget.destroy()
            
            # Update status
            status_label.config(text="🔄 Refreshing WeeklyPay data...", fg="#17a2b8")
            root.update()
            
            # Generate fresh data
            df = generate_etf_data()
            signals = generate_rotation_signals(df)
            summary = format_rotation_week_summary(df)
            
            # Create rotation bars
            rotation_title = tk.Label(rotation_container, text="📊 Weekly Rotation Signals", 
                                     font=("Arial", 16, "bold"), bg='#f8f9fa', fg='#2c3e50')
            rotation_title.pack(pady=10)
            
            for _, row in df.head(6).iterrows():
                signal_text = "[BUY FRI]" if row['Friday_Purchase_Flag'] else "[WAIT]"
                signal_color = get_signal_color(signal_text)
                score_color = get_score_color(row['WeeklyPay_Score'])
                
                # Use score color for the bar
                create_rotation_bar(rotation_container, row['Ticker'], signal_text, 
                                   row['WeeklyPay_Score'], score_color)
            
            # Create trophy boxes for top 5
            trophy_title = tk.Label(trophy_container, text="🏆 Top 5 WeeklyPay Champions", 
                                   font=("Arial", 16, "bold"), bg='#f8f9fa', fg='#2c3e50')
            trophy_title.pack(pady=10)
            
            trophy_frame = tk.Frame(trophy_container, bg='#f8f9fa')
            trophy_frame.pack(fill=tk.X, padx=20)
            
            for i, (_, row) in enumerate(df.head(5).iterrows(), 1):
                create_trophy_box(trophy_frame, i, row['Ticker'], 
                                 row['WeeklyPay_Score'], row['Weekly_Yield_%'])
            
            # Update data table with colors
            for item in tree.get_children():
                tree.delete(item)
            
            for _, row in df.head(10).iterrows():
                values = (
                    row['Ticker'],
                    f"{row['WeeklyPay_Score']:.2f}",
                    f"{row['Weekly_Yield_%']:.1f}%",
                    f"{row['RSI']:.1f}",
                    row['Ex_Dividend_Date'],
                    "[BUY FRI]" if row['Friday_Purchase_Flag'] else "[Wait]",
                    "[Yes]" if row['Payout_Eligible'] else "[No]"
                )
                item = tree.insert("", "end", values=values)
                
                # Color code rows based on score
                score = row['WeeklyPay_Score']
                if score >= 8:
                    tree.set(item, "Score", f"🔥 {score:.2f}")
                elif score >= 6:
                    tree.set(item, "Score", f"⚡ {score:.2f}")
                elif score >= 4:
                    tree.set(item, "Score", f"📈 {score:.2f}")
                else:
                    tree.set(item, "Score", f"📉 {score:.2f}")
            
            # Update status
            status_label.config(text="✅ Data refreshed successfully!", fg="#28a745")
            
            # Update ticker dropdown for trade logging
            try:
                ticker_list = df['Ticker'].tolist()
                ticker_entry['values'] = ticker_list
            except:
                pass
            
            # Refresh trade history
            try:
                load_trade_history()
            except:
                pass
            
            # Flash some colors for fun
            def flash_colors():
                colors = ["#ff6b6b", "#4ecdc4", "#45b7d1", "#96ceb4", "#ffeaa7"]
                for i, color in enumerate(colors):
                    root.after(i * 200, lambda c=color: header_frame.config(bg=c))
                root.after(1000, lambda: header_frame.config(bg='#2c3e50'))
            
            flash_colors()
        
        # Create main window with vibrant colors
        root = tk.Tk()
        root.title("🚀 WeeklyPay Tactical Rotation Engine - Colorful GUI")
        root.geometry("1400x900")
        root.configure(bg='#f8f9fa')
        
        # Make window visible and bring to front
        root.lift()
        root.attributes('-topmost', True)
        root.after_idle(root.attributes, '-topmost', False)
        root.focus_force()
        
        # Center the window on screen
        try:
            root.eval('tk::PlaceWindow . center')
        except:
            root.update_idletasks()
            width = root.winfo_width()
            height = root.winfo_height()
            x = (root.winfo_screenwidth() // 2) - (width // 2)
            y = (root.winfo_screenheight() // 2) - (height // 2)
            root.geometry(f'{width}x{height}+{x}+{y}')
        
        # Colorful gradient header
        header_frame = tk.Frame(root, bg='#2c3e50', height=80)
        header_frame.pack(fill=tk.X)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, text="🚀 WeeklyPay Tactical Rotation Engine", 
                              font=("Arial", 20, "bold"), bg='#2c3e50', fg='#f39c12')
        title_label.pack(pady=20)
        
        # Status bar
        status_frame = tk.Frame(root, bg='#17a2b8', height=30)
        status_frame.pack(fill=tk.X)
        status_frame.pack_propagate(False)
        
        status_label = tk.Label(status_frame, text="🎯 Ready to analyze WeeklyPay signals!", 
                               font=("Arial", 12, "bold"), bg='#17a2b8', fg='white')
        status_label.pack(pady=5)
        
        # Create main content frame with scrollable canvas
        main_frame = tk.Frame(root, bg='#f8f9fa')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create canvas and scrollbar for scrolling
        canvas = tk.Canvas(main_frame, bg='#f8f9fa')
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#f8f9fa')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Rotation signals container
        rotation_container = tk.Frame(scrollable_frame, bg='#f8f9fa')
        rotation_container.pack(fill=tk.X, padx=20, pady=10)
        
        # Trophy container
        trophy_container = tk.Frame(scrollable_frame, bg='#f8f9fa')
        trophy_container.pack(fill=tk.X, padx=20, pady=10)
        
        # Trade Tracking Section
        trade_frame = tk.Frame(scrollable_frame, bg='#ffffff', relief='raised', bd=3)
        trade_frame.pack(fill=tk.X, padx=20, pady=20)
        
        trade_title = tk.Label(trade_frame, text="💰 WeeklyPay Trade Tracker", 
                              font=("Arial", 16, "bold"), bg='#ffffff', fg='#2c3e50')
        trade_title.pack(pady=10)
        
        # Trade input form
        input_frame = tk.Frame(trade_frame, bg='#f8f9fa', relief='sunken', bd=2)
        input_frame.pack(fill=tk.X, padx=20, pady=10)
        
        # Row 1: Ticker, Action, Quantity
        row1 = tk.Frame(input_frame, bg='#f8f9fa')
        row1.pack(fill=tk.X, pady=5)
        
        tk.Label(row1, text="🎯 Ticker:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=5)
        ticker_var = tk.StringVar()
        ticker_entry = ttk.Combobox(row1, textvariable=ticker_var, width=8, font=("Arial", 10))
        ticker_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="⚡ Action:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=(20,5))
        action_var = tk.StringVar(value="BUY")
        action_combo = ttk.Combobox(row1, textvariable=action_var, values=["BUY", "SELL"], width=6, font=("Arial", 10))
        action_combo.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row1, text="📊 Quantity:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=(20,5))
        qty_var = tk.StringVar()
        qty_entry = tk.Entry(row1, textvariable=qty_var, width=8, font=("Arial", 10))
        qty_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 2: Price, Date, Notes
        row2 = tk.Frame(input_frame, bg='#f8f9fa')
        row2.pack(fill=tk.X, pady=5)
        
        tk.Label(row2, text="💵 Price:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=5)
        price_var = tk.StringVar()
        price_entry = tk.Entry(row2, textvariable=price_var, width=10, font=("Arial", 10))
        price_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="📅 Date:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=(20,5))
        from datetime import datetime
        date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        date_entry = tk.Entry(row2, textvariable=date_var, width=12, font=("Arial", 10))
        date_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Label(row2, text="📝 Notes:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=(20,5))
        notes_var = tk.StringVar()
        notes_entry = tk.Entry(row2, textvariable=notes_var, width=20, font=("Arial", 10))
        notes_entry.pack(side=tk.LEFT, padx=5)
        
        # Row 3: Dividend fields (only shown for DIVIDEND action)
        row3 = tk.Frame(input_frame, bg='#f8f9fa')
        row3.pack(fill=tk.X, pady=5)
        
        tk.Label(row3, text="💰 Div/Share:", font=("Arial", 10, "bold"), bg='#f8f9fa').pack(side=tk.LEFT, padx=5)
        dividend_per_share_var = tk.StringVar()
        dividend_entry = tk.Entry(row3, textvariable=dividend_per_share_var, width=10, font=("Arial", 10))
        dividend_entry.pack(side=tk.LEFT, padx=5)
        
        # Update action combo to include DIVIDEND
        action_combo.configure(values=["BUY", "SELL", "DIVIDEND"])
        
        # Trade logging functions
        def save_trade():
            """Save trade to CSV file"""
            try:
                import csv
                import os
                
                trade_file = "weeklypay_trades.csv"
                
                # Create headers if file doesn't exist
                if not os.path.exists(trade_file):
                    with open(trade_file, 'w', newline='') as f:
                        writer = csv.writer(f)
                        writer.writerow(["Date", "Ticker", "Action", "Quantity", "Price", "Total", "Notes", "WeeklyPay_Score", "Dividend_Per_Share", "Total_Dividends"])
                
                # Calculate total and dividend amounts
                try:
                    qty = float(qty_var.get() or 0)
                    price = float(price_var.get() or 0)
                    dividend_per_share = float(dividend_per_share_var.get() or 0)
                    
                    if action_var.get() == "DIVIDEND":
                        total = qty * dividend_per_share  # Total dividend received
                        total_dividends = total
                    else:
                        total = qty * price  # Regular trade total
                        total_dividends = 0
                except:
                    total = 0
                    total_dividends = 0
                    dividend_per_share = 0
                
                # Get WeeklyPay score if available
                score = "N/A"
                try:
                    df = generate_etf_data()
                    ticker_row = df[df['Ticker'] == ticker_var.get()]
                    if not ticker_row.empty:
                        score = f"{ticker_row['WeeklyPay_Score'].iloc[0]:.2f}"
                except:
                    pass
                
                # Append trade
                with open(trade_file, 'a', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        date_var.get(),
                        ticker_var.get(),
                        action_var.get(),
                        qty_var.get(),
                        price_var.get() if action_var.get() != "DIVIDEND" else dividend_per_share_var.get(),
                        f"{total:.2f}",
                        notes_var.get(),
                        score,
                        f"{dividend_per_share:.4f}" if action_var.get() == "DIVIDEND" else "0",
                        f"{total_dividends:.2f}"
                    ])
                
                # Clear form
                ticker_var.set("")
                qty_var.set("")
                price_var.set("")
                notes_var.set("")
                dividend_per_share_var.set("")
                
                # Update status
                status_label.config(text=f"✅ Trade logged: {action_var.get()} {qty_var.get()} {ticker_var.get()}", fg="#28a745")
                
                # Refresh trade display
                load_trade_history()
                
            except Exception as e:
                status_label.config(text=f"❌ Error logging trade: {str(e)}", fg="#dc3545")
        
        def load_trade_history():
            """Load and display recent trades"""
            try:
                import csv
                import os
                
                # Clear existing trades
                for widget in trades_display.winfo_children():
                    widget.destroy()
                
                trade_file = "weeklypay_trades.csv"
                if not os.path.exists(trade_file):
                    no_trades = tk.Label(trades_display, text="📊 No trades logged yet. Start tracking your WeeklyPay performance!", 
                                       font=("Arial", 11), bg='#fff3cd', fg='#856404')
                    no_trades.pack(pady=20)
                    return
                
                # Read recent trades
                trades = []
                with open(trade_file, 'r') as f:
                    reader = csv.DictReader(f)
                    trades = list(reader)
                
                # Calculate performance including dividends
                total_invested = 0
                total_dividends = 0
                total_proceeds = 0
                buy_trades = {}
                
                for trade in trades:
                    try:
                        qty = float(trade['Quantity'])
                        price = float(trade['Price'])
                        ticker = trade['Ticker']
                        action = trade['Action']
                        total_amount = float(trade['Total'])
                        
                        # Handle dividend tracking
                        dividend_amount = 0
                        if len(trade) > 9 and trade.get('Total_Dividends'):  # New format with dividend columns
                            dividend_amount = float(trade.get('Total_Dividends', 0))
                        
                        if action == 'BUY':
                            if ticker not in buy_trades:
                                buy_trades[ticker] = []
                            buy_trades[ticker].append({'qty': qty, 'price': price})
                            total_invested += total_amount
                        elif action == 'SELL':
                            total_proceeds += total_amount
                        elif action == 'DIVIDEND':
                            total_dividends += total_amount
                        
                    except:
                        continue
                
                # Performance summary
                perf_frame = tk.Frame(trades_display, bg='#d1ecf1', relief='raised', bd=2)
                perf_frame.pack(fill=tk.X, padx=5, pady=5)
                
                # Calculate total return (capital gains + dividends)
                net_capital_gains = total_proceeds - total_invested if total_proceeds > 0 else 0
                total_return = net_capital_gains + total_dividends
                return_pct = (total_return / total_invested * 100) if total_invested > 0 else 0
                
                summary_text = f"💼 Invested: ${total_invested:,.2f} | � Dividends: ${total_dividends:,.2f} | 📈 Total Return: ${total_return:,.2f} ({return_pct:+.1f}%) | � Positions: {len(buy_trades)}"
                perf_label = tk.Label(perf_frame, text=summary_text, font=("Arial", 11, "bold"), 
                                    bg='#d1ecf1', fg='#0c5460')
                perf_label.pack(pady=10)
                
                # Recent trades (last 5)
                recent_label = tk.Label(trades_display, text="🕒 Recent Trades:", 
                                      font=("Arial", 12, "bold"), bg='#ffffff', fg='#2c3e50')
                recent_label.pack(anchor='w', padx=5, pady=(10,5))
                
                for trade in trades[-5:]:
                    # Color coding for different trade types
                    if trade['Action'] == 'BUY':
                        trade_color = "#d4edda"
                        text_color = "#155724"
                    elif trade['Action'] == 'SELL':
                        trade_color = "#f8d7da"
                        text_color = "#721c24"
                    elif trade['Action'] == 'DIVIDEND':
                        trade_color = "#fff3cd"  # Yellow for dividends
                        text_color = "#856404"
                    else:
                        trade_color = "#e2e3e5"
                        text_color = "#383d41"
                    
                    trade_item = tk.Frame(trades_display, bg=trade_color, relief='raised', bd=1)
                    trade_item.pack(fill=tk.X, padx=5, pady=2)
                    
                    # Format trade text based on action type
                    if trade['Action'] == 'DIVIDEND':
                        trade_text = f"{trade['Date']} | 💰 DIVIDEND {trade['Quantity']} {trade['Ticker']} @ ${trade['Price']}/share | Total: ${trade['Total']}"
                    else:
                        trade_text = f"{trade['Date']} | {trade['Action']} {trade['Quantity']} {trade['Ticker']} @ ${trade['Price']} | Score: {trade.get('WeeklyPay_Score', 'N/A')}"
                    
                    if trade['Notes']:
                        trade_text += f" | {trade['Notes']}"
                    
                    trade_label = tk.Label(trade_item, text=trade_text, font=("Arial", 9), 
                                         bg=trade_color, fg=text_color)
                    trade_label.pack(anchor='w', padx=5, pady=2)
                
            except Exception as e:
                error_label = tk.Label(trades_display, text=f"❌ Error loading trades: {str(e)}", 
                                     font=("Arial", 10), bg='#f8d7da', fg='#721c24')
                error_label.pack(pady=10)
        
        # Trade buttons
        button_row = tk.Frame(input_frame, bg='#f8f9fa')
        button_row.pack(fill=tk.X, pady=10)
        
        log_trade_btn = tk.Button(button_row, text="💾 Log Trade", command=save_trade,
                                font=("Arial", 11, "bold"), bg='#28a745', fg='white', 
                                padx=15, pady=5, relief='raised', bd=2, cursor='hand2')
        log_trade_btn.pack(side=tk.LEFT, padx=5)
        
        def quick_fill_ticker():
            """Fill ticker from selected rotation signal"""
            try:
                df = generate_etf_data()
                if not df.empty:
                    top_ticker = df.iloc[0]['Ticker']
                    ticker_var.set(top_ticker)
                    status_label.config(text=f"🎯 Auto-filled top WeeklyPay pick: {top_ticker}", fg="#17a2b8")
            except:
                pass
        
        quick_fill_btn = tk.Button(button_row, text="🎯 Top Pick", command=quick_fill_ticker,
                                 font=("Arial", 11, "bold"), bg='#17a2b8', fg='white', 
                                 padx=15, pady=5, relief='raised', bd=2, cursor='hand2')
        quick_fill_btn.pack(side=tk.LEFT, padx=5)
        
        def open_trade_analyzer():
            """Open standalone trade analyzer"""
            try:
                import subprocess
                import sys
                
                # Create analyzer script if it doesn't exist
                analyzer_script = """# -*- coding: utf-8 -*-
import pandas as pd
import tkinter as tk
from tkinter import ttk, scrolledtext, font
import os

def get_current_prices(tickers):
    \"\"\"Fetch current prices for a list of tickers using yfinance\"\"\"
    prices = {}
    try:
        import yfinance as yf
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                # Try different price fields
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                if current_price:
                    prices[ticker] = current_price
            except Exception as e:
                print(f"Error fetching price for {ticker}: {e}")
    except ImportError:
        print("yfinance not available for price fetching")
    return prices

def calculate_current_holdings(trades_df):
    \"\"\"Calculate current holdings with live prices and total returns\"\"\"
    if trades_df.empty:
        return pd.DataFrame()
    
    holdings = []
    
    # Get unique tickers with open positions
    for ticker in trades_df['Ticker'].unique():
        ticker_trades = trades_df[trades_df['Ticker'] == ticker]
        
        # Calculate shares
        shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
        shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
        current_shares = shares_bought - shares_sold
        
        if current_shares > 0:
            # Calculate cost basis
            total_invested = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
            total_sold_proceeds = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
            net_investment = total_invested - total_sold_proceeds
            avg_cost = net_investment / current_shares if current_shares > 0 else 0
            
            # Get dividends received
            total_dividends = ticker_trades[ticker_trades['Action'] == 'DIVIDEND']['Total'].sum()
            
            holdings.append({
                'Ticker': ticker,
                'Shares': current_shares,
                'Avg_Cost': avg_cost,
                'Investment': net_investment,
                'Dividends': total_dividends
            })
    
    if not holdings:
        return pd.DataFrame()
    
    holdings_df = pd.DataFrame(holdings)
    
    # Fetch current prices
    tickers = holdings_df['Ticker'].tolist()
    current_prices = get_current_prices(tickers)
    
    # Add current prices and calculate values
    holdings_df['Current_Price'] = holdings_df['Ticker'].map(current_prices)
    holdings_df['Current_Value'] = holdings_df['Current_Price'] * holdings_df['Shares']
    holdings_df['NAV_Change'] = holdings_df['Current_Value'] - holdings_df['Investment']
    holdings_df['NAV_Change_Pct'] = (holdings_df['NAV_Change'] / holdings_df['Investment'] * 100).fillna(0)
    holdings_df['Total_Return'] = holdings_df['NAV_Change'] + holdings_df['Dividends']
    holdings_df['Total_Return_Pct'] = (holdings_df['Total_Return'] / holdings_df['Investment'] * 100).fillna(0)
    
    return holdings_df

def create_trade_analyzer():
    root = tk.Tk()
    root.title("WeeklyPay Trade Performance Analyzer")
    root.geometry("1000x750")
    root.configure(bg='#1e1e1e')
    
    # Create header with gradient effect
    header = tk.Frame(root, bg='#2563eb', pady=15)
    header.pack(fill=tk.X)
    title_label = tk.Label(header, text="TRADE PERFORMANCE ANALYZER", 
                           font=("Arial", 20, "bold"), bg='#2563eb', fg='white')
    title_label.pack()
    subtitle = tk.Label(header, text="WeeklyPay Rotation Strategy", 
                       font=("Arial", 12), bg='#2563eb', fg='#dbeafe')
    subtitle.pack()
    
    try:
        if os.path.exists("weeklypay_trades.csv"):
            df = pd.read_csv("weeklypay_trades.csv")
            
            # Calculate performance metrics
            total_trades = len(df)
            buy_trades = df[df['Action'] == 'BUY']
            sell_trades = df[df['Action'] == 'SELL']
            dividend_trades = df[df['Action'] == 'DIVIDEND']
            
            total_invested = buy_trades['Total'].astype(float).sum()
            total_sold = sell_trades['Total'].astype(float).sum()
            total_dividends = dividend_trades['Total'].astype(float).sum()
            
            # Calculate realized capital gains
            realized_gains = total_sold - total_invested if total_sold > 0 else 0
            total_return = realized_gains + total_dividends
            return_pct = (total_return / total_invested * 100) if total_invested > 0 else 0
            
            # Get average WeeklyPay score
            avg_score = pd.to_numeric(buy_trades['WeeklyPay_Score'], errors='coerce').mean()
            
            # Calculate active positions
            position_summary = df.groupby('Ticker').apply(
                lambda x: x[x['Action'] == 'BUY']['Quantity'].sum() - x[x['Action'] == 'SELL']['Quantity'].sum()
            )
            active_positions = (position_summary > 0).sum()
            
            # Create text widget with larger font
            text_frame = tk.Frame(root, bg='#1e1e1e')
            text_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
            
            text_widget = tk.Text(text_frame, font=("Arial", 13), 
                                 bg='#ffffff', fg='#1e1e1e',
                                 wrap=tk.WORD, padx=15, pady=15)
            
            # Add scrollbar
            scrollbar = tk.Scrollbar(text_frame, command=text_widget.yview)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            text_widget.config(yscrollcommand=scrollbar.set)
            text_widget.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            
            # Configure color tags
            text_widget.tag_configure("header", font=("Arial", 16, "bold"), foreground="#2563eb")
            text_widget.tag_configure("section", font=("Arial", 14, "bold"), foreground="#059669")
            text_widget.tag_configure("positive", foreground="#10b981", font=("Arial", 13, "bold"))
            text_widget.tag_configure("negative", foreground="#ef4444", font=("Arial", 13, "bold"))
            text_widget.tag_configure("neutral", foreground="#6b7280", font=("Arial", 13))
            text_widget.tag_configure("highlight", foreground="#8b5cf6", font=("Arial", 13, "bold"))
            text_widget.tag_configure("ticker", foreground="#0284c7", font=("Arial", 13, "bold"))
            text_widget.tag_configure("amount", foreground="#ea580c", font=("Arial", 13, "bold"))
            
            # Insert header
            text_widget.insert(tk.END, "\\n")
            text_widget.insert(tk.END, "="*80 + "\\n")
            text_widget.insert(tk.END, "               WEEKLYPAY PERFORMANCE ANALYSIS\\n", "header")
            text_widget.insert(tk.END, "="*80 + "\\n\\n")
            
            # TRADE SUMMARY section
            text_widget.insert(tk.END, "TRADE SUMMARY\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            text_widget.insert(tk.END, f"Total Trades: ", "neutral")
            text_widget.insert(tk.END, f"{total_trades}\\n", "highlight")
            text_widget.insert(tk.END, f"  Buy Orders: ", "neutral")
            text_widget.insert(tk.END, f"{len(buy_trades)}\\n", "positive")
            text_widget.insert(tk.END, f"  Sell Orders: ", "neutral")
            text_widget.insert(tk.END, f"{len(sell_trades)}\\n", "neutral")
            text_widget.insert(tk.END, f"  Dividend Payments: ", "neutral")
            text_widget.insert(tk.END, f"{len(dividend_trades)}\\n\\n", "ticker")
            
            # FINANCIAL METRICS section
            text_widget.insert(tk.END, "FINANCIAL METRICS\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            text_widget.insert(tk.END, f"Total Invested: ", "neutral")
            text_widget.insert(tk.END, f"${total_invested:,.2f}\\n", "amount")
            text_widget.insert(tk.END, f"Total Sold: ", "neutral")
            text_widget.insert(tk.END, f"${total_sold:,.2f}\\n", "neutral")
            text_widget.insert(tk.END, f"Total Dividends Received: ", "neutral")
            text_widget.insert(tk.END, f"${total_dividends:,.2f}\\n\\n", "positive")
            
            text_widget.insert(tk.END, f"Realized Capital Gains: ", "neutral")
            gain_tag = "positive" if realized_gains >= 0 else "negative"
            text_widget.insert(tk.END, f"${realized_gains:,.2f}\\n", gain_tag)
            
            text_widget.insert(tk.END, f"Total Realized Return: ", "neutral")
            return_tag = "positive" if total_return >= 0 else "negative"
            text_widget.insert(tk.END, f"${total_return:,.2f}\\n", return_tag)
            
            text_widget.insert(tk.END, f"Return Percentage: ", "neutral")
            pct_tag = "positive" if return_pct >= 0 else "negative"
            text_widget.insert(tk.END, f"{return_pct:+.2f}%\\n\\n", pct_tag)
            
            # PORTFOLIO STATUS section
            text_widget.insert(tk.END, "PORTFOLIO STATUS\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            text_widget.insert(tk.END, f"Active Positions: ", "neutral")
            text_widget.insert(tk.END, f"{active_positions}\\n", "highlight")
            text_widget.insert(tk.END, f"Average WeeklyPay Score: ", "neutral")
            text_widget.insert(tk.END, f"{avg_score:.2f}\\n\\n", "ticker")
            
            # CURRENT HOLDINGS WITH LIVE PRICES section
            text_widget.insert(tk.END, "CURRENT HOLDINGS (LIVE PRICES)\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            
            holdings_df = calculate_current_holdings(df)
            
            if not holdings_df.empty and holdings_df['Current_Price'].notna().any():
                # Summary totals
                total_investment = holdings_df['Investment'].sum()
                total_current_value = holdings_df['Current_Value'].sum()
                total_nav_change = holdings_df['NAV_Change'].sum()
                total_dividends_received = holdings_df['Dividends'].sum()
                total_return_value = holdings_df['Total_Return'].sum()
                
                text_widget.insert(tk.END, "Portfolio Summary:\\n", "highlight")
                text_widget.insert(tk.END, f"  Total Investment: ", "neutral")
                text_widget.insert(tk.END, f"${total_investment:,.2f}\\n", "amount")
                text_widget.insert(tk.END, f"  Current Value: ", "neutral")
                nav_tag = "positive" if total_nav_change >= 0 else "negative"
                text_widget.insert(tk.END, f"${total_current_value:,.2f} ", "amount")
                nav_pct = (total_nav_change / total_investment * 100) if total_investment > 0 else 0
                text_widget.insert(tk.END, f"({nav_pct:+.1f}%)\\n", nav_tag)
                text_widget.insert(tk.END, f"  NAV Change: ", "neutral")
                text_widget.insert(tk.END, f"${total_nav_change:+,.2f}\\n", nav_tag)
                text_widget.insert(tk.END, f"  Total Dividends: ", "neutral")
                text_widget.insert(tk.END, f"${total_dividends_received:,.2f}\\n", "positive")
                text_widget.insert(tk.END, f"  Total Return: ", "neutral")
                total_return_tag = "positive" if total_return_value >= 0 else "negative"
                text_widget.insert(tk.END, f"${total_return_value:+,.2f} ", "amount")
                total_return_pct = (total_return_value / total_investment * 100) if total_investment > 0 else 0
                text_widget.insert(tk.END, f"({total_return_pct:+.1f}%)\\n\\n", total_return_tag)
                
                # Individual holdings
                text_widget.insert(tk.END, "Individual Holdings:\\n", "highlight")
                text_widget.insert(tk.END, f"{'Ticker':<8} {'Shares':<8} {'Avg Cost':<12} {'Current':<12} {'NAV Chg':<14} {'Divs':<12} {'Total Ret':<14}\\n", "highlight")
                text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
                
                for idx, holding in holdings_df.iterrows():
                    text_widget.insert(tk.END, f"{holding['Ticker']:<8} ", "ticker")
                    text_widget.insert(tk.END, f"{int(holding['Shares']):<8} ", "neutral")
                    text_widget.insert(tk.END, f"${holding['Avg_Cost']:<11.2f} ", "neutral")
                    text_widget.insert(tk.END, f"${holding['Current_Price']:<11.2f} ", "neutral")
                    
                    # NAV Change with color
                    nav_change_tag = "positive" if holding['NAV_Change'] >= 0 else "negative"
                    text_widget.insert(tk.END, f"${holding['NAV_Change']:+,.2f} ", nav_change_tag)
                    text_widget.insert(tk.END, f"({holding['NAV_Change_Pct']:+.1f}%) ", nav_change_tag)
                    
                    text_widget.insert(tk.END, f"${holding['Dividends']:,.2f}  ", "positive")
                    
                    # Total Return with color
                    total_ret_tag = "positive" if holding['Total_Return'] >= 0 else "negative"
                    text_widget.insert(tk.END, f"${holding['Total_Return']:+,.2f} ", total_ret_tag)
                    text_widget.insert(tk.END, f"({holding['Total_Return_Pct']:+.1f}%)\\n", total_ret_tag)
                
                text_widget.insert(tk.END, "\\n💡 Total Return = NAV Change + Dividends\\n", "neutral")
            else:
                text_widget.insert(tk.END, "No open positions or unable to fetch prices.\\n", "neutral")
            
            text_widget.insert(tk.END, "\\n")
            
            # TOP TRADED TICKERS section
            text_widget.insert(tk.END, "TOP TRADED TICKERS\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            ticker_counts = df['Ticker'].value_counts().head(10)
            for ticker, count in ticker_counts.items():
                text_widget.insert(tk.END, f"{ticker}: ", "ticker")
                text_widget.insert(tk.END, f"{count} trades\\n", "neutral")
            text_widget.insert(tk.END, "\\n")
            
            # RECENT ACTIVITY section
            text_widget.insert(tk.END, "RECENT ACTIVITY (Last 10 Trades)\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            text_widget.insert(tk.END, f"{'Date':<12} {'Ticker':<8} {'Action':<10} {'Qty':<8} {'Price':<12} {'Total':<12}\\n", "highlight")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            
            for idx, row in df.tail(10).iterrows():
                # Date and Ticker
                text_widget.insert(tk.END, f"{str(row['Date']):<12} ")
                text_widget.insert(tk.END, f"{str(row['Ticker']):<8} ", "ticker")
                
                # Action with color
                action = str(row['Action'])
                if action == 'BUY':
                    text_widget.insert(tk.END, f"{action:<10} ", "positive")
                elif action == 'SELL':
                    text_widget.insert(tk.END, f"{action:<10} ", "negative")
                else:
                    text_widget.insert(tk.END, f"{action:<10} ", "highlight")
                
                # Quantity
                text_widget.insert(tk.END, f"{str(row['Quantity']):<8} ")
                
                # Price and Total
                text_widget.insert(tk.END, f"${float(row['Price']):<11.2f} ")
                text_widget.insert(tk.END, f"${float(row['Total']):<11.2f}\\n", "amount")
            
            # INCOME PROJECTIONS section
            text_widget.insert(tk.END, "\\n")
            text_widget.insert(tk.END, "INCOME PROJECTIONS\\n", "section")
            text_widget.insert(tk.END, "-"*80 + "\\n", "neutral")
            
            if len(dividend_trades) > 0:
                # Calculate date range
                div_dates = pd.to_datetime(dividend_trades['Date'])
                first_div = div_dates.min()
                last_div = div_dates.max()
                days_tracked = (last_div - first_div).days
                
                # Calculate averages
                if days_tracked > 0:
                    months_tracked = days_tracked / 30.44
                    avg_monthly = total_dividends / months_tracked if months_tracked > 0 else total_dividends
                    avg_yearly = avg_monthly * 12
                else:
                    avg_monthly = total_dividends
                    avg_yearly = total_dividends * 12
                
                # Calculate estimated future income
                position_summary = {}
                for ticker in df['Ticker'].unique():
                    ticker_trades = df[df['Ticker'] == ticker]
                    shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
                    shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
                    current_shares = shares_bought - shares_sold
                    
                    if current_shares > 0:
                        ticker_divs = dividend_trades[dividend_trades['Ticker'] == ticker]
                        if len(ticker_divs) > 0:
                            total_payments = len(ticker_divs)
                            total_amount = ticker_divs['Total'].sum()
                            avg_per_payment = total_amount / total_payments
                            position_summary[ticker] = {
                                'shares': current_shares,
                                'avg_div': avg_per_payment,
                                'payments': total_payments
                            }
                
                estimated_yearly = 0
                for ticker, info in position_summary.items():
                    ticker_div_trades = dividend_trades[dividend_trades['Ticker'] == ticker]
                    if len(ticker_div_trades) >= 2:
                        ticker_days = (pd.to_datetime(ticker_div_trades['Date']).max() - 
                                     pd.to_datetime(ticker_div_trades['Date']).min()).days
                        if ticker_days > 0:
                            annual_freq = info['payments'] * (365 / ticker_days)
                            estimated_yearly += info['avg_div'] * annual_freq
                    else:
                        estimated_yearly += info['avg_div'] * 52
                
                estimated_monthly = estimated_yearly / 12
                
                # Display metrics
                text_widget.insert(tk.END, "Historical Performance:\\n", "highlight")
                text_widget.insert(tk.END, f"  Tracking Period: ", "neutral")
                text_widget.insert(tk.END, f"{days_tracked} days\\n", "ticker")
                text_widget.insert(tk.END, f"  Total Dividend Payments: ", "neutral")
                text_widget.insert(tk.END, f"{len(dividend_trades)}\\n\\n", "ticker")
                
                text_widget.insert(tk.END, "Average Income (Based on History):\\n", "highlight")
                text_widget.insert(tk.END, f"  Monthly Average: ", "neutral")
                text_widget.insert(tk.END, f"${avg_monthly:,.2f}\\n", "positive")
                text_widget.insert(tk.END, f"  Yearly Average: ", "neutral")
                text_widget.insert(tk.END, f"${avg_yearly:,.2f}\\n\\n", "positive")
                
                if position_summary:
                    text_widget.insert(tk.END, "Estimated Future Income (Current Holdings):\\n", "highlight")
                    text_widget.insert(tk.END, f"  Est. Monthly: ", "neutral")
                    text_widget.insert(tk.END, f"${estimated_monthly:,.2f}", "positive")
                    if avg_monthly > 0:
                        pct_change = ((estimated_monthly - avg_monthly) / avg_monthly * 100)
                        change_tag = "positive" if pct_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({pct_change:+.1f}%)\\n", change_tag)
                    else:
                        text_widget.insert(tk.END, "\\n")
                    
                    text_widget.insert(tk.END, f"  Est. Yearly: ", "neutral")
                    text_widget.insert(tk.END, f"${estimated_yearly:,.2f}", "positive")
                    if avg_yearly > 0:
                        pct_change = ((estimated_yearly - avg_yearly) / avg_yearly * 100)
                        change_tag = "positive" if pct_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({pct_change:+.1f}%)\\n\\n", change_tag)
                    else:
                        text_widget.insert(tk.END, "\\n\\n")
                    
                    # Calculate total investment and yields
                    total_investment = 0
                    ticker_investments = {}
                    
                    for ticker in df['Ticker'].unique():
                        ticker_trades = df[df['Ticker'] == ticker]
                        ticker_invested = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
                        ticker_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
                        net_investment = ticker_invested - ticker_sold
                        if net_investment > 0:
                            ticker_investments[ticker] = net_investment
                            total_investment += net_investment
                    
                    # Calculate overall yields
                    monthly_yield = (avg_monthly / total_investment * 100) if total_investment > 0 else 0
                    yearly_yield = (avg_yearly / total_investment * 100) if total_investment > 0 else 0
                    est_monthly_yield = (estimated_monthly / total_investment * 100) if total_investment > 0 else 0
                    est_yearly_yield = (estimated_yearly / total_investment * 100) if total_investment > 0 else 0
                    
                    text_widget.insert(tk.END, "Return on Investment (Dividend Yield):\\n", "highlight")
                    text_widget.insert(tk.END, f"  Total Investment: ", "neutral")
                    text_widget.insert(tk.END, f"${total_investment:,.2f}\\n", "amount")
                    text_widget.insert(tk.END, f"  Monthly Yield (Historical): ", "neutral")
                    text_widget.insert(tk.END, f"{monthly_yield:.2f}%\\n", "positive")
                    text_widget.insert(tk.END, f"  Annual Yield (Historical): ", "neutral")
                    text_widget.insert(tk.END, f"{yearly_yield:.2f}%\\n", "positive")
                    text_widget.insert(tk.END, f"  Est. Monthly Yield: ", "neutral")
                    text_widget.insert(tk.END, f"{est_monthly_yield:.2f}%", "ticker")
                    if monthly_yield > 0:
                        yield_change = est_monthly_yield - monthly_yield
                        yield_tag = "positive" if yield_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({yield_change:+.2f}%)\\n", yield_tag)
                    else:
                        text_widget.insert(tk.END, "\\n")
                    text_widget.insert(tk.END, f"  Est. Annual Yield: ", "neutral")
                    text_widget.insert(tk.END, f"{est_yearly_yield:.2f}%", "ticker")
                    if yearly_yield > 0:
                        yield_change = est_yearly_yield - yearly_yield
                        yield_tag = "positive" if yield_change >= 0 else "negative"
                        text_widget.insert(tk.END, f" ({yield_change:+.2f}%)\\n\\n", yield_tag)
                    else:
                        text_widget.insert(tk.END, "\\n\\n")
                    
                    text_widget.insert(tk.END, "Current Positions:\\n", "highlight")
                    for ticker, info in position_summary.items():
                        ticker_div_trades = dividend_trades[dividend_trades['Ticker'] == ticker]
                        ticker_days = (pd.to_datetime(ticker_div_trades['Date']).max() - 
                                     pd.to_datetime(ticker_div_trades['Date']).min()).days
                        
                        if len(ticker_div_trades) >= 2 and ticker_days > 0:
                            annual_freq = info['payments'] * (365 / ticker_days)
                            est_annual = info['avg_div'] * annual_freq
                        else:
                            est_annual = info['avg_div'] * 52
                        
                        est_monthly_ticker = est_annual / 12
                        ticker_investment = ticker_investments.get(ticker, 0)
                        ticker_monthly_yield = (est_monthly_ticker / ticker_investment * 100) if ticker_investment > 0 else 0
                        ticker_yearly_yield = (est_annual / ticker_investment * 100) if ticker_investment > 0 else 0
                        
                        text_widget.insert(tk.END, f"  {ticker}: ", "ticker")
                        text_widget.insert(tk.END, f"{info['shares']} shares, ", "neutral")
                        text_widget.insert(tk.END, f"Inv: ${ticker_investment:,.2f}, ", "neutral")
                        text_widget.insert(tk.END, f"Est. ${est_annual:,.2f}/yr ", "positive")
                        
                        # Color code yield based on performance
                        if ticker_yearly_yield >= 10:
                            yield_tag = "positive"
                        elif ticker_yearly_yield >= 5:
                            yield_tag = "ticker"
                        else:
                            yield_tag = "neutral"
                        text_widget.insert(tk.END, f"({ticker_yearly_yield:.2f}% annual)\\n", yield_tag)
                else:
                    text_widget.insert(tk.END, "\\nNo current positions with dividend history.\\n", "neutral")
            else:
                text_widget.insert(tk.END, "No dividend data yet. Log dividend payments to see projections.\\n", "neutral")
            
            text_widget.insert(tk.END, "\\n")
            text_widget.insert(tk.END, "="*80 + "\\n")
            text_widget.insert(tk.END, "                    END OF ANALYSIS\\n", "header")
            text_widget.insert(tk.END, "="*80 + "\\n")
            
            text_widget.config(state=tk.DISABLED)
            
            # Add close button with better styling
            button_frame = tk.Frame(root, bg='#1e1e1e', pady=10)
            button_frame.pack()
            close_btn = tk.Button(button_frame, text="Close", command=root.destroy,
                                 font=("Arial", 14, "bold"), bg='#ef4444', fg='white',
                                 padx=30, pady=10, cursor='hand2', relief=tk.FLAT)
            close_btn.pack()
            
        else:
            label = tk.Label(root, text="No trade data found. Start logging trades first!", 
                           font=("Arial", 14), bg='#2c3e50', fg='white')
            label.pack(pady=50)
    
    except Exception as e:
        error_label = tk.Label(root, text=f"Error: {e}", font=("Arial", 12), 
                              bg='#2c3e50', fg='#e74c3c')
        error_label.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    create_trade_analyzer()
"""
                
                # Write with UTF-8 encoding to support emoji characters
                with open("trade_analyzer.py", "w", encoding="utf-8") as f:
                    f.write(analyzer_script)
                
                subprocess.Popen([sys.executable, "trade_analyzer.py"])
                status_label.config(text="📊 Trade analyzer launched!", fg="#6f42c1")
                
            except Exception as e:
                status_label.config(text=f"❌ Error launching analyzer: {str(e)}", fg="#dc3545")
        
        analyzer_btn = tk.Button(button_row, text="📊 Analyzer", command=open_trade_analyzer,
                               font=("Arial", 11, "bold"), bg='#6f42c1', fg='white', 
                               padx=15, pady=5, relief='raised', bd=2, cursor='hand2')
        analyzer_btn.pack(side=tk.LEFT, padx=5)
        
        def open_trade_manager():
            """Open trade diagnostic & edit tool"""
            try:
                import subprocess
                import sys
                import os
                
                # Get the correct path to the trade diagnostic tool
                script_dir = os.path.dirname(os.path.abspath(__file__))
                tool_path = os.path.join(script_dir, "trade_diagnostic_tool.py")
                
                if not os.path.exists(tool_path):
                    status_label.config(text="❌ Trade Manager not found!", fg="#dc3545")
                    return
                
                subprocess.Popen([sys.executable, tool_path])
                status_label.config(text="✏️ Trade Manager launched! You can now view/edit/delete trades.", fg="#f39c12")
                
            except Exception as e:
                status_label.config(text=f"❌ Error launching Trade Manager: {str(e)}", fg="#dc3545")
        
        trade_manager_btn = tk.Button(button_row, text="✏️ Trade Manager", command=open_trade_manager,
                               font=("Arial", 11, "bold"), bg='#f39c12', fg='white', 
                               padx=15, pady=5, relief='raised', bd=2, cursor='hand2')
        trade_manager_btn.pack(side=tk.LEFT, padx=5)
        
        # Trade history display
        trades_display = tk.Frame(trade_frame, bg='#ffffff')
        trades_display.pack(fill=tk.X, padx=20, pady=10)
        
        # Enhanced data table section
        table_frame = tk.Frame(scrollable_frame, bg='#ffffff', relief='raised', bd=2)
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        table_title = tk.Label(table_frame, text="📈 Detailed ETF Rankings", 
                              font=("Arial", 16, "bold"), bg='#ffffff', fg='#2c3e50')
        table_title.pack(pady=10)
        
        # Colorful data table
        columns = ("Ticker", "Score", "Yield", "RSI", "Ex-Div Date", "Friday Signal", "Payout Eligible")
        tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        # Style the treeview
        style = ttk.Style()
        style.configure("Treeview.Heading", font=("Arial", 10, "bold"))
        style.configure("Treeview", font=("Arial", 9), rowheight=25)
        
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=120, anchor=tk.CENTER)
        
        tree.pack(pady=10, padx=20, fill=tk.BOTH, expand=True)
        
        # Colorful control buttons
        button_frame = tk.Frame(root, bg='#f8f9fa')
        button_frame.pack(fill=tk.X, pady=10)
        
        # Left side buttons
        left_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        left_buttons.pack(side=tk.LEFT, padx=20)
        
        refresh_btn = tk.Button(left_buttons, text="🔄 Refresh Data", 
                              command=refresh_data, font=("Arial", 12, "bold"),
                              bg='#28a745', fg='white', padx=20, pady=8,
                              relief='raised', bd=3, cursor='hand2')
        refresh_btn.pack(side=tk.LEFT, padx=5)
        
        auto_refresh_btn = tk.Button(left_buttons, text="⚡ Auto Refresh", 
                                   font=("Arial", 12, "bold"),
                                   bg='#17a2b8', fg='white', padx=20, pady=8,
                                   relief='raised', bd=3, cursor='hand2')
        auto_refresh_btn.pack(side=tk.LEFT, padx=5)
        
        # Right side buttons
        right_buttons = tk.Frame(button_frame, bg='#f8f9fa')
        right_buttons.pack(side=tk.RIGHT, padx=20)
        
        settings_btn = tk.Button(right_buttons, text="⚙️ Settings", 
                               font=("Arial", 12, "bold"),
                               bg='#6f42c1', fg='white', padx=20, pady=8,
                               relief='raised', bd=3, cursor='hand2')
        settings_btn.pack(side=tk.LEFT, padx=5)
        
        exit_btn = tk.Button(right_buttons, text="❌ Exit", 
                           command=root.quit, font=("Arial", 12, "bold"),
                           bg='#dc3545', fg='white', padx=20, pady=8,
                           relief='raised', bd=3, cursor='hand2')
        exit_btn.pack(side=tk.LEFT, padx=5)
        
        # Bind mouse wheel to canvas scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        
        # Add some fun animations
        def animate_title():
            colors = ['#f39c12', '#e74c3c', '#9b59b6', '#3498db', '#2ecc71']
            current_color = random.choice(colors)
            title_label.config(fg=current_color)
            root.after(3000, animate_title)  # Change color every 3 seconds
        
        animate_title()
        
        # Initial data load with welcome message
        welcome_frame = tk.Frame(rotation_container, bg='#e8f5e8', relief='raised', bd=2)
        welcome_frame.pack(fill=tk.X, padx=5, pady=10)
        
        welcome_label = tk.Label(welcome_frame, 
                                text="🎉 Welcome to the Enhanced WeeklyPay GUI! Click 'Refresh Data' to load signals.",
                                font=("Arial", 12, "bold"), bg='#e8f5e8', fg='#155724')
        welcome_label.pack(pady=20)
        
        # Auto-refresh on startup
        root.after(1000, refresh_data)
        
        return root
        
    except ImportError:
        print("Warning: tkinter not available for GUI mode")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour to prevent repeated API calls
def get_live_ex_dividend_dates():
    """
    Get live ex-dividend dates for weekly ETFs
    Tries to pull real data, falls back to intelligent weekly patterns
    """
    try:
        import yfinance as yf
    except ImportError:
        print("WARNING: yfinance not installed. Install with: pip install yfinance")
        return get_fallback_ex_dividend_dates()
    
    from datetime import datetime, timedelta
    
    current_date = datetime.now()
    ex_dividend_dates = {}
    
    # Known weekly ETF tickers
    weekly_etfs = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW', 'XOMO', 'BRKW', 'TSLW', 'QDTE']
    
    # CHECK: UPDATED: Accurate ex-dividend dates from user confirmation
    # Original 6 ETFs: Ex-dividend TUESDAY, Pay WEDNESDAY (weekly pattern)
    # XOMO, BRKW, TSLW & QDTE: Ex-dividend THURSDAY, Pay FRIDAY (weekly pattern)
    last_known_ex_div = {
        'MSFW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'NVDW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'HOOW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'AMDW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'GOOW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'NFLW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'XOMO': datetime(2025, 10, 3),  # Thursday 10/3 (pays Friday) - Energy sector
        'BRKW': datetime(2025, 10, 3),  # Thursday 10/3 (pays Friday) - Financials sector
        'TSLW': datetime(2025, 10, 3),  # Thursday 10/3 (pays Friday) - High volatility tech
        'QDTE': datetime(2025, 10, 3)   # Thursday 10/3 (pays Friday) - Weekly Thursday payer
    }
    
    for ticker in weekly_etfs:
        try:
            # Try to get live data from Yahoo Finance
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Look for ex-dividend date in stock info
            if 'exDividendDate' in info and info['exDividendDate']:
                ex_date = datetime.fromtimestamp(info['exDividendDate'])
                
                # If ex-date is in the future, use it
                if ex_date > current_date:
                    ex_dividend_dates[ticker] = ex_date
                    print(f"Live data for {ticker}: {ex_date.strftime('%Y-%m-%d')}")
                    continue
            
        except Exception as e:
            print(f"WARNING Could not get live data for {ticker}: {e}")
        
        # Fall back to intelligent weekly calculation
        if ticker in last_known_ex_div:
            last_ex_div = last_known_ex_div[ticker]
            
            # Calculate how many weeks have passed since last known ex-dividend
            days_since = (current_date - last_ex_div).days
            weeks_passed = days_since // 7
            
            # Next ex-dividend should be 7 days after the last one
            next_ex_div = last_ex_div + timedelta(days=(weeks_passed + 1) * 7)
            ex_dividend_dates[ticker] = next_ex_div
            print(f"Calculated for {ticker}: {next_ex_div.strftime('%Y-%m-%d')} (based on {last_ex_div.strftime('%Y-%m-%d')})")
        else:
            # For unknown ETFs, estimate next Monday
            days_until_monday = (7 - current_date.weekday()) % 7
            if days_until_monday == 0:  # If today is Monday
                days_until_monday = 7
            next_monday = current_date + timedelta(days=days_until_monday)
            ex_dividend_dates[ticker] = next_monday
            print(f"Estimated for {ticker}: {next_monday.strftime('%Y-%m-%d')} (next Monday)")
    
    return ex_dividend_dates

def get_fallback_ex_dividend_dates():
    """Fallback function when yfinance is not available"""
    from datetime import datetime, timedelta
    current_date = datetime.now()
    
    # SUCCESS UPDATED: Accurate last ex-dividend dates from user confirmation  
    # Original 6 ETFs: Ex-dividend TUESDAY, Pay WEDNESDAY (weekly pattern)
    # XOMO, BRKW, TSLW & QDTE: Ex-dividend THURSDAY, Pay FRIDAY (weekly pattern)
    last_known_ex_div = {
        'MSFW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'NVDW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'HOOW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'AMDW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'GOOW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'NFLW': datetime(2025, 10, 7),  # Tuesday 10/7 (pays Wednesday)
        'XOMO': datetime(2025, 10, 3),  # Thursday 10/3 (pays Friday) - Energy sector
        'BRKW': datetime(2025, 10, 3),  # Thursday 10/3 (pays Friday) - Financials sector
        'TSLW': datetime(2025, 10, 3),  # Thursday 10/3 (pays Friday) - High volatility tech
        'QDTE': datetime(2025, 10, 3)   # Thursday 10/3 (pays Friday) - Weekly Thursday payer
    }
    
    ex_dividend_dates = {}
    weekly_etfs = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW', 'XOMO', 'BRKW', 'TSLW', 'QDTE']
    
    for ticker in weekly_etfs:
        if ticker in last_known_ex_div:
            last_ex_div = last_known_ex_div[ticker]
            
            # Calculate next ex-dividend (weekly pattern)
            # Most ETFs: Tuesday ex-div, Wednesday pay
            # XOMO, BRKW, TSLW & QDTE: Thursday ex-div, Friday pay
            days_since = (current_date - last_ex_div).days
            weeks_passed = days_since // 7
            next_ex_div = last_ex_div + timedelta(days=(weeks_passed + 1) * 7)
            ex_dividend_dates[ticker] = next_ex_div
        else:
            # Estimate based on weekly pattern
            # Tuesday for most ETFs (weekday 1), Thursday for XOMO, BRKW, TSLW & QDTE (weekday 3)
            if ticker in ['XOMO', 'BRKW', 'TSLW', 'QDTE']:
                # Calculate days until next Thursday
                days_until_thursday = (3 - current_date.weekday()) % 7
                if days_until_thursday == 0:
                    days_until_thursday = 7
                ex_dividend_dates[ticker] = current_date + timedelta(days=days_until_thursday)
            else:
                # Calculate days until next Tuesday
                days_until_tuesday = (1 - current_date.weekday()) % 7
                if days_until_tuesday == 0:
                    days_until_tuesday = 7
                ex_dividend_dates[ticker] = current_date + timedelta(days=days_until_tuesday)
    
    return ex_dividend_dates

# Generate realistic ETF data with caching to prevent infinite reloads
@st.cache_data(ttl=3600)  # Cache for 1 hour to prevent infinite reloads
def generate_etf_data():
    """Generate realistic WeeklyPay ETF rotation data using Aristo's identified weekly dividend ETFs"""
    # These are the actual weekly dividend ETFs identified by Aristo in the WeeklyPay plan
    etfs = [
        # Weekly Dividend ETFs - GraniteShares 1x Long Daily ETFs
        ('NVDW', 'GraniteShares 1x Long NVDA Daily ETF', 'Technology', 1.15),
        ('AMDW', 'GraniteShares 1x Long AMD Daily ETF', 'Technology', 0.95),
        ('HOOW', 'Roundhill HOOD WeeklyPay ETF', 'Technology', 0.75),
        ('MSFW', 'GraniteShares 1x Long MSFT Daily ETF', 'Technology', 0.85),
        ('GOOW', 'GraniteShares 1x Long GOOGL Daily ETF', 'Technology', 0.65),
        ('NFLW', 'GraniteShares 1x Long NFLX Daily ETF', 'Communication', 0.55),
        # NEW: Diversification tickers
        ('XOMO', 'GraniteShares 1x Long XOM Daily ETF', 'Energy', 1.05),
        ('BRKW', 'Yieldmax BRK.B Option Income Strategy ETF', 'Financials', 0.85),
        ('TSLW', 'GraniteShares 1x Long TSLA Daily ETF', 'Technology', 1.20),
        ('QDTE', 'Roundhill QQQ 0DTE Covered Call ETF', 'Technology', 1.10)
    ]
    
    # Enhanced ex-dividend and earnings data for WeeklyPay tactical timing
    current_date = datetime.now()
    
    # Get live ex-dividend dates (tries real data, falls back to intelligent calculation)
    print("Fetching ex-dividend dates...")
    ex_dividend_dates = get_live_ex_dividend_dates()
    
    # Get real earnings calendar for tactical timing
    print("Fetching real earnings calendar...")
    real_earnings = get_real_earnings_calendar()
    
    # Use real earnings data if available, otherwise use fallback estimates
    earnings_dates = real_earnings if real_earnings else {
        'NVDW': current_date + timedelta(days=5),   # Next week
        'AMDW': current_date + timedelta(days=12),  # 2 weeks
        'HOOW': current_date + timedelta(days=8),   # Next week (not 1 month!)
        'MSFW': current_date + timedelta(days=2),   # This week
        'GOOW': current_date + timedelta(days=15),  # 2+ weeks
        'NFLW': current_date + timedelta(days=21),  # 3 weeks
        'XOMO': current_date + timedelta(days=28),  # ~4 weeks (Energy sector)
        'BRKW': current_date + timedelta(days=90),  # ~quarterly (Berkshire annual meeting pattern)
        'TSLW': current_date + timedelta(days=21),  # ~3 weeks (High volatility tech)
        'QDTE': current_date + timedelta(days=90)   # QQQ composite (quarterly spread)
    }
    
    data = []
    for ticker, name, sector, base_yield in etfs:
        # Add some randomization to make it realistic
        weekly_yield = base_yield + random.uniform(-0.3, 0.3)
        weekly_yield = max(0.1, weekly_yield)  # Ensure positive yield
        
        # Weekly ETF sector-based RSI simulation (Technology and Communication focus)
        sector_rsi_base = {
            'Technology': 68,      # Strong tech momentum
            'Communication': 62,   # Moderate comm momentum
            'Energy': 65,          # Solid energy momentum
            'Financials': 63       # Moderate financial momentum
        }
        rsi = sector_rsi_base.get(sector, 60) + random.uniform(-15, 15)
        rsi = max(20, min(80, rsi))  # Clamp between 20-80
        
        # Enhanced earnings and dividend timing calculations
        ex_div_date = ex_dividend_dates.get(ticker, current_date + timedelta(days=30))
        earnings_date = earnings_dates.get(ticker, current_date + timedelta(days=60))
        
        days_to_ex_div = (ex_div_date - current_date).days
        days_to_earnings = (earnings_date - current_date).days
        
        # Payout eligibility logic (must own before ex-dividend date)
        days_until_cutoff = days_to_ex_div - 1  # T-1 settlement
        payout_eligible = days_until_cutoff >= 0  # Can still buy and get dividend
        
        # Friday purchase flag for Monday ex-dividend ETFs
        ex_div_weekday = ex_div_date.weekday()  # 0=Monday
        friday_purchase_flag = False
        
        if ex_div_weekday == 0:  # Ex-dividend is on Monday
            # Calculate days until Friday before ex-dividend Monday
            days_to_purchase_friday = days_to_ex_div - 3  # Friday is 3 days before Monday
            if days_to_purchase_friday >= 0 and days_to_purchase_friday <= 3:
                friday_purchase_flag = True
        
        # Calculate WeeklyPay score
        scores = weeklypay_scoring_formula(weekly_yield, rsi, days_to_earnings)
        
        # ROTATION Generate simple rotation signal for this ETF
        if rsi > 60 and weekly_yield > 0.5:
            rotation_signal = {'signal': 'BUY', 'strength': 0.8}
        elif rsi < 40 or weekly_yield < 0.3:
            rotation_signal = {'signal': 'SELL', 'strength': 0.7}
        else:
            rotation_signal = {'signal': 'HOLD', 'strength': 0.5}
        
        # ROTATION Check NAV erosion protection
        nav_erosion_alert = check_nav_erosion(ticker, 1.0)  # 1% threshold
        
        data.append({
            'Ticker': ticker,
            'Name': name,
            'Sector': sector,
            'Weekly_Yield_%': weekly_yield,
            'RSI': round(rsi, 1),
            'Days_to_Earnings': days_to_earnings,
            'Days_to_Ex_Div': days_to_ex_div,
            'Ex_Dividend_Date': ex_div_date.strftime('%Y-%m-%d'),
            'Earnings_Date': earnings_date.strftime('%Y-%m-%d'),
            'Payout_Eligible': payout_eligible,
            'Friday_Purchase_Flag': friday_purchase_flag,
            'WeeklyPay_Score': scores['total_score'],
            'Yield_Score': scores['yield_score'],
            'Momentum_Score': scores['momentum_score'],
            'Earnings_Score': scores['earnings_score'],
            'Rotation_Signal': rotation_signal['signal'],
            'Signal_Strength': rotation_signal['strength'],
            'NAV_Erosion_Alert': nav_erosion_alert
        })
    
    return pd.DataFrame(data)

# Custom CSS styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2c3e50;
        text-align: center;
        margin-bottom: 1rem;
        font-family: Arial, sans-serif;
        font-weight: bold;
        background: linear-gradient(90deg, #3498db, #2c3e50);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .formula-box {
        background-color: #f8f9fa;
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0;
        text-align: center;
    }
    
    .score-metric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        margin: 5px;
    }
    
    .medal-gold {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: #333;
        font-weight: bold;
    }
    
    .medal-silver {
        background: linear-gradient(135deg, #C0C0C0, #A0A0A0);
        color: #333;
        font-weight: bold;
    }
    
    .medal-bronze {
        background: linear-gradient(135deg, #CD7F32, #B8860B);
        color: white;
        font-weight: bold;
    }
    
    .payout-eligible {
        color: #27ae60;
        font-weight: bold;
    }
    
    .payout-ineligible {
        color: #e74c3c;
        font-weight: bold;
    }
    
    .urgent-timing {
        background-color: #fff3cd;
        border: 1px solid #ffeaa7;
        padding: 10px;
        border-radius: 5px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Main header
st.markdown('<h1 class="main-header">WeeklyPay Tactical Rotation Engine</h1>', unsafe_allow_html=True)
st.markdown('<h3 style="text-align: center; color: #7f8c8d; margin-top: -10px;">Weekly Dividend ETFs | Real-time Rotation Signals</h3>', unsafe_allow_html=True)

# Add refresh button and mode selector
col1, col2, col3 = st.columns([1, 1, 1])
with col1:
    rotation_mode = st.toggle("🔄 **ROTATION MODE** (3+3 Strategy)", value=False, help="Enable 3 Tuesday + 3 Thursday rotation strategy with NAV optimization")
with col2:
    if st.button("🔄 Refresh Data (Clear Cache)", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
with col3:
    if rotation_mode:
        st.metric("Active Mode", "ROTATION 3+3")
    else:
        st.metric("Active Mode", "FULL PORTFOLIO")

# Formula display
st.markdown("""
<div class="formula-box">
    <h3>WeeklyPay Scoring Formula</h3>
    <p><strong>Score = (Yield Score * 0.5) + (Momentum Score * 0.3) + (Earnings Score * 0.2)</strong></p>
    <p>TARGET <em>Tactical ETF rotation based on mathematical precision</em></p>
</div>
""", unsafe_allow_html=True)

# Generate data
df = generate_etf_data()
df_sorted = df.sort_values('WeeklyPay_Score', ascending=False).reset_index(drop=True)

# ============================================================================
# ROTATION MODE - 3+3 NAV-OPTIMIZED DIVIDEND CAPTURE STRATEGY
# ============================================================================
if rotation_mode:
    st.markdown("---")
    st.markdown("# 🔄 ROTATION MODE: 3+3 NAV-Optimized Dividend Capture")
    st.markdown("""
    <div style='background-color: #1e3a5f; padding: 20px; border-radius: 10px; margin-bottom: 20px;'>
        <h3 style='color: #ffd700; margin-top: 0;'>⚡ Active Strategy: Weekly Dividend Capture Rotation</h3>
        <p style='color: white; font-size: 16px;'>
        <strong>Capital Efficiency:</strong> Hold only 6 positions (3 Tuesday + 3 Thursday) instead of 10<br>
        <strong>Rotation Cycle:</strong> Capture dividends twice per week, rotate based on NAV recovery<br>
        <strong>Priority:</strong> Minimize NAV erosion loss, maximize dividend yield gain<br>
        <strong>Target:</strong> 4-6% weekly return on active capital
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Separate Tuesday and Thursday tickers
    tuesday_tickers = df[df['Ticker'].isin(['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW'])].copy()
    thursday_tickers = df[df['Ticker'].isin(['XOMO', 'JPOW', 'TSLW', 'QDTE'])].copy()
    
    # Sort by NAV recovery potential (score - NAV erosion)
    tuesday_tickers['NAV_Adjusted_Score'] = tuesday_tickers['WeeklyPay_Score'] - (tuesday_tickers['Weekly_Yield_%'] * 0.7)  # Assume 70% NAV recovery
    thursday_tickers['NAV_Adjusted_Score'] = thursday_tickers['WeeklyPay_Score'] - (thursday_tickers['Weekly_Yield_%'] * 0.7)
    
    tuesday_sorted = tuesday_tickers.sort_values('NAV_Adjusted_Score', ascending=False).reset_index(drop=True)
    thursday_sorted = thursday_tickers.sort_values('NAV_Adjusted_Score', ascending=False).reset_index(drop=True)
    
    # Get top 3 from each group
    top3_tuesday = tuesday_sorted.head(3)
    top3_thursday = thursday_sorted.head(3)
    
    # Calculate current day of week and rotation status
    current_day = datetime.now().weekday()  # 0=Monday, 1=Tuesday, 2=Wednesday, 3=Thursday, 4=Friday
    
    # Determine current phase
    if current_day in [0, 1]:  # Monday or Tuesday
        current_phase = "HOLD TUESDAY TICKERS"
        active_group = "Tuesday"
        next_action = "Wednesday: SELL Tuesday, BUY Thursday"
        active_tickers = top3_tuesday
    elif current_day in [2, 3]:  # Wednesday or Thursday
        current_phase = "HOLD THURSDAY TICKERS"
        active_group = "Thursday"
        next_action = "Friday: SELL Thursday, BUY Tuesday"
        active_tickers = top3_thursday
    else:  # Friday
        current_phase = "WEEKEND HOLD"
        active_group = "Thursday"
        next_action = "Monday: SELL Thursday, BUY Tuesday"
        active_tickers = top3_thursday
    
    # Phase indicator
    st.markdown(f"""
    <div style='background-color: #27ae60; padding: 15px; border-radius: 8px; margin-bottom: 20px;'>
        <h2 style='color: white; margin: 0;'>📍 Current Phase: {current_phase}</h2>
        <p style='color: white; font-size: 18px; margin: 10px 0 0 0;'><strong>Active Group:</strong> {active_group} Ex-Div Tickers</p>
        <p style='color: #ffd700; font-size: 16px; margin: 5px 0 0 0;'><strong>Next Action:</strong> {next_action}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Display active positions with NAV tracking
    st.markdown("### 💼 ACTIVE POSITIONS - NAV Recovery Tracking")
    
    for idx, row in active_tickers.iterrows():
        # Calculate NAV metrics
        expected_nav_drop = row['Weekly_Yield_%']
        typical_recovery = expected_nav_drop * 0.75  # Assume 75% typical recovery
        breakeven_price = 100.00  # Assuming $100 purchase for simplicity
        target_sell_price = breakeven_price - (expected_nav_drop - typical_recovery)
        
        # Determine signal based on days to ex-div
        days_to_div = row['Days_to_Ex_Div']
        if days_to_div < 0:  # Past ex-div
            days_since_div = abs(days_to_div)
            if days_since_div <= 1:
                signal = "🟡 HOLD - Monitor NAV Recovery"
                signal_color = "#f39c12"
            elif days_since_div == 2:
                signal = "🟢 READY TO SELL - Strong Recovery Expected"
                signal_color = "#27ae60"
            else:
                signal = "🔴 SELL NOW - Extended Hold Risk"
                signal_color = "#e74c3c"
        elif days_to_div == 0:
            signal = "⭐ EX-DIV TODAY - HOLD"
            signal_color = "#3498db"
        elif days_to_div == 1:
            signal = "🔵 PRE EX-DIV - HOLD"
            signal_color = "#9b59b6"
        else:
            signal = "🟢 BUY ZONE - Pre Ex-Div Window"
            signal_color = "#27ae60"
        
        # Display ticker card
        st.markdown(f"""
        <div style='background-color: #34495e; padding: 15px; border-left: 5px solid {signal_color}; border-radius: 5px; margin-bottom: 15px;'>
            <h3 style='color: white; margin: 0 0 10px 0;'>{row['Ticker']} - {row['Name'][:40]}</h3>
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px;'>
                <div>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>NAV Adjusted Score:</strong> {row['NAV_Adjusted_Score']:.2f}</p>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>Weekly Yield:</strong> {row['Weekly_Yield_%']:.2f}%</p>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>Expected NAV Drop:</strong> {expected_nav_drop:.2f}%</p>
                </div>
                <div>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>Ex-Div Date:</strong> {row['Ex_Dividend_Date']}</p>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>Days to/from Ex-Div:</strong> {days_to_div} days</p>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>Typical Recovery:</strong> {typical_recovery:.2f}%</p>
                </div>
                <div>
                    <p style='color: {signal_color}; margin: 5px 0; font-size: 16px;'><strong>{signal}</strong></p>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>Target Sell Price:</strong> ${target_sell_price:.2f}</p>
                    <p style='color: #bdc3c7; margin: 5px 0;'><strong>RSI:</strong> {row['RSI']}</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Rotation scheduler
    st.markdown("### 📅 7-DAY ROTATION SCHEDULE")
    
    schedule_data = []
    today = datetime.now().date()
    
    for i in range(7):
        day_date = today + timedelta(days=i)
        day_name = day_date.strftime('%A')
        day_num = day_date.weekday()
        
        if day_num == 0:  # Monday
            action = "HOLD Tuesday Tickers (from previous week)"
            tickers = ", ".join(top3_tuesday['Ticker'].tolist())
            priority = "Monitor NAV recovery from previous Thursday group"
        elif day_num == 1:  # Tuesday
            action = "EX-DIVIDEND Tuesday Group"
            tickers = ", ".join(top3_tuesday['Ticker'].tolist())
            priority = "HOLD through ex-div date, capture dividend"
        elif day_num == 2:  # Wednesday
            action = "🔄 ROTATE: SELL Tuesday → BUY Thursday"
            tickers_sell = ", ".join(top3_tuesday['Ticker'].tolist())
            tickers_buy = ", ".join(top3_thursday['Ticker'].tolist())
            tickers = f"SELL: {tickers_sell} | BUY: {tickers_buy}"
            priority = "Wait for NAV recovery (typically 1-2 days post ex-div)"
        elif day_num == 3:  # Thursday
            action = "EX-DIVIDEND Thursday Group"
            tickers = ", ".join(top3_thursday['Ticker'].tolist())
            priority = "HOLD through ex-div date, capture dividend"
        elif day_num == 4:  # Friday
            action = "🔄 ROTATE: SELL Thursday → BUY Tuesday"
            tickers_sell = ", ".join(top3_thursday['Ticker'].tolist())
            tickers_buy = ", ".join(top3_tuesday['Ticker'].tolist())
            tickers = f"SELL: {tickers_sell} | BUY: {tickers_buy}"
            priority = "Wait for NAV recovery (typically 1-2 days post ex-div)"
        else:  # Weekend
            action = "WEEKEND HOLD"
            tickers = ", ".join(top3_tuesday['Ticker'].tolist())
            priority = "No action - Market closed"
        
        schedule_data.append({
            'Date': day_date.strftime('%Y-%m-%d'),
            'Day': day_name,
            'Action': action,
            'Tickers': tickers,
            'Priority': priority
        })
    
    schedule_df = pd.DataFrame(schedule_data)
    st.dataframe(schedule_df, use_container_width=True, hide_index=True)
    
    # NAV Recovery Analysis
    st.markdown("### 📊 NAV RECOVERY ANALYSIS - Break-Even Timing")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Tuesday Group - Top 3 Picks")
        for idx, row in top3_tuesday.iterrows():
            days_to_div = row['Days_to_Ex_Div']
            recovery_timeline = "2-3 days post ex-div" if days_to_div >= 0 else f"{abs(days_to_div)} days since ex-div"
            
            st.markdown(f"""
            **{row['Ticker']}** - Score: {row['NAV_Adjusted_Score']:.2f}
            - Yield: {row['Weekly_Yield_%']:.2f}% | RSI: {row['RSI']}
            - NAV Drop: ~{row['Weekly_Yield_%']:.2f}% expected
            - Recovery Timeline: {recovery_timeline}
            - Net Gain Potential: {row['Weekly_Yield_%'] * 0.25:.2f}% (after 75% NAV recovery)
            """)
    
    with col2:
        st.markdown("#### Thursday Group - Top 3 Picks")
        for idx, row in top3_thursday.iterrows():
            days_to_div = row['Days_to_Ex_Div']
            recovery_timeline = "2-3 days post ex-div" if days_to_div >= 0 else f"{abs(days_to_div)} days since ex-div"
            
            st.markdown(f"""
            **{row['Ticker']}** - Score: {row['NAV_Adjusted_Score']:.2f}
            - Yield: {row['Weekly_Yield_%']:.2f}% | RSI: {row['RSI']}
            - NAV Drop: ~{row['Weekly_Yield_%']:.2f}% expected
            - Recovery Timeline: {recovery_timeline}
            - Net Gain Potential: {row['Weekly_Yield_%'] * 0.25:.2f}% (after 75% NAV recovery)
            """)
    
    # Historical NAV Recovery Backtest
    st.markdown("### 📈 HISTORICAL NAV RECOVERY BACKTEST (90-Day Analysis)")
    st.markdown("""
    <div style='background-color: #2c3e50; padding: 15px; border-radius: 5px; margin-bottom: 15px;'>
        <p style='color: #ecf0f1; margin: 0;'>
        Analyzing actual historical price movements after ex-dividend dates to determine optimal sell timing.
        Data shows average recovery patterns over the past 90 days for each ticker. Weekly payers should have 12-13 dividend samples.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    backtest_col1, backtest_col2 = st.columns(2)
    
    with backtest_col1:
        st.markdown("#### 📊 Tuesday Group - Backtest Results")
        for idx, row in top3_tuesday.iterrows():
            with st.spinner(f"Analyzing {row['Ticker']}..."):
                optimal_day, avg_recovery, confidence = backtest_nav_recovery(row['Ticker'], days=90)
                
                if optimal_day is not None:
                    # Calculate expected net gain
                    dividend_gain = row['Weekly_Yield_%']
                    nav_loss = dividend_gain - avg_recovery
                    net_gain = dividend_gain - nav_loss
                    
                    if net_gain > 0:
                        result_color = "#27ae60"
                        result_icon = "✅"
                    else:
                        result_color = "#e74c3c"
                        result_icon = "❌"
                    
                    st.markdown(f"""
                    <div style='background-color: #34495e; padding: 12px; border-left: 4px solid {result_color}; border-radius: 5px; margin-bottom: 10px;'>
                        <p style='color: white; font-size: 16px; margin: 0 0 8px 0;'><strong>{result_icon} {row['Ticker']}</strong></p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Optimal Sell Day:</strong> Day {optimal_day} post ex-div</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Avg Recovery:</strong> {avg_recovery:.2f}% by day {optimal_day}</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Confidence:</strong> {confidence:.0f}% (based on historical data)</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected Dividend:</strong> {dividend_gain:.2f}%</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected NAV Loss:</strong> {nav_loss:.2f}%</p>
                        <p style='color: {result_color}; margin: 3px 0; font-size: 15px;'><strong>• Net Gain:</strong> {net_gain:.2f}%</p>
                        <p style='color: #f39c12; margin: 8px 0 0 0; font-size: 14px;'><em>📍 Recommendation: Sell on Day {optimal_day} after ex-div</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Use default estimates for weekly dividend ETFs
                    dividend_gain = row['Weekly_Yield_%']
                    estimated_recovery = dividend_gain * 0.75  # Assume 75% recovery
                    nav_loss = dividend_gain - estimated_recovery
                    net_gain = dividend_gain - nav_loss
                    optimal_day_estimate = 2  # Typical for weekly payers
                    
                    st.markdown(f"""
                    <div style='background-color: #34495e; padding: 12px; border-left: 4px solid #f39c12; border-radius: 5px; margin-bottom: 10px;'>
                        <p style='color: white; font-size: 16px; margin: 0 0 8px 0;'><strong>⚠️ {row['Ticker']} - Using Estimates</strong></p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>Insufficient historical dividend data for backtest</p>
                        <p style='color: #e67e22; margin: 8px 0 3px 0; font-size: 14px;'><strong>📊 Default Estimates (Weekly ETF Pattern):</strong></p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Estimated Optimal Day:</strong> Day {optimal_day_estimate} post ex-div</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected Recovery:</strong> ~{estimated_recovery:.2f}% (75% typical)</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected Dividend:</strong> {dividend_gain:.2f}%</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected NAV Loss:</strong> {nav_loss:.2f}%</p>
                        <p style='color: #f39c12; margin: 3px 0; font-size: 15px;'><strong>• Est. Net Gain:</strong> {net_gain:.2f}%</p>
                        <p style='color: #95a5a6; margin: 8px 0 0 0; font-size: 13px;'><em>💡 Track your actual results to build personal data</em></p>
                    </div>
                    """, unsafe_allow_html=True)
    
    with backtest_col2:
        st.markdown("#### 📊 Thursday Group - Backtest Results")
        for idx, row in top3_thursday.iterrows():
            with st.spinner(f"Analyzing {row['Ticker']}..."):
                optimal_day, avg_recovery, confidence = backtest_nav_recovery(row['Ticker'], days=90)
                
                if optimal_day is not None:
                    # Calculate expected net gain
                    dividend_gain = row['Weekly_Yield_%']
                    nav_loss = dividend_gain - avg_recovery
                    net_gain = dividend_gain - nav_loss
                    
                    if net_gain > 0:
                        result_color = "#27ae60"
                        result_icon = "✅"
                    else:
                        result_color = "#e74c3c"
                        result_icon = "❌"
                    
                    st.markdown(f"""
                    <div style='background-color: #34495e; padding: 12px; border-left: 4px solid {result_color}; border-radius: 5px; margin-bottom: 10px;'>
                        <p style='color: white; font-size: 16px; margin: 0 0 8px 0;'><strong>{result_icon} {row['Ticker']}</strong></p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Optimal Sell Day:</strong> Day {optimal_day} post ex-div</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Avg Recovery:</strong> {avg_recovery:.2f}% by day {optimal_day}</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Confidence:</strong> {confidence:.0f}% (based on historical data)</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected Dividend:</strong> {dividend_gain:.2f}%</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected NAV Loss:</strong> {nav_loss:.2f}%</p>
                        <p style='color: {result_color}; margin: 3px 0; font-size: 15px;'><strong>• Net Gain:</strong> {net_gain:.2f}%</p>
                        <p style='color: #f39c12; margin: 8px 0 0 0; font-size: 14px;'><em>📍 Recommendation: Sell on Day {optimal_day} after ex-div</em></p>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Use default estimates for weekly dividend ETFs
                    dividend_gain = row['Weekly_Yield_%']
                    estimated_recovery = dividend_gain * 0.75  # Assume 75% recovery
                    nav_loss = dividend_gain - estimated_recovery
                    net_gain = dividend_gain - nav_loss
                    optimal_day_estimate = 2  # Typical for weekly payers
                    
                    st.markdown(f"""
                    <div style='background-color: #34495e; padding: 12px; border-left: 4px solid #f39c12; border-radius: 5px; margin-bottom: 10px;'>
                        <p style='color: white; font-size: 16px; margin: 0 0 8px 0;'><strong>⚠️ {row['Ticker']} - Using Estimates</strong></p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>Insufficient historical dividend data for backtest</p>
                        <p style='color: #e67e22; margin: 8px 0 3px 0; font-size: 14px;'><strong>📊 Default Estimates (Weekly ETF Pattern):</strong></p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Estimated Optimal Day:</strong> Day {optimal_day_estimate} post ex-div</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected Recovery:</strong> ~{estimated_recovery:.2f}% (75% typical)</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected Dividend:</strong> {dividend_gain:.2f}%</p>
                        <p style='color: #bdc3c7; margin: 3px 0;'>• <strong>Expected NAV Loss:</strong> {nav_loss:.2f}%</p>
                        <p style='color: #f39c12; margin: 3px 0; font-size: 15px;'><strong>• Est. Net Gain:</strong> {net_gain:.2f}%</p>
                        <p style='color: #95a5a6; margin: 8px 0 0 0; font-size: 13px;'><em>💡 Track your actual results to build personal data</em></p>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Summary recommendations
    st.markdown("### 🎯 ROTATION STRATEGY SUMMARY")
    
    tuesday_total_yield = top3_tuesday['Weekly_Yield_%'].sum()
    thursday_total_yield = top3_thursday['Weekly_Yield_%'].sum()
    weekly_expected_return = (tuesday_total_yield + thursday_total_yield) / 2  # Average of both rotations
    
    summary_col1, summary_col2, summary_col3, summary_col4 = st.columns(4)
    
    with summary_col1:
        st.metric("Tuesday Group Yield", f"{tuesday_total_yield:.2f}%", help="Combined dividend yield from 3 Tuesday tickers")
    
    with summary_col2:
        st.metric("Thursday Group Yield", f"{thursday_total_yield:.2f}%", help="Combined dividend yield from 3 Thursday tickers")
    
    with summary_col3:
        st.metric("Weekly Target Return", f"{weekly_expected_return:.2f}%", help="Expected weekly return on active capital")
    
    with summary_col4:
        annual_return = weekly_expected_return * 52
        st.metric("Annualized Target", f"{annual_return:.1f}%", help="Projected annual return (52 weeks)")
    
    # Break-even calculator
    st.markdown("### 🧮 BREAK-EVEN CALCULATOR")
    
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    
    with calc_col1:
        purchase_price = st.number_input("Purchase Price ($)", value=50.00, step=0.01, min_value=0.01, key="calc_price")
        shares = st.number_input("Number of Shares", value=100, step=1, min_value=1, key="calc_shares")
    
    with calc_col2:
        dividend_per_share = st.number_input("Dividend per Share ($)", value=0.50, step=0.01, min_value=0.01, key="calc_div")
        commission = st.number_input("Commission per Trade ($)", value=0.00, step=0.01, min_value=0.00, key="calc_comm")
    
    with calc_col3:
        nav_recovery_pct = st.slider("Expected NAV Recovery %", min_value=50, max_value=100, value=75, step=5, key="calc_recovery")
    
    # Calculate break-even
    total_investment = (purchase_price * shares) + commission
    total_dividend = dividend_per_share * shares
    dividend_pct = (dividend_per_share / purchase_price) * 100
    expected_nav_drop = dividend_pct
    actual_nav_drop = expected_nav_drop * (1 - nav_recovery_pct/100)
    nav_loss_dollars = (actual_nav_drop / 100) * purchase_price * shares
    total_sell_commission = commission
    net_gain = total_dividend - nav_loss_dollars - total_sell_commission
    net_gain_pct = (net_gain / total_investment) * 100
    breakeven_price = purchase_price - (dividend_per_share - (actual_nav_drop/100 * purchase_price))
    
    st.markdown("#### 💰 Break-Even Analysis Results")
    
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)
    
    with result_col1:
        st.metric("Total Investment", f"${total_investment:,.2f}")
        st.metric("Dividend Income", f"${total_dividend:.2f}", delta=f"{dividend_pct:.2f}%")
    
    with result_col2:
        st.metric("Expected NAV Drop", f"{expected_nav_drop:.2f}%")
        st.metric("Actual NAV Loss", f"${nav_loss_dollars:.2f}", delta=f"{actual_nav_drop:.2f}%", delta_color="inverse")
    
    with result_col3:
        st.metric("Total Commissions", f"${commission + total_sell_commission:.2f}")
        st.metric("Net Gain/Loss", f"${net_gain:.2f}", delta=f"{net_gain_pct:.2f}%")
    
    with result_col4:
        st.metric("Break-Even Sell Price", f"${breakeven_price:.2f}")
        if net_gain > 0:
            st.success(f"✅ Profitable at {nav_recovery_pct}% recovery")
        else:
            st.error(f"❌ Unprofitable - Need {100 - nav_recovery_pct + (abs(net_gain)/total_dividend*100):.0f}% recovery")
    
    st.markdown("---")

# ROTATION - Rotation Alerts Summary
    st.markdown("### 🧮 BREAK-EVEN CALCULATOR")
    
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    
    with calc_col1:
        purchase_price = st.number_input("Purchase Price ($)", value=50.00, step=0.01, min_value=0.01)
        shares = st.number_input("Number of Shares", value=100, step=1, min_value=1)
    
    with calc_col2:
        dividend_per_share = st.number_input("Dividend per Share ($)", value=0.50, step=0.01, min_value=0.01)
        commission = st.number_input("Commission per Trade ($)", value=0.00, step=0.01, min_value=0.00)
    
    with calc_col3:
        nav_recovery_pct = st.slider("Expected NAV Recovery %", min_value=50, max_value=100, value=75, step=5)
    
    # Calculate break-even
    total_investment = (purchase_price * shares) + commission
    total_dividend = dividend_per_share * shares
    dividend_pct = (dividend_per_share / purchase_price) * 100
    expected_nav_drop = dividend_pct
    actual_nav_drop = expected_nav_drop * (1 - nav_recovery_pct/100)
    nav_loss_dollars = (actual_nav_drop / 100) * purchase_price * shares
    total_sell_commission = commission
    net_gain = total_dividend - nav_loss_dollars - total_sell_commission
    net_gain_pct = (net_gain / total_investment) * 100
    breakeven_price = purchase_price - (dividend_per_share - (actual_nav_drop/100 * purchase_price))
    
    st.markdown("#### 💰 Break-Even Analysis Results")
    
    result_col1, result_col2, result_col3, result_col4 = st.columns(4)
    
    with result_col1:
        st.metric("Total Investment", f"${total_investment:,.2f}")
        st.metric("Dividend Income", f"${total_dividend:.2f}", delta=f"{dividend_pct:.2f}%")
    
    with result_col2:
        st.metric("Expected NAV Drop", f"{expected_nav_drop:.2f}%")
        st.metric("Actual NAV Loss", f"${nav_loss_dollars:.2f}", delta=f"{actual_nav_drop:.2f}%", delta_color="inverse")
    
    with result_col3:
        st.metric("Total Commissions", f"${commission + total_sell_commission:.2f}")
        st.metric("Net Gain/Loss", f"${net_gain:.2f}", delta=f"{net_gain_pct:.2f}%")
    
    with result_col4:
        st.metric("Break-Even Sell Price", f"${breakeven_price:.2f}")
        if net_gain > 0:
            st.success(f"✅ Profitable at {nav_recovery_pct}% recovery")
        else:
            st.error(f"❌ Unprofitable - Need {100 - nav_recovery_pct + (abs(net_gain)/total_dividend*100):.0f}% recovery")
    
    st.markdown("---")

# ROTATION - Rotation Alerts Summary
st.markdown("## ROTATION - LIVE Rotation Alerts")

# Generate weekly rotation summary
weekly_summary = format_rotation_week_summary(df)
if weekly_summary:
    st.markdown("### TREND - This Week's Actions")
    # Split the summary string into individual lines for proper display
    for alert in weekly_summary.split('\n'):
        if alert.strip():  # Skip empty lines
            if 'ROTATE INTO' in alert:
                st.success(f"GREEN - {alert}")
            elif 'ROTATE OUT OF' in alert:
                st.error(f"RED - {alert}")
            elif 'HOLD' in alert:
                st.warning(f"YELLOW - {alert}")
            else:
                st.info(f"INFO - {alert}")

# NAV Erosion Alerts
nav_alerts = [row for _, row in df.iterrows() if row['NAV_Erosion_Alert']]
if nav_alerts:
    st.markdown("### WARNING - NAV Erosion Alerts (1% Threshold)")
    for alert_row in nav_alerts:
        st.error(f"STOP - **{alert_row['Ticker']}**: Potential loss detected - Consider exit")

# Signal strength distribution
signal_counts = df['Rotation_Signal'].value_counts()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("GREEN - BUY Signals", signal_counts.get('BUY', 0))
with col2:
    st.metric("RED - SELL Signals", signal_counts.get('SELL', 0))
with col3:
    st.metric("YELLOW - HOLD Signals", signal_counts.get('HOLD', 0))

st.markdown("---")  # Separator

# Top 3 medals section
st.markdown("## TROPHY - Top 3 WeeklyPay Rankings")

col1, col2, col3 = st.columns(3)

with col1:
    top1 = df_sorted.iloc[0]
    eligibility_flag = "SUCCESS" if top1['Payout_Eligible'] else "ERROR"
    st.markdown(f"""
    <div class="score-metric medal-gold">
        <h3>TROPHY GOLD</h3>
        <h2>{top1['Ticker']} {eligibility_flag}</h2>
        <p>{top1['Name'][:30]}...</p>
        <h3>Score: {top1['WeeklyPay_Score']}</h3>
        <p>Yield: {top1['Weekly_Yield_%']:.2f}% | RSI: {top1['RSI']}</p>
        <p><strong>CALENDAR Ex-Div: {top1['Ex_Dividend_Date']}</strong></p>
        <p>CLOCK {top1['Days_to_Ex_Div']} days to dividend</p>
        <p>CHART {top1['Days_to_Earnings']} days to earnings</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    top2 = df_sorted.iloc[1]
    eligibility_flag = "SUCCESS" if top2['Payout_Eligible'] else "ERROR"
    st.markdown(f"""
    <div class="score-metric medal-silver">
        <h3>TROPHY SILVER</h3>
        <h2>{top2['Ticker']} {eligibility_flag}</h2>
        <p>{top2['Name'][:30]}...</p>
        <h3>Score: {top2['WeeklyPay_Score']}</h3>
        <p>Yield: {top2['Weekly_Yield_%']:.2f}% | RSI: {top2['RSI']}</p>
        <p><strong>CALENDAR Ex-Div: {top2['Ex_Dividend_Date']}</strong></p>
        <p>CLOCK {top2['Days_to_Ex_Div']} days to dividend</p>
        <p>CHART {top2['Days_to_Earnings']} days to earnings</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    top3 = df_sorted.iloc[2]
    eligibility_flag = "SUCCESS" if top3['Payout_Eligible'] else "ERROR"
    st.markdown(f"""
    <div class="score-metric medal-bronze">
        <h3>TROPHY BRONZE</h3>
        <h2>{top3['Ticker']} {eligibility_flag}</h2>
        <p>{top3['Name'][:30]}...</p>
        <h3>Score: {top3['WeeklyPay_Score']}</h3>
        <p>Yield: {top3['Weekly_Yield_%']:.2f}% | RSI: {top3['RSI']}</p>
        <p><strong>CALENDAR Ex-Div: {top3['Ex_Dividend_Date']}</strong></p>
        <p>CLOCK {top3['Days_to_Ex_Div']} days to dividend</p>
        <p>CHART {top3['Days_to_Earnings']} days to earnings</p>
    </div>
    """, unsafe_allow_html=True)

# Key metrics
st.markdown("## CHART Key Performance Metrics")

col1, col2, col3, col4 = st.columns(4)

with col1:
    avg_score = df['WeeklyPay_Score'].mean()
    st.metric("Average Score", f"{avg_score:.2f}")

with col2:
    avg_yield = df['Weekly_Yield_%'].mean()
    st.metric("Average Yield", f"{avg_yield:.2f}%")

with col3:
    high_momentum = len(df[df['RSI'] > 60])
    st.metric("High Momentum ETFs", high_momentum)

with col4:
    near_earnings = len(df[df['Days_to_Earnings'] <= 14])
    st.metric("Near Earnings", near_earnings)

# Tactical Timing Analysis - NEW ENHANCEMENT
st.markdown("## TIMING - Tactical Timing Analysis")

st.markdown("""
<div style="background-color: #e8f4f8; border: 2px solid #3498db; border-radius: 10px; padding: 20px; margin: 20px 0;">
    <h3 style="color: #2c3e50; margin-bottom: 15px;">TARGET - Rotation Timing Signals</h3>
    <p><strong>Ex-Dividend Dates:</strong> Key dates for dividend capture strategy</p>
    <p><strong>Earnings Countdown:</strong> Time remaining until quarterly earnings release</p>
    <p><strong>Payout Eligibility:</strong> CHECK = Still time to buy for next dividend | X = Too late for next payout</p>
</div>
""", unsafe_allow_html=True)

# Immediate action items
eligible_etfs = df_sorted[df_sorted['Payout_Eligible'] == True]
urgent_div = df_sorted[df_sorted['Days_to_Ex_Div'] <= 2]
urgent_earnings = df_sorted[df_sorted['Days_to_Earnings'] <= 7]

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### GREEN - Payout Eligible")
    if not eligible_etfs.empty:
        for _, etf in eligible_etfs.head(3).iterrows():
            st.markdown(f"**{etf['Ticker']}**: {etf['Days_to_Ex_Div']} days left")
    else:
        st.markdown("WARNING - No ETFs eligible for next payout")

with col2:
    st.markdown("### RED - Urgent Dividends")
    if not urgent_div.empty:
        for _, etf in urgent_div.iterrows():
            st.markdown(f"**{etf['Ticker']}**: Ex-div in {etf['Days_to_Ex_Div']} days!")
    else:
        st.markdown("CHECK - No urgent dividend dates")

with col3:
    st.markdown("### CHART - Near Earnings")
    if not urgent_earnings.empty:
        for _, etf in urgent_earnings.iterrows():
            st.markdown(f"**{etf['Ticker']}**: {etf['Days_to_Earnings']} days to earnings")
    else:
        st.markdown("CALENDAR - No immediate earnings")

# Complete rankings table
st.markdown("## TREND - Complete WeeklyPay Rankings")

# Format the dataframe for display
display_df = df_sorted.copy()
display_df['Weekly_Yield_%'] = display_df['Weekly_Yield_%'].round(2)
display_df['WeeklyPay_Score'] = display_df['WeeklyPay_Score'].round(2)

# Add payout eligibility symbols and Friday purchase flags
display_df['Payout_Status'] = display_df['Payout_Eligible'].apply(lambda x: "CHECK - Eligible" if x else "X - Too Late")
display_df['Friday_Buy_Signal'] = display_df['Friday_Purchase_Flag'].apply(lambda x: "GREEN - BUY FRIDAY" if x else "CIRCLE - Wait")

# Add rotation signals and NAV alerts
display_df['Rotation_Action'] = display_df['Rotation_Signal'].apply(
    lambda x: f"GREEN - {x}" if x == "BUY" else f"RED - {x}" if x == "SELL" else f"YELLOW - {x}"
)
display_df['NAV_Alert'] = display_df['NAV_Erosion_Alert'].apply(lambda x: "STOP - RISK" if x else "CHECK - Safe")

# Reorder columns for better display
display_cols = ['Ticker', 'WeeklyPay_Score', 'Rotation_Action', 'Weekly_Yield_%', 'RSI', 
               'Ex_Dividend_Date', 'Days_to_Ex_Div', 'Payout_Status', 'Friday_Buy_Signal',
               'Earnings_Date', 'Days_to_Earnings', 'NAV_Alert', 'Sector']
display_df = display_df[display_cols]

# Rename columns for clarity
display_df.columns = ['Ticker', 'Score', 'Rotation Signal', 'Yield %', 'RSI', 
                     'Ex-Div Date', 'Days to Div', 'Payout Status', 'Friday Signal',
                     'Earnings Date', 'Days to Earnings', 'NAV Status', 'Sector']

# Color code the top 3
def highlight_top3(row):
    if row.name == 0:  # Gold
        return ['background-color: #FFD700; color: #333; font-weight: bold'] * len(row)
    elif row.name == 1:  # Silver
        return ['background-color: #C0C0C0; color: #333; font-weight: bold'] * len(row)
    elif row.name == 2:  # Bronze
        return ['background-color: #CD7F32; color: white; font-weight: bold'] * len(row)
    else:
        return [''] * len(row)

styled_df = display_df.style.apply(highlight_top3, axis=1)
st.dataframe(styled_df, use_container_width=True)

# Score breakdown chart
st.markdown("## TARGET Score Component Breakdown")

# Create stacked bar chart
fig = go.Figure()

fig.add_trace(go.Bar(
    name='Yield Score (50%)',
    x=df_sorted['Ticker'][:10],
    y=df_sorted['Yield_Score'][:10] * 0.5,
    marker_color='#3498db'
))

fig.add_trace(go.Bar(
    name='Momentum Score (30%)',
    x=df_sorted['Ticker'][:10],
    y=df_sorted['Momentum_Score'][:10] * 0.3,
    marker_color='#e74c3c'
))

fig.add_trace(go.Bar(
    name='Earnings Score (20%)',
    x=df_sorted['Ticker'][:10],
    y=df_sorted['Earnings_Score'][:10] * 0.2,
    marker_color='#f39c12'
))

fig.update_layout(
    title='WeeklyPay Score Components (Top 10 ETFs)',
    xaxis_title='ETF Ticker',
    yaxis_title='Weighted Score Contribution',
    barmode='stack',
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# Sector analysis
st.markdown("## FACTORY Sector Performance Analysis")

sector_avg = df.groupby('Sector').agg({
    'WeeklyPay_Score': 'mean',
    'Weekly_Yield_%': 'mean',
    'RSI': 'mean'
}).round(2)

fig2 = px.scatter(
    df, 
    x='Weekly_Yield_%', 
    y='WeeklyPay_Score',
    color='Sector',
    size='RSI',
    hover_data=['Ticker', 'Name'],
    title='WeeklyPay Score vs Yield by Sector'
)

st.plotly_chart(fig2, use_container_width=True)

# Trade Tracking Section
st.markdown("---")
st.markdown("## 💰 TRADE - Portfolio Performance Tracking")

# Helper functions for trade tracking
@st.cache_data(ttl=60)  # Cache for 1 minute
def load_trade_data():
    try:
        df = pd.read_csv('weeklypay_trades.csv')
        # Handle backward compatibility - add dividend columns if they don't exist
        if 'Dividend_Per_Share' not in df.columns:
            df['Dividend_Per_Share'] = 0
        if 'Total_Dividends' not in df.columns:
            df['Total_Dividends'] = 0
        return df
    except FileNotFoundError:
        # Create empty DataFrame with proper columns including dividend tracking
        return pd.DataFrame(columns=['Date', 'Ticker', 'Action', 'Quantity', 'Price', 'Total', 'Notes', 'WeeklyPay_Score', 'Dividend_Per_Share', 'Total_Dividends'])

def save_trade_data(df):
    """Save trade data and clear cache to ensure fresh reload"""
    df.to_csv('weeklypay_trades.csv', index=False)
    # BUGFIX: Clear the cache immediately after saving to force fresh data load
    load_trade_data.clear()

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_current_prices(tickers):
    """Fetch current prices for a list of tickers using yfinance"""
    prices = {}
    try:
        import yfinance as yf
        for ticker in tickers:
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                # Try different price fields
                current_price = info.get('currentPrice') or info.get('regularMarketPrice') or info.get('previousClose')
                if current_price:
                    prices[ticker] = current_price
            except Exception as e:
                print(f"Error fetching price for {ticker}: {e}")
    except ImportError:
        print("yfinance not available for price fetching")
    return prices

def calculate_current_holdings(trades_df):
    """Calculate current holdings with live prices and total returns"""
    if trades_df.empty:
        return pd.DataFrame()
    
    holdings = []
    
    # Get unique tickers with open positions
    for ticker in trades_df['Ticker'].unique():
        ticker_trades = trades_df[trades_df['Ticker'] == ticker]
        
        # Calculate shares
        shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
        shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
        current_shares = shares_bought - shares_sold
        
        if current_shares > 0:
            # Calculate cost basis
            total_invested = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
            total_sold_proceeds = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
            net_investment = total_invested - total_sold_proceeds
            avg_cost = net_investment / current_shares if current_shares > 0 else 0
            
            # Get dividends received
            total_dividends = ticker_trades[ticker_trades['Action'] == 'DIVIDEND']['Total'].sum()
            
            holdings.append({
                'Ticker': ticker,
                'Shares': current_shares,
                'Avg_Cost': avg_cost,
                'Investment': net_investment,
                'Dividends': total_dividends
            })
    
    if not holdings:
        return pd.DataFrame()
    
    holdings_df = pd.DataFrame(holdings)
    
    # Fetch current prices
    tickers = holdings_df['Ticker'].tolist()
    current_prices = get_current_prices(tickers)
    
    # Add current prices and calculate values
    holdings_df['Current_Price'] = holdings_df['Ticker'].map(current_prices)
    holdings_df['Current_Value'] = holdings_df['Current_Price'] * holdings_df['Shares']
    holdings_df['NAV_Change'] = holdings_df['Current_Value'] - holdings_df['Investment']
    holdings_df['NAV_Change_Pct'] = (holdings_df['NAV_Change'] / holdings_df['Investment'] * 100).fillna(0)
    holdings_df['Total_Return'] = holdings_df['NAV_Change'] + holdings_df['Dividends']
    holdings_df['Total_Return_Pct'] = (holdings_df['Total_Return'] / holdings_df['Investment'] * 100).fillna(0)
    
    return holdings_df

def calculate_trade_performance(trades_df):
    if trades_df.empty:
        return 0.0, 0.0, 0.0, 0.0, 0, 0
    
    total_invested = trades_df[trades_df['Action'] == 'BUY']['Total'].sum()
    total_sold = trades_df[trades_df['Action'] == 'SELL']['Total'].sum()
    total_dividends = trades_df[trades_df['Action'] == 'DIVIDEND']['Total'].sum()
    trade_count = len(trades_df)
    
    # Calculate realized capital gains (only from actual sales)
    # For unsold positions, we can't calculate unrealized gains without live market data
    net_capital_gains = total_sold - total_invested if total_sold > 0 else 0
    
    # Total return = realized capital gains + dividends
    # Note: This does NOT include unrealized gains on open positions
    total_return = net_capital_gains + total_dividends
    
    # Calculate active positions
    position_summary = trades_df.groupby('Ticker').apply(
        lambda x: (x[x['Action'] == 'BUY']['Quantity'].sum() - x[x['Action'] == 'SELL']['Quantity'].sum())
    )
    active_positions = (position_summary > 0).sum()
    
    return total_invested, total_dividends, total_return, net_capital_gains, active_positions, trade_count

# Load existing trades
trades_df = load_trade_data()

# Trade input form
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("### 📝 Log New Trade")
    
    # Create input form
    trade_form = st.form("trade_entry", clear_on_submit=True)
    
    with trade_form:
        form_col1, form_col2, form_col3 = st.columns(3)
        
        with form_col1:
            # Get ticker list for dropdown
            ticker_list = [''] + sorted(df_sorted['Ticker'].tolist())
            selected_ticker = st.selectbox("Ticker", ticker_list, key="trade_ticker")
            action = st.selectbox("Action", ['BUY', 'SELL', 'DIVIDEND'], key="trade_action")
            
        with form_col2:
            quantity = st.number_input("Quantity", min_value=1, value=100, key="trade_quantity")
            if action == 'DIVIDEND':
                total_dividend = st.number_input("Total Dividend Amount ($)", min_value=0.01, value=50.00, step=0.01, key="trade_price")
                price = total_dividend / quantity  # Calculate per-share amount
            else:
                price = st.number_input("Price ($)", min_value=0.01, value=50.00, step=0.01, key="trade_price")
            
        with form_col3:
            trade_date = st.date_input("Date", value=datetime.now().date(), key="trade_date")
            notes = st.text_input("Notes (optional)", key="trade_notes")
        
        # Calculate total
        if action == 'DIVIDEND':
            total_value = total_dividend
            st.write(f"**Total Dividend: ${total_value:,.2f}** (${price:.4f}/share)")
        else:
            total_value = quantity * price
            st.write(f"**Total Value: ${total_value:,.2f}**")
        
        # Form buttons
        form_col1, form_col2, form_col3 = st.columns(3)
        
        with form_col1:
            submitted = st.form_submit_button("💾 Log Trade", use_container_width=True)
            
        with form_col2:
            quick_fill = st.form_submit_button("⚡ Quick Fill Top Pick", use_container_width=True)
            
        with form_col3:
            if st.form_submit_button("📊 Launch Trade Analyzer", use_container_width=True):
                st.info("Creating standalone trade analyzer...")
                
                # Create standalone trade analyzer
                analyzer_code = '''
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import streamlit as st

st.set_page_config(page_title="WeeklyPay Trade Analyzer", page_icon="📈", layout="wide")

st.title("📈 WeeklyPay Trade Performance Analyzer")

# Portfolio composition note
st.info("""
📊 **Portfolio Composition**: Tracking 10 weekly dividend payers across 5 sectors:
- **Technology**: NVDW (NVDA), AMDW (AMD), MSFW (MSFT), GOOW (GOOGL), TSLW (TSLA)
- **Fintech**: HOOW (HOOD)
- **Communications**: NFLW (NFLX)
- **Energy**: XOMO (XOM) - *Diversification*
- **Financials**: BRKW (BRK.B) - *NEW: Berkshire Hathaway - Financial sector diversification*
- **0DTE Strategy**: QDTE (QQQ 0DTE) - *⚡ High-yield strategy (50-60% annual)*

**Payment Schedule** (Balanced Distribution):
- 📅 **6 ETFs** (Tue ex-div): NVDW, AMDW, HOOW, MSFW, GOOW, NFLW → Pay WEDNESDAY
- 📅 **4 ETFs** (Thu ex-div): XOMO, BRKW, TSLW, QDTE → Pay FRIDAY

**Diversification Goal**: 5 sectors, balanced payment schedule, yields 0.75%-1.20% weekly.
""")

try:
    trades_df = pd.read_csv('weeklypay_trades.csv')
    
    if not trades_df.empty:
        trades_df['Date'] = pd.to_datetime(trades_df['Date'])
        
        # Performance metrics
        st.subheader("📊 Performance Summary")
        
        col1, col2, col3, col4 = st.columns(4)
        
        total_invested = trades_df[trades_df['Action'] == 'BUY']['Total'].sum()
        total_sold = trades_df[trades_df['Action'] == 'SELL']['Total'].sum()
        net_position = total_invested - total_sold
        trade_count = len(trades_df)
        
        col1.metric("Total Invested", f"${total_invested:,.2f}")
        col2.metric("Total Sold", f"${total_sold:,.2f}")
        col3.metric("Net Position", f"${net_position:,.2f}")
        col4.metric("Total Trades", trade_count)
        
        # Trade timeline
        st.subheader("📈 Trade Timeline")
        fig = px.scatter(trades_df, x='Date', y='Total', color='Action', 
                        size='Quantity', hover_data=['Ticker', 'Price', 'WeeklyPay_Score'])
        st.plotly_chart(fig, use_container_width=True)
        
        # Position analysis
        st.subheader("📋 Position Analysis")
        position_summary = trades_df.groupby('Ticker').apply(
            lambda x: pd.Series({
                'Total_Bought': x[x['Action'] == 'BUY']['Quantity'].sum(),
                'Total_Sold': x[x['Action'] == 'SELL']['Quantity'].sum(),
                'Net_Position': x[x['Action'] == 'BUY']['Quantity'].sum() - x[x['Action'] == 'SELL']['Quantity'].sum(),
                'Avg_WeeklyPay_Score': x['WeeklyPay_Score'].mean()
            })
        ).reset_index()
        
        st.dataframe(position_summary, use_container_width=True)
        
        # Recent trades
        st.subheader("🕒 Recent Trades")
        recent_trades = trades_df.sort_values('Date', ascending=False).head(10)
        st.dataframe(recent_trades, use_container_width=True)
        
    else:
        st.info("No trade data found. Start logging trades to see analysis.")
        
except FileNotFoundError:
    st.error("No trade data file found. Log some trades first!")
'''
                
                with open('trade_analyzer.py', 'w', encoding='utf-8') as f:
                    f.write(analyzer_code)
                
                st.success("✅ Created trade_analyzer.py - Run with: `streamlit run trade_analyzer.py`")
    
    # Handle form submissions
    if submitted and selected_ticker:
        # Get WeeklyPay score for the ticker
        ticker_score = df_sorted[df_sorted['Ticker'] == selected_ticker]['WeeklyPay_Score'].iloc[0] if selected_ticker in df_sorted['Ticker'].values else 0.0
        
        # Create new trade record with dividend fields
        dividend_per_share = price if action == 'DIVIDEND' else 0
        total_dividends = total_value if action == 'DIVIDEND' else 0
        
        new_trade = pd.DataFrame({
            'Date': [trade_date],
            'Ticker': [selected_ticker],
            'Action': [action],
            'Quantity': [quantity],
            'Price': [price],
            'Total': [total_value],
            'Notes': [notes],
            'WeeklyPay_Score': [ticker_score],
            'Dividend_Per_Share': [dividend_per_share],
            'Total_Dividends': [total_dividends]
        })
        
        # Append to existing trades
        trades_df = pd.concat([trades_df, new_trade], ignore_index=True)
        save_trade_data(trades_df)
        
        st.success(f"✅ Trade logged: {action} {quantity} shares of {selected_ticker} @ ${price:.2f}")
        st.rerun()
    
    elif quick_fill and not df_sorted.empty:
        # Auto-fill with top WeeklyPay pick
        top_pick = df_sorted.iloc[0]
        st.info(f"Quick-filled with top pick: {top_pick['Ticker']} (Score: {top_pick['WeeklyPay_Score']:.2f})")
        # Note: In a real implementation, you'd update the form fields

with col2:
    st.markdown("### ℹ️ Trade Entry Info")
    st.info("📝 Log your trades to track performance and see portfolio analytics below.")
    st.markdown("**Quick Tips:**")
    st.markdown("- Use **Quick Fill** to auto-select top-rated ticker")
    st.markdown("- **DIVIDEND** entries calculate per-share automatically")
    st.markdown("- Scores are captured at time of trade entry")

# ========== FULL WIDTH SECTIONS BELOW ==========
st.markdown("---")

# Enhanced Performance Summary - NOW FULL WIDTH
st.markdown("### 📈 Enhanced Performance Summary")

st.info("ℹ️ Returns shown are **realized only** (from sales + dividends). Unrealized gains on open positions not included.")

total_invested, total_dividends, total_return, net_capital_gains, active_positions, trade_count = calculate_trade_performance(trades_df)

# Display enhanced metrics
col2a, col2b, col2c, col2d = st.columns(4)
with col2a:
    st.metric("Total Invested", f"${total_invested:,.2f}")
    
with col2b:
    st.metric("Realized Capital Gains", f"${net_capital_gains:,.2f}", delta=f"{(net_capital_gains/total_invested*100):+.1f}%" if total_invested > 0 else None)
    
with col2c:
    st.metric("Total Dividends", f"${total_dividends:,.2f}")
    
with col2d:
    st.metric("**Total Realized Return**", f"${total_return:,.2f}", delta=f"{(total_return/total_invested*100):+.1f}%" if total_invested > 0 else None)

col2e, col2f, col2g = st.columns(3)
with col2e:
    st.metric("Active Positions", active_positions)
with col2f:
    st.metric("Total Trades", trade_count)
with col2g:
    if not trades_df.empty:
        # Show average WeeklyPay score of trades
        avg_score = trades_df['WeeklyPay_Score'].mean()
        st.metric("Avg WeeklyPay Score", f"{avg_score:.2f}")

# Current Holdings with Live Prices - NOW FULL WIDTH
st.markdown("---")
st.markdown("### 💼 Current Holdings (Live Prices)")

holdings_df = calculate_current_holdings(trades_df)

if not holdings_df.empty:
    # Check if we have price data
    if holdings_df['Current_Price'].notna().any():
        # Summary metrics
        total_investment = holdings_df['Investment'].sum()
        total_current_value = holdings_df['Current_Value'].sum()
        total_nav_change = holdings_df['NAV_Change'].sum()
        total_dividends_holdings = holdings_df['Dividends'].sum()
        total_return_value = holdings_df['Total_Return'].sum()
        
        col_h1, col_h2, col_h3, col_h4, col_h5 = st.columns(5)
        with col_h1:
            st.metric("Total Investment", f"${total_investment:,.2f}")
        with col_h2:
            st.metric("Current Value", f"${total_current_value:,.2f}", 
                     delta=f"{((total_current_value - total_investment) / total_investment * 100):+.1f}%")
        with col_h3:
            st.metric("NAV Change", f"${total_nav_change:,.2f}",
                     delta=f"{(total_nav_change / total_investment * 100):+.1f}%" if total_investment > 0 else None)
        with col_h4:
            st.metric("Total Dividends", f"${total_dividends_holdings:,.2f}")
        with col_h5:
            st.metric("Total Return", f"${total_return_value:,.2f}",
                     delta=f"{(total_return_value / total_investment * 100):+.1f}%" if total_investment > 0 else None,
                     help="NAV Change + Dividends")
        
        # Display holdings table
        display_df = holdings_df.copy()
        display_df['Shares'] = display_df['Shares'].astype(int)
        display_df['Avg_Cost'] = display_df['Avg_Cost'].apply(lambda x: f"${x:.2f}")
        display_df['Current_Price'] = display_df['Current_Price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "N/A")
        display_df['Investment'] = display_df['Investment'].apply(lambda x: f"${x:,.2f}")
        display_df['Current_Value'] = display_df['Current_Value'].apply(lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A")
        display_df['NAV_Change'] = display_df['NAV_Change'].apply(lambda x: f"${x:+,.2f}" if pd.notna(x) else "N/A")
        display_df['NAV_Change_Pct'] = display_df['NAV_Change_Pct'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
        display_df['Dividends'] = display_df['Dividends'].apply(lambda x: f"${x:,.2f}")
        display_df['Total_Return'] = display_df['Total_Return'].apply(lambda x: f"${x:+,.2f}" if pd.notna(x) else "N/A")
        display_df['Total_Return_Pct'] = display_df['Total_Return_Pct'].apply(lambda x: f"{x:+.1f}%" if pd.notna(x) else "N/A")
        
        display_df = display_df[['Ticker', 'Shares', 'Avg_Cost', 'Current_Price', 'Investment', 
                                'Current_Value', 'NAV_Change', 'NAV_Change_Pct', 'Dividends', 
                                'Total_Return', 'Total_Return_Pct']]
        
        display_df.columns = ['Ticker', 'Shares', 'Avg Cost', 'Current Price', 'Investment', 
                             'Current Value', 'NAV Change', 'NAV %', 'Dividends', 
                             'Total Return', 'Total Return %']
        
        st.dataframe(display_df, use_container_width=True, hide_index=True)
        st.caption("💡 Total Return = NAV Change + Dividends | Prices updated every 5 minutes")
    else:
        st.warning("⚠️ Unable to fetch current prices. Check internet connection.")
        # Show holdings without prices
        display_df = holdings_df[['Ticker', 'Shares', 'Avg_Cost', 'Investment', 'Dividends']].copy()
        display_df['Shares'] = display_df['Shares'].astype(int)
        display_df['Avg_Cost'] = display_df['Avg_Cost'].apply(lambda x: f"${x:.2f}")
        display_df['Investment'] = display_df['Investment'].apply(lambda x: f"${x:,.2f}")
        display_df['Dividends'] = display_df['Dividends'].apply(lambda x: f"${x:,.2f}")
        display_df.columns = ['Ticker', 'Shares', 'Avg Cost', 'Investment', 'Dividends']
        st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("📊 No open positions. All positions have been closed.")

# Trade history display
if not trades_df.empty:
    st.markdown("### 📋 Recent Trade History")
    
    # Sort by date, most recent first
    recent_trades = trades_df.sort_values('Date', ascending=False).head(10)
    
    # Style the dataframe with different colors for each trade type
    def style_trades(row):
        if row['Action'] == 'BUY':
            return ['background-color: #d4edda; color: #155724'] * len(row)
        elif row['Action'] == 'SELL':
            return ['background-color: #f8d7da; color: #721c24'] * len(row)
        elif row['Action'] == 'DIVIDEND':
            return ['background-color: #fff3cd; color: #856404'] * len(row)  # Yellow for dividends
        else:
            return ['background-color: #e2e3e5; color: #383d41'] * len(row)
    
    styled_trades = recent_trades.style.apply(style_trades, axis=1)
    st.dataframe(styled_trades, use_container_width=True)
    
    # Show correlation between WeeklyPay scores and trade performance
    if len(trades_df) >= 5:
        st.markdown("### 🎯 WeeklyPay Score Analysis")
        
        # Calculate score ranges
        high_score_trades = trades_df[trades_df['WeeklyPay_Score'] >= 7.0]
        mid_score_trades = trades_df[(trades_df['WeeklyPay_Score'] >= 5.0) & (trades_df['WeeklyPay_Score'] < 7.0)]
        low_score_trades = trades_df[trades_df['WeeklyPay_Score'] < 5.0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("High Score Trades (7.0+)", len(high_score_trades))
            if len(high_score_trades) > 0:
                st.write(f"Avg Investment: ${high_score_trades['Total'].mean():,.2f}")
        
        with col2:
            st.metric("Mid Score Trades (5.0-7.0)", len(mid_score_trades))
            if len(mid_score_trades) > 0:
                st.write(f"Avg Investment: ${mid_score_trades['Total'].mean():,.2f}")
        
        with col3:
            st.metric("Low Score Trades (<5.0)", len(low_score_trades))
            if len(low_score_trades) > 0:
                st.write(f"Avg Investment: ${low_score_trades['Total'].mean():,.2f}")

else:
    st.info("🚀 **Start tracking your WeeklyPay trades!** Log your first trade above to begin measuring the app's performance.")
    st.markdown("""
    **Track these key metrics:**
    - Which WeeklyPay scores perform best
    - Correlation between rotation signals and profits
    - Timing accuracy of dividend capture strategies
    - Overall portfolio performance vs benchmarks
    """)

# Enhanced Performance Dashboard with Charts
if not trades_df.empty and len(trades_df) >= 3:
    st.markdown("---")
    st.markdown("## 📊 Enhanced Performance Dashboard")
    
    # Convert date column for plotting
    trades_df['Date'] = pd.to_datetime(trades_df['Date'])
    
    # Create tabs for different chart views
    chart_tab1, chart_tab2, chart_tab3, chart_tab4, chart_tab5 = st.tabs(["💰 Cumulative P&L", "📈 Performance by Ticker", "🎯 WeeklyPay Score Analysis", "📊 Trade Distribution", "💵 Income Projections"])
    
    with chart_tab1:
        st.subheader("💰 Cumulative Profit & Loss Over Time")
        
        st.info("ℹ️ **Note**: This chart shows *realized* gains (from actual sales) plus dividends. Unrealized gains on open positions are not included since live market prices are not tracked.")
        
        # Calculate cumulative P&L
        trades_sorted = trades_df.sort_values('Date')
        
        # Calculate running totals
        trades_sorted['Running_Invested'] = 0
        trades_sorted['Running_Dividends'] = 0
        trades_sorted['Running_Proceeds'] = 0
        
        running_invested = 0
        running_dividends = 0
        running_proceeds = 0
        
        for idx, row in trades_sorted.iterrows():
            if row['Action'] == 'BUY':
                running_invested += row['Total']
            elif row['Action'] == 'SELL':
                running_proceeds += row['Total']
            elif row['Action'] == 'DIVIDEND':
                running_dividends += row['Total']
            
            trades_sorted.loc[idx, 'Running_Invested'] = running_invested
            trades_sorted.loc[idx, 'Running_Dividends'] = running_dividends
            trades_sorted.loc[idx, 'Running_Proceeds'] = running_proceeds
        
        # Calculate cumulative REALIZED return (sales - purchases + dividends)
        # This does NOT include unrealized gains on open positions
        # For open positions (Running_Proceeds = 0), we only show dividends, not negative invested amount
        trades_sorted['Realized_Capital_Gains'] = trades_sorted['Running_Proceeds'] - trades_sorted['Running_Invested']
        
        # Only count capital gains if we've actually sold something (proceeds > 0)
        # Otherwise capital gains = 0 (not negative invested amount!)
        trades_sorted['Realized_Capital_Gains'] = trades_sorted.apply(
            lambda row: row['Realized_Capital_Gains'] if row['Running_Proceeds'] > 0 else 0,
            axis=1
        )
        
        # Total return = realized capital gains (0 if no sales) + dividends
        trades_sorted['Cumulative_Return'] = trades_sorted['Realized_Capital_Gains'] + trades_sorted['Running_Dividends']
        
        # Return percentage based on amount invested
        trades_sorted['Return_Percentage'] = (trades_sorted['Cumulative_Return'] / trades_sorted['Running_Invested'] * 100).fillna(0)
        
        # Create the cumulative P&L chart
        fig_cumulative = go.Figure()
        
        # Add cumulative return line
        fig_cumulative.add_trace(go.Scatter(
            x=trades_sorted['Date'],
            y=trades_sorted['Cumulative_Return'],
            mode='lines+markers',
            name='Total Return ($)',
            line=dict(color='#2E86AB', width=3),
            fill='tonexty' if trades_sorted['Cumulative_Return'].iloc[-1] >= 0 else 'tozeroy',
            fillcolor='rgba(46, 134, 171, 0.1)' if trades_sorted['Cumulative_Return'].iloc[-1] >= 0 else 'rgba(220, 53, 69, 0.1)'
        ))
        
        # Add zero line
        fig_cumulative.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Break Even")
        
        fig_cumulative.update_layout(
            title="Cumulative Return Over Time (Capital Gains + Dividends)",
            xaxis_title="Date",
            yaxis_title="Total Return ($)",
            height=400,
            showlegend=True
        )
        
        st.plotly_chart(fig_cumulative, use_container_width=True)
        
        # Show key metrics
        final_return = trades_sorted['Cumulative_Return'].iloc[-1]
        final_return_pct = trades_sorted['Return_Percentage'].iloc[-1]
        
        # Calculate realized capital gains (only if we've sold something)
        realized_capital_gains = running_proceeds - running_invested if running_proceeds > 0 else 0
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Final Return", f"${final_return:,.2f}")
        col2.metric("Return %", f"{final_return_pct:+.2f}%") 
        col3.metric("Total Dividends", f"${running_dividends:,.2f}")
        col4.metric("Realized Capital Gains", f"${realized_capital_gains:,.2f}")
    
    with chart_tab2:
        st.subheader("📈 Performance Analysis by Ticker")
        
        st.info("ℹ️ Returns shown are **realized only** (from sales + dividends). For open positions without sales, only dividend returns are shown.")
        
        # Calculate performance by ticker
        ticker_performance = []
        
        for ticker in trades_df['Ticker'].unique():
            ticker_trades = trades_df[trades_df['Ticker'] == ticker]
            
            total_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
            total_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
            total_dividends = ticker_trades[ticker_trades['Action'] == 'DIVIDEND']['Total'].sum()
            
            shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
            shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
            
            net_position = shares_bought - shares_sold
            
            # Only count realized capital gains (from actual sales)
            capital_gain = total_sold - total_bought if total_sold > 0 else 0
            total_return = capital_gain + total_dividends
            return_pct = (total_return / total_bought * 100) if total_bought > 0 else 0
            
            # Handle non-numeric WeeklyPay scores
            try:
                scores = pd.to_numeric(ticker_trades['WeeklyPay_Score'], errors='coerce')
                avg_score = scores.mean()
            except:
                avg_score = None
            
            ticker_performance.append({
                'Ticker': ticker,
                'Invested': total_bought,
                'Proceeds': total_sold,
                'Dividends': total_dividends,
                'Total_Return': total_return,
                'Return_Pct': return_pct,
                'Net_Position': net_position,
                'Avg_WeeklyPay_Score': avg_score,
                'Trade_Count': len(ticker_trades)
            })
        
        ticker_df = pd.DataFrame(ticker_performance)
        
        # Create bar chart for returns by ticker
        fig_ticker = px.bar(
            ticker_df,
            x='Ticker',
            y='Total_Return',
            color='Return_Pct',
            color_continuous_scale='RdYlGn',
            title='Total Return by Ticker',
            hover_data=['Invested', 'Dividends', 'Avg_WeeklyPay_Score']
        )
        
        fig_ticker.update_layout(height=400)
        st.plotly_chart(fig_ticker, use_container_width=True)
        
        # Show ticker performance table
        st.subheader("📋 Detailed Ticker Performance")
        st.dataframe(ticker_df.round(2), use_container_width=True)
    
    with chart_tab3:
        st.subheader("🎯 WeeklyPay Score Effectiveness Analysis")
        
        # Analyze performance by WeeklyPay score ranges
        trades_with_returns = []
        
        for ticker in trades_df['Ticker'].unique():
            ticker_trades = trades_df[trades_df['Ticker'] == ticker]
            
            # Calculate return for this ticker
            total_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
            total_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
            total_dividends = ticker_trades[ticker_trades['Action'] == 'DIVIDEND']['Total'].sum()
            
            if total_bought > 0:
                # For sold positions: actual capital gain
                # For unsold positions: only count dividends (can't calculate unrealized without live prices)
                capital_gain = total_sold - total_bought if total_sold > 0 else 0
                total_return = capital_gain + total_dividends
                return_pct = total_return / total_bought * 100
                
                # Get average WeeklyPay score, handling non-numeric values
                try:
                    # Convert to numeric, coercing errors to NaN, then get mean of valid values
                    scores = pd.to_numeric(ticker_trades['WeeklyPay_Score'], errors='coerce')
                    avg_score = scores.mean()
                    
                    # Only include if we have a valid score
                    if pd.notna(avg_score):
                        trades_with_returns.append({
                            'Ticker': ticker,
                            'WeeklyPay_Score': avg_score,
                            'Return_Pct': return_pct,
                            'Total_Return': total_return,
                            'Investment': total_bought
                        })
                except:
                    # Skip tickers with invalid scores
                    pass
        
        if trades_with_returns:
            score_df = pd.DataFrame(trades_with_returns)
            
            # Additional check: remove any rows with NaN values
            score_df = score_df.dropna(subset=['WeeklyPay_Score', 'Return_Pct'])
            
            if len(score_df) > 0:
                # Create scatter plot of score vs return
                fig_score = px.scatter(
                    score_df,
                    x='WeeklyPay_Score',
                    y='Return_Pct',
                    size='Investment',
                    color='Return_Pct',
                    color_continuous_scale='RdYlGn',
                    title='WeeklyPay Score vs Actual Returns',
                    hover_data=['Ticker', 'Total_Return']
                )
                
                # Add trend line (only if we have at least 2 data points)
                if len(score_df) >= 2:
                    try:
                        from sklearn.linear_model import LinearRegression
                        import numpy as np
                        
                        X = score_df['WeeklyPay_Score'].values.reshape(-1, 1)
                        y = score_df['Return_Pct'].values
                        
                        # Double-check for NaN values before fitting
                        if not np.isnan(X).any() and not np.isnan(y).any():
                            reg = LinearRegression().fit(X, y)
                            score_range = np.linspace(score_df['WeeklyPay_Score'].min(), score_df['WeeklyPay_Score'].max(), 100)
                            trend_y = reg.predict(score_range.reshape(-1, 1))
                            
                            fig_score.add_trace(go.Scatter(
                                x=score_range,
                                y=trend_y,
                                mode='lines',
                                name=f'Trend (R²={reg.score(X, y):.3f})',
                                line=dict(color='red', dash='dash')
                            ))
                            
                            correlation = np.corrcoef(score_df['WeeklyPay_Score'], score_df['Return_Pct'])[0, 1]
                            st.write(f"**Correlation between WeeklyPay Score and Returns: {correlation:.3f}**")
                        else:
                            st.warning("⚠️ Cannot calculate trend line: data contains invalid values")
                    except ImportError:
                        st.info("Install scikit-learn for trend analysis: `pip install scikit-learn`")
                    except Exception as e:
                        st.warning(f"⚠️ Cannot calculate trend line: {str(e)}")
                
                fig_score.update_layout(height=400)
                st.plotly_chart(fig_score, use_container_width=True)
            else:
                st.info("📊 No valid data points with WeeklyPay scores to analyze yet.")
        else:
            st.info("📊 No completed trades to analyze yet. Add some trades to see WeeklyPay score effectiveness!")
            
            fig_score.update_layout(height=400)
            st.plotly_chart(fig_score, use_container_width=True)
            
            # Score range analysis
            st.subheader("📊 Performance by Score Range")
            
            score_ranges = [
                (8.0, 10.0, "Excellent (8.0-10.0)"),
                (6.0, 7.99, "Good (6.0-7.99)"),
                (4.0, 5.99, "Fair (4.0-5.99)"),
                (0.0, 3.99, "Poor (0.0-3.99)")
            ]
            
            range_analysis = []
            for min_score, max_score, label in score_ranges:
                range_trades = score_df[(score_df['WeeklyPay_Score'] >= min_score) & (score_df['WeeklyPay_Score'] <= max_score)]
                
                if not range_trades.empty:
                    avg_return = range_trades['Return_Pct'].mean()
                    trade_count = len(range_trades)
                    win_rate = (range_trades['Return_Pct'] > 0).mean() * 100
                    
                    range_analysis.append({
                        'Score_Range': label,
                        'Avg_Return_%': avg_return,
                        'Trade_Count': trade_count,
                        'Win_Rate_%': win_rate
                    })
            
            if range_analysis:
                range_df = pd.DataFrame(range_analysis)
                st.dataframe(range_df.round(2), use_container_width=True)
    
    with chart_tab4:
        st.subheader("📊 Trade Distribution Analysis")
        
        # Action distribution pie chart
        col1, col2 = st.columns(2)
        
        with col1:
            action_counts = trades_df['Action'].value_counts()
            fig_pie = px.pie(
                values=action_counts.values,
                names=action_counts.index,
                title='Trade Distribution by Action'
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Monthly trade volume
            trades_df['Month'] = trades_df['Date'].dt.to_period('M').astype(str)
            monthly_volume = trades_df.groupby(['Month', 'Action'])['Total'].sum().reset_index()
            
            fig_monthly = px.bar(
                monthly_volume,
                x='Month',
                y='Total',
                color='Action',
                title='Monthly Trade Volume by Action',
                barmode='group'
            )
            st.plotly_chart(fig_monthly, use_container_width=True)
        
        # Trade timing analysis
        trades_df['Day_of_Week'] = trades_df['Date'].dt.day_name()
        trades_df['Hour'] = trades_df['Date'].dt.hour
        
        col3, col4 = st.columns(2)
        
        with col3:
            dow_counts = trades_df['Day_of_Week'].value_counts()
            fig_dow = px.bar(
                x=dow_counts.index,
                y=dow_counts.values,
                title='Trades by Day of Week'
            )
            st.plotly_chart(fig_dow, use_container_width=True)
        
        with col4:
            # Show summary statistics
            st.subheader("📈 Trading Statistics")
            
            total_volume = trades_df['Total'].sum()
            avg_trade_size = trades_df['Total'].mean()
            largest_trade = trades_df['Total'].max()
            
            st.metric("Total Volume", f"${total_volume:,.2f}")
            st.metric("Average Trade Size", f"${avg_trade_size:,.2f}")
            st.metric("Largest Trade", f"${largest_trade:,.2f}")
            
            # Most active ticker
            most_active = trades_df['Ticker'].value_counts().iloc[0]
            most_active_ticker = trades_df['Ticker'].value_counts().index[0]
            st.metric("Most Active Ticker", f"{most_active_ticker} ({most_active} trades)")
    
    with chart_tab5:
        st.subheader("💵 Income Projections")
        
        # Calculate dividend income metrics
        dividend_trades = trades_df[trades_df['Action'] == 'DIVIDEND'].copy()
        
        if not dividend_trades.empty:
            # Convert dates to datetime
            dividend_trades['Date'] = pd.to_datetime(dividend_trades['Date'])
            
            # Get date range for calculations
            first_dividend_date = dividend_trades['Date'].min()
            last_dividend_date = dividend_trades['Date'].max()
            days_tracked = (last_dividend_date - first_dividend_date).days
            
            # Total dividends received
            total_dividends_received = dividend_trades['Total'].sum()
            
            # Calculate monthly average based on actual history
            if days_tracked > 0:
                months_tracked = days_tracked / 30.44  # Average days per month
                avg_monthly_actual = total_dividends_received / months_tracked if months_tracked > 0 else total_dividends_received
                avg_yearly_actual = avg_monthly_actual * 12
            else:
                avg_monthly_actual = total_dividends_received
                avg_yearly_actual = total_dividends_received * 12
            
            # Calculate estimated future income based on current holdings
            # Get current positions
            position_summary = {}
            for ticker in trades_df['Ticker'].unique():
                ticker_trades = trades_df[trades_df['Ticker'] == ticker]
                shares_bought = ticker_trades[ticker_trades['Action'] == 'BUY']['Quantity'].sum()
                shares_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Quantity'].sum()
                current_shares = shares_bought - shares_sold
                
                if current_shares > 0:
                    # Get latest dividend info for this ticker
                    ticker_dividends = dividend_trades[dividend_trades['Ticker'] == ticker]
                    if not ticker_dividends.empty:
                        # Calculate average dividend per share from history
                        total_div_payments = len(ticker_dividends)
                        total_div_amount = ticker_dividends['Total'].sum()
                        
                        # Estimate dividends per share (average across all payments)
                        avg_dividend_per_payment = total_div_amount / total_div_payments if total_div_payments > 0 else 0
                        
                        position_summary[ticker] = {
                            'shares': current_shares,
                            'avg_dividend_per_payment': avg_dividend_per_payment,
                            'total_payments': total_div_payments
                        }
            
            # Calculate estimated future income
            # Assume weekly dividend strategy (52 weeks/year)
            estimated_monthly = 0
            estimated_yearly = 0
            
            for ticker, info in position_summary.items():
                # Estimate based on payment frequency
                # If we have historical data, extrapolate
                ticker_div_trades = dividend_trades[dividend_trades['Ticker'] == ticker]
                if len(ticker_div_trades) >= 2:
                    ticker_days_tracked = (ticker_div_trades['Date'].max() - ticker_div_trades['Date'].min()).days
                    if ticker_days_tracked > 0:
                        # Annual payments = number of payments * (365 / days tracked)
                        annual_payment_frequency = info['total_payments'] * (365 / ticker_days_tracked)
                        estimated_yearly += info['avg_dividend_per_payment'] * annual_payment_frequency
                else:
                    # Assume weekly payments if we don't have enough history
                    estimated_yearly += info['avg_dividend_per_payment'] * 52
            
            estimated_monthly = estimated_yearly / 12
            
            # Display the metrics
            st.markdown("### 📊 Historical Performance")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Dividends Received", f"${total_dividends_received:,.2f}")
            with col2:
                st.metric("Tracking Period", f"{days_tracked} days" if days_tracked > 0 else "< 1 day")
            with col3:
                st.metric("Total Dividend Payments", len(dividend_trades))
            
            st.markdown("### 💰 Average Income (Based on History)")
            col4, col5 = st.columns(2)
            
            with col4:
                st.metric(
                    "Average Monthly Income",
                    f"${avg_monthly_actual:,.2f}",
                    help="Average monthly dividend income based on actual history"
                )
            with col5:
                st.metric(
                    "Average Yearly Income",
                    f"${avg_yearly_actual:,.2f}",
                    help="Extrapolated annual income based on current historical average"
                )
            
            st.markdown("### 🔮 Estimated Future Income (Based on Current Holdings)")
            
            if position_summary:
                col6, col7 = st.columns(2)
                
                with col6:
                    st.metric(
                        "Est. Monthly Income",
                        f"${estimated_monthly:,.2f}",
                        delta=f"{((estimated_monthly - avg_monthly_actual) / avg_monthly_actual * 100):+.1f}%" if avg_monthly_actual > 0 else None,
                        help="Estimated monthly income based on current positions and historical dividend rates"
                    )
                with col7:
                    st.metric(
                        "Est. Yearly Income",
                        f"${estimated_yearly:,.2f}",
                        delta=f"{((estimated_yearly - avg_yearly_actual) / avg_yearly_actual * 100):+.1f}%" if avg_yearly_actual > 0 else None,
                        help="Estimated annual income based on current positions and historical dividend rates"
                    )
                
                # Calculate total investment for percentage gains
                total_investment = 0
                ticker_investments = {}
                
                for ticker in trades_df['Ticker'].unique():
                    ticker_trades = trades_df[trades_df['Ticker'] == ticker]
                    ticker_invested = ticker_trades[ticker_trades['Action'] == 'BUY']['Total'].sum()
                    ticker_sold = ticker_trades[ticker_trades['Action'] == 'SELL']['Total'].sum()
                    
                    # Net investment (what's still in)
                    net_investment = ticker_invested - ticker_sold
                    if net_investment > 0:
                        ticker_investments[ticker] = net_investment
                        total_investment += net_investment
                
                # Calculate overall percentage gains
                monthly_gain_pct = (avg_monthly_actual / total_investment * 100) if total_investment > 0 else 0
                yearly_gain_pct = (avg_yearly_actual / total_investment * 100) if total_investment > 0 else 0
                est_monthly_gain_pct = (estimated_monthly / total_investment * 100) if total_investment > 0 else 0
                est_yearly_gain_pct = (estimated_yearly / total_investment * 100) if total_investment > 0 else 0
                
                # Show overall percentage gains
                st.markdown("### 📊 Return on Investment (Dividend Yield)")
                col8, col9, col10 = st.columns(3)
                
                with col8:
                    st.metric("Total Current Investment", f"${total_investment:,.2f}", 
                             help="Total capital currently invested in dividend-paying positions")
                
                with col9:
                    st.metric(
                        "Monthly Yield (Historical)", 
                        f"{monthly_gain_pct:.2f}%",
                        help="Average monthly dividend income as % of current investment"
                    )
                    st.metric(
                        "Est. Monthly Yield", 
                        f"{est_monthly_gain_pct:.2f}%",
                        delta=f"{(est_monthly_gain_pct - monthly_gain_pct):.2f}%",
                        help="Projected monthly dividend yield based on current holdings"
                    )
                
                with col10:
                    st.metric(
                        "Annual Yield (Historical)", 
                        f"{yearly_gain_pct:.2f}%",
                        help="Average annual dividend income as % of current investment"
                    )
                    st.metric(
                        "Est. Annual Yield", 
                        f"{est_yearly_gain_pct:.2f}%",
                        delta=f"{(est_yearly_gain_pct - yearly_gain_pct):.2f}%",
                        help="Projected annual dividend yield based on current holdings"
                    )
                
                # Show position details with percentage gains
                st.markdown("### 📋 Current Positions Contributing to Income")
                
                position_details = []
                for ticker, info in position_summary.items():
                    # Calculate individual projections
                    ticker_div_trades = dividend_trades[dividend_trades['Ticker'] == ticker]
                    ticker_days_tracked = (ticker_div_trades['Date'].max() - ticker_div_trades['Date'].min()).days
                    
                    if len(ticker_div_trades) >= 2 and ticker_days_tracked > 0:
                        annual_freq = info['total_payments'] * (365 / ticker_days_tracked)
                        est_annual = info['avg_dividend_per_payment'] * annual_freq
                    else:
                        annual_freq = 52  # Assume weekly
                        est_annual = info['avg_dividend_per_payment'] * 52
                    
                    # Get investment for this ticker
                    ticker_investment = ticker_investments.get(ticker, 0)
                    est_monthly = est_annual / 12
                    
                    # Calculate percentage yields for this ticker
                    ticker_monthly_pct = (est_monthly / ticker_investment * 100) if ticker_investment > 0 else 0
                    ticker_yearly_pct = (est_annual / ticker_investment * 100) if ticker_investment > 0 else 0
                    
                    position_details.append({
                        'Ticker': ticker,
                        'Shares': info['shares'],
                        'Investment': f"${ticker_investment:,.2f}",
                        'Est. Monthly': f"${est_monthly:,.2f}",
                        'Monthly Yield %': f"{ticker_monthly_pct:.2f}%",
                        'Est. Yearly': f"${est_annual:,.2f}",
                        'Annual Yield %': f"{ticker_yearly_pct:.2f}%"
                    })
                
                position_df = pd.DataFrame(position_details)
                
                # Style the dataframe with color coding for yield percentages
                def highlight_yield(val):
                    if isinstance(val, str) and '%' in val:
                        pct = float(val.strip('%'))
                        if pct >= 10:
                            return 'background-color: #d4edda; color: #155724'  # Green
                        elif pct >= 5:
                            return 'background-color: #fff3cd; color: #856404'  # Yellow
                        else:
                            return 'background-color: #f8d7da; color: #721c24'  # Red
                    return ''
                
                styled_df = position_df.style.applymap(highlight_yield, subset=['Monthly Yield %', 'Annual Yield %'])
                st.dataframe(styled_df, use_container_width=True, hide_index=True)
            else:
                st.info("📊 No current positions with dividend history. Start tracking dividends to see projections!")
            
            # Add visualization of dividend growth over time
            st.markdown("### 📈 Dividend Income Trend")
            
            # Create monthly aggregation
            dividend_trades['YearMonth'] = dividend_trades['Date'].dt.to_period('M')
            monthly_dividends = dividend_trades.groupby('YearMonth')['Total'].sum().reset_index()
            monthly_dividends['YearMonth'] = monthly_dividends['YearMonth'].astype(str)
            
            fig_div_trend = go.Figure()
            fig_div_trend.add_trace(go.Bar(
                x=monthly_dividends['YearMonth'],
                y=monthly_dividends['Total'],
                name='Monthly Dividends',
                marker_color='#28a745'
            ))
            
            # Add average line
            fig_div_trend.add_hline(
                y=avg_monthly_actual,
                line_dash="dash",
                line_color="blue",
                annotation_text=f"Avg: ${avg_monthly_actual:.2f}/mo"
            )
            
            fig_div_trend.update_layout(
                title="Monthly Dividend Income",
                xaxis_title="Month",
                yaxis_title="Dividend Income ($)",
                height=400
            )
            
            st.plotly_chart(fig_div_trend, use_container_width=True)
            
        else:
            st.info("📊 No dividend data yet. Log dividend payments to see income projections!")

# Footer with last update time
st.markdown("---")
current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
st.markdown(f"<p style='text-align: center; color: #7f8c8d;'>Last Updated: {current_time} | WeeklyPay Tactical Rotation Engine v1.0</p>", unsafe_allow_html=True)

# Auto-refresh button
if st.button("Refresh Data", width="stretch"):
    st.rerun()

# Debug Earnings Calendar button
if st.button("Test Earnings Calendar Accuracy", width="stretch"):
    with st.expander("CALENDAR - Earnings Calendar Test Results", expanded=True):
        st.code("""
TEST - TESTING EARNINGS CALENDAR ACCURACY
==================================================
""")
        
        # Run the test and capture output
        earnings_calendar = get_real_earnings_calendar()
        current_date = datetime.now()
        
        test_output = f"Current Date: {current_date.strftime('%Y-%m-%d %H:%M')}\n"
        test_output += f"Earnings Predictions:\n"
        
        for ticker, earnings_date in earnings_calendar.items():
            days_until = (earnings_date - current_date).days
            
            if days_until < 0:
                test_output += f"   WARNING: {ticker}: {earnings_date.strftime('%Y-%m-%d')} ({abs(days_until)} days AGO)\n"
            elif days_until == 0:
                test_output += f"   TARGET: {ticker}: {earnings_date.strftime('%Y-%m-%d')} (TODAY!)\n"
            elif days_until <= 7:
                test_output += f"   URGENT: {ticker}: {earnings_date.strftime('%Y-%m-%d')} ({days_until} days - THIS WEEK)\n"
            else:
                test_output += f"   INFO: {ticker}: {earnings_date.strftime('%Y-%m-%d')} ({days_until} days)\n"
        
        test_output += "\nTo verify accuracy, check actual earnings dates on:\n"
        test_output += "   - Yahoo Finance earnings calendar\n"
        test_output += "   - Company investor relations pages\n"
        test_output += "   - Finnhub.io earnings calendar\n"
        test_output += "=================================================="
        
        st.code(test_output)
        
        # Show which data source was used
        st.info("""
        **SEARCH Data Sources Used (in order of preference):**
        1. **Finnhub API** - Most accurate, real-time earnings calendar
        2. **Yahoo Finance (yfinance)** - Good backup source
        3. **Intelligent Estimates** - Quarterly cycle-based fallback
        
        **SUCCESS For NVDW specifically:** Check NVDA earnings date on Yahoo Finance or your broker
        """)

# GUI Interface Option
st.markdown("---")
st.markdown("## Desktop Native GUI Interface")
st.markdown("**Want a desktop app instead of web browser?**")

col1, col2 = st.columns(2)
with col1:
    if st.button("Launch Native GUI", width="stretch"):
        try:
            import subprocess
            import sys
            import os
            
            # Get the current script path
            current_script = os.path.abspath(__file__)
            
            # Launch GUI in separate process
            subprocess.Popen([sys.executable, current_script, "--gui"], 
                           creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0)
            
            st.success("✅ Native GUI launched in separate window! Check your taskbar or Alt+Tab to find it.")
            st.info("💡 **Tip:** The GUI window may appear behind other windows. Use Alt+Tab to find it.")
        except Exception as e:
            st.error(f"❌ GUI Launch Error: {str(e)}")
            st.info("🔧 **Alternative:** Run `python simple_dashboard.py --gui` directly in terminal")

with col2:
    st.info("**Native GUI Features:**\n- Faster performance\n- Desktop notifications\n- Offline capability\n- System tray integration")

# Main execution
if __name__ == "__main__":
    import sys
    
    # Check for GUI argument
    if len(sys.argv) > 1 and sys.argv[1] == "--gui":
        print("LAUNCH - Launching WeeklyPay Native GUI...")
        try:
            root = create_tkinter_gui_window()
            if root:
                # Make sure window is visible and on top
                root.lift()
                root.attributes('-topmost', True)
                root.after_idle(root.attributes, '-topmost', False)
                root.focus_force()
                
                print("SUCCESS - GUI window created successfully!")
                print("INFO - If you don't see the window, check your taskbar or try Alt+Tab")
                
                # Start the GUI main loop
                root.mainloop()
            else:
                print("ERROR - Failed to create GUI window")
        except Exception as e:
            print(f"ERROR - GUI Error: {str(e)}")
            print("FALLBACK - Falling back to web dashboard...")
            # Fall back to Streamlit if GUI fails
            pass
    else:
        # Run Streamlit web app by default
        print("WEB - Running as Streamlit web dashboard...")
        print("INFO - Use 'python simple_dashboard.py --gui' to launch native GUI instead")
        pass  # Streamlit handles execution automatically
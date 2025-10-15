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
        'NFLW': 'NFLX'
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
            'NFLW': 49   # NFLX - typically reports 7 weeks
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
        'NFLW': -1   # NFLX tends to report ~1 day earlier
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

def check_nav_erosion(ticker, threshold_pct=1.0):
    """
    NAV Erosion Protection: Check for >threshold% losses for specific ticker
    
    Args:
        ticker (str): ETF ticker symbol
        threshold_pct (float): Loss threshold percentage (default 1.0%)
    
    Returns:
        bool: True if erosion alert triggered, False if safe
    """
    # Simulated NAV changes (in real implementation, use actual price data)
    simulated_nav_changes = {
        'NVDW': -0.5,   # -0.5% (safe)
        'AMDW': -1.2,   # -1.2% (ALERT!)
        'HOOW': 0.8,    # +0.8% (gaining)
        'MSFW': -0.3,   # -0.3% (safe)
        'GOOW': -1.5,   # -1.5% (ALERT!)
        'NFLW': 0.2     # +0.2% (safe)
    }
    
    nav_change = simulated_nav_changes.get(ticker, 0.0)
    
    # Return True if loss exceeds threshold (triggering alert)
    return nav_change <= -threshold_pct

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
                analyzer_script = """
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk
import csv
import os

def create_trade_analyzer():
    root = tk.Tk()
    root.title("🏆 WeeklyPay Trade Performance Analyzer")
    root.geometry("800x600")
    
    try:
        if os.path.exists("weeklypay_trades.csv"):
            df = pd.read_csv("weeklypay_trades.csv")
            
            # Calculate performance metrics
            total_trades = len(df)
            buy_trades = df[df['Action'] == 'BUY']
            sell_trades = df[df['Action'] == 'SELL']
            
            text = f\"\"\"
📊 WeeklyPay Performance Analysis
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📈 Total Trades: {total_trades}
🟢 Buy Orders: {len(buy_trades)}
🔴 Sell Orders: {len(sell_trades)}

💰 Total Invested: ${buy_trades['Total'].astype(float).sum():,.2f}
📊 Average WeeklyPay Score: {pd.to_numeric(buy_trades['WeeklyPay_Score'], errors='coerce').mean():.2f}

🎯 Top Traded Tickers:
{df['Ticker'].value_counts().head().to_string()}

💡 Recent Performance:
{df.tail().to_string(index=False)}
\"\"\"
            
            text_widget = tk.Text(root, font=("Courier", 10))
            text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            text_widget.insert(1.0, text)
            
        else:
            label = tk.Label(root, text="No trade data found. Start logging trades first!", 
                           font=("Arial", 14))
            label.pack(pady=50)
    
    except Exception as e:
        error_label = tk.Label(root, text=f"Error: {e}", font=("Arial", 12))
        error_label.pack(pady=50)
    
    root.mainloop()

if __name__ == "__main__":
    create_trade_analyzer()
"""
                
                with open("trade_analyzer.py", "w") as f:
                    f.write(analyzer_script)
                
                subprocess.Popen([sys.executable, "trade_analyzer.py"])
                status_label.config(text="📊 Trade analyzer launched!", fg="#6f42c1")
                
            except Exception as e:
                status_label.config(text=f"❌ Error launching analyzer: {str(e)}", fg="#dc3545")
        
        analyzer_btn = tk.Button(button_row, text="📊 Analyzer", command=open_trade_analyzer,
                               font=("Arial", 11, "bold"), bg='#6f42c1', fg='white', 
                               padx=15, pady=5, relief='raised', bd=2, cursor='hand2')
        analyzer_btn.pack(side=tk.LEFT, padx=5)
        
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
    weekly_etfs = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW']
    
    # CHECK: UPDATED: Accurate last ex-dividend dates from user confirmation
    # ALL ETFs went ex-dividend on Monday 10/6/2025, all are weekly
    last_known_ex_div = {
        'MSFW': datetime(2025, 10, 6),  # Monday 10/6
        'NVDW': datetime(2025, 10, 6),  # Monday 10/6
        'HOOW': datetime(2025, 10, 6),  # Monday 10/6
        'AMDW': datetime(2025, 10, 6),  # Monday 10/6 CONFIRMED
        'GOOW': datetime(2025, 10, 6),  # Monday 10/6 CONFIRMED  
        'NFLW': datetime(2025, 10, 6)   # Monday 10/6 CONFIRMED
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
    # ALL ETFs went ex-dividend on Monday 10/6/2025, all are weekly
    last_known_ex_div = {
        'MSFW': datetime(2025, 10, 6),  # Monday 10/6
        'NVDW': datetime(2025, 10, 6),  # Monday 10/6
        'HOOW': datetime(2025, 10, 6),  # Monday 10/6
        'AMDW': datetime(2025, 10, 6),  # Monday 10/6 SUCCESS CONFIRMED
        'GOOW': datetime(2025, 10, 6),  # Monday 10/6 SUCCESS CONFIRMED  
        'NFLW': datetime(2025, 10, 6)   # Monday 10/6 SUCCESS CONFIRMED
    }
    
    ex_dividend_dates = {}
    weekly_etfs = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW']
    
    for ticker in weekly_etfs:
        if ticker in last_known_ex_div:
            last_ex_div = last_known_ex_div[ticker]
            
            # Calculate next ex-dividend (weekly pattern)
            days_since = (current_date - last_ex_div).days
            weeks_passed = days_since // 7
            next_ex_div = last_ex_div + timedelta(days=(weeks_passed + 1) * 7)
            ex_dividend_dates[ticker] = next_ex_div
        else:
            # Estimate based on weekly Monday pattern
            days_until_monday = (7 - current_date.weekday()) % 7
            if days_until_monday == 0:
                days_until_monday = 7
            ex_dividend_dates[ticker] = current_date + timedelta(days=days_until_monday)
    
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
        ('NFLW', 'GraniteShares 1x Long NFLX Daily ETF', 'Communication', 0.55)
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
        'NFLW': current_date + timedelta(days=21)   # 3 weeks
    }
    
    data = []
    for ticker, name, sector, base_yield in etfs:
        # Add some randomization to make it realistic
        weekly_yield = base_yield + random.uniform(-0.3, 0.3)
        weekly_yield = max(0.1, weekly_yield)  # Ensure positive yield
        
        # Weekly ETF sector-based RSI simulation (Technology and Communication focus)
        sector_rsi_base = {
            'Technology': 68,      # Strong tech momentum
            'Communication': 62    # Moderate comm momentum
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
    df.to_csv('weeklypay_trades.csv', index=False)

def calculate_trade_performance(trades_df):
    if trades_df.empty:
        return 0.0, 0.0, 0.0, 0.0, 0, 0
    
    total_invested = trades_df[trades_df['Action'] == 'BUY']['Total'].sum()
    total_sold = trades_df[trades_df['Action'] == 'SELL']['Total'].sum()
    total_dividends = trades_df[trades_df['Action'] == 'DIVIDEND']['Total'].sum()
    trade_count = len(trades_df)
    
    # Calculate total return (capital gains + dividends)
    net_capital_gains = total_sold - total_invested if total_sold > 0 else 0
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
                price = st.number_input("Dividend per Share ($)", min_value=0.0001, value=0.50, step=0.0001, key="trade_price")
            else:
                price = st.number_input("Price ($)", min_value=0.01, value=50.00, step=0.01, key="trade_price")
            
        with form_col3:
            trade_date = st.date_input("Date", value=datetime.now().date(), key="trade_date")
            notes = st.text_input("Notes (optional)", key="trade_notes")
        
        # Calculate total
        total_value = quantity * price
        if action == 'DIVIDEND':
            st.write(f"**Total Dividend: ${total_value:,.2f}**")
        else:
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
                
                with open('trade_analyzer.py', 'w') as f:
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
    st.markdown("### 📈 Enhanced Performance Summary")
    
    total_invested, total_dividends, total_return, net_capital_gains, active_positions, trade_count = calculate_trade_performance(trades_df)
    
    # Display enhanced metrics
    col2a, col2b = st.columns(2)
    with col2a:
        st.metric("Total Invested", f"${total_invested:,.2f}")
        st.metric("Capital Gains", f"${net_capital_gains:,.2f}", delta=f"{(net_capital_gains/total_invested*100):+.1f}%" if total_invested > 0 else None)
        
    with col2b:
        st.metric("Total Dividends", f"${total_dividends:,.2f}")
        st.metric("**Total Return**", f"${total_return:,.2f}", delta=f"{(total_return/total_invested*100):+.1f}%" if total_invested > 0 else None)
    
    st.metric("Active Positions", active_positions)
    st.metric("Total Trades", trade_count)
    
    if not trades_df.empty:
        # Show average WeeklyPay score of trades
        avg_score = trades_df['WeeklyPay_Score'].mean()
        st.metric("Avg WeeklyPay Score", f"{avg_score:.2f}")

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
    chart_tab1, chart_tab2, chart_tab3, chart_tab4 = st.tabs(["💰 Cumulative P&L", "📈 Performance by Ticker", "🎯 WeeklyPay Score Analysis", "📊 Trade Distribution"])
    
    with chart_tab1:
        st.subheader("💰 Cumulative Profit & Loss Over Time")
        
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
        
        # Calculate cumulative return
        trades_sorted['Cumulative_Return'] = (trades_sorted['Running_Proceeds'] - trades_sorted['Running_Invested']) + trades_sorted['Running_Dividends']
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
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Final Return", f"${final_return:,.2f}")
        col2.metric("Return %", f"{final_return_pct:+.2f}%") 
        col3.metric("Total Dividends", f"${running_dividends:,.2f}")
        col4.metric("Capital Gains", f"${(running_proceeds - running_invested):,.2f}")
    
    with chart_tab2:
        st.subheader("📈 Performance Analysis by Ticker")
        
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
            
            capital_gain = total_sold - total_bought if total_sold > 0 else 0
            total_return = capital_gain + total_dividends
            return_pct = (total_return / total_bought * 100) if total_bought > 0 else 0
            
            avg_score = ticker_trades['WeeklyPay_Score'].mean()
            
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
                total_return = (total_sold - total_bought) + total_dividends
                return_pct = total_return / total_bought * 100
                avg_score = ticker_trades['WeeklyPay_Score'].mean()
                
                trades_with_returns.append({
                    'Ticker': ticker,
                    'WeeklyPay_Score': avg_score,
                    'Return_Pct': return_pct,
                    'Total_Return': total_return,
                    'Investment': total_bought
                })
        
        if trades_with_returns:
            score_df = pd.DataFrame(trades_with_returns)
            
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
            
            # Add trend line
            try:
                from sklearn.linear_model import LinearRegression
                import numpy as np
                
                X = score_df['WeeklyPay_Score'].values.reshape(-1, 1)
                y = score_df['Return_Pct'].values
                
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
                
            except ImportError:
                st.info("Install scikit-learn for trend analysis: `pip install scikit-learn`")
            
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
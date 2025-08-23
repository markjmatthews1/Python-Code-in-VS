"""
Data Integrity Monitor - Creates intrusive popup alerts for data problems
ENHANCED VERSION: Includes specific error interpretation and root cause analysis
"""
import tkinter as tk
from tkinter import messagebox
import threading
import winsound
import pandas as pd
from datetime import datetime, date
import time

class DataIntegrityAlert:
    def __init__(self):
        self.alert_shown = False
        
    def interpret_data_errors(self, errors, details):
        """Interpret data errors and provide specific guidance on what's broken"""
        interpretations = []
        
        # Check for common patterns that indicate specific issues
        missing_tickers = []
        token_issues = []
        api_problems = []
        
        # Parse the details to understand what's actually wrong
        if isinstance(details, list):
            detail_text = "\n".join(details)
        else:
            detail_text = str(details)
        
        # Look for specific error patterns
        if "INSUFFICIENT TICKER DATA COVERAGE" in detail_text or "only" in detail_text.lower():
            # Extract coverage percentage if available
            coverage_match = None
            if "%" in detail_text:
                import re
                coverage_match = re.search(r'(\d+)%', detail_text)
            
            interpretations.append("🎯 ROOT CAUSE ANALYSIS:")
            interpretations.append("═" * 50)
            
            if coverage_match:
                coverage = coverage_match.group(1)
                interpretations.append(f"📊 TICKER COVERAGE: Only {coverage}% of expected tickers have current data")
            else:
                interpretations.append("📊 TICKER COVERAGE: Massive data gap detected")
            
            interpretations.append("")
            interpretations.append("🔍 MOST LIKELY CAUSE: Data Pipeline Issues")
            interpretations.append("   • Schwab API authentication is working")
            interpretations.append("   • Data retrieval or processing pipeline broken")
            interpretations.append("   • Ticker symbol mapping problems")
            interpretations.append("   • Data filtering or storage issues")
            interpretations.append("")
            
            interpretations.append("🔧 IMMEDIATE ACTIONS NEEDED:")
            interpretations.append("   1. Check data retrieval functions in schwab_data.py")
            interpretations.append("   2. Verify ticker symbols are valid (MSFU, TQQQ, etc.)")
            interpretations.append("   3. Test individual ticker data fetching")
            interpretations.append("   4. Check data filtering and CSV storage")
            interpretations.append("   5. Verify historical_data.csv update process")
            interpretations.append("")
            
            interpretations.append("⚡ QUICK FIX COMMANDS:")
            interpretations.append("   • Test: python test_schwab_auth_status.py")
            interpretations.append("   • Check: schwab_data.py ticker fetching")
            interpretations.append("   • Verify: historical_data.csv update process")
            interpretations.append("   • Debug: individual ticker data retrieval")
            interpretations.append("   • Review: data filtering and processing logic")
            interpretations.append("")
            
        # Check for specific missing tickers
        missing_count = 0
        for line in detail_text.split('\n'):
            if "❌" in line and ("rows" in line or "data" in line):
                missing_count += 1
                ticker = line.split()[1] if len(line.split()) > 1 else "Unknown"
                missing_tickers.append(ticker)
        
        if missing_tickers:
            interpretations.append(f"🚨 MISSING DATA FOR {len(missing_tickers)} TICKERS:")
            for ticker in missing_tickers[:10]:  # Show first 10
                interpretations.append(f"   • {ticker}")
            if len(missing_tickers) > 10:
                interpretations.append(f"   • ... and {len(missing_tickers) - 10} more")
            interpretations.append("")
        
        # Market timing context
        now = datetime.now()
        market_status = "UNKNOWN"
        if 9 <= now.hour < 16:  # Rough market hours
            market_status = "OPEN - DATA SHOULD BE FLOWING"
        elif now.hour < 9:
            market_status = "PRE-MARKET - LIMITED DATA EXPECTED"
        elif now.hour >= 16:
            market_status = "AFTER-HOURS - LIMITED DATA EXPECTED"
        
        interpretations.append(f"🕐 MARKET CONTEXT:")
        interpretations.append(f"   Current time: {now.strftime('%A, %B %d, %Y at %H:%M')}")
        interpretations.append(f"   Market status: {market_status}")
        interpretations.append("")
        
        # Risk assessment
        interpretations.append("⚠️ TRADING RISK ASSESSMENT:")
        if missing_count > 15:
            interpretations.append("   🔴 CRITICAL: >60% data missing - DO NOT TRADE")
            interpretations.append("   🔴 Dashboard indicators will be completely unreliable")
            interpretations.append("   🔴 Any trades based on this data could result in losses")
        elif missing_count > 5:
            interpretations.append("   🟡 WARNING: Significant data gaps - Trade with extreme caution")
            interpretations.append("   🟡 Verify all data manually before any trades")
        else:
            interpretations.append("   🟢 Minor data issues - Proceed with caution")
        
        return interpretations
        
    def play_alert_sound(self):
        """Play an intrusive alert sound - loud klaxon-like for hard of hearing"""
        try:
            # Play multiple system sounds for maximum attention
            for _ in range(3):
                # Play the loudest Windows system sound
                winsound.MessageBeep(winsound.MB_ICONHAND)  # Critical stop sound
                time.sleep(0.3)
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)  # Warning sound
                time.sleep(0.3)
            
            # Add frequency-based beeps that are easier to hear
            try:
                # Low frequency beep (easier for hearing impaired)
                winsound.Beep(400, 500)  # 400Hz for 500ms
                time.sleep(0.2)
                winsound.Beep(600, 500)  # 600Hz for 500ms
                time.sleep(0.2)
                winsound.Beep(800, 500)  # 800Hz for 500ms
                time.sleep(0.2)
                # Repeat the sequence
                winsound.Beep(400, 500)
                winsound.Beep(600, 500)
                winsound.Beep(800, 500)
            except:
                # If Beep fails, use multiple system beeps
                for _ in range(10):
                    winsound.MessageBeep(winsound.MB_ICONHAND)
                    time.sleep(0.1)
        except:
            # Fallback - multiple terminal beeps
            for _ in range(20):
                print('\a', end='', flush=True)
                time.sleep(0.1)
    
    def create_critical_alert_popup(self, title, message, details=None):
        """Create a colorful, intrusive popup that demands attention with error interpretation"""
        if self.alert_shown:
            return  # Don't show multiple popups
            
        self.alert_shown = True
        
        # Play alert sound in background
        sound_thread = threading.Thread(target=self.play_alert_sound)
        sound_thread.daemon = True
        sound_thread.start()
        
        # Create the popup window
        root = tk.Tk()
        root.title("🚨 CRITICAL DATA INTEGRITY ERROR 🚨")
        root.geometry("1200x900")  # Even larger for error interpretation
        root.configure(bg='#FF0000')  # Bright red background
        
        # Make it always on top and grab focus
        root.attributes('-topmost', True)
        root.focus_force()
        root.lift()
        
        # Flash the window
        def flash_window():
            for _ in range(10):
                root.configure(bg='#FF0000')
                root.update()
                time.sleep(0.2)
                root.configure(bg='#FFFF00')  # Yellow
                root.update()
                time.sleep(0.2)
            root.configure(bg='#FF0000')  # End on red
        
        # Start flashing in background
        flash_thread = threading.Thread(target=flash_window)
        flash_thread.daemon = True
        flash_thread.start()
        
        # Main frame
        main_frame = tk.Frame(root, bg='#FF0000', padx=20, pady=20)
        main_frame.pack(fill='both', expand=True)
        
        # Title
        title_label = tk.Label(
            main_frame, 
            text="🚨 CRITICAL TRADING DATA ERROR 🚨",
            font=('Arial', 24, 'bold'),
            fg='white',
            bg='#FF0000'
        )
        title_label.pack(pady=10)
        
        # Warning icon (using emoji)
        icon_label = tk.Label(
            main_frame,
            text="⚠️ SCHWAB API FAILURE ⚠️",
            font=('Arial', 20, 'bold'),
            fg='#FFFF00',
            bg='#FF0000'
        )
        icon_label.pack(pady=10)
        
        # Main message
        msg_label = tk.Label(
            main_frame,
            text=message,
            font=('Arial', 16, 'bold'),
            fg='white',
            bg='#FF0000',
            wraplength=700,
            justify='left'
        )
        msg_label.pack(pady=10)
        
        # Create notebook-style tabs for different information
        notebook_frame = tk.Frame(main_frame, bg='#FF0000')
        notebook_frame.pack(fill='both', expand=True, pady=10)
        
        # Tab buttons
        tab_frame = tk.Frame(notebook_frame, bg='#FF0000')
        tab_frame.pack(fill='x')
        
        # Content frame
        content_frame = tk.Frame(notebook_frame, bg='#FFFF00', relief='raised', bd=3)
        content_frame.pack(fill='both', expand=True, pady=5)
        
        # Create text widget for content
        text_widget = tk.Text(
            content_frame,
            font=('Courier', 12),  # Large font for readability
            bg='#FFFF99',
            fg='#000080',
            wrap='word',
            padx=10,
            pady=10
        )
        
        # Add scrollbar
        scrollbar = tk.Scrollbar(content_frame, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        # Pack text and scrollbar
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Function to update content
        def show_interpretation():
            text_widget.config(state='normal')  # Enable editing
            text_widget.delete('1.0', 'end')
            interpretations = self.interpret_data_errors([], details)
            content = "\n".join(interpretations)
            text_widget.insert('1.0', content)
            text_widget.config(state='disabled')  # Disable editing after update
            
            # Update button colors to show active tab
            interp_btn.config(bg='#00FF00', fg='#000000')  # Green for active
            tech_btn.config(bg='#FFE4B5', fg='#8B0000')   # Normal color
        
        def show_technical_details():
            text_widget.config(state='normal')  # Enable editing
            text_widget.delete('1.0', 'end')
            if details:
                if isinstance(details, list):
                    content = "\n".join(details)
                else:
                    content = str(details)
                text_widget.insert('1.0', content)
            text_widget.config(state='disabled')  # Disable editing after update
            
            # Update button colors to show active tab
            tech_btn.config(bg='#00FF00', fg='#000000')    # Green for active
            interp_btn.config(bg='#FFFF00', fg='#FF0000')  # Normal color
        
        # Tab buttons
        interp_btn = tk.Button(
            tab_frame,
            text="🔍 ERROR ANALYSIS & FIXES",
            font=('Arial', 12, 'bold'),
            bg='#FFFF00',
            fg='#FF0000',
            command=show_interpretation,
            relief='raised',
            bd=3
        )
        interp_btn.pack(side='left', padx=5)
        
        tech_btn = tk.Button(
            tab_frame,
            text="🔧 TECHNICAL DETAILS",
            font=('Arial', 12, 'bold'),
            bg='#FFE4B5',
            fg='#8B0000',
            command=show_technical_details,
            relief='raised',
            bd=3
        )
        tech_btn.pack(side='left', padx=5)
        
        # Start with interpretation tab
        show_interpretation()
        
        # Action required
        action_label = tk.Label(
            main_frame,
            text="⛔ DASHBOARD NOT SAFE FOR TRADING ⛔\nFIX SCHWAB API TOKENS BEFORE TRADING",
            font=('Arial', 18, 'bold'),
            fg='#FFFF00',
            bg='#FF0000'
        )
        action_label.pack(pady=20)
        
        # Buttons
        button_frame = tk.Frame(main_frame, bg='#FF0000')
        button_frame.pack(pady=20)
        
        acknowledge_btn = tk.Button(
            button_frame,
            text="I UNDERSTAND - WILL FIX SCHWAB TOKENS",
            font=('Arial', 14, 'bold'),
            bg='#FFFF00',
            fg='#FF0000',
            command=root.destroy,
            width=45,
            height=2
        )
        acknowledge_btn.pack(side='left', padx=10)
        
        exit_btn = tk.Button(
            button_frame,
            text="EXIT APPLICATION",
            font=('Arial', 14, 'bold'),
            bg='#800000',
            fg='white',
            command=lambda: (root.destroy(), exit()),
            width=20,
            height=2
        )
        exit_btn.pack(side='left', padx=10)
        
        # Keep window open
        root.mainloop()

# Global instance
alert_system = DataIntegrityAlert()

def show_data_integrity_error(errors, details=None):
    """Show intrusive popup for data integrity errors"""
    error_summary = "CRITICAL DATA INTEGRITY FAILURE DETECTED"
    if errors:
        error_summary += f"\n{len(errors)} critical errors found"
    
    alert_system.create_critical_alert_popup(
        title="🚨 Critical Data Error",
        message=error_summary,
        details=details
    )

def check_data_integrity(df, selected_tickers, ai_recommended_tickers=None):
    """
    Comprehensive data integrity check for trading dashboard
    Returns: (is_valid, errors, details)
    """
    errors = []
    details = []
    
    current_time = datetime.now()
    today = current_time.date()
    
    # Determine market status for weekend/holiday awareness
    def get_simple_market_status():
        """Simple market status check for data integrity validation"""
        import pytz
        
        # US market holidays (static for 2025)
        us_market_holidays_2025 = set([
            datetime(2025, 1, 1).date(),   # New Year's Day
            datetime(2025, 1, 20).date(),  # Martin Luther King Jr. Day
            datetime(2025, 2, 17).date(),  # Presidents' Day
            datetime(2025, 4, 18).date(),  # Good Friday
            datetime(2025, 5, 26).date(),  # Memorial Day
            datetime(2025, 6, 19).date(),  # Juneteenth
            datetime(2025, 7, 4).date(),   # Independence Day
            datetime(2025, 9, 1).date(),   # Labor Day
            datetime(2025, 11, 27).date(), # Thanksgiving
            datetime(2025, 12, 25).date(), # Christmas
        ])
        
        now = datetime.now(pytz.timezone("US/Eastern"))
        today_date = now.date()
        weekday = now.weekday()  # 0=Monday, 6=Sunday
        
        # Check if today is a weekend
        if weekday >= 5:  # Saturday or Sunday
            day_name = now.strftime('%A')
            return False, f"Market is CLOSED ({day_name})", f"Weekend - Markets closed on {day_name}"
        
        # Check if today is a holiday
        if today_date in us_market_holidays_2025:
            return False, f"Market is CLOSED (Holiday)", f"US Market Holiday - {now.strftime('%B %d, %Y')}"
        
        # Check trading hours (4 AM to 8 PM ET)
        market_open = now.replace(hour=4, minute=0, second=0, microsecond=0)
        market_close = now.replace(hour=20, minute=0, second=0, microsecond=0)
        
        if now < market_open:
            return False, f"Market is CLOSED (Pre-market)", f"Market opens at 4:00 AM ET"
        elif now > market_close:
            return False, f"Market is CLOSED (After-hours)", f"Market closed at 8:00 PM ET"
        else:
            # Market is open - determine which session
            regular_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            regular_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            if now < regular_open:
                return True, f"Market is OPEN (Pre-market)", f"Pre-market session: 4:00-9:30 AM ET"
            elif now <= regular_close:
                return True, f"Market is OPEN (Regular)", f"Regular session: 9:30 AM-4:00 PM ET"
            else:
                return True, f"Market is OPEN (After-hours)", f"After-hours session: 4:00-8:00 PM ET"
    
    market_is_open, market_status, market_explanation = get_simple_market_status()
    
    details.append(f"🔍 DATA INTEGRITY CHECK - {current_time.strftime('%Y-%m-%d %H:%M:%S')}")
    details.append("=" * 70)
    details.append("")
    details.append(f"📊 Market Status: {market_status}")
    details.append(f"   {market_explanation}")
    details.append("")
    
    # Check if DataFrame is empty
    if df.empty:
        errors.append("EMPTY_DATAFRAME")
        details.append("❌ CRITICAL: Historical data DataFrame is completely empty!")
        details.append("   This indicates complete failure of data retrieval system")
        details.append("   All trading indicators will fail")
        details.append("")
        return False, errors, details
    
    # Parse datetime column properly
    try:
        df['Datetime'] = pd.to_datetime(df['Datetime'], format='mixed')
        df['Date'] = df['Datetime'].dt.date
        
        # Check for today's data with safe date comparison
        today_data = df[df['Date'] == today]
    except Exception as e:
        errors.append("DATETIME_PARSE_ERROR")
        details.append(f"❌ Cannot parse datetime column: {str(e)}")
        details.append(f"❌ Error at line 398-405 in data_integrity_monitor.py")
        details.append("")
        # Use empty DataFrame as fallback
        today_data = pd.DataFrame()
    
    details.append(f"📅 Today's date: {today}")
    details.append(f"📊 Today's data rows: {len(today_data)}")
    
    if not market_is_open:
        details.append(f"ℹ️  Note: No today's data expected since markets are closed")
    
    details.append("")
    
    # Check each ticker's data availability
    details.append("🎯 TICKER DATA COVERAGE ANALYSIS:")
    details.append("-" * 50)
    
    valid_tickers = 0
    total_tickers = len(selected_tickers)
    
    for ticker in selected_tickers:
        ticker_data = df[df['Ticker'] == ticker]
        ticker_today = today_data[today_data['Ticker'] == ticker]
        
        # Check data quality
        has_data = len(ticker_data) > 0
        has_today_data = len(ticker_today) > 0
        has_recent_data = False
        
        if has_data:
            try:
                latest_date = ticker_data['Date'].max()
                if pd.isna(latest_date):
                    raise ValueError("Latest date is NaN")
                days_old = (today - latest_date).days
                # If market is closed, consider yesterday's data as "current"
                has_recent_data = days_old <= (2 if not market_is_open else 1)
            except (TypeError, ValueError) as date_error:
                details.append(f"⚠️ {ticker}: Date comparison error at line 428: {date_error}")
                has_recent_data = False
                latest_date = "ERROR"
        
        # Determine ticker status based on market status
        if market_is_open:
            # Market is open - expect today's data
            if has_today_data and len(ticker_today) >= 10:
                details.append(f"✅ {ticker}: {len(ticker_today)} rows today (GOOD)")
                valid_tickers += 1
            elif has_recent_data:
                details.append(f"⚠️ {ticker}: No today data, but recent data available")
            else:
                details.append(f"❌ {ticker}: No current data (latest: {latest_date if has_data else 'NONE'})")
        else:
            # Market is closed - don't expect today's data, recent data is fine
            if has_recent_data:
                latest_date_str = ticker_data['Date'].max().strftime('%Y-%m-%d') if has_data else 'NONE'
                details.append(f"✅ {ticker}: Recent data available through {latest_date_str} (NORMAL for {market_status.split()[3] if len(market_status.split()) > 3 else 'closed market'})")
                valid_tickers += 1
            else:
                details.append(f"❌ {ticker}: No recent data (latest: {latest_date if has_data else 'NONE'})")
    
    details.append("")
    
    # Calculate coverage percentage
    coverage_percent = (valid_tickers / total_tickers) * 100 if total_tickers > 0 else 0
    details.append(f"📊 TICKER COVERAGE SUMMARY:")
    details.append(f"   Valid tickers: {valid_tickers} / {total_tickers}")
    details.append(f"   Coverage percentage: {coverage_percent:.1f}%")
    details.append(f"   Market status: {market_status}")
    details.append("")
    
    # Determine if coverage is sufficient (more lenient when markets are closed)
    required_coverage = 60 if not market_is_open else 80  # Lower threshold for closed markets
    
    if coverage_percent < required_coverage:
        errors.append("INSUFFICIENT_TICKER_DATA_COVERAGE")
        
        if market_is_open:
            details.append("🚨 CRITICAL: Insufficient ticker data coverage during market hours!")
            details.append(f"   Expected: >{required_coverage}% coverage for reliable trading")
            details.append(f"   Actual: {coverage_percent:.1f}% coverage")
            details.append("   This indicates systematic failure of real-time data retrieval")
            details.append("")
            details.append("🔧 IMMEDIATE ACTIONS REQUIRED:")
            details.append("   • Check Schwab API authentication")
            details.append("   • Verify access tokens are not expired")
            details.append("   • Test network connectivity to Schwab servers")
            details.append("   • Check for API rate limiting")
        else:
            details.append("⚠️ NOTICE: Low data coverage detected during market closure")
            details.append(f"   Expected: >{required_coverage}% coverage (reduced for {market_status})")
            details.append(f"   Actual: {coverage_percent:.1f}% coverage")
            details.append(f"   {market_explanation}")
            details.append("")
            details.append("🔧 RECOMMENDED ACTIONS:")
            details.append("   • This may be normal for weekend/holiday periods")
            details.append("   • Verify historical data is updating properly")
            details.append("   • Data should improve when markets reopen")
        details.append("")
    
    # Check for required columns
    required_columns = ['Datetime', 'Ticker', 'Open', 'High', 'Low', 'Close', 'Volume']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        errors.append("MISSING_REQUIRED_COLUMNS")
        details.append(f"❌ Missing required columns: {missing_columns}")
        details.append("")
    
    # Check for data quality issues
    if not df.empty:
        null_counts = df[required_columns].isnull().sum()
        for col, null_count in null_counts.items():
            if null_count > len(df) * 0.1:  # More than 10% nulls
                errors.append(f"HIGH_NULL_COUNT_{col}")
                details.append(f"⚠️ High null count in {col}: {null_count} nulls ({null_count/len(df)*100:.1f}%)")
    
    # Final assessment
    is_valid = len(errors) == 0
    
    if not is_valid:
        details.append("")
        details.append("🚨 FINAL ASSESSMENT: DATA NOT SUITABLE FOR TRADING")
        details.append("   Dashboard indicators may be inaccurate or missing")
        details.append("   Trading decisions based on this data could result in losses")
        details.append("   IMMEDIATE ACTION REQUIRED TO FIX DATA SOURCES")
    else:
        details.append("")
        details.append("✅ DATA INTEGRITY CHECK PASSED")
        details.append("   All systems appear to be functioning normally")
    
    return is_valid, errors, details

def test_data_integrity():
    """Test function to demonstrate the data integrity system"""
    print("🧪 Testing Data Integrity Monitor...")
    
    # Create test data with problems
    test_df = pd.DataFrame({
        'Datetime': ['2025-08-06 09:30', '2025-08-06 09:31'] * 3,
        'Ticker': ['AAPL', 'AAPL', 'MSFT', 'MSFT', 'GOOGL', 'GOOGL'],
        'Open': [150.0, 150.5, 300.0, 300.5, 2800.0, 2805.0],
        'High': [151.0, 151.5, 301.0, 301.5, 2810.0, 2815.0],
        'Low': [149.5, 150.0, 299.5, 300.0, 2795.0, 2800.0],
        'Close': [150.5, 151.0, 300.5, 301.0, 2805.0, 2810.0],
        'Volume': [1000, 1100, 2000, 2100, 500, 550]
    })
    
    # Test with many missing tickers to trigger errors
    test_tickers = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMD', 'INTC', 'CRM', 'ORCL', 'IBM',
                   'MSFU', 'TQQQ', 'BOIL', 'NAIL', 'LABU', 'TECL', 'SSO', 'AGQ', 'BITU', 'CWEB']
    
    is_valid, errors, details = check_data_integrity(test_df, test_tickers)
    
    if not is_valid:
        show_data_integrity_error(errors, details)
    else:
        print("✅ Test passed - no errors detected")

if __name__ == "__main__":
    test_data_integrity()

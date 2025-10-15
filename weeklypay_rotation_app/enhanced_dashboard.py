"""
WeeklyPay™ Enhanced Dashboard with Manual Data Entry Integration
Combines automated API data with manual override capability for maximum reliability
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import requests
import math
import os
import sys

# Add the current directory to path for importing our modules
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Page configuration
st.set_page_config(
    page_title="WeeklyPay™ Enhanced Dashboard",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Import our enhanced earnings calendar
try:
    from comprehensive_earnings_calendar import WeeklyPayEarningsCalendar
    ENHANCED_CALENDAR_AVAILABLE = True
except ImportError:
    ENHANCED_CALENDAR_AVAILABLE = False
    st.warning("Enhanced calendar not available, using basic API calls")

# WeeklyPay™ Scoring Formula
def weeklypay_scoring_formula(weekly_yield, rsi, days_to_earnings):
    """WeeklyPay™ Tactical Rotation Scoring Formula"""
    yield_score = min((weekly_yield / 1.0) * 10, 10)
    
    if rsi >= 70:
        momentum_score = 10
    elif rsi >= 60:
        momentum_score = 8
    elif rsi >= 50:
        momentum_score = 6
    elif rsi >= 40:
        momentum_score = 4
    else:
        momentum_score = 2
    
    if days_to_earnings <= 7:
        earnings_score = 10
    elif days_to_earnings <= 14:
        earnings_score = 8
    elif days_to_earnings <= 21:
        earnings_score = 6
    elif days_to_earnings <= 30:
        earnings_score = 4
    else:
        earnings_score = 2
    
    final_score = (yield_score * 0.5) + (momentum_score * 0.3) + (earnings_score * 0.2)
    return final_score, yield_score, momentum_score, earnings_score

# Manual Data Entry Controls
def show_manual_data_controls():
    """Show manual data entry controls in sidebar"""
    st.sidebar.header("📝 Manual Data Entry")
    
    # Check if manual data file exists
    manual_data_file = "manual_earnings_data.json"
    manual_data_exists = os.path.exists(manual_data_file)
    
    if manual_data_exists:
        import json
        try:
            with open(manual_data_file, 'r') as f:
                manual_data = json.load(f)
            
            if manual_data:
                st.sidebar.success(f"📋 Manual entries: {len(manual_data)}")
                
                # Show current manual entries
                st.sidebar.subheader("Current Manual Entries")
                for etf, data in manual_data.items():
                    entry_date = data.get('earnings_date', 'Unknown')
                    days_away = (datetime.strptime(entry_date, '%Y-%m-%d') - datetime.now()).days if entry_date != 'Unknown' else 'N/A'
                    st.sidebar.text(f"{etf}: {entry_date} ({days_away} days)")
            else:
                st.sidebar.info("📋 No manual entries")
        except Exception as e:
            st.sidebar.error(f"Error reading manual data: {e}")
    else:
        st.sidebar.info("📋 No manual data file found")
    
    # Button to open manual data entry GUI
    if st.sidebar.button("🔧 Open Manual Data Entry", key="manual_data_btn"):
        try:
            import subprocess
            import sys
            
            # Launch the manual data entry GUI
            script_path = os.path.join(current_dir, "manual_data_entry_gui.py")
            subprocess.Popen([sys.executable, script_path])
            st.sidebar.success("✅ Manual data entry GUI launched!")
            st.sidebar.info("💡 Use the GUI to enter earnings dates, then refresh this dashboard")
        except Exception as e:
            st.sidebar.error(f"❌ Failed to launch GUI: {e}")
    
    # Refresh button
    if st.sidebar.button("🔄 Refresh Data", key="refresh_btn"):
        st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("**💡 Manual Entry Tips:**")
    st.sidebar.markdown("• Use YYYY-MM-DD format")
    st.sidebar.markdown("• Manual entries override API data")
    st.sidebar.markdown("• Entries persist until deleted")

# Enhanced Earnings Calendar Function
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_enhanced_earnings_calendar_data():
    """Get earnings calendar with manual data integration"""
    if ENHANCED_CALENDAR_AVAILABLE:
        try:
            calendar_system = WeeklyPayEarningsCalendar()
            # Get data without manual prompting (since we're in Streamlit)
            calendar, sources = calendar_system.get_comprehensive_earnings_calendar(prompt_for_manual=False)
            return calendar, sources
        except Exception as e:
            st.error(f"Error with enhanced calendar: {e}")
            return {}, {}
    else:
        # Fallback to basic earnings lookup
        return get_basic_earnings_calendar()

def get_basic_earnings_calendar():
    """Basic earnings calendar fallback"""
    import yfinance as yf
    
    underlying_stocks = {
        'NVDW': 'NVDA',
        'AMDW': 'AMD', 
        'HOOW': 'HOOD',
        'MSFW': 'MSFT',
        'GOOW': 'GOOGL',
        'NFLW': 'NFLX'
    }
    
    earnings_calendar = {}
    sources = {}
    current_date = datetime.now()
    
    for etf_ticker, stock_ticker in underlying_stocks.items():
        try:
            ticker = yf.Ticker(stock_ticker)
            info = ticker.info
            
            # Try to get earnings date
            earnings_date_key = None
            for key in ['nextEarningsDate', 'earningsDate', 'nextEarningsAnnouncement']:
                if key in info and info[key]:
                    earnings_date_key = key
                    break
            
            if earnings_date_key:
                earnings_date_str = info[earnings_date_key]
                if isinstance(earnings_date_str, str):
                    try:
                        earnings_date = datetime.strptime(earnings_date_str, '%Y-%m-%d')
                    except ValueError:
                        try:
                            earnings_date = datetime.strptime(earnings_date_str, '%m/%d/%Y')
                        except ValueError:
                            continue
                else:
                    # Assume it's a timestamp
                    earnings_date = datetime.fromtimestamp(earnings_date_str)
                
                if earnings_date.date() >= current_date.date():
                    earnings_calendar[etf_ticker] = earnings_date
                    sources[etf_ticker] = "yfinance_basic"
        except Exception as e:
            # Use fallback estimate
            fallback_days = {'NVDW': 14, 'AMDW': 21, 'HOOW': 29, 'MSFW': 35, 'GOOW': 42, 'NFLW': 49}
            days_away = fallback_days.get(etf_ticker, 30)
            estimated_date = current_date + timedelta(days=days_away)
            earnings_calendar[etf_ticker] = estimated_date
            sources[etf_ticker] = "fallback_estimate"
    
    return earnings_calendar, sources

# Mock data generation for demonstration
def generate_mock_data():
    """Generate mock data for the WeeklyPay ETFs"""
    earnings_calendar, sources = get_enhanced_earnings_calendar_data()
    current_date = datetime.now()
    
    etfs = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW']
    data = []
    
    for etf in etfs:
        # Get earnings date and calculate days away
        earnings_date = earnings_calendar.get(etf, current_date + timedelta(days=30))
        days_to_earnings = (earnings_date - current_date).days
        source = sources.get(etf, "unknown")
        
        # Generate mock price and dividend data
        base_price = {"NVDW": 45, "AMDW": 35, "HOOW": 25, "MSFW": 55, "GOOW": 40, "NFLW": 30}[etf]
        
        # Mock live data
        current_price = base_price + (hash(etf + str(current_date.hour)) % 10 - 5) * 0.1
        weekly_dividend = base_price * 0.006 + (hash(etf) % 5) * 0.001
        weekly_yield = (weekly_dividend / current_price) * 100
        rsi = 45 + (hash(etf) % 30)
        
        # Calculate WeeklyPay score
        score, yield_score, momentum_score, earnings_score = weeklypay_scoring_formula(
            weekly_yield, rsi, days_to_earnings
        )
        
        data.append({
            'ETF': etf,
            'Current Price': f"${current_price:.2f}",
            'Weekly Dividend': f"${weekly_dividend:.3f}",
            'Weekly Yield %': f"{weekly_yield:.2f}%",
            'RSI': rsi,
            'Days to Earnings': days_to_earnings,
            'Earnings Date': earnings_date.strftime('%Y-%m-%d'),
            'Data Source': source,
            'WeeklyPay Score': f"{score:.1f}",
            'Yield Score': f"{yield_score:.1f}",
            'Momentum Score': f"{momentum_score:.1f}",
            'Earnings Score': f"{earnings_score:.1f}",
            '_score_numeric': score,
            '_yield_numeric': weekly_yield,
            '_days_numeric': days_to_earnings
        })
    
    return pd.DataFrame(data)

# Main dashboard
def main():
    # Header
    st.title("💰 WeeklyPay™ Enhanced Tactical Rotation Engine")
    st.markdown("**Real-time ETF analysis with manual data entry capability**")
    
    # Show manual data controls in sidebar
    show_manual_data_controls()
    
    # Data source indicator
    if ENHANCED_CALENDAR_AVAILABLE:
        st.success("🚀 Enhanced earnings calendar active (API + Manual data integration)")
    else:
        st.warning("⚠️ Using basic earnings calendar (Enhanced calendar unavailable)")
    
    # Get and display data
    df = generate_mock_data()
    
    # Sort by WeeklyPay Score (descending)
    df_sorted = df.sort_values('_score_numeric', ascending=False)
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        top_etf = df_sorted.iloc[0]
        st.metric(
            "🏆 Top Performer",
            top_etf['ETF'],
            f"Score: {top_etf['WeeklyPay Score']}"
        )
    
    with col2:
        avg_yield = df['_yield_numeric'].mean()
        st.metric(
            "📊 Avg Weekly Yield",
            f"{avg_yield:.2f}%",
            f"Best: {df['_yield_numeric'].max():.2f}%"
        )
    
    with col3:
        nearest_earnings = df['_days_numeric'].min()
        nearest_etf = df[df['_days_numeric'] == nearest_earnings]['ETF'].iloc[0]
        st.metric(
            "📅 Next Earnings",
            f"{nearest_etf}",
            f"in {nearest_earnings} days"
        )
    
    with col4:
        manual_count = len([s for s in df['Data Source'] if 'manual' in s.lower()])
        st.metric(
            "🔧 Manual Entries",
            manual_count,
            f"of {len(df)} ETFs"
        )
    
    # Main data table
    st.header("📈 WeeklyPay ETF Rankings")
    
    # Display the dataframe with better formatting
    display_df = df_sorted[['ETF', 'Current Price', 'Weekly Yield %', 'RSI', 
                           'Days to Earnings', 'Earnings Date', 'Data Source', 'WeeklyPay Score']].copy()
    
    # Color-code the scores
    def highlight_scores(val):
        if isinstance(val, str) and val.replace('.', '').replace('-', '').isdigit():
            score = float(val)
            if score >= 8:
                return 'background-color: #90EE90'  # Light green
            elif score >= 6:
                return 'background-color: #FFFFE0'  # Light yellow
            else:
                return 'background-color: #FFB6C1'  # Light red
        return ''
    
    styled_df = display_df.style.applymap(highlight_scores, subset=['WeeklyPay Score'])
    st.dataframe(styled_df, use_container_width=True)
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 WeeklyPay Scores")
        fig_scores = px.bar(
            df_sorted,
            x='ETF',
            y='_score_numeric',
            title="WeeklyPay™ Tactical Scores",
            color='_score_numeric',
            color_continuous_scale='RdYlGn'
        )
        fig_scores.update_layout(showlegend=False)
        st.plotly_chart(fig_scores, use_container_width=True)
    
    with col2:
        st.subheader("📅 Earnings Timeline")
        fig_earnings = px.scatter(
            df,
            x='_days_numeric',
            y='_yield_numeric',
            size='_score_numeric',
            color='ETF',
            title="Yield vs Days to Earnings",
            labels={'_days_numeric': 'Days to Earnings', '_yield_numeric': 'Weekly Yield %'}
        )
        st.plotly_chart(fig_earnings, use_container_width=True)
    
    # Data source breakdown
    st.header("📋 Data Source Analysis")
    
    source_counts = df['Data Source'].value_counts()
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig_sources = px.pie(
            values=source_counts.values,
            names=source_counts.index,
            title="Earnings Data Sources"
        )
        st.plotly_chart(fig_sources, use_container_width=True)
    
    with col2:
        st.subheader("Source Details")
        for source, count in source_counts.items():
            emoji = "🔧" if "manual" in source.lower() else "🤖" if "api" in source.lower() else "📊"
            st.write(f"{emoji} **{source}**: {count} ETFs")
    
    # Instructions
    st.header("💡 How to Use Manual Data Entry")
    
    with st.expander("Click to see instructions"):
        st.markdown("""
        **When to use manual data entry:**
        - API data is outdated or incorrect
        - Earnings dates have been announced but not reflected in APIs
        - You have insider knowledge of schedule changes
        - APIs are experiencing downtime
        
        **How to enter manual data:**
        1. Click "🔧 Open Manual Data Entry" in the sidebar
        2. Select the ETF you want to update
        3. Enter the earnings date in YYYY-MM-DD format (e.g., 2025-11-15)
        4. Use quick date buttons for common timeframes
        5. Click "Save Entry" to store the data
        6. Return to this dashboard and click "🔄 Refresh Data"
        
        **Data priority:**
        1. Manual entries (highest priority)
        2. Cached API data (if recent)
        3. Fresh API data
        4. Fallback estimates (lowest priority)
        
        **Tips:**
        - Manual entries persist until you delete them
        - Always verify earnings dates from official company sources
        - Manual data overrides all API sources
        - Use the GUI to easily manage multiple entries
        """)

if __name__ == "__main__":
    main()
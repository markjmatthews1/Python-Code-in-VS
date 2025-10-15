"""
WeeklyPay™ Tactical Rotation Engine
Enhanced GUI Dashboard based on Aristo's design recommendations
Focus: ETF Rotation Panel & Sector Momentum Panel
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import json
import sys
from pathlib import Path

# Add src directory to path
sys.path.append(str(Path(__file__).parent / "src"))

from src.etf_tracker import ETFTracker
from src.signal_engine import RotationRulesEngine
from src.data_collector import DataCollector

# Page configuration
st.set_page_config(
    page_title="WeeklyPay™ Tactical Rotation Engine",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS styling for Aristo's design layout
st.markdown("""
<style>
    /* Main app header styling */
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
    
    /* Week display styling */
    .week-display {
        font-size: 1.5rem;
        color: #7f8c8d;
        text-align: center;
        margin-bottom: 0.5rem;
        font-family: Arial, sans-serif;
    }
    
    /* Data refresh timestamp */
    .refresh-timestamp {
        font-size: 1rem;
        color: #95a5a6;
        text-align: center;
        margin-bottom: 2rem;
        font-family: Arial, sans-serif;
    }
    
    /* ETF Rotation table styling */
    .rotation-table {
        font-family: Arial, sans-serif;
        width: 100%;
        border-collapse: collapse;
        margin: 1rem 0;
    }
    
    .rotation-table th {
        background-color: #34495e;
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: bold;
    }
    
    .rotation-table td {
        padding: 10px;
        border-bottom: 1px solid #ecf0f1;
    }
    
    /* Color-coded row styling */
    .rotate-in-row {
        background-color: #d5f4e6;
        color: #27ae60;
        border-left: 5px solid #27ae60;
    }
    
    .rotate-out-row {
        background-color: #fadbd8;
        color: #e74c3c;
        border-left: 5px solid #e74c3c;
    }
    
    .hold-row {
        background-color: #f8f9fa;
        color: #7f8c8d;
        border-left: 5px solid #95a5a6;
    }
    
    /* Sector momentum cards */
    .sector-card {
        background-color: #ffffff;
        border: 1px solid #bdc3c7;
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        font-family: Arial, sans-serif;
    }
    
    .sector-bullish {
        color: #27ae60;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .sector-bearish {
        color: #e74c3c;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .sector-neutral {
        color: #f39c12;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    /* Panel headers */
    .panel-header {
        font-size: 1.8rem;
        color: #2c3e50;
        font-family: Arial, sans-serif;
        font-weight: bold;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #3498db;
    }
    
    /* Mini-chart containers */
    .mini-chart-container {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 6px;
        padding: 10px;
        margin: 5px 0;
        font-family: Arial, sans-serif;
    }
    
    /* Alert and notes styling */
    .alert-box {
        background-color: #fff3cd;
        color: #856404;
        padding: 15px;
        border-radius: 6px;
        border-left: 4px solid #ffc107;
        margin: 10px 0;
        font-family: Arial, sans-serif;
        font-size: 1.1rem;
    }
    
    /* Earnings this week highlight */
    .earnings-highlight {
        background-color: #fef9e7;
        color: #8c6d1f;
        padding: 8px;
        border-radius: 4px;
        border-left: 3px solid #f1c40f;
        margin: 5px 0;
        font-family: Arial, sans-serif;
    }
    
    /* High yield highlight */
    .high-yield {
        background-color: #e8f5e8;
        color: #2e8b57;
        padding: 6px 10px;
        border-radius: 4px;
        font-family: Arial, sans-serif;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_system_data():
    """Load and cache system data"""
    try:
        # Initialize system components
        tracker = ETFTracker("data/etf_list.json")
        engine = RotationRulesEngine(tracker)
        data_collector = DataCollector(tracker)
        data_collector.set_signal_engine(engine)
        
        # Collect all data
        with st.spinner("🔄 Collecting real-time market data..."):
            results = data_collector.collect_all_data()
        
        # Integrate weekly payouts with signal engine
        engine.integrate_weekly_payouts(data_collector.weekly_payouts)
        
        # Add some sample earnings for demo
        engine.add_earnings_event("AMD", "2025-10-08")
        engine.add_earnings_event("META", "2025-09-30")
        engine.add_earnings_event("NFLX", "2025-10-09")
        engine.add_earnings_event("NVDA", "2025-10-07")
        
        # Generate rotation signals
        signals = engine.generate_rotation_signals()
        
        # Generate alert format
        alert = engine.generate_alert_format(data_collector.weekly_payouts)
        
        return {
            'tracker': tracker,
            'engine': engine,
            'data_collector': data_collector,
            'signals': signals,
            'alert': alert,
            'results': results
        }
    except Exception as e:
        st.error(f"Error loading system data: {e}")
        return None

def display_header():
    """Display the enhanced header section based on Aristo's design"""
    # App name and branding
    st.markdown('<h1 class="main-header">� WeeklyPay™ Tactical Rotation Engine</h1>', unsafe_allow_html=True)
    
    # Current week calculation
    today = datetime.now()
    week_start = today - timedelta(days=today.weekday())
    week_end = week_start + timedelta(days=4)  # Friday
    current_week = f"{week_start.strftime('%b %d')}–{week_end.strftime('%d')}"
    
    st.markdown(f'<div class="week-display">📅 Current Week: {current_week}</div>', unsafe_allow_html=True)
    
    # Last data refresh timestamp
    refresh_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f'<div class="refresh-timestamp">⏰ Last Refresh: {refresh_time}</div>', unsafe_allow_html=True)
    
    return current_week

def display_etf_rotation_panel(data):
    """Display the ETF Rotation Panel with color-coded table"""
    st.markdown('<h2 class="panel-header">📊 ETF Rotation Panel</h2>', unsafe_allow_html=True)
    
    if not data:
        st.error("Unable to load rotation data")
        return
    
    signals = data['signals']
    tracker = data['tracker']
    weekly_payouts = data['data_collector'].weekly_payouts
    
    # Create rotation recommendations table data
    rotation_data = []
    
    # Process ROTATE IN signals
    for symbol in signals['rotate_in']:
        etf_data = tracker.get_etf_metadata(symbol)
        underlying = etf_data.underlying_ticker if etf_data else "N/A"
        
        # Get payout info
        payout_info = "N/A"
        yield_text = ""
        if symbol in weekly_payouts.payout_data:
            payout = weekly_payouts.payout_data[symbol]
            payout_info = f"{payout.payout_percentage:.2f}%"
            if payout.payout_percentage > 3.0:
                yield_text = "🔥 High Yield"
        
        rotation_data.append({
            'ETF': symbol,
            'Underlying': underlying,
            'Action': 'ROTATE IN',
            'Weekly Yield': payout_info,
            'Signal': 'Buy Signal Active',
            'Notes': yield_text,
            'Status': 'rotate_in'
        })
    
    # Process ROTATE OUT signals
    for symbol in signals['rotate_out']:
        etf_data = tracker.get_etf_metadata(symbol)
        underlying = etf_data.underlying_ticker if etf_data else "N/A"
        
        rotation_data.append({
            'ETF': symbol,
            'Underlying': underlying,
            'Action': 'ROTATE OUT',
            'Weekly Yield': 'N/A',
            'Signal': 'Sell Signal Active',
            'Notes': 'Exit Position',
            'Status': 'rotate_out'
        })
    
    # Add some HOLD positions for demo
    all_etfs = ['NVDW', 'AMDW', 'HOOW', 'MSFW', 'GOOW', 'NFLW']
    hold_etfs = [etf for etf in all_etfs if etf not in signals['rotate_in'] and etf not in signals['rotate_out']]
    
    for symbol in hold_etfs[:2]:  # Show 2 hold positions
        etf_data = tracker.get_etf_metadata(symbol)
        underlying = etf_data.underlying_ticker if etf_data else "N/A"
        
        rotation_data.append({
            'ETF': symbol,
            'Underlying': underlying,
            'Action': 'HOLD',
            'Weekly Yield': 'N/A',
            'Signal': 'No Change',
            'Notes': 'Monitor',
            'Status': 'hold'
        })
    
    # Create the rotation table with color coding
    if rotation_data:
        df = pd.DataFrame(rotation_data)
        
        # Color-code the dataframe display
        def color_rows(row):
            if row['Status'] == 'rotate_in':
                return ['background-color: #d5f4e6; color: #27ae60; border-left: 5px solid #27ae60'] * len(row)
            elif row['Status'] == 'rotate_out':
                return ['background-color: #fadbd8; color: #e74c3c; border-left: 5px solid #e74c3c'] * len(row)
            else:  # hold
                return ['background-color: #f8f9fa; color: #7f8c8d; border-left: 5px solid #95a5a6'] * len(row)
        
        # Display the styled table
        styled_df = df.drop('Status', axis=1).style.apply(color_rows, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
        
        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🟢 Rotate In", len(signals['rotate_in']))
        with col2:
            st.metric("🔴 Rotate Out", len(signals['rotate_out']))
        with col3:
            st.metric("⚪ Hold", len(hold_etfs[:2]))
        with col4:
            total_signals = len(signals['rotate_in']) + len(signals['rotate_out'])
            st.metric("📈 Active Signals", total_signals)
    else:
        st.info("No rotation signals available at this time")

def display_sector_momentum_panel(data):
    """Display Sector Momentum Panel with mini-charts"""
    st.markdown('<h2 class="panel-header">📈 Sector Momentum Panel</h2>', unsafe_allow_html=True)
    
    if not data or not data['data_collector'].sector_momentum.momentum_data:
        st.warning("No sector momentum data available")
        return
    
    momentum_data = data['data_collector'].sector_momentum.momentum_data
    
    # Display mini-charts for SMH, XLK, XLC
    target_sectors = ['SMH', 'XLK', 'XLC']
    cols = st.columns(3)
    
    for i, sector in enumerate(target_sectors):
        with cols[i]:
            if sector in momentum_data:
                momentum = momentum_data[sector]
                
                # Determine signal color and text
                if momentum.momentum_signal == "BULLISH":
                    signal_class = "sector-bullish"
                    signal_icon = "🟢"
                elif momentum.momentum_signal == "BEARISH":
                    signal_class = "sector-bearish" 
                    signal_icon = "🔴"
                else:
                    signal_class = "sector-neutral"
                    signal_icon = "🟡"
                
                # Create mini-chart card
                st.markdown(f"""
                <div class="sector-card">
                    <h3>{sector} {signal_icon}</h3>
                    <div class="{signal_class}">{momentum.momentum_signal}</div>
                    <p><strong>RSI:</strong> {momentum.rsi_14:.1f}</p>
                    <p><strong>Price:</strong> ${momentum.price:.2f}</p>
                    <p><strong>Confidence:</strong> {momentum.confidence:.1%}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Create sparkline chart (simplified)
                chart_data = pd.DataFrame({
                    'Day': range(1, 21),
                    'Price': [momentum.price * (1 + (i-10)*0.01) for i in range(20)]
                })
                
                fig = px.line(chart_data, x='Day', y='Price', 
                            title=f"{sector} 20-Day Trend")
                fig.update_layout(height=200, showlegend=False, 
                                margin=dict(l=0, r=0, t=30, b=0))
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.markdown(f"""
                <div class="sector-card">
                    <h3>{sector}</h3>
                    <p>No data available</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Overall sector momentum summary
    st.markdown("### 📊 Sector Momentum Summary")
    
    sector_summary = []
    for sector, momentum in momentum_data.items():
        sector_summary.append({
            'Sector': sector,
            'Signal': momentum.momentum_signal,
            'RSI': f"{momentum.rsi_14:.1f}",
            'Price': f"${momentum.price:.2f}",
            'Confidence': f"{momentum.confidence:.1%}",
            'Trend': "↗️" if momentum.momentum_signal == "BULLISH" else "↘️" if momentum.momentum_signal == "BEARISH" else "→"
        })
    
    if sector_summary:
        summary_df = pd.DataFrame(sector_summary)
        st.dataframe(summary_df, use_container_width=True, hide_index=True)

def display_alerts_and_notes_panel(data):
    """Display Alerts & Notes Panel with actionable insights"""
    st.markdown('<h2 class="panel-header">� Alerts & Notes Panel</h2>', unsafe_allow_html=True)
    
    if not data:
        return
    
    alert = data['alert']
    signals = data['signals']
    
    # Display key insights and alerts
    st.markdown("### 📋 This Week's Key Insights:")
    
    for note in alert['notes']:
        st.markdown(f"""
        <div class="alert-box">
            🔔 {note}
        </div>
        """, unsafe_allow_html=True)
    
    # Add some dynamic alerts based on current signals
    if signals['rotate_in']:
        for symbol in signals['rotate_in']:
            st.markdown(f"""
            <div class="alert-box">
                🟢 <strong>{symbol}</strong> showing strong rotation signal - consider entry this week
            </div>
            """, unsafe_allow_html=True)
    
    if signals['rotate_out']:
        for symbol in signals['rotate_out']:
            st.markdown(f"""
            <div class="alert-box">
                🔴 <strong>{symbol}</strong> momentum weakening - consider exit strategy
            </div>
            """, unsafe_allow_html=True)
    
    # Weekly strategy summary
    st.markdown("### 📈 Weekly Strategy Summary:")
    
    total_rotate_in = len(signals['rotate_in'])
    total_rotate_out = len(signals['rotate_out'])
    
    if total_rotate_in > total_rotate_out:
        strategy_text = f"🟢 <strong>Bullish Week:</strong> {total_rotate_in} rotation IN signals vs {total_rotate_out} OUT signals"
        strategy_class = "sector-bullish"
    elif total_rotate_out > total_rotate_in:
        strategy_text = f"🔴 <strong>Bearish Week:</strong> {total_rotate_out} rotation OUT signals vs {total_rotate_in} IN signals"
        strategy_class = "sector-bearish"
    else:
        strategy_text = f"🟡 <strong>Neutral Week:</strong> Balanced rotation signals - selective approach recommended"
        strategy_class = "sector-neutral"
    
    st.markdown(f"""
    <div class="alert-box">
        <span class="{strategy_class}">{strategy_text}</span>
    </div>
    """, unsafe_allow_html=True)

def display_sector_momentum(data):
    """Legacy sector momentum display for compatibility"""
    return display_sector_momentum_panel(data)

def display_earnings_calendar(data):
    """Display earnings calendar"""
    st.markdown("## 📅 Earnings Calendar")
    
    # Get earnings events
    earnings_events = data['engine'].earnings_calendar
    
    if not earnings_events:
        st.info("No earnings events currently tracked")
        return
    
    # Group by timing
    this_week = [e for e in earnings_events if e.is_this_week]
    next_week = [e for e in earnings_events if not e.is_this_week and not e.is_post_earnings]
    post_earnings = [e for e in earnings_events if e.is_post_earnings]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 🟢 This Week")
        for event in this_week:
            # Map to ETF
            etf_symbol = "Unknown"
            for etf in data['tracker'].get_etf_list():
                etf_data = data['tracker'].get_etf_metadata(etf)
                if etf_data and etf_data.underlying_ticker == event.symbol:
                    etf_symbol = etf
                    break
            
            st.markdown(f"""
            <div class="earnings-this-week">
                <strong>{event.symbol}</strong> → {etf_symbol}<br>
                📅 {event.earnings_date}
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 🟡 Future")
        for event in next_week:
            st.write(f"📊 {event.symbol}: {event.earnings_date}")
    
    with col3:
        st.markdown("### 🔴 Post-Earnings")
        for event in post_earnings:
            days_ago = abs(event.days_until_earnings)
            st.write(f"📉 {event.symbol}: {days_ago} days ago")

def display_payout_history(data):
    """Display weekly payout history and analysis"""
    st.markdown("## 💰 Weekly Dividend Payouts")
    
    # Get payout data
    payout_data = data['data_collector'].weekly_payouts.payout_data
    
    if not payout_data:
        st.warning("No payout data available")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    summary = data['data_collector'].weekly_payouts.get_weekly_summary()
    
    with col1:
        st.metric("📅 Week", summary['week_of'])
    
    with col2:
        if summary['highest_payouts']:
            highest = summary['highest_payouts'][0]
            st.metric("🏆 Highest Yield", f"{highest[0]}: {highest[1]:.2f}%")
    
    with col3:
        st.metric("📊 Average Yield", f"{summary['average_payout_percentage']:.2f}%")
    
    with col4:
        st.metric("💵 Total Income", f"${summary['total_estimated_income']:.2f}")
    
    # Payout chart
    symbols = list(payout_data.keys())
    yields = [payout_data[symbol].payout_percentage for symbol in symbols]
    amounts = [payout_data[symbol].dividend_amount for symbol in symbols]
    
    # Color code by yield level
    colors = ['green' if y >= 0.5 else 'orange' if y >= 0.2 else 'red' for y in yields]
    
    fig_yield = go.Figure(data=[
        go.Bar(
            x=symbols,
            y=yields,
            marker_color=colors,
            text=[f"{y:.2f}%" for y in yields],
            textposition='auto',
            customdata=amounts,
            hovertemplate='<b>%{x}</b><br>Yield: %{y:.2f}%<br>Amount: $%{customdata:.3f}<extra></extra>'
        )
    ])
    
    fig_yield.update_layout(
        title="Weekly Dividend Yields",
        yaxis_title="Yield (%)",
        showlegend=False,
        height=400
    )
    
    # Add yield reference lines
    fig_yield.add_hline(y=0.5, line_dash="dash", line_color="green", annotation_text="High Yield (0.5%)")
    fig_yield.add_hline(y=0.2, line_dash="dash", line_color="orange", annotation_text="Low Yield (0.2%)")
    
    st.plotly_chart(fig_yield, use_container_width=True)
    
    # Detailed payout table
    payout_df = pd.DataFrame([
        {
            'ETF': symbol,
            'Company': payout.company,
            'Dividend': f"${payout.dividend_amount:.3f}",
            'NAV': f"${payout.nav_price:.2f}",
            'Yield %': f"{payout.payout_percentage:.2f}%",
            'Ex Date': payout.ex_date,
            'Pay Date': payout.pay_date,
            'Source': payout.data_source.title()
        }
        for symbol, payout in payout_data.items()
    ])
    
    st.dataframe(payout_df, use_container_width=True)

def display_export_options(data):
    """Display export and alert options"""
    st.markdown("## 📤 Export & Alerts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Export Data")
        
        if st.button("📄 Export to CSV", type="primary"):
            # Create comprehensive CSV export
            signals = data['signals']
            
            # Export rotation signals
            export_data = []
            for symbol in signals['rotate_in']:
                export_data.append({
                    'ETF': symbol,
                    'Action': 'ROTATE IN',
                    'Timestamp': signals['timestamp']
                })
            
            for symbol in signals['rotate_out']:
                export_data.append({
                    'ETF': symbol,
                    'Action': 'ROTATE OUT',
                    'Timestamp': signals['timestamp']
                })
            
            df = pd.DataFrame(export_data)
            csv = df.to_csv(index=False)
            
            st.download_button(
                label="💾 Download Rotation Signals CSV",
                data=csv,
                file_name=f"rotation_signals_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv"
            )
        
        if st.button("📋 Export Alert Format"):
            alert = data['alert']
            json_str = json.dumps(alert, indent=2)
            
            st.download_button(
                label="💾 Download Alert JSON",
                data=json_str,
                file_name=f"weekly_alert_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
    
    with col2:
        st.markdown("### 🚨 Alert Settings")
        
        # Alert preferences (for future implementation)
        st.checkbox("📧 Email alerts", value=False, disabled=True, help="Coming soon!")
        st.checkbox("📱 SMS alerts", value=False, disabled=True, help="Coming soon!")
        st.checkbox("📊 Daily summary", value=True, disabled=True, help="Coming soon!")
        
        st.info("💡 Alert features will be available in the next update!")

def main():
    """Main dashboard application following Aristo's design layout"""
    # Load system data first
    data = load_system_data()
    
    if data is None:
        st.error("Failed to load system data. Please check your configuration.")
        return
    
    # 🔷 1. Header Section
    current_week = display_header()
    
    # Sidebar controls (minimized per Aristo's layout)
    with st.sidebar:
        st.markdown("## 🎛️ Controls")
        auto_refresh = st.checkbox("🔄 Auto-refresh", value=True)
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.rerun()
    
    # Create main layout with proper spacing
    st.markdown("---")
    
    # 📊 2. ETF Rotation Panel (Primary focus - most actionable)
    display_etf_rotation_panel(data)
    
    st.markdown("---")
    
    # 📈 3. Sector Momentum Panel (Primary focus - most actionable)
    display_sector_momentum_panel(data)
    
    st.markdown("---")
    
    # 🔔 6. Alerts & Notes Panel (Key insights and strategy)
    display_alerts_and_notes_panel(data)
    
    # Secondary information in expandable sections
    # (Following Aristo's suggestion to start with ETF Rotation & Sector Momentum first)
    st.markdown("### � Additional Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📅 Earnings Calendar Panel", expanded=False):
            display_earnings_calendar(data)
    
    with col2:
        with st.expander("💰 Weekly Payout Tracker", expanded=False):
            display_payout_history(data)
    
    # Export options at the bottom
    with st.expander("📤 Export & Data Options", expanded=False):
        display_export_options(data)
    
    # Footer with updated branding
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666; font-family: Arial, sans-serif;'>"
        "� WeeklyPay™ Tactical Rotation Engine | Enhanced by Aristo's design recommendations"
        "</div>", 
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
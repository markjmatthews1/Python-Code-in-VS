"""
Minimal ADX Chart Test - Bypass dashboard completely
"""
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import date, datetime

# Load raw data
print("🔄 Loading data...")
df = pd.read_csv("historical_data.csv")
df['Datetime'] = pd.to_datetime(df['Datetime'], format='mixed')
print(f"✅ Loaded {len(df)} rows")

# Get one ticker with lots of data
ticker = "AMD"
ticker_data = df[df['Ticker'] == ticker].copy()
print(f"📊 {ticker}: {len(ticker_data)} total rows")

if len(ticker_data) < 50:
    print("❌ Not enough data")
    exit()

# Sort and get recent data
ticker_data = ticker_data.sort_values('Datetime')
recent_data = ticker_data.tail(100)  # Last 100 points
print(f"📊 Using last {len(recent_data)} rows")
print(f"   Date range: {recent_data['Datetime'].min()} to {recent_data['Datetime'].max()}")

# Simple ADX calculation (simplified)
def simple_adx(df, period=14):
    """Simplified ADX calculation"""
    df = df.copy()
    
    # True Range
    df['HL'] = df['High'] - df['Low']
    df['HC'] = abs(df['High'] - df['Close'].shift(1))
    df['LC'] = abs(df['Low'] - df['Close'].shift(1))
    df['TR'] = df[['HL', 'HC', 'LC']].max(axis=1)
    
    # Directional Movement
    df['DM+'] = df['High'] - df['High'].shift(1)
    df['DM-'] = df['Low'].shift(1) - df['Low']
    
    df['DM+'] = df['DM+'].where((df['DM+'] > 0) & (df['DM+'] > df['DM-']), 0)
    df['DM-'] = df['DM-'].where((df['DM-'] > 0) & (df['DM-'] > df['DM+']), 0)
    
    # Smoothed values
    df['ATR'] = df['TR'].rolling(window=period).mean()
    df['DM+_smooth'] = df['DM+'].rolling(window=period).mean()
    df['DM-_smooth'] = df['DM-'].rolling(window=period).mean()
    
    # DI values
    df['+DI'] = 100 * (df['DM+_smooth'] / df['ATR'])
    df['-DI'] = 100 * (df['DM-_smooth'] / df['ATR'])
    
    # ADX
    df['DX'] = 100 * abs(df['+DI'] - df['-DI']) / (df['+DI'] + df['-DI'])
    df['ADX'] = df['DX'].rolling(window=period).mean()
    
    return df[['Datetime', 'ADX', '+DI', '-DI']]

# Calculate ADX
print("🧮 Calculating ADX...")
adx_result = simple_adx(recent_data)
adx_clean = adx_result.dropna()
print(f"✅ ADX calculated: {len(adx_clean)} valid rows")

if adx_clean.empty:
    print("❌ No valid ADX data")
    exit()

print(f"📈 ADX range: {adx_clean['ADX'].min():.2f} to {adx_clean['ADX'].max():.2f}")
print(f"📈 +DI range: {adx_clean['+DI'].min():.2f} to {adx_clean['+DI'].max():.2f}")
print(f"📈 -DI range: {adx_clean['-DI'].min():.2f} to {adx_clean['-DI'].max():.2f}")

# Create simple chart
print("📊 Creating chart...")
fig = make_subplots(
    rows=1, cols=1,
    subplot_titles=[f"{ticker} ADX/DMS MINIMAL TEST"]
)

# Add traces
fig.add_trace(go.Scatter(
    x=adx_clean['Datetime'],
    y=adx_clean['ADX'],
    mode='lines',
    name='ADX',
    line=dict(color='blue', width=3)
))

fig.add_trace(go.Scatter(
    x=adx_clean['Datetime'],
    y=adx_clean['+DI'],
    mode='lines',
    name='+DI',
    line=dict(color='green', width=2)
))

fig.add_trace(go.Scatter(
    x=adx_clean['Datetime'],
    y=adx_clean['-DI'],
    mode='lines',
    name='-DI',
    line=dict(color='red', width=2)
))

# Add reference line
fig.add_hline(y=25, line_dash="dot", line_color="gray")

fig.update_layout(
    title="MINIMAL ADX TEST - Should Work!",
    height=400,
    showlegend=True
)

# Save chart
fig.write_html("minimal_adx_test.html")
print("✅ Minimal ADX chart saved as minimal_adx_test.html")
print("📂 Open this file to verify ADX charts can be created")

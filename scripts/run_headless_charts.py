"""Headless runner to invoke update_dash from day.py and save generated Plotly figures to HTML for inspection.

Usage: python scripts/run_headless_charts.py
"""
import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
from datetime import datetime

# Import the update function from day.py
from day import update_dash

# Prepare minimal inputs - n_intervals and numeric chart sizes
n_intervals = 0
# Select tickers from historical_data.csv so update_dash has data to work with
hist_csv = os.path.join(os.path.dirname(__file__), '..', 'historical_data.csv')
try:
    hist_df = pd.read_csv(hist_csv)
    available = hist_df['Ticker'].dropna().unique().tolist()
    # pick up to 3 tickers for testing
    selected_tickers = available[:3] if available else None
    print('Auto-selected tickers for headless test:', selected_tickers)
except Exception as _err:
    print('Failed to read historical_data.csv for tickers:', _err)
    selected_tickers = None
n_clicks = 0
price_chart_height = 300
price_tick_count = 120
volume_chart_height = 200
volume_tick_count = 120
adx_chart_height = 200
adx_tick_count = 60
pmo_chart_height = 200
pmo_tick_count = 60

# Call update_dash
print('Calling update_dash headlessly...')
import traceback
try:
    res = update_dash(n_intervals, selected_tickers, n_clicks,
                       price_chart_height, price_tick_count,
                       volume_chart_height, volume_tick_count,
                       adx_chart_height, adx_tick_count,
                       pmo_chart_height, pmo_tick_count)

    if res is None:
        print('update_dash returned None')
        sys.exit(1)

    price_fig, volume_fig, adx_fig, pmo_fig, news_table, whale_table = res
except Exception as e:
    print('Exception while calling update_dash:')
    traceback.print_exc()
    sys.exit(2)

# Save HTML outputs
out_dir = os.path.join(os.path.dirname(__file__), 'headless_output')
os.makedirs(out_dir, exist_ok=True)
log_file = os.path.join(out_dir, 'headless_debug.log')
f_log = open(log_file, 'w', encoding='utf-8')
def lprint(*a, **kw):
    print(*a, **kw)
    print(*a, **kw, file=f_log)

price_html = os.path.join(out_dir, 'price_fig.html')
volume_html = os.path.join(out_dir, 'volume_fig.html')
adx_html = os.path.join(out_dir, 'adx_fig.html')

lprint('Saving figures to HTML...')
price_fig.write_html(price_html, include_plotlyjs='cdn')
volume_fig.write_html(volume_html, include_plotlyjs='cdn')
adx_fig.write_html(adx_html, include_plotlyjs='cdn')

lprint('Saved:', price_html, volume_html, adx_html)
lprint('Done')
f_log.close()

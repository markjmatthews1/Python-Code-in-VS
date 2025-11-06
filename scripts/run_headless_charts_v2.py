"""Improved headless runner: loads CSV into day.historical_data, calls update_dash with explicit tickers,
writes HTML files and a debug log for inspection.
"""
import os, sys, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd

import day
from day import update_dash

out_dir = os.path.join(os.path.dirname(__file__), 'headless_output_v2')
os.makedirs(out_dir, exist_ok=True)
log_path = os.path.join(out_dir, 'headless_v2.log')
with open(log_path, 'w', encoding='utf-8') as f:
    def lprint(*args, **kwargs):
        print(*args, **kwargs)
        print(*args, **kwargs, file=f)
        f.flush()

    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'historical_data.csv')
        lprint('Reading CSV', csv_path)
        hist = pd.read_csv(csv_path)
        lprint('CSV rows:', len(hist))

        # Force Datetime parsing
        if 'Datetime' in hist.columns:
            hist['Datetime'] = pd.to_datetime(hist['Datetime'], errors='coerce')
            lprint('Parsed datetime, NaT count:', hist['Datetime'].isna().sum())
            hist = hist.dropna(subset=['Datetime'])

        # Set as global in day module
        day.historical_data = hist
        lprint('Assigned day.historical_data with rows:', len(day.historical_data))

        # Pick tickers that exist
        tickers = hist['Ticker'].dropna().unique().tolist()
        tickers = tickers[:3] if len(tickers) >= 1 else []
        lprint('Using tickers:', tickers)
        if not tickers:
            lprint('No tickers available, exiting')
            raise SystemExit(1)

        # Call update_dash
        lprint('Calling update_dash...')
        res = update_dash(0, tickers, 0, 300, 120, 200, 120, 200, 60, 200, 60)
        if res is None:
            lprint('update_dash returned None')
            raise SystemExit(2)

        price_fig, volume_fig, adx_fig, pmo_fig, news_table, whale_table = res
        lprint('Got figures: price traces', len(price_fig.data) if hasattr(price_fig, 'data') else 0,
               'volume traces', len(volume_fig.data) if hasattr(volume_fig, 'data') else 0,
               'adx traces', len(adx_fig.data) if hasattr(adx_fig, 'data') else 0)

        # Save figures
        price_html = os.path.join(out_dir, 'price_fig.html')
        volume_html = os.path.join(out_dir, 'volume_fig.html')
        adx_html = os.path.join(out_dir, 'adx_fig.html')
        price_fig.write_html(price_html, include_plotlyjs='cdn')
        volume_fig.write_html(volume_html, include_plotlyjs='cdn')
        adx_fig.write_html(adx_html, include_plotlyjs='cdn')
        lprint('Saved HTML:', price_html, volume_html, adx_html)

    except Exception:
        traceback.print_exc(file=f)
        traceback.print_exc()
        raise

print('Done. Log at', log_path)

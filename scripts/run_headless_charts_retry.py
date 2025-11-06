"""Retrying headless runner: waits and retries calling update_dash until figures are ready.
Logs to scripts/headless_output_retry/headless_retry.log and writes HTML when successful.
"""
import os, sys, time, traceback
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import pandas as pd
import day
from day import update_dash

out_dir = os.path.join(os.path.dirname(__file__), 'headless_output_retry')
os.makedirs(out_dir, exist_ok=True)
log_path = os.path.join(out_dir, 'headless_retry.log')
max_attempts = 6
wait_seconds = 30

with open(log_path, 'a', encoding='utf-8') as f:
    def lprint(*args, **kwargs):
        print(*args, **kwargs)
        print(*args, **kwargs, file=f)
        f.flush()

    lprint('=== Headless retry runner started ===')
    try:
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'historical_data.csv')
        lprint('Reading CSV', csv_path)
        hist = pd.read_csv(csv_path)
        lprint('CSV rows:', len(hist))
    except Exception as e:
        lprint('Failed to read CSV:', e)
        hist = pd.DataFrame()

    # assign historical_data to day module
    if not hist.empty and 'Datetime' in hist.columns:
        hist['Datetime'] = pd.to_datetime(hist['Datetime'], errors='coerce')
        hist = hist.dropna(subset=['Datetime'])
    day.historical_data = hist
    lprint('Assigned day.historical_data rows:', len(getattr(day, 'historical_data', pd.DataFrame())))

    tickers = hist['Ticker'].dropna().unique().tolist() if not hist.empty else []
    if not tickers:
        lprint('No tickers in CSV, exiting')
        sys.exit(1)
    tickers = tickers[:3]
    lprint('Testing tickers:', tickers)

    success = False
    for attempt in range(1, max_attempts+1):
        lprint(f'Attempt {attempt}/{max_attempts} - calling update_dash')
        try:
            res = update_dash(0, tickers, 0, 300, 120, 200, 120, 200, 60, 200, 60)
            if res is None:
                lprint('update_dash returned None')
            else:
                price_fig, volume_fig, adx_fig, pmo_fig, news_table, whale_table = res
                p_traces = len(price_fig.data) if hasattr(price_fig, 'data') else 0
                v_traces = len(volume_fig.data) if hasattr(volume_fig, 'data') else 0
                a_traces = len(adx_fig.data) if hasattr(adx_fig, 'data') else 0
                lprint(f'Got figures - price_traces={p_traces}, volume_traces={v_traces}, adx_traces={a_traces}')
                if p_traces > 0:
                    # Save outputs
                    price_html = os.path.join(out_dir, 'price_fig.html')
                    volume_html = os.path.join(out_dir, 'volume_fig.html')
                    adx_html = os.path.join(out_dir, 'adx_fig.html')
                    price_fig.write_html(price_html, include_plotlyjs='cdn')
                    volume_fig.write_html(volume_html, include_plotlyjs='cdn')
                    adx_fig.write_html(adx_html, include_plotlyjs='cdn')
                    lprint('Saved HTML:', price_html, volume_html, adx_html)
                    success = True
                    break
                else:
                    lprint('Figures had no traces yet; will retry after wait')
        except Exception:
            traceback.print_exc(file=f)
            traceback.print_exc()
        if attempt < max_attempts:
            lprint(f'Waiting {wait_seconds} seconds before next attempt...')
            time.sleep(wait_seconds)

    if not success:
        lprint('Failed to get populated figures after retries')
    else:
        lprint('Success: figures saved')

    lprint('=== Headless retry runner finished ===')

print('Done. See log at', log_path)

from logging import root
import pandas as pd
from sklearn import tree
import yfinance as yf
from datetime import date
import time
import os
from datetime import datetime, date
import json
import requests
import tkinter as tk
from tkinter import ttk
import joblib
from joblib import load
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import accuracy_score

def get_dividend_info_from_yahoo(ticker: str) -> dict:
    """
    Replacement function for yahoo_scraper using yfinance
    Returns dividend information for a given ticker
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Get dividend history
        dividends = stock.dividends
        
        # Calculate basic dividend metrics
        dividend_data = {
            'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
            'annual_dividend_rate': info.get('dividendRate', 0),
            'payout_ratio': info.get('payoutRatio', 0) * 100 if info.get('payoutRatio') else 0,
            'ex_dividend_date': info.get('exDividendDate', ''),
            'dividend_date': info.get('dividendDate', ''),
            'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield', 0),
            'forward_pe': info.get('forwardPE', 0),
            'trailing_pe': info.get('trailingPE', 0),
            'price_to_book': info.get('priceToBook', 0),
            'market_cap': info.get('marketCap', 0),
            'enterprise_value': info.get('enterpriseValue', 0),
            'current_price': info.get('currentPrice', 0),
            'beta': info.get('beta', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'return_on_equity': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else 0,
            'return_on_assets': info.get('returnOnAssets', 0) * 100 if info.get('returnOnAssets') else 0,
            'profit_margins': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else 0,
            'operating_margins': info.get('operatingMargins', 0) * 100 if info.get('operatingMargins') else 0,
            'earnings_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0,
            'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
        }
        
        # Calculate dividend growth if we have dividend history
        if not dividends.empty and len(dividends) >= 2:
            # Get last two years of dividends to calculate growth
            recent_dividends = dividends.tail(8)  # Assuming quarterly dividends
            if len(recent_dividends) >= 4:
                recent_year = recent_dividends.tail(4).sum()
                previous_year = recent_dividends.head(4).sum() if len(recent_dividends) >= 8 else recent_year
                if previous_year > 0:
                    dividend_data['dividend_growth'] = ((recent_year - previous_year) / previous_year) * 100
                else:
                    dividend_data['dividend_growth'] = 0
            else:
                dividend_data['dividend_growth'] = 0
        else:
            dividend_data['dividend_growth'] = 0
            
        return dividend_data
        
    except Exception as e:
        print(f"Error fetching Yahoo data for {ticker}: {e}")
        return {
            'dividend_yield': 0,
            'annual_dividend_rate': 0,
            'payout_ratio': 0,
            'ex_dividend_date': '',
            'dividend_date': '',
            'five_year_avg_dividend_yield': 0,
            'forward_pe': 0,
            'trailing_pe': 0,
            'price_to_book': 0,
            'market_cap': 0,
            'enterprise_value': 0,
            'current_price': 0,
            'beta': 0,
            'debt_to_equity': 0,
            'return_on_equity': 0,
            'return_on_assets': 0,
            'profit_margins': 0,
            'operating_margins': 0,
            'earnings_growth': 0,
            'revenue_growth': 0,
            'dividend_growth': 0,
        }
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV

    




                                # This script screens high-yield dividend stocks using FMP and E*TRADE APIs,
                                # caches results to avoid hitting API limits, and provides a GUI for viewing candidates.

# ========== Settings ==========
FMP_API_KEY = "QWHCIBxksyrCtnS3QOhV369o7bLQFAQh"
INPUT_CSV = "high_yield_monthlies.csv"
OUTPUT_CSV = "screened_monthly_dividend_candidates.csv"
REFRESH_META = "screening_meta.json"
PENDING_TICKERS_FILE = "tickers_pending.json"
MAX_FMP_CALLS = 250 # FMP free tier limit is really 250 calls per day, but we want to leave some buffer
DIVIDEND_CACHE_FILE = "fmp_dividend_cache.json"


MODEL_PATH = "div_continuity_model.joblib"
RETRAIN_INTERVAL_DAYS = 30
global fmp_calls

# ========== ETRADE API INTEGRATION ==========
from etrade_auth import get_etrade_session  # Already used in your etrade_quote app

def remap_frequency(val):
    freq_map = {
        52: "Weekly", 12: "Monthly", 4: "Quarterly",
        2: "Semi-Annually", 1: "Annually"
    }
    try:
        return freq_map.get(int(val), val)
    except (ValueError, TypeError):
        return val
    
def enforce_string_frequency(df):
    """Ensure 'Est. Frequency' is always a string label, not a number."""
    if "Est. Frequency" in df.columns:
        df["Est. Frequency"] = df["Est. Frequency"].apply(remap_frequency)
    return df
    
def incremental_update_candidates(candidate_file="scored_candidates.csv"):
    """
    Always update all tickers in the candidate file (except manual entries),
    preserving manual edits and only updating fields with new data.
    """
    import pandas as pd

    if not os.path.exists(candidate_file):
        print(f"🚫 Candidate file '{candidate_file}' not found.")
        return

    df = pd.read_csv(candidate_file)
    if "Source" not in df.columns:
        df["Source"] = "FMP"

    # Update all tickers (including manual entries)
    tickers_to_update = df["Ticker"].tolist()

    print(f"🔄 {len(tickers_to_update)} tickers to update out of {len(df)} total (including manual entries).")

    # Pull new data for those tickers
    if tickers_to_update:
        updated_df = build_feature_dataframe(tickers_to_update)
        if not updated_df.empty:
            scored_df = predict_dividend_continuity(updated_df)
            merge_new_screen_with_existing(candidate_file, scored_df)
        else:
            print("⚠️ No new data pulled for updates.")
    else:
        print("✅ All candidate tickers are up to date (manual entries only).")

    # Reload and return updated DataFrame
    return pd.read_csv(candidate_file)

def get_etrade_dividend_data(tickers):
    """
    Fetch dividend data from E*TRADE for a batch of tickers.
    Normalizes structure to match FMP-based screening output.
    """
    session, base_url = get_etrade_session()
    url = f"{base_url}/v1/market/quote/" + ",".join(tickers)
    headers = {"Accept": "application/json"}

    response = session.get(url, headers=headers, timeout=10)

    if response.status_code == 401:
        import os
        if os.path.exists("etrade_tokens.pkl"):
            os.remove("etrade_tokens.pkl")
        print("🔒 E*TRADE token expired. Please re-run to re-authenticate.")
        return []

    if response.status_code != 200:
        print(f"🚨 E*TRADE API error {response.status_code}: {response.text}")
        return []

    try:
        data = response.json()
    except Exception as e:
        print(f"❌ E*TRADE JSON decode error: {e}")
        return []

    fallback_results = []
    for quote in data.get("QuoteResponse", {}).get("QuoteData", []):
        symbol = quote.get("Product", {}).get("symbol")
        if not symbol or "messages" in quote:
            continue

        details = quote.get("All", quote)
        price = details.get("lastTrade") or details.get("lastPrice") or details.get("adjustedClose")

        # Dividend and fundamentals
        dividend = details.get("dividend", 0)
        div_yield = details.get("dividendYield")
        eps = details.get("eps")
        payout_ratio = details.get("payoutRatio")
        beta = details.get("beta", "N/A")
        d2e = details.get("debtToEquity", "N/A")
        sector = details.get("sector", "N/A")
        industry = details.get("industry", "N/A")

        if not price or dividend == 0:
            continue

        # Estimate yield if missing
        if not div_yield and dividend and price:
            div_yield = (dividend * 12 / price) * 100

        # EPS or payout logic fallback
        try:
            payout = float(payout_ratio) if payout_ratio else (dividend * 4) / eps if eps else "N/A"
        except Exception:
            payout = "N/A"

        # Append result with consistent field names
        fallback_results.append({
            "Ticker": symbol,
            "Yield Est (%)": round(div_yield, 2) if div_yield else "N/A",
            "EPS": round(eps, 2) if isinstance(eps, (float, int)) else eps,
            "Payout Ratio": round(payout, 2) if isinstance(payout, (float, int)) else payout,
            "Beta": round(beta, 2) if isinstance(beta, (float, int)) else beta,
            "Div History (yrs)": "N/A",
            "5Y Growth Rate (%)": "N/A",
            "Debt/Equity": round(d2e, 2) if isinstance(d2e, (float, int)) else d2e,
            "Sector": sector,
            "Industry": industry
        })

    return fallback_results

                                            # ========== FMP API Caching ==========
                                            # This is to avoid hitting the FMP API rate limit too quickly

fmp_calls = 0  # This tracks how many FMP calls we've made today

def fetch_dividend_data(ticker: str, source_a_func) -> dict:
    data = source_a_func(ticker)
    
    if not data or any(v is None for v in data.values()):
        print(f"[Fallback Triggered] Pulling Yahoo Finance data for: {ticker}")
        yahoo_data = get_dividend_info_from_yahoo(ticker)

        # Only fill missing fields from Yahoo if not already present
        for k, v in yahoo_data.items():
            if k not in data or data[k] is None:
                data[k] = v

        data["source"] = "Yahoo"
    else:
        data["source"] = "FMP"

    return data
# ...existing code...

def fetch_dividend_dates_for_df(df):
    import yfinance as yf
    from datetime import datetime

    ex_divs = []
    payouts = []

    for ticker in df["Ticker"]:
        try:
            stock = yf.Ticker(ticker)
            divs = stock.dividends
            if not divs.empty:
                ex_div_date = divs.index[-1].strftime("%Y-%m-%d")
                ex_divs.append(ex_div_date)
                # yfinance does not always provide payout date, so leave blank or try FMP
                payouts.append("")
            else:
                ex_divs.append("")
                payouts.append("")
        except Exception:
            ex_divs.append("")
            payouts.append("")
    df["Ex-Dividend Date"] = ex_divs
    df["Payout Date"] = payouts
    return df

def load_dividend_cache():
    if os.path.exists(DIVIDEND_CACHE_FILE):
        with open(DIVIDEND_CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_dividend_cache(cache):
    with open(DIVIDEND_CACHE_FILE, "w") as f:
        json.dump(cache, f)

dividend_cache = load_dividend_cache()

def get_fmp_dividends(symbol):
    global fmp_calls, dividend_cache

    if symbol in dividend_cache:
        return dividend_cache[symbol]

    if fmp_calls >= MAX_FMP_CALLS:
        print(f"🚫 FMP call limit ({MAX_FMP_CALLS}) reached.")
        return None

    url = f"https://financialmodelingprep.com/api/v3/historical-price-full/stock_dividend/{symbol}?apikey={FMP_API_KEY}"

    try:
        response = requests.get(url, timeout=10)
        fmp_calls += 1

        if response.status_code == 200:
            data = response.json().get("historical", [])
            dividend_cache[symbol] = data
            save_dividend_cache(dividend_cache)
            return data
        else:
            print(f"{symbol} – FMP call failed: {response.status_code} – {response.text}")
            return None
    except Exception as e:
        print(f"{symbol} – FMP call error: {e}")
        return None

# ========== Daily Refresh Logic ==========
def is_today_refresh_needed():
    if not os.path.exists(REFRESH_META):
        return True
    try:
        with open(REFRESH_META, "r") as f:
            data = json.load(f)
            last_run = datetime.strptime(data.get("last_run", ""), "%Y-%m-%d").date()
            return last_run < date.today()
    except:
        return True

def mark_refresh_complete():
    with open(REFRESH_META, "w") as f:
        json.dump({"last_run": date.today().strftime("%Y-%m-%d")}, f)

# ========== FMP API ==========

def run_screen():
    import pandas as pd

    if os.path.exists(PENDING_TICKERS_FILE):
        with open(PENDING_TICKERS_FILE, "r") as f:
            tickers = json.load(f)
        print("📂 Resuming from saved tickers list...")
    else:
        df = pd.read_csv(INPUT_CSV)
        tickers = df.iloc[:, 0].dropna().unique().tolist()

    # 🧷 Backup initial ticker list
    today = date.today().strftime("%Y%m%d")
    backup_path = f"backup_ticker_list_{today}.json"
    with open(backup_path, "w") as f:
        json.dump(tickers, f)
    print(f"🗂️ Backup created: {backup_path}")

    # === Daily cache file ===
    daily_cache_path = f"fmp_daily_results_{today}.csv"
    if os.path.exists(daily_cache_path):
        cache_df = pd.read_csv(daily_cache_path)
        processed = set(cache_df["Ticker"].tolist())
        filtered_data = cache_df.to_dict(orient="records")
        print(f"📁 Loaded cache with {len(processed)} entries")
    else:
        processed = set()
        filtered_data = []

    leftover = []
    total = len(tickers)
    print(f"🔍 Screening {total} tickers...")

    for i, symbol in enumerate(tickers, start=1):
        print(f"[{i}/{total}] {symbol} | Matches: {len(filtered_data)} | FMP Calls: {fmp_calls}")

        if symbol in processed:
            print(f"⏩ Skipping {symbol}, already cached.")
            continue

        if fmp_calls >= MAX_FMP_CALLS:
            leftover = tickers[i:]
            print(f"🚧 FMP rate limit hit at {fmp_calls} calls.")
            print(f"🟡 Attempting to screen remaining {len(leftover)} tickers using E*TRADE...")
            break

        try:
            # === Dividend history check from FMP ===
            fmp_divs = get_fmp_dividends(symbol)
            if not fmp_divs or len(fmp_divs) < 3:
                continue
            df_divs = pd.DataFrame(fmp_divs)
            df_divs["date"] = pd.to_datetime(df_divs["date"])
            df_divs.sort_values("date", ascending=False, inplace=True)
            dividend_dates = df_divs["date"].tolist()

            intervals = [(dividend_dates[i] - dividend_dates[i+1]).days for i in range(len(dividend_dates)-1)]
            avg_interval = sum(intervals) / len(intervals)
            if avg_interval > 35:
                continue

            most_recent_div = df_divs.iloc[0]["dividend"]
            if most_recent_div == 0:
                continue

            stock = yf.Ticker(symbol)
            try:
                price = stock.fast_info.get("lastPrice", None)
            except Exception as e:
                print(f"{symbol} – Price fetch error: {e}")
                continue
            if price is None:
                print(f"{symbol} – Price unavailable.")
                continue

            yield_est = (most_recent_div * 12 / price) * 100
            print(f"{symbol} – Price: {price:.2f}, Dividend: {most_recent_div}, Yield Est: {yield_est:.2f}%")
            if yield_est < 15:
                continue

            fin = stock.financials
            cf = stock.cashflow
            eps = fin.loc['Net Income', :].iloc[0] / fin.loc['Diluted Average Shares', :].iloc[0]
            payout = abs(cf.loc['Cash Dividends Paid', :].iloc[0]) / fin.loc['Net Income', :].iloc[0]
            if eps <= 0 and payout > 1.2:
                continue

            try:
                info = stock.get_info()
                beta = info.get("beta", "N/A")
                d2e = info.get("debtToEquity", "N/A")
                sector = info.get("sector", "N/A")
                industry = info.get("industry", "N/A")
            except:
                beta = d2e = sector = industry = "N/A"

            div_years = round((dividend_dates[0] - dividend_dates[-1]).days / 365, 1)
            if len(df_divs) >= 10:
                start, end = df_divs.iloc[-1]["dividend"], df_divs.iloc[0]["dividend"]
                try:
                    growth_rate = round(((end / start) ** (1 / div_years) - 1) * 100, 2)
                except:
                    growth_rate = "N/A"
            else:
                growth_rate = "N/A"

            row = {
                "Ticker": symbol,
                "Yield Est (%)": round(yield_est, 2),
                "EPS": round(eps, 2),
                "Payout Ratio": round(payout, 2),
                "Beta": round(beta, 2) if isinstance(beta, (float, int)) else beta,
                "Div History (yrs)": div_years,
                "5Y Growth Rate (%)": growth_rate,
                "Debt/Equity": round(d2e, 2) if isinstance(d2e, (float, int)) else d2e,
                "Sector": sector,
                "Industry": industry
            }

            filtered_data.append(row)
            pd.DataFrame(filtered_data).to_csv(daily_cache_path, index=False)
            processed.add(symbol)

        except Exception as e:
            print(f"[{symbol}] skipped: {e}")

    out_df = pd.DataFrame(filtered_data)
    expected_sort_keys = ["Yield Est (%)", "Payout Ratio", "Div History (yrs)"]
    existing_keys = [col for col in expected_sort_keys if col in out_df.columns]
    if existing_keys:
        sort_order = [False if col in ["Yield Est (%)", "Div History (yrs)"] else True for col in existing_keys]
        out_df.sort_values(by=existing_keys, ascending=sort_order, inplace=True)

    if not out_df.empty:
        out_df.to_csv(OUTPUT_CSV, index=False)
    else:
        print("⚠️ Skipped saving empty results file.")
    print(f"\n✅ {len(out_df)} tickers saved to '{OUTPUT_CSV}'")

    if leftover:
        with open(PENDING_TICKERS_FILE, "w") as f:
            json.dump(leftover, f)
    elif os.path.exists(PENDING_TICKERS_FILE):
        os.remove(PENDING_TICKERS_FILE)

    if not leftover:
        mark_refresh_complete()

    return out_df

def launch_dividend_gui(df, source_file=None):
    import tkinter as tk
    from tkinter import ttk
    import pandas as pd
    from datetime import date

    def remap_frequency(val):
        freq_map = {
            52: "Weekly", 12: "Monthly", 4: "Quarterly",
            2: "Semi-Annually", 1: "Annually"
        }
        try:
            return freq_map.get(int(val), val)
        except (ValueError, TypeError):
            return val

    # Always enforce string frequency before showing GUI
    if "Est. Frequency" in df.columns:
        df["Est. Frequency"] = df["Est. Frequency"].apply(remap_frequency)

    df = df.reset_index() if "Ticker" not in df.columns else df

    # --- PATCH: Add Ex-Dividend Date and Payout Date to editable fields ---
    required_fields = [
        "EPS", "Payout Ratio", "Beta",
        "Div History (yrs)", "5Y Growth Rate (%)", "Debt/Equity",
        "Est. Frequency", "Ex-Dividend Date", "Payout Date"
    ]
    # ---

    columns_to_show = [
        "Ticker", "Yield Est (%)", "Continuation Prob (%)",
        "Est. Frequency", "Div History (yrs)", "5Y Growth Rate (%)",
        "EPS", "Payout Ratio", "Beta", "Debt/Equity",
        "Sector", "Industry", "Source", "Last Updated",
        "Ex-Dividend Date", "Payout Date"
    ]

    if "Last Updated" not in df.columns:
        df["Last Updated"] = pd.NA
    if "Source" not in df.columns:
        df["Source"] = "FMP"

    df = df[[col for col in columns_to_show if col in df.columns]]

    if "Continuation Prob (%)" in df.columns:
        df = df.sort_values("Continuation Prob (%)", ascending=False)

    root = tk.Tk()
    root.title("Monthly Dividend Stock Candidates")

    style = ttk.Style()
    style.configure("Treeview", rowheight=28)

    tree = ttk.Treeview(root, columns=columns_to_show, show="headings")
    tree.pack(fill="both", expand=True)

    tree.tag_configure("high_prob", background="#c7f8c4")
    tree.tag_configure("med_prob", background="#fff9c0")
    tree.tag_configure("source_etrade", background="#e0f7ff")
    tree.tag_configure("source_yahoo", background="#fff3db")
    tree.tag_configure("source_manual", background="#e9dcf9")

    for col in columns_to_show:
        tree.heading(col, text=col)
        tree.column(col, width=110, anchor="center", stretch=False)

    def open_edit_window(row_data):
        edit_win = tk.Toplevel()
        edit_win.title(f"Edit {row_data['Ticker']}")
        entries = {}

        for idx, field in enumerate(required_fields):
            tk.Label(edit_win, text=field).grid(row=idx, column=0, padx=5, pady=5)
            val = row_data.get(field, "")
            entry = tk.Entry(edit_win)
            entry.insert(0, "" if pd.isna(val) else str(val))
            entry.grid(row=idx, column=1, padx=5, pady=5)
            entries[field] = entry

        def submit_edits():
            for field, entry in entries.items():
                row_data[field] = entry.get().strip()

            row_data["Source"] = "Manual"
            patched_df = pd.DataFrame([row_data])

            if "Continuation Prob (%)" in df.columns:
                df["Continuation Prob (%)"] = df["Continuation Prob (%)"].fillna("N/A")

            numeric_fields = [
                "EPS", "Payout Ratio", "Beta", "Div History (yrs)",
                "5Y Growth Rate (%)", "Debt/Equity"
            ]
            for col in numeric_fields:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
            if "Est. Frequency" in df.columns:
                df["Est. Frequency"] = df["Est. Frequency"].apply(remap_frequency)

            patched_df = predict_dividend_continuity(patched_df)
            patched_df["Last Updated"] = date.today().isoformat()

            if "Label" not in patched_df.columns:
                patched_df["Label"] = patched_df.apply(
                    lambda row: get_continuity_label(row["Ticker"], row.get("Source", "FMP")),
                    axis=1
                )
            patched_df["Label Display"] = patched_df["Label"].apply(
                lambda x: "—" if x == "N/A" else ("✅" if x == 1 else "❌")
            )
            patched_df.rename(columns={"Label": "12M Div History"}, inplace=True)

            try:
                full_df = pd.read_csv(source_file) if source_file else df
                full_df.set_index("Ticker", inplace=True)
                patched_df.set_index("Ticker", inplace=True)

                # ✅ Type alignment fix to prevent FutureWarnings
                patched_df = patched_df.convert_dtypes()
                full_df.update(patched_df)
                full_df.reset_index(inplace=True)

                # Always enforce string frequency before saving
                if "Est. Frequency" in full_df.columns:
                    full_df["Est. Frequency"] = full_df["Est. Frequency"].apply(remap_frequency)

                full_df.to_csv(source_file, index=False)
                print(f"💾 {row_data['Ticker']} saved to {source_file}")
            except Exception as e:
                print(f"⚠️ Save error: {e}")

            root.destroy()
            try:
                refreshed = pd.read_csv(source_file)
                if "Est. Frequency" in refreshed.columns:
                    refreshed["Est. Frequency"] = refreshed["Est. Frequency"].apply(remap_frequency)
                if source_file == "scored_candidates.csv":
                    # --- RE-APPLY FILTER: Only show tickers with Yield Est (%) >= 15% ---
                    refreshed["Yield Est (%)"] = pd.to_numeric(refreshed["Yield Est (%)"], errors="coerce")
                    refreshed = refreshed[refreshed["Yield Est (%)"] >= 15]
                    # --- END FILTER ---
                launch_dividend_gui(refreshed, source_file)
            except Exception as e:
                print(f"⚠️ Relaunch failed: {e}")

        tk.Button(edit_win, text="Save", command=submit_edits).grid(
            row=len(required_fields)+1, columnspan=2, pady=10
        )

    def edit_selected_row():
        selected = tree.selection()
        if selected:
            item_id = selected[0]
            values = tree.item(item_id)["values"]
            row_data = dict(zip(columns_to_show, values))
            open_edit_window(row_data)

    tk.Button(
        root, text="✏️ Edit Selected", command=edit_selected_row,
        bg="#3A75C4", fg="white", font=("Segoe UI", 11, "bold"), padx=12, pady=6
    ).pack(pady=12)

    for _, row in df.iterrows():
        row_vals = [row.get(col, "") for col in columns_to_show]
        prob = row.get("Continuation Prob (%)", 0)
        source = row.get("Source", "FMP")

        source_tag = {
            "Yahoo": "source_yahoo",
            "ETRADE": "source_etrade",
            "Manual": "source_manual"
        }.get(source, "")

        if isinstance(prob, (float, int)) and prob >= 80:
            tag = ("high_prob", source_tag)
        elif isinstance(prob, (float, int)) and 70 <= prob < 80:
            tag = ("med_prob", source_tag)
        else:
            tag = (source_tag,) if source_tag else ()

        tree.insert("", "end", values=row_vals, tags=tag)

    root.mainloop()

def build_feature_vector(ticker):
    from datetime import datetime
    global dividend_cache, fmp_calls

    # === Dividend history via FMP (cached) ===
    dividends = get_fmp_dividends(ticker)
    if dividends and len(dividends) >= 3:
        df_divs = pd.DataFrame(dividends)
        df_divs["date"] = pd.to_datetime(df_divs["date"])
        df_divs.sort_values("date", ascending=False, inplace=True)
        dividend_dates = df_divs["date"].tolist()
        most_recent_div = df_divs.iloc[0]["dividend"]

        if most_recent_div == 0:
            print(f"{ticker} – Most recent dividend is zero.")
            return None

        # === Inferred frequency-based dividend interval ===
        intervals = [(dividend_dates[i] - dividend_dates[i + 1]).days for i in range(len(dividend_dates) - 1)]
        avg_interval = sum(intervals) / len(intervals)
        estimated_frequency = round(365 / avg_interval)
        print(f"{ticker} – Frequency estimate: {estimated_frequency}×/year") # prints the estimated frequency

        # === Price and financial data ===
        stock = yf.Ticker(ticker)
        price = stock.fast_info.get("lastPrice", None)
        if price is None or price == 0:
            print(f"{ticker} – Price unavailable or invalid.")
            return None

        yield_est = (most_recent_div * estimated_frequency / price) * 100

        try:
            fin = stock.financials
            cf = stock.cashflow
            try:
                eps = fin.loc['Net Income', :].iloc[0] / fin.loc['Diluted Average Shares', :].iloc[0]
                payout = abs(cf.loc['Cash Dividends Paid', :].iloc[0]) / fin.loc['Net Income', :].iloc[0]
            except Exception as e:
                print(f"{ticker} – EPS or payout error: {e}")
                print(f"{ticker} – Escalating to fallback due to insufficient financials.")
                # Fallback handled below
                raise

        except Exception:
            eps = payout = "N/A"

        try:
            info = stock.get_info()
            beta = info.get("beta", "N/A")
            d2e = info.get("debtToEquity", "N/A")
            sector = info.get("sector", "N/A")
            industry = info.get("industry", "N/A")
        except Exception as e:
            print(f"{ticker} – get_info() error: {e}")
            beta = d2e = sector = industry = "N/A"

        # === Dividend history years and growth ===
        div_years = round((dividend_dates[0] - dividend_dates[-1]).days / 365, 1)
        if len(df_divs) >= 10:
            try:
                growth_rate = round(((df_divs.iloc[0]["dividend"] / df_divs.iloc[-1]["dividend"]) ** (1 / div_years) - 1) * 100, 2)
            except:
                growth_rate = "N/A"
        else:
            growth_rate = "N/A"

        # === Ex-Dividend and Payout Dates from FMP ===
        ex_dividend_date = df_divs.iloc[0].get("label", "")
        payout_date = df_divs.iloc[0].get("date", "")
        if isinstance(payout_date, pd.Timestamp):
            payout_date = payout_date.strftime("%Y-%m-%d")

        return pd.DataFrame([{
            "Ticker": ticker,
            "Avg Div Interval": round(avg_interval, 1),
            "Est. Frequency": estimated_frequency,
            "Yield Est (%)": round(yield_est, 2),
            "EPS": round(eps, 2) if isinstance(eps, (float, int)) else eps,
            "Payout Ratio": round(payout, 2) if isinstance(payout, (float, int)) else payout,
            "Beta": round(beta, 2) if isinstance(beta, (float, int)) else beta,
            "Div History (yrs)": div_years,
            "5Y Growth Rate (%)": growth_rate,
            "Debt/Equity": round(d2e, 2) if isinstance(d2e, (float, int)) else d2e,
            "Sector": sector,
            "Industry": industry,
            "Source": "FMP",
            "Ex-Dividend Date": ex_dividend_date,
            "Payout Date": payout_date
        }])

    # === FMP failed, try E*TRADE fallback ===
    print(f"{ticker} – Insufficient FMP dividend data. Attempting E*TRADE fallback...")
    etrade_data = get_etrade_dividend_data([ticker])
    if etrade_data:
        row = etrade_data[0]
        row["Source"] = "ETRADE"
        return pd.DataFrame([{
            "Ticker": ticker,
            "Avg Div Interval": "N/A",
            "Est. Frequency": "N/A",
            "Yield Est (%)": row.get("Yield Est (%)", "N/A"),
            "EPS": row.get("EPS", "N/A"),
            "Payout Ratio": row.get("Payout Ratio", "N/A"),
            "Beta": row.get("Beta", "N/A"),
            "Div History (yrs)": "N/A",
            "5Y Growth Rate (%)": "N/A",
            "Debt/Equity": row.get("Debt/Equity", "N/A"),
            "Sector": row.get("Sector", "N/A"),
            "Industry": row.get("Industry", "N/A"),
            "Source": row.get("Source", "ETRADE"),
            "Ex-Dividend Date": "",
            "Payout Date": ""
        }])
    row = etrade_data[0]
    row["Source"] = "ETRADE"

    return pd.DataFrame([{
        "Ticker": ticker,
        "Avg Div Interval": "N/A",
        "Yield Est (%)": row.get("Yield Est (%)", "N/A"),
        "EPS": row.get("EPS", "N/A"),
        "Payout Ratio": row.get("Payout Ratio", "N/A"),
        "Beta": row.get("Beta", "N/A"),
        "Div History (yrs)": "N/A",
        "5Y Growth Rate (%)": "N/A",
        "Debt/Equity": row.get("Debt/Equity", "N/A"),
        "Sector": row.get("Sector", "N/A"),
        "Industry": row.get("Industry", "N/A"),
        "Source": "ETRADE"
    }])

def build_feature_dataframe(ticker_list):
    print("🧪 Building feature vectors...")
    vectors = []
    for symbol in ticker_list:
        print(f"→ Processing: {symbol}")
        try:
            df = build_feature_vector(symbol)
            if df is not None:
                vectors.append(df)
            else:
                print(f"⚠️ Skipped: {symbol}")
        except Exception as e:
            print(f"❌ {symbol} – Build error: {e}")

    if vectors:
        full_df = pd.concat(vectors, ignore_index=True)
        print(f"\n✅ Built feature set for {len(full_df)} tickers.")
        return full_df
    else:
        print("\n🚫 No feature vectors were built.")
        return pd.DataFrame()
    
def predict_dividend_continuity(df, model_path="div_continuity_model.joblib"):
    import pandas as pd
    from datetime import date
    from joblib import load

    required_cols = [
        "Yield Est (%)", "EPS", "Payout Ratio", "Beta",
        "Div History (yrs)", "5Y Growth Rate (%)", "Debt/Equity"
    ]

    df = df.copy()
    # Ensure columns exist
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.0  # Use 0.0 instead of pd.NA

    # NEW: Ensure all required fields are numeric and fill missing with 0.0
    for col in required_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

    if "Last Updated" not in df.columns:
        df["Last Updated"] = pd.NA

    # Identify valid rows for scoring
    def is_valid(row):
        # Only check for missing (should never be missing now)
        for col in required_cols:
            val = row[col]
            if pd.isna(val):
                return False
        return True

    valid_mask = df.apply(is_valid, axis=1)
    valid_df = df[valid_mask].copy()
    invalid_df = df[~valid_mask].copy()

    # Prepare features
    if not valid_df.empty:
        # Convert all required columns to numeric
        for col in required_cols:
            valid_df[col] = pd.to_numeric(valid_df[col], errors="coerce")
        X = valid_df[required_cols].fillna(0.0)
        try:
            model = load(model_path)
            y_pred = model.predict_proba(X)[:, 1]
            valid_df["Continuation Prob (%)"] = (y_pred * 100).round(1)
            valid_df["Last Updated"] = date.today().isoformat()
            print(f"✅ Scored {len(valid_df)} tickers for continuation probability.")
        except FileNotFoundError:
            print(f"🚫 Model file '{model_path}' not found.")
            valid_df["Continuation Prob (%)"] = "N/A"
            valid_df["Last Updated"] = pd.NA
        except Exception as e:
            print(f"⚠️ Model prediction failed: {e}")
            print("⚠️ Data passed to model:")
            print(X)
            valid_df["Continuation Prob (%)"] = "N/A"
            valid_df["Last Updated"] = pd.NA
    else:
        print("\n🚫 No valid rows to score.")

    # For invalid rows, set as N/A
    invalid_df["Continuation Prob (%)"] = "N/A"
    invalid_df["Last Updated"] = pd.NA

    # Combine and return in original order
    final_df = pd.concat([valid_df, invalid_df], ignore_index=True)
    # Preserve original column order, add new columns at the end if needed
    for col in ["Continuation Prob (%)", "Last Updated"]:
        if col not in final_df.columns:
            final_df[col] = pd.NA
    final_df = final_df[[c for c in df.columns if c in final_df.columns] + [c for c in final_df.columns if c not in df.columns]]

    # Debug: print tickers that could not be scored
    if "Continuation Prob (%)" in final_df.columns:
        for idx, row in final_df.iterrows():
            if str(row["Continuation Prob (%)"]).upper() in ("N/A", "", "NONE", "NAN"):
                print(f"⚠️ {row['Ticker']} could not be scored due to missing/invalid data or model error.")

    return final_df

def get_continuity_label(ticker, source="FMP"):
    global dividend_cache

    if source == "ETRADE":
        return "N/A"  # No label available from E*TRADE-sourced tickers

    if ticker in dividend_cache:
        history = dividend_cache[ticker]
    else:
        history = get_fmp_dividends(ticker)

    if not history or len(history) < 3:
        return 0

    df = pd.DataFrame(history)
    df["date"] = pd.to_datetime(df["date"])
    df = df[df["date"] >= pd.Timestamp.now() - pd.DateOffset(months=12)]
    paid_months = df["date"].dt.to_period("M").nunique()

    return 1 if paid_months >= 11 else 0
    
def train_continuity_model(df, model_path="div_continuity_model.joblib"):
    # Define features and label columns
    required_cols = [
        "Yield Est (%)", "EPS", "Payout Ratio", "Beta",
        "Div History (yrs)", "5Y Growth Rate (%)", "Debt/Equity"
    ]
    label_col = "Label"  # Or whatever your label column is called

    # Drop rows with missing label or features
    df = df.dropna(subset=required_cols + [label_col])

    X = df[required_cols].apply(pd.to_numeric, errors="coerce").fillna(0.0)
    y = df[label_col].astype(int)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Build pipeline
    pipe = Pipeline([
        ("scale", StandardScaler()),
        ("logreg", LogisticRegression())
    ])
    pipe.fit(X_train, y_train)

    # Calibrate probabilities using Platt Scaling (sigmoid)
    calibrated = CalibratedClassifierCV(pipe, method='sigmoid', cv=5)
    calibrated.fit(X_train, y_train)

    # Evaluate and print performance
    y_pred = calibrated.predict(X_test)
    acc = accuracy_score(y_test, y_pred)
    print(f"📊 Calibrated model trained — test accuracy: {acc:.2%}")

    # Save calibrated model
    joblib.dump(calibrated, model_path)
    print(f"✅ Calibrated model saved to '{model_path}'")

    return calibrated

def merge_new_screen_with_existing(existing_file, new_df):
    def remap_frequency(val):
        freq_map = {
            52: "Weekly", 12: "Monthly", 4: "Quarterly",
            2: "Semi-Annually", 1: "Annually"
        }
        try:
            return freq_map.get(int(val), val)
        except (ValueError, TypeError):
            return val

    if not os.path.exists(existing_file):
        if "Est. Frequency" in new_df.columns:
            new_df["Est. Frequency"] = new_df["Est. Frequency"].apply(remap_frequency)
        new_df.to_csv(existing_file, index=False)
        return

    existing_df = pd.read_csv(existing_file)
    existing_df.set_index("Ticker", inplace=True)
    new_df.set_index("Ticker", inplace=True)

    # Ensure critical columns exist
    if "Last Updated" not in existing_df.columns:
        existing_df["Last Updated"] = pd.NA
    if "Source" not in existing_df.columns:
        existing_df["Source"] = "FMP"

    freq_strings = {"Weekly", "Monthly", "Quarterly", "Semi-Annually", "Annually"}
    invalid_values = ("", "N/A", None, 0, float('nan'), pd.NaT)

    # Fields that should only be overwritten if 0 or missing
    manual_protect_fields = [
        "EPS", "Payout Ratio", "Beta", "Div History (yrs)",
        "5Y Growth Rate (%)", "Debt/Equity"
    ]
    # Fields like Frequency, Ex-Dividend Date, Payout Date
    update_if_zero_fields = ["Est. Frequency", "Ex-Dividend Date", "Payout Date"]

    for ticker in new_df.index:
        if ticker not in existing_df.index:
            existing_df.loc[ticker] = new_df.loc[ticker]
            if "Est. Frequency" in existing_df.columns:
                existing_df.at[ticker, "Est. Frequency"] = remap_frequency(existing_df.at[ticker, "Est. Frequency"])
            continue

        for col in new_df.columns:
            new_val = new_df.at[ticker, col]
            current_val = existing_df.at[ticker, col] if col in existing_df.columns else None

            # Always update Continuation Prob and Last Updated
            if col in ["Continuation Prob (%)", "Last Updated"]:
                existing_df.at[ticker, col] = new_val
                continue

            # For manual-protected fields, only update if current is 0, N/A, nan, or missing
            if col in manual_protect_fields:
                if pd.isna(current_val) or str(current_val).strip().upper() in ("N/A", "", "NONE", "NAN", "0", "0.0"):
                    existing_df.at[ticker, col] = new_val
                continue

            # For frequency/date fields, only update if current is 0, empty, or missing
            if col in update_if_zero_fields:
                if pd.isna(current_val) or str(current_val).strip() in ("", "0", "0.0", "N/A", "nan", "None"):
                    existing_df.at[ticker, col] = new_val
                continue

            # For all other fields, update if new_val is not missing and different
            if not pd.isna(new_val) and str(new_val) != str(current_val):
                existing_df.at[ticker, col] = new_val

    # Enforce string frequency before saving
    if "Est. Frequency" in existing_df.columns:
        existing_df["Est. Frequency"] = existing_df["Est. Frequency"].apply(remap_frequency)

    existing_df.reset_index(inplace=True)
    existing_df.to_csv(existing_file, index=False)
    print(f"🔧 Merged fresh screen results into '{existing_file}' and updated changed fields as per manual rules.")

                        # ***** load portfolio tickers from Excel for personal portfolio *****

def load_portfolio_tickers_from_excel(file_path="dividend_stocks.xlsx"):
    df = pd.read_excel(file_path, usecols=[0], skiprows=1, header=None)
    tickers = df[0].dropna().astype(str).str.upper().tolist()
    return tickers

def auto_retrain_if_needed():
    """Retrain the model if it's older than RETRAIN_INTERVAL_DAYS."""
    if not os.path.exists(MODEL_PATH):
        print("🔄 Model not found, retraining...")
        retrain_model()
        return
    last_modified = os.path.getmtime(MODEL_PATH)
    days_since = (time.time() - last_modified) / (60 * 60 * 24)
    if days_since > RETRAIN_INTERVAL_DAYS:
        print(f"🔄 Model is {days_since:.1f} days old, retraining...")
        retrain_model()
    else:
        print(f"✅ Model is up to date ({days_since:.1f} days old).")

def retrain_model():
    df_holdings = pd.read_csv("scored_my_holdings.csv")
    df_candidates = pd.read_csv("scored_candidates.csv")
    df_train = pd.concat([df_holdings, df_candidates], ignore_index=True)
    train_continuity_model(df_train, model_path=MODEL_PATH)
    print("✅ Model retrained and saved.")

# Call this at the start of your main script

# ========== Run App ==========

if __name__ == "__main__":
    import tkinter as tk
    splash = tk.Tk()
    splash.title("Loading Dividend Screener...")
    splash.geometry("400x120")
    splash.configure(bg="#b3e0ff")  # Light blue background
    splash.attributes("-topmost", True)  # Always on top
    label = tk.Label(
        splash,
        text="Dividend Screener is starting...\nPlease wait...",
        font=("Segoe UI", 16, "bold"),
        fg="#0a2463",  # Deep blue text for high contrast
        bg="#b3e0ff",
        pady=30
    )
    label.pack(expand=True, fill="both")
    splash.update()

    auto_retrain_if_needed()

    print("🏁 Starting personal portfolio first...")

    # Step 0: Remove any tickers from scored_my_holdings.csv that are no longer in dividend_stocks.xlsx
    excel_tickers = set(load_portfolio_tickers_from_excel())
    scored_file = "scored_my_holdings.csv"
    if os.path.exists(scored_file):
        df_scored = pd.read_csv(scored_file)
        if "Ticker" in df_scored.columns:
            before = len(df_scored)
            df_scored = df_scored[df_scored["Ticker"].astype(str).str.upper().isin(excel_tickers)]
            after = len(df_scored)
            if after != before:
                print(f"🧹 Removed {before-after} tickers from scored_my_holdings.csv not in Excel.")
                df_scored.to_csv(scored_file, index=False)

    # Step 1: Load Think or Swim leftovers, or from Excel if none
    if os.path.exists("thinkorswim_leftovers.json"):
        print("📦 Resuming leftover Thinkorswim tickers from yesterday...")
        with open("thinkorswim_leftovers.json", "r") as f:
            tos_tickers = json.load(f)
        os.remove("thinkorswim_leftovers.json")
    else:
        tos_tickers = list(excel_tickers)

    # Step 2: Process and score as many holdings as possible (except manual)
    leftover = []
    processed = []
    for i, ticker in enumerate(tos_tickers, 1):
        print(f"[{i}/{len(tos_tickers)}] Processing {ticker}...")
        try:
            feature_df = build_feature_dataframe([ticker])
            # --- ENSURE ALL FIELDS ARE NUMERIC AND FILLED ---
            required_cols = [
                "Yield Est (%)", "EPS", "Payout Ratio", "Beta",
                "Div History (yrs)", "5Y Growth Rate (%)", "Debt/Equity"
            ]
            for col in required_cols:
                if col not in feature_df.columns:
                    feature_df[col] = 0.0
                feature_df[col] = pd.to_numeric(feature_df[col], errors="coerce").fillna(0.0)
            # ------------------------------------------------
            if not feature_df.empty:
                scored_df = predict_dividend_continuity(feature_df)
                merge_new_screen_with_existing(scored_file, scored_df)
            else:
                print(f"⚠️ No data for {ticker}, skipping.")
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
        # Check FMP call limit after each ticker
        if fmp_calls >= MAX_FMP_CALLS:
            print(f"🚧 FMP rate limit hit at {fmp_calls} calls.")
            leftover = tos_tickers[i:]  # Remaining tickers to process tomorrow
            break

    # Step 2.5: Save leftovers for tomorrow
    if leftover:
        with open("thinkorswim_leftovers.json", "w") as f:
            json.dump(leftover, f)
        print(f"💾 Saved {len(leftover)} leftover tickers for tomorrow.")
    elif os.path.exists("thinkorswim_leftovers.json"):
        os.remove("thinkorswim_leftovers.json")

    # Step 2.6: Always launch GUI with most recent holdings
    if os.path.exists(scored_file):
        df = pd.read_csv(scored_file)
        numeric_fields = [
            "EPS", "Payout Ratio", "Beta", "Div History (yrs)",
            "5Y Growth Rate (%)", "Debt/Equity"
        ]
        for col in numeric_fields:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        if "Est. Frequency" in df.columns:
            df["Est. Frequency"] = df["Est. Frequency"].apply(remap_frequency)
        try:
            splash.destroy()
        except:
            pass
        launch_dividend_gui(df, source_file=scored_file)
    else:
        try:
            splash.destroy()
        except:
            pass
        print("⚠️ No portfolio data found to launch GUI.")

    # === ADD THIS BLOCK TO PROCESS THINK OR SWIM CANDIDATES AFTER PORTFOLIO ===
    print("\n🏁 Now screening Think or Swim candidates...")

    # Load leftovers or from input CSV
    if os.path.exists("pending_tickers.json"):
        print("📦 Resuming leftover candidates from yesterday...")
        with open("pending_tickers.json", "r") as f:
            candidate_tickers = json.load(f)
        os.remove("pending_tickers.json")
    else:
        candidate_df = pd.read_csv(INPUT_CSV)
        candidate_tickers = candidate_df.iloc[:, 0].dropna().astype(str).str.upper().tolist()


    # --- PURGE: Only keep tickers that pay at least 12 times a year (monthly or 12+) ---
    print("\n🔎 Purging candidate tickers to only those with 12+ payouts/year...")
    filtered_tickers = []
    for ticker in candidate_tickers:
        try:
            feature_df = build_feature_dataframe([ticker])
            if not feature_df.empty:
                est_freq = feature_df.iloc[0].get("Est. Frequency", "")
                # Accept if frequency is numeric and >= 12, or string 'monthly' (case-insensitive)
                try:
                    freq_num = int(est_freq)
                except Exception:
                    freq_num = None
                if (freq_num is not None and freq_num >= 12) or (str(est_freq).strip().lower() == "monthly"):
                    filtered_tickers.append(ticker)
                else:
                    print(f"⏩ {ticker} purged: Est. Frequency = {est_freq}")
            else:
                print(f"⚠️ No data for {ticker}, skipping.")
        except Exception as e:
            print(f"❌ Error checking {ticker}: {e}")
    print(f"✅ {len(filtered_tickers)} tickers remain after purge.")
    candidate_tickers = filtered_tickers

    leftover = []
    for i, ticker in enumerate(candidate_tickers, 1):
        print(f"[{i}/{len(candidate_tickers)}] Processing {ticker}...")
        try:
            feature_df = build_feature_dataframe([ticker])
            if not feature_df.empty:
                scored_df = predict_dividend_continuity(feature_df)
                # --- FILTER: Only keep rows that meet your criteria ---
                filtered = scored_df.copy()

                # Ensure Est. Frequency is string for filtering
                filtered["Est. Frequency"] = filtered["Est. Frequency"].astype(str).str.strip().str.lower()

                filtered = filtered[
                    (pd.to_numeric(filtered["Yield Est (%)"], errors="coerce").fillna(0) >= 12) &
                    (pd.to_numeric(filtered["Div History (yrs)"], errors="coerce").fillna(0) >= 1) &
                    (filtered["EPS"].astype(str).str.upper() != "N/A") &
                    (pd.to_numeric(filtered["EPS"], errors="coerce").fillna(0) > 0) &
                    (
                        (filtered["Est. Frequency"] == "monthly") |
                        (filtered["Est. Frequency"] == "12")
                    )
                ]
                if not filtered.empty:
                    merge_new_screen_with_existing("scored_candidates.csv", filtered)
                else:
                    print(f"⏩ {ticker} did not meet screening criteria, not added.")
            else:
                print(f"⚠️ No data for {ticker}, skipping.")
        except Exception as e:
            print(f"❌ Error processing {ticker}: {e}")
        if fmp_calls >= MAX_FMP_CALLS:
            print(f"🚧 FMP rate limit hit at {fmp_calls} calls.")
            leftover = candidate_tickers[i:]
            break

    if leftover:
        with open("pending_tickers.json", "w") as f:
            json.dump(leftover, f)
        print(f"💾 Saved {len(leftover)} leftover candidates for tomorrow.")
    elif os.path.exists("pending_tickers.json"):
        os.remove("pending_tickers.json")

    # Show GUI for candidates
if os.path.exists("scored_candidates.csv"):
    df = pd.read_csv("scored_candidates.csv")
        # --- FILTER: Only keep monthly payers in the file and GUI ---
    df["Est. Frequency"] = df["Est. Frequency"].astype(str).str.strip().str.lower()
    df = df[
        (df["Est. Frequency"] == "monthly") |
        (df["Est. Frequency"] == "12")
    ]
    # Overwrite file with only monthly payers
    df.to_csv("scored_candidates.csv", index=False)
    # --- END FILTER ---
    # --- NEW FILTER: Only show tickers with Yield Est (%) >= 15% in the GUI ---
    df["Yield Est (%)"] = pd.to_numeric(df["Yield Est (%)"], errors="coerce")
    df = df[df["Yield Est (%)"] >= 15]
    # --- END NEW FILTER ---
    numeric_fields = [
        "EPS", "Payout Ratio", "Beta", "Div History (yrs)",
        "5Y Growth Rate (%)", "Debt/Equity"
    ]
    for col in numeric_fields:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
    if "Est. Frequency" in df.columns:
        df["Est. Frequency"] = df["Est. Frequency"].apply(remap_frequency)
    try:
        splash.destroy()
    except:
        pass
    launch_dividend_gui(df, source_file="scored_candidates.csv")
else:
    try:
        splash.destroy()
    except:
        pass
    print("⚠️ No candidate data found to launch GUI.")
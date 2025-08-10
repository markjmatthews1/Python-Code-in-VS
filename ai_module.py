import pandas as pd
from data_provider import get_yahoo_intraday
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
import joblib  # For saving/loading models
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import os
from datetime import datetime, timedelta
from schwab_data import fetch_minute_bars_for_range
from schwab_data import fetch_minute_bars_for_range, fetch_daily_bars_for_range
import numpy as np
import argparse
import json
from dateutil import parser as dateparser
import csv
from datetime import date
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import seaborn as sns



def load_news_cache(news_path="news_cache.json"):
    with open(news_path, "r", encoding="utf-8") as f:
        news_raw = json.load(f)
    # Assume news_raw is a list of dicts with keys: ticker, datetime, sentiment, headline, etc.
    news_list = []
    for item in news_raw:
        # Parse datetime if needed
        dt = item.get("datetime")
        if isinstance(dt, str):
            dt = dateparser.parse(dt)
        news_list.append({
            "Ticker": item.get("ticker", "").upper(),
            "Datetime": dt,
            "Sentiment": float(item.get("sentiment", 0)),
            "Headline": item.get("headline", "")
        })
    news_df = pd.DataFrame(news_list)
    news_df["Datetime"] = pd.to_datetime(news_df["Datetime"])
    return news_df

def load_whale_cache(whale_path="whale_cache.json"):
    """
    Loads whale (large trade) data from a JSON file and returns a DataFrame.
    Assumes each record has at least: ticker, datetime, size, direction (buy/sell), and optionally price.
    """
    with open(whale_path, "r", encoding="utf-8") as f:
        whale_raw = json.load(f)
    whale_list = []
    for item in whale_raw:
        dt = item.get("datetime")
        if isinstance(dt, str):
            dt = dateparser.parse(dt)
        whale_list.append({
            "Ticker": item.get("ticker", "").upper(),
            "Datetime": dt,
            "Size": float(item.get("size", 0)),
            "Direction": str(item.get("direction", "")).lower(),  # "buy" or "sell"
            "Price": float(item.get("price", 0)) if "price" in item else None
        })
    whale_df = pd.DataFrame(whale_list)
    whale_df["Datetime"] = pd.to_datetime(whale_df["Datetime"])
    return whale_df

#   ***** How to call this module from the command line with a ticker *****
#                      ***** python ai_module.py --ticker TSLA *****

def load_news_cache(news_path="news_cache.json"):
    with open(news_path, "r", encoding="utf-8") as f:
        news_raw = json.load(f)
    # Assume news_raw is a list of dicts with keys: ticker, datetime, sentiment, headline, etc.
    news_list = []
    for item in news_raw:
        # Parse datetime if needed
        dt = item.get("datetime")
        if isinstance(dt, str):
            dt = dateparser.parse(dt)
        news_list.append({
            "Ticker": item.get("ticker", "").upper(),
            "Datetime": dt,
            "Sentiment": float(item.get("sentiment", 0)),
            "Headline": item.get("headline", "")
        })
    news_df = pd.DataFrame(news_list)
    news_df["Datetime"] = pd.to_datetime(news_df["Datetime"])
    return news_df

def load_quiver_cache(cache_path):
    if not os.path.exists(cache_path):
        return pd.DataFrame()
    with open(cache_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    df = pd.DataFrame(data)
    # Standardize date columns
    for col in ["TransactionDate", "reportDate", "Date"]:
        if col in df.columns:
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

def load_trade_log(path="trade_log.xlsx"):
    """
    Loads your manually tracked trades from Excel and adds a binary outcome label.
    """
    df = pd.read_excel(path)
    df["Open Datetime"] = pd.to_datetime(df["Open Datetime"])
    df["Close Datetime"] = pd.to_datetime(df["Close Datetime"])
    df["Trade Outcome"] = df["Profit/Loss"].apply(lambda x: 1 if x > 0 else 0)
    return df

def compute_rsi(series, period=14):
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def compute_macd(series, fast=12, slow=26, signal=9):
    ema_fast = series.ewm(span=fast, min_periods=fast).mean()
    ema_slow = series.ewm(span=slow, min_periods=slow).mean()
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal, min_periods=signal).mean()
    return macd, macd_signal

def update_historical_daily_data(tickers, filename="historical_daily_data.csv", years_back=5):
    """
    Ensures historical_daily_data.csv contains as much daily data as possible for each ticker.
    Downloads only missing data and appends it.
    """
    if os.path.exists(filename):
        df_full = pd.read_csv(filename, parse_dates=["Datetime"])
    else:
        df_full = pd.DataFrame()

    for ticker in tickers:
        print(f"Updating daily historical data for {ticker}...")
        # Always fetch the full range for now, since Schwab returns all available data for the period
        new_data = fetch_daily_bars_for_range(ticker, years_back=years_back)
        if new_data is not None and not new_data.empty:
            print(f"Fetched {len(new_data)} new daily rows for {ticker}")
            df_full = pd.concat([df_full, new_data], ignore_index=True)
            df_full = df_full.drop_duplicates(subset=["Datetime", "Ticker"])
        else:
            print(f"No new daily data for {ticker}")

    if not df_full.empty:
        df_full = df_full.sort_values(["Ticker", "Datetime"])
        df_full.to_csv(filename, index=False)
        print(f"Saved updated daily historical data to {filename}")
    else:
        print("No daily historical data available to save.")
    return df_full

def update_historical_minute_data(tickers, filename="historical_minute_data.csv", days_back=5):
    """
    Ensures historical_minute_data.csv contains as much minute data as possible for each ticker.
    Downloads only missing data and appends it.
    """
    if os.path.exists(filename):
        df_full = pd.read_csv(filename, parse_dates=["Datetime"])
    else:
        df_full = pd.DataFrame()

    for ticker in tickers:
        print(f"Updating minute historical data for {ticker}...")
        if not df_full.empty and ticker in df_full["Ticker"].unique():
            last_dt = df_full[df_full["Ticker"] == ticker]["Datetime"].max()
            last_dt = pd.to_datetime(last_dt)  # Ensure datetime type
            start_dt = last_dt + timedelta(minutes=1)
        else:
            start_dt = datetime.now() - timedelta(days=days_back)
        end_dt = datetime.now()

        new_data = fetch_minute_bars_for_range(ticker, start_dt, end_dt)
        if new_data is not None and not new_data.empty:
            print(f"Fetched {len(new_data)} new minute rows for {ticker}")
            df_full = pd.concat([df_full, new_data], ignore_index=True)
            df_full = df_full.drop_duplicates(subset=["Datetime", "Ticker"])
        else:
            print(f"No new minute data for {ticker}")

    if not df_full.empty:
        df_full = df_full.sort_values(["Ticker", "Datetime"])
        df_full.to_csv(filename, index=False)
        print(f"Saved updated minute historical data to {filename}")
    else:
        print("No minute historical data available to save.")
    return df_full

def extract_features_from_historical(df, news_df=None, whale_df=None, congress_df=None, inst_df=None):
    """
    Computes features for each ticker from a historical DataFrame.
    Optionally merges in news, whale, congress, and institutional features.
    """
    features = []
    grouped = df.groupby("Ticker")
    for ticker, tdf in grouped:
        tdf["Datetime"] = pd.to_datetime(tdf["Datetime"], errors="coerce")
        tdf = tdf.sort_values("Datetime")
        tdf["sma_5"] = tdf["Close"].rolling(window=5).mean()
        tdf["sma_20"] = tdf["Close"].rolling(window=20).mean()
        tdf["ema_5"] = tdf["Close"].ewm(span=5).mean()
        tdf["ema_20"] = tdf["Close"].ewm(span=20).mean()
        tdf["rsi_14"] = compute_rsi(tdf["Close"], period=14)
        tdf["returns"] = tdf["Close"].pct_change()
        tdf["bb_upper"] = tdf["Close"].rolling(window=20).mean() + 2 * tdf["Close"].rolling(window=20).std()
        tdf["bb_lower"] = tdf["Close"].rolling(window=20).mean() - 2 * tdf["Close"].rolling(window=20).std()
        tdf["vol_sma_20"] = tdf["Volume"].rolling(window=20).mean()
        macd, macd_signal = compute_macd(tdf["Close"])
        tdf["macd"] = macd
        tdf["macd_signal"] = macd_signal
        for idx, row in tdf.iterrows():
            feat = {
                "ticker": ticker,
                "datetime": row["Datetime"],
                "open": row["Open"],
                "high": row["High"],
                "low": row["Low"],
                "close": row["Close"],
                "volume": row["Volume"],
                "sma_5": row["sma_5"],
                "sma_20": row["sma_20"],
                "ema_5": row["ema_5"],
                "ema_20": row["ema_20"],
                "rsi_14": row["rsi_14"],
                "returns": row["returns"],
                "bb_upper": row["bb_upper"],
                "bb_lower": row["bb_lower"],
                "vol_sma_20": row["vol_sma_20"],
                "macd": row["macd"],
                "macd_signal": row["macd_signal"],
            }
            # --- Add news features ---
            if news_df is not None:
                recent_news = news_df[
                    (news_df["Ticker"] == ticker) &
                    (news_df["Datetime"] <= row["Datetime"]) &
                    (news_df["Datetime"] > row["Datetime"] - pd.Timedelta(minutes=60))
                ]
                feat["news_sentiment_mean"] = recent_news["Sentiment"].mean() if not recent_news.empty else 0
                feat["news_count"] = len(recent_news)
            # --- Add whale features ---
            if whale_df is not None:
                recent_whales = whale_df[
                    (whale_df["Ticker"] == ticker) &
                    (whale_df["Datetime"] <= row["Datetime"]) &
                    (whale_df["Datetime"] > row["Datetime"] - pd.Timedelta(minutes=60))
                ]
                feat["whale_trade_count"] = len(recent_whales)
                feat["whale_volume"] = recent_whales["Size"].sum() if not recent_whales.empty else 0
                feat["whale_buy_count"] = (recent_whales["Direction"] == "buy").sum()
                feat["whale_sell_count"] = (recent_whales["Direction"] == "sell").sum()
                feat["whale_buy_volume"] = recent_whales[recent_whales["Direction"] == "buy"]["Size"].sum() if not recent_whales.empty else 0
                feat["whale_sell_volume"] = recent_whales[recent_whales["Direction"] == "sell"]["Size"].sum() if not recent_whales.empty else 0
            # --- Add Quiver Congress features ---
            if congress_df is not None and not congress_df.empty:
                recent_congress = congress_df[
                    (congress_df["Ticker"] == ticker) &
                    (congress_df["TransactionDate"] <= row["Datetime"]) &
                    (congress_df["TransactionDate"] > row["Datetime"] - pd.Timedelta(days=30))
                ]
                feat["congress_trade_count_30d"] = len(recent_congress)
                feat["congress_last_type"] = recent_congress["Transaction"].iloc[-1] if not recent_congress.empty and "Transaction" in recent_congress.columns else ""
            # --- Add Quiver Institutional features ---
            if inst_df is not None and not inst_df.empty:
                recent_inst = inst_df[
                    (inst_df["Ticker"] == ticker) &
                    (inst_df["Date"] <= row["Datetime"]) &
                    (inst_df["Date"] > row["Datetime"] - pd.Timedelta(days=30))
                ]
                feat["inst_trade_count_30d"] = len(recent_inst)
                feat["inst_last_type"] = recent_inst["Transaction"].iloc[-1] if not recent_inst.empty and "Transaction" in recent_inst.columns else ""
            features.append(feat)
    return pd.DataFrame(features).set_index(["ticker", "datetime"])


def label_barrier_outcomes(df, target_pct=0.02, stop_pct=0.01, max_lookahead=30):
    """
    For each row, label as 1 if target is hit before stop, 0 if stop is hit first.
    Assumes df is sorted by ticker and datetime.
    """
    df = df.sort_values(["ticker", "datetime"]).reset_index(drop=True)
    labels = []
    for idx, row in df.iterrows():
        entry = row["close"]
        ticker = row["ticker"]
        # Look ahead up to max_lookahead bars
        future = df[(df["ticker"] == ticker) & (df.index > idx)].head(max_lookahead)
        win = False
        loss = False
        for _, fut in future.iterrows():
            price = fut["close"]
            if price >= entry * (1 + target_pct):
                win = True
                break
            if price <= entry * (1 - stop_pct):
                loss = True
                break
        if win:
            labels.append(1)
        elif loss:
            labels.append(0)
        else:
            labels.append(np.nan)  # Could not determine
    df["label"] = labels
    return df.dropna(subset=["label"])

def normalize_features(df):
    """
    Normalizes numeric features (excluding label and non-numeric columns).
    """
    from sklearn.preprocessing import StandardScaler
    features = df.select_dtypes(include=["float64", "int64"]).columns.difference(["label"])
    scaler = StandardScaler()
    df[features] = scaler.fit_transform(df[features])
    return df

def train_ranking_model(X, y):
    """
    Trains a simple classifier (e.g., RandomForest).
    """
    from sklearn.ensemble import RandomForestClassifier
    clf = RandomForestClassifier(n_estimators=100, random_state=42)
    clf.fit(X, y)
    return clf

def extract_features(tickers, period="2d", interval="1m"):
    """
    Fetches the latest minute data for each ticker and computes features.
    Returns a DataFrame ready for prediction.
    """
    import pandas as pd
    from schwab_data import fetch_minute_bars_for_range

    all_features = []
    for ticker in tickers:
        end_dt = datetime.now()
        start_dt = end_dt - timedelta(days=2)
        df = fetch_minute_bars_for_range(ticker, start_dt, end_dt)
        if df.empty or len(df) < 26:  # Need enough data for MACD
            continue
        df["Datetime"] = pd.to_datetime(df["Datetime"], errors="coerce")
        df = df.sort_values("Datetime")
        df["sma_5"] = df["Close"].rolling(window=5).mean()
        df["sma_20"] = df["Close"].rolling(window=20).mean()
        df["ema_5"] = df["Close"].ewm(span=5).mean()
        df["ema_20"] = df["Close"].ewm(span=20).mean()
        df["rsi_14"] = compute_rsi(df["Close"], period=14)
        df["returns"] = df["Close"].pct_change()
        df["bb_upper"] = df["Close"].rolling(window=20).mean() + 2 * df["Close"].rolling(window=20).std()
        df["bb_lower"] = df["Close"].rolling(window=20).mean() - 2 * df["Close"].rolling(window=20).std()
        df["vol_sma_20"] = df["Volume"].rolling(window=20).mean()
        macd, macd_signal = compute_macd(df["Close"])
        df["macd"] = macd
        df["macd_signal"] = macd_signal
        latest = df.iloc[-1]
        prev_close = df["Close"].iloc[-2]
        feat = {
            "ticker": ticker,
            "open": latest["Open"],
            "high": latest["High"],
            "low": latest["Low"],
            "close": latest["Close"],
            "volume": latest["Volume"],
            "sma_5": latest["sma_5"],
            "sma_20": latest["sma_20"],
            "ema_5": latest["ema_5"],
            "ema_20": latest["ema_20"],
            "rsi_14": latest["rsi_14"],
            "returns": latest["returns"],
            "bb_upper": latest["bb_upper"],
            "bb_lower": latest["bb_lower"],
            "vol_sma_20": latest["vol_sma_20"],
            "macd": latest["macd"],
            "macd_signal": latest["macd_signal"],
            "prev_close": prev_close
        }
        all_features.append(feat)
    if all_features:
        return pd.DataFrame(all_features)
    else:
        return pd.DataFrame()

def get_ticker_ranking(live_tickers, model_path="ai_model.pkl"):
    """
    Loads the saved model and predicts/ranks live tickers using real-time data.
    """
    import joblib
    clf = joblib.load(model_path)
    live_df = extract_features(live_tickers, period="2d", interval="1m")  # Adjust as needed
    if live_df.empty:
        print("No live data available for ranking.")
        return pd.DataFrame()
    # (Optional) Use only the latest row per ticker
    latest = live_df.groupby("ticker").tail(1)
    X_live = latest.drop(columns=["label", "ticker", "datetime"], errors="ignore")
    predictions = clf.predict(X_live)
    latest["prediction"] = predictions
    return latest[["ticker", "prediction"]]

def print_trade_recommendations(tickers, model_path="ai_model.pkl", prob_threshold=0.6):
    """
    For each ticker, print the probability of going up, entry/exit suggestion,
    or 'No trade' if probability is too low.
    """
    import joblib

    # You need to implement this to get the latest features for each ticker
    live_df = extract_features(tickers, period="2d", interval="1m")
    if live_df.empty:
        print("No live data available for trade recommendations.")
        return

    # Use only the latest row per ticker
    latest = live_df.groupby("ticker").tail(1)
    X_live = latest.drop(columns=["label", "ticker", "datetime"], errors="ignore")

    clf = joblib.load(model_path)
    probs = clf.predict_proba(X_live)

    print("\nTrade Recommendations:")
    for i, ticker in enumerate(latest["ticker"]):
        prob_up = probs[i][1]  # Probability of class 1 (going up)
        current_price = latest.iloc[i]["close"]
        if prob_up >= prob_threshold:
            # Example: set a 2% target and 1% stop
            entry = current_price
            target = round(entry * 1.02, 2)
            stop = round(entry * 0.99, 2)
            print(f"{ticker}: Probability up = {prob_up:.2%} | Entry: {entry:.2f} | Target: {target:.2f} | Stop: {stop:.2f}")
        else:
            print(f"{ticker}: Probability up = {prob_up:.2%} | No trade for {ticker} today (probability below threshold)")

def log_prediction(ticker, entry_time, features, predicted_prob, outcome=None, log_path="prediction_log.csv"):
    """
    Logs model prediction, features, and (optional) outcome for later review/training.
    """
    row = {
        "Ticker": ticker,
        "Datetime": entry_time.strftime("%Y-%m-%d %H:%M:%S"),
        "Predicted_Prob": predicted_prob,
        "Outcome": outcome if outcome is not None else "",
        **features
    }

    # Write header only if file doesn't exist
    write_header = not os.path.exists(log_path)
    with open(log_path, "a", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=row.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def retrain_model_from_feedback(
    prediction_log_path="prediction_log.csv",
    trade_log_path="trade_log.xlsx",
    model_output_path="ai_model_updated.pkl"
):
        # Load prediction log
    preds_df = pd.read_csv(prediction_log_path, parse_dates=["Datetime"])
    trade_df = pd.read_excel(trade_log_path, parse_dates=["Open Datetime"])

    # Clean casing
    preds_df["Ticker"] = preds_df["Ticker"].str.upper()
    trade_df["Ticker"] = trade_df["Ticker"].str.upper()

    matched = []
    for _, trade in trade_df.iterrows():
        tkr = trade["Ticker"]
        open_time = trade["Open Datetime"]
        outcome = trade["Profit/Loss"]
        label = 1 if outcome > 0 else 0

        # Match predictions within ±10 min of entry
        candidates = preds_df[(preds_df["Ticker"] == tkr) & 
                              (abs(preds_df["Datetime"] - open_time) <= pd.Timedelta(minutes=10))]
        if not candidates.empty:
            row = candidates.iloc[0].drop(["Ticker", "Datetime", "Predicted_Prob", "Outcome"])
            feat = row.to_dict()
            matched.append({**feat, "label": label})

    if not matched:
        print("No matching trades found for retraining.")
        return

    df_train = pd.DataFrame(matched)
    features = df_train.drop(columns=["label"])
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(features)
    y = df_train["label"]

    # Train model
    clf = RandomForestClassifier(n_estimators=200, max_depth=6, random_state=42)
    clf.fit(X_scaled, y)
    
    # Show feature importance
    feature_names = features.columns.tolist()
    # Pass trade_df for strategy breakdown
    show_feature_importance(clf, feature_names, trade_df)

    joblib.dump(clf, model_output_path)

    # Performance stats
    preds = clf.predict(X_scaled)
    acc = accuracy_score(y, preds)
    report = classification_report(y, preds, output_dict=True)
    class_0 = report["0"]
    class_1 = report["1"]

    plot_accuracy_over_time("prediction_log.csv", "trade_log.xlsx")
    plot_cumulative_pl("trade_log.xlsx")
    
    # --- GUI Display ---
    root = tk.Tk()
    root.title("Retraining Performance Summary")
    root.geometry("420x250")
    root.resizable(False, False)

    summary = f"""
    🔄 Model Retrained: {len(df_train)} Samples
    ✅ Accuracy: {acc:.2%}
    📊 Class 0 (Losses): Precision {class_0['precision']:.2f}, Recall {class_0['recall']:.2f}
    📈 Class 1 (Wins): Precision {class_1['precision']:.2f}, Recall {class_1['recall']:.2f}
    💾 Saved To: {model_output_path}
    """

    label = ttk.Label(root, text=summary.strip(), justify="left", font=("Segoe UI", 10), anchor="w")
    label.pack(padx=20, pady=20)
    button = ttk.Button(root, text="Close", command=root.destroy)
    button.pack(pady=10)

    root.mainloop()

def show_feature_importance(model, feature_names, trade_df=None):
    """
    Plots a bar chart of feature importance from a trained model.
    """
    importances = model.feature_importances_
    sorted_idx = importances.argsort()[::-1]
    sorted_features = [feature_names[i] for i in sorted_idx]
    sorted_importances = importances[sorted_idx]

    plt.figure(figsize=(10, 6))
    sns.barplot(x=sorted_importances, y=sorted_features, palette="viridis")
    plt.title("Feature Importance (Random Forest)", fontsize=14)
    plt.xlabel("Importance Score")
    plt.tight_layout()
    plt.show()

    # Strategy accuracy breakdown
    if trade_df is not None and "Strategy" in trade_df.columns:
        trade_df["label"] = trade_df["Profit/Loss"].apply(lambda x: 1 if x > 0 else 0)
        strat_acc = trade_df.groupby("Strategy")["label"].mean().sort_values(ascending=False)

        plt.figure(figsize=(9, 5))
        strat_acc.plot(kind="bar", color="skyblue")
        plt.title("📊 Accuracy by Strategy Tag")
        plt.ylabel("Win Rate")
        plt.xlabel("Strategy")
        plt.ylim(0, 1)
        plt.grid(True)
        plt.tight_layout()
        plt.show()

def plot_accuracy_over_time(prediction_log_path="prediction_log.csv", trade_log_path="trade_log.xlsx"):
    """
    Plots daily win/loss accuracy based on matched trades and predictions.
    """
    
    preds_df = pd.read_csv(prediction_log_path, parse_dates=["Datetime"])
    trades_df = pd.read_excel(trade_log_path, parse_dates=["Open Datetime"])

    preds_df["Ticker"] = preds_df["Ticker"].str.upper()
    trades_df["Ticker"] = trades_df["Ticker"].str.upper()

    outcomes = []
    for _, trade in trades_df.iterrows():
        tkr = trade["Ticker"]
        time = trade["Open Datetime"]
        label = 1 if trade["Profit/Loss"] > 0 else 0
        match = preds_df[(preds_df["Ticker"] == tkr) & (abs(preds_df["Datetime"] - time) <= pd.Timedelta(minutes=10))]
        if not match.empty:
            trade_day = time.date()
            outcomes.append({"date": trade_day, "label": label})

    if not outcomes:
        print("No matches found for accuracy tracking.")
        return

    df_acc = pd.DataFrame(outcomes)
    daily = df_acc.groupby("date")["label"].mean()

    plt.figure(figsize=(8, 5))
    plt.plot(daily.index, daily.values, marker="o", linewidth=2)
    plt.title("🔍 Daily Win Rate")
    plt.xlabel("Trade Date")
    plt.ylabel("Win Accuracy")
    plt.ylim(0, 1)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def plot_cumulative_pl(trade_log_path="trade_log.xlsx"):
    """
    Plots cumulative profit/loss over time for Real and Paper trades separately.
    """
    import pandas as pd
    import matplotlib.pyplot as plt

    df = pd.read_excel(trade_log_path, parse_dates=["Close Datetime"])
    df = df.sort_values("Close Datetime")

    # Validate 'Type' column exists
    if "Type" not in df.columns:
        print("Missing 'Type' column in trade log. Cannot segment Real vs. Paper trades.")
        return

    # Split and compute cumulative P/L
    df["Cumulative PL"] = df["Profit/Loss"].cumsum()
    real_df = df[df["Type"].str.lower() == "real"].copy()
    paper_df = df[df["Type"].str.lower() == "paper"].copy()

    real_df["Cumulative PL"] = real_df["Profit/Loss"].cumsum()
    paper_df["Cumulative PL"] = paper_df["Profit/Loss"].cumsum()

    # Plot both lines
    plt.figure(figsize=(9, 6))
    if not real_df.empty:
        plt.plot(real_df["Close Datetime"], real_df["Cumulative PL"], label="Real Trades", color="blue", linewidth=2)
    if not paper_df.empty:
        plt.plot(paper_df["Close Datetime"], paper_df["Cumulative PL"], label="Paper Trades", color="orange", linewidth=2)

    plt.title("📈 Cumulative Profit/Loss Over Time")
    plt.xlabel("Close Datetime")
    plt.ylabel("Cumulative P/L ($)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def get_trade_recommendations(
    tickers,
    model_path="ai_model.pkl",
    prob_threshold=0.55,  # Lowered from 0.6
    return_df=False,
    log_path="prediction_log.csv",
    volatility_settings=None  # New parameter
):
    """
    For each ticker, compute the probability of going up, entry/exit suggestion,
    and a trade recommendation. Returns a DataFrame for further use.
    """
    import joblib
    from config import get_volatility_threshold, AI_PROB_THRESHOLD, AI_TARGET_PERCENT, AI_STOP_PERCENT

    live_df = extract_features(tickers, period="2d", interval="1m")
    if live_df.empty:
        print("No live data available for trade recommendations.")
        return pd.DataFrame() if return_df else None

    # Use only the latest row per ticker
    latest = live_df.groupby("ticker").tail(1)
    X_live = latest.drop(columns=["ticker"], errors="ignore")

    clf = joblib.load(model_path)
    probs = clf.predict_proba(X_live)

    # **IMPROVED: Calibrate probabilities to be more realistic for day trading**
    def calibrate_probability(raw_prob, volatility_ratio):
        """
        Calibrate AI probabilities to be more realistic for day trading.
        High volatility = more uncertainty = lower confidence
        Low volatility = less opportunity = lower confidence
        """
        # Optimal volatility range for day trading ETFs is 0.01-0.03 (1-3%)
        optimal_vol_min = 0.01
        optimal_vol_max = 0.03
        
        if volatility_ratio < optimal_vol_min:
            # Too low volatility - reduce confidence significantly
            confidence_factor = volatility_ratio / optimal_vol_min * 0.7  # Max 70% of original
        elif volatility_ratio > optimal_vol_max:
            # Too high volatility - reduce confidence due to uncertainty
            excess_vol = min(volatility_ratio - optimal_vol_max, 0.05)  # Cap at 5% excess
            confidence_factor = 1 - (excess_vol / 0.05) * 0.3  # Reduce up to 30%
        else:
            # Optimal volatility range - keep most confidence
            confidence_factor = 0.95
        
        # Apply calibration - pull probabilities toward 50% (neutral)
        calibrated = 0.5 + (raw_prob - 0.5) * confidence_factor
        
        # Additional realism: day trading should rarely exceed 75% confidence
        calibrated = min(calibrated, 0.75)
        calibrated = max(calibrated, 0.25)  # Never go below 25%
        
        return calibrated

    results = []
    for i, ticker in enumerate(latest["ticker"]):
        raw_prob_up = probs[i][1]
        current_price = latest.iloc[i]["close"]
        
        # Calculate volatility metrics (use actual volatility from recent returns)
        # Use the returns column that was already calculated in extract_features
        try:
            ticker_returns = live_df[live_df["ticker"] == ticker]["returns"].dropna()
            if len(ticker_returns) > 5:
                # Use standard deviation of returns as volatility measure
                range_pct = ticker_returns.std()
            else:
                # Fallback to single-bar range if insufficient return data
                avg_range = latest.iloc[i]["high"] - latest.iloc[i]["low"] 
                range_pct = avg_range / current_price
        except:
            # Final fallback to single-bar range
            avg_range = latest.iloc[i]["high"] - latest.iloc[i]["low"]
            range_pct = avg_range / current_price
        
        volatility_threshold = get_volatility_threshold(ticker)
        
        # **NEW: Apply probability calibration**
        prob_up = calibrate_probability(raw_prob_up, range_pct)
        
        entry = current_price
        target = round(entry * (1 + AI_TARGET_PERCENT), 2)
        stop = round(entry * (1 - AI_STOP_PERCENT), 2)

        # Debug output
        print(f"🔍 {ticker}: Vol {range_pct:.3f} vs Thresh {volatility_threshold:.3f}")
        print(f"    Raw Prob: {raw_prob_up:.2%} → Calibrated: {prob_up:.2%}")

        # Decision logic
        if range_pct < volatility_threshold:
            recommendation = f"❌ No trade — low volatility ({range_pct:.3f} < {volatility_threshold:.3f})"
        elif prob_up >= AI_PROB_THRESHOLD:
            recommendation = f"🔥 TRADE: Entry {entry:.2f}, Target {target:.2f}, Stop {stop:.2f}"
        else:
            recommendation = f"❌ No trade (prob {prob_up:.2%} < {AI_PROB_THRESHOLD:.2%})"

        # Log prediction for feedback loop
        entry_time = latest.iloc[i]["datetime"] if "datetime" in latest.columns else datetime.now()
        features_to_log = X_live.iloc[i].to_dict()
        log_prediction(ticker, entry_time, features_to_log, prob_up, outcome=None, log_path=log_path)

        results.append({
            "ticker": ticker,
            "probability": prob_up,
            "raw_probability": raw_prob_up,  # Keep original for debugging
            "entry": entry,
            "target": target,
            "stop": stop,
            "recommendation": recommendation,
            "volatility": range_pct,
            "vol_threshold": volatility_threshold
        })

    df_results = pd.DataFrame(results).sort_values("probability", ascending=False)
    
    # **Debug Summary**
    total_tickers = len(results)
    low_vol_filtered = len([r for r in results if "low volatility" in r["recommendation"]])
    low_prob_filtered = len([r for r in results if "probability below threshold" in r["recommendation"]])
    trade_candidates = len([r for r in results if "TRADE:" in r["recommendation"]])
    
    print(f"📊 AI RECOMMENDATION SUMMARY:")
    print(f"   Total tickers: {total_tickers}")
    print(f"   Filtered by volatility: {low_vol_filtered}")
    print(f"   Filtered by probability: {low_prob_filtered}")
    print(f"   🔥 Trade candidates: {trade_candidates}")
    
    if return_df:
        return df_results
    else:
        print("\n🤖 AI Trade Recommendations:")
        for _, row in df_results.iterrows():
            print(f"{row['ticker']}: {row['recommendation']}")
        return df_results

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI Stock Predictor")
    parser.add_argument("--tickers", type=str, help="Comma-separated ticker symbols to analyze (e.g. TSLA,SPY,QQQ)")
    args = parser.parse_args()

    if args.tickers:
        ticker_list = [t.strip().upper() for t in args.tickers.split(",")]
        get_trade_recommendations(ticker_list)
        exit(0)

    # Default tickers for normal pipeline
    tickers = ["AAPL", "AMD", "MSFT"]

    # 1. Update and load daily data (for long-term learning)
    daily_df = update_historical_daily_data(tickers, filename="historical_daily_data.csv", years_back=5)
    print("Loaded daily historical data:", daily_df.shape)

    # 2. Update and load minute data (for recent intraday learning/prediction)
    minute_df = update_historical_minute_data(tickers, filename="historical_minute_data.csv", days_back=5)
    print("Loaded minute historical data:", minute_df.shape)

    # --- Load news cache ---
    news_df = load_news_cache("news_cache.json")
    print("Loaded news data:", news_df.shape)

    whale_df = load_whale_cache("whale_cache.json")
    print("Loaded whale data:", whale_df.shape)

    # --- Load Quiver data ---
    congress_df = load_quiver_cache("quiver_congress_cache.json")
    print("Loaded Quiver Congress data:", congress_df.shape)
    inst_df = load_quiver_cache("quiver_institutional_cache.json")
    print("Loaded Quiver Institutional data:", inst_df.shape)

    # --- Load manual trade outcomes ---
    trade_df = load_trade_log("trade_log.xlsx")
    print("Loaded manual trade outcomes:", trade_df.shape)

    # 3. Extract features from minute data for training, with news
    feat_df = extract_features_from_historical(
    minute_df,
    news_df=news_df,
    whale_df=whale_df,
    congress_df=congress_df,
    inst_df=inst_df
)
    print("Labeled data for training:", feat_df.shape)


def is_retrain_day(day_threshold=1):
    """
    Returns True if today is within the first `day_threshold` days of the month.
    """
    today = date.today()
    return today.day <= day_threshold

if is_retrain_day():
    retrain_model_from_feedback(
        prediction_log_path="prediction_log.csv",
        trade_log_path="trade_log.xlsx",
        model_output_path="ai_model_updated.pkl"
    )
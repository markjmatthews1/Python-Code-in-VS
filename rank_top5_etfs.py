"""
rank_top5_etfs.py

Analysis functions for ETF ranking and dashboarding.
Includes sentiment, whale/institutional/insider activity, news, and support/resistance.
All scoring functions return a 1-5 ranking (1=very bearish, 5=very bullish).
"""

import requests
from datetime import datetime, timedelta, timezone
import pandas as pd

FINNHUB_API_KEY = "d0o631hr01qn5ghnfangd0o631hr01qn5ghnfao0"
NEWS_API_KEY = "7fdd7fe392ff4a9b9e7940a32a055fdb"

# --- News & Sentiment Analysis ---

def fetch_etf_news(etf_symbol, api_key=NEWS_API_KEY, cache=None):
    """
    Fetch news for a given ETF symbol using NewsAPI.
    Uses a cache dict to avoid repeated calls.
    Returns a list of dicts: [{"title": ..., "sentiment": ..., "url": ...}, ...]
    """
    news_cache = cache["news"] if cache and "news" in cache else None
    now = datetime.now(timezone.utc)
    cache_validity = timedelta(hours=1)
    if news_cache is not None and etf_symbol in news_cache:
        cached_time, cached_data = news_cache[etf_symbol]
        if now - cached_time < cache_validity:
            return cached_data

    api_url = f"https://newsapi.org/v2/everything?q={etf_symbol}&language=en&apiKey={api_key}"
    response = requests.get(api_url)
    if response.status_code == 200:
        news_data = response.json()["articles"][:5]
        formatted_news = [
            {
                "title": article["title"],
                "sentiment": analyze_sentiment(article["title"]),
                "url": article["url"]
            }
            for article in news_data
        ]
        if news_cache is not None:
            news_cache[etf_symbol] = (now, formatted_news)
        return formatted_news
    else:
        print(f"❌ News API error for {etf_symbol}: {response.status_code} {response.text}")
        return []

def analyze_sentiment(text):
    """
    Basic sentiment analysis using keywords.
    Returns 'Positive', 'Negative', or 'Neutral'.
    """
    positive_keywords = ["growth", "strong", "bullish", "rising", "beat", "record", "up"]
    negative_keywords = ["drop", "decline", "bearish", "falling", "miss", "down", "warning"]

    sentiment = "Neutral"
    if any(word in text.lower() for word in positive_keywords):
        sentiment = "Positive"
    elif any(word in text.lower() for word in negative_keywords):
        sentiment = "Negative"
    return sentiment

def score_sentiment(sentiment):
    """Convert sentiment string to 1-5 score."""
    if sentiment == "Positive":
        return 5
    elif sentiment == "Negative":
        return 1
    else:
        return 3

# --- Whale/Institutional/Insider Activity ---

def fetch_whale_data(ticker, finnhub_api_key=None, cache=None):
    now = datetime.now(timezone.utc)
    cache_validity = timedelta(hours=2)
    whale_cache = cache["whale"] if cache and "whale" in cache else {}

    if ticker in whale_cache:
        cached_time, cached_data = whale_cache[ticker]
        if now - cached_time < cache_validity:
            if isinstance(cached_data, dict):
                for key in ["institutional", "government", "insider"]:
                    if key not in cached_data or not isinstance(cached_data[key], list):
                        cached_data[key] = []
                return cached_data
            else:
                return {"institutional": [], "government": [], "insider": []}

    try:
        inst_url = f"https://finnhub.io/api/v1/stock/institutional-ownership?symbol={ticker}&token={finnhub_api_key}"
        inst = requests.get(inst_url).json().get("ownership", [])[:3]
        gov_url = f"https://finnhub.io/api/v1/stock/government-ownership?symbol={ticker}&token={finnhub_api_key}"
        gov = requests.get(gov_url).json().get("ownership", [])[:3]
        ins_url = f"https://finnhub.io/api/v1/stock/insider-transactions?symbol={ticker}&token={finnhub_api_key}"
        ins = requests.get(ins_url).json().get("data", [])[:3]
        data = {"institutional": inst, "government": gov, "insider": ins}
        if whale_cache is not None:
            whale_cache[ticker] = (now, data)
        return data
    except Exception as e:
        print(f"Whale fetch error for {ticker}: {e}")
        return {"institutional": [], "government": [], "insider": []}

def count_recent_whale_trades(whale_data, days=30):
    """
    Count number of whale trades in the last N days.
    """
    if not isinstance(whale_data, dict):
        print(f"[WARN] whale_data is not a dict: {type(whale_data)} - value: {whale_data}")
        return 0

    for key in ["institutional", "government", "insider"]:
        if key not in whale_data or not isinstance(whale_data[key], list):
            whale_data[key] = []

    now = datetime.now(timezone.utc)
    count = 0
    for entry in whale_data.get("institutional", []) + whale_data.get("government", []):
        date_str = entry.get("reportDate")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if now - dt.replace(tzinfo=timezone.utc) <= timedelta(days=days):
                    count += 1
            except Exception:
                continue
    for entry in whale_data.get("insider", []):
        date_str = entry.get("transactionDate")
        if date_str:
            try:
                dt = datetime.strptime(date_str, "%Y-%m-%d")
                if now - dt.replace(tzinfo=timezone.utc) <= timedelta(days=days):
                    count += 1
            except Exception:
                continue
    return count

def score_whale_activity(trade_count, high_threshold=5, low_threshold=1):
    """Score whale activity: more recent trades = higher score (1-5)."""
    if trade_count >= high_threshold:
        return 5
    elif trade_count >= (high_threshold + low_threshold) // 2:
        return 4
    elif trade_count == low_threshold:
        return 2
    elif trade_count == 0:
        return 1
    else:
        return 3

# --- Support/Resistance (Pivot Points) ---

def calculate_pivot_points(df):
    """
    Calculate classic support and resistance levels (pivot points) for a DataFrame with columns: High, Low, Close.
    Returns a DataFrame with new columns: Pivot, R1, S1, R2, S2, R3, S3.
    """
    df = df.copy()
    # Ensure price columns are numeric
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    df['Pivot'] = (df['High'] + df['Low'] + df['Close']) / 3
    df['R1'] = 2 * df['Pivot'] - df['Low']
    df['S1'] = 2 * df['Pivot'] - df['High']
    df['R2'] = df['Pivot'] + (df['High'] - df['Low'])
    df['S2'] = df['Pivot'] - (df['High'] - df['Low'])
    df['R3'] = df['High'] + 2 * (df['Pivot'] - df['Low'])
    df['S3'] = df['Low'] - 2 * (df['High'] - df['Pivot'])
    return df

def score_pivot_proximity(current_price, pivot, r1, s1):
    """
    Score price proximity to pivot/resistance/support (1-5).
    5 = price near support (bullish), 1 = price near resistance (bearish), 3 = near pivot (neutral).
    """
    # Ensure all inputs are float
    current_price = float(current_price)
    pivot = float(pivot)
    r1 = float(r1)
    s1 = float(s1)
    if abs(current_price - s1) < abs(current_price - pivot) and abs(current_price - s1) < abs(current_price - r1):
        return 5  # Near support
    elif abs(current_price - r1) < abs(current_price - pivot) and abs(current_price - r1) < abs(current_price - s1):
        return 1  # Near resistance
    else:
        return 3  # Near pivot

# --- Composite Ranking ---

def composite_etf_score(scores, weights=None):
    """
    Combine technical scores into a composite rank (1-5).
    scores: dict of {indicator_name: score}
    weights: dict of {indicator_name: weight} or None for equal weighting
    Returns: float (composite score, 1-5)
    """
    if not scores:
        return 0
    if weights is None:
        return sum(scores.values()) / len(scores)
    else:
        total_weight = sum(weights.get(k, 1) for k in scores)
        weighted_sum = sum(scores[k] * weights.get(k, 1) for k in scores)
        return weighted_sum / total_weight if total_weight else 0

# --- Top 5 ETF Ranking Function ---

def score_adx(adx):
    """ADX: 5=very strong trend, 4=strong, 3=moderate, 2=weak, 1=very weak/absent."""
    if adx is None or pd.isna(adx):
        return 2
    if adx >= 40:
        return 5
    elif adx >= 30:
        return 4
    elif adx >= 20:
        return 3
    elif adx >= 10:
        return 2
    else:
        return 1

def score_pmo(pmo):
    """PMO: 5=strongly bullish, 4=bullish, 3=neutral, 2=bearish, 1=strongly bearish."""
    if pmo is None or pd.isna(pmo):
        return 3
    if pmo >= 2:
        return 5
    elif pmo >= 1:
        return 4
    elif pmo > -1:
        return 3
    elif pmo > -2:
        return 2
    else:
        return 1

def score_cci(cci):
    """CCI: 5=very overbought, 4=overbought, 3=neutral, 2=oversold, 1=very oversold."""
    if cci is None or pd.isna(cci):
        return 3
    if cci >= 200:
        return 5
    elif cci >= 100:
        return 4
    elif cci > -100:
        return 3
    elif cci > -200:
        return 2
    else:
        return 1

def rank_top5_etfs(etf_list, price_lookup, news_api_key=NEWS_API_KEY, finnhub_api_key=FINNHUB_API_KEY, cache=None):
    """
    For each ETF in etf_list, fetch news, whale data, and calculate rankings.
    Returns a list of dicts: [{"symbol":..., "sentiment_rank":..., "whale_rank":..., "pivot_rank":..., "adx_rank":..., "pmo_rank":..., "cci_rank":..., "composite_rank":...}, ...]
    Uses both fixed scoring and relative ranking among the top 5 for each indicator.
    """
    results = []
    rows = []
    for symbol in etf_list:
        # News sentiment
        news = fetch_etf_news(symbol, news_api_key, cache=cache)
        if news and isinstance(news[0], dict) and "sentiment" in news[0]:
            sentiment = news[0]["sentiment"]
        else:
            sentiment = "Neutral"
        SentimentRank = score_sentiment(sentiment)

        # Whale activity
        whale_data = fetch_whale_data(symbol, finnhub_api_key, cache=cache)
        whale_trades = count_recent_whale_trades(whale_data)
        whale_rank = score_whale_activity(whale_trades)

        # Pivot points
        df = price_lookup[symbol]
        pivots = calculate_pivot_points(df)
        piv = pivots.iloc[-1]
        current_price = df['current_price'].iloc[-1]
        pivot_rank = score_pivot_proximity(current_price, piv['Pivot'], piv['R1'], piv['S1'])

        # --- Technicals: ADX, PMO, CCI ---
        adx = df["ADX"].iloc[-1] if "ADX" in df.columns else None
        pmo = df["PMO"].iloc[-1] if "PMO" in df.columns else None
        cci = df["CCI"].iloc[-1] if "CCI" in df.columns else None

        adx_rank = score_adx(adx)
        pmo_rank = score_pmo(pmo)
        cci_rank = score_cci(cci)

        scores = {
            "sentiment": SentimentRank,
            "whale": whale_rank,
            "pivot": pivot_rank,
            "adx": adx_rank,
            "pmo": pmo_rank,
            "cci": cci_rank
        }
        print(
            f"DEBUG: {symbol} - price: {current_price}, "
            f"ADX: {adx} (rank {adx_rank}), PMO: {pmo} (rank {pmo_rank}), CCI: {cci} (rank {cci_rank}), "
            f"Sentiment: {sentiment} (rank {SentimentRank}), Whale: {whale_rank}, Pivot: {pivot_rank}"
        )
        composite_rank = composite_etf_score(scores)

        # For relative ranking
        rows.append({
            "symbol": symbol,
            "SentimentRank": SentimentRank,
            "whale_rank": whale_rank,
            "pivot_rank": pivot_rank,
            "adx_rank": adx_rank,
            "pmo_rank": pmo_rank,
            "cci_rank": cci_rank,
            "adx": adx,
            "pmo": pmo,
            "cci": cci,
            "composite_rank": round(composite_rank, 2)
        })

        # --- Relative Ranking (1=worst, 5=best) among top 5 ---
    df = pd.DataFrame(rows)
    required_cols = ["SentimentRank", "whale_rank", "pivot_rank", "adx", "pmo", "cci"]
    if df.empty or not all(col in df.columns for col in required_cols):
        print("No data or missing columns for ranking. DataFrame columns:", df.columns)
        return []

    for col in required_cols:
        ascending = False  # Higher is better for all
        if col in ["pivot_rank"]:  # If lower is better for some, set ascending=True
            ascending = False
        if df[col].nunique() == 1:
            df[col + "_relrank"] = 3
        else:
            df[col + "_relrank"] = df[col].rank(method="min", ascending=ascending)
            df[col + "_relrank"] = ((df[col + "_relrank"] - 1) / (len(df) - 1) * 4 + 1).round().fillna(3).astype(int)

    relrank_cols = [c for c in df.columns if c.endswith("_relrank")]
    df["composite_relrank"] = df[relrank_cols].mean(axis=1).round(2)

    print("DEBUG: rank_top5_etfs relative ranks:")
    print(df[["symbol"] + relrank_cols + ["composite_relrank"]])

    # --- Output both fixed and relative ranks ---
    results = []
    for _, row in df.iterrows():
        results.append({
            "symbol": row["symbol"],
            "SentimentRank": int(row["SentimentRank"]),
            "whale_rank": int(row["whale_rank"]),
            "pivot_rank": int(row["pivot_rank"]),
            "adx_rank": int(row["adx_rank"]),
            "pmo_rank": int(row["pmo_rank"]),
            "cci_rank": int(row["cci_rank"]),
            "composite_rank": float(row["composite_rank"]),
            "Sentiment_relrank": int(row["SentimentRank_relrank"]),
            "whale_relrank": int(row["whale_rank_relrank"]),
            "pivot_relrank": int(row["pivot_rank_relrank"]),
            "adx_relrank": int(row["adx_relrank"]),
            "pmo_relrank": int(row["pmo_relrank"]),
            "cci_relrank": int(row["cci_relrank"]),
            "composite_relrank": float(row["composite_relrank"])
        })
    return results

                                                 # ***** End of rank_top5_etfs.py *****

                                          
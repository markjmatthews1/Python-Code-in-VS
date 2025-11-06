#!/usr/bin/env python3
"""
Market Consensus Collector
========================

Collects 1-minute OHLCV data for a broad set of market tickers from Schwab,
calculates a consensus score and summary, and writes to market_consensus_cache.json.
Uses Schwab's 1-minute historical data API and the existing Schwab_auth system.
"""
import os
import requests
import sys
import json
import time
from datetime import datetime, timedelta

# --- CONFIG ---
TICKERS = [
    "SPY", "DIA", "QQQ", "IWM", "RSP", "VTI", "XLF", "XLK", "XLE", "XLI", "XLC", "XLV", "XLY", "XLP", "XLU", "XLB", "XLRE"
]
CACHE_FILE = os.path.join(os.path.dirname(__file__), "market_consensus_cache.json")
SCHWAB_AUTH_PATH = os.path.join(os.path.dirname(__file__), "Schwab_auth.py")
TOKEN_FILE = os.path.join(os.path.dirname(__file__), "tokens.json")

# --- SCHWAB API WRAPPER ---
def get_schwab_session():
    """Import Schwab_auth and get an authenticated session"""
    sys.path.insert(0, os.path.dirname(__file__))
    import Schwab_auth
    access_token = Schwab_auth.get_valid_access_token()
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json"
    }
    return headers

def get_ohlcv_1min(session, symbol, minutes=480):
    """
    Get current quote with previous close from Schwab quote API.
    This works even when market is closed.
    """
    # Use the quote endpoint which gives us mark, previousClose, etc.
    endpoint = f"https://api.schwabapi.com/marketdata/v1/quotes"
    params = {
        "symbols": symbol,
        "fields": "quote,fundamental"
    }
    
    try:
        resp = requests.get(endpoint, params=params, headers=session, timeout=10)
        if resp.status_code == 401:
            print(f"⚠️ 401 Unauthorized for {symbol}, refreshing token...")
            session = get_schwab_session()  # Force refresh
            resp = requests.get(endpoint, params=params, headers=session, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        if symbol not in data:
            print(f"⚠️ No quote data for {symbol}")
            return None
        
        quote = data[symbol].get("quote", {})
        if not quote:
            print(f"⚠️ Empty quote for {symbol}")
            return None
        
        # Extract current price and previous close
        current_price = quote.get("mark", quote.get("lastPrice", 0))
        previous_close = quote.get("closePrice", quote.get("previousClose", current_price))
        
        return {
            "open": quote.get("openPrice", current_price),
            "close": current_price,
            "high": quote.get("highPrice", current_price),
            "low": quote.get("lowPrice", current_price),
            "volume": quote.get("totalVolume", 0),
            "timestamp": quote.get("quoteTime", int(datetime.now().timestamp() * 1000)),
            "previous_close": previous_close
        }
    except Exception as e:
        print(f"❌ Error fetching quote for {symbol}: {e}")
        import traceback
        traceback.print_exc()
        return None

# --- CONSENSUS CALCULATION ---
def calculate_consensus(ticker_data):
    """
    Calculate market consensus based on current price vs previous day close.
    
    Major indices (SPY, QQQ, DIA) get 2x weight.
    Threshold: 0.05% (more sensitive than old 0.1%)
    Score range: -24 to +24 (17 tickers, 3 major ones count double)
    """
    # Define major indices with higher weight
    MAJOR_INDICES = {"SPY", "QQQ", "DIA"}
    
    signals = []
    details = {}
    bullish_tickers = []
    bearish_tickers = []
    neutral_tickers = []
    
    for ticker, ohlcv in ticker_data.items():
        if not ohlcv:
            continue
        
        # Calculate daily change (current price vs previous day close)
        current_price = ohlcv["close"]
        prev_close = ohlcv.get("previous_close", ohlcv["open"])  # Fallback to open if no prev close
        
        if prev_close and prev_close > 0:
            change_pct = ((current_price - prev_close) / prev_close) * 100
        else:
            # Fallback to intraday change if no previous close
            change_pct = ((current_price - ohlcv["open"]) / ohlcv["open"]) * 100
        
        details[ticker] = {
            "change_pct": round(change_pct, 3),
            "close": current_price,
            "prev_close": prev_close
        }
        
        # Determine signal (lowered threshold to 0.05% for more sensitivity)
        weight = 2 if ticker in MAJOR_INDICES else 1
        
        if change_pct > 0.05:
            signal_value = 1 * weight
            signals.append(signal_value)
            bullish_tickers.append(f"{ticker} (+{change_pct:.2f}%)")
        elif change_pct < -0.05:
            signal_value = -1 * weight
            signals.append(signal_value)
            bearish_tickers.append(f"{ticker} ({change_pct:.2f}%)")
        else:
            signals.append(0)
            neutral_tickers.append(f"{ticker} ({change_pct:.2f}%)")
    
    score = sum(signals)
    max_possible_score = len(ticker_data) + len(MAJOR_INDICES)  # Regular + bonus from majors
    
    # Calculate percentages for summary
    total_tickers = len(ticker_data)
    bullish_count = len(bullish_tickers)
    bearish_count = len(bearish_tickers)
    neutral_count = len(neutral_tickers)
    
    # More nuanced summary with actual numbers
    if score >= 6:
        summary = f"🟢 Strong Bullish ({bullish_count}/{total_tickers} green)"
    elif score >= 3:
        summary = f"🟢 Bullish ({bullish_count}/{total_tickers} green)"
    elif score >= 1:
        summary = f"🟡 Weakly Bullish ({bullish_count}/{total_tickers} green)"
    elif score <= -6:
        summary = f"🔴 Strong Bearish ({bearish_count}/{total_tickers} red)"
    elif score <= -3:
        summary = f"🔴 Bearish ({bearish_count}/{total_tickers} red)"
    elif score <= -1:
        summary = f"🟡 Weakly Bearish ({bearish_count}/{total_tickers} red)"
    else:
        summary = f"⚪ Neutral/Mixed ({bullish_count} green, {bearish_count} red)"
    
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "details": details,
        "score": score,
        "max_score": max_possible_score,
        "summary": summary,
        "bullish_tickers": bullish_tickers,
        "bearish_tickers": bearish_tickers,
        "neutral_tickers": neutral_tickers,
        "bullish_count": bullish_count,
        "bearish_count": bearish_count,
        "neutral_count": neutral_count
    }

# --- MAIN ---
def main():
    print("\n📊 Market Consensus Collector - Schwab Daily Performance\n" + "="*60)
    session = get_schwab_session()
    ticker_data = {}
    for ticker in TICKERS:
        print(f"Fetching {ticker} current price vs prev close...")
        ohlcv = get_ohlcv_1min(session, ticker)
        ticker_data[ticker] = ohlcv
        time.sleep(0.5)  # Avoid rate limits
    
    consensus = calculate_consensus(ticker_data)
    
    print(f"\n{'='*60}")
    print(f"📊 MARKET CONSENSUS: {consensus['summary']}")
    print(f"📈 Score: {consensus['score']}/{consensus['max_score']}")
    print(f"{'='*60}")
    
    if consensus['bullish_tickers']:
        print(f"\n🟢 BULLISH ({consensus['bullish_count']}):")
        for ticker in consensus['bullish_tickers']:
            print(f"   {ticker}")
    
    if consensus['bearish_tickers']:
        print(f"\n🔴 BEARISH ({consensus['bearish_count']}):")
        for ticker in consensus['bearish_tickers']:
            print(f"   {ticker}")
    
    if consensus['neutral_tickers']:
        print(f"\n⚪ NEUTRAL ({consensus['neutral_count']}):")
        for ticker in consensus['neutral_tickers']:
            print(f"   {ticker}")
    
    # Write to cache
    with open(CACHE_FILE, "w") as f:
        json.dump(consensus, f, indent=2)
    print(f"\n✅ Consensus written to {CACHE_FILE}")
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()

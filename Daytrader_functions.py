import yfinance as yf
from newspaper import Article
           # ***** begining of news articles from Yahoo Finance ranked for strength as catalysts *****
def get_news_catalyst(symbols):
    """
    Fetches news articles for given symbols and attempts to identify catalysts.

    Args:
        symbols (list): List of stock or ETF symbols.

    Returns:
        dict: Dictionary with symbols as keys and lists of catalysts (with scores) as values.
    """
    catalysts = {}
    for symbol in symbols:
        catalysts[symbol] = []
        ticker = yf.Ticker(symbol)
        news = ticker.news
        for article_data in news:
            try:
                url = article_data['link']
                article = Article(url)
                article.download()
                article.parse()
                # Basic keyword-based catalyst identification and scoring
                score = 0
                keywords = ["earnings", "merger", "acquisition", "fda", "approval", "patent", "lawsuit", "product launch"]
                for keyword in keywords:
                    if keyword in article.text.lower():
                        score += 1  # Increment score for each keyword match
                if score > 0:
                    catalysts[symbol].append((article.title, score))
            except Exception as e:
                print(f"Error processing article for {symbol}: {e}")
    return catalysts

def rank_catalysts(catalysts):
    """
    Ranks catalysts based on their scores.

    Args:
        catalysts (dict): Dictionary of catalysts (from get_news_catalyst).

    Returns:
        dict: Dictionary with symbols as keys and ranked lists of catalysts as values.
    """
    ranked_catalysts = {}
    for symbol, catalyst_list in catalysts.items():
        ranked_catalysts[symbol] = sorted(catalyst_list, key=lambda item: item[1], reverse=True)
    return ranked_catalysts

# Example usage
symbols = tickers
catalysts = get_news_catalyst(symbols)
ranked_catalysts = rank_catalysts(catalysts)

# Display results
for symbol, ranked_list in ranked_catalysts.items():
    print(f"Catalysts for {symbol}:")
    for title, score in ranked_list:
        print(f"- {title} (Score: {score})")

        # ***** End of news articles from Yahoo Finance ranked for strength as catalysts *****

        # ***** begining of major buying from senate, legislator and major institutinal buying with ranking *****

import pandas as pd
from bs4 import BeautifulSoup
import requests

def get_significant_purchases(symbols):
    """
    Scrapes data from websites like OpenSecrets and WhaleWisdom to find significant purchases.

    Args:
        symbols (list): List of stock or ETF symbols.

    Returns:
        dict: Dictionary with symbols as keys and lists of purchases (with ratings) as values.
    """
    significant_purchases = {}
    for symbol in symbols:
        significant_purchases[symbol] = []
        # Scrape OpenSecrets for senator/legislator data
        url = f"https://www.opensecrets.org/search?q={symbol}&type=donors"  # Replace with actual OpenSecrets search URL structure
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract data from OpenSecrets (replace with actual HTML structure parsing)
        for purchase_data in soup.find_all("div", class_="purchase-item"):  # Replace with actual class name
            investor = purchase_data.find("span", class_="investor").text  # Replace with actual class name
            amount = purchase_data.find("span", class_="amount").text  # Replace with actual class name
            # Basic rating logic (replace with more sophisticated analysis)
            rating = 3 if float(amount.replace("$", "").replace(",", "")) > 100000 else 1
            significant_purchases[symbol].append((investor, amount, rating))
        # Scrape WhaleWisdom for institutional data
        url = f"https://whalewisdom.com/stock/{symbol}"  # Replace with actual WhaleWisdom URL structure
        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        # Extract data from WhaleWisdom (replace with actual HTML structure parsing)
        for purchase_data in soup.find_all("tr", class_="purchase-row"):  # Replace with actual class name
            investor = purchase_data.find("td", class_="investor").text  # Replace with actual class name
            amount = purchase_data.find("td", class_="amount").text  # Replace with actual class name
            # Basic rating logic (replace with more sophisticated analysis)
            rating = 5 if float(amount.replace("$", "").replace(",", "")) > 10000000 else 2
            significant_purchases[symbol].append((investor, amount, rating))
    return significant_purchases

# Example usage
symbols = ["AAPL", "MSFT", "GOOG", "AMZN", "TSLA"]
purchases = get_significant_purchases(symbols)

# Display results
for symbol, purchase_list in purchases.items():
    print(f"Significant Purchases for {symbol}:")
    for investor, amount, rating in purchase_list:
        print(f"- {investor}: {amount} (Rating: {rating})")

                     # ***** End of major buying from senate, legislator and major institutinal buying with ranking *****

# Authenticate Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("/content/drive/MyDrive/Colab_Data/day-trader-app-458021-798684c293d2.json", scope)
client = gspread.authorize(creds)

# Open the Google Sheet (Replace with your Sheet name)
spreadsheet = client.open("Trading Alerts").sheet1

# Function to log trades
# Function to calculate success rate and track profitable patterns
def log_trade(symbol, entry_price, exit_price, volume, pnl, pattern, timeframe):
    success = "Win" if pnl > 0 else "Loss"
    trade_data = [symbol, entry_price, exit_price, volume, pnl, success, pattern, timeframe]
    spreadsheet.append_row(trade_data)
    print(f"Trade logged: {trade_data}")

# Function to compute max drawdown
def calculate_max_drawdown(trades):
    peak = trades[0]["Exit Price"]
    max_drawdown = 0

    for trade in trades:
        current_price = trade["Exit Price"]
        drawdown = (peak - current_price) / peak * 100  # Percentage drawdown
        max_drawdown = min(max_drawdown, drawdown)
        if current_price > peak:
            peak = current_price  # Reset peak on new highs

    return round(max_drawdown, 2)

# Function to log max drawdown in Google Sheets
def log_max_drawdown():
    trades = spreadsheet.get_all_records()
    max_drawdown = calculate_max_drawdown(trades)
    spreadsheet.append_row(["Max Drawdown", max_drawdown])
    print(f"Max Drawdown Recorded: {max_drawdown}%")

# Function to send Telegram alerts if drawdown exceeds threshold
def check_drawdown_threshold(threshold=10):
    trades = spreadsheet.get_all_records()
    max_drawdown = calculate_max_drawdown(trades)

    if max_drawdown < -threshold:
        send_telegram_alert(f"⚠️ Drawdown Alert: {max_drawdown}% exceeds {threshold}% limit! Review risk strategy.")

# Function to analyze trading patterns from the Google Sheet
def analyze_trading_patterns():
    trades = spreadsheet.get_all_records()
    success_count = sum(1 for trade in trades if trade["Success"] == "Win")
    total_trades = len(trades)
    win_rate = round((success_count / total_trades) * 100, 2) if total_trades > 0 else 0

    pattern_counts = {}
    for trade in trades:
        pattern = trade["Pattern"]
        if pattern in pattern_counts:
            pattern_counts[pattern] += 1
        else:
            pattern_counts[pattern] = 1

    print(f"Win Rate: {win_rate}%")
    print(f"Most Profitable Patterns: {sorted(pattern_counts.items(), key=lambda x: x[1], reverse=True)}")



# Function to generate and play voice alert
def play_voice_alert(message, filename):
    tts = gTTS(text=message, lang="en")
    tts.save(filename)
    display(Audio(filename, autoplay=True))

# Trade setup alert (entry)
def check_trade_entry_alert(symbol, trade_score):
    if trade_score >= 8:
        play_voice_alert(f"🚀 Strong trade setup detected for {symbol}! High probability trade.", "/strong_trade.mp3")
    elif 5 <= trade_score < 8:
        play_voice_alert(f"🔵 Trade setup found for {symbol}. Moderate probability.", "/medium_trade.mp3")

# Trade exit alert
def check_trade_exit_alert(symbol, current_price, target_exit_price):
    if current_price >= target_exit_price:
        play_voice_alert(f"✅ Exit hit! {symbol} reached {target_exit_price}.", "/exit_trade.mp3")

# Integration: Voice Alert + Telegram Notification
def notify_trade_event(symbol, trade_score, current_price=None, target_exit_price=None):
    if trade_score >= 5:
        check_trade_entry_alert(symbol, trade_score)
        send_telegram_alert(f"🚀 Trade Setup Alert for {symbol}! Score: {trade_score}")

    if current_price is not None and target_exit_price is not None and current_price >= target_exit_price:
        check_trade_exit_alert(symbol, current_price, target_exit_price)
        send_telegram_alert(f"✅ Exit Hit: {symbol} reached {target_exit_price}")

# Function to send trade alerts via Telegram
def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    params = {"7753863235": "Daytrader70_bot", "text": message}
    requests.get(url, params=params)
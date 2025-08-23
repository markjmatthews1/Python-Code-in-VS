# Wishlist Tracker App

A Python app to track stocks/ETFs and find excellent put premiums using Schwab and E*TRADE data.

## Features
- Track a watchlist of stocks and ETFs
- Fetch real-time prices and 52-week highs
- Analyze option chains for high-premium puts (premium > $1, strike > current, strike < 52wk high)
- Modular code for easy extension

## Structure
- `data/`: Data fetching from APIs
- `models/`: Data models
- `utils/`: Watchlist and analysis utilities
- `tests/`: Unit tests

## Getting Started
1. Install requirements: `pip install -r requirements.txt`
2. Run the app: `python app.py`

## TODO
- Implement Schwab/E*TRADE API integration
- Build UI (Dash or CLI)
- Add persistent watchlist storage

"""
Configuration settings for WeeklyPay™ Rotation App
"""

import os
import json
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"

# Data files
ETF_LIST_FILE = DATA_DIR / "etf_list.json"
STATE_DB_FILE = DATA_DIR / "state.db"

# GUI Configuration
GUI_SETTINGS = {
    "font_family": "Arial",
    "font_size": 12,
    "window_title": "WeeklyPay™ Rotation App",
    "window_size": "800x600",
    "colors": {
        "background": "#f0f0f0",
        "rotate_in": "#00ff00",      # Green for rotate in
        "rotate_out": "#ff0000",     # Red for rotate out
        "neutral": "#ffff00",        # Yellow for neutral
        "text": "#000000",           # Black text
        "button": "#4CAF50",         # Green button
        "button_text": "#ffffff"     # White button text
    }
}

# Data refresh intervals (in seconds)
REFRESH_INTERVALS = {
    "market_data": 60,        # 1 minute for market data
    "earnings_calendar": 3600, # 1 hour for earnings calendar
    "dividend_data": 3600     # 1 hour for dividend data
}

# Market hours (Eastern Time)
MARKET_HOURS = {
    "open": "09:30",
    "close": "16:00"
}

def load_etf_config():
    """Load ETF configuration from JSON file"""
    try:
        with open(ETF_LIST_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"ETF configuration file not found: {ETF_LIST_FILE}")
        return None
    except json.JSONDecodeError:
        print(f"Error parsing ETF configuration file: {ETF_LIST_FILE}")
        return None
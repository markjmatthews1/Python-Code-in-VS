"""
Settings Manager for WeeklyPay App
Loads ticker settings from JSON and provides them to the dashboard
"""

import json
from pathlib import Path
from datetime import datetime

class WeeklyPaySettingsManager:
    def __init__(self):
        self.settings_file = Path(__file__).parent / "data" / "weeklypay_settings.json"
        self.settings = self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error loading settings: {e}")
                return self.get_default_settings()
        return self.get_default_settings()
    
    def get_default_settings(self):
        """Return default settings if file doesn't exist"""
        return {
            'tickers': {
                'NVDW': {
                    'name': 'GraniteShares 1x Long NVDA Daily ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-11-04',
                    'sector': 'Technology',
                    'active': True
                },
                'AMDW': {
                    'name': 'GraniteShares 1x Long AMD Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'HOOW': {
                    'name': 'GraniteShares 1x Long META Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'MSFW': {
                    'name': 'GraniteShares 1x Long MSFT Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'GOOW': {
                    'name': 'GraniteShares 1x Long GOOGL Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Technology',
                    'active': True
                },
                'NFLW': {
                    'name': 'GraniteShares 1x Long NFLX Daily ETF',
                    'ex_dividend_day': 'Tuesday',
                    'pay_day': 'Wednesday',
                    'last_ex_date': '2025-10-07',
                    'sector': 'Communication',
                    'active': True
                },
                'XOMO': {
                    'name': 'Roundhill XOM WeeklyPay ETF',
                    'ex_dividend_day': 'Thursday',
                    'pay_day': 'Friday',
                    'last_ex_date': '2025-10-03',
                    'sector': 'Energy',
                    'active': True
                },
                'QDTE': {
                    'name': 'Roundhill QDTE WeeklyPay ETF',
                    'ex_dividend_day': 'Thursday',
                    'pay_day': 'Friday',
                    'last_ex_date': '2025-10-03',
                    'sector': 'Technology',
                    'active': True
                },
                'TSLW': {
                    'name': 'GraniteShares 1x Long TSLA Daily ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-10-27',
                    'sector': 'Technology',
                    'active': True
                },
                'BRKW': {
                    'name': 'GraniteShares 1x Long BRK.B Daily ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-10-27',
                    'sector': 'Financials',
                    'active': True
                },
                'XDTE': {
                    'name': 'Roundhill S&P 500 0DTE Covered Call ETF',
                    'ex_dividend_day': 'Thursday',
                    'pay_day': 'Friday',
                    'last_ex_date': '2025-10-31',
                    'sector': 'Broad Market',
                    'active': True
                },
                'NVDY': {
                    'name': 'YieldMax NVDA Option Income ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-11-04',
                    'sector': 'Technology',
                    'active': True
                },
                'TSLY': {
                    'name': 'YieldMax TSLA Option Income ETF',
                    'ex_dividend_day': 'Monday',
                    'pay_day': 'Tuesday',
                    'last_ex_date': '2025-11-04',
                    'sector': 'Technology',
                    'active': True
                },
                'MSTY': {
                    'name': 'YieldMax MSTR Option Income ETF',
                    'ex_dividend_day': 'Thursday',
                    'pay_day': 'Friday',
                    'last_ex_date': '2025-10-31',
                    'sector': 'Technology/Crypto',
                    'active': True
                }
            }
        }
    
    def get_last_known_ex_div_dates(self):
        """
        Get dictionary of last known ex-dividend dates for use in dashboard
        Returns: dict with ticker -> datetime object
        """
        result = {}
        for ticker, data in self.settings['tickers'].items():
            if data.get('active', True):
                try:
                    date_str = data.get('last_ex_date', '')
                    result[ticker] = datetime.strptime(date_str, '%Y-%m-%d')
                except Exception as e:
                    print(f"Error parsing date for {ticker}: {e}")
        return result
    
    def get_active_tickers(self):
        """Get list of active ticker symbols"""
        return [ticker for ticker, data in self.settings['tickers'].items() 
                if data.get('active', True)]
    
    def get_ticker_info(self, ticker):
        """Get full info for a specific ticker"""
        return self.settings['tickers'].get(ticker, {})
    
    def get_all_tickers_info(self):
        """Get all ticker information"""
        return {ticker: data for ticker, data in self.settings['tickers'].items()
                if data.get('active', True)}
    
    def get_day_number(self, day_name):
        """Convert day name to weekday number (Monday=0, Sunday=6)"""
        days = {
            'Monday': 0,
            'Tuesday': 1,
            'Wednesday': 2,
            'Thursday': 3,
            'Friday': 4,
            'Saturday': 5,
            'Sunday': 6
        }
        return days.get(day_name, 1)  # Default to Tuesday


def get_settings_manager():
    """Convenience function to get settings manager instance"""
    return WeeklyPaySettingsManager()

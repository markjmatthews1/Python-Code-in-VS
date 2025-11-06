# Portfolio Loader for Catalyst Scanner
# 
# Reads user's investment ticker list from Excel file and manages portfolio data
# for catalyst tracking and impact analysis.
#
# Author: Investment Catalyst Team
# Date: September 29, 2025

import pandas as pd
import logging
import os
from typing import List, Dict, Optional
from datetime import datetime

from utils.logger import get_logger, log_performance, log_data_update
from utils.error_handler import data_error_handler, handle_error


class PortfolioLoader:
    """
    Portfolio loader for reading and managing user's investment ticker list
    from Excel file for catalyst tracking and analysis.
    """
    
    def __init__(self, excel_file_path: str = None):
        """
        Initialize portfolio loader
        
        Args:
            excel_file_path: Path to Excel file with investment tickers
        """
        self.logger = get_logger()
        self.excel_file_path = excel_file_path or self._find_default_excel_file()
        self.portfolio_data = {}
        self.tickers = []
        self.last_update = None
        
        # Excel file structure expectations
        self.required_columns = ['Ticker', 'Shares', 'Entry_Price', 'Current_Price', 'Weight']
        self.optional_columns = ['Sector', 'Industry', 'Market_Cap', 'Notes']
        
        self.logger.info(f"Portfolio loader initialized with Excel file: {self.excel_file_path}")
    
    def _find_default_excel_file(self) -> str:
        """Find default Excel file - prioritize Bryan Perry Transactions"""
        # Get absolute paths for better reliability
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # Go up to main directory
        
        default_paths = [
            os.path.join(base_dir, "..", "Bryan Perry Transactions.xlsx"),  # Primary source
            os.path.join(base_dir, "config", "investment_tickers.xlsx"),
            os.path.join(base_dir, "config", "portfolio.xlsx"), 
            os.path.join(base_dir, "config", "tickers.xlsx"),
            os.path.join(base_dir, "..", "dividend_stocks.xlsx")  # Final fallback
        ]
        
        for path in default_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                self.logger.info(f"Found default Excel file: {abs_path}")
                return abs_path
        
        # If no file found, use the default name with absolute path
        return os.path.join(base_dir, "config", "investment_tickers.xlsx")
    
    @data_error_handler("Portfolio loading")
    def load_portfolio(self) -> bool:
        """
        Load portfolio data from Excel file
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not os.path.exists(self.excel_file_path):
                self.logger.warning(f"Excel file not found: {self.excel_file_path}")
                self._create_sample_excel_file()
                return False
            
            # Check if this is Bryan Perry Transactions file
            if "Bryan Perry Transactions" in self.excel_file_path:
                return self._load_bryan_perry_portfolio()
            
            # Read Excel file (standard format)
            df = pd.read_excel(self.excel_file_path)
            self.logger.info(f"Read Excel file with {len(df)} rows")
            
            # Validate required columns
            missing_columns = [col for col in self.required_columns if col not in df.columns]
            if missing_columns:
                self.logger.error(f"Missing required columns: {missing_columns}")
                return False
            
            # Clean and process data
            df = self._clean_portfolio_data(df)
            
            # Extract tickers and portfolio info
            self.tickers = df['Ticker'].tolist()
            self.portfolio_data = df.to_dict('records')
            self.last_update = datetime.now()
            
            self.logger.info(f"Successfully loaded {len(self.tickers)} tickers: {self.tickers}")
            log_data_update("portfolio", len(self.tickers), f"Portfolio loaded: {len(self.tickers)} tickers")
            
            return True
            
        except Exception as e:
            handle_error(e, "Portfolio loading", "Failed to load investment portfolio")
            return False
    
    def _load_bryan_perry_portfolio(self) -> bool:
        """
        Load portfolio data from Bryan Perry Transactions file
        Reads from 'Open_Trades_2025' sheet, column D for tickers
        Handles duplicates by keeping unique tickers only
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Read the specific sheet
            df = pd.read_excel(self.excel_file_path, sheet_name='Open_Trades_2025')
            self.logger.info(f"Read Bryan Perry file 'Open_Trades_2025' sheet with {len(df)} rows")
            
            # Extract column D (should be index 3, but let's be safe)
            ticker_column = None
            for col_idx, col_name in enumerate(df.columns):
                if col_idx == 3:  # Column D (0-indexed)
                    ticker_column = col_name
                    break
            
            if ticker_column is None or ticker_column not in df.columns:
                self.logger.error("Could not find column D in Bryan Perry Transactions file")
                return False
            
            # Extract tickers from column D
            raw_tickers = df[ticker_column].dropna().astype(str).tolist()
            self.logger.info(f"Found {len(raw_tickers)} raw ticker entries")
            
            # Clean and deduplicate tickers
            unique_tickers = self._clean_bryan_perry_tickers(raw_tickers)
            
            # Create simplified portfolio data for catalyst tracking
            self.tickers = unique_tickers
            self.portfolio_data = []
            
            for ticker in unique_tickers:
                portfolio_entry = {
                    'Ticker': ticker,
                    'Shares': 100,  # Default for catalyst tracking
                    'Entry_Price': 0,  # Unknown from this source
                    'Current_Price': 0,  # To be updated with live data
                    'Weight': 100 / len(unique_tickers),  # Equal weight distribution
                    'Source': 'Bryan Perry Transactions',
                    'Sheet': 'Open_Trades_2025'
                }
                self.portfolio_data.append(portfolio_entry)
            
            self.last_update = datetime.now()
            
            self.logger.info(f"Successfully loaded {len(self.tickers)} unique tickers: {self.tickers}")
            log_data_update("portfolio", len(self.tickers), f"Bryan Perry portfolio loaded: {len(self.tickers)} unique tickers")
            
            return True
            
        except Exception as e:
            handle_error(e, "Bryan Perry portfolio loading", 
                        f"Failed to load from Bryan Perry Transactions file: {str(e)}")
            return False
    
    def _clean_bryan_perry_tickers(self, raw_tickers: List[str]) -> List[str]:
        """
        Clean and deduplicate tickers from Bryan Perry file
        
        Args:
            raw_tickers: Raw ticker list from Excel
            
        Returns:
            List[str]: Clean, unique ticker list
        """
        cleaned_tickers = set()
        
        for ticker in raw_tickers:
            # Convert to string and clean
            ticker_str = str(ticker).strip().upper()
            
            # Skip empty or invalid entries
            if not ticker_str or ticker_str in ['NAN', 'NONE', '']:
                continue
            
            # Basic ticker validation (1-5 letters, possibly with numbers)
            if len(ticker_str) >= 1 and len(ticker_str) <= 5:
                # Remove any special characters but keep letters and numbers
                clean_ticker = ''.join(c for c in ticker_str if c.isalnum())
                
                if clean_ticker and len(clean_ticker) <= 5:
                    cleaned_tickers.add(clean_ticker)
        
        # Convert back to sorted list
        unique_tickers = sorted(list(cleaned_tickers))
        
        self.logger.info(f"Cleaned {len(raw_tickers)} raw tickers down to {len(unique_tickers)} unique tickers")
        self.logger.debug(f"Unique tickers: {unique_tickers}")
        
        return unique_tickers
    
    def _clean_portfolio_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate portfolio data
        
        Args:
            df: Raw DataFrame from Excel
            
        Returns:
            pd.DataFrame: Cleaned data
        """
        # Remove empty rows
        df = df.dropna(subset=['Ticker'])
        
        # Clean ticker symbols (uppercase, remove spaces)
        df['Ticker'] = df['Ticker'].str.upper().str.strip()
        
        # Validate ticker format (basic check)
        df = df[df['Ticker'].str.match(r'^[A-Z]{1,5}$')]
        
        # Set default values for missing data
        df['Shares'] = pd.to_numeric(df['Shares'], errors='coerce').fillna(0)
        df['Entry_Price'] = pd.to_numeric(df['Entry_Price'], errors='coerce').fillna(0)
        df['Current_Price'] = pd.to_numeric(df['Current_Price'], errors='coerce').fillna(0)
        df['Weight'] = pd.to_numeric(df['Weight'], errors='coerce').fillna(0)
        
        # Calculate position value if missing
        if 'Position_Value' not in df.columns:
            df['Position_Value'] = df['Shares'] * df['Current_Price']
        
        self.logger.info(f"Cleaned portfolio data: {len(df)} valid tickers")
        return df
    
    def _create_sample_excel_file(self):
        """Create a sample Excel file template for user"""
        try:
            # Sample portfolio data
            sample_data = {
                'Ticker': ['AAPL', 'MSFT', 'NVDA', 'SMCI', 'MARA'],
                'Shares': [100, 50, 25, 200, 150],
                'Entry_Price': [150.00, 300.00, 400.00, 45.00, 15.00],
                'Current_Price': [175.00, 350.00, 450.00, 50.00, 18.00],
                'Weight': [35.0, 25.0, 20.0, 15.0, 5.0],
                'Sector': ['Technology', 'Technology', 'Technology', 'Technology', 'Crypto Mining'],
                'Notes': ['Core holding', 'Dividend play', 'AI play', 'Earnings play', 'Speculative']
            }
            
            df = pd.DataFrame(sample_data)
            
            # Ensure config directory exists
            os.makedirs('config', exist_ok=True)
            
            # Save sample file
            df.to_excel(self.excel_file_path, index=False)
            self.logger.info(f"Created sample Excel template: {self.excel_file_path}")
            
        except Exception as e:
            handle_error(e, "Sample file creation", "Failed to create sample Excel template")
    
    def get_tickers(self) -> List[str]:
        """
        Get list of ticker symbols
        
        Returns:
            List[str]: List of ticker symbols
        """
        return self.tickers.copy()
    
    def get_portfolio_data(self) -> List[Dict]:
        """
        Get complete portfolio data
        
        Returns:
            List[Dict]: Portfolio information for each ticker
        """
        return self.portfolio_data.copy()
    
    def get_ticker_info(self, ticker: str) -> Optional[Dict]:
        """
        Get information for specific ticker
        
        Args:
            ticker: Ticker symbol
            
        Returns:
            Dict: Ticker information or None if not found
        """
        for item in self.portfolio_data:
            if item.get('Ticker') == ticker.upper():
                return item
        return None
    
    def get_portfolio_weights(self) -> Dict[str, float]:
        """
        Get portfolio weights for impact analysis
        
        Returns:
            Dict[str, float]: Ticker to weight mapping
        """
        weights = {}
        for item in self.portfolio_data:
            ticker = item.get('Ticker')
            weight = item.get('Weight', 0)
            if ticker:
                weights[ticker] = weight
        return weights
    
    def refresh_current_prices(self, price_data: Dict[str, float]):
        """
        Update current prices in portfolio data
        
        Args:
            price_data: Dict mapping ticker to current price
        """
        updated_count = 0
        
        for item in self.portfolio_data:
            ticker = item.get('Ticker')
            if ticker in price_data:
                old_price = item.get('Current_Price', 0)
                new_price = price_data[ticker]
                item['Current_Price'] = new_price
                
                # Update position value
                shares = item.get('Shares', 0)
                item['Position_Value'] = shares * new_price
                
                # Calculate gain/loss
                entry_price = item.get('Entry_Price', 0)
                if entry_price > 0:
                    item['Gain_Loss_Percent'] = ((new_price - entry_price) / entry_price) * 100
                
                updated_count += 1
                self.logger.debug(f"Updated {ticker}: ${old_price:.2f} -> ${new_price:.2f}")
        
        if updated_count > 0:
            self.last_update = datetime.now()
            log_data_update(f"Updated prices for {updated_count} tickers")
            self.logger.info(f"Refreshed current prices for {updated_count} tickers")
    
    def get_high_weight_tickers(self, min_weight: float = 10.0) -> List[str]:
        """
        Get tickers with weight above threshold for priority catalyst tracking
        
        Args:
            min_weight: Minimum weight percentage
            
        Returns:
            List[str]: High-weight tickers
        """
        high_weight = []
        for item in self.portfolio_data:
            ticker = item.get('Ticker')
            weight = item.get('Weight', 0)
            if ticker and weight >= min_weight:
                high_weight.append(ticker)
        
        return high_weight
    
    def get_portfolio_summary(self) -> Dict:
        """
        Get portfolio summary statistics
        
        Returns:
            Dict: Portfolio summary information
        """
        if not self.portfolio_data:
            return {}
        
        total_value = sum(item.get('Position_Value', 0) for item in self.portfolio_data)
        total_weight = sum(item.get('Weight', 0) for item in self.portfolio_data)
        
        summary = {
            'ticker_count': len(self.tickers),
            'total_value': total_value,
            'total_weight': total_weight,
            'last_update': self.last_update,
            'file_path': self.excel_file_path,
            'high_weight_count': len(self.get_high_weight_tickers()),
            'sectors': self._get_sector_breakdown()
        }
        
        return summary
    
    def _get_sector_breakdown(self) -> Dict[str, int]:
        """Get breakdown of holdings by sector"""
        sectors = {}
        for item in self.portfolio_data:
            sector = item.get('Sector', 'Unknown')
            sectors[sector] = sectors.get(sector, 0) + 1
        return sectors
    
    def is_portfolio_loaded(self) -> bool:
        """Check if portfolio is loaded"""
        return len(self.tickers) > 0
    
    def save_portfolio_updates(self):
        """Save updated portfolio data back to Excel file"""
        try:
            if not self.portfolio_data:
                self.logger.warning("No portfolio data to save")
                return False
            
            df = pd.DataFrame(self.portfolio_data)
            df.to_excel(self.excel_file_path, index=False)
            
            self.logger.info(f"Saved portfolio updates to {self.excel_file_path}")
            return True
            
        except Exception as e:
            handle_error(e, "Portfolio saving", "Failed to save portfolio updates")
            return False


# Convenience function for quick access
def load_user_portfolio(excel_path: str = None) -> PortfolioLoader:
    """
    Quick function to load user portfolio
    
    Args:
        excel_path: Optional path to Excel file
        
    Returns:
        PortfolioLoader: Loaded portfolio instance
    """
    loader = PortfolioLoader(excel_path)
    
    if loader.load_portfolio():
        return loader
    else:
        # Return empty loader for graceful degradation
        return loader


if __name__ == "__main__":
    # Test the portfolio loader
    print("Testing Portfolio Loader...")
    
    loader = load_user_portfolio()
    
    if loader.is_portfolio_loaded():
        summary = loader.get_portfolio_summary()
        print(f"Loaded {summary['ticker_count']} tickers")
        print(f"High-weight tickers: {loader.get_high_weight_tickers()}")
        print(f"All tickers: {loader.get_tickers()}")
    else:
        print("Portfolio not loaded - sample file created")
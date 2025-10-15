# Wishlist Tracker App

A Python application that tracks stocks/ETFs and analyzes put options for premium selling strategies using E*TRADE API integration.

## Features

### Core Functionality
- **Real-time Data**: Fetches live stock prices, 52-week highs/lows, and volume data via E*TRADE API
- **Options Analysis**: Analyzes put option chains to find profitable premium selling opportunities
- **Three-Tier Sorting**: Intelligent sorting by uptrend status, positive premiums, and negative premiums (best deals first)
- **Visual Dashboard**: Professional tkinter GUI with real-time updates and colorized loading spinner

### Premium Strategy Focus
- Identifies puts with negative premiums (where you get paid to potentially buy below current price)
- Calculates net cost basis and profit potential for each option
- Prioritizes options with highest combined scores (premium yield + negative premium amount)
- Supports multiple expiration dates (current month + 2 additional months)

### User Interface
- **Clean Design**: Professional layout with proper column sizing and data formatting
- **Real-time Updates**: Live data refresh with progress indicators
- **Ticker Management**: Easy addition/removal of watchlist symbols
- **Status Monitoring**: Network error handling and success/failure reporting

## Recent Updates (October 2025)

### v2.1 - Interface Improvements
- ✅ **Fixed Three-Tier Sorting**: Corrected sorting algorithm for proper uptrend > positive > negative premium ordering
- ✅ **Enhanced Spinner**: Large, colorized loading spinner with overlay positioning to prevent header expansion
- ✅ **Clean Data Format**: Removed decorative stars for compact, professional appearance
- ✅ **Column Optimization**: Streamlined "Put Target" column with proper width management
- ✅ **Premium Column**: Renamed from "Premium vs Current" to "Premium" for clarity

### v2.0 - Core Functionality
- ✅ **E*TRADE Integration**: Full API authentication and data fetching
- ✅ **Options Analysis Engine**: Advanced put option evaluation with probability calculations
- ✅ **GUI Dashboard**: Complete tkinter interface with data tables and controls
- ✅ **Error Handling**: Robust network error management and retry logic

## Technical Architecture

### Data Flow
1. **Authentication**: OAuth token management for E*TRADE API
2. **Data Fetching**: Parallel stock and options data retrieval
3. **Analysis Engine**: Put option evaluation and scoring
4. **Sorting Algorithm**: Three-tier intelligent ranking
5. **GUI Updates**: Real-time interface updates with progress feedback

### File Structure
```
wishlist_tracker/
├── gui/
│   └── dashboard_gui.py          # Main GUI application
├── data/
│   ├── etrade_client.py          # E*TRADE API integration
│   ├── options_analyzer.py       # Options analysis engine
│   └── watchlist_manager.py      # Ticker management
├── utils/
│   └── auth_manager.py           # Authentication utilities
└── README.md                     # This file
```

## Getting Started

### Prerequisites
- Python 3.8+
- E*TRADE developer account with API keys
- Required packages (install via `pip install -r requirements.txt`):
  - tkinter (usually included with Python)
  - requests
  - datetime
  - json

### Configuration
1. **Set up E*TRADE credentials** in `config.ini` or environment variables
2. **Add watchlist tickers** to `data/watchlist.json`
3. **Run the application**: `python wishlist_tracker/gui/dashboard_gui.py`

### Usage
1. **Launch Dashboard**: Start the GUI application
2. **Refresh Data**: Click "Refresh Data" to fetch current market information
3. **Manage Tickers**: Use "Manage Tickers" to add/remove symbols
4. **Analyze Results**: Review sorted results with best opportunities at the top

## Strategy Overview

The application implements a **premium selling strategy** focused on:

1. **Negative Premium Puts**: Options where you receive more premium than the potential loss
2. **Below-Market Strikes**: Target prices below current market value
3. **Quality Underlying Assets**: Focus on stocks/ETFs you wouldn't mind owning
4. **Time Decay Advantage**: Shorter-term options for faster premium capture

### Example Opportunity
```
NVDL: 95.00 @ $17.20 (12/19)
- Current Price: $86.43
- Premium Received: $17.20
- Net Cost if Assigned: $77.80 (10% below current)
- Profit if Expires: $17.20 (18.1% yield)
```

## Development

### Contributing
1. Fork the repository
2. Create a feature branch
3. Implement improvements
4. Test thoroughly
5. Submit pull request

### Testing
```bash
python -m pytest tests/
```

### Future Enhancements
- [ ] Historical performance tracking
- [ ] Risk management tools
- [ ] Multiple broker support
- [ ] Mobile interface
- [ ] Automated trade execution

## License

MIT License - See LICENSE file for details

## Disclaimer

This software is for educational and informational purposes only. Options trading involves substantial risk. Past performance does not guarantee future results. Always consult with a qualified financial advisor before making investment decisions.

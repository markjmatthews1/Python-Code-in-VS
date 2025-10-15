# Enhanced Day Trader v2.0 🚀

A sophisticated day trading system with real-time signal generation, paper trading, and beautiful colorful displays.

## Features ✨

- **Real-time Signal Generation**: Uses Schwab API for live market data
- **Sector ETF Focus**: Trades 25 carefully selected sector ETFs
- **Paper Trading Engine**: Complete trade lifecycle management
- **Risk Management**: Professional position sizing and risk controls
- **Colorful Displays**: Beautiful Arial 12+ font interface
- **Performance Tracking**: Comprehensive trade and P&L analytics

## Quick Start 🏃‍♂️

### 1. Test the System
```bash
python test_system.py
```

### 2. Run the Full Application
```bash
python main_trader.py
```

### 3. Individual Components
```bash
# Just the signals
python live_signals.py

# Just the paper trader
python core/paper_trader.py

# Just the display
python ui/trade_display.py
```

## System Architecture 🏗️

```
enhanced_day_trader/
├── main_trader.py          # Main application entry point
├── live_signals.py         # Real-time signal generation
├── test_system.py          # Test suite with sample trades
├── dashboard.py            # Web dashboard (legacy)
├── core/
│   ├── paper_trader.py     # Paper trading engine
│   └── risk_manager.py     # Risk management system
├── data/
│   └── schwab_market_data.py # Schwab API integration
└── ui/
    └── trade_display.py    # Colorful trade display
```

## Key Components 🔧

### Signal Generation
- **Watchlist**: 25 sector ETFs (XLK, XLF, XLV, XLE, etc.)
- **Indicators**: RSI, MACD, volume, price action
- **Minimum Signal Strength**: 50% (0.5)
- **Scan Frequency**: Every 60 seconds

### Risk Management
- **Account Size**: $10,000 paper trading
- **Risk per Trade**: 0.5% maximum
- **Position Size**: Dynamically calculated
- **Maximum Position**: 20% of account
- **Daily Risk Limit**: 2.5% of account

### Paper Trading Engine
- **Trade Tracking**: Complete lifecycle management
- **Stop Loss/Take Profit**: Automated monitoring
- **Performance Metrics**: Win rate, profit factor, P&L
- **Data Persistence**: JSON storage with CSV export
- **Commission**: $0.65 per trade (Schwab rates)

### Trade Display Features
- **Colorful Interface**: Dark theme with color-coded P&L
- **Arial 12+ Fonts**: Excellent readability
- **Real-time Updates**: 5-second refresh cycle
- **Performance Summary**: Balance, P&L, win rate
- **Active Positions**: Live unrealized P&L
- **Trade History**: Complete closed trade details

## Trade Tracking 📊

The system tracks comprehensive trade data:

- **Trade ID**: Unique identifier
- **Ticker**: Symbol traded
- **Direction**: LONG/SHORT
- **Quantity**: Number of shares
- **Entry/Exit Prices**: Actual execution prices
- **Open/Close Times**: Precise timestamps
- **Signal Strength**: Quality score (0.5-1.0)
- **Stop Loss/Take Profit**: Risk management levels
- **P&L**: Dollar and percentage returns
- **Status**: OPEN, CLOSED_TAKE_PROFIT, CLOSED_STOP_LOSS, etc.

## Display Colors 🎨

- **🟢 Profits**: Bright green (#00ff88)
- **🔴 Losses**: Red (#ff4444)
- **🔵 Neutral**: Blue (#4488ff)
- **🟠 Warnings**: Orange (#ffaa00)
- **🟣 Accents**: Purple (#aa44ff)
- **⚫ Background**: Dark theme (#1e1e1e)

## Performance Metrics 📈

The system calculates:

- **Current Balance**: Real-time account value
- **Total P&L**: Cumulative profit/loss
- **Today's P&L**: Daily performance
- **Win Rate**: Percentage of profitable trades
- **Average Win/Loss**: Mean profit/loss per trade
- **Profit Factor**: Total wins ÷ total losses
- **Active Positions**: Number of open trades
- **Total Trades**: Lifetime trade count

## Example Output 💻

```
🚀 ENHANCED DAY TRADER v2.0 🚀

📊 Sector ETF Watchlist: 25 securities
🔗 Market Data: Schwab API with live quotes
💰 Account Size: $10,000 paper trading
⚡ Risk Management: 0.5% per trade, 50% min signal strength
🎨 Display: Arial 12+ fonts with colorful interface

💰 Current Portfolio Status:
   Balance: $10,000.00
   Total P&L: +0.00 (+0.0%)
   Win Rate: 0.0%
   Active Positions: 0
   Total Trades: 0
```

## Integration with Schwab API 🔗

The system uses your existing Schwab authentication:
- **tokens.json**: OAuth tokens
- **Schwab_auth.py**: Authentication functions
- **Real-time Quotes**: Live market data
- **1-minute OHLCV**: Historical price data

## Files Generated 📁

- **paper_trades.json**: Trade data storage
- **paper_trades_YYYYMMDD_HHMMSS.csv**: Trade export
- **enhanced_day_trader.log**: Application logs
- **dashboard_debug.log**: Debug information

## Safety Features 🛡️

- **Paper Trading Only**: No real money at risk
- **Position Size Limits**: Prevents oversized trades
- **Stop Loss Protection**: Automatic risk management
- **Balance Validation**: Prevents overdraft
- **Error Handling**: Robust exception management

## Future Enhancements 🔮

- Live trading integration (with safety controls)
- Additional technical indicators
- Machine learning signal enhancement
- Portfolio optimization algorithms
- Real-time news sentiment analysis

---

**Built with ❤️ by GitHub Copilot**

*Trade responsibly. Past performance does not guarantee future results.*
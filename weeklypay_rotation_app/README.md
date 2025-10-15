# WeeklyPay™ Rotation App

A real-time rotation signal system for WeeklyPay™ ETFs with colorful GUI interface.

## Project Structure
```
weeklypay_rotation_app/
├── PROJECT_PLAN.md          # Strategic plan and requirements
├── README.md               # This file
├── requirements.txt        # Python dependencies
├── src/                   # Main application code
│   ├── __init__.py
│   ├── signal_engine.py   # Core rotation logic
│   ├── data_collector.py  # Real-time data collection
│   ├── gui_interface.py   # Colorful GUI with green/red signals
│   └── config.py         # Configuration settings
├── data/                 # Data storage
│   ├── etf_list.json    # Tracked ETFs configuration
│   └── state.db         # SQLite database for state tracking
├── tests/               # Unit tests
└── docs/               # Documentation
```

## Phase 1: Signal Engine (Core Logic)
- ✅ Project structure created
- ⏳ ETF tracking configuration
- ⏳ Earnings calendar monitoring
- ⏳ Sector momentum analysis (RSI/SMA)
- ⏳ Weekly dividend payout tracking
- ⏳ Rotation alert generation

## Requirements
- Font: Arial 12
- Interface: GUI (no web dashboards)
- Colors: Colorful interface (no black and white)
- Signals: Clear Green (rotate in) and Red (rotate out)
- Data: Real-time data only (no simulated data)

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Configure ETFs in `data/etf_list.json`
3. Run the application: `python src/main.py`

## Collaboration Notes
This project is designed for collaboration between Claude and Copilot to build a robust WeeklyPay™ rotation system.
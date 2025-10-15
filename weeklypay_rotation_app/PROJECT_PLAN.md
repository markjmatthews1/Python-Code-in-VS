Strategic Plan: WeeklyPay™ Rotation App
Basic app requirements:
    All output should have the following
        Font: Arial 12
        Interface: Gui no web dashboards
        Gui: needs to be colorful no black and white 
        Gui: Clear Green rotate in and Red rotate out signals
        Data: must be realtime data no guess or simulated data for outputs.

Phase 1: Signal Engine (Core Logic)
This is the brain of the system. It doesn't need APIs yet—just logic and data.
Goals:
- Track WeeklyPay™ ETFs (e.g., NVDW, AMDW, HOOW, MSFW, GOOW)
- Monitor:
- Earnings calendar (manual scrape or free API)
- Sector momentum (RSI/SMA on SMH, XLC, XLK)
- Weekly dividend payouts (manual scrape from Roundhill site or E*TRADE calendar)
- Generate rotation alerts:
- "Rotate out of AMDW → into HOOW (Meta earnings tomorrow)"
- "Sector RSI > 60 → rotate into NVDW"
Tools:
- Python + Pandas for logic
- SQLite or JSON for state tracking
- Claude for module generation and refactoring

Phase 2: Dashboard or Alert System
You decide how you want to receive signals.
Options:
- Simple CLI output (fastest)
- Streamlit dashboard (visual, interactive)
- Email or SMS alerts (via Zapier or Twilio)
This phase is optional but helps you act quickly without needing to open VS every time.

Phase 3: Trade Execution (Optional Later)
If you want to automate trades later, this is where Schwab/E*TRADE APIs come in.
Challenges:
- Limited data from APIs (no dividend calendar, no ETF-specific metrics)
- Execution only—no deep analytics
Workaround:
- Use the app to generate trade signals
- Manually execute via Schwab/E*TRADE
- Or build basic buy/sell wrappers using your existing auth setup

🧠 Tactical Fit for You
This plan gives you:
- Fast deployment (Phase 1 can be built in a day or two)
- Full control (manual execution with smart alerts)
- Scalable logic (add more ETFs, overlays, or filters anytime)
- No paid data dependency (use free sources + manual inputs)

🔧 Suggested Starting Point
Let's begin by defining:
- The list of ETFs you want to track (e.g., NVDW, AMDW, HOOW, MSFW, GOOW)
- The rotation rules:
- Earnings week = rotate in
- Sector RSI > 60 = rotate in
- Weekly payout > 0.5% NAV = rotate in
- RSI < 40 or post-earnings = rotate out
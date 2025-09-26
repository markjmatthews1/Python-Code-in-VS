# Enhanced Day Trading System - Quick Reference Guide

## 🚀 DAILY OPERATIONS CHECKLIST

### ⏰ **Pre-Market (8:30 AM - 9:30 AM)**
- [ ] Check system logs for overnight issues
- [ ] Verify both dashboards accessible (Original: 8050, Enhanced: 8051)
- [ ] Review yesterday's performance metrics
- [ ] Check account balances and risk limits

### 🎯 **Market Open (9:30 AM - 10:00 AM)**
- [ ] **DO NOT TRADE** - Enhanced system avoids this period
- [ ] Monitor market conditions
- [ ] Let systems initialize and gather data

### 📈 **Active Trading (10:00 AM - 11:30 AM, 1:30 PM - 3:30 PM)**
- [ ] Monitor enhanced system signals
- [ ] Compare with original system signals
- [ ] Watch for ensemble confirmations (need 2+)
- [ ] Track win rate vs 60-70% target

### 🔒 **Post-Market (4:00 PM+)**
- [ ] Review day's trading performance
- [ ] Check risk management effectiveness
- [ ] Update performance tracking
- [ ] Plan any needed adjustments

---

## 🎛️ QUICK COMMANDS

### **Start Systems:**
```bash
# Original System
cd "C:\Users\mjmat\Python Code in VS"
python day.py

# Enhanced System  
cd "C:\Users\mjmat\Python Code in VS\enhanced_day_trader"
python main.py

# Or use E*Trade Menu Option 5: "🚀 Enhanced Day Trading System"
```

### **Check System Status:**
```bash
# View Enhanced System Logs
cd enhanced_day_trader
type enhanced_trader.log

# Check Configuration
python -c "from config.trading_config import get_config_summary; print(get_config_summary())"
```

---

## 📊 KEY PERFORMANCE METRICS

| Metric | Enhanced Target | Original Actual |
|--------|----------------|-----------------|
| **Win Rate** | 60-70% | 24% |
| **Risk/Reward** | 2:1 | 1:2 |
| **Breakeven** | 33% | 67% |
| **Daily Trades** | 3-8 (quality) | 10+ (quantity) |

---

## 🚨 EMERGENCY PROCEDURES

### **If Enhanced System Fails:**
1. Stop enhanced system: `Ctrl+C` in terminal
2. Ensure original system still running
3. Check logs: `enhanced_day_trader/enhanced_trader.log`
4. Restart if minor issue, investigate if major

### **If Original System Needs Restart:**
1. Enhanced system continues independently
2. Restart original: `python day.py`
3. Both systems now running on different ports

---

## 📱 DASHBOARD ACCESS

- **Original System:** http://localhost:8050
- **Enhanced System:** http://localhost:8051
- **Both can run simultaneously**

---

## 🔧 QUICK TROUBLESHOOTING

| Problem | Solution |
|---------|----------|
| Port in use | Enhanced uses 8051, original uses 8050 |
| No signals | Check time (only trades 10-11:30, 1:30-3:30) |
| Auth error | Verify Schwab_auth.py and etrade_auth.py exist |
| Model missing | System will auto-train new model |
| Low win rate | Review recent trades, may need retraining |

---

## 📋 WEEKLY REVIEW TEMPLATE

**Week of: _______________**

### Performance Summary:
- Enhanced Win Rate: ____% (Target: 60-70%)
- Original Win Rate: ____% (Baseline: 24%)
- Enhanced Daily P&L: $______
- Original Daily P&L: $______

### Issues Encountered:
- [ ] None
- [ ] Technical issues: _______________
- [ ] Performance issues: _______________
- [ ] Other: _______________

### Actions Taken:
- [ ] Parameter adjustments
- [ ] Model retraining
- [ ] Configuration changes
- [ ] Other: _______________

### Next Week Focus:
- [ ] Continue monitoring
- [ ] Increase position sizes
- [ ] Add new features
- [ ] Other: _______________

---

This quick reference guide should be kept handy for daily operations!
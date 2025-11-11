# Development Files Archive

## Date Archived: November 11, 2025

This directory contains development, testing, and obsolete files that were removed from the main WeeklyPay rotation app directory to keep it clean and maintainable.

---

## 📁 Archived Files Summary

### Test Scripts (11 files)
All test scripts moved to archive as they were development/validation tools:

- `test_backtest.py` - Backtest validation script
- `test_dashboard_compatibility.py` - Dashboard compatibility tests
- `test_display_logic.py` - Display logic validation
- `test_gui_launch.py` - GUI launch tests
- `test_gui_simple.py` - Simple GUI tests
- `test_holdings_categorization.py` - Holdings categorization tests
- `test_multiple_categories.py` - Multi-category logic tests
- `test_next_group_logic.py` - Next rotation group tests
- `test_rotation_engine.py` - Rotation engine tests
- `test_rotation_simulation.py` - Rotation simulation tests
- `test_timezone_fix.py` - Timezone fix validation

### Debug/Verification Scripts (3 files)
- `debug_holdings.py` - Holdings debugging tool
- `quick_verify.py` - Quick verification script
- `verify_config.py` - Configuration verification

### Simulation Scripts (3 files)
Day trading simulation experiments (not part of core rotation strategy):

- `pick_of_the_day_sim.py` - Pick of day simulation
- `pick_parameter_sweep.py` - Parameter sweep analysis
- `pick_premarket_sim.py` - Premarket simulation

### Strategy Experiments (3 files)
Alternative trading strategies (not implemented in production):

- `high_probability_day_trading.py` - High probability day trading experiment
- `ultra_selective_day_trading.py` - Ultra selective day trading experiment
- `scale_out_strategy.py` - Scale out strategy experiment

### Obsolete Dashboard Versions (4 files)
Older dashboard versions replaced by current production files:

- `enhanced_dashboard.py` - Replaced by `simple_dashboard.py`
- `enhanced_earnings_calendar.py` - Integrated into main dashboard
- `streamlit_dashboard.py` - Consolidated into `simple_dashboard.py`
- `comprehensive_earnings_calendar.py` - Earnings features now in main app

### Output/Signal Files (4 files)
Old demo and signal output files:

- `phase2_demo_output.json` - Phase 2 demo output
- `step2_2_demo_output.json` - Step 2.2 demo output
- `step2_3_demo_output.json` - Step 2.3 demo output
- `rotation_signals.json` - Old rotation signals
- `rotation_signals_output.json` - Old rotation signals output

### Miscellaneous (1 file)
- `ROTATION_UPDATE_SUMMARY.py` - Old update summary script

---

## 📚 Old Documentation (20 files in old_docs/)

Historical documentation moved to `old_docs/` subdirectory:

### Step/Phase Completion Docs
- `STEP1_COMPLETE.md`
- `PHASE2_COMPLETE.md`
- `CORE_SIGNAL_ENGINE_COMPLETE.md`

### Fix/Update Summaries
- `ANALYZER_FIX.md`
- `CHART_FIX_INSTRUCTIONS.md`
- `CSV_LOCATION_FIX.md`
- `CUMULATIVE_PL_FIX_COMPLETE.md`
- `NAV_EROSION_FIX_COMPLETE.md`
- `PERFORMANCE_DASHBOARD_FIX.md`
- `TICKER_UPDATE_COMPLETE.md`
- `TRADE_TRACKING_FIX_SUMMARY.md`
- `WEEKLY_ETF_UPDATE_SUMMARY.md`
- `SCALE_OUT_STRATEGY_SUMMARY.md`
- `EDIT_FEATURE_SUMMARY.md`

### Project Planning/Summary Docs
- `PROJECT_PLAN.md`
- `TESTING_PLAN_OCT7_2025.md`
- `COMPLETE_PROJECT_SUMMARY.md`
- `CLAUDE_ENHANCEMENTS_COMPLETE.md`
- `integration_notes.md`
- `WeeklyPay_Rotation_App.txt`

---

## ✅ Current Production Files (Remain in Main Directory)

### Core Application Files
- `simple_dashboard.py` - **Main Streamlit web dashboard**
- `tkinter_dashboard.py` - **Desktop GUI version**
- `rotation_engine.py` - **Core rotation logic**
- `settings_manager.py` - **Settings management**
- `weeklypay_settings.py` - **Settings configuration**

### Utilities
- `trade_analyzer.py` - Trade analysis tool
- `trade_diagnostic_tool.py` - Trade diagnostics
- `manual_data_entry_gui.py` - Manual data entry interface
- `exit_window_monitor.py` - Exit window monitoring
- `weeklypay_cli.py` - Command-line interface

### Launchers
- `launch_dashboard.bat` - Dashboard launcher (Windows)
- `launch_dashboard.py` - Dashboard launcher (Python)
- `launch_settings.bat` - Settings GUI launcher
- `launch_trade_diagnostic.bat` - Trade diagnostic launcher
- `create_desktop_shortcut.bat` - Desktop shortcut creator

### Current Documentation
- `README.md` - Main project README
- `HOW_TO_LAUNCH.md` - Launch instructions
- `ROTATION_MODE_FEATURES.md` - Rotation mode features
- `ROTATION_QUICK_REFERENCE.md` - Quick reference guide
- `SETTINGS_GUI_README.md` - Settings GUI documentation
- `MANUAL_DATA_ENTRY_README.md` - Manual data entry guide
- `TRADE_EDIT_GUIDE.md` - Trade editing guide
- `TRADE_MANAGER_BUTTON.md` - Trade manager documentation
- `TKINTER_DASHBOARD_UPDATES.md` - Recent desktop GUI updates

### Data Files
- `weeklypay_trades.csv` - **Trade history (ACTIVE)**
- `earnings_cache.json` - Earnings cache
- `requirements.txt` - Python dependencies

---

## 🗑️ Safe to Delete?

**NO** - Keep this archive for reference. These files document:
- Development history
- Test methodology
- Feature evolution
- Debugging approaches
- Experimental strategies

If disk space is needed in the future, this entire `archive_dev_files/` directory can be safely deleted or moved to external storage, as none of these files are required for production operation.

---

## 📌 Notes

1. **Testing**: All test files were kept for historical reference but are not part of the test suite (the `tests/` directory in main folder is empty)

2. **Simulation Scripts**: Day trading simulations were experimental and not implemented in production

3. **Dashboard Evolution**: 
   - Started with `enhanced_dashboard.py` and `streamlit_dashboard.py`
   - Consolidated into `simple_dashboard.py` (current production)
   - Desktop version: `tkinter_dashboard.py` (updated Nov 11, 2025)

4. **Documentation**: Old fix/update docs preserved for historical reference but superseded by current documentation

5. **Recovery**: If you need to restore any archived file, simply move it back to the main directory

---

## ✨ Clean Directory Benefits

- **Easier Navigation**: Only production files visible
- **Reduced Confusion**: No mix of old/new versions
- **Better Maintenance**: Clear what's active vs. archived
- **Professional Structure**: Clean codebase presentation
- **Faster Searches**: IDE searches focus on relevant files

---

*Archive created as part of codebase maintenance on November 11, 2025*

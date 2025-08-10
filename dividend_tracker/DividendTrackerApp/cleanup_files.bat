@echo off
echo 🧹 Cleaning up DividendTrackerApp directory...
echo Creating archive folder and moving old files...

:: Create archive folder with timestamp
set TIMESTAMP=%DATE:~10,4%%DATE:~4,2%%DATE:~7,2%_%TIME:~0,2%%TIME:~3,2%
set TIMESTAMP=%TIMESTAMP: =0%
set ARCHIVE_DIR=archive_%TIMESTAMP%

mkdir "%ARCHIVE_DIR%"
echo ✅ Created archive directory: %ARCHIVE_DIR%

:: Move fix files
echo.
echo 📁 Moving fix/repair files...
if exist "fix_dividend_sheet_accounts.py" move "fix_dividend_sheet_accounts.py" "%ARCHIVE_DIR%\"
if exist "fix_estimated_income_sheet.py" move "fix_estimated_income_sheet.py" "%ARCHIVE_DIR%\"
if exist "fix_estimated_income_totals.py" move "fix_estimated_income_totals.py" "%ARCHIVE_DIR%\"
if exist "fix_formatting.py" move "fix_formatting.py" "%ARCHIVE_DIR%\"
if exist "fix_monthly_dividends.py" move "fix_monthly_dividends.py" "%ARCHIVE_DIR%\"
if exist "fix_retiree_dashboard.py" move "fix_retiree_dashboard.py" "%ARCHIVE_DIR%\"
if exist "fix_retirement_dashboard.py" move "fix_retirement_dashboard.py" "%ARCHIVE_DIR%\"
if exist "fix_sheet_structure.py" move "fix_sheet_structure.py" "%ARCHIVE_DIR%\"
if exist "fix_summary_report.py" move "fix_summary_report.py" "%ARCHIVE_DIR%\"
if exist "fix_ticker_analysis_2025.py" move "fix_ticker_analysis_2025.py" "%ARCHIVE_DIR%\"
if exist "fix_ticker_analysis_structure.py" move "fix_ticker_analysis_structure.py" "%ARCHIVE_DIR%\"
if exist "fix_time_formatting.py" move "fix_time_formatting.py" "%ARCHIVE_DIR%\"
if exist "fix_totals.py" move "fix_totals.py" "%ARCHIVE_DIR%\"
if exist "fix_yield_update_logic.py" move "fix_yield_update_logic.py" "%ARCHIVE_DIR%\"
if exist "fixed_integration_code.py" move "fixed_integration_code.py" "%ARCHIVE_DIR%\"

:: Move test files
echo.
echo 🧪 Moving test files...
if exist "debug_popup_test.py" move "debug_popup_test.py" "%ARCHIVE_DIR%\"
if exist "minimal_dashboard_test.py" move "minimal_dashboard_test.py" "%ARCHIVE_DIR%\"
if exist "quick_test.py" move "quick_test.py" "%ARCHIVE_DIR%\"
if exist "test_401k_prompt.py" move "test_401k_prompt.py" "%ARCHIVE_DIR%\"
if exist "test_alpha_vantage.py" move "test_alpha_vantage.py" "%ARCHIVE_DIR%\"
if exist "test_automation_components.py" move "test_automation_components.py" "%ARCHIVE_DIR%\"
if exist "test_config.py" move "test_config.py" "%ARCHIVE_DIR%\"
if exist "test_console_display.py" move "test_console_display.py" "%ARCHIVE_DIR%\"
if exist "test_dashboard.py" move "test_dashboard.py" "%ARCHIVE_DIR%\"
if exist "test_data_loading.py" move "test_data_loading.py" "%ARCHIVE_DIR%\"
if exist "test_etrade_api.py" move "test_etrade_api.py" "%ARCHIVE_DIR%\"
if exist "test_fixed_popup.py" move "test_fixed_popup.py" "%ARCHIVE_DIR%\"
if exist "test_gui_popup.py" move "test_gui_popup.py" "%ARCHIVE_DIR%\"
if exist "test_gui_simple.py" move "test_gui_simple.py" "%ARCHIVE_DIR%\"
if exist "test_historical_data.py" move "test_historical_data.py" "%ARCHIVE_DIR%\"
if exist "test_popup.py" move "test_popup.py" "%ARCHIVE_DIR%\"
if exist "test_schwab_auth.py" move "test_schwab_auth.py" "%ARCHIVE_DIR%\"
if exist "test_schwab_simple.py" move "test_schwab_simple.py" "%ARCHIVE_DIR%\"
if exist "test_scraper.py" move "test_scraper.py" "%ARCHIVE_DIR%\"
if exist "test_simple_dashboard.py" move "test_simple_dashboard.py" "%ARCHIVE_DIR%\"
if exist "test_simple_popup.py" move "test_simple_popup.py" "%ARCHIVE_DIR%\"
if exist "test_simple_sidebyside.py" move "test_simple_sidebyside.py" "%ARCHIVE_DIR%\"
if exist "test_ticker_rebuild.py" move "test_ticker_rebuild.py" "%ARCHIVE_DIR%\"
if exist "test_two_columns.py" move "test_two_columns.py" "%ARCHIVE_DIR%\"

:: Move rebuild files
echo.
echo 🔧 Moving rebuild files...
if exist "rebuild_complete_portfolio.py" move "rebuild_complete_portfolio.py" "%ARCHIVE_DIR%\"
if exist "rebuild_correct_data.py" move "rebuild_correct_data.py" "%ARCHIVE_DIR%\"
if exist "rebuild_dividends_workbook.py" move "rebuild_dividends_workbook.py" "%ARCHIVE_DIR%\"
if exist "rebuild_estimated_income.py" move "rebuild_estimated_income.py" "%ARCHIVE_DIR%\"
if exist "rebuild_from_historical_data.py" move "rebuild_from_historical_data.py" "%ARCHIVE_DIR%\"
if exist "rebuild_ticker_analysis_clean.py" move "rebuild_ticker_analysis_clean.py" "%ARCHIVE_DIR%\"
if exist "rebuild_ticker_analysis_clean_with_account_header.py" move "rebuild_ticker_analysis_clean_with_account_header.py" "%ARCHIVE_DIR%\"
if exist "rebuild_ticker_analysis_with_all_accounts.py" move "rebuild_ticker_analysis_with_all_accounts.py" "%ARCHIVE_DIR%\"

:: Move integration files
echo.
echo 🔗 Moving integration files...
if exist "final_integration.py" move "final_integration.py" "%ARCHIVE_DIR%\"
if exist "final_dividend_cleanup.py" move "final_dividend_cleanup.py" "%ARCHIVE_DIR%\"
if exist "complete_ticker_integration.py" move "complete_ticker_integration.py" "%ARCHIVE_DIR%\"
if exist "integrated_ticker_update.py" move "integrated_ticker_update.py" "%ARCHIVE_DIR%\"

:: Move additional cleanup candidates
echo.
echo 📦 Moving additional cleanup files...
if exist "restore_historical_yield_progression.py" move "restore_historical_yield_progression.py" "%ARCHIVE_DIR%\"
if exist "verify_account_separation.py" move "verify_account_separation.py" "%ARCHIVE_DIR%\"
if exist "verify_comprehensive_integration.py" move "verify_comprehensive_integration.py" "%ARCHIVE_DIR%\"
if exist "verify_dashboard.py" move "verify_dashboard.py" "%ARCHIVE_DIR%\"
if exist "verify_historical_rebuild.py" move "verify_historical_rebuild.py" "%ARCHIVE_DIR%\"
if exist "verify_rebuilt_workbook.py" move "verify_rebuilt_workbook.py" "%ARCHIVE_DIR%\"
if exist "verify_totals.py" move "verify_totals.py" "%ARCHIVE_DIR%\"
if exist "force_totals.py" move "force_totals.py" "%ARCHIVE_DIR%\"
if exist "simple_check.py" move "simple_check.py" "%ARCHIVE_DIR%\"

:: Create README in archive folder
echo.
echo 📄 Creating archive documentation...
echo # Archive Created: %DATE% %TIME% > "%ARCHIVE_DIR%\README.md"
echo. >> "%ARCHIVE_DIR%\README.md"
echo This archive contains files that were cleaned up from the DividendTrackerApp directory. >> "%ARCHIVE_DIR%\README.md"
echo. >> "%ARCHIVE_DIR%\README.md"
echo ## File Categories: >> "%ARCHIVE_DIR%\README.md"
echo - **fix_*.py**: Files created to fix specific issues >> "%ARCHIVE_DIR%\README.md"
echo - **test_*.py**: Development and testing files >> "%ARCHIVE_DIR%\README.md"
echo - **rebuild_*.py**: Files for rebuilding data structures >> "%ARCHIVE_DIR%\README.md"
echo - **verify_*.py**: Verification and validation files >> "%ARCHIVE_DIR%\README.md"
echo - **integration files**: One-time migration files >> "%ARCHIVE_DIR%\README.md"
echo. >> "%ARCHIVE_DIR%\README.md"
echo These files were archived to reduce clutter while keeping them available for reference. >> "%ARCHIVE_DIR%\README.md"

:: Count files in archive
echo.
echo 📊 Cleanup Summary:
dir /b "%ARCHIVE_DIR%\*.py" 2>nul | find /c ".py" > temp_count.txt
set /p FILE_COUNT=<temp_count.txt
del temp_count.txt
echo    ✅ Files archived: %FILE_COUNT%
echo    📁 Archive location: %ARCHIVE_DIR%

echo.
echo 🎉 Cleanup completed! Your DividendTrackerApp directory is now much cleaner.
echo 💾 All files are safely stored in the archive folder.

pause

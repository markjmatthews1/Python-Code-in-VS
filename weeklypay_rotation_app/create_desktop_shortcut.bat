@echo off
echo.
echo ========================================
echo  Creating Desktop Shortcut
echo ========================================
echo.

set SCRIPT_DIR=%~dp0
set SCRIPT_PATH=%SCRIPT_DIR%trade_diagnostic_tool.py
set SHORTCUT_NAME=WeeklyPay Trade Tool

echo Creating shortcut on desktop...

powershell -Command "$WshShell = New-Object -comObject WScript.Shell; $Shortcut = $WshShell.CreateShortcut('%USERPROFILE%\Desktop\WeeklyPay Trade Tool.lnk'); $Shortcut.TargetPath = 'python'; $Shortcut.Arguments = '\"%SCRIPT_PATH%\"'; $Shortcut.WorkingDirectory = '%SCRIPT_DIR%'; $Shortcut.IconLocation = 'C:\Windows\System32\shell32.dll,43'; $Shortcut.Description = 'WeeklyPay Trade Diagnostic & Recovery Tool'; $Shortcut.Save()"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo  SUCCESS!
    echo ========================================
    echo.
    echo Desktop shortcut created!
    echo.
    echo You can now launch the Trade Diagnostic Tool
    echo by double-clicking the shortcut on your desktop.
    echo.
) else (
    echo.
    echo ERROR: Failed to create shortcut
    echo Please run this script as Administrator
    echo.
)

pause

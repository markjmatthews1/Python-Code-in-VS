@echo off
REM Compile day.py and run headless runner with correct quoting for paths with spaces.
SETLOCAL ENABLEDELAYEDEXPANSION
set "PROJECT_DIR=C:\Users\mjmat\Python Code in VS"
echo [%DATE% %TIME%] Compiling day.py...
python -m py_compile "%PROJECT_DIR%\day.py"
if errorlevel 1 (
  echo py_compile failed. See output above.
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Running headless runner...
python "%PROJECT_DIR%\scripts\run_headless_charts_retry.py"
if errorlevel 1 (
  echo headless runner failed. See output above.
  pause
  exit /b 1
)

echo [%DATE% %TIME%] Finished successfully.
pause
ENDLOCAL

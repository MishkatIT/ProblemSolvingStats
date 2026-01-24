@echo off
REM ProblemSolvingStats Batch Runner
REM This batch file helps run the ProblemSolvingStats scripts easily

echo ========================================
echo   ProblemSolvingStats Batch Runner
echo ========================================
echo.

REM Check if dependencies are installed (using system Python)
python -c "import requests, bs4, colorama, rich, selenium" 2>nul
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
    echo Dependencies installed.
) else (
    echo Dependencies already installed.
)

echo.
echo Ready to run scripts with system Python.
echo.

:menu
echo Choose an option:
echo 1. Run Auto Update (fetch and update README)
echo 2. Run Manual Update (enter stats manually)
echo 3. Configure Handles (setup profiles)
echo 4. Update README Only (regenerate README)
echo 5. Install/Update Dependencies
echo 6. Exit
echo.
set /p choice="Enter your choice (1-6): "

if "%choice%"=="1" goto auto_update
if "%choice%"=="2" goto manual_update
if "%choice%"=="3" goto configure_handles
if "%choice%"=="4" goto update_readme
if "%choice%"=="5" goto install_deps
if "%choice%"=="6" goto exit

echo Invalid choice. Please try again.
goto menu

:auto_update
echo Running Auto Update...
python scripts/auto_update.py
goto after_run

:manual_update
echo Running Manual Update...
python scripts/manual_update.py
goto after_run

:configure_handles
echo Running Configure Handles...
python scripts/configure_handles.py
goto after_run

:update_readme
echo Running Update README...
python scripts/update_readme.py
goto after_run

:install_deps
echo Installing/Updating Dependencies...
pip install -r requirements.txt
echo Dependencies updated.
goto after_run

:after_run
echo.
echo Press any key to return to menu...
pause >nul
goto menu

:exit
echo Goodbye!
pause
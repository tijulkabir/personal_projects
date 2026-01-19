@echo off
:: ═══════════════════════════════════════════════════════════════════════════════
:: Subscription Manager — Windows Installer
:: ByteFroster Edition v2.0.0
:: ═══════════════════════════════════════════════════════════════════════════════
setlocal EnableDelayedExpansion

:: Colors and styling (via ANSI codes on Windows 10+)
set "GREEN=[92m"
set "YELLOW=[93m"
set "RED=[91m"
set "CYAN=[96m"
set "RESET=[0m"
set "BOLD=[1m"

:: Get script directory
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: ───────────────────────────────────────────────────────────────────────────────
:: BANNER
:: ───────────────────────────────────────────────────────────────────────────────
echo.
echo %CYAN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %BOLD%%GREEN%   ___  _   _ ___  ___  ___ ___ ___ ___ _____ ___ ___  _  _ %RESET%
echo %BOLD%%GREEN%  / __^|^| ^| ^| ^| _ )/ __^|/ __^| _ \_ _^| _ \_   _^|_ _/ _ \^| \^| ^|%RESET%
echo %BOLD%%GREEN%  \__ \^| ^|_^| ^| _ \\__ ^\ (__^|   /^| ^|^|  _/ ^| ^|  ^| ^| (_) ^| .` ^|%RESET%
echo %BOLD%%GREEN%  ^|___/ \___/^|___/^|___/\___^|_^|_\___^|_^|   ^|_^| ^|___\___/^|_^|\_^|%RESET%
echo %BOLD%%GREEN%                     MANAGER v2.0.0%RESET%
echo %CYAN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo                        %YELLOW%ByteFroster Edition%RESET%
echo                   by Tijul Kabir Toha ^| tijulkabir.me
echo %CYAN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo.

:: ───────────────────────────────────────────────────────────────────────────────
:: CHECK PYTHON
:: ───────────────────────────────────────────────────────────────────────────────
echo %YELLOW%[1/5]%RESET% Checking for Python installation...

set "PYTHON_CMD="

:: Try py launcher first (most reliable on Windows)
py --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=py -3"
    for /f "tokens=2 delims= " %%v in ('py -3 --version 2^>^&1') do set "PY_VERSION=%%v"
    echo       %GREEN%✓%RESET% Found Python !PY_VERSION! via py launcher
    goto :python_found
)

:: Try python command
python --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python"
    for /f "tokens=2 delims= " %%v in ('python --version 2^>^&1') do set "PY_VERSION=%%v"
    echo       %GREEN%✓%RESET% Found Python !PY_VERSION!
    goto :python_found
)

:: Try python3 command
python3 --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=python3"
    for /f "tokens=2 delims= " %%v in ('python3 --version 2^>^&1') do set "PY_VERSION=%%v"
    echo       %GREEN%✓%RESET% Found Python !PY_VERSION!
    goto :python_found
)

:: Python not found
echo.
echo %RED%══════════════════════════════════════════════════════════════%RESET%
echo %RED%  ERROR: Python not found!%RESET%
echo %RED%══════════════════════════════════════════════════════════════%RESET%
echo.
echo   Please install Python 3.10 or newer from:
echo   %CYAN%https://www.python.org/downloads/%RESET%
echo.
echo   %YELLOW%TIP: During installation, check "Add Python to PATH"%RESET%
echo.
pause
exit /b 1

:python_found

:: ───────────────────────────────────────────────────────────────────────────────
:: CREATE VIRTUAL ENVIRONMENT
:: ───────────────────────────────────────────────────────────────────────────────
echo.
echo %YELLOW%[2/5]%RESET% Setting up virtual environment...

if exist ".venv\Scripts\python.exe" (
    echo       %GREEN%✓%RESET% Virtual environment already exists
) else (
    echo       Creating new virtual environment...
    %PYTHON_CMD% -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo       %RED%✗ Failed to create virtual environment%RESET%
        pause
        exit /b 1
    )
    echo       %GREEN%✓%RESET% Virtual environment created
)

:: ───────────────────────────────────────────────────────────────────────────────
:: INSTALL DEPENDENCIES
:: ───────────────────────────────────────────────────────────────────────────────
echo.
echo %YELLOW%[3/5]%RESET% Installing dependencies...
echo       This may take a few minutes on first install...
echo.

".venv\Scripts\pip.exe" install --upgrade pip >nul 2>&1
".venv\Scripts\pip.exe" install -r requirements.txt

if %ERRORLEVEL% neq 0 (
    echo.
    echo       %RED%✗ Failed to install dependencies%RESET%
    echo       Please check your internet connection and try again.
    pause
    exit /b 1
)

echo.
echo       %GREEN%✓%RESET% All dependencies installed

:: ───────────────────────────────────────────────────────────────────────────────
:: CREATE DESKTOP SHORTCUT
:: ───────────────────────────────────────────────────────────────────────────────
echo.
echo %YELLOW%[4/5]%RESET% Creating desktop shortcut...

set "SHORTCUT_PATH=%USERPROFILE%\Desktop\Subscription Manager.lnk"
set "VBS_SCRIPT=%SCRIPT_DIR%run_silent.vbs"
set "ICON_PATH=%SCRIPT_DIR%bytefroster.ico"

:: Create shortcut using PowerShell
powershell -NoProfile -Command ^
    "$ws = New-Object -ComObject WScript.Shell; ^
     $sc = $ws.CreateShortcut('%SHORTCUT_PATH%'); ^
     $sc.TargetPath = '%VBS_SCRIPT%'; ^
     $sc.WorkingDirectory = '%SCRIPT_DIR%'; ^
     $sc.IconLocation = '%ICON_PATH%'; ^
     $sc.Description = 'Subscription Manager - ByteFroster Edition'; ^
     $sc.Save()"

if exist "%SHORTCUT_PATH%" (
    echo       %GREEN%✓%RESET% Desktop shortcut created
) else (
    echo       %YELLOW%! Could not create shortcut automatically%RESET%
    echo         You can manually run: run_silent.vbs
)

:: ───────────────────────────────────────────────────────────────────────────────
:: DONE
:: ───────────────────────────────────────────────────────────────────────────────
echo.
echo %YELLOW%[5/5]%RESET% Installation complete!

echo.
echo %GREEN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo %BOLD%%GREEN%  ✓ INSTALLATION SUCCESSFUL!%RESET%
echo %GREEN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo.
echo   You can now launch the app by:
echo.
echo     %CYAN%1.%RESET% Double-click the %BOLD%"Subscription Manager"%RESET% shortcut on your Desktop
echo     %CYAN%2.%RESET% Or run: %YELLOW%run_silent.vbs%RESET%
echo     %CYAN%3.%RESET% Or run: %YELLOW%.venv\Scripts\pythonw.exe subscription_manager.py%RESET%
echo.
echo   %CYAN%Data is stored in:%RESET% %%LOCALAPPDATA%%\SubscriptionManager
echo.
echo %GREEN%═══════════════════════════════════════════════════════════════════════════════%RESET%
echo.

:: Ask if user wants to launch now
set /p LAUNCH="Would you like to launch the app now? (Y/N): "
if /i "%LAUNCH%"=="Y" (
    echo.
    echo Starting Subscription Manager...
    start "" "%VBS_SCRIPT%"
)

echo.
echo Thank you for using Subscription Manager!
echo Visit %CYAN%https://github.com/tijulkabir/personal_projects%RESET% for updates.
echo.
pause

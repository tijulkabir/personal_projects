:: run.cmd - launcher for Subscription Manager (uses pythonw to hide console)
@echo off
setlocal

REM Adjust path to your venv relative to script - set to your actual venv folder if different
set VENV_REL=".venv\Scripts\pythonw.exe"

REM script file to run (relative to this run.cmd)
set APP_PY=subscription_manager.py

REM Determine script folder
set SCRIPT_DIR=%~dp0

REM Prefer packaged EXE (built by PyInstaller) if present
set DIST_EXE=dist\subscription_manager\subscription_manager.exe
if exist "%SCRIPT_DIR%%DIST_EXE%" (
    "%SCRIPT_DIR%%DIST_EXE%" %*
    exit /b %ERRORLEVEL%
)

REM Try venv pythonw first
if exist "%SCRIPT_DIR%%VENV_REL%" (
    "%SCRIPT_DIR%%VENV_REL%" "%SCRIPT_DIR%%APP_PY%" %*
    exit /b %ERRORLEVEL%
)

REM Try pythonw on PATH
where pythonw.exe >nul 2>&1
if %ERRORLEVEL%==0 (
    pythonw.exe "%SCRIPT_DIR%%APP_PY%" %*
    exit /b %ERRORLEVEL%
)

REM Nothing found
msg * "Could not find pythonw.exe. Please install Python or ensure .venv\\Scripts\\pythonw.exe exists."
exit /b 1

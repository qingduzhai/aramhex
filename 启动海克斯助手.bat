@echo off
setlocal
cd /d "%~dp0"

taskkill /F /IM AramHex.exe >nul 2>&1
taskkill /F /IM pythonw.exe >nul 2>&1

if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m lolhex
    exit /b 0
)

if exist "build\dist\AramHex\AramHex.exe" (
    start "" "build\dist\AramHex\AramHex.exe"
    exit /b 0
)

echo AramHex runtime not found.
pause

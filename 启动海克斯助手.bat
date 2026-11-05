@echo off
setlocal
cd /d "%~dp0"

if exist "build\dist\AramHex\AramHex.exe" (
    start "" "build\dist\AramHex\AramHex.exe"
    exit /b 0
)

if exist ".venv\Scripts\python.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m lolhex
    exit /b 0
)

echo 未找到助手运行环境。
pause

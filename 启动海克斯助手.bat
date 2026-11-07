@echo off
setlocal
cd /d "%~dp0"

:: 结束后台已有的旧实例（托盘驻留进程），确保每次双击都加载最新代码而非唤醒旧窗口
taskkill /F /IM AramHex.exe >nul 2>&1
powershell -NoProfile -Command "Get-CimInstance Win32_Process -Filter \"Name='pythonw.exe' OR Name='python.exe'\" | Where-Object { $_.CommandLine -match 'lolhex' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }" >nul 2>&1

:: 优先直接运行源码（.venv），无需等待打包即可 100% 实时生效最新改动
if exist ".venv\Scripts\pythonw.exe" (
    start "" ".venv\Scripts\pythonw.exe" -m lolhex
    exit /b 0
)

if exist "build\dist\AramHex\AramHex.exe" (
    start "" "build\dist\AramHex\AramHex.exe"
    exit /b 0
)

echo 未找到助手运行环境。
pause
@echo off
chcp 65001 >nul
cd /d "%~dp0"
py scripts\update_daily.py
echo.
pause

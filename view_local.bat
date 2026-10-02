@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 本機預覽：http://localhost:8000  （關閉此視窗即停止）
start "" http://localhost:8000/index.html
py -m http.server 8000

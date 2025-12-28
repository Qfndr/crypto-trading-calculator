@echo off
taskkill /F /IM python.exe >nul 2>&1
timeout /t 2 /nobreak >nul
copy /Y main_update.py main.py
del main_update.py
start "" "python" "main.py"

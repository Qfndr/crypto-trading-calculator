@echo off
cd /d "%~dp0"

timeout /t 2 /nobreak >nul

if not exist "%~dp0main_update.py" (
  echo Could Not Find "%~dp0main_update.py"
  pause
  exit /b 1
)

copy /Y "%~dp0main_update.py" "%~dp0main.py" >nul
del "%~dp0main_update.py" >nul

start "" /D "%~dp0" "%~dp0main.py"

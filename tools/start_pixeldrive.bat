@echo off
rem Starts (or safely restarts) the AI sprite sheet runner. See tools\start_pixeldrive.ps1.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_pixeldrive.ps1"
pause

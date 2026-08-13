@echo off
cd /d "%~dp0"
python triage.py
if errorlevel 1 pause

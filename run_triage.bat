@echo off
cd /d "%~dp0"
python triage.py >> triage.log 2>&1

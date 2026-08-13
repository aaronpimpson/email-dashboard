@echo off
echo A normal Chrome window will open.
echo 1. Log into your FIRST Google account.
echo 2. Avatar (top right) - "Add another account" - log into the rest.
echo 3. Close the Chrome window when all accounts are in.
set CHROME="C:\Program Files\Google\Chrome\Application\chrome.exe"
if not exist %CHROME% set CHROME="C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
%CHROME% --user-data-dir="%~dp0browser_profile" --no-first-run https://mail.google.com

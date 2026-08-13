#!/bin/bash
cd "$(dirname "$0")"
echo "A normal Chrome window will open."
echo "1. Log into your FIRST Google account."
echo "2. Avatar (top right) - 'Add another account' - log into the rest."
echo "3. Close the Chrome window when all accounts are in."
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" --user-data-dir="$(pwd)/browser_profile" --no-first-run https://mail.google.com

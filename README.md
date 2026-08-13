# Email Triage

A daily AI email assistant that runs entirely on your own computer. It reads the last 24 hours of your Gmail inboxes (multiple accounts), has Claude decide which emails are real humans waiting on you vs junk, and puts them on a local dashboard where you mark items Done or Ignore. Nothing you don't clear ever disappears, and your email never leaves your machine.

Works on Windows and Mac.

## Requirements

- Windows or macOS
- [Python 3.10+](https://www.python.org/downloads/) (on Windows, check "Add to PATH" during install; Macs can use the python.org installer or Homebrew)
- Google Chrome
- [Claude Code](https://claude.com/claude-code) installed and logged in (the triage step runs `claude -p`, no API key needed)

Windows users run the `.bat` files below; Mac users run the matching `.sh` files (first time: `chmod +x *.sh` in the folder).

## Setup

1. Install the one dependency:
   ```
   pip install playwright        (Windows)
   pip3 install playwright       (Mac)
   ```
2. Set your account count: open `scrape.py` and change `NUM_ACCOUNTS` at the top (default 4).
3. Run `setup_login.bat` (Windows) or `./setup_login.sh` (Mac). A Chrome window opens with a fresh profile: log into your first Google account, then avatar (top right) > "Add another account" for the rest. Close Chrome when done. You only do this once; sessions last months.
   (Login happens in real Chrome on purpose. Google blocks logins inside automation browsers.)
4. Run `run_triage.bat` / `./run_triage.sh`. It scrapes the last 24h, triages with Claude, and opens the dashboard at http://127.0.0.1:8377.

## Daily automation

**Windows** - run once in PowerShell for a fresh triage every morning at 6am:

```
schtasks /create /tn "EmailTriageDaily" /tr "C:\path\to\email-triage\run_triage.bat" /sc daily /st 06:00
```

**Mac** - run `crontab -e` and add:

```
0 6 * * * /path/to/email-triage/run_triage.sh
```

## Dashboard

- Tabs: PENDING / DONE / IGNORED
- Every item links straight to the email in the right account
- DONE and IGNORE are permanent (the daily scan never resurfaces a cleared thread); RESTORE undoes
- Open it anytime with `dashboard.bat` / `./dashboard.sh`

## Your inbox command center, anywhere on earth (optional, free)

Tailscale creates a private network between your devices, so you can pull up the dashboard from your phone at a coffee shop, the airport, wherever, while it stays completely invisible to the rest of the internet. No hosting, no cloud, your own machine serving only you.

1. Install Tailscale on your computer (`winget install Tailscale.Tailscale` on Windows, `brew install --cask tailscale` on Mac, or from [tailscale.com](https://tailscale.com)) and log in (free personal account).
2. Install the Tailscale app on your phone, sign into the SAME account, and turn its VPN toggle on.
3. On the computer, run:
   ```
   tailscale serve --bg 8377
   ```
   The first time, it prints a link to enable serving on your tailnet. Open it, click enable, then run the command again.
4. It prints your private `https://...ts.net` URL. Bookmark that on your phone.

Requirements on the go: phone's Tailscale toggle on, and your computer at home powered on.

**"Address not found" on your phone?** In order:
1. Make sure the phone's Tailscale app is signed into the SAME account as the computer. A different account means your computer is invisible.
2. Check the app's VPN toggle is ON (it should say Connected).
3. Look at the app's device list: your computer's name should be there. If it is, reload the URL.
4. Still nothing? Toggle the VPN off and back on, which forces DNS to refresh.

## If an account stops scraping

The dashboard's "last scan" note will say `logged_out`. Just run the login setup again and log back into that account.

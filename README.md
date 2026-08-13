# Email Triage

A daily AI email assistant that runs entirely on your own PC. It reads the last 24 hours of your Gmail inboxes (multiple accounts), has Claude decide which emails are real humans waiting on you vs junk, and puts them on a local dashboard where you mark items Done or Ignore. Nothing you don't clear ever disappears, and your email never leaves your machine.

## Requirements

- Windows
- [Python 3.10+](https://www.python.org/downloads/) (check "Add to PATH" during install)
- Google Chrome
- [Claude Code](https://claude.com/claude-code) installed and logged in (the triage step runs `claude -p`, no API key needed)

## Setup

1. Install the one dependency:
   ```
   pip install playwright
   ```
2. Set your account count: open `scrape.py` and change `NUM_ACCOUNTS` at the top (default 4).
3. Double-click `setup_login.bat`. A Chrome window opens with a fresh profile: log into your first Google account, then avatar (top right) > "Add another account" for the rest. Close Chrome when done. You only do this once; sessions last months.
   (Login happens in real Chrome on purpose. Google blocks logins inside automation browsers.)
4. Double-click `run_triage.bat`. It scrapes the last 24h, triages with Claude, and opens the dashboard at http://127.0.0.1:8377.

## Daily automation

Run this once in PowerShell to get a fresh triage every morning at 6am:

```
schtasks /create /tn "EmailTriageDaily" /tr "C:\path\to\email-triage\run_triage.bat" /sc daily /st 06:00
```

## Dashboard

- Tabs: PENDING / DONE / IGNORED
- Every item links straight to the email in the right account
- DONE and IGNORE are permanent (the daily scan never resurfaces a cleared thread); RESTORE undoes
- Open it anytime with `dashboard.bat`

## Phone access (optional, free)

Tailscale creates a private network between your devices, so your phone can reach the dashboard from anywhere while it stays invisible to everyone else.

1. Install Tailscale on your PC (`winget install Tailscale.Tailscale` or from [tailscale.com](https://tailscale.com)) and log in (free personal account).
2. Install the Tailscale app on your phone, sign into the SAME account, and turn its VPN toggle on.
3. On the PC, run:
   ```
   tailscale serve --bg 8377
   ```
   The first time, it prints a link to enable serving on your tailnet. Open it, click enable, then run the command again.
4. It prints your private `https://...ts.net` URL. Bookmark that on your phone.

Requirements on the go: phone's Tailscale toggle on, and your PC at home powered on.

## If an account stops scraping

The dashboard's "last scan" note will say `logged_out`. Just run `setup_login.bat` again and log back into that account.

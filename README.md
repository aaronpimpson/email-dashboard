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

Install [Tailscale](https://tailscale.com) on your PC and phone, sign into both with the same account, then run:

```
tailscale serve --bg 8377
```

It prints a private https URL that works from your phone anywhere. Only your devices can reach it.

## If an account stops scraping

The dashboard's "last scan" note will say `logged_out`. Just run `setup_login.bat` again and log back into that account.

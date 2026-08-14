# Email Triage

A daily AI email assistant that runs entirely on your own computer. It reads the last 24 hours of your Gmail inboxes (multiple accounts), has Claude decide which emails are real humans waiting on you vs junk, and puts them on a local dashboard where you mark items Done or Ignore. Nothing you don't clear ever disappears, and your email never leaves your machine.

Works on Windows and Mac. Windows users run the `.bat` files; Mac users run the matching `.sh` files.

## What you need first

1. **Google Chrome** installed.
2. **Python 3.10+**
   - Windows: install from [python.org/downloads](https://www.python.org/downloads/) and CHECK THE "Add python.exe to PATH" BOX during install.
   - Mac: `brew install python` or the [python.org](https://www.python.org/downloads/) installer.
   - Test it: open a terminal and run `python --version` (Windows) or `python3 --version` (Mac). You should see a version number.
3. **Claude Code** with a Claude account (this does the AI triage, no API key needed):
   - Install: [claude.com/claude-code](https://claude.com/claude-code) (Windows: `winget install Anthropic.ClaudeCode`, Mac: `brew install --cask claude-code`)
   - Run `claude` once in a terminal and follow the login prompts.
   - Test it: `claude -p "say hi"` should answer in a few seconds.

## Setup (5 minutes)

1. Download this repo (green Code button > Download ZIP, or `git clone`) and unzip it somewhere permanent.
2. Open a terminal and install the one dependency:
   - Windows: `pip install playwright`
   - Mac: `pip3 install playwright`
3. Open `scrape.py` in any text editor and set `NUM_ACCOUNTS` at the top to how many Gmail accounts you have (default 5).
4. Log your Gmail accounts in (one time only):
   - Windows: double-click `setup_login.bat`
   - Mac: in a terminal in the folder, run `chmod +x *.sh` once, then `./setup_login.sh`
   - A fresh Chrome window opens. Log into your first Google account, then click your avatar (top right) > "Add another account" and repeat for the rest. When all accounts are in, close the Chrome window.
   - IMPORTANT: only ever log in through THIS window (it is real Chrome, which Google trusts). Sessions last months.
5. Run it:
   - Windows: double-click `run_triage.bat`
   - Mac: `./run_triage.sh`
   - You'll see each account scanned (`u/0: you@gmail.com [ok] 12 threads` etc.), then "Triaging with Claude...", then the dashboard opens at http://127.0.0.1:8377.
   - If the PENDING tab is empty: congratulations, nobody's waiting on you in the last 24 hours. Items only appear when a real human needs a reply.

## Make it daily

**Windows** — one PowerShell command (edit the path to where you unzipped):

```
schtasks /create /tn "EmailTriageDaily" /tr "C:\path\to\email-dashboard\run_triage.bat" /sc daily /st 06:00
```

**Mac** — run `crontab -e` and add (edit the path):

```
0 6 * * * /path/to/email-dashboard/run_triage.sh
```

Your computer needs to be on (not asleep) at that time; otherwise just run it manually whenever.

## Using the dashboard

- Tabs: PENDING / DONE / IGNORED, grouped by account
- Every item shows who, what they want, and links straight to the email in the right account
- DONE and IGNORE are permanent: once cleared, that thread never comes back, even if tomorrow's scan sees it again. RESTORE undoes.
- Cleared items quietly fall off the Done/Ignored tabs after 7 days, so they never pile up.
- Open it anytime: `dashboard.bat` (Windows) / `./dashboard.sh` (Mac)

## Your rules, in plain English (optional)

Teach the triage your personal law: copy `rules.example.txt` to `rules.txt` and write rules as normal sentences. The AI applies them on every scan and they override its default judgment. Examples:

- "Any email from Adobe Sign or DocuSign: always flag, mark URGENT" (never miss a contract again)
- "Never flag verification codes"
- Account-specific: "the contract rule does NOT apply to my personal account (me@gmail.com)"

No `rules.txt`? Everything works with the default judgment. Your rules stay on your machine (the file is gitignored).

## Your inbox command center, anywhere on earth (optional, free)

Tailscale creates a private network between your devices, so you can pull up the dashboard from your phone at a coffee shop, the airport, wherever, while it stays completely invisible to the rest of the internet. No hosting, no cloud, your own machine serving only you.

1. Install Tailscale on your computer (`winget install Tailscale.Tailscale` on Windows, `brew install --cask tailscale` on Mac, or from [tailscale.com](https://tailscale.com)) and log in (free personal account).
2. Install the Tailscale app on your phone, sign into the SAME account, and turn its VPN toggle on.
3. On the computer, run:
   ```
   tailscale serve --bg 8377
   ```
   The first time, it prints a link to enable serving on your tailnet. Open it, click enable, then run the command again.
4. It prints your private `https://...ts.net` URL. Open it on your phone and add it to your home screen.

## Troubleshooting

**Google won't log in / spins forever during setup**
You're logging in somewhere other than the setup window. Only log in via `setup_login.bat` / `setup_login.sh` — that's real Chrome. Google blocks logins from automated browsers.

**`pip` or `python` is "not recognized"**
Python isn't on your PATH. Windows: reinstall Python and check the "Add to PATH" box, or use `py -m pip install playwright`. Mac: use `pip3` / `python3`.

**`claude` is "not recognized" or triage fails**
Claude Code isn't installed or logged in. Run `claude` in a terminal and complete login, then test `claude -p "say hi"`.

**An account shows `logged_out` in the scan output**
That Google session expired. Run the login setup again and log back into that account. Everything else keeps working meanwhile.

**Dashboard page won't load at 127.0.0.1:8377**
The server isn't running. Run `dashboard.bat` / `./dashboard.sh` — it starts the server and opens the page.

**Phone says "address not found"**
1. The phone's Tailscale app must be signed into the SAME account as the computer — a different account makes your computer invisible.
2. The app's VPN toggle must be ON (it should say Connected).
3. Your computer must appear in the app's device list and be powered on.
4. Still nothing? Toggle the phone's VPN off and on to refresh DNS.

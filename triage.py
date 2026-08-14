"""Scrape the last 24h of email, have Claude triage, merge into the dashboard state."""
import json
import re
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

from dashboard import open_dashboard

BASE = Path(__file__).parent
STATE = BASE / "state.json"

PROMPT = """You are an email triage assistant. Below is JSON scraped from Aaron's Gmail inboxes
(multiple accounts, last 24 hours only). Decide which emails actually need a reply from him.

Rules:
- needs_reply: real humans asking him something, waiting on him, or time-sensitive threads.
- Ignore newsletters, receipts, notifications, promos, automated mail, and FYI-only threads.
- Weigh unread higher, but a read email can still need a reply.
- maybe: genuinely borderline only, max 3 per account.
- If an account's status is "logged_out", "duplicate", or an error, put that in its "note".
{user_rules}

Output ONLY valid JSON, no markdown fences, no commentary, exactly this shape:
{
  "accounts": [
    {
      "email": "account email",
      "note": "one-liner if logged_out/error, else null",
      "needs_reply": [
        {"thread_id": "copied from input", "date": "Aug 13", "sender": "Name",
         "subject": "Subject", "reason": "one line on what they want and why it needs him"}
      ],
      "maybe": [ same shape ]
    }
  ]
}
Do not use em dashes anywhere.

INBOX DATA:
"""


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"items": {}}


def main():
    print("Scraping last 24h...")
    r = subprocess.run([sys.executable, str(BASE / "scrape.py")], capture_output=True, text=True)
    print(r.stdout)
    if r.returncode != 0:
        print(r.stderr)
        sys.exit(1)

    inbox = (BASE / "inbox.json").read_text(encoding="utf-8")

    rules_file = BASE / "rules.txt"
    user_rules = ""
    if rules_file.exists() and rules_file.read_text(encoding="utf-8").strip():
        user_rules = (
            "\nUSER RULES (these override every default rule above):\n"
            + rules_file.read_text(encoding="utf-8").strip() + "\n"
        )

    print("Triaging with Claude...")
    result = subprocess.run(
        "claude -p",
        shell=True,
        input=PROMPT.replace("{user_rules}", user_rules) + inbox,
        capture_output=True,
        text=True,
        encoding="utf-8",
        timeout=600,
    )
    raw = (result.stdout or "").strip()
    if result.returncode != 0 or not raw:
        print("Claude triage failed:")
        print(result.stderr)
        sys.exit(1)
    raw = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw)
    data = json.loads(raw)

    # real email timestamps by thread id, from Gmail's date tooltip
    email_ts = {}
    for acc in json.loads(inbox)["accounts"]:
        for t in acc["threads"]:
            raw_date = (t.get("date") or "").replace(" ", " ").replace(" ", " ")
            try:
                email_ts[t["thread_id"]] = datetime.strptime(
                    raw_date, "%a, %b %d, %Y, %I:%M %p").isoformat(timespec="seconds")
            except ValueError:
                pass

    state = load_state()
    items = state["items"]

    cutoff = datetime.now() - timedelta(days=7)
    purged = 0
    for tid in list(items):
        it = items[tid]
        if it["status"] in ("done", "ignored"):
            resolved = it.get("resolved_at")
            if not resolved:
                it["resolved_at"] = datetime.now().isoformat(timespec="seconds")
            elif datetime.fromisoformat(resolved) < cutoff:
                del items[tid]
                purged += 1

    new = 0
    notes = []
    for acc in data.get("accounts", []):
        if acc.get("note"):
            notes.append(f"{acc.get('email') or '?'}: {acc['note']}")
        for bucket in ("needs_reply", "maybe"):
            for it in acc.get(bucket) or []:
                tid = it.get("thread_id")
                if not tid or tid in items:
                    continue
                items[tid] = {
                    "account": acc.get("email") or "unknown",
                    "date": it.get("date") or "",
                    "sender": it.get("sender") or "",
                    "subject": it.get("subject") or "",
                    "reason": it.get("reason") or "",
                    "bucket": bucket,
                    "status": "pending",
                    "added": datetime.now().isoformat(timespec="seconds"),
                    "sort_ts": email_ts.get(tid),
                }
                new += 1

    state["last_run"] = datetime.now().strftime("%a %b %d, %Y %I:%M %p")
    if notes:
        state["last_run"] += " (" + "; ".join(notes) + ")"
    STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
    pending = sum(1 for i in items.values() if i["status"] == "pending")
    print(f"{new} new item(s), {pending} pending total, {purged} aged off.")

    open_dashboard()


if __name__ == "__main__":
    main()

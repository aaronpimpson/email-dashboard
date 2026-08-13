"""Scrape Gmail inboxes for all logged-in accounts into inbox.json."""
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE = Path(__file__).parent
PROFILE_DIR = BASE / "browser_profile"
OUTPUT = BASE / "inbox.json"

NUM_ACCOUNTS = 4
MAX_THREADS = 40
HEADLESS = "--headed" not in sys.argv


def scrape_account(context, index, seen_emails):
    page = context.new_page()
    account = {"index": index, "email": None, "status": "ok", "threads": []}
    try:
        page.goto(f"https://mail.google.com/mail/u/{index}/#search/in:inbox+newer_than:1d", timeout=60000)
        page.wait_for_load_state("domcontentloaded")
        if "accounts.google.com" in page.url or "signin" in page.url.lower():
            account["status"] = "logged_out"
            return account
        try:
            page.wait_for_selector("tr.zA", timeout=20000)
        except Exception:
            pass  # no emails in the last 24h is a valid result

        title = page.title()
        m = re.search(r"[\w.+-]+@[\w.-]+", title)
        if m:
            account["email"] = m.group(0)
        if account["email"] and account["email"] in seen_emails:
            account["status"] = "duplicate"
            return account
        if account["email"]:
            seen_emails.add(account["email"])

        rows = page.query_selector_all("tr.zA")[:MAX_THREADS]
        for row in rows:
            cls = row.get_attribute("class") or ""
            sender_el = row.query_selector(".yW span[email]") or row.query_selector(".yW span")
            subject_el = row.query_selector(".bog")
            snippet_el = row.query_selector(".y2")
            date_el = row.query_selector("td.xW span")
            id_el = row.query_selector("[data-legacy-thread-id]")
            account["threads"].append({
                "thread_id": (id_el.get_attribute("data-legacy-thread-id") if id_el else None),
                "unread": "zE" in cls,
                "sender": (sender_el.inner_text().strip() if sender_el else ""),
                "sender_email": (sender_el.get_attribute("email") if sender_el else None),
                "subject": (subject_el.inner_text().strip() if subject_el else ""),
                "snippet": (snippet_el.inner_text().strip(" -–—") if snippet_el else ""),
                "date": (date_el.get_attribute("title") if date_el and date_el.get_attribute("title")
                         else (date_el.inner_text().strip() if date_el else "")),
            })
    except Exception as e:
        account["status"] = f"error: {e.__class__.__name__}: {e}"
    finally:
        page.close()
    return account


def main():
    data = {"scraped_at": datetime.now().isoformat(timespec="seconds"), "accounts": []}
    seen_emails = set()
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            str(PROFILE_DIR),
            channel="chrome",
            headless=HEADLESS,
            viewport={"width": 1280, "height": 900},
        )
        for i in range(NUM_ACCOUNTS):
            data["accounts"].append(scrape_account(context, i, seen_emails))
        context.close()

    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    for a in data["accounts"]:
        print(f"u/{a['index']}: {a['email'] or '?'} [{a['status']}] {len(a['threads'])} threads")


if __name__ == "__main__":
    main()

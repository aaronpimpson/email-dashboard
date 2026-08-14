"""Local dashboard server for the email triage state."""
import json
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

BASE = Path(__file__).parent
STATE = BASE / "state.json"
PORT = 8377


def load_state():
    if STATE.exists():
        return json.loads(STATE.read_text(encoding="utf-8"))
    return {"items": {}}


class Handler(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        data = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", f"{ctype}; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        if self.path == "/":
            self._send(200, (BASE / "dashboard.html").read_text(encoding="utf-8"), "text/html")
        elif self.path == "/api/state":
            self._send(200, json.dumps(load_state()))
        else:
            self._send(404, "{}")

    def do_POST(self):
        if self.path != "/api/update":
            self._send(404, "{}")
            return
        length = int(self.headers.get("Content-Length", 0))
        req = json.loads(self.rfile.read(length))
        state = load_state()
        item = state["items"].get(req.get("thread_id"))
        if item and req.get("status") in ("pending", "done", "ignored"):
            item["status"] = req["status"]
            if req["status"] in ("done", "ignored"):
                item["resolved_at"] = datetime.now().isoformat(timespec="seconds")
            else:
                item.pop("resolved_at", None)
            STATE.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")
            self._send(200, '{"ok": true}')
        else:
            self._send(400, '{"ok": false}')

    def log_message(self, *args):
        pass


if __name__ == "__main__":
    ThreadingHTTPServer(("127.0.0.1", PORT), Handler).serve_forever()

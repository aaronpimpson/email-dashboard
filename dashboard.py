"""Ensure the dashboard server is running and open it in the browser."""
import socket
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

BASE = Path(__file__).parent
PORT = 8377
CREATE_NO_WINDOW = 0x08000000


def server_running():
    with socket.socket() as s:
        s.settimeout(1)
        return s.connect_ex(("127.0.0.1", PORT)) == 0


def open_dashboard():
    if not server_running():
        subprocess.Popen(
            [sys.executable, str(BASE / "server.py")],
            creationflags=CREATE_NO_WINDOW,
        )
        for _ in range(20):
            if server_running():
                break
            time.sleep(0.25)
    webbrowser.open(f"http://127.0.0.1:{PORT}")


if __name__ == "__main__":
    open_dashboard()

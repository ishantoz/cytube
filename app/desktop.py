from __future__ import annotations

import html
import subprocess
import sys
import time
import urllib.error
import urllib.request

HOST = "127.0.0.1"
PORT = 8000
BASE_URL = f"http://{HOST}:{PORT}"
HOME_URL = f"{BASE_URL}/youtube"
WAIT_SECONDS = 10


class PortalError(Exception):
    pass


def portal_is_up() -> bool:
    try:
        with urllib.request.urlopen(HOME_URL, timeout=1) as response:
            return 200 <= response.status < 400
    except (urllib.error.URLError, TimeoutError, OSError):
        return False


def _start_daemon() -> subprocess.Popen[bytes]:
    return subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "app.main:app",
            "--host",
            HOST,
            "--port",
            str(PORT),
        ]
    )


def ensure_portal() -> tuple[str, subprocess.Popen[bytes] | None]:
    """Return (home_url, child). child is set only when this process started uvicorn."""
    if portal_is_up():
        return HOME_URL, None

    child = _start_daemon()
    deadline = time.monotonic() + WAIT_SECONDS
    while time.monotonic() < deadline:
        if portal_is_up():
            return HOME_URL, child
        if child.poll() is not None:
            break
        time.sleep(0.2)

    if child.poll() is None:
        child.terminate()
        try:
            child.wait(timeout=5)
        except subprocess.TimeoutExpired:
            child.kill()
    raise PortalError(
        f"Could not start the CyTube server at {BASE_URL}. "
        "Stop whatever is using that port, or start it with "
        "`uv run uvicorn app.main:app --host 127.0.0.1 --port 8000`."
    )


def _error_window(message: str) -> None:
    import webview

    body = html.escape(message)
    page = (
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
        "<title>CyTube</title></head><body style='font-family:sans-serif;padding:2rem'>"
        f"<h1>CyTube could not start</h1><p>{body}</p></body></html>"
    )
    webview.create_window("CyTube", html=page)
    webview.start()


def main() -> None:
    print(f"CyTube web UI: {BASE_URL}", flush=True)
    try:
        home, child = ensure_portal()
    except PortalError as error:
        print(error, file=sys.stderr)
        _error_window(str(error))
        raise SystemExit(1) from error

    import webview

    webview.create_window(f"CyTube — {BASE_URL}", home)
    try:
        webview.start()
    finally:
        if child is not None and child.poll() is None:
            child.terminate()
            try:
                child.wait(timeout=5)
            except subprocess.TimeoutExpired:
                child.kill()


if __name__ == "__main__":
    main()

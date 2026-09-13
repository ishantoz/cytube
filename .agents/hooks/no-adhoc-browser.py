#!/usr/bin/env python3
"""Block ad-hoc browser-driving scripts in shell commands.

Runs under two agent hosts from one file:

- Cursor  `beforeShellExecution`: stdin `{"command": ...}`,
  stdout `{"permission": "allow"|"ask"|"deny", ...}`
- Claude Code `PreToolUse` (matcher `Bash`, invoked with `--claude`): stdin
  `{"tool_name": "Bash", "tool_input": {"command": ...}}`, stdout
  `{"hookSpecificOutput": {"permissionDecision": ...}}`

Policy is identical on both; only the envelope differs.

Playwright MCP is this project's tool of record for UI inspection
(see `.agents/rules/browser-evidence.md`). Agents nonetheless tend to reach for
a throwaway `node .probe.mjs` that launches Chrome, measures a box, screenshots
a page, and gets deleted. This hook denies that.

Two signals, because the giveaway is not always in the command string:

1. The command text itself carries browser-launch code — heredocs that write a
   probe script, `node -e "...puppeteer..."`, or a direct headless Chrome call.
2. The command executes a script file whose *contents* carry browser-launch
   code. `node .probe.mjs` looks innocent until you read the file.

Committed gates are allowed by path. A tracked-but-unlisted script asks instead
of denying, so an approved new gate can still proceed with the user's consent.

Fails open: a bug here must not wedge every shell command.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Paths allowed to contain browser-launch code. This repo owns no browser gate
# today, so the list is just this hook and its tests, which must name the
# patterns they match. Extend it only alongside an approved spec step.
ALLOWED_SCRIPTS = {
    ".agents/hooks/no-adhoc-browser.py",
    ".agents/hooks/no-adhoc-browser.test.py",
}

# The sanctioned path: launching the Playwright MCP server itself.
SANCTIONED = re.compile(r"@playwright/mcp", re.I)

# Signals must mean "this launches a browser", not "this mentions a browser
# tool". A README or a comment naming Playwright is not a violation.
BROWSER_SIGNALS = (
    re.compile(
        r"""(?:require|from|import)\s*\(?\s*['"]"""
        r"""(?:puppeteer(?:-core)?|playwright(?:-core|-chromium)?"""
        r"""|chrome-remote-interface|chrome-launcher|selenium-webdriver)['"]""",
        re.I,
    ),
    re.compile(r"\bexecutablePath\b"),
    re.compile(r"\b(?:chromium|firefox|webkit|puppeteer|browser)\.launch\b", re.I),
    re.compile(r"\.newPage\s*\(", re.I),
    re.compile(r"\bpage\.(?:screenshot|goto|setViewport|evaluate)\b"),
    re.compile(r"--(?:headless|dump-dom|screenshot|remote-debugging-port)\b", re.I),
    re.compile(r"Google Chrome\.app/Contents/MacOS", re.I),
    re.compile(r"\b(?:npx|dlx)\s+(?:@?playwright|puppeteer)", re.I),
    re.compile(r"\bplaywright\s+(?:screenshot|pdf|codegen|open)\b", re.I),
    re.compile(r"\bchromedriver\b", re.I),
)

# Direct browser-binary invocation, e.g. a quoted Chrome.app path plus --headless.
BROWSER_BINARY = re.compile(r"(?:google[ _-]?chrome|chromium|msedge|brave)", re.I)
BROWSER_FLAG = re.compile(r"--(?:headless|screenshot|dump-dom|remote-debugging-port)\b", re.I)

RUNTIMES = {
    "node", "nodejs", "bun", "deno", "tsx", "ts-node",
    "python", "python3", "npx", "osascript",
}
BROWSERS = {"chrome", "chromium", "google-chrome", "msedge", "brave", "chrome.exe"}
PACKAGE_SUBCOMMANDS = {"install", "add", "i", "ci", "remove", "dlx", "exec", "why", "ls"}
PACKAGE_MANAGERS = {"npm", "pnpm", "yarn", "bun", "npx"}
SCRIPT_SUFFIXES = {".mjs", ".cjs", ".js", ".ts", ".py"}

MAX_READ = 256_000


def signals(text: str) -> list[str]:
    return [pattern.pattern for pattern in BROWSER_SIGNALS if pattern.search(text)]


def strip_comments(text: str) -> str:
    """Drop comments so prose about Playwright cannot look like Playwright code."""
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)  # /* ... */
    text = re.sub(r"(?<!:)//[^\n]*", " ", text)  # // ... but keep http://
    text = re.sub(r"(?m)^\s*#[^\n]*", " ", text)  # whole-line # comments
    text = re.sub(r'(?s)""".*?"""', " ", text)  # python docstrings
    return text


def segments(command: str) -> list[str]:
    return [part for part in re.split(r"&&|\|\||[;\n|]", command) if part.strip()]


def leading_program(segment: str) -> str:
    """First real program token, skipping env assignments and `(` subshells."""
    for token in segment.replace("(", " ").split():
        if "=" in token and not token.startswith("-") and "/" not in token.split("=")[0]:
            continue  # FOO=bar prefix
        return Path(token.strip("\"'")).name
    return ""


def is_package_command(segment: str) -> bool:
    tokens = [t for t in segment.split() if not t.startswith("-")]
    if not tokens:
        return False
    program = Path(tokens[0].strip("\"'")).name
    if program not in PACKAGE_MANAGERS:
        return False
    return any(t in PACKAGE_SUBCOMMANDS for t in tokens[1:3])


def script_targets(command: str) -> list[Path]:
    found: list[Path] = []
    for raw in re.findall(r"[\w./~@-]+", command):
        candidate = raw.strip("\"'")
        if Path(candidate).suffix not in SCRIPT_SUFFIXES:
            continue
        path = Path(candidate).expanduser()
        if not path.is_absolute():
            path = Path.cwd() / path
        try:
            if path.is_file() and path not in found:
                found.append(path)
        except OSError:
            continue
    return found


def relative(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def is_tracked(path: Path) -> bool:
    try:
        done = subprocess.run(
            ["git", "ls-files", "--error-unmatch", relative(path)],
            capture_output=True,
            timeout=5,
        )
        return done.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


CLAUDE_HOST = "--claude" in sys.argv[1:]


def respond(permission: str, user_message: str = "", agent_message: str = "") -> None:
    """Emit the verdict in whichever host protocol is active."""
    if CLAUDE_HOST:
        reason = " ".join(part for part in (user_message, agent_message) if part)
        payload: dict = {
            "hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "permissionDecision": permission,
                "permissionDecisionReason": reason,
            }
        }
    else:
        payload = {"permission": permission}
        if user_message:
            payload["user_message"] = user_message
        if agent_message:
            payload["agent_message"] = agent_message
    json.dump(payload, sys.stdout)
    sys.stdout.write("\n")
    sys.exit(0)


def read_command(raw: str) -> str | None:
    """Pull the shell command out of either host's stdin payload.

    Returns None when the payload is unparseable or is not a Bash tool call,
    which both mean "nothing for this hook to judge".
    """
    try:
        data = json.loads(raw) or {}
    except (json.JSONDecodeError, AttributeError):
        return None
    if not isinstance(data, dict):
        return None
    if CLAUDE_HOST:
        if data.get("tool_name") not in (None, "Bash"):
            return ""
        tool_input = data.get("tool_input")
        if isinstance(tool_input, dict) and tool_input.get("command"):
            return str(tool_input["command"])
    return str(data.get("command") or "")


GUIDANCE = (
    "Use the `playwright` MCP server instead. Start the admin app first "
    "(`pnpm dev`, http://127.0.0.1:3000) with iflow-backend reachable, then "
    "drive it with Playwright MCP. This repo owns no committed browser gate; "
    "adding one needs an approved spec step and an entry in ALLOWED_SCRIPTS. "
    "If Playwright MCP is unavailable in this session, say so instead of "
    "hand-rolling a browser script. Rule: .agents/rules/browser-evidence.md"
)


def main() -> None:
    command = read_command(sys.stdin.read())
    if command is None:
        respond("allow")
        return

    if not command.strip():
        respond("allow")
        return

    if SANCTIONED.search(command):
        respond("allow")

    parts = segments(command)
    runs_code = any(
        leading_program(part) in RUNTIMES or leading_program(part) in BROWSERS
        for part in parts
    )
    # A quoted browser path splits badly on whitespace, so match it directly.
    if BROWSER_BINARY.search(command) and BROWSER_FLAG.search(command):
        runs_code = True
    writes_file = bool(re.search(r"<<-?\s*['\"]?\w+|>>?\s*\S+|\btee\b", command))

    # Signal 1: browser code sitting in the command text (heredoc, -e, direct call).
    inline = signals(command)
    if inline and (runs_code or writes_file) and not all(
        is_package_command(part) for part in parts if signals(part)
    ):
        allowed = any(name in command for name in ALLOWED_SCRIPTS)
        if not allowed:
            respond(
                "deny",
                "Blocked an ad-hoc browser script. This project uses Playwright MCP "
                "for UI inspection and screenshots.",
                f"Denied: the command carries browser-launch code "
                f"({', '.join(inline[:3])}). {GUIDANCE}",
            )

    # Signal 2: it runs a script file whose contents drive a browser.
    if runs_code:
        for path in script_targets(command):
            rel = relative(path)
            if rel in ALLOWED_SCRIPTS:
                continue
            try:
                body = path.read_text(encoding="utf-8", errors="ignore")[:MAX_READ]
            except OSError:
                continue
            hits = signals(strip_comments(body))
            if not hits:
                continue
            if is_tracked(path):
                respond(
                    "ask",
                    f"`{rel}` drives a browser but is not a listed gate. Approve only "
                    "if this is an intended committed gate.",
                    f"`{rel}` contains browser-launch code ({', '.join(hits[:3])}) and is "
                    f"not in the allowlist. Prefer Playwright MCP; if this really is a new "
                    f"committed gate, it needs an approved spec step and an entry in "
                    f".cursor/hooks/no-adhoc-browser.py. {GUIDANCE}",
                )
            respond(
                "deny",
                f"Blocked `{rel}` — an untracked script that launches a browser. "
                "Use Playwright MCP for UI inspection.",
                f"Denied: `{rel}` is untracked and contains browser-launch code "
                f"({', '.join(hits[:3])}). {GUIDANCE}",
            )

    respond("allow")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:  # fail open; never wedge the session
        print(json.dumps({"permission": "allow", "agent_message": f"browser hook error: {error}"}))
        sys.exit(0)

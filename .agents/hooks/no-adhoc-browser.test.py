#!/usr/bin/env python3
"""Cases for the ad-hoc browser hook.

Every case runs twice: once through the Cursor `beforeShellExecution` envelope
and once through the Claude Code `PreToolUse` envelope (`--claude`). The verdict
must match, because the two hosts share one policy.

Run from the repo root:  python3 .agents/hooks/no-adhoc-browser.test.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HOOK = Path(".agents/hooks/no-adhoc-browser.py")

# (label, command, expected permission)
CASES = [
    # --- must be denied: the mistakes this hook exists to stop --------------
    (
        "heredoc that writes a puppeteer probe",
        "cat > .probe.mjs <<'JS'\n"
        "const puppeteer = require('puppeteer-core');\nJS\nnode .probe.mjs",
        "deny",
    ),
    (
        "inline node -e launching a browser",
        "node -e \"const p=require('puppeteer-core');p.launch()\"",
        "deny",
    ),
    (
        "direct headless Chrome screenshot",
        "'/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' "
        "--headless --screenshot=out.png http://127.0.0.1:4321/",
        "deny",
    ),
    (
        "running an untracked probe file",
        "node .agents/hooks/fixtures/tmp-probe.mjs",
        "deny",
    ),
    # --- must be allowed: legitimate work ----------------------------------
    ("starting the admin app", "pnpm dev", "allow"),
    ("starting the Playwright MCP server", "pnpm dlx @playwright/mcp@latest --help", "allow"),
    ("the repo Playwright launcher", "./.agents/playwright-mcp.sh --help", "allow"),
    ("the one-shot typecheck", "pnpm exec tsc --noEmit", "allow"),
    ("lint", "pnpm lint", "allow"),
    ("a production build", "pnpm build", "allow"),
    ("grepping for puppeteer references", "grep -rn puppeteer .agents/rules/browser-evidence.md", "allow"),
    ("reading the rule that names puppeteer", "cat .agents/rules/browser-evidence.md", "allow"),
    ("ordinary git work", "git status --short", "allow"),
    ("formatting changed files", "pnpm exec prettier --write src/browser/modules/store-modules/category/category.hooks.ts", "allow"),
]


def invoke(payload: dict, claude: bool) -> dict:
    done = subprocess.run(
        [sys.executable, str(HOOK)] + (["--claude"] if claude else []),
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert done.returncode == 0, f"hook exited {done.returncode}: {done.stderr}"
    return json.loads(done.stdout)


def run_cursor(command: str) -> str | None:
    return invoke({"command": command}, claude=False).get("permission")


def run_claude(command: str) -> str | None:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    out = invoke(payload, claude=True).get("hookSpecificOutput") or {}
    return out.get("permissionDecision")


def main() -> int:
    fixture = Path(".agents/hooks/fixtures/tmp-probe.mjs")
    fixture.parent.mkdir(parents=True, exist_ok=True)
    fixture.write_text("import puppeteer from 'puppeteer-core';\nawait puppeteer.launch();\n")

    failures = []
    try:
        for label, command, expected in CASES:
            cursor = run_cursor(command)
            claude = run_claude(command)
            ok = cursor == expected and claude == expected
            status = "ok  " if ok else "FAIL"
            if cursor != expected:
                failures.append(f"{label} [cursor]: expected {expected}, got {cursor}")
            if claude != expected:
                failures.append(f"{label} [claude]: expected {expected}, got {claude}")
            print(f"{status} {expected:<5} {label}")

        # A non-Bash Claude tool call carries no shell command to judge.
        other = invoke({"tool_name": "Read", "tool_input": {"file_path": "x"}}, claude=True)
        decision = (other.get("hookSpecificOutput") or {}).get("permissionDecision")
        ok = decision == "allow"
        print(f"{'ok  ' if ok else 'FAIL'} allow non-Bash Claude tool call")
        if not ok:
            failures.append(f"non-Bash Claude tool call: expected allow, got {decision}")
    finally:
        fixture.unlink(missing_ok=True)
        try:
            fixture.parent.rmdir()
        except OSError:
            pass

    print()
    if failures:
        for line in failures:
            print(f"FAIL {line}")
        return 1
    print(f"all {len(CASES)} cases passed on both hosts")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
